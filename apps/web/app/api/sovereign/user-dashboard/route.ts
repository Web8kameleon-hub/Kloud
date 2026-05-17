import { NextRequest, NextResponse } from "next/server";

export const dynamic = "force-dynamic";
export const revalidate = 0;

type StatusPayload = {
  metrics?: {
    active_peers?: number;
    avg_latency_ms?: number;
    bandwidth_kbps?: number;
    load?: number;
  };
  ndb_score?: number;
  ndb_delta?: number;
  ndb_threshold?: number;
  state?: string;
  tide?: string;
};

type SecurityEvent = {
  timestamp_ms: number;
  endpoint: string;
  action: string;
  stigma_level: number;
  ndb_score: number;
  outcome: string;
};

type SecurityPayload = {
  node_id?: number;
  tide?: string;
  ndb_score?: number;
  ndb_delta?: number;
  ndb_threshold?: number;
  high_risk?: boolean;
  event_count?: number;
};

type LocalStatePayload = {
  state?: Record<string, string>;
};

function toCsv(events: SecurityEvent[]): string {
  const header = ["timestamp_ms", "endpoint", "action", "stigma_level", "ndb_score", "outcome"];
  const rows = events.map((event) => [
    String(event.timestamp_ms),
    event.endpoint,
    event.action,
    String(event.stigma_level),
    String(event.ndb_score),
    event.outcome,
  ]);

  return [header, ...rows]
    .map((row) => row.map((value) => `"${String(value).replaceAll('"', '""')}"`).join(","))
    .join("\n");
}

function decodeBase64Json(input: string): Record<string, unknown> | null {
  try {
    const raw = Buffer.from(input, "base64").toString("utf-8");
    const parsed = JSON.parse(raw) as Record<string, unknown>;
    return parsed;
  } catch {
    return null;
  }
}

export async function GET(request: NextRequest) {
  const format = request.nextUrl.searchParams.get("format")?.toLowerCase();
  const base =
    process.env.KLOUD_PUBLIC_STATUS_BASE ||
    process.env.NEXT_PUBLIC_KLOUD_STATUS_BASE ||
    "https://kloud.aiagi.io";

  const [statusRes, securityRes, eventsRes, localStateRes] = await Promise.allSettled([
    fetch(`${base}/status`, { cache: "no-store" }),
    fetch(`${base}/security/status`, { cache: "no-store" }),
    fetch(`${base}/security/events?limit=25`, { cache: "no-store" }),
    fetch(`${base}/state`, { cache: "no-store" }),
  ]);

  const status: StatusPayload =
    statusRes.status === "fulfilled" && statusRes.value.ok
      ? ((await statusRes.value.json()) as StatusPayload)
      : {};

  const security: SecurityPayload =
    securityRes.status === "fulfilled" && securityRes.value.ok
      ? ((await securityRes.value.json()) as SecurityPayload)
      : {};

  const events: SecurityEvent[] =
    eventsRes.status === "fulfilled" && eventsRes.value.ok
      ? ((await eventsRes.value.json()) as SecurityEvent[])
      : [];

  const localState: LocalStatePayload =
    localStateRes.status === "fulfilled" && localStateRes.value.ok
      ? ((await localStateRes.value.json()) as LocalStatePayload)
      : {};

  const decodedState = Object.entries(localState.state || {}).map(([key, value]) => ({
    key,
    raw: value,
    decoded: decodeBase64Json(value),
  }));

  if (format === "csv") {
    return new NextResponse(toCsv(events), {
      headers: {
        "Content-Type": "text/csv; charset=utf-8",
        "Content-Disposition": 'attachment; filename="kloud-sovereign-events.csv"',
        "Cache-Control": "no-cache, no-store, must-revalidate",
      },
    });
  }

  return NextResponse.json({
    success: true,
    source: base,
    timestamp_utc: new Date().toISOString(),
    status,
    security,
    events,
    localState: decodedState,
  });
}
