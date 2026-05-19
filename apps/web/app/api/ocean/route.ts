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
const OCEAN_CORE_URL =
  process.env.OCEAN_INTERNAL_URL ||
  process.env.OCEAN_CORE_URL ||
  "http://ocean-core:8030";
const GLOBAL_AI_URL =
  process.env.AI_9999_URL ||
  "http://ai-global-9999:9999";

const OCEAN_CHAT_URL = `${OCEAN_CORE_URL}/api/v1/chat`;
const GLOBAL_CHAT_URL = `${GLOBAL_AI_URL}/api/v1/chat`;

interface CuriosityResponse {
  answer: string;
  sources: Array<Record<string, unknown>>;
  confidence: number;
  reasoning_chain?: string[];
  backend?: "global-9999" | "ocean-core";
}

/**
 * Health check for Ocean-Core service
 */
async function checkOceanCoreHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${OCEAN_CORE_URL}/health`, {
      method: "GET",
    });
    return response.ok;
  } catch {
    return false;
  }
}

/**
 * Query the Ocean Core chat endpoint configured in Docker
 */
async function queryOceanCore(
  question: string,
  language: string,
  resonanceProfile: string,
  resonanceNdb: number,
): Promise<CuriosityResponse | null> {
  try {
    const response = await fetch(OCEAN_CHAT_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: question,
        language,
        mode: resonanceProfile,
        resonance_profile: resonanceProfile,
        resonance_ndb: resonanceNdb,
      }),
    });

    if (response.ok) {
      const data = await response.json();
      return {
        answer: data.response || data.answer || data.persona_answer || "",
        sources: data.sources_consulted || data.sources || [],
        confidence: data.confidence || 0.7,
        reasoning_chain: data.reasoning_chain || [],
        backend: "ocean-core",
      };
    }
    console.error(`Curiosity Ocean returned ${response.status}`);
    return null;
  } catch (error) {
    console.error("Curiosity Ocean connection failed:", error);
    return null;
  }
}

async function queryGlobal9999(
  question: string,
  language: string,
  resonanceProfile: string,
  resonanceNdb: number,
): Promise<CuriosityResponse | null> {
  try {
    const response = await fetch(GLOBAL_CHAT_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: question,
        query: question,
        language_hint: language,
        mode: resonanceProfile,
        resonance_profile: resonanceProfile,
        resonance_ndb: resonanceNdb,
        wwwmmm_gate: "active",
      }),
    });

    if (!response.ok) {
      console.error(`Global 9999 returned ${response.status}`);
      return null;
    }

    const data = await response.json();
    return {
      answer: data.response || data.answer || data.persona_answer || "",
      sources: data.sources_consulted || data.sources || [],
      confidence: data.confidence || 0.82,
      reasoning_chain: data.reasoning_chain || [],
      backend: "global-9999",
    };
  } catch (error) {
    console.error("Global 9999 connection failed:", error);
    return null;
  }
}

async function queryCuriosityElastic(
  question: string,
  language: string,
  resonanceProfile: string,
  resonanceNdb: number,
): Promise<CuriosityResponse | null> {
  const attempts = [
    queryGlobal9999(question, language, resonanceProfile, resonanceNdb),
    queryOceanCore(question, language, resonanceProfile, resonanceNdb),
  ].map(async (p) => {
    const result = await p;
    if (!result?.answer) {
      throw new Error("empty_response");
    }
    return result;
  });

  try {
    return await Promise.any(attempts);
  } catch {
    return null;
  }
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const question = body.question || body.message;
    const curiosity_level = body.curiosity_level || "curious";
    const language = body.language || "en";
    const resonanceProfileMap: Record<string, string> = {
      curious: "normal",
      wild: "deep",
      chaos: "exploratory",
      genius: "expert",
    };
    const resonanceNdbMap: Record<string, number> = {
      curious: 0.74,
      wild: 0.82,
      chaos: 0.88,
      genius: 0.93,
    };
    const resonanceProfile = body.resonance_profile || resonanceProfileMap[curiosity_level] || "normal";
    const resonanceNdb = Number(body.resonance_ndb ?? resonanceNdbMap[curiosity_level] ?? 0.74);

    if (!question?.trim()) {
      return NextResponse.json(
        { error: "Question is required" },
        { status: 400 },
      );
    }

    const oceanResponse = await queryCuriosityElastic(question, language, resonanceProfile, resonanceNdb);

    if (oceanResponse) {
      return NextResponse.json({
        response: oceanResponse.answer,
        ocean_response: oceanResponse.answer,
        persona_answer: oceanResponse.answer,
        curiosity_threads: [],
        rabbit_holes: [],
        next_questions: [],
        key_findings: [],
        resonance_profile: resonanceProfile,
        resonance_ndb: resonanceNdb,
        source:
          oceanResponse.backend === "global-9999"
            ? "Clisonix Global AI (Light)"
            : "Curiosity Ocean",
        confidence: oceanResponse.confidence,
        sources_consulted: oceanResponse.sources || [],
        reasoning_chain: oceanResponse.reasoning_chain || [],
        backend: oceanResponse.backend,
      });
    }

    return NextResponse.json(
      {
        error: "No upstream AI backend returned a valid response",
        source: "upstream",
        resonance_profile: resonanceProfile,
        resonance_ndb: resonanceNdb,
        backend_attempts: ["global-9999", "ocean-core"],
      },
      { status: 502 },
    );
  } catch (error: unknown) {
    const errMsg = error instanceof Error ? error.message : "Unknown";
    console.error("Ocean API error:", errMsg);
    return NextResponse.json(
      {
        error: "Ocean API internal error",
        details: errMsg,
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
    global_9999_url: GLOBAL_AI_URL,
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

