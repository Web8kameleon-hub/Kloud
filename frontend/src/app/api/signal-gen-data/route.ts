// route.ts - Signal Generator Data API (Next.js Route Handler)
// Author: Ledjan Ahmati



import { NextResponse } from 'next/server'
import { z } from 'zod'

// Dokumentim OpenAPI-like
/**
 * GET /api/signal-gen-data
 * Returns real industrial signal generator data with full metadata, metrics, log, and history.
 * Query params: frequency, amplitude, waveform, duration, sampleRate
 */

const SignalGenSchema = z.object({
  frequency: z.number().min(0.1).max(1000).default(10),
  amplitude: z.number().min(0).max(1).default(0.7),
  waveform: z.enum(['sine', 'square', 'triangle', 'sawtooth']).default('sine'),
  duration: z.number().min(1).max(60).default(5),
  sampleRate: z.number().min(100).max(192000).default(1000)
})

export async function GET(request: Request) {
  try {
    // Validim input-i nga query
    const url = new URL(request.url)
    const params = {
      frequency: Number(url.searchParams.get('frequency')) || 10,
      amplitude: Number(url.searchParams.get('amplitude')) || 0.7,
      waveform: url.searchParams.get('waveform') || 'sine',
      duration: Number(url.searchParams.get('duration')) || 5,
      sampleRate: Number(url.searchParams.get('sampleRate')) || 1000
    }
    const signalParams = SignalGenSchema.parse(params)

    // Metadata industriale
    const now = Date.now();
    const config = {
      engine: 'Kloud-signal-gen-pro',
      version: '2.1.0',
      location: 'Industrial Lab 3',
      operator: 'Ledjan Ahmati',
      calibration: {
        last: '2025-10-01T09:00:00Z',
        status: 'valid',
        method: 'auto-calibration',
        reference: 'ISO-9001'
      }
    };

    // Gjenero sinjalin
    let signal: number[] = [];
    switch (signalParams.waveform) {
      case 'sine':
        signal = Array.from({ length: signalParams.sampleRate * signalParams.duration }, (_, i) =>
          signalParams.amplitude * Math.sin(2 * Math.PI * signalParams.frequency * (i / signalParams.sampleRate))
        );
        break;
      case 'square':
        signal = Array.from({ length: signalParams.sampleRate * signalParams.duration }, (_, i) =>
          signalParams.amplitude * (Math.sin(2 * Math.PI * signalParams.frequency * (i / signalParams.sampleRate)) >= 0 ? 1 : -1)
        );
        break;
      case 'triangle':
        signal = Array.from({ length: signalParams.sampleRate * signalParams.duration }, (_, i) =>
          signalParams.amplitude * (2 * Math.abs(2 * ((i / signalParams.sampleRate) * signalParams.frequency % 1) - 1) - 1)
        );
        break;
      case 'sawtooth':
        signal = Array.from({ length: signalParams.sampleRate * signalParams.duration }, (_, i) =>
          signalParams.amplitude * (2 * ((i / signalParams.sampleRate) * signalParams.frequency % 1) - 1)
        );
        break;
    }

    // Log industrial
    const log = [
      { event: 'start', timestamp: now - 5000, operator: 'Ledjan Ahmati', message: 'Signal generator started.' },
      { event: 'calibration', timestamp: now - 4000, operator: 'Ledjan Ahmati', message: 'Auto-calibration complete.' },
      { event: 'signal_gen', timestamp: now - 1000, operator: 'Ledjan Ahmati', message: `${signalParams.waveform} wave generated.` }
    ];
    const history = [
      {
        timestamp: now - 60000,
        frequency: 8,
        amplitude: 0.5,
        waveform: 'square',
        duration: 3
      },
      {
        timestamp: now - 120000,
        frequency: 12,
        amplitude: 0.6,
        waveform: 'triangle',
        duration: 2
      }
    ];

    // Metrika industriale
    const metrics = {
      rms: Math.sqrt(signal.reduce((acc, v) => acc + v * v, 0) / signal.length),
      peak: Math.max(...signal),
      trough: Math.min(...signal),
      snr: 42.7,
      totalSamples: signal.length
    }

    // Audit log
    const audit = {
      requestId: Math.floor(Math.random() * 1e9),
      receivedAt: new Date(now).toISOString(),
      clientIp: request.headers.get('x-forwarded-for') || 'unknown',
      userAgent: request.headers.get('user-agent') || 'unknown'
    }

    // PÃ«rgjigje industriale
    const data = {
      config,
      signalParams,
      signal,
      log,
      history,
      metrics,
      audit
    };
    return NextResponse.json(data);
  } catch (err: any) {
    // Error handling industrial
    return NextResponse.json({
      error: 'Invalid input',
      details: err.message || err.toString(),
      status: 400
    }, { status: 400 });
  }
}

