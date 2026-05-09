/**
 * SPECIALIZED CHAT PROXY
 * Routes specialized chat requests through Next.js to Ocean-Core
 * so the browser never needs direct access to the backend.
 */

import { NextResponse } from "next/server";

const isDev = process.env.NODE_ENV !== "production";
const OCEAN_CORE_URL =
  process.env.OCEAN_CORE_URL ||
  (isDev ? "http://localhost:8030" : "http://kloud-ocean-core:8030");

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { message, domain } = body;

    if (!message?.trim()) {
      return NextResponse.json(
        { error: "Message is required" },
        { status: 400 },
      );
    }

    // Try specialized endpoint first
    try {
      const specializedRes = await fetch(
        `${OCEAN_CORE_URL}/api/v1/chat/specialized`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message, domain }),
        },
      );

      if (specializedRes.ok) {
        const data = await specializedRes.json();
        return NextResponse.json(data);
      }
    } catch {
      // Specialized endpoint not available, try fallback
    }

    // Fallback to standard chat
    try {
      const chatRes = await fetch(`${OCEAN_CORE_URL}/api/v1/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message, query: message }),
      });

      if (chatRes.ok) {
        const data = await chatRes.json();
        return NextResponse.json(data);
      }
    } catch {
      // Standard chat also failed
    }

    return NextResponse.json(
      {
        response:
          "⚠️ Ocean Core is currently starting up. Please try again in a few seconds.",
        domain: domain || "general",
        confidence: 0,
      },
      { status: 503 },
    );
  } catch {
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 },
    );
  }
}

export async function GET() {
  try {
    const res = await fetch(`${OCEAN_CORE_URL}/health`);
    if (res.ok) {
      const data = await res.json();
      return NextResponse.json({ status: "online", ...data });
    }
    return NextResponse.json({ status: "offline" }, { status: 503 });
  } catch {
    return NextResponse.json({ status: "offline" }, { status: 503 });
  }
}

