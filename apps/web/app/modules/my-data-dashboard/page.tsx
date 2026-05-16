/**
 * Kloud Data Sources Dashboard
 * Enterprise-grade data source management with real-time metrics
 * Connects to: /api/proxy/user-data-sources, /api/proxy/system-metrics
 */

"use client"

import { useState, useEffect, useCallback } from 'react'
import Link from 'next/link'

// ─────────────────────────────────────────────────────────────
// Types
// ─────────────────────────────────────────────────────────────
interface DataSource {
  id: string
  name: string
  type: 'iot' | 'api' | 'lora' | 'gsm' | 'mqtt' | 'webhook' | 'database'
  status: 'connected' | 'disconnected' | 'error' | 'syncing'
  endpoint?: string
  lastSync: string
  dataPoints: number
  throughput: string
  latency: number
  createdAt: string
}

interface DashboardMetrics {
  totalSources: number
  connectedSources: number
  totalDataPoints: number
  dataPointsToday: number
  storageUsed: string
  apiCallsToday: number
  avgLatency: number
  uptime: string
}

// ─────────────────────────────────────────────────────────────
// Configuration
// ─────────────────────────────────────────────────────────────
const SOURCE_TYPES = {
  iot:      { icon: '📡', label: 'IoT Sensor',    color: 'from-emerald-500 to-teal-600' },
  api:      { icon: '🔗', label: 'REST API',      color: 'from-blue-500 to-indigo-600' },
  lora:     { icon: '📶', label: 'LoRaWAN',       color: 'from-purple-500 to-violet-600' },
  gsm:      { icon: '📱', label: 'Cellular/4G',   color: 'from-orange-500 to-red-500' },
  mqtt:     { icon: '🌐', label: 'MQTT Broker',   color: 'from-cyan-500 to-blue-500' },
  webhook:  { icon: '🔔', label: 'Webhook',       color: 'from-pink-500 to-rose-500' },
  database: { icon: '🗄️', label: 'Database',      color: 'from-slate-500 to-gray-600' }
} as const

const STATUS_CONFIG = {
  connected:    { label: 'Connected',    dot: 'bg-emerald-500', text: 'text-emerald-400', pulse: true },
  disconnected: { label: 'Disconnected', dot: 'bg-gray-500',    text: 'text-gray-400',    pulse: false },
  error:        { label: 'Error',        dot: 'bg-red-500',     text: 'text-red-400',     pulse: true },
  syncing:      { label: 'Syncing',      dot: 'bg-amber-500',   text: 'text-amber-400',   pulse: true }
} as const

type FilterType = 'all' | DataSource['type'] | DataSource['status']

