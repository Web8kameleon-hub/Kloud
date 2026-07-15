'use client'

import { useEffect, useMemo, useState } from 'react'

type HealthModule = {
  name: string
  status: string
  lastCheck?: string
  calibration?: string
  polyphony?: number
}

type HealthMetrics = {
  cpu?: string
  memory?: string
  requests?: number
  errors?: number
  auditEvents?: number
  calibrationEvents?: number
  polyphony?: number
  latencyMs?: number
  throughput?: string
}

type HealthLogEvent = {
  event: string
  timestamp: number
  message?: string
}

type BackendHealthResponse = {
  success: boolean
  health: {
    timestamp: number
    status: string
    uptime?: string
    modules?: HealthModule[]
    metrics?: HealthMetrics
    log?: HealthLogEvent[]
  }
}

function statusToTone(status?: string) {
  const s = (status || '').toLowerCase()
  if (s === 'healthy') return { label: 'Healthy', tone: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30' }
  if (s === 'warning') return { label: 'Warning', tone: 'bg-amber-500/15 text-amber-200 border-amber-500/30' }
  if (s === 'down') return { label: 'Down', tone: 'bg-rose-500/15 text-rose-200 border-rose-500/30' }
  return { label: 'Unknown', tone: 'bg-slate-500/15 text-slate-200 border-slate-500/30' }
}

export default function LiveServicesPanel() {
  const [data, setData] = useState<BackendHealthResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const status = data?.health?.status
  const tone = useMemo(() => statusToTone(status), [status])

  useEffect(() => {
    let alive = true

    async function poll() {
      try {
        setError(null)
        const res = await fetch('/api/backend-health', { cache: 'no-store' })
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        const json = (await res.json()) as BackendHealthResponse
        if (!alive) return
        setData(json)
      } catch (e: any) {
        if (!alive) return
        setError(e?.message || 'Failed to fetch health')
      } finally {
        if (!alive) return
        setLoading(false)
      }
    }

    poll()
    const interval = setInterval(poll, 4000)

    return () => {
      alive = false
      clearInterval(interval)
    }
  }, [])

  const modules = data?.health?.modules ?? []
  const metrics = data?.health?.metrics ?? {}
  const log = data?.health?.log ?? []

  const lastLogs = log.slice(0, 4)

  return (
    <section id="live" className="mt-6">
      <div className="rounded-2xl border border-white/10 bg-white/5 backdrop-blur px-5 py-5 md:px-6 md:py-6">
        <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
          <div>
            <h2 className="text-xl md:text-2xl font-bold">Live Services (Real-time)</h2>
            <p className="text-sm text-white/70 mt-1">
              Updating automatically from <span className="text-white/90">/api/backend-health</span>
            </p>
          </div>

          <div className="flex items-center gap-3">
            <div className={`rounded-xl border px-3 py-2 text-sm font-semibold ${tone.tone}`}>
              {loading ? 'Updating…' : tone.label}
            </div>

            <div className="text-sm text-white/60">
              {data?.health?.uptime ? `Uptime: ${data.health.uptime}` : '—'}
            </div>
          </div>
        </div>

        {/* Metrics */}
        <div className="mt-5 grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div className="rounded-xl border border-white/10 bg-black/10 p-4">
            <div className="text-xs text-white/60">Latency</div>
            <div className="mt-1 text-lg font-bold">{metrics.latencyMs ?? '—'} ms</div>
          </div>
          <div className="rounded-xl border border-white/10 bg-black/10 p-4">
            <div className="text-xs text-white/60">CPU</div>
            <div className="mt-1 text-lg font-bold">{metrics.cpu ?? '—'}</div>
          </div>
          <div className="rounded-xl border border-white/10 bg-black/10 p-4">
            <div className="text-xs text-white/60">Memory</div>
            <div className="mt-1 text-lg font-bold">{metrics.memory ?? '—'}</div>
          </div>
          <div className="rounded-xl border border-white/10 bg-black/10 p-4">
            <div className="text-xs text-white/60">Requests / Errors</div>
            <div className="mt-1 text-lg font-bold">
              {(metrics.requests ?? '—').toString()} / {(metrics.errors ?? '—').toString()}
            </div>
          </div>
        </div>

        {/* Modules + Log */}
        <div className="mt-5 grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div className="lg:col-span-2">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold">Modules</h3>
              <div className="text-sm text-white/60">{modules.length ? `${modules.length} active` : '—'}</div>
            </div>

            <div className="mt-3 grid grid-cols-1 sm:grid-cols-2 gap-3">
              {modules.map((m) => {
                const mStatus = (m.status || '').toLowerCase()
                const tone2 =
                  mStatus === 'active'
                    ? 'border-emerald-500/30 bg-emerald-500/10 text-emerald-200'
                    : 'border-white/10 bg-white/5 text-white/80'

                return (
                  <div
                    key={m.name}
                    className={`rounded-xl border px-4 py-3 ${tone2}`}
                  >
                    <div className="font-bold">{m.name}</div>
                    <div className="mt-1 text-xs text-white/70">
                      Status: {m.status || '—'}
                      {typeof m.polyphony === 'number' ? ` • Polyphony: ${m.polyphony}` : ''}
                    </div>
                    {m.lastCheck ? (
                      <div className="mt-2 text-[11px] text-white/50">
                        Last check: {new Date(m.lastCheck).toLocaleString()}
                      </div>
                    ) : null}
                  </div>
                )
              })}
            </div>
          </div>

          <div>
            <h3 className="font-semibold">Latest log</h3>
            {error ? (
              <div className="mt-3 rounded-xl border border-rose-500/30 bg-rose-500/10 p-4 text-rose-200 text-sm">
                {error}
              </div>
            ) : null}

            <div className="mt-3 space-y-2">
              {lastLogs.length ? (
                lastLogs.map((e, idx) => (
                  <div
                    key={`${e.event}-${idx}`}
                    className="rounded-xl border border-white/10 bg-white/5 p-3"
                  >
                    <div className="text-xs text-white/60">{e.event}</div>
                    <div className="text-sm text-white/85 mt-1">{e.message ?? '—'}</div>
                    <div className="text-[11px] text-white/50 mt-2">
                      {new Date(e.timestamp).toLocaleString()}
                    </div>
                  </div>
                ))
              ) : (
                <div className="mt-3 text-sm text-white/60">Updating…</div>
              )}
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
