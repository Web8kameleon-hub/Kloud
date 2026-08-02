'use client'

import { useState, useRef } from 'react'

interface DebateResponse {
  persona: string
  name: string
  emoji: string
  role: string
  response: string
  status: 'success' | 'error' | 'partial'
  tokens?: number
}

interface StreamingPersona {
  persona: string
  name: string
  emoji: string
  role?: string
  text: string
  done: boolean
}

const PERSONAS = [
  { id: 'alba', name: 'Alba', emoji: '🌅', role: 'Optimist' },
  { id: 'albi', name: 'Albi', emoji: '🔧', role: 'Pragmatist' },
  { id: 'jona', name: 'Jona', emoji: '🔍', role: 'Skeptic' },
  { id: 'blerina', name: 'Blerina', emoji: '💡', role: 'Analyst' },
  { id: 'asi', name: 'ASI', emoji: '🧠', role: 'Meta-Thinker' },
]

export default function DebatePage() {
  const [topic, setTopic] = useState('')
  const [responses, setResponses] = useState<DebateResponse[]>([])
  const [streaming, setStreaming] = useState<Record<string, StreamingPersona>>({})
  const [loading, setLoading] = useState(false)
  const [activeSpeaker, setActiveSpeaker] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [progress, setProgress] = useState(0)
  const abortRef = useRef<AbortController | null>(null)

  const startDebate = async () => {
    if (!topic.trim()) return
    
    // Cancel previous request if any
    if (abortRef.current) {
      abortRef.current.abort()
    }
    abortRef.current = new AbortController()
    
    setLoading(true)
    setError(null)
    setResponses([])
    setStreaming({})
    setProgress(0)
    
    try {
      // Use streaming endpoint for elastic responses
      const res = await fetch('/api/debate/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic, max_tokens: 25000 }),
        signal: abortRef.current.signal
      })
      
      if (!res.ok) throw new Error('Debate failed')
      
      const reader = res.body?.getReader()
      const decoder = new TextDecoder()
      
      if (!reader) throw new Error('No stream available')
      
      let completedCount = 0
      
      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        
        const text = decoder.decode(value)
        const lines = text.split('\n').filter(l => l.startsWith('data: '))
        
        for (const line of lines) {
          try {
            const data = JSON.parse(line.slice(6))
            
            if (data.type === 'thinking') {
              setActiveSpeaker(data.persona)
              // Initialize streaming state for this persona
              setStreaming(prev => ({
                ...prev,
                [data.persona]: {
                  persona: data.persona,
                  name: data.name || PERSONAS.find(p => p.id === data.persona)?.name || data.persona,
                  emoji: data.emoji || PERSONAS.find(p => p.id === data.persona)?.emoji || '🤖',
                  text: '',
                  done: false
                }
              }))
            } else if (data.type === 'token') {
              // Real-time token streaming - append token immediately
              setStreaming(prev => ({
                ...prev,
                [data.persona]: {
                  ...prev[data.persona],
                  text: (prev[data.persona]?.text || '') + data.token
                }
              }))
            } else if (data.type === 'response') {
              // Persona completed
              setResponses(prev => [...prev, data.data])
              setStreaming(prev => ({
                ...prev,
                [data.data.persona]: { ...prev[data.data.persona], done: true }
              }))
              completedCount++
              setProgress((completedCount / PERSONAS.length) * 100)
              setActiveSpeaker(null)
            } else if (data.type === 'done') {
              setActiveSpeaker(null)
            }
          } catch {
            // Skip parse errors
          }
        }
      }
    } catch (err) {
      if ((err as Error).name === 'AbortError') {
        setError('Debate cancelled')
      } else {
        // Fallback to non-streaming
        try {
          const res = await fetch('/api/debate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ topic })
          })
          if (res.ok) {
            const data = await res.json()
            setResponses(data.responses || [])
          } else {
            setError('Failed to connect to debate engine')
          }
        } catch {
          setError('Failed to connect to debate engine')
        }
      }
    } finally {
      setActiveSpeaker(null)
      setLoading(false)
      abortRef.current = null
    }
  }

  const cancelDebate = () => {
    if (abortRef.current) {
      abortRef.current.abort()
    }
  }

  const getResponseForPersona = (personaId: string) => {
    return responses.find(r => r.persona === personaId)
  }
  
  const getStreamingForPersona = (personaId: string) => {
    return streaming[personaId]
  }

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100">
      {/* Header */}
      <header className="border-b border-zinc-800">
        <div className="max-w-5xl mx-auto px-6 py-5 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-zinc-800 rounded-lg flex items-center justify-center text-lg">
              🎭
            </div>
            <div>
              <h1 className="text-lg font-semibold text-zinc-100">Trinity Debate</h1>
              <p className="text-xs text-zinc-500">5 AI Perspectives • Elastic Streaming • Up to 20K words</p>
            </div>
          </div>
          <a href="/modules" className="text-sm text-zinc-500 hover:text-zinc-300">
            ← Back
          </a>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-6 py-8">
        
        {/* Progress Bar */}
        {loading && (
          <div className="mb-6">
            <div className="h-1 bg-zinc-800 rounded-full overflow-hidden">
              <div 
                className="h-full bg-blue-500 transition-all duration-500"
                style={{ width: `${progress}%` }}
              />
            </div>
            <p className="text-xs text-zinc-500 mt-2 text-center">
              {activeSpeaker ? `${PERSONAS.find(p => p.id === activeSpeaker)?.name} is thinking...` : 'Processing...'}
            </p>
          </div>
        )}

        {/* Personas */}
        <div className="grid grid-cols-5 gap-3 mb-8">
          {PERSONAS.map((p) => {
            const resp = getResponseForPersona(p.id)
            const streamData = getStreamingForPersona(p.id)
            const isActive = activeSpeaker === p.id
            const isStreaming = streamData && !streamData.done && streamData.text.length > 0
            const hasResponse = !!resp
            
            return (
              <div
                key={p.id}
                className={`text-center p-4 rounded-xl border transition-all ${
                  isActive || isStreaming
                    ? 'bg-blue-900/20 border-blue-600 animate-pulse' 
                    : hasResponse
                      ? resp.status === 'success' 
                        ? 'bg-green-900/10 border-green-800'
                        : 'bg-yellow-900/10 border-yellow-800'
                      : 'bg-zinc-900 border-zinc-800'
                }`}
              >
                <div className="text-2xl mb-2">{p.emoji}</div>
                <div className="text-sm font-medium text-zinc-200">{p.name}</div>
                <div className="text-xs text-zinc-500">{p.role}</div>
                {(isActive || isStreaming) && (
                  <div className="mt-2">
                    {isStreaming ? (
                      <span className="text-xs text-blue-400">{streamData.text.length} chars</span>
                    ) : (
                      <div className="flex justify-center gap-1">
                        <span className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce" style={{animationDelay: '0ms'}} />
                        <span className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce" style={{animationDelay: '150ms'}} />
                        <span className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce" style={{animationDelay: '300ms'}} />
                      </div>
                    )}
                  </div>
                )}
                {hasResponse && !isActive && (
                  <div className="mt-2 text-xs text-zinc-500">
                    {resp.tokens ? `${resp.tokens} words` : '✓'}
                  </div>
                )}
              </div>
            )
          })}
        </div>

        {/* Input */}
        <div className="bg-zinc-900 rounded-xl p-5 border border-zinc-800 mb-6">
          <input
            type="text"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && !loading && startDebate()}
            placeholder="Enter a topic for debate..."
            className="w-full bg-transparent text-zinc-100 placeholder-zinc-600 focus:outline-none text-sm"
            disabled={loading}
          />
          <div className="flex items-center justify-between pt-4 mt-4 border-t border-zinc-800">
            <div className="flex flex-wrap gap-2">
              {['Future of AI', 'Remote vs Office', 'Privacy vs Security', 'Climate Action'].map((t) => (
                <button
                  key={t}
                  onClick={() => setTopic(t)}
                  disabled={loading}
                  className="px-3 py-1.5 bg-zinc-800 text-zinc-400 text-xs rounded-lg hover:bg-zinc-700 hover:text-zinc-300 transition-colors disabled:opacity-50"
                >
                  {t}
                </button>
              ))}
            </div>
            <div className="flex gap-2">
              {loading && (
                <button
                  onClick={cancelDebate}
                  className="px-4 py-2 bg-red-900/20 text-red-400 text-sm font-medium rounded-lg hover:bg-red-900/30 transition-colors"
                >
                  Cancel
                </button>
              )}
              <button
                onClick={startDebate}
                disabled={loading || !topic.trim()}
                className="px-5 py-2 bg-zinc-100 text-zinc-900 text-sm font-medium rounded-lg hover:bg-white disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
              >
                {loading ? 'Streaming...' : 'Start Debate'}
              </button>
            </div>
          </div>
        </div>

        {/* Error */}
        {error && (
          <div className="bg-red-500/5 border border-red-500/20 rounded-xl p-4 text-red-400 text-sm mb-6">
            {error}
          </div>
        )}

        {/* Debate Results - Real-time streaming */}
        {(responses.length > 0 || Object.keys(streaming).length > 0) && (
          <div className="space-y-4">
            <div className="flex items-center justify-between text-sm">
              <span className="text-zinc-400">Topic: <span className="text-zinc-200">{topic}</span></span>
              <span className="text-zinc-600">{responses.filter(r => r.status === 'success').length}/{PERSONAS.length} responses</span>
            </div>
            
            {/* Show streaming personas first */}
            {PERSONAS.map((p) => {
              const resp = getResponseForPersona(p.id)
              const streamData = getStreamingForPersona(p.id)
              
              // Skip if no data
              if (!resp && !streamData) return null
              
              // Use final response if available, otherwise show streaming
              const displayText = resp?.response || streamData?.text || ''
              const isLive = streamData && !streamData.done && streamData.text.length > 0
              
              return (
                <div
                  key={p.id}
                  className={`bg-zinc-900 rounded-xl p-5 border animate-fadeIn ${
                    isLive ? 'border-blue-600' : 'border-zinc-800'
                  }`}
                >
                  <div className="flex items-start gap-4">
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center text-xl flex-shrink-0 ${
                      isLive ? 'bg-blue-900/30' : 'bg-zinc-800'
                    }`}>
                      {p.emoji}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="font-medium text-zinc-200">{p.name}</span>
                        <span className="text-xs text-zinc-600">{p.role}</span>
                        {isLive && (
                          <span className="px-2 py-0.5 bg-blue-500/10 text-blue-400 text-xs rounded flex items-center gap-1">
                            <span className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-pulse" />
                            Live
                          </span>
                        )}
                        {resp?.status === 'partial' && (
                          <span className="px-2 py-0.5 bg-yellow-500/10 text-yellow-400 text-xs rounded">
                            Partial
                          </span>
                        )}
                        {resp?.status === 'error' && (
                          <span className="px-2 py-0.5 bg-red-500/10 text-red-400 text-xs rounded">
                            Error
                          </span>
                        )}
                        {resp?.tokens && (
                          <span className="px-2 py-0.5 bg-zinc-800 text-zinc-500 text-xs rounded">
                            {resp.tokens} tokens
                          </span>
                        )}
                      </div>
                      <p className="text-zinc-400 text-sm leading-relaxed whitespace-pre-wrap">
                        {displayText || 'Starting...'}
                        {isLive && <span className="inline-block w-2 h-4 bg-blue-400 ml-1 animate-pulse" />}
                      </p>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        )}

        {/* Empty */}
        {responses.length === 0 && Object.keys(streaming).length === 0 && !loading && !error && (
          <div className="text-center py-20 text-zinc-600">
            <div className="text-5xl mb-4">🎭</div>
            <p className="text-sm">Enter a topic to start a multi-perspective debate</p>
            <p className="text-xs text-zinc-700 mt-1">5 AI personas • Elastic streaming • Up to 20,000 words per response</p>
          </div>
        )}
      </main>
      
      {/* CSS for animations */}
      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fadeIn {
          animation: fadeIn 0.3s ease-out forwards;
        }
      `}</style>
    </div>
  )
}
