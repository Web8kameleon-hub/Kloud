import { NextResponse } from "next/server";

/**
 * CURIOSITY OCEAN API - Powered by Ocean-Core Knowledge Engine
 *
 * UPGRADED: Now connects to REAL AI backend with 14 Specialist Personas
 * NO MORE fixed responses - connects to ocean-core SaaS
 *
 * Ocean-Core Features:
 * - 14 Expert Personas for domain-specific responses
 * - Knowledge Engine with multi-source aggregation
 * - Curiosity Threads for deeper exploration
 * - Real-time analysis and intelligent responses
 *
 * Personas available:
 * - neuroscience_expert, ai_specialist, data_analyst
 * - systems_engineer, security_expert, medical_advisor
 * - wellness_coach, creative_director, performance_optimizer
 * - research_scientist, business_strategist, technical_writer
 * - ux_specialist, ethics_advisor
 */

// Detect environment for correct API URL
const isDev = process.env.NODE_ENV !== "production";
const CURIOSITY_URL =
  process.env.CURIOSITY_URL ||
  (isDev ? "http://localhost:8019" : "http://curiosity:8019");

interface CuriosityResponse {
  answer: string;
  sources: Array<Record<string, unknown>>;
  confidence: number;
  reasoning_chain?: string[];
}

/**
 * Query the Curiosity Ocean service configured in Docker
 */
async function queryCuriosity(
  question: string,
  language: string,
): Promise<CuriosityResponse | null> {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000);

    const response = await fetch(`${CURIOSITY_URL}/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        query: question,
        language,
      }),
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (response.ok) {
      return (await response.json()) as CuriosityResponse;
    }
    console.error(`Curiosity Ocean returned ${response.status}`);
    return null;
  } catch (error) {
    console.error("Curiosity Ocean connection failed:", error);
    return null;
  }
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const question = body.question || body.message;
    const curiosity_level = body.curiosity_level || "curious";
    const language = body.language || "en";

    if (!question?.trim()) {
      return NextResponse.json(
        { error: "Question is required" },
        { status: 400 },
      );
    }

    const oceanResponse = await queryCuriosity(question, language);

    if (oceanResponse) {
      return NextResponse.json({
        response: oceanResponse.answer,
        ocean_response: oceanResponse.answer,
        persona_answer: oceanResponse.answer,
        curiosity_threads: [],
        rabbit_holes: [],
        next_questions: [],
        key_findings: [],
        mode: curiosity_level,
        source: "Curiosity Ocean",
        confidence: oceanResponse.confidence,
        sources_consulted: oceanResponse.sources || [],
        reasoning_chain: oceanResponse.reasoning_chain || [],
      });
    }

    const fallbackResponse = `🌊 **Curiosity Ocean is offline right now.**

Your question: "${question}"

The frontend is configured for the Docker curiosity service, not Clerk/Redis.

**To start Curiosity Ocean:**
\`\`\`bash
docker compose up -d --build curiosity
\`\`\`

Or locally:
\`\`\`bash
cd services/curiosity_ocean
$env:PORT=8019
python -m uvicorn api:app --host 127.0.0.1 --port 8019
\`\`\``;

    return NextResponse.json({
      ocean_response: fallbackResponse,
      response: fallbackResponse,
      rabbit_holes: ["Start Curiosity service", "Check port 8019"],
      next_questions: ["Is Curiosity Ocean running?", "What sources are available?"],
      mode: curiosity_level,
      source: "Fallback (Curiosity offline)",
      curiosity_status: "offline",
      startup_hint: `docker compose up -d --build curiosity`,
    });
  } catch (error: unknown) {
    const errMsg = error instanceof Error ? error.message : "Unknown";
    console.error("Ocean API error:", errMsg);
    return NextResponse.json(
      {
        ocean_response: "🌊 The Ocean is recalibrating. Please try again.",
        rabbit_holes: [],
        next_questions: [],
        error: errMsg,
      },
      { status: 500 },
    );
  }
}

/**
 * GET: Health check and status
 */
export async function GET() {
  const oceanCoreHealthy = await checkOceanCoreHealth();

  return NextResponse.json({
    status: oceanCoreHealthy ? "connected" : "ocean-core-offline",
    ocean_core_url: OCEAN_CORE_URL,
    environment: isDev ? "development" : "production",
    message: oceanCoreHealthy
      ? "🌊 Ocean-Core Knowledge Engine is active with 14 Specialist Personas"
      : "⚠️ Ocean-Core offline. Start with: cd ocean-core && python -m uvicorn ocean_api:app --port 8030",
    features: [
      "14 Specialist Personas",
      "Knowledge Engine",
      "Multi-source aggregation",
      "Curiosity Threads",
      "Domain-specific routing",
    ],
  });
}

