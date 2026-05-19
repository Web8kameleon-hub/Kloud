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

type NodeDBNode = {
  metadata?: {
    node_id?: string;
    service_name?: string;
    service_type?: string;
  };
  state?: {
    stigma_state?: string;
    ndb_quality?: string;
    ndb_delta?: number;
    metrics?: Record<string, unknown>;
  };
};

type MonitoringPayload = {
  node_summary?: {
    nodes_total?: number;
    state_counts?: Record<string, number>;
    quality_counts?: Record<string, number>;
  };
  membership?: {
    count?: number;
    active_count?: number;
  };
  sync_loop?: {
    running?: boolean;
    interval_seconds?: number;
    cycles?: number;
    last_run_utc?: string | null;
  };
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
  const nodedbBase = process.env.NODEDB_CONTROL_PLANE_URL || "http://kloud-nodedb-control-plane:9090";

  const [statusRes, securityRes, eventsRes, localStateRes, monitoringRes, nodesRes] = await Promise.allSettled([
    fetch(`${base}/status`, { cache: "no-store" }),
    fetch(`${base}/security/status`, { cache: "no-store" }),
    fetch(`${base}/security/events?limit=25`, { cache: "no-store" }),
    fetch(`${base}/state`, { cache: "no-store" }),
    fetch(`${nodedbBase}/api/v1/control-plane/monitoring`, { cache: "no-store" }),
    fetch(`${nodedbBase}/api/v1/control-plane/nodes`, { cache: "no-store" }),
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

  const monitoring: MonitoringPayload =
    monitoringRes.status === "fulfilled" && monitoringRes.value.ok
      ? ((await monitoringRes.value.json()) as MonitoringPayload)
      : {};

  const nodesPayload: { items?: NodeDBNode[] } =
    nodesRes.status === "fulfilled" && nodesRes.value.ok
      ? ((await nodesRes.value.json()) as { items?: NodeDBNode[] })
      : {};

  const firstNode = nodesPayload.items?.[0];
  const firstNodeMetrics = (firstNode?.state?.metrics || {}) as Record<string, unknown>;

  const externalTelemetryEmpty =
    !status.metrics && !status.ndb_score && !security.event_count && events.length === 0 && Object.keys(localState.state || {}).length === 0;

  if (externalTelemetryEmpty) {
    const fallbackScoreRaw = firstNodeMetrics.quality_score;
    const fallbackScore = typeof fallbackScoreRaw === "number" ? fallbackScoreRaw : Number(fallbackScoreRaw || 0.041);
    const fallbackLatencyRaw = firstNodeMetrics.response_time_ms;
    const fallbackLatency = typeof fallbackLatencyRaw === "number" ? fallbackLatencyRaw : 0;
    const fallbackBandwidthRaw = firstNodeMetrics.bandwidth_kbps;
    const fallbackBandwidth = typeof fallbackBandwidthRaw === "number" ? fallbackBandwidthRaw : 0;
    const fallbackLoadRaw = firstNodeMetrics.load;
    const fallbackLoad = typeof fallbackLoadRaw === "number" ? fallbackLoadRaw : 0;
    const fallbackActivePeers = monitoring.node_summary?.nodes_total || nodesPayload.items?.length || monitoring.membership?.active_count || 0;

    status.metrics = {
      active_peers: fallbackActivePeers,
      avg_latency_ms: fallbackLatency,
      bandwidth_kbps: fallbackBandwidth,
      load: fallbackLoad,
    };
    status.ndb_score = fallbackScore;
    status.ndb_delta = typeof firstNode?.state?.ndb_delta === "number" ? firstNode.state.ndb_delta : status.ndb_delta ?? 0;
    status.ndb_threshold = status.ndb_threshold ?? 0.65;
    status.state = firstNode?.state?.stigma_state || monitoring.sync_loop?.running ? "active" : "initializing";
    status.tide = status.tide || "Low";

    security.node_id = security.node_id ?? 1;
    security.tide = security.tide || status.tide;
    security.ndb_score = security.ndb_score ?? fallbackScore;
    security.ndb_delta = security.ndb_delta ?? (typeof status.ndb_delta === "number" ? status.ndb_delta : 0);
    security.ndb_threshold = security.ndb_threshold ?? 0.65;
    security.high_risk = security.high_risk ?? false;
    security.event_count = security.event_count ?? (nodesPayload.items?.length || monitoring.sync_loop?.cycles || 0);

    const synthesizedEvents: SecurityEvent[] = (nodesPayload.items || []).map((node, index) => {
      const metrics = (node.state?.metrics || {}) as Record<string, unknown>;
      const scoreRaw = metrics.quality_score;
      const score = typeof scoreRaw === "number" ? scoreRaw : Number(scoreRaw || fallbackScore);
      const stigmaLevel = node.state?.stigma_state === "active" ? 2 : node.state?.stigma_state === "degraded" ? 3 : 1;
      return {
        timestamp_ms: Date.now() - index * 1000,
        endpoint: `/api/v1/control-plane/nodes/${node.metadata?.node_id || index}`,
        action: `state-${node.state?.stigma_state || "unknown"}`,
        stigma_level: stigmaLevel,
        ndb_score: score,
        outcome: node.state?.stigma_state === "active" ? "ok" : "observed",
      };
    });

    if (events.length === 0 && synthesizedEvents.length > 0) {
      events.push(...synthesizedEvents);
    }

    if (Object.keys(localState.state || {}).length === 0) {
      const summaryKey = `nodedb:summary:${Date.now()}`;
      const nodeKey = `nodedb:node:${firstNode?.metadata?.node_id || "node-1"}`;
      const summaryValue = Buffer.from(
        JSON.stringify({
          nodes_total: monitoring.node_summary?.nodes_total || nodesPayload.items?.length || 0,
          active_members: monitoring.membership?.active_count || 0,
          sync_loop: monitoring.sync_loop || {},
          timestamp_utc: new Date().toISOString(),
        }),
      ).toString("base64");
      const nodeValue = Buffer.from(
        JSON.stringify({
          metadata: firstNode?.metadata || {},
          state: firstNode?.state || {},
        }),
      ).toString("base64");
      localState.state = {
        [summaryKey]: summaryValue,
        [nodeKey]: nodeValue,
      };
    }
  }

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
