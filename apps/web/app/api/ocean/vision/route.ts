import { NextRequest, NextResponse } from "next/server";

/**
 * Vision Analysis API Proxy
 * Proxies vision/analyze requests to Ocean-Core backend
 * This runs server-side so it can reach the internal Docker network
 */

const isDev = process.env.NODE_ENV !== "production";
const OCEAN_CORE_URL =
  process.env.OCEAN_CORE_URL ||
  (isDev ? "http://localhost:8030" : "http://kloud-ocean-core:8030");

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    // Forward auth headers
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };
    const clerkUserId = request.headers.get("X-Clerk-User-Id");
    if (clerkUserId) {
      headers["X-Clerk-User-Id"] = clerkUserId;
      headers["X-User-ID"] = clerkUserId;
    }

    const response = await fetch(`${OCEAN_CORE_URL}/api/v1/vision/analyze`, {
      method: "POST",
      headers,
      body: JSON.stringify(body),
    });

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error("[Vision Proxy] Error:", error);
    return NextResponse.json(
      {
        status: "error",
        message: "Vision analysis service unavailable. Please try again.",
      },
      { status: 502 }
    );
  }
}

