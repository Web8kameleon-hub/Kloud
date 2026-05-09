import { NextRequest, NextResponse } from 'next/server'

export const dynamic = 'force-dynamic'
export const revalidate = 0

const KLOUD_MESH_API = process.env.KLOUD_MESH_API || 'https://kloud.aiagi.io'

function hashToId(str: string): number {
  let hash = 5381
  for (let i = 0; i < str.length; i++) {
    hash = ((hash << 5) + hash) + str.charCodeAt(i)
  }
  return Math.abs(hash) % 1000000000
}

async function announce(host: string) {
  const nodeId = hashToId(host)
  const payload = {
    id: nodeId,
    api_addr: `https://${host}/api/mesh/announce`,
    gossip_addr: 'vercel-edge:0',
  }

  const resp = await fetch(`${KLOUD_MESH_API}/peers/announce`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
    cache: 'no-store',
  })

  if (!resp.ok) {
    throw new Error(`announce failed: ${resp.status} ${resp.statusText}`)
  }

  const data = await resp.json()
  return {
    ok: true,
    announced: payload,
    mesh_response: data,
    timestamp: new Date().toISOString(),
  }
}

function validateCronAuth(req: NextRequest): boolean {
  const required = process.env.MESH_ANNOUNCE_TOKEN
  if (!required) {
    return true
  }
  const provided = req.headers.get('authorization')?.replace(/^Bearer\s+/i, '') || ''
  return provided === required
}

export async function GET(req: NextRequest) {
  if (!validateCronAuth(req)) {
    return NextResponse.json({ ok: false, error: 'unauthorized' }, { status: 401 })
  }

  const host = req.headers.get('x-forwarded-host') || req.headers.get('host') || 'vercel-edge'

  try {
    const result = await announce(host)
    return NextResponse.json(result, { status: 200 })
  } catch (error) {
    return NextResponse.json(
      { ok: false, error: error instanceof Error ? error.message : 'unknown error' },
      { status: 500 }
    )
  }
}

export async function POST(req: NextRequest) {
  return GET(req)
}
