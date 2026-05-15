/**
 * Stripe Subscription API
 * GET /api/billing/subscription - Get customer's active subscription
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
        subscription: null,
        message: "No customer found",
      });
    }

    // Fetch active subscriptions
    const subscriptions = await stripe.subscriptions.list({
      customer: customer.id,
      status: "all",
      limit: 1,
    });

    if (subscriptions.data.length === 0) {
      return NextResponse.json({
        success: true,
        subscription: null,
        message: "No subscription found",
      });
    }

    const sub = subscriptions.data[0];
    const priceItem = sub.items?.data?.[0];

    // Determine plan name from price metadata or product name
    let planName = "Unknown";
    if (priceItem?.price?.product) {
      try {
        const product = await stripe.products.retrieve(
          priceItem.price.product as string,
        );
        planName = product.name || "Kloud Plan";
      } catch {
        planName = "Kloud Plan";
      }
    }

    // Map Stripe status to our status
    const statusMap: Record<string, string> = {
      active: "active",
      canceled: "canceled",
      past_due: "past_due",
      trialing: "trialing",
      incomplete: "pending",
      incomplete_expired: "expired",
      unpaid: "past_due",
    };

    const subscription = {
      id: sub.id,
      plan: planName,
      status: statusMap[sub.status] || sub.status,
      currentPeriodStart: new Date(
        ((sub as unknown as Record<string, number>).current_period_start || 0) *
          1000,
      ).toISOString(),
      currentPeriodEnd: new Date(
        ((sub as unknown as Record<string, number>).current_period_end || 0) *
          1000,
      ).toISOString(),
      cancelAtPeriodEnd: sub.cancel_at_period_end || false,
      amount: (priceItem?.price?.unit_amount || 0) / 100,
      currency: priceItem?.price?.currency?.toUpperCase() || "EUR",
      interval: priceItem?.price?.recurring?.interval || "month",
    };

    return NextResponse.json({
      success: true,
      subscription,
    });
  } catch (error: unknown) {
    console.error("Error fetching subscription:", error);
    if (error instanceof Error && error.message === "Unauthorized") {
      return NextResponse.json(
        { success: false, error: "Unauthorized", subscription: null },
        { status: 401 },
      );
    }
    if (error instanceof Error && error.message === "Stripe not configured") {
      return NextResponse.json(
        { success: false, error: "Stripe not configured", subscription: null },
        { status: 400 },
      );
    }
    const errorMessage =
      error instanceof Error ? error.message : "Failed to fetch subscription";
    return NextResponse.json(
      { success: false, error: errorMessage, subscription: null },
      { status: 500 },
    );
  }
}

// Cancel subscription
export async function DELETE(request: Request) {
  try {
    await requireInternalAuthUser(request);
    const stripe = getStripeClient();

    const { subscriptionId, cancelAtPeriodEnd = true } = await request.json();

    if (!subscriptionId) {
      return NextResponse.json(
        { success: false, error: "Subscription ID required" },
        { status: 400 },
      );
    }

    if (cancelAtPeriodEnd) {
      // Cancel at end of billing period
      await stripe.subscriptions.update(subscriptionId, {
        cancel_at_period_end: true,
      });
    } else {
      // Cancel immediately
      await stripe.subscriptions.cancel(subscriptionId);
    }

    return NextResponse.json({
      success: true,
      message: cancelAtPeriodEnd
        ? "Subscription will cancel at end of billing period"
        : "Subscription canceled immediately",
    });
  } catch (error: unknown) {
    console.error("Error canceling subscription:", error);
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
      error instanceof Error ? error.message : "Failed to cancel subscription";
    return NextResponse.json(
      { success: false, error: errorMessage },
      { status: 500 },
    );
  }
}


