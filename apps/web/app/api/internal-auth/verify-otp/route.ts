import { NextResponse } from "next/server";
import { verifyInternalOtp } from "@/lib/internal-auth";
import { writeAuthStigmaEvent, type StigmaWriteResult } from "@/lib/stigma-memory";

export async function POST(request: Request) {
  const startedAt = Date.now();
  try {
    const body = (await request.json()) as {
      challengeId?: string;
      code?: string;
    };

    const nodeId = request.headers.get("x-kloud-node-id") || undefined;
    const ip =
      request.headers.get("x-forwarded-for")?.split(",")[0]?.trim() || undefined;
    const userAgent = request.headers.get("user-agent") || undefined;

    const result = await verifyInternalOtp({
      challengeId: body.challengeId || "",
      code: body.code || "",
      context: { nodeId, ip, userAgent },
    });

    // Policy gate: Log success and enforce NDB persistence
    const writeResult: StigmaWriteResult = await writeAuthStigmaEvent({
      event: "otp_verified",
      success: true,
      userId: (result as Record<string, unknown>).userId as string | undefined,
      latencyMs: Date.now() - startedAt,
      ip,
      userAgent,
    });

    if (writeResult.status !== "persisted") {
      return NextResponse.json(
        {
          success: false,
          error: "Telemetry persistence failed",
          details: writeResult,
        },
        { status: 503 }
      );
    }

    return NextResponse.json(result);
  } catch (error) {
    const message = error instanceof Error ? error.message : "OTP verification failed";
    const latency = Date.now() - startedAt;
    const nodeId = request.headers.get("x-kloud-node-id") || undefined;
    const ip = request.headers.get("x-forwarded-for")?.split(",")[0]?.trim() || undefined;
    const userAgent = request.headers.get("user-agent") || undefined;

    // Log failure with policy enforcement
    const writeResult: StigmaWriteResult = await writeAuthStigmaEvent({
      event: "otp_verified",
      success: false,
      latencyMs: latency,
      ip,
      userAgent,
    });

    if (writeResult.status !== "persisted") {
      return NextResponse.json(
        {
          success: false,
          error: "Telemetry persistence failed",
          details: writeResult,
        },
        { status: 503 }
      );
    }

    return NextResponse.json({ success: false, error: message }, { status: 400 });
  }
}

