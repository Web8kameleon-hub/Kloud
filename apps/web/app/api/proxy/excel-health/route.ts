import { NextResponse } from "next/server";

// Excel Service - Future microservice (not deployed yet)
// Falls back to main API health when Excel service is not available
const EXCEL_API = process.env.EXCEL_API_URL || null;
const isDev = process.env.NODE_ENV === "development";
const API_INTERNAL =
  process.env.API_INTERNAL_URL ||
  (isDev ? "http://localhost:8000" : "http://kloud-api:8000");

export async function GET() {
  // If Excel microservice is configured, check it directly
  if (EXCEL_API) {
    try {
      const response = await fetch(`${EXCEL_API}/health`, {
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
        { error: "Failed to connect to Excel Service", details: String(error) },
        { status: 503 },
      );
    }
  }

  // Excel microservice not deployed - return status from main API
  try {
    const response = await fetch(`${API_INTERNAL}/health`, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
      signal: AbortSignal.timeout(5000),
    });

    if (response.ok) {
      return NextResponse.json(
        {
          service: "excel",
          status: "integrated",
          message: "Excel functionality available via main API",
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
        service: "excel",
        status: "pending",
        message: "Excel microservice not deployed",
      },
      { status: 200 },
    );
  }
}

