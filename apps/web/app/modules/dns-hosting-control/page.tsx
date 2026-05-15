'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
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
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Fetch DNS zones
        const zonesRes = await fetch('/api/dns/zones', { cache: 'no-store' });
        if (zonesRes.ok) {
          const zonesData = await zonesRes.json();
          setZones(zonesData);
        } else {
          throw new Error(`Failed to fetch zones: ${zonesRes.statusText}`);
        }
        
        // Fetch hosting origins
        const originsRes = await fetch('/api/dns/origins', { cache: 'no-store' });
        if (originsRes.ok) {
          const originsData = await originsRes.json();
          setOrigins(originsData);
        } else {
          throw new Error(`Failed to fetch origins: ${originsRes.statusText}`);
        }
        
        setLastSync(new Date().toLocaleString());
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load DNS data');
        console.error('DNS data fetch error:', err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
    // Refetch every 30 seconds
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 text-white">
      <nav className="fixed top-0 w-full z-50 bg-slate-950/80 backdrop-blur-xl border-b border-slate-800">
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <Link href="/modules" className="flex items-center gap-3 hover:opacity-90 transition-opacity">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-cyan-500 to-emerald-500 flex items-center justify-center">
              <Cloud className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="font-bold text-white">Kloud</div>
              <div className="text-xs text-gray-400 -mt-0.5">DNS & Hosting Control</div>
            </div>
          </Link>
          <div className="flex items-center gap-4">
            <Link href="/status" className="text-gray-400 hover:text-white transition-colors">Status</Link>
            <Link href="/security" className="text-gray-400 hover:text-white transition-colors">Security</Link>
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
            <div className="rounded-3xl border border-slate-800 bg-white/5 p-8 shadow-2xl shadow-cyan-500/5">
              <div className="flex items-center gap-3 mb-6 text-cyan-300">
                <Lock className="w-5 h-5" />
                <span className="text-sm font-medium uppercase tracking-[0.2em]">Kloud DNS / Hosting Operations</span>
              </div>
              <h1 className="text-4xl md:text-5xl font-black leading-tight mb-5">
                Manage domains, origins, security, and routing from one dashboard.
              </h1>
              <p className="text-lg text-gray-300 max-w-3xl leading-relaxed">
                This view brings together DNS records, hosting origins, SSL/TLS, WAF, caching, Workers routes, and load balancing.
                It is designed as the Kloud control surface for teams that want one clear place to run DNS, trust policies, and edge runtime controls.
              </p>

              <div className="mt-8 grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-4">
                  <div className="text-3xl font-black text-white">{zones.length}</div>
                  <div className="text-xs uppercase tracking-wide text-gray-400 mt-1">Managed domains</div>
                </div>
                <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-4">
                  <div className="text-3xl font-black text-white">8</div>
                  <div className="text-xs uppercase tracking-wide text-gray-400 mt-1">Kloud services</div>
                </div>
                <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-4">
                  <div className="text-3xl font-black text-white">{origins.length}</div>
                  <div className="text-xs uppercase tracking-wide text-gray-400 mt-1">Hosting origins</div>
                </div>
                <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-4">
                  <div className="text-3xl font-black text-white">24/7</div>
                  <div className="text-xs uppercase tracking-wide text-gray-400 mt-1">Edge readiness</div>
                </div>
              </div>
            </div>

            <div className="rounded-3xl border border-slate-800 bg-gradient-to-br from-cyan-500/10 to-emerald-500/10 p-8">
              <div className="flex items-center gap-3 mb-5">
                <Sparkles className="w-5 h-5 text-cyan-300" />
                <h2 className="text-xl font-bold">Quick Actions</h2>
              </div>
              <div className="space-y-3">
                {[
                  'Add DNS record',
                  'Review SSL/TLS',
                  'Deploy hosting origin',
                  'Enable failover',
                  'Open security rules'
                ].map((action) => (
                  <div key={action} className="flex items-center justify-between rounded-2xl border border-slate-800 bg-slate-950/60 px-4 py-3">
                    <span className="text-gray-200 text-sm font-medium">{action}</span>
                    <ArrowRight className="w-4 h-4 text-cyan-300" />
                  </div>
                ))}
              </div>
            <div className="mt-6 rounded-2xl border border-emerald-500/20 bg-emerald-500/10 p-4 text-sm text-emerald-200">
              Last sync: {lastSync || 'Initializing...'}
            </div>
            {error && (
              <div className="mt-4 rounded-2xl border border-red-500/20 bg-red-500/10 p-4 text-sm text-red-200 flex gap-2">
                <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
                <span>{error}</span>
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
              { label: 'Security policies', value: '8', icon: Shield },
              { label: 'Observed routes', value: String(zones.reduce((sum, z) => sum + (z.records?.length || 0), 0)), icon: Route }
            ].map((item) => {
              const Icon = item.icon;
              return (
                <div key={item.label} className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5">
                  <div className="flex items-center justify-between mb-4">
                    <Icon className="w-5 h-5 text-cyan-300" />
                    <CheckCircle2 className="w-4 h-4 text-emerald-300" />
                  </div>
                  <div className="text-3xl font-black text-white">{item.value}</div>
                  <div className="text-sm text-gray-400 mt-1">{item.label}</div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      <section className="px-6 py-10">
        <div className="max-w-7xl mx-auto grid lg:grid-cols-2 gap-6">
          <div className="rounded-3xl border border-slate-800 bg-slate-900/60 p-6">
            <div className="flex items-center gap-3 mb-5">
              <Database className="w-5 h-5 text-cyan-300" />
              <h2 className="text-2xl font-bold">DNS Records</h2>
            </div>
            
            {loading ? (
              <div className="text-center py-8 text-gray-400">Loading DNS zones...</div>
            ) : zones.length === 0 ? (
              <div className="text-center py-8 text-gray-400">No DNS zones configured</div>
            ) : (
              <div className="space-y-6">
                {zones.map((zone) => (
                  <div key={zone.id} className="rounded-2xl border border-slate-700 bg-slate-950/80 p-5 overflow-hidden">
                    <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-800">
                      <div>
                        <div className="font-bold text-white text-lg">{zone.domain}</div>
                        <div className="text-xs text-gray-500 mt-1">Zone ID: {zone.id}</div>
                      </div>
                      <div className={`px-3 py-1 rounded-lg text-xs font-semibold ${zone.status === 'active' ? 'bg-emerald-500/15 text-emerald-300' : 'bg-amber-500/15 text-amber-300'}`}>
                        {zone.status}
                      </div>
                    </div>
                    
                    {/* Nameservers */}
                    <div className="mb-4 p-3 bg-slate-900/60 rounded-lg border border-slate-800">
                      <div className="text-xs font-semibold text-cyan-300 uppercase tracking-wide mb-2">Nameservers</div>
                      <div className="space-y-1">
                        <div className="text-sm text-gray-300"><span className="text-gray-500">NS</span> {zone.nameserver_1}</div>
                        <div className="text-sm text-gray-300"><span className="text-gray-500">NS</span> {zone.nameserver_2}</div>
                      </div>
                    </div>
                    
                    {/* DNS Records for this zone */}
                    {zone.records && zone.records.length > 0 ? (
                      <div className="space-y-2">
                        <div className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">Records ({zone.records.length})</div>
                        {zone.records.map((record, idx) => (
                          <div key={idx} className="flex items-center justify-between rounded-lg bg-slate-900/40 p-3 text-sm">
                            <div className="flex items-center gap-3 flex-1">
                              <span className="px-2 py-0.5 rounded bg-cyan-500/15 text-cyan-300 text-xs font-semibold min-w-max">{record.type}</span>
                              <span className="text-gray-300 min-w-max">{record.name}</span>
                              <span className="text-gray-500 truncate">{record.content}</span>
                            </div>
                            <div className="flex items-center gap-2">
                              <span className={`px-2 py-0.5 rounded text-xs font-semibold whitespace-nowrap ${record.proxy_status === 'Proxied' ? 'bg-emerald-500/15 text-emerald-300' : 'bg-slate-800 text-gray-300'}`}>
                                {record.proxy_status}
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-sm text-gray-500 italic">No records configured</div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="rounded-3xl border border-slate-800 bg-slate-900/60 p-6">
            <div className="flex items-center gap-3 mb-5">
              <Server className="w-5 h-5 text-cyan-300" />
              <h2 className="text-2xl font-bold">Hosting Origins</h2>
            </div>
            
            {loading ? (
              <div className="text-center py-8 text-gray-400">Loading origins...</div>
            ) : origins.length === 0 ? (
              <div className="text-center py-8 text-gray-400">No hosting origins configured</div>
            ) : (
              <div className="space-y-3">
                {origins.map((origin) => (
                  <div key={origin.id} className="rounded-2xl border border-slate-800 bg-slate-950/60 p-4">
                    <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                      <div>
                        <div className="font-semibold text-white">{origin.name}</div>
                        <div className="text-sm text-gray-400">{origin.endpoint}</div>
                        <div className="text-xs text-gray-500 mt-1">{origin.role}</div>
                      </div>
                      <div className="flex flex-wrap gap-2 text-xs">
                        <span className={`px-2.5 py-1 rounded-full border ${origin.health_status === 'Healthy' ? 'bg-emerald-500/15 text-emerald-300 border-emerald-500/20' : origin.health_status === 'Warning' ? 'bg-amber-500/15 text-amber-300 border-amber-500/20' : 'bg-slate-800 text-gray-300 border-slate-700'}`}>
                          {origin.health_status}
                        </span>
                        <span className="px-2.5 py-1 rounded-full bg-slate-800 text-gray-300 border border-slate-700">{origin.region}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </section>

      <section className="px-6 py-10 bg-slate-900/30 border-y border-slate-800">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center gap-3 mb-6">
            <Activity className="w-5 h-5 text-cyan-300" />
            <h2 className="text-2xl font-bold">Edge Services</h2>
          </div>
          <div className="grid md:grid-cols-2 xl:grid-cols-4 gap-4">
            {EDGE_SERVICES.map((service) => (
              <div key={service.name} className="rounded-2xl border border-slate-800 bg-slate-950/60 p-5 hover:border-cyan-500/30 transition-colors">
                <div className="font-semibold text-white mb-2">{service.name}</div>
                <div className="text-sm text-gray-400 leading-relaxed">{service.detail}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="px-6 py-12">
        <div className="max-w-7xl mx-auto rounded-3xl border border-cyan-500/20 bg-gradient-to-br from-cyan-500/10 to-emerald-500/10 p-8 flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
          <div>
            <h2 className="text-3xl font-bold mb-3">A single control surface for DNS and hosting.</h2>
            <p className="text-gray-300 max-w-2xl">
              Use this dashboard to keep domains, routing, edge security, and origins in one place while your team
              keeps shipping.
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <Link href="/security" className="px-5 py-3 rounded-xl bg-white text-slate-950 font-semibold hover:bg-gray-100 transition-colors">
              Review Security
            </Link>
            <Link href="/status" className="px-5 py-3 rounded-xl border border-slate-700 bg-slate-950/60 text-white font-semibold hover:border-cyan-500 transition-colors">
              Check Status
            </Link>
          </div>
        </div>
      </section>

      <footer className="px-6 pb-10 text-center text-gray-500 text-sm">
        <Link href="/modules" className="text-cyan-300 hover:text-cyan-200 transition-colors">Back to modules</Link>
      </footer>
    </div>
  );
}
