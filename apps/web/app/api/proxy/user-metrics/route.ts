import { NextRequest, NextResponse } from 'next/server'

const API_URL = process.env.NODE_ENV === 'production' 
  ? 'http://kloud-api:8000' 
  : 'http://127.0.0.1:8000';

export async function GET(request: NextRequest) {
  try {
    const userId = request.headers.get('X-User-ID') || 'demo-user'
    
    const response = await fetch(`${API_URL}/api/user/metrics`, {
      cache: 'no-store',
      headers: { 
        'Accept': 'application/json',
        'X-User-ID': userId
      }
    })
    
    if (!response.ok) {
      return NextResponse.json({ metrics: [] }, { status: 200 })
    }
    
    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('User metrics fetch error:', error)
    return NextResponse.json({ metrics: [] }, { status: 200 })
  }
}

export async function POST(request: NextRequest) {
  try {
    const userId = request.headers.get('X-User-ID') || 'demo-user'
    const body = await request.json()
    
    const response = await fetch(`${API_URL}/api/user/metrics`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-User-ID': userId
      },
      body: JSON.stringify(body)
    })
    
    const data = await response.json()
    return NextResponse.json(data, { status: response.status })
  } catch (error) {
    console.error('User metric create error:', error)
    return NextResponse.json({ error: 'Failed to create metric' }, { status: 500 })
  }
}

