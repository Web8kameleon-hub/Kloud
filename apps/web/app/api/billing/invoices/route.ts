/**
 * Stripe Invoices API
 * GET /api/billing/invoices - Get customer invoices from Stripe
 */

import { NextResponse } from "next/server";
import Stripe from "stripe";

export async function GET() {
  try {
    // Check if Stripe is configured
    if (
      !process.env.STRIPE_SECRET_KEY ||
      process.env.STRIPE_SECRET_KEY.includes("YOUR_")
    ) {
      return NextResponse.json({
        success: true,
        invoices: [],
        message: "Stripe not configured - no invoices available",
      });
    }

    const stripe = new Stripe(process.env.STRIPE_SECRET_KEY, {
      
    });

    // Get customer email from session/auth (in production, get from authenticated user)
    const customerEmail = process.env.USER_EMAIL || "customer@kloud.com";

    // Search for customer by email
    const customers = await stripe.customers.list({
      email: customerEmail,
      limit: 1,
    });

    if (customers.data.length === 0) {
      return NextResponse.json({
        success: true,
        invoices: [],
        message: "No customer found",
      });
    }

    const customerId = customers.data[0].id;

    // Fetch invoices for this customer
    const stripeInvoices = await stripe.invoices.list({
      customer: customerId,
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
    const errorMessage =
      error instanceof Error ? error.message : "Failed to fetch invoices";
    return NextResponse.json(
      { success: false, error: errorMessage, invoices: [] },
      { status: 500 },
    );
  }
}


