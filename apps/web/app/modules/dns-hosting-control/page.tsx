'use client';

import Link from 'next/link';
import { useCallback, useEffect, useState } from 'react';
import { Activity, ArrowRight, CheckCircle2, Cloud, Database, Globe, Lock, Route, Server, Shield, Sparkles, AlertCircle } from 'lucide-react';

type DNSRecord = {
  id?: string;
  name: string;
  type: string;
  content: string;
  ttl: number;
  proxy_status: 'Proxied' | 'DNS only';
  priority?: number;
};

type DNSZone = {
  id: string;
  domain: string;
  status: string;
  nameserver_1: string;
  nameserver_2: string;
  created_at?: string;
  records?: DNSRecord[];
};

type OriginItem = {
  id: string;
  name: string;
  endpoint: string;
  health_status: 'Healthy' | 'Warning' | 'Disabled';
  region: string;
  role: string;
};

type EdgeService = {
  name: string;
  detail: string;
};

const EDGE_SERVICES: EdgeService[] = [
  { name: 'DNS', detail: 'Zone management, records, routing, and failover policies' },
  { name: 'SSL/TLS', detail: 'Certificate control, encryption mode, and origin trust' },
  { name: 'WAF', detail: 'Protection rules, bot blocking, and request filtering' },
  { name: 'Security', detail: 'Access policies, attack mode, and threat response' },
  { name: 'Speed', detail: 'Caching, compression, and performance tuning' },
  { name: 'Workers Routes', detail: 'Edge logic for custom routing and transforms' },
  { name: 'Load Balancing', detail: 'Active health checks and geo-aware failover' },
  { name: 'Rules', detail: 'Page rules, redirects, and request policies' }
];

