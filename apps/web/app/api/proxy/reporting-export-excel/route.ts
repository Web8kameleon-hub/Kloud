import { NextResponse } from 'next/server';

const isDev = process.env.NODE_ENV !== 'production';
const API_INTERNAL = process.env.API_INTERNAL_URL || (isDev ? 'http://localhost:8000' : 'http://kloud-api:8000');

// Generate filename with date and time to avoid conflicts
function generateFilename(): string {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, '0');
  const day = String(now.getDate()).padStart(2, '0');
  const hours = String(now.getHours()).padStart(2, '0');
  const minutes = String(now.getMinutes()).padStart(2, '0');
  const seconds = String(now.getSeconds()).padStart(2, '0');
  return `kloud-report-${year}${month}${day}-${hours}${minutes}${seconds}.xlsx`;
}

export async function GET() {
  try {
    const response = await fetch(`${API_INTERNAL}/api/reporting/export-excel`, {
      method: 'GET',
      signal: AbortSignal.timeout(15000),
    });

    if (!response.ok) {
      return NextResponse.json(
        { error: 'Failed to generate Excel', status: response.status },
        { status: response.status }
      );
    }

    const buffer = await response.arrayBuffer();
    const filename = generateFilename();

    return new NextResponse(buffer, {
      status: 200,
      headers: {
        'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'Content-Disposition': `attachment; filename="${filename}"`,
      },
    });
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to export to Excel', details: String(error) },
      { status: 503 }
    );
  }
}

