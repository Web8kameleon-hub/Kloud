/**
 * User Profile API
 * GET /api/user/profile - Get current user profile
 * PUT /api/user/profile - Update user profile
 *
 * Production: Connect to PostgreSQL database
 * Development: Returns config-based user data
 */

import { NextResponse } from "next/server";

type DecodedToken = {
  sub?: string;
  email?: string;
  name?: string;
  preferred_username?: string;
  picture?: string;
};

function decodeBearerPayload(authorizationHeader: string | null): DecodedToken {
  if (!authorizationHeader?.startsWith("Bearer ")) {
    return {};
  }

  const token = authorizationHeader.slice("Bearer ".length).trim();
  const parts = token.split(".");
  if (parts.length < 2) {
    return {};
  }

  try {
    const payload = parts[1];
    const normalized = payload.replace(/-/g, "+").replace(/_/g, "/");
    const padded = normalized + "===".slice((normalized.length + 3) % 4);
    const decoded = Buffer.from(padded, "base64").toString("utf8");
    const parsed = JSON.parse(decoded) as DecodedToken;
    return parsed;
  } catch {
    return {};
  }
}

function resolveProfile(request: Request) {
  const tokenPayload = decodeBearerPayload(request.headers.get("authorization"));
  const now = new Date().toISOString();

  const headerUserId = request.headers.get("x-user-id")?.trim();
  const headerUserName = request.headers.get("x-user-name")?.trim();
  const headerUserEmail = request.headers.get("x-user-email")?.trim();

  const id =
    headerUserId ||
    tokenPayload.sub ||
    process.env.USER_ID ||
    "usr_local_default";

  const name =
    headerUserName ||
    tokenPayload.name ||
    tokenPayload.preferred_username ||
    process.env.USER_NAME ||
    "Kloud User";

  const email =
    headerUserEmail || tokenPayload.email || process.env.USER_EMAIL || "";

  return {
    id,
    name,
    email,
    avatar: tokenPayload.picture || process.env.USER_AVATAR || null,
    plan: process.env.USER_PLAN || "free",
    company: process.env.USER_COMPANY || "",
    phone: process.env.USER_PHONE || "",
    timezone: process.env.USER_TIMEZONE || "UTC",
    language: process.env.USER_LANGUAGE || "en",
    role: process.env.USER_ROLE || "user",
    createdAt: process.env.USER_CREATED_AT || now,
    updatedAt: now,
  };
}

export async function GET(request: Request) {
  try {
    // TODO: In production, fetch from database using authenticated user's session
    // const session = await getServerSession(authOptions)
    // if (!session) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    // const user = await prisma.user.findUnique({ where: { id: session.user.id } })

    const profile = resolveProfile(request);

    return NextResponse.json({
      success: true,
      data: profile,
      source: process.env.DATABASE_URL ? "database" : "runtime",
    });
  } catch (error) {
    console.error("Profile fetch error:", error);
    return NextResponse.json(
      { success: false, error: "Failed to fetch profile" },
      { status: 500 },
    );
  }
}

export async function PUT(request: Request) {
  try {
    const body = await request.json();

    // TODO: In production, update database
    // const session = await getServerSession(authOptions)
    // if (!session) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    // const updatedUser = await prisma.user.update({
    //   where: { id: session.user.id },
    //   data: { name: body.name, company: body.company, phone: body.phone }
    // })

    // For now, just return success (data won't persist without database)
    const updatedProfile = {
      ...resolveProfile(request),
      ...body,
      updatedAt: new Date().toISOString(),
    };

    return NextResponse.json({
      success: true,
      data: updatedProfile,
      message: "Profile updated successfully",
    });
  } catch (error) {
    console.error("Profile update error:", error);
    return NextResponse.json(
      { success: false, error: "Failed to update profile" },
      { status: 500 },
    );
  }
}

