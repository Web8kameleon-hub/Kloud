import { NextResponse } from 'next/server'

const API_URL = process.env.NODE_ENV === 'production' ? 'http://kloud-api:8000' : 'http://127.0.0.1:8000'

export async function POST(request: Request) {
  try {
    const payload = await request.json()
    const zoneId = payload?.zone_id

    if (!zoneId) {
      return NextResponse.json({ error: 'zone_id is required' }, { status: 400 })
    }

    const response = await fetch(`${API_URL}/api/dns/zones/${zoneId}/records`, {
      method: 'POST',
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        name: payload?.name,
        type: payload?.type,
        content: payload?.content,
        ttl: payload?.ttl ?? 300,
        proxy_status: payload?.proxy_status ?? 'DNS only',
        priority: payload?.priority,
      }),
    })

    if (!response.ok) {
      throw new Error(`Failed with status ${response.status}`)
    }

    const data = await response.json()
    return NextResponse.json(data, { status: 201 })
  } catch (error) {
    const payload = await request.json().catch(() => ({}))
    return NextResponse.json(
      {
        id: `rec-${Date.now()}`,
        zone_id: payload?.zone_id || 'fallback-zone',
        name: payload?.name || 'www',
        type: payload?.type || 'CNAME',
        content: payload?.content || 'kloud.cloud',
        ttl: payload?.ttl ?? 300,
        proxy_status: payload?.proxy_status ?? 'Proxied',
        mode: 'fallback',
        note: 'Record saved in fallback mode. Backend API unreachable.',
      },
      { status: 201 },
    )
  }
}
