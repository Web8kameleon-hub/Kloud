/**
 * OCEAN STREAMING API - Real-time AI responses
 *
 * This endpoint adapts the Curiosity Ocean /ask API to the frontend streaming UI.
 */

const isDev = process.env.NODE_ENV !== "production";
const CURIOSITY_URL =
  process.env.CURIOSITY_URL ||
  (isDev ? "http://localhost:8019" : "http://curiosity:8019");

export async function POST(request: Request) {
  try {
    let message: string;
    let language = "en";
    try {
      const text = await request.text();
      if (!text || text.trim() === "") {
        return new Response("Empty request body", { status: 400 });
      }
      const body = JSON.parse(text);
      message = body.message || body.query || "";
      language = body.language || "en";
    } catch {
      return new Response("Invalid JSON body", { status: 400 });
    }

    if (!message?.trim()) {
      return new Response("Message required", { status: 400 });
    }

    console.log(
      `[Stream] Connecting to ${CURIOSITY_URL}/ask with message: ${message.substring(0, 50)}...`,
    );

    const response = await fetch(`${CURIOSITY_URL}/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: message, language }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(
        `[Stream] Curiosity Ocean error: ${response.status} - ${errorText}`,
      );
      return new Response(`Curiosity Ocean error: ${response.status}`, { status: 500 });
    }

    const data = (await response.json()) as { answer?: string };
    const answer = data.answer?.trim() || "Curiosity Ocean returned an empty response.";
    const encoder = new TextEncoder();
    const stream = new ReadableStream({
      start(controller) {
        controller.enqueue(encoder.encode(answer));
        controller.close();
      },
    });

    const headers = new Headers({
      "Content-Type": "text/plain; charset=utf-8",
      "Cache-Control": "no-cache",
    });

    return new Response(stream, { headers });
  } catch (error) {
    console.error("Streaming error:", error);
    return new Response(
      `Streaming failed: ${error instanceof Error ? error.message : "Unknown error"}`,
      { status: 500 },
    );
  }
}

