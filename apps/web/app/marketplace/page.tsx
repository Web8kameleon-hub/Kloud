'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'

interface PricingPlan {
  name: string
  price: number
  period: string
  features: string[]
  limits: {
    requests: string
    storage: string
    support: string
  }
  popular?: boolean
  cta: string
}

const plans: PricingPlan[] = [
  {
    name: 'Free',
    price: 0,
    period: 'forever',
    features: [
      'Basic API Access',
      'Demo Endpoints',
      'Community Support',
      'Public Documentation'
    ],
    limits: {
      requests: '50/day',
      storage: '100MB',
      support: 'Community'
    },
    cta: 'Get Started Free'
  },
  {
    name: 'Pro',
    price: 29,
    period: '/month',
    features: [
      'Full API Access',
      'EEG Processing',
      'Audio Synthesis',
      'Brain-Sync Engine',
      'Priority Support',
      'Webhook Notifications'
    ],
    limits: {
      requests: '5,000/day',
      storage: '10GB',
      support: 'Email 24h'
    },
    popular: true,
    cta: 'Start Pro Trial'
  },
  {
    name: 'Enterprise',
    price: 199,
    period: '/month',
    features: [
      'Unlimited API Access',
      'Distributed Nodes',
      'Real-time Analytics',
      'Custom Integrations',
      'Dedicated Support',
      'SLA 99.9%',
      'On-premise Option',
      'White-label Ready'
    ],
    limits: {
      requests: '50,000/day',
      storage: '1TB',
      support: 'Phone 24/7'
    },
    cta: 'Contact Sales'
  }
]

const apiCategories = [
  {
    name: 'Core System',
    icon: '⚡',
    endpoints: 5,
    description: 'Health, status, and system monitoring',
    basePath: '/api/status',
    docsUrl: '/docs#core'
  },
  {
    name: 'Brain Engine',
    icon: '🧠',
    endpoints: 8,
    description: 'Neural processing, harmony analysis, brain-sync',
    basePath: '/api/brain',
    docsUrl: '/docs#brain'
  },
  {
    name: 'Audio Processing',
    icon: '🎵',
    endpoints: 7,
    description: 'Binaural beats, spectrum analysis, brain-sync audio',
    basePath: '/api/audio',
    docsUrl: '/docs#audio'
  },
  {
    name: 'EEG Analysis',
    icon: '📊',
    endpoints: 6,
    description: 'Signal processing, frequency bands, coherence',
    basePath: '/api/eeg',
    docsUrl: '/docs#eeg'
  },
  {
    name: 'ASI Trinity',
    icon: '🔺',
    endpoints: 12,
    description: 'Alba, Albi, Jona autonomous systems',
    basePath: '/api/alba',
    docsUrl: '/docs#asi'
  },
  {
    name: 'Ocean Chat',
    icon: '🌊',
    endpoints: 4,
    description: 'AI chat, streaming responses, context',
    basePath: '/ocean',
    docsUrl: '/docs#ocean'
  },
  {
    name: 'Zürich Engine',
    icon: '🎯',
    endpoints: 2,
    description: '9-stage deterministic reasoning, no AI randomness',
    basePath: '/zurich',
    docsUrl: '/docs#zurich'
  },
  {
    name: 'Trinity Debate',
    icon: '🎭',
    endpoints: 2,
    description: '5 AI personas debate any topic',
    basePath: '/debate',
    docsUrl: '/docs#debate'
  },
  {
    name: 'Billing',
    icon: '💳',
    endpoints: 8,
    description: 'Stripe, PayPal, SEPA payments',
    basePath: '/api/billing',
    docsUrl: '/docs#billing'
  },
  {
    name: 'Reporting',
    icon: '📈',
    endpoints: 6,
    description: 'Excel export, dashboards, metrics',
    basePath: '/api/reporting',
    docsUrl: '/docs#reporting'
  }
]

