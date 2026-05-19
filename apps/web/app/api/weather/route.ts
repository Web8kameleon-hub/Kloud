import { NextResponse } from 'next/server'

export async function GET() {
  try {
    const upstream = await fetch(`http://api:8000/api/weather`, {
      headers: { Accept: 'application/json' },
      cache: 'no-store',
    })

    if (!upstream.ok) {
      throw new Error(`Upstream responded with ${upstream.status}`)
    }

    const payload = await upstream.json()
    return NextResponse.json({ success: true, data: payload })
  } catch (error) {
    console.error('[weather] upstream error:', error)
    return NextResponse.json(
      {
        error: 'Weather service unavailable',
        source: 'upstream',
      },
      { status: 502 },
    )
  }
}
