import { promises as fs } from "fs";
import os from "os";
import path from "path";

/**
 * STIGMA MEMORY - BINARY NODEDB PATTERN
 *
 * Lightweight trace format:
 * - Binary frame encoding (no JSON parsing overhead)
 * - Fixed-field header (timestamp, resonance score, stigma level, flags)
 * - Variable-length string fields (16-bit TLV)
 * - NodeDB fluid persistence (mandatory policy gate)
 * - JSON metrics export (secondary reporting only)
 *
 * No fake data: Optional NodeDB reported as not_configured/error.
 */

export type StigmaWriteResult = {
  status: "persisted" | "not_configured" | "error";
  statusCode?: number;
  transport?: string;
  bytes?: number;
  message?: string;
};

type AuthEvent = {
  timestamp: string;
  nodeId: string;
  event: string;
  success: boolean;
  userId?: string;
  identifier?: string;
  channel?: "sms" | "email";
  remember?: boolean;
  latencyMs?: number;
  ip?: string;
  userAgent?: string;
  extra?: Record<string, unknown>;
};

type AuthMetrics = {
  updatedAt: string;
  nodeId: string;
  totals: {
    register: number;
    login: number;
    otpVerified: number;
    tokenValidated: number;
    failed: number;
    sms: number;
    email: number;
    rememberEnabled: number;
  };
  avgLatencyMs: number;
  samples: number;
};

const STIGMA_DIR =
  process.env.STIGMA_MEMORY_PATH ||
  path.join(process.cwd(), ".runtime", "stigma-memory");
const METRICS_PATH = path.join(STIGMA_DIR, "auth-metrics.json");
const NODEDB_FLUID_URL = process.env.STIGMA_NODEDB_URL || "";
const REQUIRE_NODEDB_FLUID =
  process.env.REQUIRE_STIGMA_NODEDB === "1" ||
  process.env.REQUIRE_STIGMA_NODEDB === "true";
const REQUEST_TIMEOUT_MS = 2500; // 2.5s timeout (non-blocking)

let writeQueue: Promise<void> = Promise.resolve();

function getNodeId(): string {
  return process.env.KLOUD_NODE_ID || os.hostname();
}

/**
 * Pack uint32 (timestamp in seconds) as big-endian bytes
 */
function packU32Time(timestamp: Date): Buffer {
  const seconds = Math.floor(timestamp.getTime() / 1000);
  const buf = Buffer.allocUnsafe(4);
  buf.writeUInt32BE(seconds, 0);
  return buf;
}

/**
 * Pack 16-bit length + UTF-8 string (variable-length TLV)
 */
function packU16Text(value: string): Buffer {
  const utf8 = Buffer.from(value, "utf-8");
  if (utf8.length > 65535) {
    throw new Error("stigma_field_text_too_long");
  }
  const len = Buffer.allocUnsafe(2);
  len.writeUInt16BE(utf8.length, 0);
  return Buffer.concat([len, utf8]);
}

/**
 * Pack boolean as single byte (0x00 or 0x01)
 */
function packBool(value: boolean): Buffer {
  return Buffer.from([value ? 0x01 : 0x00]);
}

/**
 * Pack float64 (double) as big-endian 8 bytes
 */
function packF64(value: number): Buffer {
  const buf = Buffer.allocUnsafe(8);
  buf.writeDoubleBE(value, 0);
  return buf;
}

/**
 * Build binary auth event frame
 *
 * Format:
 * [1 byte] version (0x01)
 * [4 bytes] timestamp (uint32 seconds)
 * [8 bytes] latency_ms (float64)
 * [1 byte] event_type (0=register, 1=login, 2=otp_verified, 3=token_validated, 4=failed)
 * [1 byte] success flag
 * [1 byte] channel (0=none, 1=sms, 2=email)
 * [1 byte] remember flag
 * [2+N bytes] nodeId (TLV)
 * [2+N bytes] event_name (TLV)
 * [2+N bytes] userId (TLV, optional empty)
 * [2+N bytes] identifier (TLV, optional empty)
 * [2+N bytes] ip (TLV, optional empty)
 * [2+N bytes] userAgent (TLV, optional empty)
 */
function buildAuthEventFrame(event: AuthEvent): Buffer {
  const eventTypeMap: Record<string, number> = {
    register: 0,
    login: 1,
    otp_verified: 2,
    token_validated: 3,
    failed: 4,
  };

  const channelMap: Record<string, number> = {
    none: 0,
    sms: 1,
    email: 2,
  };

  const parts: Buffer[] = [];

  // Version
  parts.push(Buffer.from([0x01]));

  // Timestamp (uint32)
  parts.push(packU32Time(new Date(event.timestamp)));

  // Latency (float64)
  parts.push(packF64(event.latencyMs || 0.0));

  // Event type (uint8)
  const eventNum = eventTypeMap[event.event] ?? 4;
  parts.push(Buffer.from([eventNum]));

  // Success flag
  parts.push(packBool(event.success));

  // Channel
  const channelNum = event.channel ? channelMap[event.channel] : 0;
  parts.push(Buffer.from([channelNum]));

  // Remember flag
  parts.push(packBool(event.remember || false));

  // Variable-length fields (TLV)
  parts.push(packU16Text(event.nodeId));
  parts.push(packU16Text(event.event));
  parts.push(packU16Text(event.userId || ""));
  parts.push(packU16Text(event.identifier || ""));
  parts.push(packU16Text(event.ip || ""));
  parts.push(packU16Text(event.userAgent || ""));

  return Buffer.concat(parts);
}

