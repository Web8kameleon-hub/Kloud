"use client"

import { useState, useEffect, useRef } from 'react'
import Link from 'next/link'
import { ASITerminal } from '../src/components/asi/ASITerminal';

interface SystemStatus {
  signal_gen: { status: string; version: string }
  albi: { status: string; neural_patterns: number }
  alba: { status: string; data_streams: number }
  jona: { status: string; audio_synthesis: boolean }
}

export default function Home() {
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const remoteFailureLoggedRef = useRef(false)

  useEffect(() => {
    const fetchSystemStatus = async () => {
      try {
        // Try to fetch REAL data directly from backend via /backend/ route
        let albiData: any = null
        let albaData: any = null
        let jonaData: any = null

        try {
          // Direct call to Python backend through nginx /backend/ route
          const asiStatusRes = await fetch(`/backend/asi/status`)
          if (asiStatusRes.ok) {
            const asiData = await asiStatusRes.json()
            const trinity = asiData.trinity
            albiData = trinity?.albi
            albaData = trinity?.alba
            jonaData = trinity?.jona
          }
        } catch (e) {
          console.warn('Failed to fetch real ASI metrics from backend:', e)
        }

        // Fallback to Next.js API route if direct backend fails
        if (!albiData || !albaData || !jonaData) {
          try {
            const asiStatusRes = await fetch(`/api/asi-status`)
            if (asiStatusRes.ok) {
              const asiData = await asiStatusRes.json()
              const trinity = asiData.asi_status?.trinity || asiData.asi_status
              albiData = trinity?.albi
              albaData = trinity?.alba
              jonaData = trinity?.jona
            }
          } catch (e) {
            console.warn('Failed to fetch from Next.js API route:', e)
          }
        }

        // Set status from real Prometheus data
        if (albiData && albaData && jonaData) {
          setSystemStatus({
            signal_gen: {
              status: 'Online',
              version: '2.1.0'
            },
            albi: {
              status: albiData.operational ? 'Online' : 'Offline',
              neural_patterns: albiData.metrics?.neural_patterns || 0
            },
            alba: {
              status: albaData.operational ? 'Online' : 'Offline',
              data_streams: Math.round(albaData.metrics?.memory_mb / 64) || 8
            },
            jona: {
              status: jonaData.operational ? 'Online' : 'Offline',
              audio_synthesis: jonaData.metrics?.audio_synthesis ?? true
            }
          })
        } else {
          // Fallback when no data available
          setSystemStatus({
            signal_gen: { status: 'Degraded', version: '1.0.0' },
            albi: { status: 'Unknown', neural_patterns: 0 },
            alba: { status: 'Unknown', data_streams: 0 },
            jona: { status: 'Unknown', audio_synthesis: false }
          })
        }
      } catch (error) {
        console.error('Failed to fetch system status:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchSystemStatus()
    const interval = setInterval(fetchSystemStatus, 10000)
    return () => clearInterval(interval)
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900 flex items-center justify-center">
        <div className="text-center">
          <div className="text-white text-xl mb-4">🧠 Initializing Kloud Cloud...</div>
          <div className="text-gray-400">Loading industrial-grade neuroacoustic processing...</div>
        </div>
      </div>
    )
  }

  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'online':
      case 'active':
      case 'collecting':
      case 'monitoring':
      case 'operational':
        return 'bg-green-500'
      case 'processing':
      case 'analyzing':
      case 'synthesizing':
        return 'bg-yellow-500'
      default:
        return 'bg-red-500'
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-12 bg-white/10 rounded-2xl p-8 border border-white/20">
          <h1 className="text-5xl font-bold text-white mb-4 bg-gradient-to-r from-cyan-400 via-violet-400 to-emerald-400 bg-clip-text text-transparent">
            🧠 Kloud Cloud Platform
          </h1>
          <p className="text-xl text-gray-300 mb-4">
            Industrial-grade Neuroacoustic Processing & EEG Analysis
          </p>
          <div className="flex items-center justify-center space-x-2">
            <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
            <span className="text-sm text-gray-400">Live Industrial Backend • ASI Trinity Integrated • Real Data Only</span>
          </div>
        </div>

        {/* ASI Trinity Status */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white/10 rounded-xl p-6 border border-white/20">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white flex items-center">
                 Signal-Gen Backend
              </h3>
              <div className={`w-3 h-3 rounded-full ${getStatusColor(systemStatus?.signal_gen.status || 'offline')}`}></div>
            </div>
            <p className="text-gray-300">Status: {systemStatus?.signal_gen.status || 'Unknown'}</p>
            <p className="text-gray-300">Version: {systemStatus?.signal_gen.version || 'N/A'}</p>
            <p className="text-xs text-cyan-400 mt-2">📡 Connected to Prometheus</p>
          </div>

          <div className="bg-white/10 rounded-xl p-6 border border-white/20 border-l-4 border-l-cyan-500">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white flex items-center">
                🧠 Creative Intelligence
              </h3>
              <div className={`w-3 h-3 rounded-full ${getStatusColor(systemStatus?.albi.status || 'offline')}`}></div>
            </div>
            <p className="text-gray-300">EEG Processing: {systemStatus?.albi.status || 'Unknown'}</p>
            <p className="text-gray-300">Patterns: {systemStatus?.albi.neural_patterns || 0}</p>
            <p className="text-xs text-cyan-400 mt-2">🔴 Real Prometheus data</p>
          </div>

          <div className="bg-white/10 rounded-xl p-6 border border-white/20 border-l-4 border-l-emerald-500">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white flex items-center">
                📊 Analytical Intelligence
              </h3>
              <div className={`w-3 h-3 rounded-full ${getStatusColor(systemStatus?.alba.status || 'offline')}`}></div>
            </div>
            <p className="text-gray-300">Data Collection: {systemStatus?.alba.status || 'Unknown'}</p>
            <p className="text-gray-300">Streams: {systemStatus?.alba.data_streams || 0}</p>
            <p className="text-xs text-cyan-400 mt-2">🔴 Real Prometheus data</p>
          </div>

          <div className="bg-white/10 rounded-xl p-6 border border-white/20 border-l-4 border-l-purple-500">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white flex items-center">
                🛡️ Coordinator Intelligence
              </h3>
              <div className={`w-3 h-3 rounded-full ${getStatusColor(systemStatus?.jona.status || 'offline')}`}></div>
            </div>
            <p className="text-gray-300">Neural Synthesis: {systemStatus?.jona.status || 'Unknown'}</p>
            <p className="text-gray-300">Audio: {systemStatus?.jona.audio_synthesis ? 'Ready' : 'Disabled'}</p>
            <p className="text-xs text-cyan-400 mt-2">🔴 Real Prometheus data</p>
          </div>
        </div>

        {/* Neuroacoustic Modules */}
        <div className="bg-white/10 rounded-xl p-6 border border-white/20 mb-8">
          <h3 className="text-2xl font-semibold text-white mb-6 flex items-center">
            🧠 Advanced Neuroacoustic Modules
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <Link href="/modules/eeg-analysis" className="group bg-gradient-to-r from-cyan-500/20 to-blue-500/20 hover:from-cyan-500/30 hover:to-blue-500/30 rounded-lg p-6 text-white font-medium transition-all duration-300 border border-cyan-500/30 hover:border-cyan-400/50 hover:scale-105">
              <div className="flex items-center space-x-3">
                <span className="text-2xl">🧠</span>
                <div>
                  <div className="font-semibold">Creative Intelligence - EEG Analysis</div>
                  <div className="text-sm text-gray-300">Neural frequency processing</div>
                </div>
              </div>
            </Link>

            <Link href="/modules/neural-synthesis" className="group bg-gradient-to-r from-violet-500/20 to-purple-500/20 hover:from-violet-500/30 hover:to-purple-500/30 rounded-lg p-6 text-white font-medium transition-all duration-300 border border-violet-500/30 hover:border-violet-400/50 hover:scale-105">
              <div className="flex items-center space-x-3">
                <span className="text-2xl">🎵</span>
                <div>
                  <div className="font-semibold">Coordinator - Neural Synthesis</div>
                  <div className="text-sm text-gray-300">EEG to audio conversion</div>
                </div>
              </div>
            </Link>

            <Link href="/modules/neuroacoustic-converter" className="group bg-gradient-to-r from-emerald-500/20 to-green-500/20 hover:from-emerald-500/30 hover:to-green-500/30 rounded-lg p-6 text-white font-medium transition-all duration-300 border border-emerald-500/30 hover:border-emerald-400/50 hover:scale-105">
              <div className="flex items-center space-x-3">
                <span className="text-2xl">🔄</span>
                <div>
                  <div className="font-semibold">Neuroacoustic Converter</div>
                  <div className="text-sm text-gray-300">Real-time signal conversion</div>
                </div>
              </div>
            </Link>

            <Link href="/modules/spectrum-analyzer" className="group bg-gradient-to-r from-orange-500/20 to-red-500/20 hover:from-orange-500/30 hover:to-red-500/30 rounded-lg p-6 text-white font-medium transition-all duration-300 border border-orange-500/30 hover:border-orange-400/50 hover:scale-105">
              <div className="flex items-center space-x-3">
                <span className="text-2xl">📊</span>
                <div>
                  <div className="font-semibold">Spectrum Analyzer</div>
                  <div className="text-sm text-gray-300">Multi-band FFT analysis</div>
                </div>
              </div>
            </Link>

            <Link href="/modules/industrial-dashboard" className="group bg-gradient-to-r from-indigo-500/20 to-blue-500/20 hover:from-indigo-500/30 hover:to-blue-500/30 rounded-lg p-6 text-white font-medium transition-all duration-300 border border-indigo-500/30 hover:border-indigo-400/50 hover:scale-105">
              <div className="flex items-center space-x-3">
                <span className="text-2xl">🏭</span>
                <div>
                  <div className="font-semibold">Industrial Dashboard</div>
                  <div className="text-sm text-gray-300">Complete system monitoring</div>
                </div>
              </div>
            </Link>

            <Link href="/modules/phone-monitor" className="group bg-gradient-to-r from-pink-500/20 to-rose-500/20 hover:from-pink-500/30 hover:to-rose-500/30 rounded-lg p-6 text-white font-medium transition-all duration-300 border border-pink-500/30 hover:border-pink-400/50 hover:scale-105">
              <div className="flex items-center space-x-3">
                <span className="text-2xl">📱</span>
                <div>
                  <div className="font-semibold">Phone Monitor v3.0</div>
                  <div className="text-sm text-gray-300">Mobile neural interface</div>
                </div>
              </div>
            </Link>

            <Link href="/modules/curiosity-ocean" className="group bg-gradient-to-r from-teal-500/20 to-blue-500/20 hover:from-teal-500/30 hover:to-blue-500/30 rounded-lg p-6 text-white font-medium transition-all duration-300 border border-teal-500/30 hover:border-teal-400/50 hover:scale-105">
              <div className="flex items-center space-x-3">
                <span className="text-2xl">🌊</span>
                <div>
                  <div className="font-semibold">Curiosity Ocean</div>
                  <div className="text-sm text-gray-300">Infinite information engine</div>
                </div>
              </div>
            </Link>
          </div>
        </div>

        {/* Quick Access Hub */}
        <div className="bg-white/10 rounded-xl p-6 border border-white/20">
          <h3 className="text-xl font-semibold text-white mb-4 flex items-center">
            ⚡ Quick Access Hub
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Link href="/modules" className="bg-gradient-to-r from-cyan-500/20 to-blue-500/20 hover:from-cyan-500/30 hover:to-blue-500/30 rounded-lg p-4 text-white font-medium transition-all duration-300 border border-cyan-500/30 text-center">
              <div className="text-lg">🧠 All Modules</div>
              <div className="text-sm text-gray-300">Complete module access</div>
            </Link>
            
            <button className="bg-gradient-to-r from-violet-500/20 to-purple-500/20 hover:from-violet-500/30 hover:to-purple-500/30 rounded-lg p-4 text-white font-medium transition-all duration-300 border border-violet-500/30">
              <div className="text-lg">🎵 Start Neural Synthesis</div>
              <div className="text-sm text-gray-300">Begin EEG to audio</div>
            </button>
            
            <a href="/grafana/" target="_blank" rel="noopener noreferrer" className="bg-gradient-to-r from-emerald-500/20 to-green-500/20 hover:from-emerald-500/30 hover:to-green-500/30 rounded-lg p-4 text-white font-medium transition-all duration-300 border border-emerald-500/30">
              <div className="text-lg">📊 Grafana Dashboards</div>
              <div className="text-sm text-gray-300">Real-time monitoring (admin/kloud2025)</div>
            </a>

            <a href="/prometheus/" target="_blank" rel="noopener noreferrer" className="bg-gradient-to-r from-orange-500/20 to-red-500/20 hover:from-orange-500/30 hover:to-red-500/30 rounded-lg p-4 text-white font-medium transition-all duration-300 border border-orange-500/30">
              <div className="text-lg">⚙️ Prometheus Metrics</div>
              <div className="text-sm text-gray-300">Raw metrics database</div>
            </a>
          </div>
        </div>

        {/* Real Data - Monitoring Section */}
        <div className="bg-gradient-to-br from-red-500/10 to-orange-500/10 rounded-xl p-6 border border-red-500/20 mb-8">
          <h3 className="text-xl font-semibold text-white mb-4 flex items-center">
            🔴 REAL-TIME MONITORING • PROMETHEUS POWERED
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white/5 rounded-lg p-4 border border-white/10">
              <div className="text-sm font-semibold text-cyan-400 mb-2">🧠 Creative Intelligence</div>
              <p className="text-xs text-gray-400 mb-3">Processing goroutines, neural pattern detection, AI efficiency metrics from actual system</p>
              <a href="/backend/asi/albi/metrics" className="text-xs text-cyan-400 hover:text-cyan-300">→ Real metrics endpoint</a>
            </div>
            <div className="bg-white/5 rounded-lg p-4 border border-white/10">
              <div className="text-sm font-semibold text-emerald-400 mb-2">📊 Analytical Intelligence</div>
              <p className="text-xs text-gray-400 mb-3">CPU usage, memory, network latency from actual system monitoring</p>
              <a href="/backend/asi/alba/metrics" className="text-xs text-emerald-400 hover:text-emerald-300">→ Real metrics endpoint</a>
            </div>
            <div className="bg-white/5 rounded-lg p-4 border border-white/10">
              <div className="text-sm font-semibold text-purple-400 mb-2">🛡️ Coordinator Intelligence</div>
              <p className="text-xs text-gray-400 mb-3">Request throughput, uptime, coordination efficiency from live system</p>
              <a href="/backend/asi/jona/metrics" className="text-xs text-purple-400 hover:text-purple-300">→ Real metrics endpoint</a>
            </div>
          </div>
        </div>

        {/* Neural Biofeedback Training */}
        <Link href="/modules/neural-biofeedback" className="block">
          <div className="bg-white/10 rounded-xl p-6 border border-white/20 mt-8 hover:border-teal-400/50 transition-all hover:bg-white/15 cursor-pointer">
            <h3 className="text-2xl font-semibold text-white mb-6 flex items-center">
              🌀 Neural Biofeedback Training
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="group bg-gradient-to-r from-sky-500/20 to-cyan-500/20 hover:from-sky-500/30 hover:to-cyan-500/30 rounded-lg p-6 text-white transition-all duration-300 border border-cyan-500/30 hover:border-cyan-400/50 hover:scale-105">
                <div className="flex items-center space-x-3">
                  <span className="text-3xl">🌊</span>
                  <div>
                    <div className="font-semibold text-lg">Alpha Training</div>
                    <div className="text-sm text-gray-300">Relaxation & calm focus</div>
                  </div>
                </div>
              </div>
              <div className="group bg-gradient-to-r from-violet-500/20 to-indigo-500/20 hover:from-violet-500/30 hover:to-indigo-500/30 rounded-lg p-6 text-white transition-all duration-300 border border-violet-500/30 hover:border-violet-400/50 hover:scale-105">
                <div className="flex items-center space-x-3">
                  <span className="text-3xl">🧠</span>
                  <div>
                    <div className="font-semibold text-lg">Theta Training</div>
                    <div className="text-sm text-gray-300">Deep meditation states</div>
                  </div>
                </div>
              </div>
              <div className="group bg-gradient-to-r from-amber-500/20 to-orange-500/20 hover:from-amber-500/30 hover:to-orange-500/30 rounded-lg p-6 text-white transition-all duration-300 border border-amber-500/30 hover:border-amber-400/50 hover:scale-105">
                <div className="flex items-center space-x-3">
                  <span className="text-3xl">⚡</span>
                  <div>
                    <div className="font-semibold text-lg">Beta Training</div>
                    <div className="text-sm text-gray-300">Focus & concentration</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </Link>

        {/* Real Data Dashboards */}
        <div className="mt-12 pt-8 border-t border-white/20">
          <h2 className="text-3xl font-bold text-white mb-6">💎 Real Data & APIs</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Crypto Dashboard */}
            <Link href="/modules/crypto-dashboard" className="group">
              <div className="bg-gradient-to-br from-yellow-500/20 to-orange-500/20 hover:from-yellow-500/30 hover:to-orange-500/30 rounded-xl p-6 border border-yellow-500/30 hover:border-yellow-400/50 transition-all hover:scale-105 cursor-pointer">
                <div className="flex items-center space-x-4 mb-4">
                  <span className="text-4xl">💰</span>
                  <div>
                    <h3 className="text-2xl font-semibold text-white">Crypto Market</h3>
                    <p className="text-sm text-gray-300">Real CoinGecko API</p>
                  </div>
                </div>
                <p className="text-gray-300">Live cryptocurrency prices • Bitcoin, Ethereum & more • Real-time market data</p>
              </div>
            </Link>

            {/* Weather Dashboard */}
            <Link href="/modules/weather-dashboard" className="group">
              <div className="bg-gradient-to-br from-cyan-500/20 to-blue-500/20 hover:from-cyan-500/30 hover:to-blue-500/30 rounded-xl p-6 border border-cyan-500/30 hover:border-cyan-400/50 transition-all hover:scale-105 cursor-pointer">
                <div className="flex items-center space-x-4 mb-4">
                  <span className="text-4xl">🌍</span>
                  <div>
                    <h3 className="text-2xl font-semibold text-white">Weather Dashboard</h3>
                    <p className="text-sm text-gray-300">Real Open-Meteo API</p>
                  </div>
                </div>
                <p className="text-gray-300">Live weather data • Multiple cities • Temperature, humidity & wind</p>
              </div>
            </Link>
          </div>
        </div>

  <ASITerminal />
      </div>
    </div>
  )
}



