/**
 * Stripe Billing Address API
 * GET/PUT /api/billing/billing-address - Manage customer billing address
 */

import { NextResponse } from "next/server";
import { findCustomerByInternalUser, getStripeClient, requireInternalAuthUser } from "@/lib/stripe-billing";

interface BillingAddress {
  line1: string;
  line2?: string;
  city: string;
  state?: string;
  postal_code: string;
  country: string;
  name?: string;
  phone?: string;
}

export async function GET(request: Request) {
  try {
    const authUser = await requireInternalAuthUser(request);
    const stripe = getStripeClient();
    const customer = await findCustomerByInternalUser(stripe, authUser);

    if (!customer) {
      return NextResponse.json({
        success: true,
        billingAddress: null,
        message: "No customer found",
      });
    }
    const address = customer.address;

    if (!address || !address.line1) {
      return NextResponse.json({
        success: true,
        billingAddress: null,
        message: "No billing address set",
      });
    }

    const billingAddress: BillingAddress = {
      line1: address.line1,
      line2: address.line2 || undefined,
      city: address.city || "",
      state: address.state || undefined,
      postal_code: address.postal_code || "",
      country: address.country || "",
      name: customer.name || undefined,
      phone: customer.phone || undefined,
    };

    return NextResponse.json({
      success: true,
      billingAddress,
    });
  } catch (error: unknown) {
    console.error("Error fetching billing address:", error);
    if (error instanceof Error && error.message === "Unauthorized") {
      return NextResponse.json(
        { success: false, error: "Unauthorized", billingAddress: null },
        { status: 401 },
      );
    }
    if (error instanceof Error && error.message === "Stripe not configured") {
      return NextResponse.json(
        { success: false, error: "Stripe not configured", billingAddress: null },
        { status: 400 },
      );
    }
    const errorMessage =
      error instanceof Error
        ? error.message
        : "Failed to fetch billing address";
    return NextResponse.json(
      { success: false, error: errorMessage, billingAddress: null },
      { status: 500 },
    );
  }
}

export async function PUT(request: Request) {
  try {
    const authUser = await requireInternalAuthUser(request);
    const stripe = getStripeClient();

    const billingAddress: BillingAddress = await request.json();

    // Validate required fields
    if (
      !billingAddress.line1 ||
      !billingAddress.city ||
      !billingAddress.postal_code ||
      !billingAddress.country
    ) {
      return NextResponse.json(
        { success: false, error: "Missing required address fields" },
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

    // Update customer address
    await stripe.customers.update(customer.id, {
      address: {
        line1: billingAddress.line1,
        line2: billingAddress.line2 || undefined,
        city: billingAddress.city,
        state: billingAddress.state || undefined,
        postal_code: billingAddress.postal_code,
        country: billingAddress.country,
      },
      name: billingAddress.name || undefined,
      phone: billingAddress.phone || undefined,
    });

    return NextResponse.json({
      success: true,
      message: "Billing address updated",
    });
  } catch (error: unknown) {
    console.error("Error updating billing address:", error);
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
        : "Failed to update billing address";
    return NextResponse.json(
      { success: false, error: errorMessage },
      { status: 500 },
    );
  }
}


