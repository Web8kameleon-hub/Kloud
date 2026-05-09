/**
 * Stripe Billing Address API
 * GET/PUT /api/billing/billing-address - Manage customer billing address
 */

import { NextResponse } from "next/server";
import Stripe from "stripe";

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

export async function GET() {
  try {
    // Check if Stripe is configured
    if (
      !process.env.STRIPE_SECRET_KEY ||
      process.env.STRIPE_SECRET_KEY.includes("YOUR_")
    ) {
      return NextResponse.json({
        success: true,
        billingAddress: null,
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
        billingAddress: null,
        message: "No customer found",
      });
    }

    const customer = customers.data[0];
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

    // Update customer address
    await stripe.customers.update(customerId, {
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


