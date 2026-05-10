import { NextRequest, NextResponse } from "next/server";
import { resolveBearerUser } from "@/lib/internal-auth";

export async function GET(request: NextRequest) {
  try {
    const user = await resolveBearerUser(request.headers.get("authorization"));
    if (!user) {
      return NextResponse.json({ authenticated: false }, { status: 401 });
    }

    return NextResponse.json({
      authenticated: true,
      user: {
        id: user.id,
        name: user.name,
        email: user.email,
        phone: user.phone,
        emailVerified: user.emailVerified,
        phoneVerified: user.phoneVerified,
        googleLinked: user.googleLinked,
      },
    });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Failed to get profile";
    return NextResponse.json({ authenticated: false, error: message }, { status: 400 });
  }
}

