'use client'

import { useState } from 'react'

export default function OpenWebUIChat() {
  const [messages, setMessages] = useState([
    { id: 1, text: "Hello! I'm Kloud AI Assistant. How can I help you with EEG analysis, neural synthesis, or system monitoring?", sender: 'bot' }
  ])
  const [input, setInput] = useState('')

  const sendMessage = () => {
    if (input.trim()) {
      const newMessage = { id: Date.now(), text: input, sender: 'user' }
      setMessages(prev => [...prev, newMessage])
      setInput('')
      
      // Simulate AI response
      setTimeout(() => {
        const botResponse = { 
          id: Date.now(), 
          text: I understand you're asking about: "". Let me process this with our Kloud modules..., 
          sender: 'bot' 
        }
        setMessages(prev => [...prev, botResponse])
      }, 1000)
    }
  }

  return (
    <div className="min-h-screen bg-white flex">
      {/* Sidebar - Kloud Modules */}
      <div className="w-80 bg-gradient-to-b from-slate-900 to-blue-900 text-white p-6">
        <h1 className="text-2xl font-bold mb-2">?? Kloud</h1>
        <p className="text-gray-300 mb-6">AI Chat Interface</p>
        
        <div className="space-y-3">
          <div className="p-3 bg-green-500/20 rounded-lg border border-green-500/30">
            <div className="font-semibold">?? ALBI</div>
            <div className="text-sm text-gray-300">EEG Analysis</div>
          </div>
          <div className="p-3 bg-blue-500/20 rounded-lg border border-blue-500/30">
            <div className="font-semibold">?? ALBA</div>
            <div className="text-sm text-gray-300">Data Collection</div>
          </div>
          <div className="p-3 bg-purple-500/20 rounded-lg border border-purple-500/30">
            <div className="font-semibold">?? JONA</div>
            <div className="text-sm text-gray-300">Neural Synthesis</div>
          </div>
        </div>

        <div className="mt-8">
          <h3 className="font-semibold mb-3">Quick Actions</h3>
          <button className="w-full text-left p-2 hover:bg-white/10 rounded">
            ?? View EEG Analytics
          </button>
          <button className="w-full text-left p-2 hover:bg-white/10 rounded">
            ?? Start Neural Synthesis
          </button>
          <button className="w-full text-left p-2 hover:bg-white/10 rounded">
            ?? System Settings
          </button>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Messages */}
        <div className="flex-1 p-6 space-y-4 overflow-auto bg-gray-50">
          {messages.map((message) => (
            <div key={message.id} className={lex }>
              <div className={max-w-md px-4 py-3 rounded-2xl }>
                <div className="flex items-center space-x-2 mb-1">
                  {message.sender === 'bot' && <span className="text-lg">??</span>}
                  <span className="text-sm font-medium">
                    {message.sender === 'user' ? 'You' : 'Kloud AI'}
                  </span>
                </div>
                <div className="text-sm">{message.text}</div>
              </div>
            </div>
          ))}
        </div>

        {/* Input Area */}
        <div className="border-t bg-white p-6">
          <div className="flex space-x-4 max-w-4xl mx-auto">
            <input
              type="text"
              placeholder="Ask about EEG data analysis, neural synthesis, ALBI patterns, or system status..."
              className="flex-1 p-4 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
            />
            <button 
              onClick={sendMessage}
              className="px-8 py-4 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition flex items-center space-x-2"
            >
              <span>Send</span>
              <span>??</span>
            </button>
          </div>
          <div className="text-center mt-3 text-sm text-gray-500">
            Ask about: EEG Analysis � Neural Synthesis � Data Streams � System Status
          </div>
        </div>
      </div>
    </div>
  )
}

