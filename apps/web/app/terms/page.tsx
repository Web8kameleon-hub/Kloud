'use client';

export default function TermsPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-900 to-slate-800 text-white">
      <div className="max-w-4xl mx-auto px-6 py-16">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold mb-4">Terms of Use</h1>
          <p className="text-slate-400">Kloud Cloud Research Series</p>
          <p className="text-sm text-slate-500 mt-2">Last updated: February 2026</p>
        </div>

        {/* Content */}
        <div className="space-y-8 text-slate-300">
          {/* Intellectual Property */}
          <section>
            <h2 className="text-2xl font-semibold text-white mb-4">1. Intellectual Property</h2>
            <p className="mb-4">
              All articles, research notes, technical documentation, source code, algorithms, 
              methodologies, and other content published on this website and associated repositories 
              are the exclusive intellectual property of <strong className="text-white">Ledjan Ahmati</strong>.
            </p>
            <p>
              This includes but is not limited to: EEG analysis systems, AI/ML pipelines, 
              neural signal processing algorithms, health monitoring frameworks, and all 
              associated documentation.
            </p>
          </section>

          {/* Allowed Uses */}
          <section>
            <h2 className="text-2xl font-semibold text-white mb-4">2. Permitted Uses</h2>
            <ul className="list-disc list-inside space-y-2">
              <li>Reading and viewing the content for personal, non-commercial purposes</li>
              <li>Sharing direct links to articles (with proper attribution)</li>
              <li>Citing the work in academic papers (with full citation)</li>
              <li>Discussing the concepts in educational contexts (with attribution)</li>
            </ul>
          </section>

          {/* Prohibited Uses */}
          <section>
            <h2 className="text-2xl font-semibold text-white mb-4">3. Prohibited Uses</h2>
            <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-6">
              <ul className="list-disc list-inside space-y-2">
                <li>Copying, reproducing, or republishing content without written permission</li>
                <li>Commercial use of any kind without licensing agreement</li>
                <li>Modifying, translating, or creating derivative works</li>
                <li>Training AI/ML models on this content</li>
                <li>Incorporating into products, services, or applications</li>
                <li>Using in corporate, institutional, or research settings without permission</li>
                <li>Scraping, data mining, or automated collection</li>
                <li>Removing copyright notices or attribution</li>
              </ul>
            </div>
          </section>

          {/* Commercial Licensing */}
          <section>
            <h2 className="text-2xl font-semibold text-white mb-4">4. Commercial Licensing</h2>
            <p className="mb-4">
              For commercial use, enterprise licensing, research partnerships, or integration 
              into products and services, please contact us directly:
            </p>
            <div className="bg-blue-900/20 border border-blue-500/30 rounded-lg p-6">
              <p className="font-mono">contact@kloud.com</p>
            </div>
          </section>

          {/* Enforcement */}
          <section>
            <h2 className="text-2xl font-semibold text-white mb-4">5. Enforcement</h2>
            <p>
              Violations of these terms will be pursued under applicable copyright, 
              intellectual property, and trade secret laws in all applicable jurisdictions. 
              We actively monitor for unauthorized use and will take legal action when necessary.
            </p>
          </section>

          {/* Disclaimer */}
          <section>
            <h2 className="text-2xl font-semibold text-white mb-4">6. Disclaimer</h2>
            <p>
              The content is provided &ldquo;as is&rdquo; without warranty of any kind. 
              The author is not liable for any damages arising from the use of this content.
            </p>
          </section>
        </div>

        {/* Footer */}
        <div className="mt-16 pt-8 border-t border-slate-700 text-center text-slate-500">
          <p>© 2026 Ledjan Ahmati. All rights reserved.</p>
          <p className="mt-2">Kloud Cloud Research Series</p>
        </div>
      </div>
    </div>
  );
}

