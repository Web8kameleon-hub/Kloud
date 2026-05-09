import { NextRequest, NextResponse } from 'next/server'

const API_URL = process.env.NODE_ENV === 'production' 
  ? 'http://kloud-api:8000' 
  : 'http://127.0.0.1:8000';

export async function GET(request: NextRequest) {
  try {
    const userId = request.headers.get('X-User-ID') || 'demo-user'
    
    const response = await fetch(`${API_URL}/api/user/summary`, {
      cache: 'no-store',
      headers: { 
        'Accept': 'application/json',
        'X-User-ID': userId
      }
    })
    
    if (!response.ok) {
      return NextResponse.json({
        total_sources: 0,
        active_sources: 0,
        total_data_points: 0,
        total_metrics: 0,
        sources_by_type: {}
      }, { status: 200 })
    }
    
    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('User summary fetch error:', error)
    return NextResponse.json({
      total_sources: 0,
      active_sources: 0,
      total_data_points: 0,
      total_metrics: 0,
      sources_by_type: {}
    }, { status: 200 })
  }
}

