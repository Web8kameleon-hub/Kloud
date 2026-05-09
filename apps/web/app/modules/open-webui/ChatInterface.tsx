
/*
  Copyright (c) 2025 Ledjan Ahmati. All rights reserved.
  This software is proprietary and confidential. Unauthorized copying, distribution, or use is strictly prohibited.
  Author: Ledjan Ahmati
  License: Closed Source
*/

'use client'

import { useState, useRef, useCallback, useEffect } from 'react'

export default function OpenWebUIChat() {
  const [messages, setMessages] = useState<Array<{id: number; text: string; sender: string; type?: string}>>([
    { id: 1, text: "Hello! I'm Kloud AI. Send text, voice, photos, or documents — everything is processed by real AI.", sender: 'bot' }
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  // Mic state
  const [isRecording, setIsRecording] = useState(false)
  const [recordingDuration, setRecordingDuration] = useState(0)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const recordingTimerRef = useRef<ReturnType<typeof setInterval> | null>(null)

  // Camera state
  const [showCamera, setShowCamera] = useState(false)
  const [facingMode, setFacingMode] = useState<'user' | 'environment'>('user')
  const [cameraReady, setCameraReady] = useState(false)
  const videoRef = useRef<HTMLVideoElement>(null)
  const streamRef = useRef<MediaStream | null>(null)

  // Document state
  const [isDragOver, setIsDragOver] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const messagesEndRef = useRef<HTMLDivElement>(null)
  const OCEAN_API = process.env.NEXT_PUBLIC_OCEAN_URL || 'http://localhost:8030'

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopCameraStream()
      stopRecording()
    }
  }, [])

  const addMessage = useCallback((text: string, sender: string, type?: string) => {
    setMessages(prev => [...prev, { id: Date.now() + Math.random(), text, sender, type }])
  }, [])

  // ======================== CHAT (STREAMING) ========================
  const sendMessage = async () => {
    const trimmed = input.trim()
    if (!trimmed || isLoading) return
    addMessage(trimmed, 'user')
    setInput('')
    setIsLoading(true)
    
    // Create placeholder for streaming response
    const botMsgId = Date.now() + Math.random()
    setMessages(prev => [...prev, { id: botMsgId, text: '', sender: 'bot' }])
    
    try {
      // Use STREAMING endpoint for instant response!
      const res = await fetch('/api/ocean/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: trimmed })
      })
      
      if (!res.ok) throw new Error('API error')
      if (!res.body) throw new Error('No response body')
      
      // Stream response in real-time
      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      let fullContent = ''
      
      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        
        const chunk = decoder.decode(value, { stream: true })
        const lines = chunk.split('\n')
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6)
            if (data === '[DONE]') continue
            try {
              const json = JSON.parse(data)
              if (json.chunk) fullContent += json.chunk
            } catch {
              fullContent += data
            }
          } else if (line.trim()) {
            fullContent += line
          }
        }
        
        // Update message in real-time
        setMessages(prev => prev.map(msg =>
          msg.id === botMsgId ? { ...msg, text: fullContent } : msg
        ))
      }
      
      // Final update
      if (!fullContent) {
        setMessages(prev => prev.map(msg =>
          msg.id === botMsgId ? { ...msg, text: 'No response received.' } : msg
        ))
      }
    } catch {
      setMessages(prev => prev.map(msg =>
        msg.id === botMsgId ? { ...msg, text: 'Connection error. Check if Ocean Core is running.', type: 'error' } : msg
      ))
    } finally {
      setIsLoading(false)
    }
  }

  // ======================== MICROPHONE ========================
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const recorder = new MediaRecorder(stream, { mimeType: MediaRecorder.isTypeSupported('audio/webm') ? 'audio/webm' : 'audio/mp4' })
      const chunks: BlobPart[] = []
      recorder.ondataavailable = (e) => { if (e.data.size > 0) chunks.push(e.data) }
      recorder.onstop = async () => {
        stream.getTracks().forEach(t => t.stop())
        const blob = new Blob(chunks, { type: recorder.mimeType })
        if (blob.size < 100) {
          addMessage('Recording too short. Hold longer.', 'bot', 'error')
          return
        }
        await sendAudio(blob)
      }
      mediaRecorderRef.current = recorder
      recorder.start()
      setIsRecording(true)
      setRecordingDuration(0)
      recordingTimerRef.current = setInterval(() => {
        setRecordingDuration(prev => prev + 1)
      }, 1000)
    } catch {
      addMessage('Microphone access denied. Check browser permissions.', 'bot', 'error')
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current?.state === 'recording') {
      mediaRecorderRef.current.stop()
    }
    mediaRecorderRef.current = null
    setIsRecording(false)
    setRecordingDuration(0)
    if (recordingTimerRef.current) {
      clearInterval(recordingTimerRef.current)
      recordingTimerRef.current = null
    }
  }

  const sendAudio = async (blob: Blob) => {
    addMessage(`🎤 Voice message (${(blob.size / 1024).toFixed(0)} KB)`, 'user')
    setIsLoading(true)
    try {
      const reader = new FileReader()
      const base64 = await new Promise<string>((resolve, reject) => {
        reader.onloadend = () => resolve((reader.result as string).split(',')[1])
        reader.onerror = reject
        reader.readAsDataURL(blob)
      })
      const res = await fetch('/api/ocean/audio', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ audio_base64: base64, language: 'auto' })
      })
      const data = await res.json()
      if (data.status === 'success' && data.transcript) {
        const transcript = data.transcript.trim()
        addMessage(`📝 "${transcript}" (${data.language || 'auto'}, ${data.processing_time}s)`, 'bot')
        // Put transcript in input so user can send it as chat or edit it
        if (transcript && transcript !== '[Nuk u dallua fjalim në audio]') {
          setInput(transcript)
        }
      } else if (data.status === 'whisper_not_available') {
        addMessage('Whisper engine not available on server. Install: pip install faster-whisper', 'bot', 'error')
      } else {
        addMessage(data.message || 'Could not transcribe audio.', 'bot', 'error')
      }
    } catch {
      addMessage('Audio transcription failed. Check server connection.', 'bot', 'error')
    } finally {
      setIsLoading(false)
    }
  }

  const toggleRecording = () => {
    if (isRecording) stopRecording()
    else startRecording()
  }

  // ======================== CAMERA ========================
  const startCameraStream = useCallback(async (facing: 'user' | 'environment') => {
    stopCameraStream()
    setCameraReady(false)
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: facing, width: { ideal: 1280 }, height: { ideal: 720 } }
      })
      streamRef.current = stream
      if (videoRef.current) {
        videoRef.current.srcObject = stream
        videoRef.current.onloadeddata = () => setCameraReady(true)
      }
    } catch {
      addMessage('Camera access denied. Check browser permissions.', 'bot', 'error')
      setShowCamera(false)
    }
  }, [addMessage])

  const stopCameraStream = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(t => t.stop())
      streamRef.current = null
    }
    if (videoRef.current) videoRef.current.srcObject = null
    setCameraReady(false)
  }

  const toggleCamera = async () => {
    if (showCamera) {
      stopCameraStream()
      setShowCamera(false)
    } else {
      setShowCamera(true)
      await startCameraStream(facingMode)
    }
  }

  const switchCamera = async () => {
    const newFacing = facingMode === 'user' ? 'environment' : 'user'
    setFacingMode(newFacing)
    if (showCamera) await startCameraStream(newFacing)
  }

  const captureAndAnalyze = async () => {
    const video = videoRef.current
    if (!video || !cameraReady) return
    const canvas = document.createElement('canvas')
    canvas.width = video.videoWidth || 640
    canvas.height = video.videoHeight || 480
    const ctx = canvas.getContext('2d')
    if (!ctx) return
    ctx.drawImage(video, 0, 0)
    const base64 = canvas.toDataURL('image/jpeg', 0.85).split(',')[1]
    addMessage('📷 Photo captured for AI analysis', 'user')
    stopCameraStream()
    setShowCamera(false)
    setIsLoading(true)
    try {
      const res = await fetch('/api/ocean/vision', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image_base64: base64, prompt: 'Describe this image in detail' })
      })
      const data = await res.json()
      if (data.status === 'success') {
        addMessage(`🔍 ${data.analysis}`, 'bot')
      } else if (data.status === 'model_not_found') {
        addMessage(`Vision model not installed. Run: ${data.install_command}`, 'bot', 'error')
      } else {
        addMessage(data.message || 'Vision analysis failed.', 'bot', 'error')
      }
    } catch {
      addMessage('Vision analysis failed. Check server connection.', 'bot', 'error')
    } finally {
      setIsLoading(false)
    }
  }

  // ======================== DOCUMENT ========================
  const processFile = async (file: File) => {
    const maxSize = 5 * 1024 * 1024
    if (file.size > maxSize) {
      addMessage(`File too large (${(file.size / 1024 / 1024).toFixed(1)} MB). Max 5 MB.`, 'bot', 'error')
      return
    }
    const textTypes = ['.txt', '.md', '.csv', '.json', '.xml', '.html', '.log']
    const isText = textTypes.some(ext => file.name.toLowerCase().endsWith(ext)) || file.type.startsWith('text/')
    if (!isText) {
      addMessage(`Unsupported file: ${file.name}. Use text-based files (.txt, .md, .csv, .json, .xml).`, 'bot', 'error')
      return
    }
    addMessage(`📄 ${file.name} (${(file.size / 1024).toFixed(0)} KB)`, 'user')
    setIsLoading(true)
    try {
      const content = await file.text()
      const res = await fetch('/api/ocean/document', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content, action: 'summarize', doc_type: file.name.split('.').pop() || 'text' })
      })
      const data = await res.json()
      if (data.status === 'success') {
        addMessage(`📋 ${data.analysis}`, 'bot')
      } else {
        addMessage(data.message || 'Document analysis failed.', 'bot', 'error')
      }
    } catch {
      addMessage('Document analysis failed. Check server connection.', 'bot', 'error')
    } finally {
      setIsLoading(false)
    }
  }

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) processFile(file)
    e.target.value = ''
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
    const file = e.dataTransfer.files[0]
    if (file) processFile(file)
  }

  return (
    <div className="min-h-screen bg-white flex">
      {/* Sidebar */}
      <div className="w-72 bg-gradient-to-b from-slate-900 to-slate-800 text-white p-5 hidden md:flex flex-col">
        <h1 className="text-xl font-bold mb-1">🧠 Kloud AI</h1>
        <p className="text-slate-400 text-sm mb-6">Multimodal Assistant</p>
        <div className="space-y-2">
          {[
            { icon: '🧠', name: 'ALBI', desc: 'EEG Analysis', color: 'green' },
            { icon: '📚', name: 'ALBA', desc: 'Data Collection', color: 'violet' },
            { icon: '🎵', name: 'JONA', desc: 'Neural Synthesis', color: 'purple' },
          ].map(m => (
            <div key={m.name} className={`p-3 bg-${m.color}-500/20 rounded-lg border border-${m.color}-500/30`}>
              <div className="font-semibold">{m.icon} {m.name}</div>
              <div className="text-sm text-slate-400">{m.desc}</div>
            </div>
          ))}
        </div>
        <div className="mt-auto pt-6 text-xs text-slate-500">
          <div className="flex items-center gap-2 mb-1">
            <span className="w-2 h-2 bg-green-400 rounded-full" />
            Ocean Core Connected
          </div>
          <div>🎤 Whisper • 📷 LLaVA • 📄 Ollama</div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div
        className={`flex-1 flex flex-col ${isDragOver ? 'ring-2 ring-violet-400 ring-inset' : ''}`}
        onDragOver={(e) => { e.preventDefault(); setIsDragOver(true) }}
        onDragLeave={() => setIsDragOver(false)}
        onDrop={handleDrop}
      >
        {/* Drag overlay */}
        {isDragOver && (
          <div className="absolute inset-0 bg-violet-500/10 z-40 flex items-center justify-center pointer-events-none">
            <div className="bg-white shadow-xl rounded-2xl p-8 text-center">
              <span className="text-4xl block mb-2">📄</span>
              <p className="text-lg font-semibold text-slate-700">Drop file to analyze</p>
              <p className="text-sm text-slate-400">.txt, .md, .csv, .json, .xml</p>
            </div>
          </div>
        )}

        {/* Messages */}
        <div className="flex-1 p-4 md:p-6 space-y-3 overflow-auto bg-slate-50">
          {messages.map((msg) => (
            <div key={msg.id} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-lg px-4 py-3 rounded-2xl text-sm leading-relaxed ${
                msg.sender === 'user'
                  ? 'bg-violet-600 text-white'
                  : msg.type === 'error'
                    ? 'bg-red-50 text-red-700 border border-red-200'
                    : 'bg-white text-slate-800 shadow-sm border border-slate-100'
              }`}>
                {msg.sender === 'bot' && (
                  <div className="flex items-center gap-1.5 mb-1 text-xs font-medium text-slate-400">
                    <span>🧠</span> Kloud AI
                  </div>
                )}
                <div className="whitespace-pre-wrap">{msg.text}</div>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-white px-4 py-3 rounded-2xl shadow-sm border border-slate-100">
                <div className="flex items-center gap-2 text-sm text-slate-400">
                  <span className="animate-spin">⏳</span> Processing...
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Camera Panel */}
        {showCamera && (
          <div className="bg-black p-3">
            <div className="relative max-w-lg mx-auto">
              <video ref={videoRef} autoPlay playsInline muted className="w-full rounded-xl bg-slate-900" />
              {!cameraReady && (
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-white animate-pulse">Starting camera...</span>
                </div>
              )}
              <div className="absolute bottom-3 left-1/2 -translate-x-1/2 flex gap-2">
                <button onClick={switchCamera} className="px-3 py-2 bg-white/20 backdrop-blur text-white rounded-lg hover:bg-white/30 text-sm">
                  🔄 Flip
                </button>
                <button onClick={captureAndAnalyze} disabled={!cameraReady} className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:opacity-40 text-sm font-medium">
                  📸 Capture & Analyze
                </button>
                <button onClick={toggleCamera} className="px-3 py-2 bg-red-500/80 text-white rounded-lg hover:bg-red-600 text-sm">
                  ✕
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Recording Indicator */}
        {isRecording && (
          <div className="bg-red-500 text-white px-4 py-2 flex items-center justify-center gap-3 text-sm">
            <span className="w-3 h-3 bg-white rounded-full animate-pulse" />
            Recording... {recordingDuration}s
            <button onClick={stopRecording} className="ml-2 px-3 py-1 bg-white/20 rounded hover:bg-white/30">
              ⏹ Stop & Send
            </button>
          </div>
        )}

        {/* Input Area */}
        <div className="border-t bg-white p-3 md:p-4">
          <div className="flex items-center gap-2 max-w-4xl mx-auto">
            <button
              onClick={toggleRecording}
              className={`p-3 rounded-xl transition-all shrink-0 ${isRecording ? 'bg-red-500 text-white scale-110' : 'bg-slate-100 hover:bg-slate-200 text-slate-600'}`}
              title="Voice recording — real transcription via Whisper"
            >
              🎤
            </button>
            <button
              onClick={toggleCamera}
              className={`p-3 rounded-xl transition-all shrink-0 ${showCamera ? 'bg-blue-500 text-white' : 'bg-slate-100 hover:bg-slate-200 text-slate-600'}`}
              title="Camera — real AI vision analysis via LLaVA"
            >
              📷
            </button>
            <button
              onClick={() => fileInputRef.current?.click()}
              className="p-3 bg-slate-100 rounded-xl hover:bg-slate-200 transition-all text-slate-600 shrink-0"
              title="Upload document — or drag & drop anywhere"
            >
              📄
            </button>
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileUpload}
              className="hidden"
              accept=".txt,.md,.csv,.json,.xml,.html,.log"
            />
            <input
              type="text"
              placeholder="Type a message..."
              className="flex-1 p-3 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent text-sm"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && sendMessage()}
              disabled={isLoading}
            />
            <button
              onClick={sendMessage}
              disabled={isLoading || !input.trim()}
              className="px-5 py-3 bg-violet-600 text-white rounded-xl hover:bg-violet-700 transition disabled:opacity-40 shrink-0 text-sm font-medium"
            >
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}









