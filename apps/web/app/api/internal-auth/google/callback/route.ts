import { NextRequest, NextResponse } from "next/server";
import { finishGoogleAuth } from "@/lib/internal-auth";

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const code = searchParams.get("code") || "";
    const state = searchParams.get("state") || "";

    const result = await finishGoogleAuth(code, state);
    return NextResponse.json(result);
  } catch (error) {
    const message = error instanceof Error ? error.message : "Google auth callback failed";
    return NextResponse.json({ success: false, error: message }, { status: 400 });
  }
}

