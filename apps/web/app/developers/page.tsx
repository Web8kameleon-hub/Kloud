'use client'

import Link from 'next/link'
import { useState, useCallback, useRef, useEffect } from 'react'

/* ──────────────────────────────────────────────
   REAL API endpoints that exist on production
   All routes go through Next.js /api/* proxy
   ────────────────────────────────────────────── */
const liveEndpoints = {
  core: [
    { method: 'GET',  path: '/api',               desc: 'API info & endpoint list' },
    { method: 'GET',  path: '/api/ping',           desc: 'Health ping' },
    { method: 'GET',  path: '/api/system-status',  desc: 'Full system status' },
  ],
  ocean: [
    { method: 'POST', path: '/api/ocean',            desc: 'Chat with Curiosity Ocean AI' },
    { method: 'POST', path: '/api/ocean/stream',     desc: 'Streaming AI chat' },
    { method: 'POST', path: '/api/ocean/vision',     desc: 'Image analysis (LLaVA)' },
    { method: 'POST', path: '/api/ocean/audio',      desc: 'Audio transcription (Whisper)' },
    { method: 'POST', path: '/api/ocean/document',   desc: 'Document analysis' },
    { method: 'GET',  path: '/api/ocean/web-reader', desc: 'Web content reader' },
  ],
  proxy: [
    { method: 'GET',  path: '/api/proxy/health',             desc: 'Backend health' },
    { method: 'GET',  path: '/api/proxy/system-metrics',     desc: 'System metrics (CPU, RAM, disk)' },
    { method: 'GET',  path: '/api/proxy/docker-stats',       desc: 'Docker container stats' },
    { method: 'GET',  path: '/api/proxy/docker-containers',  desc: 'Container list' },
    { method: 'GET',  path: '/api/proxy/core-health',        desc: 'Core services health' },
    { method: 'GET',  path: '/api/proxy/marketplace-health', desc: 'Marketplace status' },
  ],
  reporting: [
    { method: 'GET',  path: '/api/proxy/reporting-dashboard',     desc: 'Dashboard metrics' },
    { method: 'GET',  path: '/api/proxy/reporting-errors',        desc: 'Error logs' },
    { method: 'GET',  path: '/api/proxy/reporting-error-summary', desc: 'Error summary' },
    { method: 'GET',  path: '/api/proxy/reporting-export-excel',  desc: 'Export to Excel' },
    { method: 'GET',  path: '/api/proxy/reporting-export-pptx',   desc: 'Export to PowerPoint' },
  ],
  user: [
    { method: 'GET',  path: '/api/proxy/user-summary',      desc: 'User summary' },
    { method: 'GET',  path: '/api/proxy/user-metrics',      desc: 'User metrics' },
    { method: 'POST', path: '/api/proxy/user-metrics',      desc: 'Submit user metrics' },
    { method: 'GET',  path: '/api/proxy/user-data-sources', desc: 'User data sources' },
    { method: 'POST', path: '/api/proxy/user-data-sources', desc: 'Add data source' },
    { method: 'GET',  path: '/api/user/profile',            desc: 'User profile' },
  ],
  billing: [
    { method: 'POST', path: '/api/billing/checkout',          desc: 'Create checkout session' },
    { method: 'GET',  path: '/api/billing/subscription',      desc: 'Subscription status' },
    { method: 'GET',  path: '/api/billing/invoices',          desc: 'Invoice history' },
    { method: 'GET',  path: '/api/billing/payment-methods',   desc: 'Payment methods' },
    { method: 'POST', path: '/api/billing/billing-address',   desc: 'Update billing address' },
  ],
  engines: [
    { method: 'GET',  path: '/api/alba/metrics',       desc: 'ALBA engine metrics' },
    { method: 'GET',  path: '/api/albi/metrics',       desc: 'ALBI engine metrics' },
    { method: 'GET',  path: '/api/asi-status',         desc: 'ASI Trinity status' },
    { method: 'POST', path: '/api/chat',               desc: 'General chat endpoint' },
    { method: 'GET',  path: '/api/neural-symphony',    desc: 'Neural Symphony status' },
    { method: 'GET',  path: '/api/jona/metrics',       desc: 'JONA engine metrics' },
  ],
} as const

