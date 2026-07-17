/**
 * Kloud Cloud - Authentication Middleware
 * Internal authentication policy (email + OTP) only.
 *
 * @author Ledjan Ahmati
 * @copyright 2026 Kloud Cloud
 */

import { NextRequest, NextResponse } from "next/server";

// Internal-only auth policy (no external auth providers)
const authProvider = "internal";

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

  // Internal auth flow is handled by internal API routes and client session token checks.
  // Middleware currently allows requests and avoids external-provider gates.
  if (authProvider === "internal") {
    return NextResponse.next();
  }

  // Check if route is public
  const isPublic = publicRoutes.some(
    (route) => pathname === route || pathname.startsWith(route + "/"),
  );

  if (isPublic || pathname.startsWith("/api")) {
    return NextResponse.next();
  }

  // Fallback (kept for safety)
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

