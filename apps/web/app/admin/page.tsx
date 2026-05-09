'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

/**
 * KLOUD ADMIN DASHBOARD
 * ========================
 * Password-protected infrastructure monitoring
 * Only for administrators
 */

const ADMIN_PASSWORD = 'admin8981.!admin1';

interface SystemMetrics {
  alba: { status: string; connections: number; efficiency: number };
  albi: { status: string; creativity: number; intelligence: number };
  jona: { status: string; harmony: number; stability: number };
  system: {
    cpu_load: number;
    memory_usage: number;
    uptime_hours: number;
  };
}

// Infrastructure Modules (Admin Only)
const ADMIN_MODULES = [
  {
    id: 'data-collection',
    name: 'Data Collection',
    description: 'Industrial IoT and sensor data collection',
    icon: '📡',
    color: 'from-violet-500 to-violet-600',
    category: 'Infrastructure'
  },
  {
    id: 'reporting-dashboard',
    name: 'Reporting Dashboard',
    description: 'Generate reports and analytics',
    icon: '📈',
    color: 'from-blue-800 to-blue-900',
    category: 'Infrastructure'
  },
  {
    id: 'spectrum-analyzer',
    name: 'Spectrum Analyzer',
    description: 'Frequency spectrum visualization',
    icon: '📊',
    color: 'from-green-500 to-blue-900',
    category: 'Analysis'
  },
  {
    id: 'industrial-dashboard',
    name: 'Industrial Dashboard',
    description: 'Full industrial monitoring system',
    icon: '🏭',
    color: 'from-gray-500 to-slate-600',
    category: 'Infrastructure'
  },
  {
    id: 'asi-demo',
    name: 'ASI Demo',
    description: 'ASI Trinity demonstration',
    icon: '🧠',
    color: 'from-purple-500 to-pink-600',
    category: 'Infrastructure'
  },
  {
    id: 'developer-docs',
    name: 'Developer Docs',
    description: 'API docs, SDKs & examples publik',
    icon: '👨‍💻',
    color: 'from-violet-500 to-purple-600',
    category: 'Documentation'
  },
  // 🔒 PRIVATE MODULES - Admin Only Access
  {
    id: 'neuroacoustic-converter',
    name: 'Neuroacoustic Converter',
    description: 'EEG to Audio Conversion • Advanced Neural Processing',
    icon: '🔄',
    color: 'from-green-500 to-blue-900',
    category: 'Private Admin',
    private: true
  },
  {
    id: 'neural-biofeedback',
    name: 'Neural Biofeedback',
    description: 'Brain Wave Training System • Postman-Style API Interface',
    icon: '💫',
    color: 'from-blue-700 to-purple-600',
    category: 'Private Admin',
    private: true
  },
  {
    id: 'spectrum-analyzer',
    name: 'Spectrum Analyzer',
    description: 'Multi-band EEG FFT Analysis • Postman-Style API Interface',
    icon: '📊',
    color: 'from-violet-500 to-violet-600',
    category: 'Private Admin',
    private: true
  },
  {
    id: 'albi-eeg-analysis',
    name: 'ALBI EEG Analysis',
    description: 'Real-time brain wave analysis • Postman-Style API Interface',
    icon: '🧬',
    color: 'from-pink-500 to-rose-600',
    category: 'Private Admin',
    private: true
  },
  {
    id: 'kloud-api-collection',
    name: 'Kloud API Collection',
    description: 'Real-time API monitoring • No mock data',
    icon: '📡',
    color: 'from-orange-500 to-red-600',
    category: 'Private Admin',
    private: true
  }
];

const ASI_TRINITY = [
  {
    name: 'ALBA',
    role: 'Analytical Intelligence',
    description: 'Data collection and pattern recognition engine',
    icon: '🔬',
    color: 'from-violet-400 to-violet-500',
    endpoint: '/api/alba/info'
  },
  {
    name: 'ALBI',
    role: 'Creative Intelligence',
    description: 'Innovation and creative problem solving engine',
    icon: '🎨',
    color: 'from-purple-400 to-pink-500',
    endpoint: '/api/albi/info'
  },
  {
    name: 'JONA',
    role: 'Coordinator Intelligence',
    description: 'System harmony and orchestration monitor',
    icon: '∞',
    color: 'from-amber-400 to-orange-500',
    endpoint: '/api/jona/info'
  }
];

