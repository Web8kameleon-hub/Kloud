import { NextResponse } from "next/server";
import { startGoogleAuth } from "@/lib/internal-auth";

export async function POST(request: Request) {
  try {
    const body = (await request.json()) as { returnUrl?: string };
    const result = await startGoogleAuth(body.returnUrl);
    return NextResponse.json(result);
  } catch (error) {
    const message = error instanceof Error ? error.message : "Google auth start failed";
    return NextResponse.json({ success: false, error: message }, { status: 400 });
  }
}

