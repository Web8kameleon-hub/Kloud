import { NextResponse } from "next/server";
import { promises as fs } from "fs";
import path from "path";

/**
 * OWNER-ONLY OTP SINK
 * ===================
 * Real, non-fake OTP delivery endpoint used as AUTH_OTP_WEBHOOK_URL.
 *
 * Security:
 * - Requires header `X-OTP-Webhook-Key` to match env `AUTH_OTP_WEBHOOK_KEY`.
 * - Never returns the code in the response.
 * - Appends codes to an owner-only file inside the durable runtime mount,
 *   readable only by the server operator (docker exec / host bind mount).
 *
 * This keeps OTPs out of the public API surface (production-safe) while giving
 * the operator a real delivery inbox until an email/SMS provider is wired.
 */

const OTP_INBOX_DIR =
  process.env.OTP_INBOX_PATH ||
  path.join(process.cwd(), ".runtime", "otp-inbox");
const OTP_INBOX_FILE = path.join(OTP_INBOX_DIR, "otp.jsonl");

export async function POST(request: Request) {
  const expectedKey = process.env.AUTH_OTP_WEBHOOK_KEY || "";
  const providedKey = request.headers.get("x-otp-webhook-key") || "";

  if (!expectedKey || providedKey !== expectedKey) {
    return NextResponse.json(
      { success: false, error: "unauthorized" },
      { status: 401 },
    );
  }

  let body: { channel?: string; target?: string; code?: string };
  try {
    body = (await request.json()) as typeof body;
  } catch {
    return NextResponse.json(
      { success: false, error: "invalid_json" },
      { status: 400 },
    );
  }

  const record = {
    timestamp: new Date().toISOString(),
    channel: body.channel || "unknown",
    target: body.target || "unknown",
    code: body.code || "",
  };

  try {
    await fs.mkdir(OTP_INBOX_DIR, { recursive: true });
    await fs.appendFile(OTP_INBOX_FILE, JSON.stringify(record) + "\n", "utf-8");
  } catch (err) {
    return NextResponse.json(
      {
        success: false,
        error: "otp_inbox_write_failed",
        detail: err instanceof Error ? err.message : String(err),
      },
      { status: 503 },
    );
  }

  return NextResponse.json({ success: true, delivered: true });
}
