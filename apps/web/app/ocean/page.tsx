'use client'
/**
 * CURIOSITY OCEAN - Interactive AI Chat
 * =====================================
 * 
 * Full integration with Ocean Core API via Next.js API route
 * Features:
 * - Real-time chat with AI Orchestrator
 * - Streaming responses
 * - Real-time date/time awareness
 * - Wikipedia, Weather, GitHub integration
 */

import { useState, useEffect, useRef } from 'react'

interface ChatMessage {
  id: number
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  persona?: string
  sources?: string[]
  confidence?: number
}

interface OceanStatus {
  service: string
  version: string
  status: string
  timestamp: string
}

// Use Next.js API route as proxy to Ocean-Core (works from browser!)
const OCEAN_API = '/api/ocean'

export default function OceanPage() {
  const [messages, setMessages] = useState<ChatMessage[]>(() => {
    const now = new Date()
    return [{
      id: 1,
      role: 'assistant',
      content: `🌊 **Curiosity Ocean është online.**

Platforma është gati për pyetje teknike, kërkim, analizë dhe orkestrim operacional.

Mund të fillojmë me:
- Arkitekturë dhe troubleshooting
- Kërkim dokumentacioni
- Analizë kodi dhe API

Shkruaj pyetjen tënde.`,
      timestamp: now,
    }]
  })
  const [inputMessage, setInputMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const [chatLoading, setChatLoading] = useState(false)
  const [status, setStatus] = useState<OceanStatus | null>(null)
  const [error, setError] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Check Ocean Core status
  useEffect(() => {
    const checkStatus = async () => {
      try {
        // Use Next.js API route
        const response = await fetch(OCEAN_API)
        if (response.ok) {
          const data = await response.json()
          setStatus({ 
            service: 'Ocean Core',
            version: '2.0',
            status: data.status || 'connected',
            timestamp: new Date().toISOString()
          })
          setError(null)
        } else {
          throw new Error('API not available')
        }
      } catch (err) {
        // Keep chat usable even if status check fails
        setStatus({ 
          service: 'Ocean Core',
          version: '2.0',
          status: 'ready',
          timestamp: new Date().toISOString()
        })
        setError(null)
        console.error('Ocean Core connection error:', err)
      }
    }

    checkStatus()
  }, [])

// Send message to Ocean Core with STREAMING via Next.js API route
  const sendMessage = async () => {
    if (!inputMessage.trim() || chatLoading) return

    const userMessage: ChatMessage = {
      id: Date.now(),
      role: 'user',
      content: inputMessage,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputMessage('')
    setChatLoading(true)

    // Add empty assistant message that we'll fill with streaming content
    const assistantMessageId = Date.now() + 1
    setMessages(prev => [...prev, {
      id: assistantMessageId,
      role: 'assistant',
      content: '',
      timestamp: new Date()
    }])

    try {
      // Use STREAMING endpoint - starts writing immediately!
      const response = await fetch('/api/ocean/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: inputMessage })
      })

      if (!response.ok) throw new Error('API error')
      if (!response.body) throw new Error('No response body')

      // Read streaming response
      const reader = response.body.getReader()
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
              if (json.chunk) {
                fullContent += json.chunk
                // Update message in real-time as chunks arrive
                setMessages(prev => prev.map(msg =>
                  msg.id === assistantMessageId
                    ? { ...msg, content: fullContent }
                    : msg
                ))
              }
            } catch {
              // Not JSON, might be raw text
              fullContent += data
              setMessages(prev => prev.map(msg =>
                msg.id === assistantMessageId
                  ? { ...msg, content: fullContent }
                  : msg
              ))
            }
          }
        }
      }

      // Ensure final content is set
      if (fullContent) {
        setMessages(prev => prev.map(msg =>
          msg.id === assistantMessageId
            ? { ...msg, content: fullContent }
            : msg
        ))
      }

    } catch (err) {
      setMessages(prev => prev.map(msg =>
        msg.id === assistantMessageId
          ? { ...msg, content: '❌ Gabim lidhjeje. Provoni përsëri.' }
          : msg
      ))
      console.error('Chat error:', err)
    } finally {
      setChatLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-slate-900 to-slate-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-violet-400 mx-auto"></div>
          <p className="mt-4 text-violet-300">Connecting to Ocean Core...</p>
        </div>
      </div>
    )
  }

  // Error state
  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-slate-900 to-red-900">
        <div className="text-center max-w-md p-8">
          <div className="text-6xl mb-4">🌊</div>
          <h1 className="text-2xl font-bold text-white mb-4">Ocean Core Offline</h1>
          <p className="text-red-300 mb-6">{error}</p>
          <div className="bg-slate-800 rounded-lg p-4 text-left text-sm text-gray-300">
            <p className="mb-2">Try these commands:</p>
            <code className="block bg-black/50 p-2 rounded mb-2">docker-compose up -d ocean-core</code>
            <code className="block bg-black/50 p-2 rounded">curl http://localhost:8030/api/v1/status</code>
          </div>
          <button 
            onClick={() => window.location.reload()}
            className="mt-6 px-6 py-2 bg-violet-500 hover:bg-violet-600 text-white rounded-lg transition-colors"
          >
            Retry Connection
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-900 via-slate-900 to-slate-900">
      {/* Header */}
      <header className="border-b border-slate-800/50 bg-slate-900/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-4xl">🌊</span>
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-violet-400 to-violet-400 bg-clip-text text-transparent">
                Curiosity Ocean
              </h1>
              <p className="text-xs text-gray-400">AI Orchestrator • Sovereign Runtime • Real-time Telemetry</p>
            </div>
          </div>
          {status && (
            <div className="flex items-center gap-2 text-sm">
              <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
              <span className="text-green-400">v{status.version}</span>
            </div>
          )}
        </div>
      </header>

      {/* Chat Container */}
      <main className="max-w-4xl mx-auto px-4 py-6 flex flex-col h-[calc(100vh-140px)]">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto space-y-4 pb-4">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                  msg.role === 'user'
                    ? 'bg-violet-600 text-white rounded-br-md'
                    : 'bg-slate-800 text-gray-100 rounded-bl-md border border-slate-800/30'
                }`}
              >
                {/* Message content with markdown-like formatting */}
                <div className="whitespace-pre-wrap">
                  {msg.content.split('\n').map((line, i) => {
                    // Bold text
                    const boldParsed = line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                    return (
                      <p 
                        key={i} 
                        className={line.startsWith('•') ? 'ml-2' : ''}
                        dangerouslySetInnerHTML={{ __html: boldParsed }}
                      />
                    )
                  })}
                </div>
                
                {/* Metadata for assistant messages */}
                {msg.role === 'assistant' && (msg.sources?.length || msg.confidence) && (
                  <div className="mt-2 pt-2 border-t border-slate-800/30 text-xs text-gray-400 flex gap-4">
                    {msg.confidence && (
                      <span>Confidence: {Math.round(msg.confidence * 100)}%</span>
                    )}
                    {msg.sources && msg.sources.length > 0 && (
                      <span>Sources: {msg.sources.slice(0, 3).join(', ')}</span>
                    )}
                  </div>
                )}
                
                <div className="text-xs opacity-50 mt-1">
                  {msg.timestamp.toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))}
          
          {/* Loading indicator */}
          {chatLoading && (
            <div className="flex justify-start">
              <div className="bg-slate-800 rounded-2xl rounded-bl-md px-4 py-3 border border-slate-800/30">
                <div className="flex items-center gap-2">
                  <div className="animate-pulse flex gap-1">
                    <span className="w-2 h-2 bg-violet-400 rounded-full animate-bounce"></span>
                    <span className="w-2 h-2 bg-violet-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></span>
                    <span className="w-2 h-2 bg-violet-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></span>
                  </div>
                  <span className="text-violet-300 text-sm">Orchestrator is thinking...</span>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="border-t border-slate-800/50 pt-4">
          <div className="flex gap-3">
            <textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyDown={handleKeyPress}
              placeholder="Ask anything... (Press Enter to send)"
              className="flex-1 bg-slate-800 border border-slate-800/50 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-violet-500 resize-none"
              rows={2}
              disabled={chatLoading}
            />
            <button
              onClick={sendMessage}
              disabled={!inputMessage.trim() || chatLoading}
              className="px-6 bg-gradient-to-r from-violet-500 to-violet-500 hover:from-violet-600 hover:to-violet-600 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-xl font-medium transition-all"
            >
              {chatLoading ? '...' : 'Send'}
            </button>
          </div>
          <p className="text-center text-xs text-gray-500 mt-2">
            Powered by Kloud Ocean Core • Operational reasoning and verified integrations
          </p>
        </div>
      </main>
    </div>
  )
}








