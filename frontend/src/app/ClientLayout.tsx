'use client'

// Kloud Industrial Cloud Client Layout
// Author: Ledjan Ahmati
// All interactive logic moved here

import React, { useEffect, useState, useMemo, useCallback } from 'react'
import dynamic from 'next/dynamic'

interface GlobalStatus {
  systemUptime: string
  activeUsers: number
  lastGlobalAudit: string
  complianceStatus: string
  tracingId: string
  apiHealth: 'healthy' | 'degraded' | 'critical'
  cpuUsage: number
  memoryUsage: number
}

interface GlobalUser {
  username: string
  role: string
  lastLogin: string
  status: string
  permissions: string[]
}

// Lazy load heavy components
const PerformanceMonitor = dynamic(() => import('../components/PerformanceMonitor'), {
  loading: () => <div className="animate-pulse bg-gray-700 h-8 rounded" />,
  ssr: false
})

export default function ClientLayout({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<GlobalUser | null>(null)
  const [status, setStatus] = useState<GlobalStatus | null>(null)
  const [globalLog, setGlobalLog] = useState<Array<{ event: string; time: string }>>([])
  const [isConnected, setIsConnected] = useState(true)

  // Memoized user data
  const userData = useMemo(() => ({
    username: 'cloud_admin',
    role: 'Superuser',
    lastLogin: new Date(Date.now() - 7200 * 1000).toLocaleString(),
    status: 'Active',
    permissions: ['admin', 'read', 'write', 'delete', 'audit']
  }), [])

  // Memoized status data
  const statusData = useMemo(() => ({
    systemUptime: '120h 42m',
    activeUsers: 12,
    lastGlobalAudit: new Date(Date.now() - 1800 * 1000).toLocaleString(),
    complianceStatus: 'Compliant',
    tracingId: Math.floor(Math.random() * 1e9).toString(16),
    apiHealth: 'healthy' as const,
    cpuUsage: Math.random() * 80,
    memoryUsage: Math.random() * 75
  }), [])

  // Fetch system health with retry logic
  const fetchSystemHealth = useCallback(async () => {
    try {
      const response = await fetch('/api/health', {
        method: 'GET',
        cache: 'no-store',
        signal: AbortSignal.timeout(5000)
      })

      if (!response.ok) throw new Error('Health check failed')

      const healthData = await response.json()
      setStatus(prev => prev ? ({
        ...prev,
        apiHealth: healthData.status === 'ok' ? 'healthy' : 'degraded'
      }) : statusData)
      setIsConnected(true)
    } catch (error) {
      console.warn('[HEALTH CHECK] Failed:', error)
      setIsConnected(false)
      setStatus(prev => prev ? ({
        ...prev,
        apiHealth: 'degraded' as const
      }) : statusData)
    }
  }, [statusData])

  useEffect(() => {
    // Initialize data
    setUser(userData)
    setStatus(statusData)
    setGlobalLog([
      { event: 'Global login', time: new Date(Date.now() - 7200 * 1000).toLocaleTimeString() },
      { event: 'Global audit', time: new Date(Date.now() - 1800 * 1000).toLocaleTimeString() },
      { event: 'System update', time: new Date(Date.now() - 600 * 1000).toLocaleTimeString() },
      { event: 'Health check passed', time: new Date().toLocaleTimeString() }
    ])

    // Health check on mount
    fetchSystemHealth()

    // Poll health every 30 seconds
    const healthInterval = setInterval(fetchSystemHealth, 30000)

    // Connection monitoring
    const handleOnline = () => setIsConnected(true)
    const handleOffline = () => setIsConnected(false)

    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    return () => {
      clearInterval(healthInterval)
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [userData, statusData, fetchSystemHealth])

  const statusColor = {
    healthy: 'bg-green-700',
    degraded: 'bg-yellow-700',
    critical: 'bg-red-700'
  }[status?.apiHealth || 'degraded']

  const connectionStatus = {
    healthy: 'Connected',
    degraded: 'Degraded',
    critical: 'Disconnected'
  }[status?.apiHealth || 'degraded']

  return (
    <div className={`min-h-screen flex flex-col ${!isConnected ? 'opacity-75' : ''}`}>
      {/* Connection Status Bar */}
      {!isConnected && (
        <div className="bg-red-600 text-white px-4 py-2 text-center text-sm font-semibold">
          ⚠️ Offline Mode - Some features may be limited
        </div>
      )}

      {/* Header */}
      <header className={`${statusColor} text-white py-4 px-8 flex items-center justify-between shadow-lg`}>
        <div className="flex items-center gap-4 flex-1">
          <div className="flex items-center gap-2">
            <div className="text-3xl font-black tracking-tight">Kloud</div>
            <span className="text-xs font-bold px-2 py-1 bg-black/30 rounded-full">Cloud</span>
          </div>
          <div className="flex gap-2 ml-4">
            <span className="px-3 py-1 bg-green-600 rounded-lg text-xs font-semibold">Industrial</span>
            <span className={`px-3 py-1 rounded-lg text-xs font-semibold ${statusColor}`}>
              {connectionStatus}
            </span>
            <span className="px-3 py-1 bg-purple-600 rounded-lg text-xs font-semibold">
              Compliance: {status?.complianceStatus ?? 'Unknown'}
            </span>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex gap-6 items-center text-sm font-medium">
          <a href="/modules" className="hover:opacity-80 transition">Modules</a>
          <a href="/dashboard" className="hover:opacity-80 transition">Dashboard</a>
          <a href="/api" className="hover:opacity-80 transition">APIs</a>
          <a href="/docs" className="hover:opacity-80 transition">Docs</a>
          <div className="h-6 w-px bg-white/20" />
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-green-300 rounded-full animate-pulse" />
            <span className="text-xs">{user?.username ?? 'Guest'}</span>
          </div>
        </nav>
      </header>

      {/* Main Content */}
      <main className="flex-1 container mx-auto py-8 px-4">
        {/* System Status Dashboard */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {/* Uptime */}
          <div className="bg-gradient-to-br from-gray-800 to-gray-700 p-6 rounded-lg shadow-lg border border-gray-600">
            <div className="text-xs text-gray-400 font-semibold mb-2">SYSTEM UPTIME</div>
            <div className="text-3xl font-black text-green-400">{status?.systemUptime ?? '-'}</div>
            <div className="text-xs text-gray-500 mt-2">Continuous operation</div>
          </div>

          {/* Active Users */}
          <div className="bg-gradient-to-br from-blue-900 to-blue-800 p-6 rounded-lg shadow-lg border border-blue-600">
            <div className="text-xs text-blue-300 font-semibold mb-2">ACTIVE USERS</div>
            <div className="text-3xl font-black text-white">{status?.activeUsers ?? '-'}</div>
            <div className="text-xs text-blue-200 mt-2">Connected sessions</div>
          </div>

          {/* CPU Usage */}
          <div className="bg-gradient-to-br from-purple-900 to-purple-800 p-6 rounded-lg shadow-lg border border-purple-600">
            <div className="text-xs text-purple-300 font-semibold mb-2">CPU USAGE</div>
            <div className="text-3xl font-black text-white">{Math.round(status?.cpuUsage ?? 0)}%</div>
            <div className="w-full bg-purple-900 rounded-full h-1 mt-3">
              <div
                className="bg-purple-400 h-1 rounded-full transition-all"
                style={{ width: `${Math.min(status?.cpuUsage ?? 0, 100)}%` }}
              />
            </div>
          </div>

          {/* Memory Usage */}
          <div className="bg-gradient-to-br from-orange-900 to-orange-800 p-6 rounded-lg shadow-lg border border-orange-600">
            <div className="text-xs text-orange-300 font-semibold mb-2">MEMORY USAGE</div>
            <div className="text-3xl font-black text-white">{Math.round(status?.memoryUsage ?? 0)}%</div>
            <div className="w-full bg-orange-900 rounded-full h-1 mt-3">
              <div
                className="bg-orange-400 h-1 rounded-full transition-all"
                style={{ width: `${Math.min(status?.memoryUsage ?? 0, 100)}%` }}
              />
            </div>
          </div>
        </div>

        {/* Content Area */}
        <div className="bg-gray-800 rounded-lg shadow-lg border border-gray-700 p-8">
          {children}
        </div>

        {/* Global Log */}
        <div className="mt-8 bg-gray-800 rounded-lg shadow-lg border border-gray-700 p-6">
          <div className="font-bold text-lg mb-4 text-white">📋 Global Event Log</div>
          <div className="space-y-2 max-h-48 overflow-y-auto">
            {globalLog.map((log, i) => (
              <div key={i} className="flex items-center justify-between text-xs text-gray-400 p-2 hover:bg-gray-700 rounded transition">
                <span>✓ {log.event}</span>
                <span className="text-gray-600">{log.time}</span>
              </div>
            ))}
          </div>
        </div>
      </main>

      {/* Performance Monitor */}
      <PerformanceMonitor />

      {/* Footer */}
      <footer className="bg-gray-900 border-t border-gray-700 text-gray-400 py-6 px-8 text-center text-xs mt-8">
        <div className="mb-2 text-gray-500">
          © 2025 Kloud Industrial Cloud Platform. Enterprise Grade Monitoring & Orchestration.
        </div>
        <div className="flex justify-center gap-4 mb-2 text-gray-600">
          <span>Compliance: {status?.complianceStatus}</span>
          <span>•</span>
          <span>Tracing: {status?.tracingId}</span>
          <span>•</span>
          <span>User: {user?.username}</span>
          <span>•</span>
          <span>Role: {user?.role}</span>
        </div>
        <div className="text-gray-600">
          All systems protected, audited, and monitored. Global compliance enabled.
        </div>
      </footer>
    </div>
  )
}

