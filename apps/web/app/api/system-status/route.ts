import { NextResponse } from "next/server";

// SERVER-TO-SERVER: Use localhost in development, Docker container name in production
// In development: localhost:8000
// In production (Docker): kloud-api:8000
const isDev = process.env.NODE_ENV === "development";
const API_INTERNAL =
  process.env.API_INTERNAL_URL ||
  (isDev ? "http://localhost:8000" : "http://kloud-api:8000");

export const dynamic = "force-dynamic";
export const revalidate = 0;
export async function GET() {
  try {
    const upstream = await fetch(`${API_INTERNAL}/status`, {
      headers: { Accept: "application/json" },
      cache: "no-store",
    });

    if (!upstream.ok) {
      const body = await upstream.text();
      throw new Error(`Upstream responded ${upstream.status}: ${body}`);
    }

    const payload = await upstream.json();
    return NextResponse.json(
      { success: true, data: payload },
      {
        headers: {
          "Cache-Control": "no-cache, no-store, must-revalidate",
          "Access-Control-Allow-Origin": "*",
        },
      },
    );
  } catch (error: unknown) {
    console.error("[system-status] error:", error);
    const fallback = {
      timestamp: new Date().toISOString(),
      instance_id: "fallback",
      status: "error",
      uptime: "N/A",
      memory: { used: 0, total: 0 },
      system: {
        cpu_percent: 0,
        memory_percent: 0,
        disk_percent: 0,
        hostname: "unknown",
      },
    };
    return NextResponse.json(
      { success: false, error: "upstream_unavailable", data: fallback },
      {
        status: 502,
        headers: {
          "Cache-Control": "no-cache, no-store, must-revalidate",
          "Access-Control-Allow-Origin": "*",
        },
      },
    );
  }
}

