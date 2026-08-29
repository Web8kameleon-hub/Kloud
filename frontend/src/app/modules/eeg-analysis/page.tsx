/* eslint-disable @next/next/no-img-element */
// EEG Analysis Industrial Page
// Author: Ledjan Ahmati

'use client'

import React, { useEffect, useState } from 'react'

interface EEGAnalysisData {
  timestamp: number
  analysisType: string
  eegSignal: number[]
  detectedEvents: Array<{ type: string; time: number; value: number }>
  status: string
  metrics: {
    analysisTimeMs: number
    peak: number
    mean: number
    eventCount: number
  }
  log: Array<{ event: string; timestamp: number; message: string }>
  audit: {
    requestId: number
    receivedAt: string
    clientIp: string
    userAgent: string
  }
}

export default function EEGAnalysisPage() {
  const [data, setData] = useState<EEGAnalysisData | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchData() {
      try {
        // Simulate industrial EEG analysis data
        const now = Date.now()
        const eegSignal = Array.from({ length: 128 }, (_, i) => Math.sin(2 * Math.PI * 10 * (i / 128)) + Math.random() * 0.1)
        const detectedEvents = eegSignal
          .map((v, i) => ({ type: v > 0.9 ? 'spike' : '', time: i, value: v }))
          .filter(e => e.type)
        const metrics = {
          analysisTimeMs: 33,
          peak: Math.max(...eegSignal),
          mean: eegSignal.reduce((a, b) => a + b, 0) / eegSignal.length,
          eventCount: detectedEvents.length
        }
        const log = [
          { event: 'start', timestamp: now - 3000, message: 'EEG analysis started.' },
          { event: 'analysis', timestamp: now - 200, message: 'EEG analysis complete.' }
        ]
        const audit = {
          requestId: Math.floor(Math.random() * 1e9),
          receivedAt: new Date(now).toISOString(),
          clientIp: '127.0.0.1',
          userAgent: navigator.userAgent
        }
        setData({
          timestamp: now,
          analysisType: 'EEG Spike Detection',
          eegSignal,
          detectedEvents,
          status: 'success',
          metrics,
          log,
          audit
        })
      } catch (err: any) {
        setError('Failed to load EEG analysis data')
      }
    }
    fetchData()
  }, [])

  if (error) return <div className="text-red-500">{error}</div>
  if (!data) return <div>Loading EEG analysis data...</div>

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">EEG Analysis (Industrial)</h1>
      <div className="mb-2 text-xs text-muted-foreground">Request ID: {data.audit.requestId}</div>
      <div className="mb-4">Type: {data.analysisType} | Status: {data.status}</div>
      <div className="mb-4">Analysis Time: {data.metrics.analysisTimeMs} ms | Events: {data.metrics.eventCount}</div>
      <div className="mb-6">
        <h2 className="font-semibold mb-2">EEG Signal</h2>
        <div className="grid grid-cols-16 gap-1">
          {data.eegSignal.map((v, i) => (
            <div key={i} className="bg-pink-100 text-pink-800 text-xs p-1 rounded text-center">{v.toFixed(2)}</div>
          ))}
        </div>
      </div>
      <div className="mb-6">
        <h2 className="font-semibold mb-2">Detected Events</h2>
        <ul className="text-xs">
          {data.detectedEvents.map((e, i) => (
            <li key={i}>{e.type} at {e.time}: {e.value.toFixed(2)}</li>
          ))}
        </ul>
      </div>
      <div className="mb-6">
        <h2 className="font-semibold mb-2">Log</h2>
        <ul className="text-xs">
          {data.log.map((l, i) => (
            <li key={i}>{new Date(l.timestamp).toLocaleTimeString()} - {l.event}: {l.message}</li>
          ))}
        </ul>
      </div>
      <div className="mb-2 text-xs text-muted-foreground">Received at: {data.audit.receivedAt}</div>
      <div className="mb-2 text-xs text-muted-foreground">Client IP: {data.audit.clientIp}</div>
      <div className="mb-2 text-xs text-muted-foreground">User Agent: {data.audit.userAgent}</div>
    </div>
  )
}
