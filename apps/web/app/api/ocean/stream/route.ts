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
const GLOBAL_AI_URL =
  process.env.AI_9999_URL ||
  "http://ai-global-9999:9999";

const OCEAN_CHAT_URL = `${OCEAN_CORE_URL}/api/v1/chat`;
const GLOBAL_CHAT_URL = `${GLOBAL_AI_URL}/api/v1/chat`;

async function fetchOceanCore(
  message: string,
  language: string,
  resonanceProfile: string,
  resonanceNdb: number,
): Promise<string> {
  const response = await fetch(OCEAN_CHAT_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message,
      language,
      mode: resonanceProfile,
      resonance_profile: resonanceProfile,
      resonance_ndb: resonanceNdb,
    }),
  });
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`ocean-core ${response.status}: ${errorText}`);
  }
  const data = (await response.json()) as { response?: string; answer?: string };
  return (data.response || data.answer || "Ocean returned an empty response.").trim();
}

async function fetchGlobal9999(
  message: string,
  language: string,
  resonanceProfile: string,
  resonanceNdb: number,
): Promise<string> {
  const response = await fetch(GLOBAL_CHAT_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message,
      query: message,
      language_hint: language,
      mode: resonanceProfile,
      resonance_profile: resonanceProfile,
      resonance_ndb: resonanceNdb,
      wwwmmm_gate: "active",
    }),
  });
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`global-9999 ${response.status}: ${errorText}`);
  }
  const data = (await response.json()) as { response?: string; answer?: string };
  return (data.response || data.answer || "Global 9999 returned an empty response.").trim();
}

export async function POST(request: Request) {
  try {
    let message: string;
    let language = "en";
    let resonanceProfile = "normal";
    let resonanceNdb = 0.74;
    try {
      const text = await request.text();
      if (!text || text.trim() === "") {
        return new Response("Empty request body", { status: 400 });
      }
      const body = JSON.parse(text);
      message = body.message || body.query || "";
      language = body.language || "en";
      const profileMap: Record<string, string> = {
        curious: "normal",
        wild: "deep",
        chaos: "exploratory",
        genius: "expert",
      };
      const ndbMap: Record<string, number> = {
        curious: 0.74,
        wild: 0.82,
        chaos: 0.88,
        genius: 0.93,
      };
      const curiosityLevel = body.curiosityLevel || body.curiosity_level || "curious";
      resonanceProfile = body.resonance_profile || profileMap[curiosityLevel] || "normal";
      resonanceNdb = Number(body.resonance_ndb ?? ndbMap[curiosityLevel] ?? 0.74);
    } catch {
      return new Response("Invalid JSON body", { status: 400 });
    }

    if (!message?.trim()) {
      return new Response("Message required", { status: 400 });
    }

    console.log(
      `[Stream] Connecting to ${OCEAN_CHAT_URL} with message: ${message.substring(0, 50)}...`,
    );

    const answer = await Promise.any([
      fetchGlobal9999(message, language, resonanceProfile, resonanceNdb),
      fetchOceanCore(message, language, resonanceProfile, resonanceNdb),
    ]);

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
    console.error("Streaming error (global/ocean):", error);
    return new Response(
      `Streaming failed: ${error instanceof Error ? error.message : "Unknown error"}`,
      { status: 500 },
    );
  }
}

