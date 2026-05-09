import { NextRequest, NextResponse } from 'next/server';

/**
 * Video Job Status API Route
 * Check status of video generation job
 */

const VIDEO_GENERATOR_URL = process.env.VIDEO_GENERATOR_URL || 'http://kloud-video-generator:8029';

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const jobId = params.id;

    if (!jobId) {
      return NextResponse.json(
        { error: 'Job ID required' },
        { status: 400 }
      );
    }

    // Forward to video generator service
    const response = await fetch(`${VIDEO_GENERATOR_URL}/jobs/${jobId}`);

    if (!response.ok) {
      if (response.status === 404) {
        return NextResponse.json(
          { error: 'Job not found' },
          { status: 404 }
        );
      }
      return NextResponse.json(
        { error: 'Failed to get job status' },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Job status API error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

