import { NextResponse } from 'next/server'

const API_URL = process.env.NODE_ENV === 'production' ? 'http://kloud-api:8000' : 'http://127.0.0.1:8000'

const EDGE_SEED_ORIGINS = [
  {
    id: 'origin-ocean-hq',
    name: 'Ocean HQ API',
    endpoint: 'http://178.105.52.245:8000',
    health_status: 'Healthy',
    region: 'eu-central',
    role: 'api-control',
  },
  {
    id: 'origin-compute-fsk',
    name: 'Compute FSK',
    endpoint: 'http://91.98.47.131:8030',
    health_status: 'Healthy',
    region: 'eu-central',
    role: 'inference-core',
  },
  {
    id: 'origin-failover-nbg',
    name: 'Failover NBG',
    endpoint: 'http://46.224.203.89:8030',
    health_status: 'Warning',
    region: 'eu-central',
    role: 'failover',
  },
]

export async function GET() {
  try {
    const response = await fetch(`${API_URL}/api/dns/origins`, {
      cache: 'no-store',
      headers: { Accept: 'application/json' },
    })

    if (!response.ok) {
      return NextResponse.json(EDGE_SEED_ORIGINS, { status: 200 })
    }

    const data = await response.json()
    if (Array.isArray(data) && data.length > 0) {
      return NextResponse.json(data, { status: 200 })
    }

    return NextResponse.json(EDGE_SEED_ORIGINS, { status: 200 })
  } catch (error) {
    console.error('DNS origins fetch error:', error)
    return NextResponse.json(EDGE_SEED_ORIGINS, { status: 200 })
  }
}
