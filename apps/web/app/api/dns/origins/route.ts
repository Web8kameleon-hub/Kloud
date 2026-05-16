import { NextResponse } from 'next/server'

const API_URL = process.env.NODE_ENV === 'production' ? 'http://kloud-api:8000' : 'http://127.0.0.1:8000'
const CLOUDFLARE_API = 'https://api.cloudflare.com/client/v4'
const CF_TOKEN = process.env.CLOUDFLARE_API_TOKEN
const CF_ACCOUNT_ID = process.env.CLOUDFLARE_ACCOUNT_ID

function jsonError(message: string, status = 502) {
  return NextResponse.json({ error: message }, { status })
}

function endpointToAddress(endpoint: string): string {
  try {
    const u = new URL(endpoint)
    return u.hostname
  } catch {
    return endpoint
  }
}

export async function GET() {
  // 1) Prefer internal product API if available
  try {
    const response = await fetch(`${API_URL}/api/dns/origins`, {
      cache: 'no-store',
      headers: { Accept: 'application/json' },
    })

    if (response.ok) {
      const data = await response.json()
      if (Array.isArray(data)) {
        return NextResponse.json(data, { status: 200 })
      }
    }
  } catch {
    // fallback handled below
  }

  // 2) Cloudflare Load Balancer Pools mode
  if (!CF_TOKEN || !CF_ACCOUNT_ID) {
    return jsonError('Origins provider not configured. Set CLOUDFLARE_API_TOKEN and CLOUDFLARE_ACCOUNT_ID or enable backend /api/dns service.', 503)
  }

  try {
    const poolsRes = await fetch(`${CLOUDFLARE_API}/accounts/${CF_ACCOUNT_ID}/load_balancers/pools`, {
      cache: 'no-store',
      headers: {
        Authorization: `Bearer ${CF_TOKEN}`,
        'Content-Type': 'application/json',
      },
    })

    if (!poolsRes.ok) {
      return jsonError(`Cloudflare pools request failed (${poolsRes.status})`)
    }

    const poolsPayload = await poolsRes.json()
    const pools = Array.isArray(poolsPayload?.result) ? poolsPayload.result : []

    const origins = pools.flatMap((pool: any) =>
      (pool.origins || []).map((origin: any, idx: number) => ({
        id: `${pool.id}-${idx}`,
        name: origin.name || `${pool.name}-origin-${idx + 1}`,
        endpoint: `http://${origin.address}`,
        health_status: origin.enabled === false ? 'Disabled' : 'Healthy',
        region: 'global',
        role: pool.name || 'load-balancer-pool',
      })),
    )

    return NextResponse.json(origins, { status: 200 })
  } catch (error) {
    console.error('DNS origins provider error:', error)
    return jsonError('Failed to retrieve hosting origins from configured providers.')
  }
}

export async function POST(request: Request) {
  const payload = await request.json().catch(() => ({}))

  // 1) Prefer internal product API if available
  try {
    const response = await fetch(`${API_URL}/api/dns/origins`, {
      method: 'POST',
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    })

    if (!response.ok) {
      throw new Error(`Failed with status ${response.status}`)
    }

    const data = await response.json()
    return NextResponse.json(data, { status: 201 })
  } catch {
    // fallback handled below
  }

  // 2) Cloudflare pool create mode
  if (!CF_TOKEN || !CF_ACCOUNT_ID) {
    return jsonError('Origin creation provider not configured. Set CLOUDFLARE_API_TOKEN and CLOUDFLARE_ACCOUNT_ID or enable backend /api/dns service.', 503)
  }

  try {
    const address = endpointToAddress(payload?.endpoint || '')
    if (!address) {
      return jsonError('endpoint is required for origin deployment', 400)
    }

    const createRes = await fetch(`${CLOUDFLARE_API}/accounts/${CF_ACCOUNT_ID}/load_balancers/pools`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${CF_TOKEN}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        name: payload?.name || `origin-${Date.now()}`,
        origins: [
          {
            name: payload?.name || 'origin',
            address,
            enabled: payload?.health_status !== 'Disabled',
          },
        ],
        description: payload?.role || 'kloud-origin',
        enabled: true,
      }),
    })

    if (!createRes.ok) {
      return jsonError(`Cloudflare origin deploy failed (${createRes.status})`)
    }

    const created = await createRes.json()
    const pool = created?.result
    return NextResponse.json(
      {
        id: pool?.id,
        name: payload?.name || 'origin',
        endpoint: payload?.endpoint,
        health_status: payload?.health_status || 'Healthy',
        region: payload?.region || 'global',
        role: payload?.role || 'load-balancer-pool',
      },
      { status: 201 },
    )
  } catch (error) {
    console.error('DNS origin create provider error:', error)
    return jsonError('Failed to deploy hosting origin to configured providers.')
  }
}
