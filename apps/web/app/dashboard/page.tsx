'use client';

import Link from 'next/link';
import { useState, useEffect } from 'react';
import { ArrowLeft, Plus, Download } from 'lucide-react';

// Dynamic API URL - uses environment variable or defaults
const OCEAN_API_URL = process.env.NEXT_PUBLIC_OCEAN_API_URL || 'http://localhost:8030';

interface DataSource {
  id: string;
  name: string;
  type: 'IOT' | 'API' | 'DATABASE' | 'WEBHOOK';
  status: 'active' | 'inactive' | 'error';
  lastSync: string;
  dataPoints: number;
}

interface DashboardMetrics {
  totalSources: number;
  activeSources: number;
  totalDataPoints: number;
  trackedMetrics: number;
  laboratories?: number;
}

export default function DataDashboard() {
  const [activeTab, setActiveTab] = useState<'overview' | 'sources' | 'metrics' | 'export'>('overview');
  const [dataSources, setDataSources] = useState<DataSource[]>([]);
  const [metrics, setMetrics] = useState<DashboardMetrics>({
    totalSources: 0,
    activeSources: 0,
    totalDataPoints: 0,
    trackedMetrics: 0,
    laboratories: 0
  });
  const [_loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch real data from Ocean Core API
    fetchRealData();
  }, []);

  const fetchRealData = async () => {
    setLoading(true);
    try {
      // Fetch from Ocean Core API
      const response = await fetch(`${OCEAN_API_URL}/api/status`);
      if (response.ok) {
        const data = await response.json();
        
        // Build data sources from real API response
        const realSources: DataSource[] = [];
        
        // Add sources from data_sources if available
        if (data.data_sources) {
          Object.entries(data.data_sources).forEach(([key, value]: [string, unknown]) => {
            realSources.push({
              id: key,
              name: key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
              type: key.includes('api') ? 'API' : key.includes('iot') ? 'IOT' : 'DATABASE',
              status: 'active',
              lastSync: new Date().toISOString(),
              dataPoints: typeof value === 'number' ? value : ((value as { count?: number })?.count || 0)
            });
          });
        }

        // Update metrics with real data
        setDataSources(realSources);
        setMetrics({
          totalSources: realSources.length || data.data_sources_count || 0,
          activeSources: realSources.filter(s => s.status === 'active').length,
          totalDataPoints: realSources.reduce((acc, s) => acc + s.dataPoints, 0),
          trackedMetrics: realSources.length,
          laboratories: data.laboratories_count || data.labs_count || 23
        });
      }
    } catch (error) {
      console.error('Failed to fetch from Ocean Core:', error);
      // Fallback to empty state
      setMetrics({
        totalSources: 0,
        activeSources: 0,
        totalDataPoints: 0,
        trackedMetrics: 0,
        laboratories: 0
      });
    } finally {
      setLoading(false);
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'IOT': return '📡';
      case 'API': return '🔗';
      case 'DATABASE': return '🗄️';
      case 'WEBHOOK': return '🪝';
      default: return '📊';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'inactive': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      case 'error': return 'bg-red-500/20 text-red-400 border-red-500/30';
      default: return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      {/* Header */}
      <div className="border-b border-slate-800/50 bg-slate-900/50 backdrop-blur-sm sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center gap-4 mb-4">
            <Link href="/" className="p-2 hover:bg-slate-800/50 rounded-lg transition-colors">
              <ArrowLeft className="w-5 h-5 text-gray-400" />
            </Link>
            <div>
              <h1 className="text-3xl font-bold flex items-center gap-2">
                <span>📊</span> My Data Dashboard
              </h1>
              <p className="text-gray-400 text-sm mt-1">Manage your data sources and view metrics</p>
            </div>
          </div>

          {/* Tabs */}
          <div className="flex gap-2 mt-6">
            {['overview', 'sources', 'metrics', 'export'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab as 'overview' | 'sources' | 'metrics' | 'export')}
                className={`px-4 py-2 rounded-lg transition-all font-medium text-sm ${
                  activeTab === tab
                    ? 'bg-blue-800 text-white'
                    : 'bg-slate-800/50 text-gray-400 hover:bg-slate-700/50'
                }`}
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Quick Stats */}
        <div className="grid md:grid-cols-4 gap-4 mb-8">
          <div className="p-6 rounded-xl bg-gradient-to-br from-slate-800/50 to-slate-900/50 border border-slate-700/50">
            <div className="flex items-center justify-between mb-2">
              <span className="text-gray-400 text-sm">Data Sources</span>
              <span className="text-2xl">📊</span>
            </div>
            <div className="text-3xl font-bold">{metrics.totalSources}</div>
            <p className="text-xs text-gray-500 mt-2">{metrics.activeSources} Active</p>
          </div>

          <div className="p-6 rounded-xl bg-gradient-to-br from-slate-800/50 to-slate-900/50 border border-slate-700/50">
            <div className="flex items-center justify-between mb-2">
              <span className="text-gray-400 text-sm">Total Data Points</span>
              <span className="text-2xl">📈</span>
            </div>
            <div className="text-3xl font-bold">{metrics.totalDataPoints}</div>
            <p className="text-xs text-gray-500 mt-2">Across all sources</p>
          </div>

          <div className="p-6 rounded-xl bg-gradient-to-br from-slate-800/50 to-slate-900/50 border border-slate-700/50">
            <div className="flex items-center justify-between mb-2">
              <span className="text-gray-400 text-sm">Tracked Metrics</span>
              <span className="text-2xl">📡</span>
            </div>
            <div className="text-3xl font-bold">{metrics.trackedMetrics}</div>
            <p className="text-xs text-gray-500 mt-2">Active metrics</p>
          </div>

          <div className="p-6 rounded-xl bg-gradient-to-br from-cyan-900/30 to-cyan-950/30 border border-blue-900/50">
            <div className="flex items-center justify-between mb-2">
              <span className="text-gray-400 text-sm">Action</span>
              <span className="text-2xl">➕</span>
            </div>
            <button className="w-full mt-4 py-2 px-3 bg-blue-800 hover:bg-blue-900 text-white rounded-lg font-medium text-sm transition-colors flex items-center justify-center gap-2">
              <Plus className="w-4 h-4" />
              Add Source
            </button>
          </div>
        </div>

        {/* Tab Content */}
        {activeTab === 'overview' && (
          <div className="grid lg:grid-cols-2 gap-8">
            {/* Live Metrics */}
            <section>
              <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                <span>📈</span> Live Metrics
              </h2>
              <div className="p-6 rounded-xl bg-gradient-to-br from-slate-800/50 to-slate-900/50 border border-slate-700/50">
                <div className="space-y-4">
                  <div className="flex justify-between items-center p-3 bg-slate-900/50 rounded-lg">
                    <span className="text-gray-400">Data Points (24h)</span>
                    <span className="font-bold">0</span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-slate-900/50 rounded-lg">
                    <span className="text-gray-400">API Calls (24h)</span>
                    <span className="font-bold">0</span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-slate-900/50 rounded-lg">
                    <span className="text-gray-400">Active Connections</span>
                    <span className="font-bold text-green-400">2</span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-slate-900/50 rounded-lg">
                    <span className="text-gray-400">Last Update</span>
                    <span className="font-bold text-yellow-400">Never</span>
                  </div>
                </div>
              </div>
            </section>

            {/* Active Data Sources */}
            <section>
              <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                <span>🔌</span> Active Data Sources
              </h2>
              <div className="space-y-3">
                {dataSources.map((source) => (
                  <div key={source.id} className="p-4 rounded-xl bg-gradient-to-br from-slate-800/50 to-slate-900/50 border border-slate-700/50 hover:border-blue-700/30 transition-all">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-3">
                        <span className="text-2xl">{getTypeIcon(source.type)}</span>
                        <div>
                          <h3 className="font-semibold">{source.name}</h3>
                          <span className="text-xs text-gray-500">{source.type}</span>
                        </div>
                      </div>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(source.status)}`}>
                        {source.status.charAt(0).toUpperCase() + source.status.slice(1)}
                      </span>
                    </div>
                    <div className="text-xs text-gray-400 space-y-1">
                      <p>Last sync: {source.lastSync}</p>
                      <p>{source.dataPoints} points</p>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          </div>
        )}

        {activeTab === 'sources' && (
          <section>
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold">All Data Sources</h2>
              <button className="px-4 py-2 bg-blue-800 hover:bg-blue-900 text-white rounded-lg font-medium flex items-center gap-2 transition-colors">
                <Plus className="w-4 h-4" />
                Add Data Source
              </button>
            </div>
            <div className="space-y-3">
              {dataSources.map((source) => (
                <div key={source.id} className="p-6 rounded-xl bg-gradient-to-br from-slate-800/50 to-slate-900/50 border border-slate-700/50 hover:border-blue-700/30 transition-all">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <span className="text-4xl">{getTypeIcon(source.type)}</span>
                      <div>
                        <h3 className="text-lg font-semibold">{source.name}</h3>
                        <p className="text-sm text-gray-400">{source.type}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <span className={`px-3 py-1 rounded-full text-sm font-medium border ${getStatusColor(source.status)} inline-block mb-2`}>
                        {source.status.charAt(0).toUpperCase() + source.status.slice(1)}
                      </span>
                      <p className="text-sm text-gray-400">Last sync: {source.lastSync}</p>
                      <p className="text-sm text-gray-400">{source.dataPoints} data points</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {activeTab === 'metrics' && (
          <section>
            <h2 className="text-2xl font-bold mb-6">Performance Metrics</h2>
            <div className="grid md:grid-cols-2 gap-6">
              <div className="p-6 rounded-xl bg-gradient-to-br from-slate-800/50 to-slate-900/50 border border-slate-700/50">
                <h3 className="font-semibold mb-4">Data Volume</h3>
                <div className="h-32 bg-slate-900/50 rounded-lg flex items-center justify-center text-gray-500">
                  Chart placeholder
                </div>
              </div>
              <div className="p-6 rounded-xl bg-gradient-to-br from-slate-800/50 to-slate-900/50 border border-slate-700/50">
                <h3 className="font-semibold mb-4">Source Health</h3>
                <div className="h-32 bg-slate-900/50 rounded-lg flex items-center justify-center text-gray-500">
                  Chart placeholder
                </div>
              </div>
            </div>
          </section>
        )}

        {activeTab === 'export' && (
          <section>
            <h2 className="text-2xl font-bold mb-6">Export Data</h2>
            <div className="p-8 rounded-xl bg-gradient-to-br from-slate-800/50 to-slate-900/50 border border-slate-700/50 text-center">
              <Download className="w-12 h-12 mx-auto mb-4 text-gray-500" />
              <h3 className="text-lg font-semibold mb-2">Export Options</h3>
              <p className="text-gray-400 mb-6">Choose your preferred format</p>
              <div className="flex gap-4 justify-center flex-wrap">
                <button className="px-6 py-2 bg-blue-800 hover:bg-blue-900 text-white rounded-lg font-medium transition-colors">
                  CSV
                </button>
                <button className="px-6 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg font-medium transition-colors">
                  JSON
                </button>
                <button className="px-6 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg font-medium transition-colors">
                  Excel
                </button>
              </div>
            </div>
          </section>
        )}
      </div>
    </div>
  );
}