type CategoryKey = keyof typeof liveEndpoints

const apiCategories: { id: CategoryKey; icon: string; title: string; description: string; color: string }[] = [
  { id: 'core',      icon: '⚡', title: 'Core System',       description: 'Health, status, and system information',               color: 'from-emerald-500 to-teal-500' },
  { id: 'ocean',     icon: '🧠', title: 'Curiosity Ocean',   description: 'AI chat, vision, audio & document analysis',          color: 'from-cyan-500 to-blue-500' },
  { id: 'proxy',     icon: '📡', title: 'Infrastructure',     description: 'System metrics, Docker, and service health',          color: 'from-violet-500 to-purple-500' },
  { id: 'reporting', icon: '📊', title: 'Reporting',          description: 'Dashboards, error tracking, and exports',             color: 'from-amber-500 to-orange-500' },
  { id: 'user',      icon: '👤', title: 'User & Data',        description: 'Profiles, metrics, and data source management',       color: 'from-pink-500 to-rose-500' },
  { id: 'billing',   icon: '💳', title: 'Billing',            description: 'Subscriptions, invoices, and payment methods',        color: 'from-green-500 to-emerald-500' },
  { id: 'engines',   icon: '🔥', title: 'Engine Fleet',       description: 'ALBA, ALBI, ASI, JONA & Neural Symphony',            color: 'from-red-500 to-orange-500' },
]

const totalEndpoints = Object.values(liveEndpoints).reduce((s, arr) => s + arr.length, 0)

/* ── Pricing and usage billing model ── */
const pricingPlans = [
  {
    name: 'Starter',
    price: '€0',
    period: '',
    requests: '250 events / month',
    support: 'Community',
    features: ['Core status endpoints', 'Dashboard metrics', 'Email login', 'Developer docs'],
    cta: 'Start Free',
    ctaLink: '/sign-up',
    popular: false,
  },
  {
    name: 'Usage-Based API',
    price: '€0.002',
    period: '/request',
    requests: 'Metered monthly',
    support: 'Priority email',
    features: ['API request metering', 'Ocean / vision / audio units', 'Usage metrics export', 'Stripe billing integration', 'Email + phone auth ready'],
    cta: 'Enable Metered Billing',
    ctaLink: '/modules/account',
    popular: true,
  },
  {
    name: 'Enterprise',
    price: 'Custom',
    period: '',
    requests: 'Dedicated limits',
    support: 'Dedicated',
    features: ['Contract pricing', 'Custom meter definitions', 'Private infrastructure', 'SLA guarantee', 'Advanced auth and compliance'],
    cta: 'Contact Sales',
    ctaLink: 'mailto:enterprise@kloud.com',
    popular: false,
  },
]

const usageMetrics = [
  { label: 'api_request', unit: '1 HTTP request', price: '€0.002' },
  { label: 'ocean_chat', unit: '1 generated response', price: '€0.01' },
  { label: 'vision_job', unit: '1 image/document analysis', price: '€0.03' },
  { label: 'audio_job', unit: '1 transcription minute', price: '€0.015' },
  { label: 'export_job', unit: '1 reporting export', price: '€0.05' },
]

const authModes = [
  'Email login via Clerk',
  'Phone number + SMS login via Clerk',
  'Session-based browser auth',
  'Stripe-linked customer identity for billing flows',
]

