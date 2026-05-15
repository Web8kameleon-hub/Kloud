/**
 * Stripe Checkout API
 * POST /api/billing/checkout - Create Stripe Checkout session
 */

import { NextResponse } from "next/server";
import { getOrCreateCustomerForInternalUser, getStripeClient, requireInternalAuthUser } from "@/lib/stripe-billing";

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
    const authUser = await requireInternalAuthUser(request);

    const { priceId, planName, successUrl, cancelUrl } = await request.json();
    const stripe = getStripeClient();

    // Get pricing for the selected plan
    const pricing = PLAN_PRICING[priceId as keyof typeof PLAN_PRICING];

    if (!pricing) {
      return NextResponse.json(
        { success: false, error: `Invalid plan: ${priceId}` },
        { status: 400 },
      );
    }

    const customer = await getOrCreateCustomerForInternalUser(stripe, authUser);

    // Create Checkout Session with dynamic pricing (no pre-created products needed)
    const session = await stripe.checkout.sessions.create({
      mode: "subscription",
      customer: customer.id,
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
        internal_user_id: authUser.id,
        internal_user_email: authUser.email || "",
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
    if (error instanceof Error && error.message === "Unauthorized") {
      return NextResponse.json(
        { success: false, error: "Unauthorized" },
        { status: 401 },
      );
    }
    if (error instanceof Error && error.message === "Stripe not configured") {
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



