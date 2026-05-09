'use client';

import Link from 'next/link';
import Script from 'next/script';

/**
 * PRICING PAGE - Stripe Pricing Table Integration
 * 
 * Plans (via Stripe Pricing Table):
 * - Pro: €9.99/month - All 63+ articles, Curiosity Ocean, priority support
 * - Team: €29.99/month - Everything + team features
 */

export default function PricingPage() {
  const faqs = [
    {
      q: 'Can I try Kloud before paying?',
      a: 'Absolutely! The Free plan gives you access to 10 research articles and basic Curiosity Ocean features forever - no credit card required.'
    },
    {
      q: 'What payment methods do you accept?',
      a: 'We accept all major credit cards (Visa, Mastercard, American Express), SEPA bank transfers, and PayPal through our secure Stripe payment system.'
    },
    {
      q: 'Can I cancel anytime?',
      a: 'Yes! No contracts, no commitments. Cancel your subscription anytime and you\'ll keep access until the end of your billing period.'
    },
    {
      q: 'What\'s included in the 63+ articles?',
      a: 'Our research articles cover EEG analysis, industrial AI, FDA compliance, neural networks, and more. New articles are added monthly.'
    },
    {
      q: 'What is Curiosity Ocean?',
      a: 'Curiosity Ocean is our AI assistant powered by advanced language models. It can analyze documents, answer questions, and help with research using camera and microphone tools.'
    },
    {
      q: 'Do you offer refunds?',
      a: 'Yes, we offer a 14-day money-back guarantee. If you\'re not satisfied, contact us for a full refund.'
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
            <Link href="/why-kloud" className="text-gray-400 hover:text-white transition-colors">Why Kloud</Link>
            <Link href="/platform" className="text-gray-400 hover:text-white transition-colors">Platform</Link>
            <Link href="/modules" className="px-4 py-2 bg-violet-600 hover:bg-violet-500 rounded-lg transition-colors">
              Open Dashboard
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="pt-32 pb-8 px-6 text-center">
        <h1 className="text-5xl font-bold mb-4">
          Simple, Transparent Pricing
        </h1>
        <p className="text-xl text-gray-400 mb-8 max-w-2xl mx-auto">
          Start free, scale as you grow. No hidden fees, no surprises.
        </p>
      </section>

      {/* Stripe Pricing Table */}
      <section className="py-12 px-6">
        <div className="max-w-4xl mx-auto">
          <Script 
            async 
            src="https://js.stripe.com/v3/pricing-table.js"
            strategy="lazyOnload"
          />
          {/* @ts-expect-error - Stripe custom element */}
          <stripe-pricing-table 
            pricing-table-id="prctbl_1Sy8ChJQa06Hh2HG3AT0Lh1s"
            publishable-key="pk_live_51SMsVsJQa06Hh2HGoqyEOIwdY5dcRYjr2Ic5Xk2xkjdHZf71cXGM7wU3sFTWHPXaePYEE0fmVJzbihbJEXU8oaKP00kNtNyHEg"
          />
        </div>
      </section>

      {/* Free Tier Info */}
      <section className="py-8 px-6">
        <div className="max-w-2xl mx-auto text-center">
          <div className="p-6 rounded-2xl bg-slate-800/50 border border-slate-700">
            <h3 className="text-xl font-bold mb-2">🆓 Free Tier Available</h3>
            <p className="text-gray-400 mb-4">
              Want to try before you buy? Get 10 free research articles and basic Curiosity Ocean access.
            </p>
            <Link 
              href="/sign-up" 
              className="inline-flex px-6 py-3 bg-slate-700 hover:bg-slate-600 rounded-xl font-semibold transition-colors"
            >
              Start Free →
            </Link>
          </div>
        </div>
      </section>

      {/* Trust Badges */}
      <section className="py-12 px-6">
        <div className="max-w-4xl mx-auto">
          <div className="flex flex-wrap justify-center items-center gap-8 opacity-60">
            <div className="text-center">
              <div className="text-2xl font-bold">99.97%</div>
              <div className="text-sm text-gray-400">Uptime</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold">&lt;100ms</div>
              <div className="text-sm text-gray-400">Latency</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold">SOC2</div>
              <div className="text-sm text-gray-400">Compliant</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold">GDPR</div>
              <div className="text-sm text-gray-400">Ready</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold">24/7</div>
              <div className="text-sm text-gray-400">Support</div>
            </div>
          </div>
        </div>
      </section>

      {/* FAQs */}
      <section className="py-20 px-6 bg-slate-900/50">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">Frequently Asked Questions</h2>
          
          <div className="space-y-6">
            {faqs.map((faq) => (
              <div key={faq.q} className="p-6 rounded-xl bg-slate-800/50 border border-slate-700">
                <h3 className="font-semibold text-lg mb-2">{faq.q}</h3>
                <p className="text-gray-400">{faq.a}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-6 text-center">
        <h2 className="text-3xl font-bold mb-4">Still have questions?</h2>
        <p className="text-gray-400 mb-8">Our team is here to help you find the perfect plan.</p>
        <Link
          href="mailto:support@kloud.com"
          className="inline-flex px-8 py-4 bg-slate-800 hover:bg-slate-700 rounded-xl font-semibold transition-colors"
        >
          Contact Support
        </Link>
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