export default function DnsHostingControlPage() {
  const [lastSync, setLastSync] = useState('');
  const [zones, setZones] = useState<DNSZone[]>([]);
  const [origins, setOrigins] = useState<OriginItem[]>([]);
  const [syncWarnings, setSyncWarnings] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionFeedback, setActionFeedback] = useState<string | null>(null);
  const [actionBusy, setActionBusy] = useState<string | null>(null);
  const [showAddRecordModal, setShowAddRecordModal] = useState(false);
  const [showAddOriginModal, setShowAddOriginModal] = useState(false);
  const [recordForm, setRecordForm] = useState({
    zone_id: '',
    name: 'www',
    type: 'CNAME',
    content: 'kloud.cloud',
    ttl: 300,
    proxy_status: 'Proxied' as 'Proxied' | 'DNS only',
  });
  const [originForm, setOriginForm] = useState({
    name: 'New Origin',
    endpoint: 'http://origin.kloud.cloud',
    region: 'eu-central',
    role: 'frontend',
    health_status: 'Healthy' as 'Healthy' | 'Warning' | 'Disabled',
  });

  const observedRoutes = zones.reduce((sum, z) => sum + (z.records?.length || 0), 0);
  const healthyOrigins = origins.filter((o) => o.health_status === 'Healthy').length;
  const activeZones = zones.filter((z) => z.status.toLowerCase() === 'active').length;
  const proxiedRecords = zones.reduce(
    (sum, z) => sum + (z.records?.filter((r) => r.proxy_status === 'Proxied').length || 0),
    0,
  );
  const readinessPercent = origins.length
    ? Math.round((healthyOrigins / origins.length) * 100)
    : 0;

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      setSyncWarnings([]);

      const [zonesRes, originsRes] = await Promise.all([
        fetch('/api/dns/zones', { cache: 'no-store' }),
        fetch('/api/dns/origins', { cache: 'no-store' }),
      ]);

      const warnings: string[] = [];

      if (zonesRes.ok) {
        const zonesData = await zonesRes.json();
        setZones(Array.isArray(zonesData) ? zonesData : []);
      } else {
        setZones([]);
        const zonesError = await zonesRes.json().catch(() => null) as { error?: string } | null;
        warnings.push(zonesError?.error || `Zones unavailable (${zonesRes.status})`);
      }

      if (originsRes.ok) {
        const originsData = await originsRes.json();
        setOrigins(Array.isArray(originsData) ? originsData : []);
      } else {
        setOrigins([]);
        const originsError = await originsRes.json().catch(() => null) as { error?: string } | null;
        warnings.push(originsError?.error || `Origins unavailable (${originsRes.status})`);
      }

      if (warnings.length > 0) {
        setSyncWarnings(warnings);
      }

      setLastSync(new Date().toLocaleString());
    } catch (err) {
      setZones([]);
      setOrigins([]);
      setError(err instanceof Error ? err.message : 'Failed to load DNS data');
      console.error('DNS data fetch error:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
    // Refetch every 30 seconds
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, [fetchData]);

  const handleQuickAction = async (action: string) => {
    setActionFeedback(null);

    if (action === 'add-dns') {
      setRecordForm((prev) => ({ ...prev, zone_id: zones[0]?.id || '' }));
      setShowAddRecordModal(true);
      return;
    }

    if (action === 'review-ssl') {
      window.location.href = '/security';
      return;
    }

    if (action === 'deploy-origin') {
      setShowAddOriginModal(true);
      return;
    }

    if (action === 'security-rules') {
      window.location.href = '/security';
      return;
    }

    if (action === 'enable-failover') {
      try {
        setActionBusy('enable-failover');
        const response = await fetch('/api/dns/failover', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ reason: 'quick-action' }),
        });
        if (!response.ok) {
          throw new Error('Failover action failed');
        }
        const result = await response.json();
        setActionFeedback(result.message || 'Failover workflow enabled successfully.');
      } catch (err) {
        setActionFeedback(err instanceof Error ? err.message : 'Failed to enable failover.');
      } finally {
        setActionBusy(null);
      }
    }
  };

  const submitAddRecord = async () => {
    try {
      setActionBusy('submit-record');
      const response = await fetch('/api/dns/records', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(recordForm),
      });
      if (!response.ok) {
        throw new Error('Failed to add DNS record');
      }
      setShowAddRecordModal(false);
      setActionFeedback('DNS record created successfully.');
      await fetchData();
    } catch (err) {
      setActionFeedback(err instanceof Error ? err.message : 'DNS record creation failed.');
    } finally {
      setActionBusy(null);
    }
  };

  const submitAddOrigin = async () => {
    try {
      setActionBusy('submit-origin');
      const response = await fetch('/api/dns/origins', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(originForm),
      });
      if (!response.ok) {
        throw new Error('Failed to deploy hosting origin');
      }
      setShowAddOriginModal(false);
      setActionFeedback('Hosting origin deployed successfully.');
      await fetchData();
    } catch (err) {
      setActionFeedback(err instanceof Error ? err.message : 'Origin deployment failed.');
    } finally {
      setActionBusy(null);
    }
  };

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top_left,_#ecfeff,_#f8fafc_45%,_#f0fdfa)] text-slate-900">
      <nav className="fixed top-0 w-full z-50 bg-white/80 backdrop-blur-xl border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <Link href="/modules" className="flex items-center gap-3 hover:opacity-90 transition-opacity">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-cyan-500 to-emerald-500 flex items-center justify-center">
              <Cloud className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="font-bold text-slate-900">Kloud</div>
              <div className="text-xs text-slate-500 -mt-0.5">DNS & Hosting Control</div>
            </div>
          </Link>
          <div className="flex items-center gap-4">
            <Link href="/status" className="text-slate-500 hover:text-slate-900 transition-colors">Status</Link>
            <Link href="/security" className="text-slate-500 hover:text-slate-900 transition-colors">Security</Link>
            <Link href="/modules" className="px-4 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-medium transition-colors">
              Dashboard
            </Link>
          </div>
        </div>
      </nav>

      <section className="pt-32 pb-10 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-wrap items-center gap-3 mb-5">
            <span className="px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wide bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
              Kloud edge services
            </span>
            <span className="px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wide bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
              One place for DNS, hosting, and edge rules
            </span>
          </div>

          <div className="grid lg:grid-cols-[1.7fr_1fr] gap-6 items-stretch">
            <div className="rounded-3xl border border-cyan-100 bg-white p-8 shadow-xl shadow-cyan-100/70">
              <div className="flex items-center gap-3 mb-6 text-cyan-700">
                <Lock className="w-5 h-5" />
                <span className="text-sm font-medium uppercase tracking-[0.2em]">Kloud DNS / Hosting Operations</span>
              </div>
              <h1 className="text-4xl md:text-5xl font-black leading-tight mb-5">
                Manage domains, origins, security, and routing from one dashboard.
              </h1>
              <p className="text-lg text-slate-600 max-w-3xl leading-relaxed">
                This view brings together DNS records, hosting origins, SSL/TLS, WAF, caching, Workers routes, and load balancing.
                It is designed as the Kloud control surface for teams that want one clear place to run DNS, trust policies, and edge runtime controls.
              </p>

              <div className="mt-8 grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                  <div className="text-3xl font-black text-slate-900">{zones.length}</div>
                  <div className="text-xs uppercase tracking-wide text-slate-500 mt-1">Managed domains</div>
                </div>
                <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                  <div className="text-3xl font-black text-slate-900">{activeZones}</div>
                  <div className="text-xs uppercase tracking-wide text-slate-500 mt-1">Active zones</div>
                </div>
                <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                  <div className="text-3xl font-black text-slate-900">{origins.length}</div>
                  <div className="text-xs uppercase tracking-wide text-slate-500 mt-1">Hosting origins</div>
                </div>
                <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                  <div className="text-3xl font-black text-slate-900">{readinessPercent}%</div>
                  <div className="text-xs uppercase tracking-wide text-slate-500 mt-1">Edge readiness</div>
                </div>
              </div>
            </div>

            <div className="rounded-3xl border border-cyan-100 bg-gradient-to-br from-cyan-50 to-emerald-50 p-8">
              <div className="flex items-center gap-3 mb-5">
                <Sparkles className="w-5 h-5 text-cyan-700" />
                <h2 className="text-xl font-bold">Quick Actions</h2>
              </div>
              <div className="space-y-3">
                {[
                  { id: 'add-dns', label: 'Add DNS record' },
                  { id: 'review-ssl', label: 'Review SSL/TLS' },
                  { id: 'deploy-origin', label: 'Deploy hosting origin' },
                  { id: 'enable-failover', label: 'Enable failover' },
                  { id: 'security-rules', label: 'Open security rules' },
                ].map((action) => (
                  <button
                    key={action.id}
                    type="button"
                    onClick={() => handleQuickAction(action.id)}
                    disabled={actionBusy === action.id}
                    className="w-full flex items-center justify-between rounded-2xl border border-slate-200 bg-white px-4 py-3 hover:border-cyan-300 transition-colors disabled:opacity-70"
                  >
                    <span className="text-slate-700 text-sm font-medium">{action.label}</span>
                    <ArrowRight className="w-4 h-4 text-cyan-700" />
                  </button>
                ))}
              </div>
            <div className="mt-6 rounded-2xl border border-emerald-500/20 bg-emerald-500/10 p-4 text-sm text-emerald-200">
              Last sync: {lastSync || 'Initializing...'}
            </div>
            {actionFeedback && (
              <div className="mt-4 rounded-2xl border border-cyan-500/20 bg-cyan-500/10 p-4 text-sm text-cyan-200">
                {actionFeedback}
              </div>
            )}
            {error && (
              <div className="mt-4 rounded-2xl border border-red-500/20 bg-red-500/10 p-4 text-sm text-red-200 flex gap-2">
                <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
                <span>{error}</span>
              </div>
            )}
            {syncWarnings.length > 0 && (
              <div className="mt-4 rounded-2xl border border-amber-500/20 bg-amber-500/10 p-4 text-sm text-amber-200">
                {syncWarnings.map((warning, idx) => (
                  <div key={`${warning}-${idx}`}>{warning}</div>
                ))}
              </div>
            )}
            </div>
          </div>
        </div>
      </section>

      <section className="px-6 pb-10">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-4 gap-4">
            {[
              { label: 'DNS zones', value: String(zones.length), icon: Globe },
              { label: 'Protected origins', value: String(origins.length), icon: Server },
              { label: 'Proxied records', value: String(proxiedRecords), icon: Shield },
              { label: 'Observed routes', value: String(observedRoutes), icon: Route }
            ].map((item) => {
              const Icon = item.icon;
              return (
                <div key={item.label} className="rounded-2xl border border-slate-200 bg-white p-5">
                  <div className="flex items-center justify-between mb-4">
                    <Icon className="w-5 h-5 text-cyan-700" />
                    <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  </div>
                  <div className="text-3xl font-black text-slate-900">{item.value}</div>
                  <div className="text-sm text-slate-500 mt-1">{item.label}</div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      <section className="px-6 py-10">
        <div className="max-w-7xl mx-auto grid lg:grid-cols-2 gap-6">
          <div className="rounded-3xl border border-slate-200 bg-white p-6">
            <div className="flex items-center gap-3 mb-5">
              <Database className="w-5 h-5 text-cyan-700" />
              <h2 className="text-2xl font-bold">DNS Records</h2>
            </div>
            
            {loading ? (
              <div className="text-center py-8 text-slate-500">Loading DNS zones...</div>
            ) : zones.length === 0 ? (
              <div className="text-center py-8 text-slate-500">No DNS zones configured</div>
            ) : (
              <div className="space-y-6">
                {zones.map((zone) => (
                  <div key={zone.id} className="rounded-2xl border border-slate-200 bg-slate-50 p-5 overflow-hidden">
                    <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-200">
                      <div>
                        <div className="font-bold text-slate-900 text-lg">{zone.domain}</div>
                        <div className="text-xs text-slate-500 mt-1">Zone ID: {zone.id}</div>
                      </div>
                      <div className={`px-3 py-1 rounded-lg text-xs font-semibold ${zone.status === 'active' ? 'bg-emerald-500/15 text-emerald-300' : 'bg-amber-500/15 text-amber-300'}`}>
                        {zone.status}
                      </div>
                    </div>
                    
                    {/* Nameservers */}
                    <div className="mb-4 p-3 bg-white rounded-lg border border-slate-200">
                      <div className="text-xs font-semibold text-cyan-700 uppercase tracking-wide mb-2">Nameservers</div>
                      <div className="space-y-1">
                        <div className="text-sm text-slate-700"><span className="text-slate-500">NS</span> {zone.nameserver_1}</div>
                        <div className="text-sm text-slate-700"><span className="text-slate-500">NS</span> {zone.nameserver_2}</div>
                      </div>
                    </div>
                    
                    {/* DNS Records for this zone */}
                    {zone.records && zone.records.length > 0 ? (
                      <div className="space-y-2">
                        <div className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">Records ({zone.records.length})</div>
                        {zone.records.map((record, idx) => (
                          <div key={idx} className="flex items-center justify-between rounded-lg bg-white p-3 text-sm border border-slate-200">
                            <div className="flex items-center gap-3 flex-1">
                              <span className="px-2 py-0.5 rounded bg-cyan-100 text-cyan-700 text-xs font-semibold min-w-max">{record.type}</span>
                              <span className="text-slate-700 min-w-max">{record.name}</span>
                              <span className="text-slate-500 truncate">{record.content}</span>
                            </div>
                            <div className="flex items-center gap-2">
                              <span className={`px-2 py-0.5 rounded text-xs font-semibold whitespace-nowrap ${record.proxy_status === 'Proxied' ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-600'}`}>
                                {record.proxy_status}
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-sm text-slate-500 italic">No records configured</div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="rounded-3xl border border-slate-200 bg-white p-6">
            <div className="flex items-center gap-3 mb-5">
              <Server className="w-5 h-5 text-cyan-700" />
              <h2 className="text-2xl font-bold">Hosting Origins</h2>
            </div>
            
            {loading ? (
              <div className="text-center py-8 text-slate-500">Loading origins...</div>
            ) : origins.length === 0 ? (
              <div className="text-center py-8 text-slate-500">No hosting origins configured</div>
            ) : (
              <div className="space-y-3">
                {origins.map((origin) => (
                  <div key={origin.id} className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                    <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                      <div>
                        <div className="font-semibold text-slate-900">{origin.name}</div>
                        <div className="text-sm text-slate-600">{origin.endpoint}</div>
                        <div className="text-xs text-slate-500 mt-1">{origin.role}</div>
                      </div>
                      <div className="flex flex-wrap gap-2 text-xs">
                        <span className={`px-2.5 py-1 rounded-full border ${origin.health_status === 'Healthy' ? 'bg-emerald-100 text-emerald-700 border-emerald-200' : origin.health_status === 'Warning' ? 'bg-amber-100 text-amber-700 border-amber-200' : 'bg-slate-100 text-slate-600 border-slate-200'}`}>
                          {origin.health_status}
                        </span>
                        <span className="px-2.5 py-1 rounded-full bg-white text-slate-700 border border-slate-200">{origin.region}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </section>

      <section className="px-6 py-10 bg-white/70 border-y border-slate-200">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center gap-3 mb-6">
            <Activity className="w-5 h-5 text-cyan-700" />
            <h2 className="text-2xl font-bold">Edge Services</h2>
          </div>
          <div className="grid md:grid-cols-2 xl:grid-cols-4 gap-4">
            {EDGE_SERVICES.map((service) => (
              <div key={service.name} className="rounded-2xl border border-slate-200 bg-white p-5 hover:border-cyan-300 transition-colors">
                <div className="font-semibold text-slate-900 mb-2">{service.name}</div>
                <div className="text-sm text-slate-600 leading-relaxed">{service.detail}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="px-6 py-12">
        <div className="max-w-7xl mx-auto rounded-3xl border border-cyan-200 bg-gradient-to-br from-cyan-50 to-emerald-50 p-8 flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
          <div>
            <h2 className="text-3xl font-bold mb-3">A single control surface for DNS and hosting.</h2>
            <p className="text-slate-600 max-w-2xl">
              Use this dashboard to keep domains, routing, edge security, and origins in one place while your team
              keeps shipping.
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <Link href="/security" className="px-5 py-3 rounded-xl bg-white text-slate-950 font-semibold hover:bg-gray-100 transition-colors">
              Review Security
            </Link>
            <Link href="/status" className="px-5 py-3 rounded-xl border border-slate-300 bg-white text-slate-900 font-semibold hover:border-cyan-500 transition-colors">
              Check Status
            </Link>
          </div>
        </div>
      </section>

      <footer className="px-6 pb-10 text-center text-slate-500 text-sm">
        <Link href="/modules" className="text-cyan-700 hover:text-cyan-600 transition-colors">Back to modules</Link>
      </footer>

      {showAddRecordModal && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="w-full max-w-xl rounded-2xl bg-white border border-slate-200 p-6">
            <h3 className="text-xl font-bold text-slate-900 mb-4">Add DNS Record</h3>
            <div className="grid gap-3">
              <select
                value={recordForm.zone_id}
                onChange={(e) => setRecordForm((p) => ({ ...p, zone_id: e.target.value }))}
                className="rounded-lg border border-slate-300 px-3 py-2"
              >
                <option value="">Select zone</option>
                {zones.map((z) => (
                  <option key={z.id} value={z.id}>{z.domain}</option>
                ))}
              </select>
              <input value={recordForm.name} onChange={(e) => setRecordForm((p) => ({ ...p, name: e.target.value }))} className="rounded-lg border border-slate-300 px-3 py-2" placeholder="Record name (e.g. www)" />
              <select value={recordForm.type} onChange={(e) => setRecordForm((p) => ({ ...p, type: e.target.value }))} className="rounded-lg border border-slate-300 px-3 py-2">
                {['A', 'AAAA', 'CNAME', 'MX', 'TXT', 'NS', 'SOA', 'SRV'].map((t) => <option key={t} value={t}>{t}</option>)}
              </select>
              <input value={recordForm.content} onChange={(e) => setRecordForm((p) => ({ ...p, content: e.target.value }))} className="rounded-lg border border-slate-300 px-3 py-2" placeholder="Target content" />
              <input type="number" value={recordForm.ttl} onChange={(e) => setRecordForm((p) => ({ ...p, ttl: Number(e.target.value) || 300 }))} className="rounded-lg border border-slate-300 px-3 py-2" placeholder="TTL" />
              <select value={recordForm.proxy_status} onChange={(e) => setRecordForm((p) => ({ ...p, proxy_status: e.target.value as 'Proxied' | 'DNS only' }))} className="rounded-lg border border-slate-300 px-3 py-2">
                <option value="Proxied">Proxied</option>
                <option value="DNS only">DNS only</option>
              </select>
            </div>
            <div className="mt-5 flex gap-3 justify-end">
              <button type="button" onClick={() => setShowAddRecordModal(false)} className="px-4 py-2 rounded-lg border border-slate-300 text-slate-700">Cancel</button>
              <button type="button" onClick={submitAddRecord} disabled={actionBusy === 'submit-record' || !recordForm.zone_id} className="px-4 py-2 rounded-lg bg-cyan-600 text-white disabled:opacity-60">Save Record</button>
            </div>
          </div>
        </div>
      )}

      {showAddOriginModal && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="w-full max-w-xl rounded-2xl bg-white border border-slate-200 p-6">
            <h3 className="text-xl font-bold text-slate-900 mb-4">Deploy Hosting Origin</h3>
            <div className="grid gap-3">
              <input value={originForm.name} onChange={(e) => setOriginForm((p) => ({ ...p, name: e.target.value }))} className="rounded-lg border border-slate-300 px-3 py-2" placeholder="Origin name" />
              <input value={originForm.endpoint} onChange={(e) => setOriginForm((p) => ({ ...p, endpoint: e.target.value }))} className="rounded-lg border border-slate-300 px-3 py-2" placeholder="Endpoint URL" />
              <input value={originForm.region} onChange={(e) => setOriginForm((p) => ({ ...p, region: e.target.value }))} className="rounded-lg border border-slate-300 px-3 py-2" placeholder="Region" />
              <input value={originForm.role} onChange={(e) => setOriginForm((p) => ({ ...p, role: e.target.value }))} className="rounded-lg border border-slate-300 px-3 py-2" placeholder="Role" />
              <select value={originForm.health_status} onChange={(e) => setOriginForm((p) => ({ ...p, health_status: e.target.value as 'Healthy' | 'Warning' | 'Disabled' }))} className="rounded-lg border border-slate-300 px-3 py-2">
                <option value="Healthy">Healthy</option>
                <option value="Warning">Warning</option>
                <option value="Disabled">Disabled</option>
              </select>
            </div>
            <div className="mt-5 flex gap-3 justify-end">
              <button type="button" onClick={() => setShowAddOriginModal(false)} className="px-4 py-2 rounded-lg border border-slate-300 text-slate-700">Cancel</button>
              <button type="button" onClick={submitAddOrigin} disabled={actionBusy === 'submit-origin'} className="px-4 py-2 rounded-lg bg-cyan-600 text-white disabled:opacity-60">Deploy Origin</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
