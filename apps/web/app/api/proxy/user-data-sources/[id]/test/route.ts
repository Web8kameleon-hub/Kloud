import { NextRequest, NextResponse } from "next/server";

const API_URL =
  process.env.NODE_ENV === "production"
    ? "http://kloud-api:8000"
    : "http://127.0.0.1:8000";

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> },
) {
  try {
    const { id: sourceId } = await params;
    const userId = request.headers.get("X-User-ID") || "demo-user";

    const response = await fetch(
      `${API_URL}/api/user/data-sources/${sourceId}/test`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
          "X-User-ID": userId,
        },
      },
    );

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error("Connection test error:", error);
    return NextResponse.json(
      {
        success: false,
        error: "Test service unavailable",
      },
      { status: 500 },
    );
  }
}

