import { NextResponse } from "next/server";
import { verifyInternalOtp } from "@/lib/internal-auth";

export async function POST(request: Request) {
  try {
    const body = (await request.json()) as {
      challengeId?: string;
      code?: string;
    };

    const result = await verifyInternalOtp({
      challengeId: body.challengeId || "",
      code: body.code || "",
    });

    return NextResponse.json(result);
  } catch (error) {
    const message = error instanceof Error ? error.message : "OTP verification failed";
    return NextResponse.json({ success: false, error: message }, { status: 400 });
  }
}

