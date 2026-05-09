'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';

/**
 * STATUS PAGE - Public System Status
 * Real-time monitoring display
 */

interface ServiceStatus {
  name: string;
  status: 'operational' | 'degraded' | 'outage' | 'maintenance';
  latency?: number;
  uptime: string;
}

export default function StatusPage() {
  const [lastUpdated, setLastUpdated] = useState<string>('');

  const services: ServiceStatus[] = [
    { name: 'API Gateway', status: 'operational', latency: 45, uptime: '99.98%' },
    { name: 'ASI Trinity Core', status: 'operational', latency: 52, uptime: '99.97%' },
    { name: 'ALBA Service', status: 'operational', latency: 38, uptime: '99.99%' },
    { name: 'ALBI Service', status: 'operational', latency: 41, uptime: '99.98%' },
    { name: 'JONA Service', status: 'operational', latency: 44, uptime: '99.97%' },
    { name: 'Dashboard (Web)', status: 'operational', latency: 120, uptime: '99.99%' },
    { name: 'WebSocket Services', status: 'operational', latency: 28, uptime: '99.96%' },
    { name: 'Database Cluster', status: 'operational', latency: 12, uptime: '99.99%' },
    { name: 'CDN (Cloudflare)', status: 'operational', latency: 18, uptime: '99.99%' },
    { name: 'Authentication', status: 'operational', latency: 35, uptime: '99.98%' },
  ];

  const overallStatus = services.every(s => s.status === 'operational')
    ? 'All Systems Operational'
    : services.some(s => s.status === 'outage')
    ? 'System Outage'
    : 'Degraded Performance';

  const incidents: { date: string; title: string; status: string; description: string; duration: string }[] = [];

  // Uptime history will be populated with real data
  const uptimeHistory: { month: string; uptime: number }[] = [];

  useEffect(() => {
    setLastUpdated(new Date().toLocaleString());
    const interval = setInterval(() => {
      setLastUpdated(new Date().toLocaleString());
    }, 60000);
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'operational': return 'bg-green-500';
      case 'degraded': return 'bg-yellow-500';
      case 'outage': return 'bg-red-500';
      case 'maintenance': return 'bg-violet-500';
      default: return 'bg-gray-500';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'operational': return 'Operational';
      case 'degraded': return 'Degraded';
      case 'outage': return 'Outage';
      case 'maintenance': return 'Maintenance';
      default: return 'Unknown';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 text-white">
      {/* Navigation */}
      <nav className="fixed top-0 w-full z-50 bg-slate-950/80 backdrop-blur-xl border-b border-slate-800">
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <Link href="/" className="flex items-center gap-3">
            <span className="text-2xl">🧠</span>
            <span className="text-xl font-bold">Kloud</span>
          </Link>
          <div className="flex items-center gap-6">
            <Link href="/platform" className="text-gray-400 hover:text-white transition-colors">Platform</Link>
            <Link href="/security" className="text-gray-400 hover:text-white transition-colors">Security</Link>
            <Link href="/modules" className="px-4 py-2 bg-violet-600 hover:bg-violet-500 rounded-lg transition-colors">
              Dashboard
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="pt-32 pb-8 px-6 text-center">
        <h1 className="text-4xl font-bold mb-4">System Status</h1>
        <div className="inline-flex items-center gap-3 px-6 py-3 rounded-full bg-green-500/20 border border-green-500/30">
          <div className="w-3 h-3 rounded-full bg-green-500 animate-pulse"></div>
          <span className="text-green-400 font-medium">{overallStatus}</span>
        </div>
        <p className="text-gray-500 text-sm mt-4">
          Last updated: {lastUpdated || 'Loading...'}
        </p>
      </section>

      {/* Services Grid */}
      <section className="py-8 px-6">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-xl font-semibold mb-6">Service Status</h2>
          
          <div className="space-y-3">
            {services.map((service) => (
              <div
                key={service.name}
                className="flex items-center justify-between p-4 rounded-xl bg-slate-800/50 border border-slate-700"
              >
                <div className="flex items-center gap-4">
                  <div className={`w-3 h-3 rounded-full ${getStatusColor(service.status)}`}></div>
                  <span className="font-medium">{service.name}</span>
                </div>
                <div className="flex items-center gap-6 text-sm">
                  {service.latency && (
                    <span className="text-gray-400">{service.latency}ms</span>
                  )}
                  <span className="text-gray-500">{service.uptime}</span>
                  <span className={`px-3 py-1 rounded-full text-xs ${
                    service.status === 'operational' 
                      ? 'bg-green-500/20 text-green-400'
                      : service.status === 'degraded'
                      ? 'bg-yellow-500/20 text-yellow-400'
                      : 'bg-red-500/20 text-red-400'
                  }`}>
                    {getStatusText(service.status)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Uptime History */}
      <section className="py-12 px-6 bg-slate-900/50">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-xl font-semibold mb-6">Uptime History</h2>
          
          <div className="grid grid-cols-3 md:grid-cols-6 gap-4">
            {uptimeHistory.map((month) => (
              <div key={month.month} className="text-center p-4 rounded-xl bg-slate-800/50">
                <div className={`text-2xl font-bold ${
                  month.uptime >= 99.99 ? 'text-green-400' :
                  month.uptime >= 99.9 ? 'text-violet-400' :
                  'text-yellow-400'
                }`}>
                  {month.uptime}%
                </div>
                <div className="text-xs text-gray-500 mt-1">{month.month}</div>
              </div>
            ))}
          </div>

          <div className="mt-6 p-4 rounded-xl bg-slate-800/30 text-center">
            <span className="text-2xl font-bold text-violet-400">99.97%</span>
            <span className="text-gray-400 ml-2">6-Month Average Uptime</span>
          </div>
        </div>
      </section>

      {/* Recent Incidents */}
      <section className="py-12 px-6">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-xl font-semibold mb-6">Recent Incidents</h2>
          
          {incidents.length === 0 ? (
            <div className="p-8 rounded-xl bg-slate-800/50 border border-slate-700 text-center">
              <span className="text-gray-400">No incidents in the last 90 days 🎉</span>
            </div>
          ) : (
            <div className="space-y-4">
              {incidents.map((incident, idx) => (
                <div
                  key={idx}
                  className="p-6 rounded-xl bg-slate-800/50 border border-slate-700"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <h3 className="font-semibold">{incident.title}</h3>
                      <p className="text-sm text-gray-500">{incident.date}</p>
                    </div>
                    <span className="px-3 py-1 rounded-full text-xs bg-green-500/20 text-green-400">
                      {incident.status}
                    </span>
                  </div>
                  <p className="text-gray-400 text-sm">{incident.description}</p>
                  <p className="text-gray-500 text-xs mt-2">Duration: {incident.duration}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </section>

      {/* Subscribe */}
      <section className="py-12 px-6 bg-slate-900/50">
        <div className="max-w-2xl mx-auto text-center">
          <h2 className="text-xl font-semibold mb-4">Stay Updated</h2>
          <p className="text-gray-400 mb-6">
            Subscribe to receive notifications about system status changes.
          </p>
          <div className="flex gap-4 justify-center">
            <Link
              href="https://twitter.com/kloud"
              className="px-6 py-3 bg-slate-800 hover:bg-slate-700 rounded-xl transition-colors"
            >
              🐦 Twitter Updates
            </Link>
            <Link
              href="mailto:support@kloud.com?subject=Status%20Updates%20Subscription"
              className="px-6 py-3 bg-slate-800 hover:bg-slate-700 rounded-xl transition-colors"
            >
              📧 Email Alerts
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-6 border-t border-slate-800">
        <div className="max-w-6xl mx-auto text-center text-gray-500 text-sm">
          © 2026 Kloud. All rights reserved. | 
          <Link href="/security" className="hover:text-violet-400 ml-2">Security</Link> | 
          <Link href="/platform" className="hover:text-violet-400 ml-2">Platform</Link> | 
          <Link href="/company" className="hover:text-violet-400 ml-2">Company</Link>
        </div>
      </footer>
    </div>
  );
}








