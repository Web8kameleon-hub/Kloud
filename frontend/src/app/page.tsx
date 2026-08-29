
'use client'

import Link from 'next/link'
import NatureHero from '../components/landing/NatureHero'
import LiveServicesPanel from '../components/landing/LiveServicesPanel'

export default function HomePage() {
  const modules = [
    { name: 'EEG Analysis', path: '/modules/eeg-analysis', icon: '🧠', status: 'active' },
    { name: 'Neural Synthesis', path: '/modules/neural-synthesis', icon: '⚡', status: 'active' },
    { name: 'Spectrum Analyzer', path: '/modules/spectrum-analyzer', icon: '📊', status: 'active' },
    { name: 'Neuroacoustic Converter', path: '/modules/neuroacoustic-converter', icon: '🔊', status: 'active' },
  ]

  return (
    <div className="min-h-screen text-white">
      {/* Hero (Nature + inspiring UI) */}
      <div className="mb-6">
        <NatureHero />
      </div>

      {/* Live Services (real-time from /api/backend-health) */}
      <div className="mb-10">
        <LiveServicesPanel />
      </div>

      {/* Quick Access Modules */}
      <div className="mb-12">
        <h2 className="text-2xl font-bold mb-6">🚀 Quick Access</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {modules.map((module) => (
            <Link
              key={module.path}
              href={module.path}
              className="bg-gray-800 hover:bg-gray-700 p-6 rounded-xl border border-gray-700 transition-all hover:scale-105"
            >
              <div className="text-3xl mb-3">{module.icon}</div>
              <div className="font-bold text-lg">{module.name}</div>
              <div className="text-xs text-green-400 mt-2">● {module.status}</div>
            </Link>
          ))}
        </div>
      </div>

      {/* System Components */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
        <div className="bg-gray-800 p-6 rounded-xl border border-gray-700">
          <h3 className="font-bold text-lg mb-4">🧠 Ocean Core</h3>
          <ul className="space-y-2 text-sm text-gray-400">
            <li>✅ Expert Personas</li>
            <li>✅ Laboratories</li>
            <li>✅ Auto-Learning Engine</li>
            <li>✅ Response Orchestrator</li>
          </ul>
          <a
            href="http://localhost:8030/api/docs"
            target="_blank"
            rel="noreferrer noopener"
            className="mt-4 inline-block text-blue-400 hover:text-blue-300 text-sm"
          >
            Open API Docs →
          </a>
        </div>

        <div className="bg-gray-800 p-6 rounded-xl border border-gray-700">
          <h3 className="font-bold text-lg mb-4">🔤 Alphabet Layers</h3>
          <ul className="space-y-2 text-sm text-gray-400">
            <li>✅ Greek: α-ω</li>
            <li>✅ Albanian: letters</li>
            <li>✅ Mathematical functions</li>
            <li>✅ Phonetic properties</li>
          </ul>
        </div>

        <div className="bg-gray-800 p-6 rounded-xl border border-gray-700">
          <h3 className="font-bold text-lg mb-4">⚡ ASI Trinity</h3>
          <ul className="space-y-2 text-sm text-gray-400">
            <li>✅ ALBA - EEG Processing</li>
            <li>✅ ALBI - Intelligence</li>
            <li>✅ JONA - Ethics & Coordination</li>
          </ul>
        </div>
      </div>

      {/* Links */}
      <div className="text-center py-8 border-t border-gray-700">
        <div className="flex justify-center gap-6 text-sm">
          <Link href="/modules" className="text-blue-400 hover:text-blue-300">
            All Modules
          </Link>
          <a href="https://kloud.com" target="_blank" rel="noreferrer noopener" className="text-purple-400 hover:text-purple-300">
            Kloud.com
          </a>
          <a href="https://clisonix.com" target="_blank" rel="noreferrer noopener" className="text-green-400 hover:text-green-300">
            clisonix.com
          </a>
        </div>
      </div>
    </div>
  )
}

