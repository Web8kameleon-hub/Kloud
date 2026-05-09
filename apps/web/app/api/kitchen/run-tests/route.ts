import { NextResponse } from "next/server";
import { v4 as uuidv4 } from "uuid";
import { writeFileSync, existsSync, mkdirSync, readdirSync } from "fs";
import { join } from "path";

// Kitchen API - Enqueue Postman/Newman test jobs
// In production, this uses a file-based queue (upgradeable to Redis/RabbitMQ)

const JOBS_DIR =
  process.env.KITCHEN_JOBS_DIR || join(process.cwd(), "kitchen-jobs");
const COLLECTIONS_DIR = join(process.cwd(), "postman-collections");

// Available collections mapping
const COLLECTIONS: Record<string, string> = {
  sovereign: "Protocol_Kitchen_Sovereign_System.postman_collection.json",
  "ultra-mega": "kloud-ultra-mega-collection.json",
  "cloud-api": "Kloud_Cloud_API.postman_collection.json",
  "real-apis": "Kloud-Cloud-Real-APIs.postman_collection.json",
  main: "kloud-cloud.postman_collection.json",
};

// Ensure jobs directory exists
function ensureJobsDir() {
  if (!existsSync(JOBS_DIR)) {
    mkdirSync(JOBS_DIR, { recursive: true });
  }
}

/**
 * POST /api/kitchen/run-tests
 *
 * Body:
 *   - collection: string (key from COLLECTIONS or full filename)
 *   - baseUrl: string (API base URL to test against)
 *   - environment?: string (environment name: production, staging, development)
 *   - priority?: number (1-10, default 5)
 *
 * Headers:
 *   - Authorization: Bearer <KITCHEN_RUN_API_KEY>
 *
 * Returns:
 *   - 202: { runId, status: "queued", estimatedStart }
 *   - 401: Unauthorized
 *   - 400: Bad request
 *   - 500: Internal error
 */
export async function POST(req: Request) {
  try {
    // Authenticate request
    const auth = req.headers.get("authorization") || "";
    const apiKey = process.env.KITCHEN_RUN_API_KEY;

    if (!apiKey) {
      console.error("[kitchen] KITCHEN_RUN_API_KEY not configured");
      return NextResponse.json(
        { error: "Service not configured" },
        { status: 503 },
      );
    }

    if (!auth.startsWith("Bearer ") || auth.split(" ")[1] !== apiKey) {
      return NextResponse.json(
        { error: "Unauthorized", message: "Invalid or missing API key" },
        { status: 401 },
      );
    }

    // Parse request body
    const body = await req.json();
    const collectionKey = body.collection || "main";
    const collection = COLLECTIONS[collectionKey] || collectionKey;
    const baseUrl =
      body.baseUrl || process.env.API_URL || "https://api.kloud.cloud";
    const environment = body.environment || "production";
    const priority = Math.min(10, Math.max(1, body.priority || 5));

    // Validate collection exists (optional check)
    const collectionPath = join(COLLECTIONS_DIR, collection);
    const collectionExists =
      existsSync(collectionPath) || existsSync(join(process.cwd(), collection));

    // Generate unique run ID
    const runId = uuidv4();
    const timestamp = new Date().toISOString();

    // Create job payload
    const job = {
      runId,
      collection,
      collectionPath: collectionExists ? collectionPath : collection,
      baseUrl,
      environment,
      priority,
      status: "queued",
      createdAt: timestamp,
      requestedBy: req.headers.get("x-user-id") || "api",
      metadata: {
        userAgent: req.headers.get("user-agent"),
        ip: req.headers.get("x-forwarded-for") || req.headers.get("x-real-ip"),
      },
    };

    // Ensure directory and write job file
    ensureJobsDir();
    const jobFile = join(JOBS_DIR, `${runId}.json`);
    writeFileSync(jobFile, JSON.stringify(job, null, 2));

    console.log(
      `[kitchen] Job ${runId} queued: ${collection} against ${baseUrl}`,
    );

    // Estimate start time based on queue size
    const queueSize = readdirSync(JOBS_DIR).filter(
      (f) => f.endsWith(".json") && !f.includes(".done"),
    ).length;
    const estimatedMinutes = queueSize * 2; // ~2 min per job estimate

    return NextResponse.json(
      {
        runId,
        status: "queued",
        collection,
        baseUrl,
        environment,
        queuePosition: queueSize,
        estimatedStart: new Date(
          Date.now() + estimatedMinutes * 60000,
        ).toISOString(),
        statusUrl: `/api/kitchen/status/${runId}`,
        reportUrl: `/api/kitchen/reports/${runId}`,
      },
      { status: 202 },
    );
  } catch (error) {
    console.error("[kitchen] Error enqueueing job:", error);
    return NextResponse.json(
      { error: "Failed to enqueue job", detail: String(error) },
      { status: 500 },
    );
  }
}

/**
 * GET /api/kitchen/run-tests
 *
 * Returns available collections and API documentation
 */
export async function GET() {
  return NextResponse.json({
    service: "Kitchen Test Runner",
    version: "1.0.0",
    description:
      "API for running Postman/Newman tests against Kloud services",
    collections: Object.entries(COLLECTIONS).map(([key, file]) => ({
      key,
      file,
      description: getCollectionDescription(key),
    })),
    endpoints: {
      "POST /api/kitchen/run-tests": "Queue a new test run",
      "GET /api/kitchen/status/:runId": "Get status of a test run",
      "GET /api/kitchen/reports/:runId": "Get HTML report for a test run",
      "GET /api/kitchen/queue": "View current queue status",
    },
    authentication: "Bearer token in Authorization header",
    example: {
      method: "POST",
      headers: { Authorization: "Bearer <your-api-key>" },
      body: {
        collection: "main",
        baseUrl: "https://api.kloud.cloud",
        environment: "production",
      },
    },
  });
}

function getCollectionDescription(key: string): string {
  const descriptions: Record<string, string> = {
    sovereign: "Protocol Kitchen Sovereign System - Core protocol tests",
    "ultra-mega": "Ultra Mega Collection - Comprehensive API tests",
    "cloud-api": "Cloud API Collection - Main cloud service tests",
    "real-apis": "Real APIs Collection - Production endpoint tests",
    main: "Main Collection - Standard test suite",
  };
  return descriptions[key] || "Postman collection";
}

