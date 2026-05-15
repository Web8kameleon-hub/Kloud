/**
 * Stripe Payment Methods API
 * GET /api/billing/payment-methods - Get customer's saved payment methods
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
        paymentMethods: [],
        message: "No customer found",
      });
    }

    // Fetch payment methods for this customer
    const stripeMethods = await stripe.paymentMethods.list({
      customer: customer.id,
      type: "card",
    });

    // Get default payment method
    const defaultMethodId =
      typeof customer.invoice_settings?.default_payment_method === "string"
        ? customer.invoice_settings.default_payment_method
        : customer.invoice_settings?.default_payment_method?.id;

    // Transform to our format
    const paymentMethods = stripeMethods.data.map((method) => ({
      id: method.id,
      type: "card" as const,
      last4: method.card?.last4 || "****",
      brand: method.card?.brand || "unknown",
      expiryMonth: method.card?.exp_month,
      expiryYear: method.card?.exp_year,
      isDefault: method.id === defaultMethodId,
    }));

    return NextResponse.json({
      success: true,
      paymentMethods,
      total: paymentMethods.length,
    });
  } catch (error: unknown) {
    console.error("Error fetching payment methods:", error);
    if (error instanceof Error && error.message === "Unauthorized") {
      return NextResponse.json(
        { success: false, error: "Unauthorized", paymentMethods: [] },
        { status: 401 },
      );
    }
    if (error instanceof Error && error.message === "Stripe not configured") {
      return NextResponse.json(
        { success: false, error: "Stripe not configured", paymentMethods: [] },
        { status: 400 },
      );
    }
    const errorMessage =
      error instanceof Error
        ? error.message
        : "Failed to fetch payment methods";
    return NextResponse.json(
      { success: false, error: errorMessage, paymentMethods: [] },
      { status: 500 },
    );
  }
}

// Set default payment method
export async function PUT(request: Request) {
  try {
    const authUser = await requireInternalAuthUser(request);
    const stripe = getStripeClient();

    const { paymentMethodId } = await request.json();

    if (!paymentMethodId) {
      return NextResponse.json(
        { success: false, error: "Payment method ID required" },
        { status: 400 },
      );
    }

    const customer = await findCustomerByInternalUser(stripe, authUser);

    if (!customer) {
      return NextResponse.json(
        { success: false, error: "Customer not found" },
        { status: 404 },
      );
    }

    // Set as default payment method
    await stripe.customers.update(customer.id, {
      invoice_settings: {
        default_payment_method: paymentMethodId,
      },
    });

    return NextResponse.json({
      success: true,
      message: "Default payment method updated",
    });
  } catch (error: unknown) {
    console.error("Error updating default payment method:", error);
    if (error instanceof Error && error.message === "Unauthorized") {
      return NextResponse.json(
        { success: false, error: "Unauthorized" },
        { status: 401 },
      );
    }
    if (error instanceof Error && error.message === "Stripe not configured") {
      return NextResponse.json(
        { success: false, error: "Stripe not configured" },
        { status: 400 },
      );
    }
    const errorMessage =
      error instanceof Error
        ? error.message
        : "Failed to update payment method";
    return NextResponse.json(
      { success: false, error: errorMessage },
      { status: 500 },
    );
  }
}

// Delete payment method
export async function DELETE(request: Request) {
  try {
    await requireInternalAuthUser(request);
    const stripe = getStripeClient();

    const { paymentMethodId } = await request.json();

    if (!paymentMethodId) {
      return NextResponse.json(
        { success: false, error: "Payment method ID required" },
        { status: 400 },
      );
    }

    // Detach payment method from customer
    await stripe.paymentMethods.detach(paymentMethodId);

    return NextResponse.json({
      success: true,
      message: "Payment method removed",
    });
  } catch (error: unknown) {
    console.error("Error removing payment method:", error);
    if (error instanceof Error && error.message === "Unauthorized") {
      return NextResponse.json(
        { success: false, error: "Unauthorized" },
        { status: 401 },
      );
    }
    if (error instanceof Error && error.message === "Stripe not configured") {
      return NextResponse.json(
        { success: false, error: "Stripe not configured" },
        { status: 400 },
      );
    }
    const errorMessage =
      error instanceof Error
        ? error.message
        : "Failed to remove payment method";
    return NextResponse.json(
      { success: false, error: errorMessage },
      { status: 500 },
    );
  }
}


