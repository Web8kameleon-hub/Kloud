/**
 * Kloud Cloud - Stripe Checkout API
 *
 * Creates checkout sessions for subscription plans
 *
 * @author Ledjan Ahmati
 * @copyright 2026 Kloud Cloud
 */

import { NextRequest, NextResponse } from "next/server";
import Stripe from "stripe";
import { resolveBearerUser } from "@/lib/internal-auth";

// Initialize Stripe lazily to avoid build-time errors
const getStripe = () => {
  if (!process.env.STRIPE_SECRET_KEY) {
    throw new Error("STRIPE_SECRET_KEY is not configured");
  }
  return new Stripe(process.env.STRIPE_SECRET_KEY, {
    apiVersion: "2024-12-18.acacia" as Stripe.LatestApiVersion,
  });
};

// Price IDs for each plan (with fallbacks for build time)
const PRICE_IDS: Record<string, Record<string, string>> = {
  starter: {
    monthly:
      process.env.STRIPE_PRICE_STARTER_MONTHLY || "price_starter_monthly",
    yearly: process.env.STRIPE_PRICE_STARTER_YEARLY || "price_starter_yearly",
  },
  professional: {
    monthly:
      process.env.STRIPE_PRICE_PROFESSIONAL_MONTHLY || "price_pro_monthly",
    yearly: process.env.STRIPE_PRICE_PROFESSIONAL_YEARLY || "price_pro_yearly",
  },
  enterprise: {
    monthly: process.env.STRIPE_PRICE_ENTERPRISE_MONTHLY || "price_ent_monthly",
    yearly: process.env.STRIPE_PRICE_ENTERPRISE_YEARLY || "price_ent_yearly",
  },
};

export async function POST(request: NextRequest) {
  try {
    const authUser = await resolveBearerUser(request.headers.get("authorization"));
    if (!authUser) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const body = await request.json();
    const { plan, interval = "monthly" } = body;

    if (!plan || !PRICE_IDS[plan]) {
      return NextResponse.json({ error: "Invalid plan" }, { status: 400 });
    }

    const priceId = PRICE_IDS[plan][interval];
    if (!priceId) {
      return NextResponse.json({ error: "Invalid interval" }, { status: 400 });
    }

    const stripe = getStripe();

    // Create or retrieve Stripe customer
    let customerId: string;

    // Check if user already has a Stripe customer
    const existingCustomers = await stripe.customers.list({
      email: authUser.email || undefined,
      limit: 1,
    });

    if (existingCustomers.data.length > 0) {
      customerId = existingCustomers.data[0].id;
    } else {
      const customer = await stripe.customers.create({
        email: authUser.email || undefined,
        name: authUser.name,
        metadata: {
          internal_user_id: authUser.id,
        },
      });
      customerId = customer.id;
    }

    // Create checkout session
    const session = await stripe.checkout.sessions.create({
      customer: customerId,
      payment_method_types: ["card"],
      line_items: [
        {
          price: priceId,
          quantity: 1,
        },
      ],
      mode: "subscription",
      success_url: `${process.env.NEXT_PUBLIC_APP_URL || "https://kloud.com"}/subscription?success=true&session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${process.env.NEXT_PUBLIC_APP_URL || "https://kloud.com"}/pricing?cancelled=true`,
      metadata: {
        internal_user_id: authUser.id,
        plan: plan,
        interval: interval,
      },
      subscription_data: {
        metadata: {
          internal_user_id: authUser.id,
          plan: plan,
        },
      },
      allow_promotion_codes: true,
      billing_address_collection: "required",
    });

    return NextResponse.json({
      sessionId: session.id,
      url: session.url,
    });
  } catch (error) {
    console.error("Error creating checkout session:", error);
    return NextResponse.json(
      { error: "Failed to create checkout session" },
      { status: 500 },
    );
  }
}

export async function GET() {
  return NextResponse.json({
    plans: {
      starter: {
        name: "Starter",
        monthly: 9,
        yearly: 90,
        features: [
          "500 API calls/day",
          "Basic analytics",
          "Email support",
          "1 project",
        ],
      },
      professional: {
        name: "Professional",
        monthly: 29,
        yearly: 290,
        features: [
          "5,000 API calls/day",
          "Advanced analytics",
          "Priority support",
          "10 projects",
          "Team collaboration",
        ],
      },
      enterprise: {
        name: "Enterprise",
        monthly: 99,
        yearly: 990,
        features: [
          "Unlimited API calls",
          "Custom analytics",
          "Dedicated support",
          "Unlimited projects",
          "SSO & SAML",
          "SLA guarantee",
        ],
      },
    },
  });
}


