import Stripe from "stripe";
import { InternalUser, resolveBearerUser } from "@/lib/internal-auth";

export function getStripeClient(): Stripe {
  const secret = process.env.STRIPE_SECRET_KEY || "";
  if (!secret || secret === "disabled" || secret.includes("YOUR_")) {
    throw new Error("Stripe not configured");
  }
  return new Stripe(secret, {});
}

export async function requireInternalAuthUser(request: Request): Promise<InternalUser> {
  const authUser = await resolveBearerUser(request.headers.get("authorization"));
  if (!authUser) {
    throw new Error("Unauthorized");
  }
  return authUser;
}

export async function findCustomerByInternalUser(
  stripe: Stripe,
  authUser: InternalUser,
): Promise<Stripe.Customer | null> {
  const query = `metadata['internal_user_id']:'${authUser.id}'`;
  try {
    const result = await stripe.customers.search({
      query,
      limit: 1,
    });
    if (result.data.length > 0) {
      return result.data[0];
    }
  } catch {
    // Search API can be unavailable in some accounts/environments.
  }

  if (authUser.email) {
    const byEmail = await stripe.customers.list({
      email: authUser.email,
      limit: 10,
    });

    const exact = byEmail.data.find(
      (c) => c.metadata?.internal_user_id === authUser.id,
    );
    if (exact) {
      return exact;
    }

    if (byEmail.data.length > 0) {
      return byEmail.data[0];
    }
  }

  return null;
}

export async function getOrCreateCustomerForInternalUser(
  stripe: Stripe,
  authUser: InternalUser,
): Promise<Stripe.Customer> {
  const existing = await findCustomerByInternalUser(stripe, authUser);
  if (existing) {
    return existing;
  }

  return stripe.customers.create({
    email: authUser.email || undefined,
    name: authUser.name || undefined,
    phone: authUser.phone || undefined,
    metadata: {
      internal_user_id: authUser.id,
    },
  });
}
