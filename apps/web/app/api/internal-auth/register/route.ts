import { NextResponse } from "next/server";
import { registerInternalUser } from "@/lib/internal-auth";

export async function POST(request: Request) {
  try {
    const body = (await request.json()) as {
      name?: string;
      email?: string;
      phone?: string;
      password?: string;
      channel?: "sms" | "email";
    };

    const result = await registerInternalUser({
      name: body.name,
      email: body.email,
      phone: body.phone,
      password: body.password || "",
      channel: body.channel,
    });

    return NextResponse.json(result);
  } catch (error) {
    const message = error instanceof Error ? error.message : "Register failed";
    return NextResponse.json({ success: false, error: message }, { status: 400 });
  }
}

