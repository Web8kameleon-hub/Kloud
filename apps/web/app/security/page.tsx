'use client';

import Link from 'next/link';

/**
 * SECURITY PAGE - Trust & Compliance
 * Enterprise security commitments
 */

export default function SecurityPage() {
  const certifications = [
    { name: 'SOC 2 Type II', icon: '🛡️', desc: 'Audited security controls', status: 'Planned 2026' },
    { name: 'GDPR', icon: '🇪🇺', desc: 'EU data protection ready', status: 'Compliant' },
    { name: 'ISO 27001', icon: '📋', desc: 'Information security management', status: 'Planned' },
    { name: 'HIPAA', icon: '🏥', desc: 'Healthcare data ready', status: 'On Request' },
  ];

  const securityFeatures = [
    {
      title: 'Encryption at Rest',
      desc: 'All data encrypted using AES-256 encryption',
      icon: '🔐'
    },
    {
      title: 'Encryption in Transit',
      desc: 'TLS 1.3 for all API communications',
      icon: '🔒'
    },
    {
      title: 'Zero Trust Architecture',
      desc: 'Every request verified, nothing implicitly trusted',
      icon: '🎯'
    },
    {
      title: 'API Key Security',
      desc: 'Hashed keys, automatic rotation, scope restrictions',
      icon: '🔑'
    },
    {
      title: 'Rate Limiting',
      desc: 'Intelligent throttling to prevent abuse',
      icon: '⚡'
    },
    {
      title: 'Audit Logging',
      desc: 'Complete audit trail for all operations',
      icon: '📝'
    },
    {
      title: 'DDoS Protection',
      desc: 'Cloudflare enterprise-grade protection',
      icon: '🛡️'
    },
    {
      title: 'Network Isolation',
      desc: 'Private networks, VPC peering available',
      icon: '🌐'
    },
  ];

  const practices = [
    {
      title: 'Security Reviews',
      items: ['Regular penetration testing', 'Automated vulnerability scanning', 'Third-party security audits', 'Bug bounty program']
    },
    {
      title: 'Data Handling',
      items: ['Minimal data retention', 'Data anonymization', 'Right to deletion (GDPR)', 'Data portability']
    },
    {
      title: 'Access Control',
      items: ['Role-based access (RBAC)', 'Multi-factor authentication', 'SSO integration (Enterprise)', 'Session management']
    },
    {
      title: 'Incident Response',
      items: ['24/7 security monitoring', '<1 hour response SLA', 'Transparent communication', 'Post-mortem reports']
    },
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
            <Link href="/status" className="text-gray-400 hover:text-white transition-colors">Status</Link>
            <Link href="/modules" className="px-4 py-2 bg-violet-600 hover:bg-violet-500 rounded-lg transition-colors">
              Dashboard
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="pt-32 pb-16 px-6 text-center">
        <div className="inline-block px-4 py-2 rounded-full bg-green-500/20 text-green-400 text-sm font-medium mb-6">
          🔒 Security First
        </div>
        <h1 className="text-5xl font-bold mb-6">
          Enterprise-Grade Security
        </h1>
        <p className="text-xl text-gray-400 max-w-2xl mx-auto">
          Your data security is our top priority. Built with defense-in-depth 
          from the ground up.
        </p>
      </section>

      {/* Certifications */}
      <section className="py-12 px-6">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-2xl font-bold text-center mb-8">Compliance & Certifications</h2>
          
          <div className="grid md:grid-cols-4 gap-6">
            {certifications.map((cert) => (
              <div
                key={cert.name}
                className="p-6 rounded-xl bg-slate-800/50 border border-slate-700 text-center"
              >
                <div className="text-4xl mb-3">{cert.icon}</div>
                <h3 className="font-bold mb-1">{cert.name}</h3>
                <p className="text-sm text-gray-400 mb-3">{cert.desc}</p>
                <span className={`text-xs px-3 py-1 rounded-full ${
                  cert.status === 'Certified' || cert.status === 'Compliant'
                    ? 'bg-green-500/20 text-green-400'
                    : cert.status === 'In Progress'
                    ? 'bg-yellow-500/20 text-yellow-400'
                    : 'bg-violet-500/20 text-violet-400'
                }`}>
                  {cert.status}
                </span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Security Features */}
      <section className="py-16 px-6 bg-slate-900/50">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-2xl font-bold text-center mb-4">Security Features</h2>
          <p className="text-gray-400 text-center mb-12 max-w-2xl mx-auto">
            Multi-layered security protecting every aspect of your data and operations
          </p>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {securityFeatures.map((feature) => (
              <div
                key={feature.title}
                className="p-6 rounded-xl bg-slate-800/30 border border-slate-700 hover:border-violet-500/30 transition-colors"
              >
                <div className="text-3xl mb-3">{feature.icon}</div>
                <h3 className="font-semibold mb-2">{feature.title}</h3>
                <p className="text-sm text-gray-400">{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Security Practices */}
      <section className="py-16 px-6">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-2xl font-bold text-center mb-12">Security Practices</h2>

          <div className="grid md:grid-cols-2 gap-8">
            {practices.map((practice) => (
              <div
                key={practice.title}
                className="p-6 rounded-xl bg-slate-800/50 border border-slate-700"
              >
                <h3 className="font-bold text-lg mb-4 text-violet-400">{practice.title}</h3>
                <ul className="space-y-3">
                  {practice.items.map((item) => (
                    <li key={item} className="flex items-center gap-3 text-gray-300">
                      <span className="text-green-400">✓</span>
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Data Centers */}
      <section className="py-16 px-6 bg-slate-900/50">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-2xl font-bold mb-4">Infrastructure</h2>
          <p className="text-gray-400 mb-8">
            Hosted on enterprise-grade infrastructure with geographic redundancy
          </p>

          <div className="grid md:grid-cols-3 gap-6">
            <div className="p-6 rounded-xl bg-slate-800/30 border border-slate-700">
              <div className="text-3xl mb-3">🇪🇺</div>
              <h3 className="font-semibold">EU (Germany)</h3>
              <p className="text-sm text-gray-400">Primary datacenter</p>
              <p className="text-xs text-green-400 mt-2">● Active</p>
            </div>
            <div className="p-6 rounded-xl bg-slate-800/30 border border-slate-700">
              <div className="text-3xl mb-3">🇺🇸</div>
              <h3 className="font-semibold">US (East)</h3>
              <p className="text-sm text-gray-400">Enterprise option</p>
              <p className="text-xs text-violet-400 mt-2">● Available</p>
            </div>
            <div className="p-6 rounded-xl bg-slate-800/30 border border-slate-700">
              <div className="text-3xl mb-3">🌏</div>
              <h3 className="font-semibold">Asia (Singapore)</h3>
              <p className="text-sm text-gray-400">Enterprise option</p>
              <p className="text-xs text-violet-400 mt-2">● Available</p>
            </div>
          </div>
        </div>
      </section>

      {/* Bug Bounty */}
      <section className="py-16 px-6">
        <div className="max-w-3xl mx-auto">
          <div className="p-8 rounded-2xl bg-gradient-to-r from-violet-500/10 to-purple-500/10 border border-violet-500/20 text-center">
            <h2 className="text-2xl font-bold mb-4">🐛 Security Research</h2>
            <p className="text-gray-400 mb-6">
              Found a vulnerability? We appreciate responsible disclosure and reward 
              security researchers who help keep our platform secure.
            </p>
            <Link
              href="mailto:support@kloud.com?subject=Security%20Vulnerability%20Report"
              className="inline-flex px-6 py-3 bg-violet-600 hover:bg-violet-500 rounded-xl font-semibold transition-colors"
            >
              Report a Vulnerability
            </Link>
          </div>
        </div>
      </section>

      {/* Contact */}
      <section className="py-16 px-6 bg-slate-900/50 text-center">
        <h2 className="text-2xl font-bold mb-4">Security Questions?</h2>
        <p className="text-gray-400 mb-6">
          Our security team is available to discuss your specific requirements.
        </p>
        <Link
          href="mailto:support@kloud.com?subject=Security%20Inquiry"
          className="inline-flex px-8 py-4 bg-slate-800 hover:bg-slate-700 rounded-xl font-semibold transition-colors"
        >
          Contact Security Team
        </Link>
      </section>

      {/* Footer */}
      <footer className="py-12 px-6 border-t border-slate-800">
        <div className="max-w-6xl mx-auto text-center text-gray-500 text-sm">
          © 2026 Kloud. All rights reserved. | 
          <Link href="/status" className="hover:text-violet-400 ml-2">Status</Link> | 
          <Link href="/platform" className="hover:text-violet-400 ml-2">Platform</Link> | 
          <Link href="/company" className="hover:text-violet-400 ml-2">Company</Link>
        </div>
      </footer>
    </div>
  );
}








