import { NextResponse } from "next/server";

export async function POST() {
  return NextResponse.json(
    {
      success: false,
      error: "Google auth is disabled by internal-auth-only policy",
    },
    { status: 410 },
  );
}

