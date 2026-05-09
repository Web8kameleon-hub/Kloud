'use client'

import { useState, useEffect, useCallback } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { 
  Database, 
  RefreshCw,
  Play,
  CheckCircle,
  AlertCircle,
  AlertTriangle,
  Server,
  HardDrive,
  Network,
  Clock,
  Zap,
  Send,
  Copy,
  ExternalLink
} from 'lucide-react'

// ============================================================================
// REAL API ENDPOINTS - No fake data, no Math.random()
// ============================================================================

// Use relative paths for security - proxied through Next.js API routes
const API_BASE = ''

interface EndpointResult {
  name: string
  method: 'GET' | 'POST' | 'PUT' | 'DELETE'
  url: string
  status: number | null
  statusText: string
  responseTime: number | null
  response: unknown
  timestamp: string
  isLoading: boolean
  error: string | null
}

interface SystemHealth {
  status: string
  cpu_percent: number
  memory_percent: number
  disk_percent: number
  disk_total: number
  disk_used: number
  uptime_seconds: number
  hostname: string
}

interface ServiceStatus {
  name: string
  healthy: boolean
  latency_ms: number
  url: string
}

export default function DataCollectionPage() {
  // Real API endpoints to monitor
  const [endpoints, setEndpoints] = useState<EndpointResult[]>([
    {
      name: 'System Health',
      method: 'GET',
      url: `${API_BASE}/health`,
      status: null,
      statusText: 'Not tested',
      responseTime: null,
      response: null,
      timestamp: '',
      isLoading: false,
      error: null
    },
    {
      name: 'ASI Trinity Status',
      method: 'GET',
      url: `${API_BASE}/api/asi/status`,
      status: null,
      statusText: 'Not tested',
      responseTime: null,
      response: null,
      timestamp: '',
      isLoading: false,
      error: null
    },
    {
      name: 'System Health',
      method: 'GET',
      url: `${API_BASE}/health`,
      status: null,
      statusText: 'Not tested',
      responseTime: null,
      response: null,
      timestamp: '',
      isLoading: false,
      error: null
    },
    {
      name: 'ALBA Metrics',
      method: 'GET',
      url: `${API_BASE}/api/asi/alba/metrics`,
      status: null,
      statusText: 'Not tested',
      responseTime: null,
      response: null,
      timestamp: '',
      isLoading: false,
      error: null
    },
    {
      name: 'System Status',
      method: 'GET',
      url: `${API_BASE}/status`,
      status: null,
      statusText: 'Not tested',
      responseTime: null,
      response: null,
      timestamp: '',
      isLoading: false,
      error: null
    },
    {
      name: 'ASI Health',
      method: 'GET',
      url: `${API_BASE}/api/asi/health`,
      status: null,
      statusText: 'Not tested',
      responseTime: null,
      response: null,
      timestamp: '',
      isLoading: false,
      error: null
    }
  ])

  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null)
  const [services, setServices] = useState<ServiceStatus[]>([])
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [lastRefresh, setLastRefresh] = useState<string>('')
  const [selectedEndpoint, setSelectedEndpoint] = useState<number>(0)

  // Call single endpoint
  const callEndpoint = useCallback(async (index: number) => {
    setEndpoints(prev => prev.map((ep, i) => 
      i === index ? { ...ep, isLoading: true, error: null } : ep
    ))

    const endpoint = endpoints[index]
    const startTime = performance.now()

    try {
      const response = await fetch(endpoint.url, {
        method: endpoint.method,
        headers: {
          'Accept': 'application/json',
        },
        signal: AbortSignal.timeout(10000)
      })

      const responseTime = Math.round(performance.now() - startTime)
      let data = null
      
      try {
        data = await response.json()
      } catch {
        data = { message: 'Non-JSON response' }
      }

      setEndpoints(prev => prev.map((ep, i) => 
        i === index ? {
          ...ep,
          status: response.status,
          statusText: response.statusText,
          responseTime,
          response: data,
          timestamp: new Date().toISOString(),
          isLoading: false,
          error: null
        } : ep
      ))

      // Update system health if this is the health endpoint
      if (index === 0 && data?.system) {
        setSystemHealth({
          status: data.status,
          cpu_percent: data.system.cpu_percent,
          memory_percent: data.system.memory_percent,
          disk_percent: data.system.disk_percent,
          disk_total: data.system.disk_total,
          disk_used: Math.round(data.system.disk_total * data.system.disk_percent / 100),
          uptime_seconds: data.system.uptime_seconds,
          hostname: data.system.hostname
        })
      }

      // Update services if this is unified status
      if (index === 1 && data?.services) {
        setServices(data.services)
      }

    } catch (err) {
      const responseTime = Math.round(performance.now() - startTime)
      setEndpoints(prev => prev.map((ep, i) => 
        i === index ? {
          ...ep,
          status: 0,
          statusText: 'Error',
          responseTime,
          response: null,
          timestamp: new Date().toISOString(),
          isLoading: false,
          error: err instanceof Error ? err.message : 'Request failed'
        } : ep
      ))
    }
  }, [endpoints])

  // Call all endpoints
  const refreshAll = useCallback(async () => {
    setIsRefreshing(true)
    
    for (let i = 0; i < endpoints.length; i++) {
      await callEndpoint(i)
      // Small delay between requests
      await new Promise(r => setTimeout(r, 100))
    }
    
    setLastRefresh(new Date().toLocaleTimeString())
    setIsRefreshing(false)
  }, [endpoints.length, callEndpoint])

  // Initial load
  useEffect(() => {
    refreshAll()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // Auto refresh every 30 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      refreshAll()
    }, 30000)
    return () => clearInterval(interval)
  }, [refreshAll])

  const getStatusBadge = (status: number | null, error: string | null) => {
    if (error) return <Badge className="bg-red-100 text-red-700">ERROR</Badge>
    if (status === null) return <Badge className="bg-gray-100 text-gray-600">PENDING</Badge>
    if (status >= 200 && status < 300) return <Badge className="bg-green-100 text-green-700">{status} OK</Badge>
    if (status >= 400 && status < 500) return <Badge className="bg-yellow-100 text-yellow-700">{status}</Badge>
    if (status >= 500) return <Badge className="bg-red-100 text-red-700">{status}</Badge>
    return <Badge className="bg-gray-100 text-gray-600">{status}</Badge>
  }

  const formatUptime = (seconds: number) => {
    const days = Math.floor(seconds / 86400)
    const hours = Math.floor((seconds % 86400) / 3600)
    const mins = Math.floor((seconds % 3600) / 60)
    if (days > 0) return `${days}d ${hours}h ${mins}m`
    if (hours > 0) return `${hours}h ${mins}m`
    return `${mins}m`
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
  }

  const selected = endpoints[selectedEndpoint]

  return (
    <div className="min-h-screen bg-[#1e1e1e] text-gray-200 p-6">
      {/* Header - Postman Style */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-3">
            <Database className="h-7 w-7 text-orange-500" />
            Kloud API Collection
          </h1>
          <p className="text-gray-400 mt-1">Real-time API monitoring • No mock data</p>
        </div>
        <div className="flex items-center gap-4">
          {lastRefresh && (
            <span className="text-sm text-gray-500">
              Last refresh: {lastRefresh}
            </span>
          )}
          <Button 
            onClick={refreshAll}
            disabled={isRefreshing}
            className="bg-orange-600 hover:bg-orange-700 text-white"
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
            {isRefreshing ? 'Refreshing...' : 'Run All'}
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-12 gap-6">
        {/* Left Sidebar - Endpoint List */}
        <div className="col-span-4 space-y-2">
          <Card className="bg-[#252526] border-[#3c3c3c]">
            <CardHeader className="pb-2 border-b border-[#3c3c3c]">
              <CardTitle className="text-sm font-medium text-gray-300 flex items-center gap-2">
                <Server className="h-4 w-4" />
                API Endpoints ({endpoints.length})
              </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              {endpoints.map((endpoint, index) => (
                <div
                  key={index}
                  onClick={() => setSelectedEndpoint(index)}
                  className={`p-3 border-b border-[#3c3c3c] cursor-pointer transition-colors ${
                    selectedEndpoint === index 
                      ? 'bg-[#094771] border-l-2 border-l-orange-500' 
                      : 'hover:bg-[#2a2d2e]'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Badge className={`text-xs font-mono ${
                        endpoint.method === 'GET' ? 'bg-green-900 text-green-300' :
                        endpoint.method === 'POST' ? 'bg-yellow-900 text-yellow-300' :
                        'bg-slate-900 text-violet-300'
                      }`}>
                        {endpoint.method}
                      </Badge>
                      <span className="text-sm font-medium text-gray-200">{endpoint.name}</span>
                    </div>
                    {endpoint.isLoading ? (
                      <RefreshCw className="h-3 w-3 animate-spin text-orange-500" />
                    ) : (
                      getStatusBadge(endpoint.status, endpoint.error)
                    )}
                  </div>
                  <div className="mt-1 flex items-center gap-3 text-xs text-gray-500">
                    {endpoint.responseTime !== null && (
                      <span className="flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {endpoint.responseTime}ms
                      </span>
                    )}
                    {endpoint.timestamp && (
                      <span>{new Date(endpoint.timestamp).toLocaleTimeString()}</span>
                    )}
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* System Metrics from Real Data */}
          {systemHealth && (
            <Card className="bg-[#252526] border-[#3c3c3c]">
              <CardHeader className="pb-2 border-b border-[#3c3c3c]">
                <CardTitle className="text-sm font-medium text-gray-300 flex items-center gap-2">
                  <HardDrive className="h-4 w-4" />
                  System Metrics (Real)
                </CardTitle>
              </CardHeader>
              <CardContent className="p-4 space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-400">Status</span>
                  <Badge className={systemHealth.status === 'operational' ? 'bg-green-900 text-green-300' : 'bg-yellow-900 text-yellow-300'}>
                    {systemHealth.status}
                  </Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-400">CPU</span>
                  <span className="text-sm font-mono text-white">{systemHealth.cpu_percent.toFixed(1)}%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-400">Memory</span>
                  <span className="text-sm font-mono text-white">{systemHealth.memory_percent.toFixed(1)}%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-400">Disk</span>
                  <span className="text-sm font-mono text-white">{systemHealth.disk_percent.toFixed(1)}%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-400">Uptime</span>
                  <span className="text-sm font-mono text-white">{formatUptime(systemHealth.uptime_seconds)}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-400">Host</span>
                  <span className="text-sm font-mono text-gray-300">{systemHealth.hostname}</span>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Services Status */}
          {services.length > 0 && (
            <Card className="bg-[#252526] border-[#3c3c3c]">
              <CardHeader className="pb-2 border-b border-[#3c3c3c]">
                <CardTitle className="text-sm font-medium text-gray-300 flex items-center gap-2">
                  <Network className="h-4 w-4" />
                  Services ({services.length})
                </CardTitle>
              </CardHeader>
              <CardContent className="p-4 space-y-2">
                {services.map((service, i) => (
                  <div key={i} className="flex justify-between items-center py-1">
                    <div className="flex items-center gap-2">
                      {service.healthy ? (
                        <CheckCircle className="h-3 w-3 text-green-500" />
                      ) : (
                        <AlertCircle className="h-3 w-3 text-red-500" />
                      )}
                      <span className="text-sm text-gray-300">{service.name}</span>
                    </div>
                    <span className="text-xs font-mono text-gray-500">{service.latency_ms.toFixed(0)}ms</span>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}
        </div>

        {/* Right Panel - Request/Response Details */}
        <div className="col-span-8">
          <Card className="bg-[#252526] border-[#3c3c3c] h-full">
            {/* Request URL Bar */}
            <div className="p-4 border-b border-[#3c3c3c] flex items-center gap-3">
              <Badge className={`font-mono ${
                selected.method === 'GET' ? 'bg-green-900 text-green-300' :
                selected.method === 'POST' ? 'bg-yellow-900 text-yellow-300' :
                'bg-slate-900 text-violet-300'
              }`}>
                {selected.method}
              </Badge>
              <div className="flex-1 bg-[#1e1e1e] rounded px-3 py-2 font-mono text-sm text-gray-300 flex items-center justify-between">
                <span className="truncate">{selected.url}</span>
                <div className="flex items-center gap-2 ml-2">
                  <button 
                    onClick={() => copyToClipboard(selected.url)}
                    className="text-gray-500 hover:text-white"
                  >
                    <Copy className="h-4 w-4" />
                  </button>
                  <a 
                    href={selected.url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-gray-500 hover:text-white"
                  >
                    <ExternalLink className="h-4 w-4" />
                  </a>
                </div>
              </div>
              <Button 
                onClick={() => callEndpoint(selectedEndpoint)}
                disabled={selected.isLoading}
                className="bg-violet-600 hover:bg-violet-700"
              >
                {selected.isLoading ? (
                  <RefreshCw className="h-4 w-4 animate-spin" />
                ) : (
                  <Send className="h-4 w-4" />
                )}
                <span className="ml-2">Send</span>
              </Button>
            </div>

            {/* Response Info Bar */}
            <div className="px-4 py-2 border-b border-[#3c3c3c] bg-[#2d2d2d] flex items-center gap-6 text-sm">
              <div className="flex items-center gap-2">
                <span className="text-gray-500">Status:</span>
                <span className={`font-mono ${
                  selected.status && selected.status >= 200 && selected.status < 300 
                    ? 'text-green-400' 
                    : selected.status 
                      ? 'text-red-400' 
                      : 'text-gray-500'
                }`}>
                  {selected.error ? 'Error' : selected.status || '---'} {selected.statusText}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-gray-500">Time:</span>
                <span className="font-mono text-gray-300">
                  {selected.responseTime !== null ? `${selected.responseTime}ms` : '---'}
                </span>
              </div>
              {selected.timestamp && (
                <div className="flex items-center gap-2">
                  <Clock className="h-3 w-3 text-gray-500" />
                  <span className="text-gray-400">
                    {new Date(selected.timestamp).toLocaleTimeString()}
                  </span>
                </div>
              )}
            </div>

            {/* Response Body */}
            <div className="p-4">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-medium text-gray-400">Response Body</h3>
                {typeof selected.response !== 'undefined' && selected.response !== null && (
                  <button 
                    onClick={() => copyToClipboard(JSON.stringify(selected.response, null, 2))}
                    className="text-xs text-gray-500 hover:text-white flex items-center gap-1"
                  >
                    <Copy className="h-3 w-3" />
                    Copy
                  </button>
                )}
              </div>
              
              <div className="bg-[#1e1e1e] rounded-lg p-4 font-mono text-sm overflow-auto max-h-[500px]">
                {selected.error ? (
                  <div className="text-red-400">
                    <AlertTriangle className="h-4 w-4 inline mr-2" />
                    {selected.error}
                  </div>
                ) : selected.response ? (
                  <pre className="text-gray-300 whitespace-pre-wrap">
                    {JSON.stringify(selected.response, null, 2)}
                  </pre>
                ) : (
                  <div className="text-gray-500 flex items-center gap-2">
                    <Play className="h-4 w-4" />
                    Click &quot;Send&quot; to execute request
                  </div>
                )}
              </div>
            </div>
          </Card>
        </div>
      </div>

      {/* Bottom Stats Bar */}
      <div className="mt-6 grid grid-cols-4 gap-4">
        <Card className="bg-[#252526] border-[#3c3c3c] p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-gray-500 uppercase">Total Endpoints</p>
              <p className="text-2xl font-bold text-white">{endpoints.length}</p>
            </div>
            <Server className="h-8 w-8 text-violet-500 opacity-50" />
          </div>
        </Card>
        
        <Card className="bg-[#252526] border-[#3c3c3c] p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-gray-500 uppercase">Healthy</p>
              <p className="text-2xl font-bold text-green-400">
                {endpoints.filter(e => e.status && e.status >= 200 && e.status < 300).length}
              </p>
            </div>
            <CheckCircle className="h-8 w-8 text-green-500 opacity-50" />
          </div>
        </Card>
        
        <Card className="bg-[#252526] border-[#3c3c3c] p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-gray-500 uppercase">Errors</p>
              <p className="text-2xl font-bold text-red-400">
                {endpoints.filter(e => e.error || (e.status && e.status >= 400)).length}
              </p>
            </div>
            <AlertCircle className="h-8 w-8 text-red-500 opacity-50" />
          </div>
        </Card>
        
        <Card className="bg-[#252526] border-[#3c3c3c] p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-gray-500 uppercase">Avg Response</p>
              <p className="text-2xl font-bold text-orange-400">
                {endpoints.filter(e => e.responseTime).length > 0
                  ? Math.round(
                      endpoints
                        .filter(e => e.responseTime)
                        .reduce((sum, e) => sum + (e.responseTime || 0), 0) /
                      endpoints.filter(e => e.responseTime).length
                    )
                  : 0}
                <span className="text-sm font-normal text-gray-500">ms</span>
              </p>
            </div>
            <Zap className="h-8 w-8 text-orange-500 opacity-50" />
          </div>
        </Card>
      </div>
    </div>
  )
}










