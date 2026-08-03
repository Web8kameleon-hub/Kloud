import { NextResponse } from "next/server";

export async function POST() {
  return NextResponse.json({
    success: true,
    loggedOut: true,
    message: "Internal auth logout acknowledged on server. Clear client token/cookie.",
  });
}
