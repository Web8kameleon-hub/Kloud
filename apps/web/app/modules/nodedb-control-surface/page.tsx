'use client';

import { useEffect, useMemo, useState } from 'react';
import Link from 'next/link';

type SyncLoopState = {
  running: boolean;
  interval_seconds: number;
  cycles: number;
  last_run_utc: string | null;
};

type MonitoringSnapshot = {
  status: string;
  timestamp_utc: string;
  node_summary: {
    nodes_total: number;
    state_counts: Record<string, number>;
    quality_counts: Record<string, number>;
  };
  membership: {
    count: number;
    active_count: number;
    items: Array<Record<string, unknown>>;
  };
  recovery: {
    count: number;
    plans: Record<string, unknown>;
  };
  sync_loop: SyncLoopState;
  discovery: {
    available_count: number;
    unavailable_services: string[];
    service_scan: Record<string, unknown>;
  };
};

type NodeEntry = {
  metadata: {
    node_id: string;
    service_name: string;
    service_type: string;
  };
  state: {
    stigma_state: string;
    ndb_quality: string;
    ndb_delta: number;
    metrics: Record<string, unknown>;
  };
};

const CONTROL_PLANE_URL =
  '/api/nodedb-control-plane';

function compactErrorDetail(detail: string): string {
  const trimmed = detail.trim();

  if (trimmed.startsWith('<!DOCTYPE html') || trimmed.startsWith('<html')) {
    return 'Upstream returned HTML error page (likely gateway/proxy issue).';
  }

  try {
    const parsed = JSON.parse(trimmed) as { message?: string; error?: string; status?: number; target?: string };
    if (parsed.message || parsed.error) {
      const suffix = parsed.status ? ` (status ${parsed.status})` : '';
      return `${parsed.message || parsed.error}${suffix}`;
    }
  } catch {
    // Fall back to plain-text trimming when payload is not JSON.
  }

  if (trimmed.length > 240) {
    return `${trimmed.slice(0, 240)}...`;
  }

  return trimmed;
}

