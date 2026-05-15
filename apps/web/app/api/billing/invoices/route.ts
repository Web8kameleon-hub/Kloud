/**
 * Stripe Invoices API
 * GET /api/billing/invoices - Get customer invoices from Stripe
 */

import { NextResponse } from "next/server";
import { findCustomerByInternalUser, getStripeClient, requireInternalAuthUser } from "@/lib/stripe-billing";

export async function GET(request: Request) {
  try {
    const authUser = await requireInternalAuthUser(request);
    const stripe = getStripeClient();
    const customer = await findCustomerByInternalUser(stripe, authUser);

    if (!customer) {
      return NextResponse.json({
        success: true,
        invoices: [],
        message: "No customer found",
      });
    }

    // Fetch invoices for this customer
    const stripeInvoices = await stripe.invoices.list({
      customer: customer.id,
      limit: 50,
    });

    // Transform to our format
    const invoices = stripeInvoices.data.map((invoice) => ({
      id: invoice.number || invoice.id,
      date: new Date((invoice.created || 0) * 1000).toISOString(),
      amount: (invoice.amount_paid || 0) / 100,
      currency: invoice.currency?.toUpperCase() || "EUR",
      status:
        invoice.status === "paid"
          ? "paid"
          : invoice.status === "open"
            ? "pending"
            : "failed",
      pdfUrl: invoice.invoice_pdf || undefined,
      hostedUrl: invoice.hosted_invoice_url || undefined,
      description:
        invoice.description ||
        invoice.lines?.data?.[0]?.description ||
        "Kloud Subscription",
    }));

    return NextResponse.json({
      success: true,
      invoices,
      total: stripeInvoices.data.length,
    });
  } catch (error: unknown) {
    console.error("Error fetching invoices:", error);
    if (error instanceof Error && error.message === "Unauthorized") {
      return NextResponse.json(
        { success: false, error: "Unauthorized", invoices: [] },
        { status: 401 },
      );
    }
    if (error instanceof Error && error.message === "Stripe not configured") {
      return NextResponse.json(
        { success: false, error: "Stripe not configured", invoices: [] },
        { status: 400 },
      );
    }
    const errorMessage =
      error instanceof Error ? error.message : "Failed to fetch invoices";
    return NextResponse.json(
      { success: false, error: errorMessage, invoices: [] },
      { status: 500 },
    );
  }
}