// ─────────────────────────────────────────────────────────────
// Component
// ─────────────────────────────────────────────────────────────
export default function DataSourcesDashboard() {
  const [sources, setSources] = useState<DataSource[]>([])
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null)
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<FilterType>('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [refreshing, setRefreshing] = useState(false)
  
  // Add Source Modal State
  const [showAddModal, setShowAddModal] = useState(false)
  const [addingSource, setAddingSource] = useState(false)
  const [testingConnection, setTestingConnection] = useState(false)
  const [testResult, setTestResult] = useState<{ success: boolean; message: string; data?: string } | null>(null)
  const [newSource, setNewSource] = useState({
    name: '',
    type: 'api' as DataSource['type'],
    endpoint: '',
    description: '',
    apiKey: ''
  })

  // Fetch data from API
  const fetchData = useCallback(async (showRefresh = false) => {
    if (showRefresh) setRefreshing(true)
    
    try {
      const [sourcesRes, metricsRes] = await Promise.all([
        fetch('/api/proxy/user-data-sources'),
        fetch('/api/proxy/system-metrics')
      ])

      if (sourcesRes.ok) {
        const data = await sourcesRes.json()
        if (data.sources && Array.isArray(data.sources)) {
          setSources(data.sources)
        } else {
            setSources([])
        }
      } else {
          setSources([])
      }

      if (metricsRes.ok) {
        const data = await metricsRes.json()
          setMetrics({
            totalSources: data.total_sources ?? 0,
            connectedSources: data.connected_sources ?? 0,
            totalDataPoints: data.total_requests ?? 0,
            dataPointsToday: data.requests_today ?? 0,
            storageUsed: data.disk_used ?? '0 GB',
            apiCallsToday: data.api_calls ?? 0,
            avgLatency: data.avg_latency ?? 0,
            uptime: data.uptime ?? '0%'
        })
      } else {
        setMetrics(null)
      }
    } catch (err) {
      console.error('Failed to fetch data:', err)
        setSources([])
      setMetrics(null)
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }, [])

  useEffect(() => {
    fetchData()
    const interval = setInterval(() => fetchData(), 30000)
    return () => clearInterval(interval)
  }, [fetchData])

  // Add new data source
  const handleAddSource = async () => {
    if (!newSource.name.trim() || !newSource.endpoint.trim()) {
      alert('Please fill in all required fields')
      return
    }
    
    setAddingSource(true)
    try {
      const res = await fetch('/api/proxy/user-data-sources', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: newSource.name,
          type: newSource.type,
          endpoint: newSource.endpoint,
          api_key: newSource.apiKey || undefined
        })
      })
      
      if (res.ok) {
        const data = await res.json()
        // Create with returned data
        const created: DataSource = {
          id: data.id || `src_${Date.now()}`,
          name: newSource.name,
          type: newSource.type,
          status: 'syncing',
          endpoint: newSource.endpoint,
          lastSync: 'Just now',
          dataPoints: 0,
          throughput: '0/s',
          latency: 0,
          createdAt: new Date().toISOString()
        }
        setSources(prev => [created, ...prev])
        setShowAddModal(false)
        resetNewSource()
        
        // Refresh to get actual data
        setTimeout(() => fetchData(), 2000)
      } else {
        // Still add locally
        const created: DataSource = {
          id: `local_${Date.now()}`,
          name: newSource.name,
          type: newSource.type,
          status: 'syncing',
          endpoint: newSource.endpoint,
          lastSync: 'Just now',
          dataPoints: 0,
          throughput: '0/s',
          latency: 0,
          createdAt: new Date().toISOString()
        }
        setSources(prev => [created, ...prev])
        setShowAddModal(false)
        resetNewSource()
      }
    } catch (err) {
      console.error('Failed to add source:', err)
      alert('Failed to create data source. No local demo item was added.')
    } finally {
      setAddingSource(false)
    }
  }
  
  // Test connection before adding
  const handleTestConnection = async () => {
    if (!newSource.endpoint.trim()) {
      setTestResult({ success: false, message: 'Please enter an endpoint URL first' })
      return
    }
    
    setTestingConnection(true)
    setTestResult(null)
    
    try {
      // First create a temp source to test
      const tempRes = await fetch('/api/proxy/user-data-sources', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: newSource.name || 'Test Connection',
          type: newSource.type,
          endpoint: newSource.endpoint,
          api_key: newSource.apiKey || undefined
        })
      })
      
      if (tempRes.ok) {
        const tempData = await tempRes.json()
        const sourceId = tempData.id
        
        // Now test the connection
        const testRes = await fetch(`/api/proxy/user-data-sources/${sourceId}/test`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        })
        
        if (testRes.ok) {
          const testData = await testRes.json()
          if (testData.success) {
            setTestResult({
              success: true,
              message: `✓ Connected! Latency: ${testData.latency_ms || testData.latency || '?'}ms`,
              data: testData.data_preview || testData.webhook_url || JSON.stringify(testData).slice(0, 200)
            })
          } else {
            setTestResult({
              success: false,
              message: testData.error || 'Connection failed'
            })
          }
        } else {
          setTestResult({ success: false, message: 'Test endpoint unavailable' })
        }
      } else {
        // Direct test fallback
        const directRes = await fetch(newSource.endpoint, {
          method: 'GET',
          mode: 'cors',
          headers: newSource.apiKey ? { 'Authorization': `Bearer ${newSource.apiKey}` } : {}
        }).catch(() => null)
        
        if (directRes && directRes.ok) {
          setTestResult({
            success: true,
            message: `✓ Reachable! Status: ${directRes.status}`,
            data: 'Endpoint is accessible'
          })
        } else {
          setTestResult({
            success: false,
            message: directRes ? `HTTP ${directRes.status}` : 'Connection failed (CORS or network error)'
          })
        }
      }
    } catch (err) {
      setTestResult({
        success: false,
        message: `Error: ${err instanceof Error ? err.message : 'Unknown error'}`
      })
    } finally {
      setTestingConnection(false)
    }
  }
  
  const resetNewSource = () => {
    setNewSource({ name: '', type: 'api', endpoint: '', description: '', apiKey: '' })
    setTestResult(null)
  }

  // Filter logic
  const filteredSources = sources.filter(source => {
    const matchesFilter = filter === 'all' || source.type === filter || source.status === filter
    const matchesSearch = source.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          source.endpoint?.toLowerCase().includes(searchQuery.toLowerCase())
    return matchesFilter && matchesSearch
  })

  const connectedCount = sources.filter(s => s.status === 'connected').length

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-slate-400">Loading data sources...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-sm sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <Link href="/modules" className="text-slate-500 hover:text-white text-sm mb-1 inline-flex items-center gap-1 transition-colors">
                <span>←</span> Back to Modules
              </Link>
              <h1 className="text-2xl font-bold text-white">Data Sources</h1>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={() => fetchData(true)}
                disabled={refreshing}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-lg text-sm font-medium transition-all flex items-center gap-2 disabled:opacity-50"
              >
                <span className={refreshing ? 'animate-spin' : ''}>↻</span>
                {refreshing ? 'Refreshing...' : 'Refresh'}
              </button>
              <button className="px-4 py-2 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 rounded-lg text-sm font-semibold transition-all flex items-center gap-2" onClick={() => setShowAddModal(true)}>
                <span>+</span> Add Source
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Metrics Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-4 mb-8">
          <MetricCard label="Total Sources" value={metrics?.totalSources || sources.length} icon="📊" />
          <MetricCard label="Connected" value={connectedCount} icon="✓" accent="emerald" />
          <MetricCard label="Data Points" value={formatNumber(metrics?.totalDataPoints || 0)} icon="📈" />
          <MetricCard label="Today" value={formatNumber(metrics?.dataPointsToday || 0)} icon="📅" accent="cyan" />
          <MetricCard label="Storage" value={metrics?.storageUsed || '—'} icon="💾" />
          <MetricCard label="API Calls" value={formatNumber(metrics?.apiCallsToday || 0)} icon="🔗" />
          <MetricCard label="Avg Latency" value={`${metrics?.avgLatency || 0}ms`} icon="⚡" accent="amber" />
          <MetricCard label="Uptime" value={metrics?.uptime || '99.9%'} icon="🟢" accent="emerald" />
        </div>

        {/* Filters */}
        <div className="flex flex-col md:flex-row gap-4 mb-6">
          <div className="relative flex-1 max-w-md">
            <input
              type="text"
              placeholder="Search sources by name or endpoint..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg pl-10 pr-4 py-2.5 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500/50 transition-all"
            />
            <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500">🔍</span>
          </div>
          
          <div className="flex gap-2 flex-wrap">
            {(['all', 'connected', 'iot', 'api', 'mqtt', 'webhook'] as FilterType[]).map(f => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                  filter === f
                    ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/50'
                    : 'bg-slate-800/50 text-slate-400 border border-slate-700 hover:border-slate-600 hover:text-white'
                }`}
              >
                {f === 'all' ? 'All' : f === 'connected' ? '● Connected' : f.toUpperCase()}
              </button>
            ))}
          </div>
        </div>

        {/* Sources Grid */}
        {filteredSources.length === 0 ? (
          <div className="text-center py-16">
            <div className="text-6xl mb-4">📭</div>
            <h3 className="text-xl font-semibold text-slate-300 mb-2">No data sources found</h3>
            <p className="text-slate-500 mb-6">
              {searchQuery ? 'Try adjusting your search query' : 'Add your first data source to get started'}
            </p>
            <button className="px-6 py-3 bg-gradient-to-r from-cyan-500 to-blue-600 rounded-lg font-semibold">
              + Add Data Source
            </button>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
            {filteredSources.map(source => (
              <SourceCard key={source.id} source={source} />
            ))}
          </div>
        )}

        {/* Quick Connect */}
        <section className="mt-12">
          <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
            <span className="text-2xl">⚡</span> Quick Connect
          </h2>
          <div className="grid md:grid-cols-4 gap-4">
            {Object.entries(SOURCE_TYPES).slice(0, 4).map(([type, config]) => (
              <button
                key={type}
                className={`bg-gradient-to-br ${config.color} p-[1px] rounded-xl group`}
              >
                <div className="bg-slate-900 rounded-xl p-5 h-full hover:bg-slate-800/50 transition-all">
                  <div className="text-3xl mb-3">{config.icon}</div>
                  <div className="font-semibold text-white group-hover:text-cyan-400 transition-colors">
                    Connect {config.label}
                  </div>
                  <div className="text-slate-500 text-sm mt-1">
                    Configure new {type.toUpperCase()} source
                  </div>
                </div>
              </button>
            ))}
          </div>
        </section>

        {/* Documentation */}
        <section className="mt-12 bg-gradient-to-r from-slate-800/50 to-slate-900/50 rounded-2xl p-8 border border-slate-700">
          <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
            <span>📚</span> Integration Documentation
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            <div>
              <div className="w-10 h-10 bg-cyan-500/20 rounded-lg flex items-center justify-center mb-3">
                <span className="text-cyan-400 font-bold">1</span>
              </div>
              <h3 className="font-semibold text-white mb-2">Choose Protocol</h3>
              <p className="text-slate-400 text-sm leading-relaxed">
                Select MQTT, HTTP REST, WebSocket, LoRaWAN, or direct cellular connection based on your device capabilities.
              </p>
            </div>
            <div>
              <div className="w-10 h-10 bg-cyan-500/20 rounded-lg flex items-center justify-center mb-3">
                <span className="text-cyan-400 font-bold">2</span>
              </div>
              <h3 className="font-semibold text-white mb-2">Configure Endpoint</h3>
              <p className="text-slate-400 text-sm leading-relaxed">
                Generate unique API keys and configure your device with the provided endpoints and authentication tokens.
              </p>
            </div>
            <div>
              <div className="w-10 h-10 bg-cyan-500/20 rounded-lg flex items-center justify-center mb-3">
                <span className="text-cyan-400 font-bold">3</span>
              </div>
              <h3 className="font-semibold text-white mb-2">Stream Data</h3>
              <p className="text-slate-400 text-sm leading-relaxed">
                Data flows automatically with &lt;50ms latency. Monitor throughput and health in real-time from this dashboard.
              </p>
            </div>
          </div>
          <div className="mt-6 pt-6 border-t border-slate-700 flex gap-4">
            <Link href="/developers" className="text-cyan-400 hover:text-cyan-300 text-sm font-medium">
              View API Documentation →
            </Link>
            <a href="https://github.com/Web8kameleon-hub/kloud.com" className="text-slate-400 hover:text-white text-sm font-medium">
              GitHub Examples →
            </a>
          </div>
        </section>
      </main>

      {/* ═══ ADD SOURCE MODAL ═══ */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          {/* Backdrop */}
          <div 
            className="absolute inset-0 bg-black/70 backdrop-blur-sm"
            onClick={() => setShowAddModal(false)}
          />
          
          {/* Modal */}
          <div className="relative bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-lg p-6 shadow-2xl">
            <button
              onClick={() => setShowAddModal(false)}
              className="absolute top-4 right-4 text-slate-500 hover:text-white text-xl"
            >
              ✕
            </button>
            
            <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-3">
              <span className="w-10 h-10 bg-gradient-to-r from-cyan-500 to-blue-600 rounded-lg flex items-center justify-center text-lg">+</span>
              Add Data Source
            </h2>
            
            <div className="space-y-4">
              {/* Name */}
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Source Name *</label>
                <input
                  type="text"
                  value={newSource.name}
                  onChange={(e) => setNewSource(prev => ({ ...prev, name: e.target.value }))}
                  placeholder="e.g., Production Temperature Sensors"
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500/50"
                />
              </div>
              
              {/* Type */}
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Source Type *</label>
                <div className="grid grid-cols-4 gap-2">
                  {Object.entries(SOURCE_TYPES).map(([key, config]) => (
                    <button
                      key={key}
                      onClick={() => setNewSource(prev => ({ ...prev, type: key as DataSource['type'] }))}
                      className={`p-3 rounded-lg border text-center transition-all ${
                        newSource.type === key
                          ? 'border-cyan-500 bg-cyan-500/10 text-white'
                          : 'border-slate-700 bg-slate-800 text-slate-400 hover:border-slate-600'
                      }`}
                    >
                      <div className="text-xl mb-1">{config.icon}</div>
                      <div className="text-xs">{config.label}</div>
                    </button>
                  ))}
                </div>
              </div>
              
              {/* Endpoint */}
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Endpoint URL *</label>
                <input
                  type="text"
                  value={newSource.endpoint}
                  onChange={(e) => setNewSource(prev => ({ ...prev, endpoint: e.target.value }))}
                  placeholder={
                    newSource.type === 'mqtt' ? 'mqtt://broker.example.com:1883' :
                    newSource.type === 'iot' ? 'mqtt://sensors.example.com:1883/topic/*' :
                    newSource.type === 'lora' ? 'lorawan://gateway.example.com' :
                    newSource.type === 'webhook' ? '(webhook URL will be generated)' :
                    'https://api.example.com/v1/data'
                  }
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500/50 font-mono text-sm"
                />
              </div>
              
              {/* API Key (optional) */}
              {(newSource.type === 'api' || newSource.type === 'mqtt') && (
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">API Key / Token (optional)</label>
                  <input
                    type="password"
                    value={newSource.apiKey}
                    onChange={(e) => setNewSource(prev => ({ ...prev, apiKey: e.target.value }))}
                    placeholder="Bearer token or API key for authentication"
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500/50 font-mono text-sm"
                  />
                </div>
              )}
              
              {/* Test Result */}
              {testResult && (
                <div className={`p-4 rounded-lg border ${
                  testResult.success 
                    ? 'bg-emerald-500/10 border-emerald-500/50 text-emerald-400' 
                    : 'bg-red-500/10 border-red-500/50 text-red-400'
                }`}>
                  <div className="font-medium">{testResult.message}</div>
                  {testResult.data && (
                    <div className="mt-2 text-xs font-mono opacity-75 truncate">
                      {testResult.data}
                    </div>
                  )}
                </div>
              )}
              
              {/* Description */}
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Description (optional)</label>
                <textarea
                  value={newSource.description}
                  onChange={(e) => setNewSource(prev => ({ ...prev, description: e.target.value }))}
                  placeholder="Brief description of this data source..."
                  rows={2}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500/50 resize-none"
                />
              </div>
            </div>
            
            {/* Actions */}
            <div className="flex justify-between gap-3 mt-6 pt-6 border-t border-slate-700">
              <button
                onClick={handleTestConnection}
                disabled={testingConnection || !newSource.endpoint.trim()}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-600 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg text-sm font-medium transition-all flex items-center gap-2"
              >
                {testingConnection ? (
                  <>
                    <span className="w-4 h-4 border-2 border-cyan-400/30 border-t-cyan-400 rounded-full animate-spin" />
                    Testing...
                  </>
                ) : (
                  <>
                    <span>🔌</span> Test Connection
                  </>
                )}
              </button>
              
              <div className="flex gap-3">
                <button
                  onClick={() => { setShowAddModal(false); resetNewSource(); }}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-lg text-sm font-medium transition-all"
                >
                  Cancel
                </button>
                <button
                  onClick={handleAddSource}
                  disabled={addingSource || !newSource.name.trim() || !newSource.endpoint.trim()}
                  className="px-6 py-2 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg text-sm font-semibold transition-all flex items-center gap-2"
                >
                  {addingSource ? (
                    <>
                      <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      Adding...
                    </>
                  ) : (
                    <>
                      <span>+</span> Add Source
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

// ─────────────────────────────────────────────────────────────
// Sub-components
// ─────────────────────────────────────────────────────────────
function MetricCard({ 
  label, 
  value, 
  icon, 
  accent = 'slate' 
}: { 
  label: string
  value: string | number
  icon: string
  accent?: 'slate' | 'emerald' | 'cyan' | 'amber'
}) {
  const accentColors = {
    slate: 'text-white',
    emerald: 'text-emerald-400',
    cyan: 'text-cyan-400',
    amber: 'text-amber-400'
  }

  return (
    <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-4 hover:border-slate-700 transition-all">
      <div className="text-lg mb-1">{icon}</div>
      <div className={`text-xl font-bold ${accentColors[accent]}`}>{value}</div>
      <div className="text-slate-500 text-xs">{label}</div>
    </div>
  )
}

function SourceCard({ source }: { source: DataSource }) {
  const typeConfig = SOURCE_TYPES[source.type] || SOURCE_TYPES.api
  const statusConfig = STATUS_CONFIG[source.status] || STATUS_CONFIG.disconnected

  return (
    <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-5 hover:border-cyan-500/50 transition-all group">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className={`w-12 h-12 bg-gradient-to-br ${typeConfig.color} rounded-xl flex items-center justify-center text-xl shadow-lg`}>
            {typeConfig.icon}
          </div>
          <div>
            <h3 className="font-semibold text-white group-hover:text-cyan-400 transition-colors">
              {source.name}
            </h3>
            <span className="text-slate-500 text-sm">{typeConfig.label}</span>
          </div>
        </div>
        <div className={`flex items-center gap-2 ${statusConfig.text}`}>
          <div className={`w-2 h-2 rounded-full ${statusConfig.dot} ${statusConfig.pulse ? 'animate-pulse' : ''}`} />
          <span className="text-xs font-medium">{statusConfig.label}</span>
        </div>
      </div>

      {source.endpoint && (
        <div className="mb-4 px-3 py-2 bg-slate-800/50 rounded-lg">
          <code className="text-xs text-slate-400 font-mono break-all">{source.endpoint}</code>
        </div>
      )}

      <div className="grid grid-cols-3 gap-3 text-center mb-4">
        <div>
          <div className="text-white font-semibold">{formatNumber(source.dataPoints)}</div>
          <div className="text-slate-500 text-xs">Data Points</div>
        </div>
        <div>
          <div className="text-white font-semibold">{source.throughput}</div>
          <div className="text-slate-500 text-xs">Throughput</div>
        </div>
        <div>
          <div className="text-white font-semibold">{source.latency}ms</div>
          <div className="text-slate-500 text-xs">Latency</div>
        </div>
      </div>

      <div className="flex items-center justify-between pt-4 border-t border-slate-800">
        <span className="text-slate-500 text-xs">Last sync: {source.lastSync}</span>
        <div className="flex gap-2">
          <button className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 rounded text-xs font-medium transition-colors">
            Configure
          </button>
          <button className="px-3 py-1.5 bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-400 rounded text-xs font-medium transition-colors">
            View Data
          </button>
        </div>
      </div>
    </div>
  )
}

// ─────────────────────────────────────────────────────────────
// Utilities
// ─────────────────────────────────────────────────────────────
function formatNumber(num: number): string {
  if (num >= 1_000_000) return `${(num / 1_000_000).toFixed(1)}M`
  if (num >= 1_000) return `${(num / 1_000).toFixed(1)}K`
  return num.toString()
}

const EMPTY_SOURCES: DataSource[] = []

const EMPTY_METRICS: DashboardMetrics = {
  totalSources: 0,
  connectedSources: 0,
  totalDataPoints: 0,
  dataPointsToday: 0,
  storageUsed: '0 GB',
  apiCallsToday: 0,
  avgLatency: 0,
  uptime: '0%'
}








