import { NextResponse } from 'next/server'

// Use Docker container name in kloud-secure network
const API_URL = process.env.NODE_ENV === 'production' ? 'http://kloud-api:8000' : 'http://127.0.0.1:8000';

export async function GET() {
  try {
    // Use /api/system-status which has the real metrics
    const response = await fetch(`${API_URL}/api/system-status`, {
      cache: 'no-store',
      headers: { 'Accept': 'application/json' }
    })
    
    if (!response.ok) {
      return NextResponse.json({ cpu_percent: 0, memory_percent: 0, disk_percent: 0 }, { status: 200 })
    }
    
    const data = await response.json()
    // Extract system metrics from the response
    return NextResponse.json({
      cpu_percent: data.system?.cpu_percent || 0,
      memory_percent: data.system?.memory_percent || 0,
      disk_percent: data.system?.disk_percent || 0,
      uptime: data.uptime || '0h',
      hostname: data.system?.hostname || 'unknown'
    })
  } catch (error) {
    console.error('System metrics fetch error:', error)
    return NextResponse.json({ cpu_percent: 0, memory_percent: 0, disk_percent: 0 }, { status: 200 })
  }
}

