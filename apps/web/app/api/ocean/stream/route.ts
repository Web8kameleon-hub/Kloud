/**
 * OCEAN STREAMING API - Real-time AI responses
 *
 * This endpoint streams responses from Ocean-Core,
 * so text appears immediately (2-3 seconds) instead of waiting 60+ seconds.
 */

// Detect environment for correct API URL
const isDev = process.env.NODE_ENV !== "production";
const OCEAN_CORE_URL =
  process.env.OCEAN_CORE_URL ||
  (isDev ? "http://localhost:8030" : "http://kloud-ocean-core:8030");

export async function POST(request: Request) {
  try {
    // Parse body with error handling
    let message: string;
    try {
      const text = await request.text();
      if (!text || text.trim() === "") {
        return new Response("Empty request body", { status: 400 });
      }
      const body = JSON.parse(text);
      message = body.message || body.query || "";
    } catch {
      return new Response("Invalid JSON body", { status: 400 });
    }

    if (!message?.trim()) {
      return new Response("Message required", { status: 400 });
    }

    console.log(
      `[Stream] Connecting to ${OCEAN_CORE_URL}/api/v1/chat/stream with message: ${message.substring(0, 50)}...`,
    );

    // Call Ocean-Core streaming endpoint
    const response = await fetch(`${OCEAN_CORE_URL}/api/v1/chat/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(
        `[Stream] Ocean-Core error: ${response.status} - ${errorText}`,
      );
      return new Response(`Ocean-Core error: ${response.status}`, {
        status: 500,
      });
    }

    // Stream the response directly to the client
    const headers = new Headers({
      "Content-Type": "text/plain; charset=utf-8",
      "Cache-Control": "no-cache",
      "Transfer-Encoding": "chunked",
    });

    return new Response(response.body, { headers });
  } catch (error) {
    console.error("Streaming error:", error);
    return new Response(
      `Streaming failed: ${error instanceof Error ? error.message : "Unknown error"}`,
      { status: 500 },
    );
  }
}

