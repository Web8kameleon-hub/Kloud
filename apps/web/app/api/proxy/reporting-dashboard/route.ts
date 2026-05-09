import { NextResponse } from 'next/server';

const isDev = process.env.NODE_ENV !== 'production';
const API_INTERNAL = process.env.API_INTERNAL_URL || (isDev ? 'http://localhost:8000' : 'http://kloud-api:8000');

export async function GET() {
  try {
    const response = await fetch(`${API_INTERNAL}/api/reporting/dashboard`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
      signal: AbortSignal.timeout(5000),
    });

    if (!response.ok) {
      return NextResponse.json(
        { error: 'Failed to fetch dashboard data', status: response.status },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data, { status: 200 });
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to connect to reporting service', details: String(error) },
      { status: 503 }
    );
  }
}

