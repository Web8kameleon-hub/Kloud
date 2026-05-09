import { NextResponse } from "next/server";

// Marketplace API - Future microservice (not deployed yet)
// Falls back to main API health when Marketplace service is not available
const MARKETPLACE_API = process.env.MARKETPLACE_API_URL || null;
const isDev = process.env.NODE_ENV === "development";
const API_INTERNAL =
  process.env.API_INTERNAL_URL ||
  (isDev ? "http://localhost:8000" : "http://kloud-api:8000");

export async function GET() {
  // If Marketplace microservice is configured, check it directly
  if (MARKETPLACE_API) {
    try {
      const response = await fetch(`${MARKETPLACE_API}/health`, {
        method: "GET",
        headers: { "Content-Type": "application/json" },
        signal: AbortSignal.timeout(5000),
      });

      if (!response.ok) {
        return NextResponse.json(
          { error: "API returned non-200 status", status: response.status },
          { status: response.status },
        );
      }

      const data = await response.json();
      return NextResponse.json(data, { status: 200 });
    } catch (error) {
      return NextResponse.json(
        { error: "Failed to connect to Marketplace", details: String(error) },
        { status: 503 },
      );
    }
  }

  // Marketplace microservice not deployed - return status from main API
  try {
    const response = await fetch(`${API_INTERNAL}/health`, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
      signal: AbortSignal.timeout(5000),
    });

    if (response.ok) {
      return NextResponse.json(
        {
          service: "marketplace",
          status: "integrated",
          message: "Marketplace functionality available via main API",
          main_api: "operational",
        },
        { status: 200 },
      );
    }
    return NextResponse.json(
      { error: "Main API unavailable" },
      { status: 503 },
    );
  } catch (_error) {
    return NextResponse.json(
      {
        service: "marketplace",
        status: "pending",
        message: "Marketplace microservice not deployed",
      },
      { status: 200 },
    );
  }
}

