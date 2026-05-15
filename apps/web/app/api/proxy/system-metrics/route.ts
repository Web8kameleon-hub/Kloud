import { NextResponse } from 'next/server'

// Use Docker container name in kloud-secure network
const API_URL = process.env.NODE_ENV === 'production' ? 'http://kloud-api:8000' : 'http://127.0.0.1:8000';

export async function GET() {
  try {
    const response = await fetch(`${API_URL}/api/mymirror/live-metrics`, {
      cache: 'no-store',
      headers: { 'Accept': 'application/json' }
    })
    
    if (!response.ok) {
      return NextResponse.json({ cpu_percent: 0, memory_percent: 0, disk_percent: 0 }, { status: 200 })
    }
    
    const data = await response.json()
    const system = data?.system || {}

    return NextResponse.json({
      cpu_percent: Number(system.cpu || 0),
      memory_percent: Number(system.memory || 0),
      disk_percent: Number(system.disk || 0),
      uptime: data.uptime || '0h',
      hostname: data.hostname || 'unknown'
    })
  } catch (error) {
    console.error('System metrics fetch error:', error)
    return NextResponse.json({ cpu_percent: 0, memory_percent: 0, disk_percent: 0 }, { status: 200 })
  }
}

