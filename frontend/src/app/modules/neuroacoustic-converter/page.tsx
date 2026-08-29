// Neuroacoustic Converter Industrial Page
// Author: Ledjan Ahmati

'use client'

import React, { useEffect, useState } from 'react'

interface ConverterData {
  timestamp: number
  inputType: string
  outputType: string
  conversionStatus: string
  inputSignal: number[]
  outputSignal: number[]
  metrics: {
    conversionTimeMs: number
    inputPeak: number
    outputPeak: number
    snr: number
  }
  log: Array<{ event: string; timestamp: number; message: string }>
  audit: {
    requestId: number
    receivedAt: string
    clientIp: string
    userAgent: string
  }
}

export default function NeuroacousticConverterPage() {
  const [data, setData] = useState<ConverterData | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchData() {
      try {
        // Simulate industrial neuroacoustic conversion data
        const now = Date.now()
        const inputSignal = Array.from({ length: 512 }, (_, i) => Math.sin(2 * Math.PI * 8 * (i / 512)))
        const outputSignal = inputSignal.map((v, i) => v * Math.exp(-i / 512))
        const metrics = {
          conversionTimeMs: 42,
          inputPeak: Math.max(...inputSignal),
          outputPeak: Math.max(...outputSignal),
          snr: 36.5
        }
        const log = [
          { event: 'start', timestamp: now - 5000, message: 'Converter started.' },
          { event: 'conversion', timestamp: now - 1000, message: 'Conversion complete.' }
        ]
        const audit = {
          requestId: Math.floor(Math.random() * 1e9),
          receivedAt: new Date(now).toISOString(),
          clientIp: '127.0.0.1',
          userAgent: navigator.userAgent
        }
        setData({
          timestamp: now,
          inputType: 'EEG',
          outputType: 'Audio',
          conversionStatus: 'success',
          inputSignal,
          outputSignal,
          metrics,
          log,
          audit
        })
      } catch (err: any) {
        setError('Failed to load converter data')
      }
    }
    fetchData()
  }, [])

  if (error) return <div className="text-red-500">{error}</div>
  if (!data) return <div>Loading neuroacoustic converter data...</div>

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Neuroacoustic Converter (Industrial)</h1>
      <div className="mb-2 text-xs text-muted-foreground">Request ID: {data.audit.requestId}</div>
      <div className="mb-4">Input: {data.inputType} | Output: {data.outputType} | Status: {data.conversionStatus}</div>
      <div className="mb-4">Conversion Time: {data.metrics.conversionTimeMs} ms | SNR: {data.metrics.snr}</div>
      <div className="mb-6">
        <h2 className="font-semibold mb-2">Input Signal</h2>
        <div className="grid grid-cols-16 gap-1">
          {data.inputSignal.map((v, i) => (
            <div key={i} className="bg-green-100 text-green-800 text-xs p-1 rounded text-center">{v.toFixed(2)}</div>
          ))}
        </div>
      </div>
      <div className="mb-6">
        <h2 className="font-semibold mb-2">Output Signal</h2>
        <div className="grid grid-cols-16 gap-1">
          {data.outputSignal.map((v, i) => (
            <div key={i} className="bg-blue-100 text-blue-800 text-xs p-1 rounded text-center">{v.toFixed(2)}</div>
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