/* ─────────────────────────────── Component ── */
export default function DevelopersPage() {
  const [activeCategory, setActiveCategory] = useState<CategoryKey>('core')
  const [activeTab, setActiveTab] = useState<'typescript' | 'python' | 'curl'>('curl')
  const [copied, setCopied] = useState<string | null>(null)
  const [liveResult, setLiveResult] = useState<string | null>(null)
  const [liveLoading, setLiveLoading] = useState(false)
  const [expandedEndpoint, setExpandedEndpoint] = useState<string | null>(null)
  const resultRef = useRef<HTMLPreElement>(null)

  const copy = useCallback((text: string, id: string) => {
    navigator.clipboard.writeText(text)
    setCopied(id)
    setTimeout(() => setCopied(null), 2000)
  }, [])

  /* Live API tester — actually calls the real endpoint */
  const testEndpoint = useCallback(async (method: string, path: string) => {
    setLiveLoading(true)
    setLiveResult(null)
    const key = `${method}:${path}`
    setExpandedEndpoint(key)
    try {
      const opts: RequestInit = { method, headers: { 'Accept': 'application/json' } }
      if (method === 'POST') {
        opts.headers = { ...opts.headers as Record<string,string>, 'Content-Type': 'application/json' }
        // Sensible defaults for POST endpoints
        if (path.includes('/ocean') && !path.includes('vision') && !path.includes('audio') && !path.includes('document')) {
          opts.body = JSON.stringify({ message: 'Hello from API playground', language: 'en' })
        } else {
          opts.body = JSON.stringify({})
        }
      }
      const start = performance.now()
      const res = await fetch(path, opts)
      const elapsed = Math.round(performance.now() - start)
      const contentType = res.headers.get('content-type') || ''
      let body: string
      if (contentType.includes('json')) {
        const json = await res.json()
        body = JSON.stringify(json, null, 2)
      } else {
        body = await res.text()
        if (body.length > 2000) body = body.slice(0, 2000) + '\n... (truncated)'
      }
      setLiveResult(`HTTP ${res.status} — ${elapsed}ms\n\n${body}`)
    } catch (err: unknown) {
      setLiveResult(`Error: ${err instanceof Error ? err.message : 'Network error'}`)
    } finally {
      setLiveLoading(false)
    }
  }, [])

  useEffect(() => {
    if (liveResult && resultRef.current) {
      resultRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
    }
  }, [liveResult])

  const codeExamples = {
    curl: `# Health check
curl -s https://kloud.com/api/ping

# System status
curl -s https://kloud.com/api/system-status | jq .

# Chat with Ocean AI
curl -X POST https://kloud.com/api/ocean \\
  -H "Content-Type: application/json" \\
  -d '{"message": "What is neural audio processing?", "language": "en"}'

# Streaming chat
curl -N -X POST https://kloud.com/api/ocean/stream \\
  -H "Content-Type: application/json" \\
  -d '{"message": "Explain EEG analysis", "language": "en"}'`,
    typescript: `// Kloud Cloud API — TypeScript
const BASE = 'https://kloud.com/api'

// Health check
const ping = await fetch(\`\${BASE}/ping\`)
console.log(await ping.json())
// → { status: "ok", service: "frontend", timestamp: "..." }

// Chat with Curiosity Ocean
const chat = await fetch(\`\${BASE}/ocean\`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: 'What is neural audio processing?',
    language: 'en'
  })
})
const result = await chat.json()
console.log(result.response)

// System metrics
const metrics = await fetch(\`\${BASE}/proxy/system-metrics\`)
const { data } = await metrics.json()
console.log(\`CPU: \${data.cpu_percent}%, RAM: \${data.memory_percent}%\`)`,
    python: `import requests

BASE = "https://kloud.com/api"

# Health check
r = requests.get(f"{BASE}/ping")
print(r.json())
# → {"status": "ok", "service": "frontend", "timestamp": "..."}

# Chat with Curiosity Ocean
r = requests.post(f"{BASE}/ocean", json={
    "message": "What is neural audio processing?",
    "language": "en"
})
print(r.json()["response"])

# System metrics
r = requests.get(f"{BASE}/proxy/system-metrics")
data = r.json()["data"]
print(f"CPU: {data['cpu_percent']}%, RAM: {data['memory_percent']}%")`,
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white">

      {/* ── Nav ── */}
      <nav className="fixed top-0 w-full z-50 bg-slate-950/80 backdrop-blur-xl border-b border-slate-800/50">
        <div className="max-w-7xl mx-auto flex items-center justify-between h-16 px-6">
          <Link href="/" className="flex items-center gap-3">
            <div className="w-8 h-8 bg-gradient-to-br from-emerald-400 to-teal-500 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">C</span>
            </div>
            <span className="font-semibold text-lg">Kloud <span className="text-slate-500 font-normal">Developers</span></span>
          </Link>
          <div className="hidden md:flex items-center gap-8 text-sm">
            <a href="#endpoints" className="text-slate-400 hover:text-white transition-colors">Endpoints</a>
            <a href="#playground" className="text-slate-400 hover:text-white transition-colors">Playground</a>
            <a href="#examples" className="text-slate-400 hover:text-white transition-colors">Examples</a>
            <a href="#pricing" className="text-slate-400 hover:text-white transition-colors">Pricing</a>
            <Link href="/sign-up" className="px-4 py-2 bg-emerald-500 hover:bg-emerald-600 rounded-lg text-white font-medium transition-colors text-sm">
              Get Started
            </Link>
          </div>
        </div>
      </nav>

      {/* ── Hero ── */}
      <section className="pt-32 pb-16 px-6">
        <div className="max-w-5xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-500/10 border border-emerald-500/20 rounded-full mb-8">
            <span className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse" />
            <span className="text-emerald-400 text-sm font-medium">{totalEndpoints} Live Endpoints — All Verified</span>
          </div>

          <h1 className="text-5xl md:text-6xl font-bold mb-6 leading-tight">
            Build with{' '}
            <span className="bg-gradient-to-r from-emerald-400 to-teal-400 bg-clip-text text-transparent">
              Real APIs
            </span>
          </h1>
          <p className="text-xl text-slate-400 max-w-2xl mx-auto mb-10">
            AI chat, vision, audio, system monitoring, billing — every endpoint listed here works on production right now.
            No fake demos. No placeholder links.
          </p>

          {/* Quick live test */}
          <div className="max-w-2xl mx-auto bg-slate-900/60 border border-slate-800 rounded-2xl p-6 mb-8">
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm text-slate-400">Try it now — live from production</span>
              <span className="text-xs text-slate-600">kloud.com</span>
            </div>
            <div className="flex gap-3">
              <code className="flex-1 bg-slate-950 rounded-lg px-4 py-3 text-left text-sm text-emerald-400 font-mono">
                GET /api/ping
              </code>
              <button
                onClick={() => testEndpoint('GET', '/api/ping')}
                disabled={liveLoading}
                className="px-6 py-3 bg-emerald-500 hover:bg-emerald-600 disabled:opacity-50 rounded-lg text-white font-medium transition-colors text-sm"
              >
                {liveLoading ? (
                  <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
                ) : 'Send'}
              </button>
            </div>
            {liveResult && expandedEndpoint === 'GET:/api/ping' && (
              <pre ref={resultRef} className="mt-4 bg-slate-950 rounded-lg p-4 text-left text-xs text-slate-300 font-mono overflow-x-auto max-h-48 overflow-y-auto whitespace-pre-wrap">
                {liveResult}
              </pre>
            )}
          </div>
        </div>
      </section>

      {/* ── API Endpoints (real, interactive) ── */}
      <section id="endpoints" className="py-20 px-6 bg-slate-900/40">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">API Endpoints</h2>
            <p className="text-slate-400">Every endpoint below is live. Click any to see the real response.</p>
          </div>

          {/* Category tabs */}
          <div className="flex flex-wrap justify-center gap-2 mb-10">
            {apiCategories.map((cat) => (
              <button
                key={cat.id}
                onClick={() => { setActiveCategory(cat.id); setExpandedEndpoint(null); setLiveResult(null) }}
                className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium transition-all ${
                  activeCategory === cat.id
                    ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40'
                    : 'bg-slate-800/50 text-slate-400 border border-slate-700/50 hover:text-white hover:bg-slate-800'
                }`}
              >
                <span>{cat.icon}</span>
                {cat.title}
                <span className="text-xs opacity-60">{liveEndpoints[cat.id].length}</span>
              </button>
            ))}
          </div>

          {/* Endpoint list */}
          <div id="playground" className="max-w-4xl mx-auto space-y-2">
            {liveEndpoints[activeCategory].map((ep) => {
              const key = `${ep.method}:${ep.path}`
              const isExpanded = expandedEndpoint === key
              return (
                <div key={key} className="bg-slate-900/80 border border-slate-800 rounded-xl overflow-hidden">
                  <div className="flex items-center gap-4 px-5 py-4">
                    <span className={`font-mono text-xs font-bold px-2.5 py-1 rounded-md ${
                      ep.method === 'GET'
                        ? 'bg-blue-500/20 text-blue-400'
                        : 'bg-amber-500/20 text-amber-400'
                    }`}>
                      {ep.method}
                    </span>
                    <code className="font-mono text-sm text-slate-300 flex-1">{ep.path}</code>
                    <span className="hidden sm:block text-xs text-slate-500 flex-shrink-0">{ep.desc}</span>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => copy(`curl ${ep.method === 'POST' ? '-X POST ' : '-s '}https://kloud.com${ep.path}${ep.method === 'POST' ? ' -H "Content-Type: application/json" -d \'{"message":"test"}\'': ''}`, key + '-copy')}
                        className="p-2 text-slate-500 hover:text-white transition-colors"
                        title="Copy cURL"
                      >
                        {copied === key + '-copy' ? (
                          <svg className="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                        ) : (
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" /></svg>
                        )}
                      </button>
                      <button
                        onClick={() => testEndpoint(ep.method, ep.path)}
                        disabled={liveLoading}
                        className="px-3 py-1.5 bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30 disabled:opacity-50 rounded-lg text-xs font-medium transition-colors"
                      >
                        {liveLoading && isExpanded ? '...' : 'Try'}
                      </button>
                    </div>
                  </div>
                  {isExpanded && liveResult && (
                    <div className="border-t border-slate-800">
                      <pre ref={resultRef} className="p-5 text-xs text-slate-300 font-mono overflow-x-auto max-h-80 overflow-y-auto whitespace-pre-wrap bg-slate-950/50">
                        {liveResult}
                      </pre>
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </div>
      </section>

      {/* ── Code Examples ── */}
      <section id="examples" className="py-20 px-6">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Code Examples</h2>
            <p className="text-slate-400">Copy-paste ready. Every example uses real production URLs.</p>
          </div>

          <div className="bg-slate-900 rounded-2xl border border-slate-800 overflow-hidden">
            <div className="flex items-center justify-between px-5 py-3 border-b border-slate-800">
              <div className="flex gap-2">
                {(['curl', 'typescript', 'python'] as const).map((tab) => (
                  <button
                    key={tab}
                    onClick={() => setActiveTab(tab)}
                    className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors capitalize ${
                      activeTab === tab ? 'bg-emerald-500 text-white' : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    {tab === 'curl' ? 'cURL' : tab === 'typescript' ? 'TypeScript' : 'Python'}
                  </button>
                ))}
              </div>
              <button
                onClick={() => copy(codeExamples[activeTab], 'code')}
                className="flex items-center gap-2 px-3 py-1.5 text-slate-400 hover:text-white text-sm transition-colors"
              >
                {copied === 'code' ? (
                  <><svg className="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg> Copied!</>
                ) : (
                  <><svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" /></svg> Copy</>
                )}
              </button>
            </div>
            <pre className="p-6 overflow-x-auto">
              <code className={`text-sm font-mono leading-relaxed ${
                activeTab === 'curl' ? 'text-emerald-400' : activeTab === 'typescript' ? 'text-blue-400' : 'text-yellow-400'
              }`}>
                {codeExamples[activeTab]}
              </code>
            </pre>
          </div>
        </div>
      </section>

      {/* ── Pricing ── */}
      <section id="pricing" className="py-20 px-6 bg-slate-900/40">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Usage Pricing</h2>
            <p className="text-slate-400">Meter requests and bill only for the units you actually consume.</p>
          </div>

          <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
            {pricingPlans.map((plan) => (
              <div
                key={plan.name}
                className={`relative p-8 rounded-2xl border transition-all ${
                  plan.popular
                    ? 'bg-gradient-to-b from-emerald-500/10 to-transparent border-emerald-500/50 shadow-lg shadow-emerald-500/5'
                    : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'
                }`}
              >
                {plan.popular && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-4 py-1 bg-emerald-500 text-white text-xs font-medium rounded-full">
                    Most Popular
                  </div>
                )}
                <div className="text-center mb-8">
                  <h3 className="text-xl font-bold mb-3">{plan.name}</h3>
                  <div className="flex items-baseline justify-center gap-1">
                    <span className="text-4xl font-bold">{plan.price}</span>
                    <span className="text-slate-400">{plan.period}</span>
                  </div>
                  <div className="mt-2 text-sm text-slate-500">{plan.requests} requests</div>
                </div>

                <ul className="space-y-3 mb-8">
                  {plan.features.map((feat) => (
                    <li key={feat} className="flex items-center gap-3 text-sm text-slate-300">
                      <svg className="w-4 h-4 text-emerald-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      {feat}
                    </li>
                  ))}
                </ul>

                {plan.ctaLink.startsWith('mailto:') ? (
                  <a
                    href={plan.ctaLink}
                    className="block w-full py-3 text-center font-medium rounded-lg bg-slate-800 hover:bg-slate-700 text-white border border-slate-700 transition-colors"
                  >
                    {plan.cta}
                  </a>
                ) : (
                  <Link
                    href={plan.ctaLink}
                    className={`block w-full py-3 text-center font-medium rounded-lg transition-colors ${
                      plan.popular
                        ? 'bg-emerald-500 hover:bg-emerald-600 text-white'
                        : 'bg-slate-800 hover:bg-slate-700 text-white border border-slate-700'
                    }`}
                  >
                    {plan.cta}
                  </Link>
                )}
              </div>
            ))}
          </div>

          <div className="grid lg:grid-cols-2 gap-6 max-w-5xl mx-auto mt-10">
            <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-8">
              <h3 className="text-xl font-bold mb-4">Billable Metrics</h3>
              <div className="space-y-3">
                {usageMetrics.map((metric) => (
                  <div key={metric.label} className="flex items-center justify-between gap-4 border-b border-slate-800 pb-3 last:border-b-0 last:pb-0">
                    <div>
                      <div className="font-mono text-emerald-400 text-sm">{metric.label}</div>
                      <div className="text-slate-400 text-sm">{metric.unit}</div>
                    </div>
                    <div className="text-white font-semibold">{metric.price}</div>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-8">
              <h3 className="text-xl font-bold mb-4">Stripe Product Setup</h3>
              <ol className="space-y-3 text-sm text-slate-300 list-decimal pl-5">
                <li>Create one metered product in Stripe for each metric family you want to bill.</li>
                <li>Use usage records or meter events named like <span className="font-mono text-emerald-400">api_request</span> and <span className="font-mono text-emerald-400">ocean_chat</span>.</li>
                <li>Store product/price IDs in app env and connect checkout through <span className="font-mono text-emerald-400">/api/billing/checkout</span>.</li>
                <li>Emit usage from your API gateway or worker layer, then reconcile invoices through Stripe billing webhooks.</li>
              </ol>
            </div>
          </div>
        </div>
      </section>

      <section className="py-20 px-6">
        <div className="max-w-5xl mx-auto grid lg:grid-cols-2 gap-6">
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-8">
            <h2 className="text-2xl font-bold mb-4">Authentication Modes</h2>
            <p className="text-slate-400 mb-6">Login is wired through Clerk in the web app. Phone/SMS is a configuration step, not a fake UI promise.</p>
            <ul className="space-y-3">
              {authModes.map((mode) => (
                <li key={mode} className="flex items-center gap-3 text-sm text-slate-300">
                  <svg className="w-4 h-4 text-emerald-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                  {mode}
                </li>
              ))}
            </ul>
          </div>

          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-8">
            <h2 className="text-2xl font-bold mb-4">Company & Owner</h2>
            <div className="space-y-3 text-sm text-slate-300">
              <div><span className="text-slate-500">Brand:</span> Kloud Cloud</div>
              <div><span className="text-slate-500">Legal entity:</span> ABA GmbH</div>
              <div><span className="text-slate-500">Owner:</span> Ledjan Ahmati</div>
              <div><span className="text-slate-500">Support:</span> support@kloud.com</div>
              <div><span className="text-slate-500">Developers:</span> https://kloud.com/developers</div>
            </div>
          </div>
        </div>
      </section>

      {/* ── FAQ ── */}
      <section className="py-20 px-6">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">FAQ</h2>
          <div className="space-y-4">
            {[
              { q: 'How do I get started?', a: 'Sign up for a free account at kloud.com/sign-up. You can start calling public endpoints immediately — no API key required for read-only status and health endpoints.' },
              { q: 'Do these APIs actually work?', a: 'Yes. Every endpoint listed on this page is live on production. Click "Try" next to any endpoint above to see the real response.' },
              { q: 'What AI models power Ocean?', a: 'Curiosity Ocean uses Llama 3.1 8B for text, LLaVA for vision, and Faster-Whisper for audio transcription. All models run on our infrastructure — no external API calls.' },
              { q: 'Can I bill per usage instead of fixed tiers?', a: 'Yes. The platform supports metered billing. Track billable units such as api_request, ocean_chat, vision_job, audio_job, and export_job, then attach them to Stripe metered products.' },
              { q: 'How do I enable phone and SMS login?', a: 'Use Clerk as the identity provider and enable phone number sign-in plus SMS verification in the Clerk dashboard. The app UI already supports Clerk-based auth surfaces.' },
              { q: 'Can I upgrade or downgrade anytime?', a: 'Yes. Upgrades take effect immediately. Downgrades apply at the next billing cycle. All payments are processed through Stripe.' },
              { q: 'Is there an SDK?', a: 'SDKs are in development. For now, all endpoints work with any HTTP client — cURL, fetch, requests, axios, etc. See the code examples above.' },
              { q: 'Do you offer enterprise solutions?', a: 'Yes — custom API limits, dedicated infrastructure, SLA guarantees, and on-premise deployment. Contact enterprise@kloud.com.' },
            ].map((item) => (
              <div key={item.q} className="bg-slate-900/60 border border-slate-800 rounded-xl p-6">
                <h3 className="font-semibold mb-2">{item.q}</h3>
                <p className="text-slate-400 text-sm leading-relaxed">{item.a}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA ── */}
      <section className="py-20 px-6">
        <div className="max-w-4xl mx-auto">
          <div className="p-12 rounded-2xl bg-gradient-to-r from-emerald-500/10 to-teal-500/10 border border-emerald-500/20 text-center">
            <h2 className="text-3xl font-bold mb-4">Ready to Build?</h2>
            <p className="text-slate-400 mb-8 max-w-lg mx-auto">
              {totalEndpoints} production endpoints. AI chat, vision, audio, monitoring, billing — all live.
            </p>
            <div className="flex flex-wrap justify-center gap-4">
              <Link
                href="/sign-up"
                className="px-8 py-4 bg-emerald-500 hover:bg-emerald-600 text-white font-medium rounded-lg transition-colors"
              >
                Get Started Free
              </Link>
              <a
                href="#endpoints"
                className="px-8 py-4 bg-slate-800 text-white font-medium rounded-lg border border-slate-700 hover:bg-slate-700 transition-colors"
              >
                Explore Endpoints
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* ── Footer ── */}
      <footer className="py-8 px-6 border-t border-slate-800">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 bg-gradient-to-br from-emerald-400 to-teal-500 rounded flex items-center justify-center">
              <span className="text-white font-bold text-xs">C</span>
            </div>
            <span className="text-slate-500 text-sm">© 2026 Kloud Cloud · ABA GmbH</span>
          </div>
          <div className="flex gap-6 text-sm">
            <Link href="/terms" className="text-slate-500 hover:text-white transition-colors">Terms</Link>
            <Link href="/privacy" className="text-slate-500 hover:text-white transition-colors">Privacy</Link>
            <Link href="/status" className="text-slate-500 hover:text-white transition-colors">Status</Link>
            <a href="mailto:support@kloud.com" className="text-slate-500 hover:text-white transition-colors">Support</a>
          </div>
        </div>
      </footer>
    </div>
  )
}

