import { NextResponse } from 'next/server'

export async function GET() {
  try {
    const upstream = await fetch(`http://api:8000/api/crypto/market`, {
      headers: { Accept: 'application/json' },
      cache: 'no-store',
    })

    if (!upstream.ok) {
      throw new Error(`Upstream responded with ${upstream.status}`)
    }

    const payload = await upstream.json()
    return NextResponse.json({ success: true, data: payload })
  } catch (error) {
    console.error('[crypto/market] upstream error:', error)
    return NextResponse.json(
      {
        error: 'Crypto service unavailable',
        source: 'upstream',
      },
      { status: 502 },
    )
  }
}
