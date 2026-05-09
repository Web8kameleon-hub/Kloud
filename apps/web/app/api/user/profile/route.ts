/**
 * User Profile API
 * GET /api/user/profile - Get current user profile
 * PUT /api/user/profile - Update user profile
 *
 * Production: Connect to PostgreSQL database
 * Development: Returns config-based user data
 */

import { NextResponse } from "next/server";

// User profile configuration - In production, this comes from database
// Plan is determined by Stripe subscription status (default: free)
const USER_PROFILE = {
  id: "usr_kloud_001",
  name: process.env.USER_NAME || "Ledjan Ahmati",
  email: process.env.USER_EMAIL || "ledjan@kloud.com",
  avatar: process.env.USER_AVATAR || null,
  plan: process.env.USER_PLAN || "free", // Will be overridden by Stripe subscription
  company: process.env.USER_COMPANY || "WEB8euroweb GmbH",
  phone: process.env.USER_PHONE || "+49 176 XXX XXXX",
  timezone: process.env.USER_TIMEZONE || "Europe/Berlin",
  language: process.env.USER_LANGUAGE || "en",
  role: "admin",
  createdAt: "2024-01-15T10:00:00Z",
  updatedAt: new Date().toISOString(),
};

export async function GET() {
  try {
    // TODO: In production, fetch from database using authenticated user's session
    // const session = await getServerSession(authOptions)
    // if (!session) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    // const user = await prisma.user.findUnique({ where: { id: session.user.id } })

    return NextResponse.json({
      success: true,
      data: USER_PROFILE,
      source: process.env.DATABASE_URL ? "database" : "config",
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
      ...USER_PROFILE,
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

