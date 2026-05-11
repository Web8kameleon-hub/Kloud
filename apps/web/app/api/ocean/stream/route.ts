/**
 * OCEAN STREAMING API - Real-time AI responses
 *
 * This endpoint adapts Ocean Core /api/v1/chat to the frontend streaming UI.
 */

const isDev = process.env.NODE_ENV !== "production";
const OCEAN_CORE_URL =
  process.env.OCEAN_INTERNAL_URL ||
  process.env.OCEAN_CORE_URL ||
  "http://ocean-core:8030";

const OCEAN_CHAT_URL = `${OCEAN_CORE_URL}/api/v1/chat`;

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
      `[Stream] Connecting to ${OCEAN_CHAT_URL} with message: ${message.substring(0, 50)}...`,
    );

    const response = await fetch(OCEAN_CHAT_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, language, mode: "normal" }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(
        `[Stream] Curiosity Ocean error: ${response.status} - ${errorText}`,
      );
      return new Response(`Curiosity Ocean error: ${response.status}`, { status: 500 });
    }

    const data = (await response.json()) as { response?: string; answer?: string };
    const answer = (data.response || data.answer || "Ocean returned an empty response.").trim();
    const encoder = new TextEncoder();
    const stream = new ReadableStream({
      start(controller) {
        const chunks = answer.match(/.{1,64}(\s|$)/g) || [answer];
        for (const chunk of chunks) {
          controller.enqueue(encoder.encode(chunk));
        }
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

