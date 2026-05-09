import { NextRequest, NextResponse } from 'next/server'

export const dynamic = 'force-dynamic'
export const revalidate = 0

const KLOUD_MESH_API = process.env.KLOUD_MESH_API || 'https://kloud.aiagi.io'

function validateCronAuth(req: NextRequest): boolean {
  const required = process.env.MESH_ANNOUNCE_TOKEN
  if (!required) {
    return true
  }
  const provided = req.headers.get('authorization')?.replace(/^Bearer\s+/i, '') || ''
  return provided === required
}

async function loadLocalHealth(baseUrl: string) {
  const resp = await fetch(`${baseUrl}/api/health-check`, {
    cache: 'no-store',
    signal: AbortSignal.timeout(3000),
  })

  if (!resp.ok) {
    throw new Error(`health-check failed: ${resp.status} ${resp.statusText}`)
  }

  return resp.json()
}

export async function GET(req: NextRequest) {
  if (!validateCronAuth(req)) {
    return NextResponse.json({ ok: false, error: 'unauthorized' }, { status: 401 })
  }

  const host = req.headers.get('x-forwarded-host') || req.headers.get('host') || 'www.clisonix.com'
  const proto = req.headers.get('x-forwarded-proto') || 'https'
  const baseUrl = `${proto}://${host}`

  try {
    const health = await loadLocalHealth(baseUrl)

    const payload = {
      project: host,
      channel: 'wwwmmm',
      stigma_level: health.overall === 'ALL_OPERATIONAL' ? 1 : health.overall === 'PARTIAL_OUTAGE' ? 2 : 3,
      note: `overall=${health.overall};operational=${health.operational_count}/${health.total_services}`,
    }

    const signalResp = await fetch(`${KLOUD_MESH_API}/wwwmmm/signal`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      cache: 'no-store',
    })

    if (!signalResp.ok) {
      throw new Error(`wwwmmm signal failed: ${signalResp.status} ${signalResp.statusText}`)
    }

    const signalResult = await signalResp.json()

    return NextResponse.json({
      ok: true,
      host,
      health,
      signal: signalResult,
      timestamp: new Date().toISOString(),
    })
  } catch (error) {
    return NextResponse.json(
      {
        ok: false,
        error: error instanceof Error ? error.message : 'unknown error',
        timestamp: new Date().toISOString(),
      },
      { status: 500 }
    )
  }
}

export async function POST(req: NextRequest) {
  return GET(req)
}
