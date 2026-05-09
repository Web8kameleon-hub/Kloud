import { NextResponse } from 'next/server';

// Internal API URL - use localhost in dev, Docker container name in production
const isDev = process.env.NODE_ENV === 'development';
const API_INTERNAL = process.env.API_INTERNAL_URL || (isDev ? 'http://localhost:8000' : 'http://kloud-api:8000');

export async function GET() {
  try {
    const response = await fetch(`${API_INTERNAL}/health`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
      signal: AbortSignal.timeout(5000),
    });
    
    if (!response.ok) {
      return NextResponse.json(
        { error: 'API returned non-200 status', status: response.status },
        { status: response.status }
      );
    }
    
    const data = await response.json();
    return NextResponse.json(data, { status: 200 });
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to connect to Main API', details: String(error) },
      { status: 503 }
    );
  }
}

