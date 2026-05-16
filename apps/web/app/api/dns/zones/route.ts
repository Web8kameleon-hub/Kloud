import { NextResponse } from 'next/server'

const API_URL = process.env.NODE_ENV === 'production' ? 'http://kloud-api:8000' : 'http://127.0.0.1:8000'
const CLOUDFLARE_API = 'https://api.cloudflare.com/client/v4'
const CF_TOKEN = process.env.CLOUDFLARE_API_TOKEN

function jsonError(message: string, status = 502) {
  return NextResponse.json({ error: message }, { status })
}

export async function GET() {
  // 1) Prefer internal product API if available
  try {
    const response = await fetch(`${API_URL}/api/dns/zones`, {
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

  // 2) Cloudflare provider mode
  if (!CF_TOKEN) {
    return jsonError('DNS provider not configured. Set CLOUDFLARE_API_TOKEN or enable backend /api/dns service.', 503)
  }

  try {
    const zonesRes = await fetch(`${CLOUDFLARE_API}/zones?per_page=50`, {
      cache: 'no-store',
      headers: {
        Authorization: `Bearer ${CF_TOKEN}`,
        'Content-Type': 'application/json',
      },
    })

    if (!zonesRes.ok) {
      return jsonError(`Cloudflare zones request failed (${zonesRes.status})`)
    }

    const zonesPayload = await zonesRes.json()
    const zones = Array.isArray(zonesPayload?.result) ? zonesPayload.result : []

    const mappedZones = await Promise.all(
      zones.map(async (z: any) => {
        let records: any[] = []
        try {
          const recRes = await fetch(`${CLOUDFLARE_API}/zones/${z.id}/dns_records?per_page=100`, {
            cache: 'no-store',
            headers: {
              Authorization: `Bearer ${CF_TOKEN}`,
              'Content-Type': 'application/json',
            },
          })
          if (recRes.ok) {
            const recPayload = await recRes.json()
            records = Array.isArray(recPayload?.result)
              ? recPayload.result.map((r: any) => ({
                  id: r.id,
                  name: r.name,
                  type: r.type,
                  content: r.content,
                  ttl: r.ttl,
                  proxy_status: r.proxied ? 'Proxied' : 'DNS only',
                  priority: r.priority,
                }))
              : []
          }
        } catch {
          records = []
        }

        return {
          id: z.id,
          domain: z.name,
          status: z.status,
          nameserver_1: z.name_servers?.[0] || '',
          nameserver_2: z.name_servers?.[1] || '',
          created_at: z.created_on,
          records,
        }
      }),
    )

    return NextResponse.json(mappedZones, { status: 200 })
  } catch (error) {
    console.error('DNS zones provider error:', error)
    return jsonError('Failed to retrieve DNS zones from configured providers.')
  }
}
