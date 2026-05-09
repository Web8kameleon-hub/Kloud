/**
 * OCEAN API - Proxy to Ocean-Core /api/v1/chat
 */

const isDev = process.env.NODE_ENV !== "production";
const OCEAN_CORE_URL =
  process.env.OCEAN_CORE_URL ||
  (isDev ? "http://localhost:8030" : "http://kloud-ocean-core:8030");

export async function POST(request: Request) {
  try {
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

    console.log(`[Ocean] Calling ${OCEAN_CORE_URL}/api/v1/chat`);

    const response = await fetch(`${OCEAN_CORE_URL}/api/v1/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`[Ocean] Error: ${response.status} - ${errorText}`);
      return new Response(`Ocean error: ${response.status}`, { status: 500 });
    }

    const data = await response.json();
    const responseText = data.response || data.message || JSON.stringify(data);

    return new Response(responseText, {
      headers: {
        "Content-Type": "text/plain; charset=utf-8",
        "Cache-Control": "no-cache",
      },
    });
  } catch (error) {
    console.error("Error:", error);
    return new Response(
      `Failed: ${error instanceof Error ? error.message : "Unknown"}`,
      { status: 500 },
    );
  }
}

