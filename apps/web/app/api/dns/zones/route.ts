import { NextResponse } from 'next/server'

const API_URL = process.env.NODE_ENV === 'production' ? 'http://kloud-api:8000' : 'http://127.0.0.1:8000'

const EDGE_SEED_ZONES = [
  {
    id: 'zone-kloud-cloud',
    domain: 'kloud.cloud',
    status: 'active',
    nameserver_1: 'jonathan.ns.kloud.cloud',
    nameserver_2: 'katja.ns.kloud.cloud',
    created_at: new Date().toISOString(),
    records: [
      {
        id: 'rec-root-a',
        name: '@',
        type: 'A',
        content: '91.98.47.131',
        ttl: 300,
        proxy_status: 'Proxied',
      },
      {
        id: 'rec-www-cname',
        name: 'www',
        type: 'CNAME',
        content: 'kloud.cloud',
        ttl: 300,
        proxy_status: 'Proxied',
      },
      {
        id: 'rec-api-a',
        name: 'api',
        type: 'A',
        content: '178.105.52.245',
        ttl: 120,
        proxy_status: 'Proxied',
      },
      {
        id: 'rec-edge-cname',
        name: 'edge',
        type: 'CNAME',
        content: 'edge.kloud.cloud',
        ttl: 120,
        proxy_status: 'DNS only',
      },
    ],
  },
]

export async function GET() {
  try {
    const response = await fetch(`${API_URL}/api/dns/zones`, {
      cache: 'no-store',
      headers: { Accept: 'application/json' },
    })

    if (!response.ok) {
      return NextResponse.json(EDGE_SEED_ZONES, { status: 200 })
    }

    const data = await response.json()
    if (Array.isArray(data) && data.length > 0) {
      return NextResponse.json(data, { status: 200 })
    }

    return NextResponse.json(EDGE_SEED_ZONES, { status: 200 })
  } catch (error) {
    console.error('DNS zones fetch error:', error)
    return NextResponse.json(EDGE_SEED_ZONES, { status: 200 })
  }
}
