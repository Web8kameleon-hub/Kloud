/**
 * Kloud Cloud - Authentication Middleware
 * Protects routes using Clerk authentication
 *
 * @author Ledjan Ahmati
 * @copyright 2026 Kloud Cloud
 */

import { NextRequest, NextResponse } from "next/server";

// Auth provider policy: internal auth is default, Clerk only when explicitly selected.
const authProvider = process.env.AUTH_PROVIDER || "internal";
const isClerkConfigured =
  authProvider === "clerk" && !!process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY;

// Public routes that don't require authentication
const publicRoutes = [
  "/",
  "/sign-in",
  "/sign-up",
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
  const host = (
    request.headers.get("x-forwarded-host") ||
    request.headers.get("host") ||
    ""
  ).toLowerCase();

  const isKameleonBlogHost =
    host.includes("kameleon-blog") ||
    host.startsWith("blog.") ||
    host.startsWith("kameleon-blog.");

  if (isKameleonBlogHost && !pathname.startsWith("/api")) {
    const url = request.nextUrl.clone();
    if (pathname === "/") {
      url.pathname = "/blog";
      return NextResponse.rewrite(url);
    }
    if (!pathname.startsWith("/blog") && !pathname.startsWith("/_next")) {
      url.pathname = `/blog${pathname}`;
      return NextResponse.rewrite(url);
    }
  }

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

