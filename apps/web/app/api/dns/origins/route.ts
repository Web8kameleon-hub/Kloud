import { NextResponse } from 'next/server'

const API_URL = process.env.NODE_ENV === 'production' ? 'http://kloud-api:8000' : 'http://127.0.0.1:8000'

export async function GET() {
  try {
    const response = await fetch(`${API_URL}/api/dns/origins`, {
      cache: 'no-store',
      headers: { Accept: 'application/json' },
    })

    if (!response.ok) {
      return NextResponse.json([], { status: 200 })
    }

    const data = await response.json()
    return NextResponse.json(Array.isArray(data) ? data : [], { status: 200 })
  } catch (error) {
    console.error('DNS origins fetch error:', error)
    return NextResponse.json([], { status: 200 })
  }
}
