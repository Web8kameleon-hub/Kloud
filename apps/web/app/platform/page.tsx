'use client';

import Link from 'next/link';

/**
 * PLATFORM OVERVIEW PAGE - Technical Architecture
 * Shows the complete Kloud ecosystem
 */

export default function PlatformPage() {
  const modules = [
    { name: 'ASI Core', icon: '🧠', desc: 'Central intelligence orchestration', status: 'Live' },
    { name: 'Analytical', icon: '📡', desc: 'Network intelligence & monitoring', status: 'Live' },
    { name: 'Creative', icon: '⚡', desc: 'Neural processing engine', status: 'Live' },
    { name: 'Coordinator', icon: '🔗', desc: 'Data coordination layer', status: 'Live' },
    { name: 'Pulse', icon: '💓', desc: 'Real-time heartbeat monitor', status: 'Live' },
    { name: 'Grid', icon: '📊', desc: 'Distributed computing mesh', status: 'Live' },
    { name: 'Cycle', icon: '🔄', desc: 'Workflow automation engine', status: 'Live' },
    { name: 'Vision', icon: '👁️', desc: 'Computer vision processing', status: 'Live' },
    { name: 'Ocean', icon: '🌊', desc: 'Deep knowledge explorer', status: 'Live' },
    { name: 'Nebula', icon: '✨', desc: 'Creative generation suite', status: 'Live' },
    { name: 'Compass', icon: '🧭', desc: 'Navigation & recommendations', status: 'Live' },
    { name: 'Prism', icon: '🔮', desc: 'Data analysis & insights', status: 'Live' },
    { name: 'Harmony', icon: '🎵', desc: 'Audio processing engine', status: 'Live' },
    { name: 'Nexus', icon: '🌐', desc: 'Integration hub', status: 'Live' },
    { name: 'Chronicle', icon: '📜', desc: 'Historical data archive', status: 'Live' },
    { name: 'Web Reader', icon: '🌐', desc: 'Browse & search the web', status: 'Live' },
  ];

  const apiStats = [
    { label: 'Response Time', value: '~45ms', desc: 'P95 latency' },
    { label: 'Throughput', value: '50K+', desc: 'Requests/second' },
    { label: 'Availability', value: '99.97%', desc: 'Historical uptime' },
    { label: 'Endpoints', value: '150+', desc: 'REST + WebSocket' },
  ];

  const techStack = [
    { category: 'Backend', items: ['FastAPI', 'Python 3.12', 'PostgreSQL', 'Redis'] },
    { category: 'Frontend', items: ['Next.js 14', 'React 18', 'TypeScript', 'TailwindCSS'] },
    { category: 'Infrastructure', items: ['Docker', 'Kubernetes', 'Nginx', 'Cloudflare'] },
    { category: 'AI/ML', items: ['PyTorch', 'TensorFlow', 'Transformers', 'Custom Models'] },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 text-white">
      {/* Navigation */}
      <nav className="fixed top-0 w-full z-50 bg-slate-950/80 backdrop-blur-xl border-b border-slate-800">
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <Link href="/" className="flex items-center gap-3">
            <span className="text-2xl">🧠</span>
            <span className="text-xl font-bold">Kloud</span>
          </Link>
          <div className="flex items-center gap-6">
            <Link href="/why-kloud" className="text-gray-400 hover:text-white transition-colors">Why Kloud</Link>
            <Link href="/pricing" className="text-gray-400 hover:text-white transition-colors">Pricing</Link>
            <Link href="/modules" className="px-4 py-2 bg-violet-600 hover:bg-violet-500 rounded-lg transition-colors">
              Open Dashboard
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="pt-32 pb-16 px-6">
        <div className="max-w-6xl mx-auto text-center">
          <div className="inline-block px-4 py-2 rounded-full bg-slate-800 text-violet-400 text-sm font-medium mb-6">
            Platform Architecture
          </div>
          <h1 className="text-5xl font-bold mb-6">
            The Complete AI Infrastructure
          </h1>
          <p className="text-xl text-gray-400 max-w-3xl mx-auto">
            15+ specialized modules working in harmony, powered by the ASI Trinity core.
            Built for developers who need reliability at scale.
          </p>
        </div>
      </section>

      {/* API Stats */}
      <section className="py-12 px-6">
        <div className="max-w-5xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-6">
          {apiStats.map((stat) => (
            <div key={stat.label} className="p-6 rounded-xl bg-slate-800/50 border border-slate-700 text-center">
              <div className="text-3xl font-bold text-violet-400">{stat.value}</div>
              <div className="font-medium mt-1">{stat.label}</div>
              <div className="text-sm text-gray-500">{stat.desc}</div>
            </div>
          ))}
        </div>
      </section>

      {/* ASI Trinity Section */}
      <section className="py-20 px-6 bg-slate-900/50">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-4">The ASI Trinity</h2>
          <p className="text-gray-400 text-center mb-12 max-w-2xl mx-auto">
            Three synchronized artificial superintelligence systems working together
            to deliver unprecedented capabilities.
          </p>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="p-8 rounded-2xl bg-gradient-to-b from-violet-500/20 to-slate-800 border border-violet-500/30">
              <div className="text-4xl mb-4">📡</div>
              <h3 className="text-2xl font-bold text-violet-400 mb-2">ALBA</h3>
              <p className="text-gray-400 mb-4">Advanced Learning & Behavioral Analysis</p>
              <ul className="space-y-2 text-sm">
                <li className="flex items-center gap-2">
                  <span className="text-violet-400">◆</span> Real-time network monitoring
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-violet-400">◆</span> Anomaly detection
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-violet-400">◆</span> Predictive intelligence
                </li>
              </ul>
            </div>

            <div className="p-8 rounded-2xl bg-gradient-to-b from-purple-500/20 to-slate-800 border border-purple-500/30">
              <div className="text-4xl mb-4">⚡</div>
              <h3 className="text-2xl font-bold text-purple-400 mb-2">ALBI</h3>
              <p className="text-gray-400 mb-4">Adaptive Logic & Biometric Intelligence</p>
              <ul className="space-y-2 text-sm">
                <li className="flex items-center gap-2">
                  <span className="text-purple-400">◆</span> Neural processing
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-purple-400">◆</span> Pattern recognition
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-purple-400">◆</span> Adaptive learning
                </li>
              </ul>
            </div>

            <div className="p-8 rounded-2xl bg-gradient-to-b from-green-500/20 to-slate-800 border border-green-500/30">
              <div className="text-4xl mb-4">🔗</div>
              <h3 className="text-2xl font-bold text-green-400 mb-2">JONA</h3>
              <p className="text-gray-400 mb-4">Joint Orchestration & Neural Architecture</p>
              <ul className="space-y-2 text-sm">
                <li className="flex items-center gap-2">
                  <span className="text-green-400">◆</span> Data coordination
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-green-400">◆</span> System orchestration
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-green-400">◆</span> Cross-module sync
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* All Modules */}
      <section className="py-20 px-6">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-4">All Modules</h2>
          <p className="text-gray-400 text-center mb-12">
            Each module is a specialized AI system designed for specific tasks
          </p>

          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
            {modules.map((mod) => (
              <div
                key={mod.name}
                className="p-4 rounded-xl bg-slate-800/50 border border-slate-700 hover:border-violet-500/50 transition-colors"
              >
                <div className="text-3xl mb-2">{mod.icon}</div>
                <h3 className="font-semibold">{mod.name}</h3>
                <p className="text-xs text-gray-500 mb-2">{mod.desc}</p>
                <span className={`text-xs px-2 py-1 rounded-full ${
                  mod.status === 'Live' 
                    ? 'bg-green-500/20 text-green-400' 
                    : 'bg-yellow-500/20 text-yellow-400'
                }`}>
                  {mod.status}
                </span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Tech Stack */}
      <section className="py-20 px-6 bg-slate-900/50">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">Technology Stack</h2>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {techStack.map((stack) => (
              <div key={stack.category} className="p-6 rounded-xl bg-slate-800/50 border border-slate-700">
                <h3 className="font-semibold text-violet-400 mb-4">{stack.category}</h3>
                <ul className="space-y-2">
                  {stack.items.map((item) => (
                    <li key={item} className="text-gray-400 text-sm flex items-center gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-violet-500"></span>
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* API Example */}
      <section className="py-20 px-6">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-4">Developer-First API</h2>
          <p className="text-gray-400 text-center mb-8">
            Clean, RESTful APIs with comprehensive documentation
          </p>

          <div className="p-6 rounded-xl bg-slate-900 border border-slate-700 font-mono text-sm overflow-x-auto">
            <div className="text-gray-500 mb-2"># Quick start example</div>
            <pre className="text-green-400">{`curl -X GET "https://kloud.com/api/asi/health" \\
  -H "Authorization: Bearer your-api-key"

# Response:
{
  "status": "healthy",
  "trinity": {
    "alba": "operational",
    "albi": "operational", 
    "jona": "operational"
  },
  "latency_ms": 42,
  "timestamp": "2026-01-15T10:30:00Z"
}`}</pre>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-6 text-center">
        <h2 className="text-3xl font-bold mb-4">Ready to Build?</h2>
        <p className="text-gray-400 mb-8 max-w-xl mx-auto">
          Start with our free tier and scale when you&apos;re ready.
        </p>
        <div className="flex flex-wrap justify-center gap-4">
          <Link
            href="/modules"
            className="px-8 py-4 bg-violet-600 hover:bg-violet-500 rounded-xl font-semibold transition-colors"
          >
            Explore Modules
          </Link>
          <Link
            href="/pricing"
            className="px-8 py-4 bg-slate-800 hover:bg-slate-700 rounded-xl font-semibold transition-colors"
          >
            View Pricing
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-6 border-t border-slate-800">
        <div className="max-w-6xl mx-auto text-center text-gray-500 text-sm">
          © 2026 Kloud. All rights reserved. | 
          <Link href="/security" className="hover:text-violet-400 ml-2">Security</Link> | 
          <Link href="/status" className="hover:text-violet-400 ml-2">Status</Link> | 
          <Link href="/company" className="hover:text-violet-400 ml-2">Company</Link>
        </div>
      </footer>
    </div>
  );
}








