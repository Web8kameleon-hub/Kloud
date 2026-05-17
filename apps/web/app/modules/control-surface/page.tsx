"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { Activity, ArrowLeft, Database, Download, Globe, LayoutGrid, Server, Shield } from "lucide-react";

type SovereignEvent = {
  timestamp_ms: number;
  endpoint: string;
  action: string;
  stigma_level: number;
  ndb_score: number;
  outcome: string;
};

type SovereignData = {
  status?: {
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
  security?: {
    node_id?: number;
    event_count?: number;
    high_risk?: boolean;
  };
  events?: SovereignEvent[];
  localState?: Array<{ key: string; raw: string; decoded: Record<string, unknown> | null }>;
};

type DeploymentStatus = {
  success?: boolean;
  source?: string;
  count?: number;
  last?: {
    raw: string;
    date?: string;
    time?: string;
    sha?: string;
    services?: string;
    status?: string;
    notes?: string;
  } | null;
  recent?: Array<{
    raw: string;
    date?: string;
    time?: string;
    sha?: string;
    services?: string;
    status?: string;
    notes?: string;
  }>;
  has_log?: boolean;
};

const tabs = ["overview", "audit", "deployment", "services"] as const;

const services = [
  { name: "Kloud Control Surface", href: "/user/dashboard", icon: Activity, desc: "Live NDB/STIGMA telemetry and audit events" },
  { name: "NodeDB Control Surface", href: "/modules/nodedb-control-surface", icon: Database, desc: "Bootstrap, sync loop, and behavioral trace" },
  { name: "DNS & Hosting Control", href: "/modules/dns-hosting-control", icon: Globe, desc: "DNS zones, origins, SSL/TLS, edge policy" },
  { name: "Sovereign Edge Operations", href: "/status", icon: Server, desc: "Multi-PoP routing and failover drills" },
  { name: "Security & Compliance", href: "/security", icon: Shield, desc: "Posture, integrity, and trust-layer operations" },
  { name: "MyMirror Now", href: "/modules/mymirror-now", icon: LayoutGrid, desc: "Real-time admin portal with live sources" },
];

export default function ControlSurfaceHubPage() {
  const [activeTab, setActiveTab] = useState<(typeof tabs)[number]>("overview");
  const [sovereign, setSovereign] = useState<SovereignData | null>(null);
  const [deployment, setDeployment] = useState<DeploymentStatus | null>(null);
  const [loading, setLoading] = useState(true);

  const apiBase = useMemo(
    () => process.env.NEXT_PUBLIC_KLOUD_STATUS_BASE || process.env.KLOUD_PUBLIC_STATUS_BASE || "https://kloud.aiagi.io",
    [],
  );

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      try {
        const [sovereignRes, deploymentRes] = await Promise.all([
          fetch("/api/sovereign/user-dashboard", { cache: "no-store" }),
          fetch("/api/deployment/status", { cache: "no-store" }),
        ]);

        if (sovereignRes.ok) {
          setSovereign(await sovereignRes.json());
        }

        if (deploymentRes.ok) {
          setDeployment(await deploymentRes.json());
        }
      } finally {
        setLoading(false);
      }
    };

    load();
  }, []);

  const exportCsv = async () => {
    const res = await fetch("/api/sovereign/user-dashboard?format=csv", { cache: "no-store" });
    const text = await res.text();
    const blob = new Blob([text], { type: "text/csv;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "kloud-sovereign-events.csv";
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    URL.revokeObjectURL(url);
  };

  const fmt = (value?: number | null) => (typeof value === "number" ? value.toLocaleString() : "0");

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-white">
      <header className="border-b border-slate-800/60 bg-slate-900/60 backdrop-blur sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 py-5">
          <div className="flex items-center gap-4 mb-4">
            <Link href="/modules" className="p-2 rounded-lg hover:bg-slate-800/60 transition-colors">
              <ArrowLeft className="w-5 h-5 text-slate-300" />
            </Link>
            <div>
              <h1 className="text-3xl font-bold">Kloud Control Surface</h1>
              <p className="text-slate-400 text-sm">Unified operations hub for trust, audit, state, and deployment visibility.</p>
              <p className="text-slate-500 text-xs mt-1">Telemetry source: {apiBase}</p>
            </div>
          </div>

          <div className="flex flex-wrap gap-2">
            {tabs.map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  activeTab === tab ? "bg-cyan-600 text-white" : "bg-slate-800/70 text-slate-300 hover:bg-slate-700"
                }`}
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
            <button onClick={exportCsv} className="ml-auto px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-sm font-medium flex items-center gap-2">
              <Download className="w-4 h-4" /> Export CSV
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8 space-y-8">
        {loading ? <div className="text-slate-400">Loading control surface...</div> : null}

        {activeTab === "overview" && (
          <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <MetricCard title="Active Peers" value={fmt(sovereign?.status?.metrics?.active_peers)} subtitle="Live mesh nodes" />
            <MetricCard title="NDB Score" value={(sovereign?.status?.ndb_score ?? 0).toFixed(3)} subtitle={`Delta ${(sovereign?.status?.ndb_delta ?? 0).toFixed(3)}`} />
            <MetricCard title="Latency" value={`${fmt(sovereign?.status?.metrics?.avg_latency_ms)} ms`} subtitle="Current response band" />
            <MetricCard title="Deployment Log" value={String(deployment?.count ?? 0)} subtitle={deployment?.has_log ? "Log available" : "No log found"} />
          </section>
        )}

        {activeTab === "audit" && (
          <section className="grid xl:grid-cols-[1.7fr_1fr] gap-6">
            <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="text-xl font-semibold">Security Events</h2>
                  <p className="text-sm text-slate-400">Pulled from the sovereign audit stream.</p>
                </div>
                <button onClick={exportCsv} className="px-3 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-sm flex items-center gap-2">
                  <Download className="w-4 h-4" /> CSV
                </button>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="text-slate-400">
                    <tr className="border-b border-slate-800">
                      <th className="py-2 text-left">Timestamp</th>
                      <th className="py-2 text-left">Endpoint</th>
                      <th className="py-2 text-left">Action</th>
                      <th className="py-2 text-left">Stigma</th>
                      <th className="py-2 text-left">Score</th>
                      <th className="py-2 text-left">Outcome</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(sovereign?.events || []).slice(0, 8).map((event) => (
                      <tr key={`${event.timestamp_ms}-${event.endpoint}`} className="border-b border-slate-800/60 text-slate-200">
                        <td className="py-2 pr-3">{event.timestamp_ms}</td>
                        <td className="py-2 pr-3">{event.endpoint}</td>
                        <td className="py-2 pr-3">{event.action}</td>
                        <td className="py-2 pr-3">L{event.stigma_level}</td>
                        <td className="py-2 pr-3">{event.ndb_score.toFixed(3)}</td>
                        <td className="py-2 pr-3">{event.outcome}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 space-y-4">
              <h2 className="text-xl font-semibold">Audit Summary</h2>
              <SummaryRow label="Node ID" value={`#${sovereign?.security?.node_id ?? 1}`} />
              <SummaryRow label="Events tracked" value={String(sovereign?.security?.event_count ?? sovereign?.events?.length ?? 0)} />
              <SummaryRow label="Security posture" value={sovereign?.status?.state || "STABLE"} />
              <SummaryRow label="TIDE" value={sovereign?.status?.tide || "Low"} />
              <Link href="/user/dashboard" className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-sm font-medium">
                <Activity className="w-4 h-4" /> Open Live Dashboard
              </Link>
            </div>
          </section>
        )}

        {activeTab === "deployment" && (
          <section className="grid xl:grid-cols-[1fr_1.2fr] gap-6">
            <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 space-y-4">
              <h2 className="text-xl font-semibold">Deployment Status</h2>
              <SummaryRow label="Log source" value={deployment?.source || "missing"} />
              <SummaryRow label="Deploy count" value={String(deployment?.count ?? 0)} />
              <SummaryRow label="Last SHA" value={deployment?.last?.sha || "n/a"} />
              <SummaryRow label="Last services" value={deployment?.last?.services || "n/a"} />
              <SummaryRow label="Last status" value={deployment?.last?.status || "n/a"} />
            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5">
              <h3 className="text-lg font-semibold mb-4">Recent Deployments</h3>
              <div className="space-y-3 max-h-[420px] overflow-auto pr-1">
                {(deployment?.recent || []).map((entry, index) => (
                  <div key={`${entry.raw}-${index}`} className="rounded-xl border border-slate-800 bg-slate-950/50 p-4">
                    <div className="text-sm text-slate-400 mb-1">{entry.date} {entry.time}</div>
                    <div className="font-medium">{entry.sha || "n/a"} · {entry.services || "n/a"}</div>
                    <div className="text-sm text-slate-300 mt-1">{entry.status || "n/a"} {entry.notes ? `· ${entry.notes}` : ""}</div>
                  </div>
                ))}
                {(deployment?.recent || []).length === 0 && <p className="text-slate-400 text-sm">No deployment log found yet.</p>}
              </div>
            </div>
          </section>
        )}

        {activeTab === "services" && (
          <section>
            <h2 className="text-xl font-semibold mb-4">Operational Services</h2>
            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
              {services.map((service) => {
                const Icon = service.icon;
                return (
                  <Link key={service.name} href={service.href} className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 hover:border-cyan-600/60 transition-colors">
                    <div className="flex items-center justify-between mb-4">
                      <div className="w-10 h-10 rounded-xl bg-slate-800 flex items-center justify-center">
                        <Icon className="w-5 h-5 text-cyan-300" />
                      </div>
                      <span className="text-xs uppercase tracking-wider text-slate-500">Service</span>
                    </div>
                    <h3 className="text-lg font-semibold mb-1">{service.name}</h3>
                    <p className="text-sm text-slate-400">{service.desc}</p>
                  </Link>
                );
              })}
            </div>
          </section>
        )}
      </main>
    </div>
  );
}

function MetricCard({ title, value, subtitle }: { title: string; value: string; subtitle: string }) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5">
      <div className="text-xs uppercase tracking-wider text-slate-500 mb-2">{title}</div>
      <div className="text-3xl font-bold mb-1">{value}</div>
      <div className="text-sm text-slate-400">{subtitle}</div>
    </div>
  );
}

function SummaryRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between gap-4 rounded-xl border border-slate-800 bg-slate-950/40 px-4 py-3">
      <span className="text-sm text-slate-400">{label}</span>
      <span className="text-sm font-medium text-white break-all text-right">{value}</span>
    </div>
  );
}