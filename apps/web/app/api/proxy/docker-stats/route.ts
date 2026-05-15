import { NextResponse } from 'next/server'

// Use Docker container name in kloud-secure network
const API_URL = process.env.NODE_ENV === 'production' ? 'http://kloud-api:8000' : 'http://127.0.0.1:8000';

export async function GET() {
  try {
    const response = await fetch(`${API_URL}/api/mymirror/docker-containers`, {
      cache: 'no-store',
      headers: { 'Accept': 'application/json' }
    })
    
    if (!response.ok) {
      return NextResponse.json({ stats: [] }, { status: 200 })
    }
    
    const data = await response.json()
    const containers = Array.isArray(data?.containers) ? data.containers : []

    const stats = containers.map((container: any) => ({
      name: container?.name || 'unknown',
      cpu_percent:
        typeof container?.cpu === 'number' ? `${container.cpu.toFixed(1)}%` : '0%',
      memory_percent:
        typeof container?.memory === 'number'
          ? `${container.memory.toFixed(1)}%`
          : '0%',
      memory_usage: '-',
    }))

    return NextResponse.json({ stats })
  } catch (error) {
    console.error('Docker stats fetch error:', error)
    return NextResponse.json({ stats: [] }, { status: 200 })
  }
}

