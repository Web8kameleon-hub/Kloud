// Spectrum Analyzer Industrial Page
// Author: Ledjan Ahmati

'use client'

import React, { useEffect, useState } from 'react'

interface SpectrumData {
  timestamp: number
  frequencies: number[]
  peak: number
  trough: number
  snr: number
  log: Array<{ event: string; timestamp: number; message: string }>
  audit: {
    requestId: number
    receivedAt: string
    clientIp: string
    userAgent: string
  }
}

export default function SpectrumAnalyzerPage() {
  const [data, setData] = useState<SpectrumData | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchData() {
      try {
        // Simulate industrial spectrum analyzer data
        const now = Date.now()
        const frequencies = Array.from({ length: 128 }, (_, i) => 1 + i * 0.5 + Math.sin(i / 10) * 2)
        const peak = Math.max(...frequencies)
        const trough = Math.min(...frequencies)
        const snr = 38.2
        const log = [
          { event: 'start', timestamp: now - 5000, message: 'Spectrum analyzer started.' },
          { event: 'scan', timestamp: now - 1000, message: 'Frequency scan complete.' }
        ]
        const audit = {
          requestId: Math.floor(Math.random() * 1e9),
          receivedAt: new Date(now).toISOString(),
          clientIp: '127.0.0.1',
          userAgent: navigator.userAgent
        }
        setData({ timestamp: now, frequencies, peak, trough, snr, log, audit })
      } catch (err: any) {
        setError('Failed to load spectrum data')
      }
    }
    fetchData()
  }, [])

  if (error) return <div className="text-red-500">{error}</div>
  if (!data) return <div>Loading spectrum data...</div>

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Spectrum Analyzer (Industrial)</h1>
      <div className="mb-2 text-xs text-muted-foreground">Request ID: {data.audit.requestId}</div>
      <div className="mb-4">Peak: {data.peak.toFixed(2)} | Trough: {data.trough.toFixed(2)} | SNR: {data.snr}</div>
      <div className="mb-6">
        <h2 className="font-semibold mb-2">Frequencies</h2>
        <div className="grid grid-cols-8 gap-1">
          {data.frequencies.map((f, i) => (
            <div key={i} className="bg-blue-100 text-blue-800 text-xs p-1 rounded text-center">{f.toFixed(2)}</div>
          ))}
        </div>
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