export default function NodeDBControlSurfacePage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [nodes, setNodes] = useState<NodeEntry[]>([]);
  const [loop, setLoop] = useState<SyncLoopState>({
    running: false,
    interval_seconds: 5,
    cycles: 0,
    last_run_utc: null,
  });
  const [monitoring, setMonitoring] = useState<MonitoringSnapshot | null>(null);
  const [lastRefresh, setLastRefresh] = useState<string>('');

  const activeNodes = useMemo(
    () => nodes.filter((n) => n.state.stigma_state === 'active').length,
    [nodes]
  );

  const degradedNodes = useMemo(
    () => nodes.filter((n) => n.state.stigma_state !== 'active').length,
    [nodes]
  );

  const refresh = async () => {
    try {
      const [nodesRes, loopRes, monitoringRes] = await Promise.all([
        fetch(`${CONTROL_PLANE_URL}/api/v1/control-plane/nodes`),
        fetch(`${CONTROL_PLANE_URL}/api/v1/control-plane/sync/loop/status`),
        fetch(`${CONTROL_PLANE_URL}/api/v1/control-plane/monitoring`),
      ]);

      if (!nodesRes.ok) {
        const detail = await nodesRes.text();
        throw new Error(`nodes endpoint failed: ${compactErrorDetail(detail)}`);
      }
      if (!loopRes.ok) {
        const detail = await loopRes.text();
        throw new Error(`loop status endpoint failed: ${compactErrorDetail(detail)}`);
      }

      const nodesJson = await nodesRes.json();
      const loopJson = await loopRes.json();
  const monitoringJson = await monitoringRes.json();

      setNodes(Array.isArray(nodesJson.items) ? nodesJson.items : []);
      setLoop(loopJson as SyncLoopState);
      setMonitoring(monitoringJson as MonitoringSnapshot);
      setLastRefresh(new Date().toLocaleTimeString());
      setError(null);
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Unknown error';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const post = async (path: string) => {
    const res = await fetch(`${CONTROL_PLANE_URL}${path}`, { method: 'POST' });
    if (!res.ok) {
      const detail = await res.text();
      throw new Error(detail || `Request failed: ${path}`);
    }
    await refresh();
  };

  useEffect(() => {
    void refresh();
    const timer = setInterval(() => {
      void refresh();
    }, 5000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-cyan-950 to-slate-900 p-6 text-white">
      <div className="mx-auto max-w-7xl">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <Link href="/modules" className="text-cyan-300 hover:text-cyan-200">
              ← Back to Modules
            </Link>
            <h1 className="mt-2 text-4xl font-bold">NodeDB Control Surface</h1>
            <p className="mt-1 text-cyan-100/90">
              Hybrid Kameleon Fabric: wwwmmm · ndb · stigma · tide · nanogrid · cxl · cxl.i
            </p>
          </div>
          <div className="rounded-xl border border-cyan-500/40 bg-cyan-500/10 p-4 text-right">
            <div className="text-sm text-cyan-200">Last Refresh</div>
            <div className="text-lg font-semibold">{lastRefresh || '...'}</div>
          </div>
        </div>

        <div className="mb-6 grid grid-cols-1 gap-4 md:grid-cols-4">
          <MetricCard label="Total Nodes" value={String(nodes.length)} />
          <MetricCard label="Active Nodes" value={String(activeNodes)} />
          <MetricCard label="Degraded/Recovering" value={String(degradedNodes)} />
          <MetricCard
            label="Sync Loop"
            value={loop.running ? `ON (${loop.interval_seconds}s)` : 'OFF'}
          />
        </div>

        {monitoring && (
          <div className="mb-6 grid grid-cols-1 gap-4 md:grid-cols-3">
            <MetricCard label="Registered Members" value={String(monitoring.membership.count)} />
            <MetricCard label="Active Members" value={String(monitoring.membership.active_count)} />
            <MetricCard label="Recovery Plans" value={String(monitoring.recovery.count)} />
          </div>
        )}

        {monitoring && (
          <div className="mb-6 rounded-2xl border border-cyan-500/30 bg-cyan-500/5 p-5">
            <h2 className="mb-3 text-xl font-semibold text-cyan-100">Monitoring Snapshot</h2>
            <div className="grid grid-cols-1 gap-3 text-sm md:grid-cols-2 xl:grid-cols-4">
              <div>
                <div className="text-cyan-200/80">NodeDB Total</div>
                <div className="font-semibold text-white">{monitoring.node_summary.nodes_total}</div>
              </div>
              <div>
                <div className="text-cyan-200/80">Discovery Available</div>
                <div className="font-semibold text-white">{monitoring.discovery.available_count}</div>
              </div>
              <div>
                <div className="text-cyan-200/80">Unavailable Services</div>
                <div className="font-semibold text-white">{monitoring.discovery.unavailable_services.length}</div>
              </div>
              <div>
                <div className="text-cyan-200/80">Snapshot UTC</div>
                <div className="font-mono text-xs text-white/90">{monitoring.timestamp_utc}</div>
              </div>
            </div>
          </div>
        )}

        <div className="mb-6 rounded-2xl border border-slate-700 bg-slate-900/70 p-5">
          <h2 className="mb-4 text-xl font-semibold">Control Actions</h2>
          <div className="flex flex-wrap gap-3">
            <ActionButton label="Bootstrap" onClick={() => post('/api/v1/control-plane/bootstrap')} />
            <ActionButton label="Sync Now" onClick={() => post('/api/v1/control-plane/sync')} />
            <ActionButton label="Start Loop 5s" onClick={() => post('/api/v1/control-plane/sync/loop/start?interval_seconds=5')} />
            <ActionButton label="Stop Loop" onClick={() => post('/api/v1/control-plane/sync/loop/stop')} />
          </div>
          <p className="mt-3 text-sm text-slate-300">
            Loop cycles: {loop.cycles} · Last run UTC: {loop.last_run_utc || 'n/a'}
          </p>
        </div>

        {error && (
          <div className="mb-6 rounded-xl border border-rose-500/50 bg-rose-500/10 p-4 text-rose-200">
            {error}
          </div>
        )}

        <div className="rounded-2xl border border-slate-700 bg-slate-900/70 p-5">
          <h2 className="mb-4 text-xl font-semibold">Node Runtime Table</h2>
          {loading ? (
            <p className="text-slate-300">Loading...</p>
          ) : nodes.length === 0 ? (
            <p className="text-slate-300">No nodes registered yet.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full min-w-[920px] text-sm">
                <thead>
                  <tr className="border-b border-slate-700 text-left text-cyan-200">
                    <th className="px-3 py-2">Node ID</th>
                    <th className="px-3 py-2">Service</th>
                    <th className="px-3 py-2">Type</th>
                    <th className="px-3 py-2">State</th>
                    <th className="px-3 py-2">NDB Quality</th>
                    <th className="px-3 py-2">Delta</th>
                    <th className="px-3 py-2">Quality Score</th>
                  </tr>
                </thead>
                <tbody>
                  {nodes.map((node) => {
                    const qualityScore = node.state.metrics?.quality_score;
                    return (
                      <tr key={node.metadata.node_id} className="border-b border-slate-800/70">
                        <td className="px-3 py-2 font-mono text-xs text-cyan-100">{node.metadata.node_id}</td>
                        <td className="px-3 py-2">{node.metadata.service_name}</td>
                        <td className="px-3 py-2">{node.metadata.service_type}</td>
                        <td className="px-3 py-2">{node.state.stigma_state}</td>
                        <td className="px-3 py-2">{node.state.ndb_quality}</td>
                        <td className="px-3 py-2">{Number(node.state.ndb_delta || 0).toFixed(3)}</td>
                        <td className="px-3 py-2">{typeof qualityScore === 'number' ? qualityScore.toFixed(3) : '-'}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function MetricCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-slate-700 bg-slate-900/70 p-4">
      <div className="text-sm text-slate-300">{label}</div>
      <div className="mt-1 text-2xl font-semibold text-cyan-100">{value}</div>
    </div>
  );
}

function ActionButton({ label, onClick }: { label: string; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className="rounded-lg border border-cyan-400/40 bg-cyan-500/10 px-4 py-2 text-sm font-medium text-cyan-100 hover:bg-cyan-500/20"
    >
      {label}
    </button>
  );
}
