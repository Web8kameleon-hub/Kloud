'use client';

import Link from 'next/link';

/**
 * WHY KLOUD - Enterprise Value Proposition
 * SEO-optimized landing page for conversions
 */

export default function WhyKloudPage() {
  const competitors = [
    { name: 'Traditional Cloud', latency: '200-500ms', uptime: '99.5%', ai: '❌', price: '$$$' },
    { name: 'Generic AI APIs', latency: '300-800ms', uptime: '99.0%', ai: '✓', price: '$$$$' },
    { name: 'Kloud', latency: '< 100ms', uptime: '99.97%', ai: '✓✓✓', price: '$$' },
  ];

  const benefits = [
    {
      icon: '🧠',
      title: 'ASI Trinity Architecture',
      description: 'Three synchronized AI systems (ALBA, ALBI, JONA) working in harmony for unprecedented intelligence.',
      metric: '99.97% uptime'
    },
    {
      icon: '⚡',
      title: 'Sub-100ms Latency',
      description: 'Edge-optimized infrastructure delivers responses faster than human perception.',
      metric: '< 87ms p95'
    },
    {
      icon: '🔒',
      title: 'Enterprise Security',
      description: 'SOC2-ready infrastructure with end-to-end encryption and GDPR compliance.',
      metric: 'Zero breaches'
    },
    {
      icon: '📊',
      title: 'Real-Time Analytics',
      description: 'Live dashboards, custom reports, and predictive insights powered by neural processing.',
      metric: '125K+ daily insights'
    },
    {
      icon: '🌐',
      title: 'Global Edge Network',
      description: 'Distributed processing across multiple regions for consistent worldwide performance.',
      metric: '15+ edge locations'
    },
    {
      icon: '🔌',
      title: 'API-First Design',
      description: 'RESTful APIs, WebSocket streams, and SDKs for seamless integration.',
      metric: '50+ endpoints'
    }
  ];

  const useCases = [
    {
      industry: 'Healthcare & Biotech',
      icon: '🏥',
      description: 'EEG analysis, neural pattern recognition, patient monitoring systems',
      companies: 'Research labs, hospitals, biotech startups'
    },
    {
      industry: 'Financial Services',
      icon: '🏦',
      description: 'Real-time fraud detection, market analysis, algorithmic trading support',
      companies: 'Banks, fintech, hedge funds'
    },
    {
      industry: 'Industrial & IoT',
      icon: '🏭',
      description: 'Predictive maintenance, sensor data processing, anomaly detection',
      companies: 'Manufacturing, energy, logistics'
    },
    {
      industry: 'Research & Academia',
      icon: '🎓',
      description: 'Data synthesis, pattern analysis, research acceleration',
      companies: 'Universities, research institutes, think tanks'
    }
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
            <Link href="/platform" className="text-gray-400 hover:text-white transition-colors">Platform</Link>
            <Link href="/pricing" className="text-gray-400 hover:text-white transition-colors">Pricing</Link>
            <Link href="/modules" className="px-4 py-2 bg-violet-600 hover:bg-violet-500 rounded-lg transition-colors">
              Open Dashboard
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-6">
        <div className="max-w-5xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-violet-500/10 border border-violet-500/30 mb-8">
            <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse"></span>
            <span className="text-violet-300 text-sm">ASI Trinity Online • 99.97% Uptime</span>
          </div>
          
          <h1 className="text-5xl md:text-6xl font-bold mb-6">
            Why Leading Companies Choose{' '}
            <span className="bg-gradient-to-r from-violet-400 to-violet-400 bg-clip-text text-transparent">
              Kloud
            </span>
          </h1>
          
          <p className="text-xl text-gray-400 mb-10 max-w-3xl mx-auto">
            The only neural intelligence platform with three synchronized AI systems, 
            sub-100ms latency, and enterprise-grade reliability. Built for teams who 
            demand more than generic cloud solutions.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link 
              href="/modules"
              className="px-8 py-4 bg-gradient-to-r from-violet-600 to-violet-600 hover:from-violet-500 hover:to-violet-500 rounded-xl font-semibold text-lg transition-all shadow-lg shadow-violet-500/25"
            >
              Start Free Trial
            </Link>
            <Link 
              href="/developers"
              className="px-8 py-4 bg-slate-800 hover:bg-slate-700 rounded-xl font-semibold text-lg transition-colors border border-slate-700"
            >
              View Documentation
            </Link>
          </div>
        </div>
      </section>

      {/* Comparison Table */}
      <section className="py-20 px-6 bg-slate-900/50">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-4">How We Compare</h2>
          <p className="text-gray-400 text-center mb-12">See why enterprises are switching to Kloud</p>
          
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-700">
                  <th className="text-left py-4 px-6 text-gray-400 font-medium">Platform</th>
                  <th className="text-center py-4 px-6 text-gray-400 font-medium">Latency</th>
                  <th className="text-center py-4 px-6 text-gray-400 font-medium">Uptime</th>
                  <th className="text-center py-4 px-6 text-gray-400 font-medium">AI Integration</th>
                  <th className="text-center py-4 px-6 text-gray-400 font-medium">Value</th>
                </tr>
              </thead>
              <tbody>
                {competitors.map((comp, i) => (
                  <tr 
                    key={comp.name} 
                    className={`border-b border-slate-800 ${i === 2 ? 'bg-violet-500/10' : ''}`}
                  >
                    <td className="py-4 px-6 font-medium">
                      {i === 2 && <span className="mr-2">🏆</span>}
                      {comp.name}
                    </td>
                    <td className="text-center py-4 px-6">{comp.latency}</td>
                    <td className="text-center py-4 px-6">{comp.uptime}</td>
                    <td className="text-center py-4 px-6">{comp.ai}</td>
                    <td className="text-center py-4 px-6">{comp.price}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* Benefits Grid */}
      <section className="py-20 px-6">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-4">Enterprise-Grade Capabilities</h2>
          <p className="text-gray-400 text-center mb-12">Everything you need to build intelligent applications</p>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {benefits.map((benefit) => (
              <div 
                key={benefit.title}
                className="p-6 rounded-2xl bg-slate-800/50 border border-slate-700 hover:border-violet-500/50 transition-colors"
              >
                <div className="text-4xl mb-4">{benefit.icon}</div>
                <h3 className="text-xl font-semibold mb-2">{benefit.title}</h3>
                <p className="text-gray-400 mb-4">{benefit.description}</p>
                <div className="inline-flex px-3 py-1 rounded-full bg-violet-500/20 text-violet-300 text-sm">
                  {benefit.metric}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Use Cases */}
      <section className="py-20 px-6 bg-slate-900/50">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-4">Built for Your Industry</h2>
          <p className="text-gray-400 text-center mb-12">Trusted by teams across diverse sectors</p>
          
          <div className="grid md:grid-cols-2 gap-6">
            {useCases.map((uc) => (
              <div 
                key={uc.industry}
                className="p-6 rounded-2xl bg-gradient-to-br from-slate-800 to-slate-800/50 border border-slate-700"
              >
                <div className="flex items-center gap-3 mb-4">
                  <span className="text-3xl">{uc.icon}</span>
                  <h3 className="text-xl font-semibold">{uc.industry}</h3>
                </div>
                <p className="text-gray-300 mb-3">{uc.description}</p>
                <p className="text-sm text-gray-500">{uc.companies}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl font-bold mb-6">
            Ready to Experience the Difference?
          </h2>
          <p className="text-xl text-gray-400 mb-10">
            Join hundreds of teams already using Kloud to build smarter applications.
            Start free, scale when ready.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link 
              href="/modules"
              className="px-8 py-4 bg-gradient-to-r from-violet-600 to-violet-600 hover:from-violet-500 hover:to-violet-500 rounded-xl font-semibold text-lg transition-all"
            >
              Start Building Today
            </Link>
            <Link 
              href="mailto:support@kloud.com"
              className="px-8 py-4 bg-slate-800 hover:bg-slate-700 rounded-xl font-semibold text-lg transition-colors"
            >
              Contact Sales
            </Link>
          </div>
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