/**
 * Write auth event to NodeDB via binary HTTP POST
 * Non-blocking: 2.5s timeout, no impact on auth flow
 */
async function writeToNodeDB(
  event: AuthEvent,
): Promise<StigmaWriteResult> {
  if (!NODEDB_FLUID_URL) {
    return { status: "not_configured" };
  }

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

  try {
    const frame = buildAuthEventFrame(event);

    const response = await fetch(NODEDB_FLUID_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/octet-stream",
        "X-Kloud-Event-Type": "auth_event",
        "X-Kloud-Request-Id": `auth_${Date.now()}`,
        "X-Kloud-Node-Id": event.nodeId,
      },
      body: frame as unknown as BodyInit,
      signal: controller.signal,
    });

    if (200 <= response.status && response.status < 300) {
      return {
        status: "persisted",
        statusCode: response.status,
        transport: "binary",
        bytes: frame.length,
      };
    }

    return {
      status: "error",
      statusCode: response.status,
      message: "nodedb_rejected_event",
    };
  } catch (err) {
    const message =
      err instanceof Error
        ? err.name === "AbortError"
          ? "nodedb_timeout"
          : err.message
        : String(err);

    return {
      status: "error",
      message,
    };
  } finally {
    clearTimeout(timeoutId);
  }
}

async function readMetrics(): Promise<AuthMetrics> {
  try {
    const text = await fs.readFile(METRICS_PATH, "utf-8");
    return JSON.parse(text) as AuthMetrics;
  } catch {
    return {
      updatedAt: new Date().toISOString(),
      nodeId: getNodeId(),
      totals: {
        register: 0,
        login: 0,
        otpVerified: 0,
        tokenValidated: 0,
        failed: 0,
        sms: 0,
        email: 0,
        rememberEnabled: 0,
      },
      avgLatencyMs: 0,
      samples: 0,
    };
  }
}

function updateAggregate(metrics: AuthMetrics, event: AuthEvent): AuthMetrics {
  const next = { ...metrics };
  next.updatedAt = new Date().toISOString();
  next.nodeId = event.nodeId;

  if (event.event === "register") next.totals.register += 1;
  if (event.event === "login") next.totals.login += 1;
  if (event.event === "otp_verified") next.totals.otpVerified += 1;
  if (event.event === "token_validated") next.totals.tokenValidated += 1;
  if (!event.success) next.totals.failed += 1;
  if (event.channel === "sms") next.totals.sms += 1;
  if (event.channel === "email") next.totals.email += 1;
  if (event.remember) next.totals.rememberEnabled += 1;

  if (typeof event.latencyMs === "number") {
    const totalLatency = next.avgLatencyMs * next.samples + event.latencyMs;
    next.samples += 1;
    next.avgLatencyMs = Number((totalLatency / next.samples).toFixed(2));
  }

  return next;
}

/**
 * Write auth event with policy gate enforcement
 * Returns result with status: persisted | not_configured | error
 */
export async function writeAuthStigmaEvent(
  input: Omit<AuthEvent, "timestamp" | "nodeId">,
): Promise<StigmaWriteResult> {
  const event: AuthEvent = {
    timestamp: new Date().toISOString(),
    nodeId: getNodeId(),
    ...input,
  };

  const prev = writeQueue;
  let release!: () => void;
  writeQueue = new Promise<void>((resolve) => {
    release = resolve;
  });

  await prev;
  try {
    // Write to NodeDB (async, non-blocking). writeToNodeDB never throws.
    const ndbResult = await writeToNodeDB(event);

    // Update local metrics (real, file-based persistence). Isolate failures so a
    // read-only filesystem can never crash the auth flow (which previously caused
    // an empty 500 body → "Unexpected end of JSON input" on the client).
    let localPersisted = false;
    let localMessage: string | undefined;
    try {
      await fs.mkdir(STIGMA_DIR, { recursive: true });
      const metrics = await readMetrics();
      const updated = updateAggregate(metrics, event);
      await fs.writeFile(METRICS_PATH, JSON.stringify(updated, null, 2), "utf-8");
      localPersisted = true;
    } catch (err) {
      localMessage = err instanceof Error ? err.message : String(err);
    }

    // Honest status resolution (no fake): if NodeDB is mandatory, only its result
    // counts. Otherwise a successful local file write is real persistence.
    if (REQUIRE_NODEDB_FLUID) {
      return ndbResult;
    }
    if (ndbResult.status === "persisted") {
      return ndbResult;
    }
    if (localPersisted) {
      return {
        status: "persisted",
        transport: "local",
        message:
          ndbResult.status === "not_configured"
            ? "nodedb_not_configured_local_persisted"
            : undefined,
      };
    }
    return {
      status: "error",
      message: localMessage || ndbResult.message || "stigma_persist_failed",
    };
  } catch (err) {
    // Absolute guard: this function must never throw.
    return {
      status: "error",
      message: err instanceof Error ? err.message : String(err),
    };
  } finally {
    release();
  }
}
