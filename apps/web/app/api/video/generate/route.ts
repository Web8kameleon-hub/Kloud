import { NextRequest, NextResponse } from 'next/server';

/**
 * Video Generation API Route
 * Proxies requests to video-generator service
 */

const VIDEO_GENERATOR_URL = process.env.VIDEO_GENERATOR_URL || 'http://kloud-video-generator:8029';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    // Validate request
    if (!body.topic || body.topic.trim().length < 3) {
      return NextResponse.json(
        { error: 'Topic must be at least 3 characters' },
        { status: 400 }
      );
    }

    // Forward to video generator service
    const response = await fetch(`${VIDEO_GENERATOR_URL}/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        topic: body.topic,
        style: body.style || 'social_media',
        voice: body.voice || 'narrator',
        add_subtitles: body.add_subtitles !== false,
      }),
    });

    if (!response.ok) {
      const error = await response.text();
      console.error('Video generator error:', error);
      return NextResponse.json(
        { error: 'Failed to start video generation' },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Video generation API error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

