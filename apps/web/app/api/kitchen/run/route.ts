import { NextRequest, NextResponse } from "next/server";
import { writeFileSync, mkdirSync, existsSync } from "fs";
import { join } from "path";
import { randomUUID } from "crypto";

const JOBS_DIR =
  process.env.KITCHEN_JOBS_DIR || join(process.cwd(), "kitchen-jobs");

interface RunRequest {
  collection: string;
  baseUrl?: string;
  priority?: number;
  environment?: Record<string, string>;
}

/**
 * POST /api/kitchen/run
 *
 * Queue a new Kitchen test run
 */
export async function POST(request: NextRequest) {
  try {
    const body: RunRequest = await request.json();

    if (!body.collection) {
      return NextResponse.json(
        { error: "Missing required field: collection" },
        { status: 400 },
      );
    }

    // Ensure jobs directory exists
    if (!existsSync(JOBS_DIR)) {
      mkdirSync(JOBS_DIR, { recursive: true });
    }

    const runId = randomUUID();
    const job = {
      runId,
      collection: body.collection,
      baseUrl: body.baseUrl || "http://localhost:8000",
      priority: body.priority || 5,
      environment: body.environment || {},
      status: "queued",
      createdAt: new Date().toISOString(),
    };

    const jobFile = join(JOBS_DIR, `${runId}.json`);
    writeFileSync(jobFile, JSON.stringify(job, null, 2));

    return NextResponse.json({
      success: true,
      runId,
      message: "Job queued successfully",
      job,
    });
  } catch (e) {
    console.error("[kitchen] Error creating job:", e);
    return NextResponse.json(
      { error: "Failed to create job", detail: String(e) },
      { status: 500 },
    );
  }
}

/**
 * GET /api/kitchen/run
 *
 * Get info about run endpoint
 */
export async function GET() {
  return NextResponse.json({
    endpoint: "/api/kitchen/run",
    method: "POST",
    description: "Queue a new Kitchen test run",
    body: {
      collection: "string (required) - Postman collection name or path",
      baseUrl: "string (optional) - Base URL for API calls",
      priority: "number (optional) - Priority 1-10, default 5",
      environment: "object (optional) - Environment variables",
    },
    example: {
      collection: "kloud-api-tests",
      baseUrl: "https://api.kloud.cloud",
      priority: 8,
    },
  });
}

