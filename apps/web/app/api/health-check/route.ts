import { NextResponse } from 'next/server'

export const dynamic = 'force-dynamic'
export const revalidate = 0

interface ServiceHealth {
  name: string
  status: 'operational' | 'degraded' | 'outage'
  latency: number
  port: number
}

// Service configuration for Docker environment - ALL use container names
// Only include services that are actually deployed
const SERVICES = [
  { name: 'Main API', host: 'kloud-api', port: 8000, path: '/health' },
  { name: 'Core-A (Analytics)', host: 'kloud-alba', port: 5555, path: '/health' },
  { name: 'Core-B (Creative)', host: 'kloud-albi', port: 6680, path: '/health' },
  { name: 'Frontend', host: 'kloud-web', port: 3000, path: '/api/ping' },
]

async function checkService(name: string, host: string, port: number, path = '/health'): Promise<ServiceHealth> {
  const start = Date.now()
  const url = `http://${host}:${port}${path}`
  try {
    const res = await fetch(url, {
      cache: 'no-store',
      signal: AbortSignal.timeout(3000)
    })
    const latency = Date.now() - start
    if (res.ok) {
      return { name, status: 'operational', latency, port }
    }
    return { name, status: 'degraded', latency, port }
  } catch {
    return { name, status: 'outage', latency: Date.now() - start, port }
  }
}

export async function GET() {
  const checks = await Promise.all(
    SERVICES.map(s => checkService(s.name, s.host, s.port, s.path))
  )

  const operational = checks.filter(s => s.status === 'operational').length
  const overall = operational === checks.length ? 'ALL_OPERATIONAL'
    : operational > checks.length / 2 ? 'PARTIAL_OUTAGE' : 'MAJOR_OUTAGE'

  return NextResponse.json({
    timestamp: new Date().toISOString(),
    overall,
    operational_count: operational,
    total_services: checks.length,
    services: checks
  }, {
    headers: { 'Cache-Control': 'no-cache, no-store' }
  })
}