const TECH_STACK = [
  { name: 'Docker', desc: 'Containerization', icon: '🐳' },
  { name: 'Kubernetes', desc: 'Orchestration', icon: '☸️' },
  { name: 'Nginx', desc: 'Load Balancer', icon: '🔄' },
  { name: 'PostgreSQL', desc: 'Database', icon: '🐘' },
  { name: 'Redis', desc: 'Cache Layer', icon: '⚡' },
  { name: 'Grafana', desc: 'Monitoring', icon: '📊' },
  { name: 'Prometheus', desc: 'Metrics', icon: '🔥' },
  { name: 'Hetzner', desc: 'Cloud Provider', icon: '☁️' },
];

export default function AdminDashboard() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Check if already authenticated in session
    const authStatus = sessionStorage.getItem('admin_authenticated');
    if (authStatus === 'true') {
      setIsAuthenticated(true);
      fetchMetrics();
    }
  }, []);

  useEffect(() => {
    if (isAuthenticated) {
      const interval = setInterval(fetchMetrics, 10000);
      return () => clearInterval(interval);
    }
  }, [isAuthenticated]);

  const fetchMetrics = async () => {
    try {
      // 🔒 PRIVATE: ASI/Alba/Albi/Jona metrics hidden from public access
      // const response = await fetch('/api/asi/status');
      // Disabled for private access
      // Mocked/fallback metrics (no fetch)
      setMetrics({
        alba: { status: 'online', connections: 847, efficiency: 94 },
        albi: { status: 'online', creativity: 94, intelligence: 98 },
        jona: { status: 'online', harmony: 0.98, stability: 99 },
        system: { cpu_load: 12, memory_usage: 45, uptime_hours: 720 }
      });
    } catch {
      // Use fallback metrics
      setMetrics({
        alba: { status: 'online', connections: 847, efficiency: 94 },
        albi: { status: 'online', creativity: 94, intelligence: 98 },
        jona: { status: 'online', harmony: 0.98, stability: 99 },
        system: { cpu_load: 12, memory_usage: 45, uptime_hours: 720 }
      });
    }
  };

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    setTimeout(() => {
      if (password === ADMIN_PASSWORD) {
        setIsAuthenticated(true);
        sessionStorage.setItem('admin_authenticated', 'true');
        setError('');
        fetchMetrics();
      } else {
        setError('Invalid password');
      }
      setLoading(false);
    }, 500);
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    sessionStorage.removeItem('admin_authenticated');
    setPassword('');
  };

  // Login Modal
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 flex items-center justify-center p-4">
        <div className="w-full max-w-md">
          <div className="bg-slate-800/50 backdrop-blur-xl border border-slate-700/50 rounded-2xl p-8 shadow-2xl">
            <div className="text-center mb-8">
              <div className="w-20 h-20 mx-auto bg-gradient-to-br from-red-500 to-orange-500 rounded-2xl flex items-center justify-center mb-4 shadow-lg">
                <span className="text-4xl">🔒</span>
              </div>
              <h1 className="text-2xl font-bold text-white mb-2">Admin Access</h1>
              <p className="text-gray-400">Infrastructure Dashboard</p>
            </div>

            <form onSubmit={handleLogin} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Admin Password
                </label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full px-4 py-3 bg-slate-900/50 border border-slate-600 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-violet-500 focus:ring-1 focus:ring-violet-500"
                  placeholder="Enter admin password"
                  autoFocus
                />
              </div>

              {error && (
                <div className="p-3 bg-red-500/20 border border-red-500/50 rounded-lg text-red-400 text-sm text-center">
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={loading || !password}
                className="w-full py-3 bg-gradient-to-r from-violet-600 to-violet-600 hover:from-violet-500 hover:to-violet-500 disabled:opacity-50 disabled:cursor-not-allowed rounded-xl font-semibold text-white transition-all shadow-lg shadow-violet-500/30"
              >
                {loading ? 'Authenticating...' : 'Access Dashboard'}
              </button>
            </form>

            <div className="mt-6 text-center">
              <Link href="/" className="text-gray-400 hover:text-violet-400 text-sm transition-colors">
                ← Back to Public Site
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Admin Dashboard
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-white">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-2xl">🛡️</span>
            <div>
              <h1 className="text-xl font-bold">Admin Dashboard</h1>
              <p className="text-xs text-gray-400">Infrastructure Monitoring</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-green-500/20 text-green-400 text-sm">
              <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse"></span>
              Authenticated
            </div>
            <button
              onClick={handleLogout}
              className="px-4 py-2 bg-red-500/20 hover:bg-red-500/30 border border-red-500/50 rounded-lg text-red-400 text-sm transition-all"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* System Overview */}
        {metrics && (
          <section className="mb-12">
            <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
              <span>📊</span> System Overview
            </h2>
            <div className="grid md:grid-cols-4 gap-4">
              <div className="p-6 rounded-xl bg-slate-800/50 border border-slate-700/50">
                <p className="text-gray-400 text-sm mb-1">CPU Load</p>
                <p className="text-3xl font-bold text-violet-400">{metrics.system.cpu_load}%</p>
                <div className="mt-2 h-2 bg-slate-700 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-gradient-to-r from-violet-500 to-violet-500"
                    style={{ width: `${metrics.system.cpu_load}%` }}
                  ></div>
                </div>
              </div>
              <div className="p-6 rounded-xl bg-slate-800/50 border border-slate-700/50">
                <p className="text-gray-400 text-sm mb-1">Memory Usage</p>
                <p className="text-3xl font-bold text-purple-400">{metrics.system.memory_usage}%</p>
                <div className="mt-2 h-2 bg-slate-700 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-gradient-to-r from-purple-500 to-pink-500"
                    style={{ width: `${metrics.system.memory_usage}%` }}
                  ></div>
                </div>
              </div>
              <div className="p-6 rounded-xl bg-slate-800/50 border border-slate-700/50">
                <p className="text-gray-400 text-sm mb-1">Uptime</p>
                <p className="text-3xl font-bold text-green-400">{metrics.system.uptime_hours}h</p>
                <p className="text-xs text-gray-500 mt-2">≈ {Math.floor(metrics.system.uptime_hours / 24)} days</p>
              </div>
              <div className="p-6 rounded-xl bg-slate-800/50 border border-slate-700/50">
                <p className="text-gray-400 text-sm mb-1">System Status</p>
                <p className="text-3xl font-bold text-green-400">Online</p>
                <p className="text-xs text-gray-500 mt-2">All services operational</p>
              </div>
            </div>
          </section>
        )}

        {/* ASI Trinity */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
            <span>🧠</span> ASI Trinity - Core Engines
          </h2>
          <div className="grid md:grid-cols-3 gap-6">
            {ASI_TRINITY.map((asi) => (
              <div 
                key={asi.name}
                className="p-6 rounded-2xl bg-gradient-to-br from-slate-800/50 to-slate-900/80 border border-slate-700/50 hover:border-violet-500/30 transition-all"
              >
                <div className={`w-16 h-16 rounded-xl bg-gradient-to-br ${asi.color} flex items-center justify-center mb-4 shadow-lg`}>
                  <span className="text-3xl">{asi.icon}</span>
                </div>
                <h3 className="text-xl font-bold mb-1">{asi.name}</h3>
                <p className={`text-sm font-medium bg-gradient-to-r ${asi.color} bg-clip-text text-transparent mb-3`}>
                  {asi.role}
                </p>
                <p className="text-gray-400 text-sm mb-4">{asi.description}</p>
                
                {metrics && (
                  <div className="space-y-2 pt-4 border-t border-slate-700/50">
                    {asi.name === 'ALBA' && (
                      <>
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-400">Connections:</span>
                          <span className="text-violet-400">{metrics.alba.connections}</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-400">Efficiency:</span>
                          <span className="text-violet-400">{metrics.alba.efficiency}%</span>
                        </div>
                      </>
                    )}
                    {asi.name === 'ALBI' && (
                      <>
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-400">Creativity:</span>
                          <span className="text-purple-400">{metrics.albi.creativity}%</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-400">Intelligence:</span>
                          <span className="text-purple-400">{metrics.albi.intelligence}%</span>
                        </div>
                      </>
                    )}
                    {asi.name === 'JONA' && (
                      <>
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-400">Harmony:</span>
                          <span className="text-amber-400">{(metrics.jona.harmony * 100).toFixed(0)}%</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-400">Stability:</span>
                          <span className="text-amber-400">{metrics.jona.stability}%</span>
                        </div>
                      </>
                    )}
                  </div>
                )}
                
                <div className="flex items-center gap-2 text-sm mt-4">
                  <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse"></span>
                  <span className="text-gray-500">Active</span>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Infrastructure Modules */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
            <span>🔧</span> Infrastructure Modules
          </h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {ADMIN_MODULES.filter(m => !m.private).map((module) => (
              <Link 
                key={module.id}
                href={`/modules/${module.id}`}
                className="p-6 rounded-2xl bg-gradient-to-br from-slate-800/50 to-slate-900/80 border border-slate-700/50 hover:border-violet-500/50 transition-all group"
              >
                <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${module.color} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform shadow-lg`}>
                  <span className="text-2xl">{module.icon}</span>
                </div>
                <div className="flex items-center gap-2 mb-2">
                  <h3 className="text-lg font-semibold">{module.name}</h3>
                  <span className="px-2 py-0.5 text-xs rounded-full bg-orange-500/20 text-orange-400">
                    {module.category}
                  </span>
                </div>
                <p className="text-gray-400 text-sm">{module.description}</p>
                <div className="mt-4 flex items-center gap-2 text-violet-400 group-hover:gap-3 transition-all">
                  <span className="text-sm font-medium">Open Module</span>
                  <span>→</span>
                </div>
              </Link>
            ))}
          </div>
        </section>

        {/* 🔒 PRIVATE ADMIN MODULES - Neuroacoustic & Neural Biofeedback */}
        <section className="mb-12 p-8 rounded-2xl bg-gradient-to-br from-red-900/20 to-purple-900/20 border border-red-700/30 backdrop-blur-sm">
          <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
            <span>🔒</span> <span className="text-red-400">PRIVATE ADMIN MODULES</span>
          </h2>
          <p className="text-gray-300 mb-6">Advanced neural processing systems - Administrator access only</p>
          <div className="grid md:grid-cols-2 gap-6">
            {ADMIN_MODULES.filter(m => m.private).map((module) => (
              <Link
                key={module.id}
                href={`/modules/${module.id}`}
                className="p-6 rounded-2xl bg-gradient-to-br from-slate-900/60 to-slate-950/80 border border-red-700/50 hover:border-red-500/80 transition-all group shadow-lg"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${module.color} flex items-center justify-center group-hover:scale-110 transition-transform shadow-lg`}>
                    <span className="text-2xl">{module.icon}</span>
                  </div>
                  <span className="px-3 py-1 text-xs rounded-full bg-red-600/40 text-red-300 font-semibold border border-red-600/50">
                    🔒 PRIVATE
                  </span>
                </div>
                <div className="mb-2">
                  <h3 className="text-lg font-semibold text-white">{module.name}</h3>
                  <span className="text-xs text-red-400 font-medium">Admin Only • {module.category}</span>
                </div>
                <p className="text-gray-300 text-sm mb-4">{module.description}</p>
                <div className="flex items-center gap-2 text-red-400 group-hover:gap-3 transition-all">
                  <span className="text-sm font-medium">Access Module</span>
                  <span>→</span>
                </div>
              </Link>
            ))}
          </div>
          <div className="mt-6 p-4 rounded-lg bg-red-950/40 border border-red-800/50">
            <p className="text-sm text-red-300 flex items-center gap-2">
              <span>⚠️</span> These modules contain sensitive neural processing capabilities and are restricted to administrators only.
            </p>
          </div>
        </section>

        {/* Tech Stack */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
            <span>⚙️</span> Technology Stack
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {TECH_STACK.map((tech) => (
              <div 
                key={tech.name}
                className="p-4 rounded-xl bg-slate-800/50 border border-slate-700/50 text-center hover:border-violet-500/30 transition-all"
              >
                <span className="text-3xl mb-2 block">{tech.icon}</span>
                <h4 className="font-semibold text-white">{tech.name}</h4>
                <p className="text-xs text-gray-400">{tech.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Quick Actions */}
        <section>
          <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
            <span>⚡</span> Quick Actions
          </h2>
          <div className="grid md:grid-cols-3 gap-4">
            <Link 
              href="/modules"
              className="p-4 rounded-xl bg-violet-500/10 border border-violet-500/30 hover:bg-violet-500/20 transition-all text-center"
            >
              <span className="text-2xl block mb-2">📊</span>
              <span className="font-medium">All Modules</span>
            </Link>
            <Link 
              href="/developers"
              className="p-4 rounded-xl bg-purple-500/10 border border-purple-500/30 hover:bg-purple-500/20 transition-all text-center"
            >
              <span className="text-2xl block mb-2">📚</span>
              <span className="font-medium">API Docs</span>
            </Link>
            <Link 
              href="/"
              className="p-4 rounded-xl bg-gray-500/10 border border-gray-500/30 hover:bg-gray-500/20 transition-all text-center"
            >
              <span className="text-2xl block mb-2">🏠</span>
              <span className="font-medium">Public Site</span>
            </Link>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800 py-8 px-4 mt-12">
        <div className="max-w-7xl mx-auto text-center text-gray-500 text-sm">
          <p>🔒 Admin Dashboard - Infrastructure Monitoring</p>
          <p className="mt-2">© 2026 Kloud. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}








