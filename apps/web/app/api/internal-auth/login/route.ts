import { NextResponse } from "next/server";
import { loginInternalUser } from "@/lib/internal-auth";

export async function POST(request: Request) {
  try {
    const body = (await request.json()) as {
      identifier?: string;
      password?: string;
      channel?: "sms" | "email";
    };

    const result = await loginInternalUser({
      identifier: body.identifier || "",
      password: body.password || "",
      channel: body.channel,
    });

    return NextResponse.json(result);
  } catch (error) {
    const message = error instanceof Error ? error.message : "Login failed";
    return NextResponse.json({ success: false, error: message }, { status: 400 });
  }
}

