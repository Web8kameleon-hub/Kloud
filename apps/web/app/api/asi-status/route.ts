import { NextResponse } from 'next/server'

// PRODUCTION: Hetzner server IP / kloud.com
// DEVELOPMENT: Use localhost for local backend
const isDev = process.env.NODE_ENV === 'development'
const HETZNER_API = process.env.API_URL || (isDev ? 'http://localhost:8000' : 'http://kloud-api:8000')
const API_BASE = process.env.API_INTERNAL_URL || process.env.NEXT_PUBLIC_API_BASE || HETZNER_API

// Suppress repetitive error logging
let lastErrorTime = 0
const ERROR_LOG_INTERVAL = 30000 // 30 seconds

export async function GET() {
  try {
    // Backend uses /asi/status NOT /api/asi-status
    const upstream = await fetch(`${API_BASE}/asi/status`, {
      headers: { Accept: 'application/json' },
      cache: 'no-store',
    })

    if (!upstream.ok) {
      throw new Error(`Upstream responded with ${upstream.status}`)
    }

    const payload = await upstream.json()
    return NextResponse.json({ success: true, asi_status: payload.trinity ? payload : { trinity: payload } })
  } catch (error) {
    // Only log errors every 30 seconds to prevent spam
    const now = Date.now()
    if (now - lastErrorTime > ERROR_LOG_INTERVAL) {
      console.warn('[asi-status] Backend not available:', (error as Error).message)
      lastErrorTime = now
    }

    // NO MOCK DATA - Return real error status
    return NextResponse.json({
      success: false,
      error: 'Backend unavailable',
      message: (error as Error).message,
      timestamp: new Date().toISOString(),
      asi_status: null
    }, { status: 503 })
  }
}

