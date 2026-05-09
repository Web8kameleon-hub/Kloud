/**
 * Stripe Payment Methods API
 * GET /api/billing/payment-methods - Get customer's saved payment methods
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
        paymentMethods: [],
        message: "Stripe not configured",
      });
    }

    const stripe = new Stripe(process.env.STRIPE_SECRET_KEY, {
      
    });

    // Get customer email from session/auth
    const customerEmail = process.env.USER_EMAIL || "customer@kloud.com";

    // Search for customer by email
    const customers = await stripe.customers.list({
      email: customerEmail,
      limit: 1,
    });

    if (customers.data.length === 0) {
      return NextResponse.json({
        success: true,
        paymentMethods: [],
        message: "No customer found",
      });
    }

    const customer = customers.data[0];
    const customerId = customer.id;

    // Fetch payment methods for this customer
    const stripeMethods = await stripe.paymentMethods.list({
      customer: customerId,
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
    if (
      !process.env.STRIPE_SECRET_KEY ||
      process.env.STRIPE_SECRET_KEY.includes("YOUR_")
    ) {
      return NextResponse.json(
        { success: false, error: "Stripe not configured" },
        { status: 400 },
      );
    }

    const stripe = new Stripe(process.env.STRIPE_SECRET_KEY, {
      
    });

    const { paymentMethodId } = await request.json();

    if (!paymentMethodId) {
      return NextResponse.json(
        { success: false, error: "Payment method ID required" },
        { status: 400 },
      );
    }

    // Get customer
    const customerEmail = process.env.USER_EMAIL || "customer@kloud.com";
    const customers = await stripe.customers.list({
      email: customerEmail,
      limit: 1,
    });

    if (customers.data.length === 0) {
      return NextResponse.json(
        { success: false, error: "Customer not found" },
        { status: 404 },
      );
    }

    const customerId = customers.data[0].id;

    // Set as default payment method
    await stripe.customers.update(customerId, {
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
    if (
      !process.env.STRIPE_SECRET_KEY ||
      process.env.STRIPE_SECRET_KEY.includes("YOUR_")
    ) {
      return NextResponse.json(
        { success: false, error: "Stripe not configured" },
        { status: 400 },
      );
    }

    const stripe = new Stripe(process.env.STRIPE_SECRET_KEY, {
      
    });

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


