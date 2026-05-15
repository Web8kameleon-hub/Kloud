import { NextResponse } from "next/server";
import { loginInternalUser } from "@/lib/internal-auth";
import { writeAuthStigmaEvent, type StigmaWriteResult } from "@/lib/stigma-memory";

export async function POST(request: Request) {
  const startedAt = Date.now();
  try {
    const body = (await request.json()) as {
      identifier?: string;
      password?: string;
      channel?: "sms" | "email";
      remember?: boolean;
    };

    const nodeId = request.headers.get("x-kloud-node-id") || undefined;
    const ip =
      request.headers.get("x-forwarded-for")?.split(",")[0]?.trim() || undefined;
    const userAgent = request.headers.get("user-agent") || undefined;

    const result = await loginInternalUser({
      identifier: body.identifier || "",
      password: body.password || "",
      channel: body.channel,
      remember: body.remember,
      context: { nodeId, ip, userAgent },
    });

    // Policy gate: Log success and enforce NDB persistence
    // Note: userId not available until OTP verification (this is OTP challenge stage)
    const writeResult: StigmaWriteResult = await writeAuthStigmaEvent({
      event: "login",
      success: true,
      identifier: body.identifier,
      channel: body.channel,
      remember: body.remember,
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
    const message = error instanceof Error ? error.message : "Login failed";
    const latency = Date.now() - startedAt;
    const nodeId = request.headers.get("x-kloud-node-id") || undefined;
    const ip = request.headers.get("x-forwarded-for")?.split(",")[0]?.trim() || undefined;
    const userAgent = request.headers.get("user-agent") || undefined;

    // Log failure with policy enforcement
    const writeResult: StigmaWriteResult = await writeAuthStigmaEvent({
      event: "login",
      success: false,
      identifier: "unknown",
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