export default function MarketplacePage() {
  const [activeTab, setActiveTab] = useState<'overview' | 'pricing' | 'docs' | 'sdks'>('overview')
  const [copiedKey, setCopiedKey] = useState(false)
  const [demoApiKey, setDemoApiKey] = useState('pk_demo_loading')

  // Generate demo key client-side with crypto API
  useEffect(() => {
    if (typeof window !== 'undefined' && window.crypto) {
      setDemoApiKey('pk_demo_' + crypto.randomUUID().replace(/-/g, '').substring(0, 13))
    }
  }, [])

  const copyApiKey = () => {
    navigator.clipboard.writeText(demoApiKey)
    setCopiedKey(true)
    setTimeout(() => setCopiedKey(false), 2000)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <header className="border-b border-slate-700 bg-slate-900/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-r from-blue-800 to-violet-500 rounded-lg flex items-center justify-center text-white font-bold text-xl">
              C
            </div>
            <div>
              <h1 className="text-white font-bold text-xl">Kloud Cloud</h1>
              <p className="text-slate-400 text-xs">API Marketplace</p>
            </div>
          </div>
          <nav className="flex gap-6">
            <Link href="/modules" className="text-slate-300 hover:text-white transition">
              Dashboard
            </Link>
            <a href="#docs" className="text-slate-300 hover:text-white transition">
              Documentation
            </a>
            <a href="#pricing" className="text-slate-300 hover:text-white transition">
              Pricing
            </a>
            <button className="bg-blue-900 hover:bg-blue-800 text-white px-4 py-2 rounded-lg transition">
              Get API Key
            </button>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20 px-6">
        <div className="max-w-7xl mx-auto text-center">
          <div className="inline-block bg-blue-800/10 border border-blue-800/30 text-blue-700 px-4 py-1 rounded-full text-sm mb-6">
            🚀 70+ Production-Ready Endpoints
          </div>
          <h1 className="text-5xl md:text-6xl font-bold text-white mb-6">
            Neural-Audio APIs for
            <span className="bg-gradient-to-r from-blue-700 to-violet-400 bg-clip-text text-transparent"> Brain Technology</span>
          </h1>
          <p className="text-xl text-slate-400 max-w-3xl mx-auto mb-10">
            Enterprise-grade APIs for EEG processing, brain-sync audio generation, 
            neural pattern analysis, and real-time monitoring.
          </p>
          
          {/* Quick Demo */}
          <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6 max-w-2xl mx-auto mb-10">
            <div className="flex justify-between items-center mb-4">
              <span className="text-slate-400 text-sm">Try it now - Demo API Key</span>
              <button 
                onClick={copyApiKey}
                className="text-blue-700 hover:text-blue-600 text-sm flex items-center gap-2"
              >
                {copiedKey ? '✓ Copied!' : '📋 Copy Key'}
              </button>
            </div>
            <code className="block bg-slate-900 rounded-lg p-4 text-left overflow-x-auto">
              <span className="text-violet-400">curl</span>
              <span className="text-slate-300"> -X GET </span>
              <span className="text-blue-700">&quot;https://kloud.com/api/ping&quot;</span>
              <span className="text-slate-300"> \</span>
              <br />
              <span className="text-slate-300">  -H </span>
              <span className="text-yellow-400">&quot;X-API-Key: {demoApiKey}&quot;</span>
            </code>
          </div>

          <div className="flex justify-center gap-4">
            <button className="bg-gradient-to-r from-blue-900 to-violet-600 hover:from-blue-800 hover:to-violet-500 text-white px-8 py-4 rounded-lg font-semibold text-lg transition shadow-lg shadow-blue-800/25">
              Get Free API Key
            </button>
            <Link 
              href="/modules/protocol-kitchen"
              className="bg-slate-700 hover:bg-slate-600 text-white px-8 py-4 rounded-lg font-semibold text-lg transition border border-slate-600"
            >
              View Live Demo
            </Link>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="py-12 border-y border-slate-700 bg-slate-800/30">
        <div className="max-w-7xl mx-auto px-6 grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
          <div>
            <div className="text-4xl font-bold text-blue-700">70+</div>
            <div className="text-slate-400">API Endpoints</div>
          </div>
          <div>
            <div className="text-4xl font-bold text-violet-400">12</div>
            <div className="text-slate-400">Core Modules</div>
          </div>
          <div>
            <div className="text-4xl font-bold text-purple-400">99.9%</div>
            <div className="text-slate-400">Uptime SLA</div>
          </div>
          <div>
            <div className="text-4xl font-bold text-yellow-400">&lt;50ms</div>
            <div className="text-slate-400">Avg Response</div>
          </div>
        </div>
      </section>

      {/* API Categories */}
      <section className="py-20 px-6" id="docs">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-bold text-white text-center mb-4">API Categories</h2>
          <p className="text-slate-400 text-center mb-12 max-w-2xl mx-auto">
            Explore our comprehensive API suite organized by functionality
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {apiCategories.map((cat) => (
              <div 
                key={cat.name}
                className="bg-slate-800/50 border border-slate-700 rounded-xl p-6 hover:border-blue-800/50 transition cursor-pointer group"
              >
                <div className="text-4xl mb-4">{cat.icon}</div>
                <h3 className="text-white font-semibold text-lg mb-2 group-hover:text-blue-700 transition">
                  {cat.name}
                </h3>
                <p className="text-slate-400 text-sm mb-4">{cat.description}</p>
                <div className="flex justify-between items-center">
                  <span className="text-blue-700 text-sm">{cat.endpoints} endpoints</span>
                  <span className="text-slate-500 group-hover:text-blue-700 transition">→</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section className="py-20 px-6 bg-slate-800/30" id="pricing">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-bold text-white text-center mb-4">Simple, Transparent Pricing</h2>
          <p className="text-slate-400 text-center mb-12 max-w-2xl mx-auto">
            Start free, scale as you grow. All plans include core features.
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {plans.map((plan) => (
              <div 
                key={plan.name}
                className={`relative bg-slate-800 border rounded-2xl p-8 ${
                  plan.popular 
                    ? 'border-blue-800 shadow-lg shadow-blue-800/20' 
                    : 'border-slate-700'
                }`}
              >
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-gradient-to-r from-blue-800 to-violet-500 text-white text-sm px-4 py-1 rounded-full">
                    Most Popular
                  </div>
                )}
                
                <h3 className="text-2xl font-bold text-white mb-2">{plan.name}</h3>
                <div className="flex items-baseline gap-1 mb-6">
                  <span className="text-4xl font-bold text-white">€{plan.price}</span>
                  <span className="text-slate-400">{plan.period}</span>
                </div>
                
                <div className="space-y-4 mb-8">
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-400">Requests</span>
                    <span className="text-white font-medium">{plan.limits.requests}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-400">Storage</span>
                    <span className="text-white font-medium">{plan.limits.storage}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-400">Support</span>
                    <span className="text-white font-medium">{plan.limits.support}</span>
                  </div>
                </div>
                
                <ul className="space-y-3 mb-8">
                  {plan.features.map((feature) => (
                    <li key={feature} className="flex items-center gap-2 text-slate-300">
                      <span className="text-blue-700">✓</span>
                      {feature}
                    </li>
                  ))}
                </ul>
                
                <button 
                  className={`w-full py-3 rounded-lg font-semibold transition ${
                    plan.popular
                      ? 'bg-gradient-to-r from-blue-900 to-violet-600 hover:from-blue-800 hover:to-violet-500 text-white'
                      : 'bg-slate-700 hover:bg-slate-600 text-white border border-slate-600'
                  }`}
                >
                  {plan.cta}
                </button>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* SDK Section */}
      <section className="py-20 px-6">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-bold text-white text-center mb-4">Official SDKs</h2>
          <p className="text-slate-400 text-center mb-12 max-w-2xl mx-auto">
            Get started quickly with our official client libraries
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-4xl mx-auto">
            {[
              { name: 'TypeScript', icon: '🔷', cmd: 'npm install @kloud/sdk' },
              { name: 'Python', icon: '🐍', cmd: 'pip install kloud-sdk' },
              { name: 'Go', icon: '🔵', cmd: 'go get kloud.com/sdk' },
              { name: 'cURL', icon: '📟', cmd: 'curl -X GET ...' }
            ].map((sdk) => (
              <div key={sdk.name} className="bg-slate-800/50 border border-slate-700 rounded-xl p-6 text-center">
                <div className="text-4xl mb-3">{sdk.icon}</div>
                <h3 className="text-white font-semibold mb-2">{sdk.name}</h3>
                <code className="text-xs text-slate-400 bg-slate-900 px-2 py-1 rounded">
                  {sdk.cmd}
                </code>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Code Examples */}
      <section className="py-20 px-6 bg-slate-800/30">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-white text-center mb-12">Quick Start</h2>
          
          <div className="bg-slate-900 rounded-xl overflow-hidden border border-slate-700">
            <div className="flex border-b border-slate-700">
              {['TypeScript', 'Python', 'cURL'].map((lang) => (
                <button 
                  key={lang}
                  className="px-6 py-3 text-sm text-slate-400 hover:text-white hover:bg-slate-800 transition"
                >
                  {lang}
                </button>
              ))}
            </div>
            <pre className="p-6 overflow-x-auto">
              <code className="text-sm">
{`import { KloudClient } from '@kloud/sdk';

const client = new KloudClient({
  apiKey: 'your_api_key_here',
  baseUrl: 'https://kloud.com/api'
});

// Get system status
const status = await client.status();
console.log('System:', status.status, 'Uptime:', status.uptime);

// Analyze brain harmony
const analysis = await client.brain.analyzeHarmony({
  audioFile: 'sample.wav'
});
console.log('Harmony:', analysis.harmonics);

// Process EEG data
const eeg = await client.eeg.process({
  data: eegSignal,
  channels: ['Fp1', 'Fp2', 'F3', 'F4']
});
console.log('Alpha Power:', eeg.bands.alpha);`}
              </code>
            </pre>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-6 border-t border-slate-700">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-6">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-gradient-to-r from-blue-800 to-violet-500 rounded-lg flex items-center justify-center text-white font-bold">
              C
            </div>
            <span className="text-slate-400">© 2026 Kloud Cloud. Part of Webultrathinking Euroweb.</span>
          </div>
          <div className="flex gap-6 text-slate-400">
            <a href="#" className="hover:text-white transition">API Docs</a>
            <a href="#" className="hover:text-white transition">Status</a>
            <a href="#" className="hover:text-white transition">Terms</a>
            <a href="#" className="hover:text-white transition">Privacy</a>
          </div>
        </div>
      </footer>
    </div>
  )
}








