import { NextResponse } from "next/server";
import { registerInternalUser } from "@/lib/internal-auth";
import { writeAuthStigmaEvent, type StigmaWriteResult } from "@/lib/stigma-memory";

export async function POST(request: Request) {
  const startedAt = Date.now();
  try {
    const body = (await request.json()) as {
      name?: string;
      email?: string;
      phone?: string;
      password?: string;
      channel?: "sms" | "email";
      remember?: boolean;
    };

    const nodeId = request.headers.get("x-kloud-node-id") || undefined;
    const ip =
      request.headers.get("x-forwarded-for")?.split(",")[0]?.trim() || undefined;
    const userAgent = request.headers.get("user-agent") || undefined;

    const result = await registerInternalUser({
      name: body.name,
      email: body.email,
      phone: body.phone,
      password: body.password || "",
      channel: body.channel,
      remember: body.remember,
      context: { nodeId, ip, userAgent },
    });

    // Policy gate: Log success and enforce NDB persistence
    // Note: userId not available until OTP verification (this is OTP challenge stage)
    const writeResult: StigmaWriteResult = await writeAuthStigmaEvent({
      event: "register",
      success: true,
      identifier: body.email || body.phone,
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
    const message = error instanceof Error ? error.message : "Register failed";
    const latency = Date.now() - startedAt;
    const nodeId = request.headers.get("x-kloud-node-id") || undefined;
    const ip = request.headers.get("x-forwarded-for")?.split(",")[0]?.trim() || undefined;
    const userAgent = request.headers.get("user-agent") || undefined;

    // Log failure with policy enforcement
    const writeResult: StigmaWriteResult = await writeAuthStigmaEvent({
      event: "register",
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

