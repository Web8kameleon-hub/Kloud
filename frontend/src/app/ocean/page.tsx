'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'

/**
 * OCEAN CORE - Curiosity Ocean Frontend
 * =====================================
 * Complete integration with Ocean Core API
 * - 14 Specialist Personas
 * - 23 City-Named Laboratories
 * - 61 Alphabet Layers
 * - Real-time Chat Interface
 * - System Status Monitoring
 * 
 * Author: Ledjan Ahmati
 * API: http://localhost:8030/api/v1
 */

interface OceanStatus {
  status: string
  version: string
  personas: number
  knowledge_engine: string
  data_sources: {
    laboratories: number
    ocean_labs_list: number
    ai_agents_status: number
  }
}

interface Persona {
  domain: string
  keywords: string[]
  description: string
}

interface ChatMessage {
  id: number
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  persona?: string
}

interface Lab {
  name: string
  location: string
  type: string
  status: string
}

const OCEAN_API = process.env.NEXT_PUBLIC_OCEAN_API || 'http://localhost:8030/api/v1'

export default function OceanPage() {
  const [status, setStatus] = useState<OceanStatus | null>(null)
  const [personas, setPersonas] = useState<Persona[]>([])
  const [labs, setLabs] = useState<Lab[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  // Chat state
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [inputMessage, setInputMessage] = useState('')
  const [chatLoading, setChatLoading] = useState(false)
  const [activeTab, setActiveTab] = useState<'chat' | 'personas' | 'labs' | 'status'>('chat')

  // Fetch status on mount
  useEffect(() => {
    fetchStatus()
    fetchPersonas()
    fetchLabs()
  }, [])

  const fetchStatus = async () => {
    try {
      const response = await fetch(`${OCEAN_API}/status`)
      if (response.ok) {
        const data = await response.json()
        setStatus(data)
      }
    } catch (err) {
      setError('Could not connect to Ocean Core')
    } finally {
      setLoading(false)
    }
  }

  const fetchPersonas = async () => {
    try {
      const response = await fetch(`${OCEAN_API}/personas`)
      if (response.ok) {
        const data = await response.json()
        setPersonas(data.personas || [])
      }
    } catch (err) {
      console.error('Failed to fetch personas:', err)
    }
  }

  const fetchLabs = async () => {
    try {
      const response = await fetch(`${OCEAN_API}/laboratories`)
      if (response.ok) {
        const data = await response.json()
        setLabs(data.laboratories || [])
      }
    } catch (err) {
      console.error('Failed to fetch labs:', err)
    }
  }

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

    try {
      const response = await fetch(`${OCEAN_API}/chat/orchestrated`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: inputMessage })
      })

      if (response.ok) {
        const data = await response.json()
        const assistantMessage: ChatMessage = {
          id: Date.now() + 1,
          role: 'assistant',
          content: data.fused_answer || data.response || 'No response',
          timestamp: new Date(),
          persona: data.primary_persona
        }
        setMessages(prev => [...prev, assistantMessage])
      } else {
        throw new Error('Failed to get response')
      }
    } catch (err) {
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        role: 'assistant',
        content: '❌ Failed to connect to Ocean Core. Please check if the service is running.',
        timestamp: new Date()
      }])
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

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-400">Connecting to Ocean Core...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <header className="bg-gradient-to-r from-blue-900 to-purple-900 p-6 border-b border-blue-700">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
              🌊 Curiosity Ocean
            </h1>
            <p className="text-gray-400 text-sm mt-1">
              Universal Knowledge Aggregation Engine • 14 Personas • 61 Layers
            </p>
          </div>
          <div className="flex items-center gap-4">
            <span className={`px-3 py-1 rounded-full text-sm ${
              status?.status === 'operational' ? 'bg-green-900 text-green-300' : 'bg-red-900 text-red-300'
            }`}>
              {status?.status === 'operational' ? '● Online' : '○ Offline'}
            </span>
            <Link href="/" className="text-gray-400 hover:text-white">
              ← Dashboard
            </Link>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto flex gap-1 p-2">
          {(['chat', 'personas', 'labs', 'status'] as const).map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 rounded-lg transition-colors ${
                activeTab === tab
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-400 hover:bg-gray-700 hover:text-white'
              }`}
            >
              {tab === 'chat' && '💬 Chat'}
              {tab === 'personas' && '🎭 Personas'}
              {tab === 'labs' && '🔬 Laboratories'}
              {tab === 'status' && '📊 Status'}
            </button>
          ))}
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto p-6">
        
        {/* Chat Tab */}
        {activeTab === 'chat' && (
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            {/* Chat Area */}
            <div className="lg:col-span-3 bg-gray-800 rounded-xl border border-gray-700 flex flex-col h-[600px]">
              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.length === 0 ? (
                  <div className="text-center text-gray-500 py-20">
                    <p className="text-4xl mb-4">🌊</p>
                    <p className="text-lg">Welcome to Curiosity Ocean</p>
                    <p className="text-sm mt-2">Ask anything and our 14 specialist personas will help you</p>
                    <div className="mt-6 grid grid-cols-2 gap-2 max-w-md mx-auto">
                      {['What is consciousness?', 'Tell me about IoT sensors', 'How does EEG work?', 'Explain quantum computing'].map(q => (
                        <button
                          key={q}
                          onClick={() => setInputMessage(q)}
                          className="p-2 bg-gray-700 rounded-lg text-sm hover:bg-gray-600 transition"
                        >
                          {q}
                        </button>
                      ))}
                    </div>
                  </div>
                ) : (
                  messages.map(msg => (
                    <div
                      key={msg.id}
                      className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-[80%] p-4 rounded-2xl ${
                          msg.role === 'user'
                            ? 'bg-blue-600 text-white'
                            : 'bg-gray-700 text-gray-100'
                        }`}
                      >
                        {msg.persona && (
                          <p className="text-xs text-blue-300 mb-1">🎭 {msg.persona}</p>
                        )}
                        <p className="whitespace-pre-wrap">{msg.content}</p>
                        <p className="text-xs opacity-50 mt-2">
                          {msg.timestamp.toLocaleTimeString()}
                        </p>
                      </div>
                    </div>
                  ))
                )}
                {chatLoading && (
                  <div className="flex justify-start">
                    <div className="bg-gray-700 p-4 rounded-2xl">
                      <div className="flex space-x-2">
                        <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                        <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Input */}
              <div className="p-4 border-t border-gray-700">
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={inputMessage}
                    onChange={e => setInputMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Ask Ocean anything..."
                    className="flex-1 bg-gray-700 border border-gray-600 rounded-xl px-4 py-3 focus:outline-none focus:border-blue-500"
                    disabled={chatLoading}
                  />
                  <button
                    onClick={sendMessage}
                    disabled={chatLoading || !inputMessage.trim()}
                    className="px-6 py-3 bg-blue-600 hover:bg-blue-500 disabled:bg-gray-600 rounded-xl transition-colors"
                  >
                    Send
                  </button>
                </div>
              </div>
            </div>

            {/* Sidebar */}
            <div className="space-y-4">
              {/* Quick Stats */}
              <div className="bg-gray-800 rounded-xl border border-gray-700 p-4">
                <h3 className="font-bold text-lg mb-3">📊 Quick Stats</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Personas</span>
                    <span className="text-blue-400">{status?.personas || 14}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Laboratories</span>
                    <span className="text-green-400">{labs.length || 23}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Alphabet Layers</span>
                    <span className="text-purple-400">61</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Knowledge Engine</span>
                    <span className="text-cyan-400">{status?.knowledge_engine || 'ready'}</span>
                  </div>
                </div>
              </div>

              {/* Active Personas */}
              <div className="bg-gray-800 rounded-xl border border-gray-700 p-4">
                <h3 className="font-bold text-lg mb-3">🎭 Active Personas</h3>
                <div className="space-y-1 text-xs max-h-40 overflow-y-auto">
                  {personas.slice(0, 7).map((p, i) => (
                    <div key={i} className="flex items-center gap-2 p-1">
                      <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                      <span className="text-gray-300">{p.domain}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Personas Tab */}
        {activeTab === 'personas' && (
          <div>
            <h2 className="text-2xl font-bold mb-6">🎭 14 Specialist Personas</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {personas.map((persona, i) => (
                <div key={i} className="bg-gray-800 rounded-xl border border-gray-700 p-4 hover:border-blue-500 transition-colors">
                  <h3 className="font-bold text-lg text-blue-400 mb-2">{persona.domain}</h3>
                  <p className="text-gray-400 text-sm mb-3">{persona.description}</p>
                  <div className="flex flex-wrap gap-1">
                    {persona.keywords?.slice(0, 4).map((kw, j) => (
                      <span key={j} className="px-2 py-0.5 bg-gray-700 rounded text-xs text-gray-300">
                        {kw}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Labs Tab */}
        {activeTab === 'labs' && (
          <div>
            <h2 className="text-2xl font-bold mb-6">🔬 23 City-Named Laboratories</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {labs.length > 0 ? labs.map((lab, i) => (
                <div key={i} className="bg-gray-800 rounded-xl border border-gray-700 p-4 hover:border-green-500 transition-colors">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                    <h3 className="font-bold text-green-400">{lab.name}</h3>
                  </div>
                  <p className="text-gray-400 text-sm">📍 {lab.location}</p>
                  <p className="text-gray-500 text-xs mt-1">{lab.type}</p>
                </div>
              )) : (
                // Default labs if API not connected
                ['Elbasan AI', 'Tirana Medical', 'Durrës IoT', 'Vlorë Marine', 'Prishtina Security', 'Roma Architecture', 'Zurich Finance', 'Vienna Neuroscience'].map((lab, i) => (
                  <div key={i} className="bg-gray-800 rounded-xl border border-gray-700 p-4">
                    <h3 className="font-bold text-green-400">{lab}</h3>
                    <p className="text-gray-500 text-xs mt-1">Laboratory #{i + 1}</p>
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        {/* Status Tab */}
        {activeTab === 'status' && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-gray-800 rounded-xl border border-gray-700 p-6">
              <h2 className="text-xl font-bold mb-4">🧠 Ocean Core Status</h2>
              {status ? (
                <div className="space-y-3">
                  <div className="flex justify-between border-b border-gray-700 pb-2">
                    <span>Status</span>
                    <span className="text-green-400">{status.status}</span>
                  </div>
                  <div className="flex justify-between border-b border-gray-700 pb-2">
                    <span>Version</span>
                    <span className="text-blue-400">{status.version}</span>
                  </div>
                  <div className="flex justify-between border-b border-gray-700 pb-2">
                    <span>Personas Active</span>
                    <span className="text-purple-400">{status.personas}</span>
                  </div>
                  <div className="flex justify-between border-b border-gray-700 pb-2">
                    <span>Knowledge Engine</span>
                    <span className="text-cyan-400">{status.knowledge_engine}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Laboratories</span>
                    <span className="text-green-400">{status.data_sources?.laboratories || 0}</span>
                  </div>
                </div>
              ) : (
                <p className="text-gray-500">Unable to fetch status</p>
              )}
            </div>

            <div className="bg-gray-800 rounded-xl border border-gray-700 p-6">
              <h2 className="text-xl font-bold mb-4">🔗 API Endpoints</h2>
              <div className="space-y-2 text-sm font-mono">
                <p><span className="text-green-400">GET</span> /api/v1/status</p>
                <p><span className="text-green-400">GET</span> /api/v1/personas</p>
                <p><span className="text-green-400">GET</span> /api/v1/laboratories</p>
                <p><span className="text-blue-400">POST</span> /api/v1/chat/orchestrated</p>
                <p><span className="text-blue-400">POST</span> /api/v1/query</p>
                <p><span className="text-green-400">GET</span> /api/v1/curiosity/*</p>
              </div>
              <a 
                href="http://localhost:8030/api/v1/docs" 
                target="_blank"
                className="inline-block mt-4 px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg transition-colors"
              >
                Open API Docs →
              </a>
            </div>

            <div className="bg-gray-800 rounded-xl border border-gray-700 p-6 md:col-span-2">
              <h2 className="text-xl font-bold mb-4">🌐 System Architecture</h2>
              <div className="grid grid-cols-4 gap-4 text-center">
                <div className="p-4 bg-blue-900/30 rounded-lg border border-blue-700">
                  <p className="text-2xl mb-2">🎭</p>
                  <p className="font-bold">14 Personas</p>
                  <p className="text-xs text-gray-400">Specialist Modules</p>
                </div>
                <div className="p-4 bg-green-900/30 rounded-lg border border-green-700">
                  <p className="text-2xl mb-2">🔬</p>
                  <p className="font-bold">23 Labs</p>
                  <p className="text-xs text-gray-400">City-Named</p>
                </div>
                <div className="p-4 bg-purple-900/30 rounded-lg border border-purple-700">
                  <p className="text-2xl mb-2">🔤</p>
                  <p className="font-bold">61 Layers</p>
                  <p className="text-xs text-gray-400">Alphabet Algebra</p>
                </div>
                <div className="p-4 bg-cyan-900/30 rounded-lg border border-cyan-700">
                  <p className="text-2xl mb-2">⚡</p>
                  <p className="font-bold">ASI Trinity</p>
                  <p className="text-xs text-gray-400">Alba+Albi+Jona</p>
                </div>
              </div>
            </div>
          </div>
        )}

      </main>

      {/* Footer */}
      <footer className="mt-12 py-6 border-t border-gray-800 text-center text-gray-500 text-sm">
        <p>© 2025 Kloud Cloud • Ocean Core v4.0.0 • By Ledjan Ahmati</p>
      </footer>
    </div>
  )
}

