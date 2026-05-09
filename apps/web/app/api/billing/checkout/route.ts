/**
 * Stripe Checkout API
 * POST /api/billing/checkout - Create Stripe Checkout session
 */

import { NextResponse } from "next/server";
import Stripe from "stripe";

// Plan pricing configuration (in cents)
const PLAN_PRICING = {
  starter_monthly: {
    amount: 2900,
    name: "Kloud Starter",
    interval: "month" as const,
  },
  starter_yearly: {
    amount: 29000,
    name: "Kloud Starter (Yearly)",
    interval: "year" as const,
  },
  professional_monthly: {
    amount: 9900,
    name: "Kloud Professional",
    interval: "month" as const,
  },
  professional_yearly: {
    amount: 99000,
    name: "Kloud Professional (Yearly)",
    interval: "year" as const,
  },
  enterprise_monthly: {
    amount: 29900,
    name: "Kloud Enterprise",
    interval: "month" as const,
  },
  enterprise_yearly: {
    amount: 299000,
    name: "Kloud Enterprise (Yearly)",
    interval: "year" as const,
  },
};

export async function POST(request: Request) {
  try {
    const { priceId, planName, successUrl, cancelUrl } = await request.json();

    // Check if Stripe is configured
    if (
      !process.env.STRIPE_SECRET_KEY ||
      process.env.STRIPE_SECRET_KEY.includes("YOUR_")
    ) {
      return NextResponse.json(
        {
          success: false,
          error: "Stripe not configured",
          message: "Please add STRIPE_SECRET_KEY to environment variables",
          demo: true,
        },
        { status: 400 },
      );
    }

    const stripe = new Stripe(process.env.STRIPE_SECRET_KEY, {
      
    });

    // Get pricing for the selected plan
    const pricing = PLAN_PRICING[priceId as keyof typeof PLAN_PRICING];

    if (!pricing) {
      return NextResponse.json(
        { success: false, error: `Invalid plan: ${priceId}` },
        { status: 400 },
      );
    }

    // Create or get a customer (required for Stripe Accounts V2 in test mode)
    // In production, you'd fetch the customer from your database
    const customerEmail = process.env.USER_EMAIL || "customer@kloud.com";

    // Search for existing customer
    const existingCustomers = await stripe.customers.list({
      email: customerEmail,
      limit: 1,
    });

    let customerId: string;
    if (existingCustomers.data.length > 0) {
      customerId = existingCustomers.data[0].id;
    } else {
      // Create new customer
      const customer = await stripe.customers.create({
        email: customerEmail,
        name: process.env.USER_NAME || "Kloud User",
        metadata: {
          company: process.env.USER_COMPANY || "",
        },
      });
      customerId = customer.id;
    }

    // Create Checkout Session with dynamic pricing (no pre-created products needed)
    const session = await stripe.checkout.sessions.create({
      mode: "subscription",
      customer: customerId,
      payment_method_types: ["card"],
      line_items: [
        {
          price_data: {
            currency: "eur",
            product_data: {
              name: pricing.name,
              description: `${planName || pricing.name} - Kloud Cloud Platform`,
            },
            unit_amount: pricing.amount,
            recurring: {
              interval: pricing.interval,
            },
          },
          quantity: 1,
        },
      ],
      success_url:
        successUrl ||
        `${process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000"}/modules/account?success=true&session_id={CHECKOUT_SESSION_ID}`,
      cancel_url:
        cancelUrl ||
        `${process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000"}/modules/account?canceled=true`,
      metadata: {
        planName: planName || pricing.name,
        priceId,
      },
      billing_address_collection: "required",
      allow_promotion_codes: true,
    });

    return NextResponse.json({
      success: true,
      sessionId: session.id,
      url: session.url,
    });
  } catch (error: unknown) {
    console.error("Stripe checkout error:", error);
    const errorMessage =
      error instanceof Error
        ? error.message
        : "Failed to create checkout session";
    return NextResponse.json(
      { success: false, error: errorMessage },
      { status: 500 },
    );
  }
}


