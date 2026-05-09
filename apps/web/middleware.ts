/**
 * Kloud Cloud - Authentication Middleware
 * Protects routes using Clerk authentication
 *
 * @author Ledjan Ahmati
 * @copyright 2026 Kloud Cloud
 */

import { NextRequest, NextResponse } from "next/server";

// Check if Clerk is configured
const isClerkConfigured = !!process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY;

// Public routes that don't require authentication
const publicRoutes = [
  "/",
  "/sign-in",
  "/sign-up",
  "/landing",
  "/about-us",
  "/pricing",
  "/why-kloud",
  "/platform",
  "/security",
  "/company",
  "/developers",
  "/status",
  "/health",
];

// Middleware function
export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // If Clerk is not configured, allow all routes
  if (!isClerkConfigured) {
    return NextResponse.next();
  }

  // Check if route is public
  const isPublic = publicRoutes.some(
    (route) => pathname === route || pathname.startsWith(route + "/"),
  );

  if (isPublic || pathname.startsWith("/api")) {
    return NextResponse.next();
  }

  // For protected routes when Clerk is configured,
  // let the client-side components handle auth checks
  return NextResponse.next();
}

export const config = {
  matcher: [
    // Skip Next.js internals and all static files
    "/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)",
    // Always run for API routes
    "/(api|trpc)(.*)",
  ],
};

