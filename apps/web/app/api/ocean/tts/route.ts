import { NextRequest, NextResponse } from "next/server";

/**
 * Text-to-Speech API Proxy
 * Proxies TTS requests to Ocean-Core backend (Edge TTS Neural Voices)
 * This runs server-side so it can reach the internal Docker network
 */

const isDev = process.env.NODE_ENV !== "production";
const OCEAN_CORE_URL =
  process.env.OCEAN_CORE_URL ||
  (isDev ? "http://localhost:8030" : "http://kloud-ocean-core:8030");

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    // Validate input
    if (!body.text || typeof body.text !== "string") {
      return NextResponse.json(
        { status: "error", message: "Text is required" },
        { status: 400 }
      );
    }

    // Forward auth headers
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };
    const clerkUserId = request.headers.get("X-Clerk-User-Id");
    if (clerkUserId) {
      headers["X-Clerk-User-Id"] = clerkUserId;
      headers["X-User-ID"] = clerkUserId;
    }

    const response = await fetch(`${OCEAN_CORE_URL}/api/v1/tts`, {
      method: "POST",
      headers,
      body: JSON.stringify({
        text: body.text,
        language: body.language || "en",
        voice: body.voice,
        rate: body.rate || "+0%",
        pitch: body.pitch || "+0Hz",
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error("[TTS Proxy] Backend error:", errorText);
      return NextResponse.json(
        { status: "error", message: "TTS generation failed" },
        { status: response.status }
      );
    }

    // Stream audio response back to client
    const audioData = await response.arrayBuffer();
    
    return new NextResponse(audioData, {
      status: 200,
      headers: {
        "Content-Type": "audio/mpeg",
        "Content-Length": audioData.byteLength.toString(),
        "X-Voice-Used": response.headers.get("X-Voice-Used") || "unknown",
        "X-Processing-Time": response.headers.get("X-Processing-Time") || "0s",
      },
    });
  } catch (error) {
    console.error("[TTS Proxy] Error:", error);
    return NextResponse.json(
      {
        status: "error",
        message: "Text-to-speech service unavailable. Please try again.",
      },
      { status: 502 }
    );
  }
}

/**
 * GET /api/ocean/tts/voices - List available voices
 */
export async function GET() {
  try {
    const response = await fetch(`${OCEAN_CORE_URL}/api/v1/tts/voices`);
    const data = await response.json();
    return NextResponse.json(data);
  } catch {
    return NextResponse.json(
      { 
        status: "error", 
        message: "Could not fetch voices list",
        fallback: {
          en: "en-US-AriaNeural",
          sq: "en-GB-SoniaNeural",
          de: "de-DE-KatjaNeural",
        }
      },
      { status: 502 }
    );
  }
}

