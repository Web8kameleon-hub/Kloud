'use client';

import Link from 'next/link';
import { useState, useEffect } from 'react';

/**
 * KLOUD HOME PAGE
 * Enterprise-first sovereign fabric positioning
 */

const MODULES = [
  // AI & COGNITIVE SURFACES
  {
    id: 'curiosity-ocean',
    name: 'Curiosity Ocean',
    description: 'AI service interface for guided reasoning, routing, and operational assistance.',
    icon: '🌊',
    color: 'from-emerald-500 to-teal-600',
    category: 'AI Operations',
    featured: true
  },
  {
    id: 'web-reader',
    name: 'Web Reader',
    description: 'Controlled web ingestion and contextual analysis inside the sovereign runtime.',
    icon: '🌐',
    color: 'from-blue-500 to-cyan-600',
    category: 'AI Operations',
    isNew: true
  },
  {
    id: 'archive',
    name: 'Archive & Research',
    description: 'Federated access to research corpora and trusted technical knowledge sources.',
    icon: '📜',
    color: 'from-indigo-500 to-violet-600',
    category: 'Research',
    isNew: true
  },
  // COGNITIVE TELEMETRY
  {
    id: 'eeg-analysis',
    name: 'EEG Analysis',
    description: 'Real-time cognitive telemetry for behavioral signal interpretation.',
    icon: '🧠',
    color: 'from-purple-500 to-pink-600',
    category: 'Neuroscience',
    featured: true
  },
  {
    id: 'neural-synthesis',
    name: 'Neural Synthesis',
    description: 'Synthesis and transformation workflows for advanced neural signal pipelines.',
    icon: '⚡',
    color: 'from-yellow-500 to-orange-600',
    category: 'Neuroscience'
  },
  // FABRIC OPERATIONS
  {
    id: 'nodedb-control-surface',
    name: 'NodeDB Control Surface',
    description: 'Live node membership, STIGMA/BTI state, and DAS quality supervision across the fabric.',
    icon: '🧩',
    color: 'from-teal-500 to-emerald-600',
    category: 'Infrastructure',
    featured: true
  },
  {
    id: 'dns-hosting-control',
    name: 'DNS Hosting Control',
    description: 'Trust-aware DNS and routing governance for production domain operations.',
    icon: '🛰️',
    color: 'from-cyan-500 to-sky-600',
    category: 'Infrastructure'
  },
  {
    id: 'protocol-kitchen',
    name: 'Protocol Kitchen',
    description: 'Design and validate protocol contracts for secure distributed execution.',
    icon: '🧪',
    color: 'from-fuchsia-500 to-violet-600',
    category: 'Infrastructure'
  },
  {
    id: 'functions-registry',
    name: 'Functions Registry',
    description: 'Governed catalog of runtime functions, contracts, and deployment readiness.',
    icon: '📚',
    color: 'from-amber-500 to-orange-600',
    category: 'Governance'
  },
  // TENANT & DEVELOPER LAYERS
  {
    id: 'account',
    name: 'Account & Billing',
    description: 'Tenant profile, subscriptions, policy controls, and payment governance.',
    icon: '👤',
    color: 'from-emerald-500 to-teal-600',
    category: 'Account'
  },
  {
    id: 'my-data-dashboard',
    name: 'My Data Dashboard',
    description: 'IoT devices, API integrations, and ingestion channels across sovereign data flows.',
    icon: '📊',
    color: 'from-green-500 to-teal-600',
    category: 'Data'
  },
  {
    id: 'developer-docs',
    name: 'Developer Documentation',
    description: 'API reference, SDKs, quick starts, and integration standards for platform teams.',
    icon: '👨‍💻',
    color: 'from-purple-500 to-pink-600',
    category: 'Developer'
  }
];

const SERVICES = [
  {
    title: 'Ocean Core — AI Service Guide',
    summary: 'Ocean Core is the autonomous operational brain of Kloud: it orchestrates workloads, enforces policy, guides users, and maintains integrity in real time.',
    href: '/ocean',
    badge: 'Assistant'
  },
  {
    title: 'AI Inference & Cognitive Analytics',
    summary: 'EEG analysis, audio intelligence, and adaptive pipelines (ALBI, ALBA, ASI) for production real-time and batch execution.',
    href: '/modules/curiosity-ocean',
    badge: 'AI Platform'
  },
  {
    title: 'Billing & Subscription Governance',
    summary: 'Stripe, SEPA, and PayPal with webhook automation, usage-based billing, and policy enforcement per tenant.',
    href: '/modules',
    badge: 'Payments'
  },
  {
    title: 'Sovereign Infrastructure & Edge Routing',
    summary: 'Multi-container orchestration, DNS trust policy management, health monitoring, and zero-downtime deployment pipelines.',
    href: '/status',
    badge: 'Infrastructure'
  }
];

const SEO_SERVICE_CLUSTERS = [
  {
    title: 'AI Operations Platform',
    keywords: [
      'enterprise ai platform',
      'ai orchestration',
      'multi-agent ai platform',
      'real-time decision intelligence'
    ],
    href: '/ocean'
  },
  {
    title: 'Industrial Intelligence Services',
    keywords: [
      'industrial ai services',
      'predictive analytics',
      'iot telemetry analytics',
      'operational intelligence platform'
    ],
    href: '/platform'
  },
  {
    title: 'Sovereign Infrastructure Services',
    keywords: [
      'sovereign ai cloud',
      'distributed execution engine',
      'secure api gateway',
      'edge routing governance'
    ],
    href: '/security'
  },
  {
    title: 'Observability and Telemetry',
    keywords: [
      'agent telemetry platform',
      'ai observability',
      'runtime monitoring ai',
      'distributed systems monitoring'
    ],
    href: '/status'
  }
];

const PRODUCT_DOMAINS = [
  'ocean',
  'brain',
  'eeg',
  'audio',
  'billing',
  'asi',
  'jona',
  'kitchen',
  'excel',
  'user',
  'mymirror',
  'monitoring',
  'crypto',
  'weather'
];

type HeroMetrics = {
  totalPaths: number;
  productDomains: number;
  oceanBrainPaths: number;
};

const DEFAULT_HERO_METRICS: HeroMetrics = {
  totalPaths: 154,
  productDomains: 14,
  oceanBrainPaths: 32
};

export default function HomePage() {
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [showAllModules, setShowAllModules] = useState(false);
  const [heroMetrics, setHeroMetrics] = useState<HeroMetrics>(DEFAULT_HERO_METRICS);

  const categories = ['all', ...new Set(MODULES.map(m => m.category))];
  const filteredModules = selectedCategory === 'all' 
    ? MODULES 
    : MODULES.filter(m => m.category === selectedCategory);
  const featuredModules = MODULES.filter((m) => m.featured);
  const modulesToRender = showAllModules ? filteredModules : filteredModules.slice(0, 6);
  const serviceItemListSchema = {
    '@context': 'https://schema.org',
    '@type': 'ItemList',
    name: 'Kloud Services',
    itemListElement: SERVICES.map((service, index) => ({
      '@type': 'ListItem',
      position: index + 1,
      url: `https://kameleon.life${service.href}`,
      name: service.title,
      description: service.summary,
    })),
  };

  useEffect(() => {
    let isMounted = true;

    const loadHeroMetrics = async () => {
      try {
        const response = await fetch('/openapi.json', { cache: 'no-store' });
        if (!response.ok) {
          return;
        }

        const spec = await response.json();
        const paths = Object.keys(spec?.paths ?? {});
        const totalPaths = paths.length;
        const productDomains = PRODUCT_DOMAINS.filter((domain) =>
          paths.some((path) => path.includes(`/${domain}`))
        ).length;
        const oceanBrainPaths = paths.filter((path) => /(^|\/)(ocean|brain)(\/|$)/.test(path)).length;

        if (isMounted) {
          setHeroMetrics({
            totalPaths,
            productDomains,
            oceanBrainPaths
          });
        }
      } catch {
        if (isMounted) {
          setHeroMetrics(DEFAULT_HERO_METRICS);
        }
      }
    };

    void loadHeroMetrics();

    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-b from-white via-gray-50 to-white text-black">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(serviceItemListSchema),
        }}
      />
      {/* Navigation */}
      <nav className="fixed top-0 w-full z-50 bg-white/80 backdrop-blur-xl border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center shadow-lg shadow-emerald-500/30">
                <span className="text-2xl">🧠</span>
              </div>
              <div>
                <span className="text-xl font-bold bg-gradient-to-r from-emerald-500 to-teal-500 bg-clip-text text-transparent">
                  Kloud
                </span>
                <span className="text-xs text-gray-600 block -mt-1">Sovereign Intelligence Fabric</span>
              </div>
            </div>
            
            <div className="hidden md:flex items-center gap-8">
              <a href="#definition" className="text-gray-600 hover:text-emerald-600 transition-colors">What is Kloud</a>
              <a href="#services" className="text-gray-600 hover:text-emerald-600 transition-colors">Ocean Core</a>
              <a href="#capabilities" className="text-gray-600 hover:text-emerald-600 transition-colors">Architecture</a>
              <a href="#tech-stack" className="text-gray-600 hover:text-emerald-600 transition-colors">Security Model</a>
              <Link href="/security" className="text-gray-600 hover:text-emerald-600 transition-colors">Security</Link>
              <Link href="/modules" className="text-gray-600 hover:text-emerald-600 transition-colors">Dashboard</Link>
            </div>
            
            <div className="flex items-center gap-4">
              <Link 
                href="/modules"
                className="px-5 py-2 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 rounded-lg font-medium transition-all shadow-lg shadow-emerald-500/25"
              >
                Start Enterprise Pilot
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Welcome Tagline — above Hero */}
      <section className="pt-28 pb-0 px-4 text-center">
        <div className="max-w-4xl mx-auto">
          <p className="text-sm uppercase tracking-[0.22em] text-gray-400 font-semibold mb-3">
            Welcome to the new world of technology.
          </p>
          <p className="text-lg md:text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
            A world where intelligence is sovereign, systems are alive, and operations think for themselves.
            <span className="block mt-2 text-gray-800 font-medium">
              Kloud is the fabric that powers this world — real-time telemetry, cognitive security,
              and distributed AI execution in one unified surface.
            </span>
          </p>
        </div>
      </section>

      {/* Hero Section */}
      <section className="pt-12 pb-20 px-4 relative overflow-hidden">
        {/* Animated Background */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse delay-1000"></div>
        </div>
        
        <div className="max-w-7xl mx-auto text-center relative z-10">
          {/* Live Status Badge */}
          <div className="inline-flex items-center gap-3 px-5 py-2.5 rounded-full bg-gray-100/50 border border-emerald-500/30 mb-8">
            <span className="w-2.5 h-2.5 rounded-full bg-green-400 animate-pulse"></span>
            <span className="text-sm text-emerald-600 font-medium">
              Sovereign Fabric Online • 99.97% Uptime
            </span>
          </div>

          {/* Main Headline */}
          <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight">
            <span className="bg-gradient-to-r from-emerald-500 via-teal-500 to-emerald-500 bg-clip-text text-transparent">
              Kloud
            </span>
            <br />
            <span className="text-2xl md:text-3xl text-gray-500 font-medium block mt-2 mb-1">
              Built for the world that thinks.
            </span>
            <span className="text-2xl md:text-4xl text-gray-700">
              Sovereign Intelligence Fabric for AI, Infrastructure, and Operations
            </span>
          </h1>

          {/* Subheadline */}
          <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-10 leading-relaxed">
            Real-time telemetry, secure execution, distributed AI pipelines, and operational governance
            in one unified control surface.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-12">
            <Link 
              href="/modules"
              className="w-full sm:w-auto px-8 py-4 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 rounded-xl font-semibold text-lg text-black transition-all shadow-lg shadow-emerald-500/30 flex items-center justify-center gap-2"
            >
              Start Enterprise Pilot
            </Link>
            <Link 
              href="#capabilities"
              className="w-full sm:w-auto px-8 py-4 bg-gray-100 hover:bg-gray-200 border border-gray-300 hover:border-emerald-500 rounded-xl font-semibold text-lg text-gray-700 transition-all flex items-center justify-center gap-2"
            >
              View Architecture
            </Link>
          </div>
        </div>
      </section>

      {/* What is Kloud */}
      <section id="definition" className="py-16 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="rounded-3xl border border-gray-200 bg-white p-8 md:p-10 shadow-[0_20px_60px_rgba(15,23,42,0.06)]">
            <p className="text-xs uppercase tracking-[0.18em] text-emerald-700 font-semibold mb-3">What is Kloud</p>
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Kloud is a Sovereign Intelligence Fabric.
            </h2>
            <p className="text-lg text-gray-600 max-w-4xl leading-relaxed">
              A distributed runtime that unifies AI inference, telemetry, security, and operational governance
              into one control surface. Built for platform teams that need predictable operations, provable trust,
              and full infrastructure control.
            </p>
            <div className="mt-8 grid md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div className="rounded-xl border border-gray-200 bg-gray-50 p-4">
                <p className="text-sm font-semibold text-gray-900">Behavioral Telemetry</p>
                <p className="text-sm text-gray-600 mt-1">STIGMA (BTI), NDB (DAS), Rezonance (PFD)</p>
              </div>
              <div className="rounded-xl border border-gray-200 bg-gray-50 p-4">
                <p className="text-sm font-semibold text-gray-900">Distributed Execution</p>
                <p className="text-sm text-gray-600 mt-1">CRDT-backed runtime consistency across sovereign nodes</p>
              </div>
              <div className="rounded-xl border border-gray-200 bg-gray-50 p-4">
                <p className="text-sm font-semibold text-gray-900">Operational Governance</p>
                <p className="text-sm text-gray-600 mt-1">Trust policy enforcement, routing, and incident visibility</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Services Hero Section */}
      <section id="services" className="py-20 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="relative overflow-hidden rounded-3xl border border-gray-200 bg-white shadow-[0_30px_80px_rgba(15,23,42,0.08)]">
            <div className="absolute -top-20 -left-20 w-72 h-72 rounded-full bg-emerald-300/30 blur-3xl"></div>
            <div className="absolute -bottom-24 -right-24 w-80 h-80 rounded-full bg-cyan-300/30 blur-3xl"></div>

            <div className="relative z-10 p-8 md:p-12 lg:p-14">
              <div className="flex flex-wrap items-center gap-3 mb-6">
                <span className="px-3 py-1 rounded-full text-xs font-semibold tracking-wider uppercase bg-emerald-100 text-emerald-700 border border-emerald-300">
                  Sovereign Fabric
                </span>
                <span className="px-3 py-1 rounded-full text-xs font-semibold tracking-wider uppercase bg-cyan-100 text-cyan-700 border border-cyan-300">
                  Enterprise Operations
                </span>
              </div>

              <h2 className="text-4xl md:text-5xl lg:text-6xl font-black leading-tight text-gray-900 max-w-4xl">
                What Kloud delivers.
                <span className="block text-gray-900">Sovereign AI Fabric. Cognitive Telemetry. Distributed Execution.</span>
                <span className="block bg-gradient-to-r from-emerald-600 to-cyan-600 bg-clip-text text-transparent">
                  Managed by Ocean Core — in one control surface.
                </span>
              </h2>

              <p className="mt-6 text-lg md:text-xl text-gray-600 max-w-3xl leading-relaxed">
                Kloud runs production AI services, trust and billing governance, and sovereign routing across distributed nodes.
                Ocean Core is the autonomous brain that orchestrates workloads, enforces policy,
                and preserves system integrity in real time.
              </p>

              <div className="mt-6">
                <Link
                  href="/ocean"
                  className="inline-flex items-center justify-center px-6 py-3 rounded-xl border border-emerald-300 bg-emerald-50 text-emerald-700 font-semibold hover:bg-emerald-100 transition-all"
                >
                  Meet Ocean Core
                </Link>
              </div>

              <div className="mt-8 grid grid-cols-2 md:grid-cols-4 gap-3 max-w-4xl">
                <div className="rounded-xl border border-gray-200 bg-white/80 px-4 py-3">
                  <p className="text-2xl font-black text-gray-900">{heroMetrics.totalPaths}</p>
                  <p className="text-xs uppercase tracking-wide text-gray-500">Live API Endpoints</p>
                  <p className="text-xs text-gray-500 mt-1">Inference, telemetry, orchestration, and compute.</p>
                </div>
                <div className="rounded-xl border border-gray-200 bg-white/80 px-4 py-3">
                  <p className="text-2xl font-black text-gray-900">{heroMetrics.productDomains}</p>
                  <p className="text-xs uppercase tracking-wide text-gray-500">Operational Domains</p>
                  <p className="text-xs text-gray-500 mt-1">Governed under one sovereign control surface.</p>
                </div>
                <div className="rounded-xl border border-gray-200 bg-white/80 px-4 py-3">
                  <p className="text-2xl font-black text-gray-900">{heroMetrics.oceanBrainPaths}</p>
                  <p className="text-xs uppercase tracking-wide text-gray-500">Ocean and Brain Services</p>
                  <p className="text-xs text-gray-500 mt-1">Autonomous routing, cognitive analysis, distributed execution.</p>
                </div>
                <div className="rounded-xl border border-gray-200 bg-white/80 px-4 py-3">
                  <p className="text-2xl font-black text-gray-900">24/7</p>
                  <p className="text-xs uppercase tracking-wide text-gray-500">Ocean Core Concierge</p>
                  <p className="text-xs text-gray-500 mt-1">Continuous guidance, routing, and integrity posture.</p>
                </div>
              </div>

              <div className="mt-10 grid gap-4 md:grid-cols-3">
                {SERVICES.map((service, index) => (
                  <Link
                    key={service.title}
                    href={service.href}
                    className="group rounded-2xl border border-gray-200 bg-white/90 p-6 hover:-translate-y-1 hover:border-emerald-500 hover:shadow-xl hover:shadow-emerald-500/10 transition-all"
                    style={{ animationDelay: `${index * 120}ms` }}
                  >
                    <span className="inline-flex px-2.5 py-1 rounded-full text-[11px] font-semibold uppercase tracking-wide bg-gray-100 text-gray-700 mb-4">
                      {service.badge}
                    </span>
                    <h3 className="text-xl font-bold text-gray-900 mb-2">{service.title}</h3>
                    <p className="text-gray-600 leading-relaxed">{service.summary}</p>
                    <div className="mt-5 text-emerald-700 font-semibold flex items-center gap-2 group-hover:gap-3 transition-all">
                      View Service
                      <span aria-hidden="true">→</span>
                    </div>
                  </Link>
                ))}
              </div>

              <div className="mt-10 flex flex-col sm:flex-row gap-4">
                <Link
                  href="/modules"
                  className="inline-flex items-center justify-center px-7 py-3.5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 text-black font-semibold shadow-lg shadow-emerald-500/20 hover:from-emerald-500 hover:to-teal-500 transition-all"
                >
                  Start Enterprise Pilot
                </Link>
                <Link
                  href="#capabilities"
                  className="inline-flex items-center justify-center px-7 py-3.5 rounded-xl border border-gray-300 bg-white text-gray-800 font-semibold hover:border-cyan-500 hover:text-cyan-700 transition-all"
                >
                  View Architecture
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="py-14 px-4 bg-white border-y border-gray-200">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-8">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900">
              Global Service Keywords We Are Targeting
            </h2>
            <p className="text-gray-600 mt-3 max-w-3xl mx-auto">
              This service map reflects our core ranking intent for AI operations, industrial intelligence,
              sovereign infrastructure, and telemetry observability.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-5">
            {SEO_SERVICE_CLUSTERS.map((cluster) => (
              <Link
                key={cluster.title}
                href={cluster.href}
                className="rounded-2xl border border-gray-200 bg-gray-50 p-5 hover:border-emerald-500 hover:bg-emerald-50/40 transition-all"
              >
                <h3 className="text-lg font-bold text-gray-900 mb-3">{cluster.title}</h3>
                <div className="flex flex-wrap gap-2">
                  {cluster.keywords.map((keyword) => (
                    <span
                      key={keyword}
                      className="inline-flex rounded-full border border-gray-300 bg-white px-3 py-1 text-sm text-gray-700"
                    >
                      {keyword}
                    </span>
                  ))}
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* AI Features Section */}
      <section id="capabilities" className="py-20 px-4 bg-gradient-to-b from-transparent to-gray-100/50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4 bg-gradient-to-r from-emerald-500 to-teal-400 bg-clip-text text-transparent">
              Sovereign Fabric Architecture
            </h2>
            <p className="text-gray-600 text-lg max-w-2xl mx-auto">
              The operating model behind secure distributed execution.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <Link href="/modules/eeg-analysis" className="p-8 rounded-2xl bg-gray-100/50 border border-gray-300 hover:border-emerald-500 hover:shadow-xl hover:shadow-emerald-500/10 transition-all text-center cursor-pointer">
              <div className="w-16 h-16 mx-auto rounded-2xl bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center mb-6 shadow-lg">
                <span className="text-3xl">🔬</span>
              </div>
              <h3 className="text-xl font-bold text-black mb-2">Cognitive Telemetry</h3>
              <p className="text-gray-600">Behavioral traces (BTI), deviation scoring (DAS), and propagation dynamics (PFD).</p>
            </Link>
            <Link href="/modules/curiosity-ocean" className="p-8 rounded-2xl bg-gray-100/50 border border-gray-300 hover:border-teal-500 hover:shadow-xl hover:shadow-teal-500/10 transition-all text-center cursor-pointer">
              <div className="w-16 h-16 mx-auto rounded-2xl bg-gradient-to-br from-teal-400 to-emerald-500 flex items-center justify-center mb-6 shadow-lg">
                <span className="text-3xl">🎨</span>
              </div>
              <h3 className="text-xl font-bold text-black mb-2">Distributed Execution Engine</h3>
              <p className="text-gray-600">Production inference and workload orchestration with sovereign node control.</p>
            </Link>
            <Link href="/modules" className="p-8 rounded-2xl bg-gray-100/50 border border-gray-300 hover:border-orange-500 hover:shadow-xl hover:shadow-orange-500/10 transition-all text-center cursor-pointer">
              <div className="w-16 h-16 mx-auto rounded-2xl bg-gradient-to-br from-amber-400 to-orange-500 flex items-center justify-center mb-6 shadow-lg">
                <span className="text-3xl">✨</span>
              </div>
              <h3 className="text-xl font-bold text-black mb-2">Operational Governance</h3>
              <p className="text-gray-600">Unified trust, routing policy, and runtime integrity enforcement in one surface.</p>
            </Link>
          </div>
        </div>
      </section>

      {/* Modules Section */}
      <section id="modules" className="py-20 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-4xl md:text-5xl font-bold mb-4 bg-gradient-to-r from-emerald-500 to-teal-500 bg-clip-text text-transparent">
              Platform Modules
            </h2>
            <p className="text-gray-600 text-lg max-w-2xl mx-auto mb-8">
              Operational capabilities of the sovereign fabric, grouped by domain.
            </p>
            
            {/* Category Filter */}
            <div className="flex flex-wrap items-center justify-center gap-2">
              {categories.map((category) => (
                <button
                  key={category}
                  onClick={() => setSelectedCategory(category)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                    selectedCategory === category
                      ? 'bg-emerald-500 text-black shadow-lg shadow-emerald-500/25'
                      : 'bg-gray-100 text-gray-600 hover:text-black hover:bg-gray-200'
                  }`}
                >
                  {category === 'all' ? 'All Modules' : category}
                </button>
              ))}
            </div>
          </div>

          {selectedCategory === 'all' && (
            <div className="mb-10">
              <h3 className="text-2xl font-bold text-black mb-4">Priority Modules for Production Teams</h3>
              <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
                {featuredModules.slice(0, 4).map((module) => (
                  <Link
                    key={`featured-${module.id}`}
                    href={`/modules/${module.id}`}
                    className="p-5 rounded-2xl bg-white border border-emerald-200 hover:border-emerald-500 hover:shadow-lg hover:shadow-emerald-500/10 transition-all"
                  >
                    <div className="flex items-center gap-3 mb-3">
                      <span className="text-2xl">{module.icon}</span>
                      <div>
                        <p className="font-semibold text-black leading-tight">{module.name}</p>
                        <p className="text-xs text-emerald-700">{module.category}</p>
                      </div>
                    </div>
                    <p className="text-sm text-gray-600 leading-relaxed">{module.description}</p>
                  </Link>
                ))}
              </div>
            </div>
          )}

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {modulesToRender.map((module) => (
              <Link 
                key={module.id}
                href={`/modules/${module.id}`}
                className={`p-6 rounded-2xl bg-gray-100/50 border hover:shadow-xl hover:shadow-emerald-500/10 transition-all group relative ${
                  (module as { isNew?: boolean }).isNew 
                    ? 'border-green-500/50 hover:border-green-400 ring-1 ring-green-500/20' 
                    : 'border-gray-300 hover:border-emerald-500'
                }`}
              >
                {(module as { isNew?: boolean }).isNew && (
                  <div className="absolute -top-2 -right-2 px-3 py-1 bg-gradient-to-r from-green-500 to-emerald-500 rounded-full text-xs font-bold text-black shadow-lg animate-pulse">
                    NEW ✨
                  </div>
                )}
                <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${module.color} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform shadow-lg`}>
                  <span className="text-2xl">{module.icon}</span>
                </div>
                <div className="flex items-center gap-2 mb-2">
                  <h3 className="text-xl font-semibold text-black">{module.name}</h3>
                  <span className="px-2 py-0.5 text-xs rounded-full bg-emerald-500/20 text-emerald-600">
                    {module.category}
                  </span>
                </div>
                <p className="text-gray-600">{module.description}</p>
                <div className="mt-4 flex items-center gap-2 text-emerald-600 group-hover:gap-3 transition-all">
                  <span className="text-sm font-medium">Open Module</span>
                  <span>→</span>
                </div>
              </Link>
            ))}
          </div>

          {filteredModules.length > 6 && (
            <div className="mt-8 text-center">
              <button
                type="button"
                onClick={() => setShowAllModules((prev) => !prev)}
                className="px-6 py-3 rounded-xl border border-gray-300 bg-white text-gray-800 font-semibold hover:border-emerald-500 hover:text-emerald-700 transition-all"
              >
                {showAllModules ? 'Show fewer modules' : `Show all modules (${filteredModules.length})`}
              </button>
            </div>
          )}
        </div>
      </section>

      {/* Why Choose Us Section */}
      <section id="tech-stack" className="py-20 px-4 bg-gradient-to-b from-transparent to-gray-100/50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold mb-4 bg-gradient-to-r from-emerald-500 to-teal-400 bg-clip-text text-transparent">
              Why Kloud?
            </h2>
            <p className="text-gray-600 text-lg">
              Built for sovereignty, behavioral integrity, and operational control.
            </p>
          </div>

          <div className="grid md:grid-cols-4 gap-6">
            {[
              { name: 'Sovereign by Design', desc: 'Run workloads inside your own infrastructure perimeter.', icon: '🛡️' },
              { name: 'Cognitive Telemetry', desc: 'BTI, DAS, and PFD expose behavior before failure spreads.', icon: '🧠' },
              { name: 'Distributed Execution', desc: 'CRDT-backed consistency with resilient orchestration.', icon: '⚙️' },
              { name: 'Zero-Trust Governance', desc: 'Policy enforcement and trust controls in one control surface.', icon: '🔒' },
            ].map((item) => (
              <div 
                key={item.name}
                className="p-6 rounded-xl bg-gray-100/50 border border-gray-300 text-center hover:border-emerald-500 hover:shadow-lg hover:shadow-emerald-500/10 transition-all"
              >
                <span className="text-4xl mb-3 block">{item.icon}</span>
                <h4 className="font-semibold text-black text-lg">{item.name}</h4>
                <p className="text-sm text-gray-600 mt-1">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Get Started Section */}
      <section className="py-20 px-4">
        <div className="max-w-4xl mx-auto">
          <div className="p-8 rounded-2xl bg-gradient-to-br from-gray-100 to-gray-50 border border-emerald-500/30 shadow-lg shadow-emerald-500/10">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold text-black mb-2">Ready to run sovereign operations?</h2>
              <p className="text-gray-600">Start a pilot, deploy nodes, and govern AI execution from one control surface.</p>
            </div>
            
            <div className="grid md:grid-cols-3 gap-4">
              <div className="p-4 rounded-lg bg-gray-200/50 border border-gray-300 text-center">
                <p className="text-lg mb-2 font-bold text-gray-800">SLA</p>
                <p className="text-gray-800 text-sm font-medium">Production Reliability</p>
                <p className="text-xs text-gray-600">Measured uptime and controlled incident response</p>
              </div>
              <div className="p-4 rounded-lg bg-gray-200/50 border border-gray-300 text-center">
                <p className="text-lg mb-2 font-bold text-gray-800">TRUST</p>
                <p className="text-gray-800 text-sm font-medium">Policy and Telemetry</p>
                <p className="text-xs text-gray-600">BTI/DAS/PFD plus DNS and email trust governance</p>
              </div>
              <div className="p-4 rounded-lg bg-gray-200/50 border border-gray-300 text-center">
                <p className="text-lg mb-2 font-bold text-gray-800">PILOT</p>
                <p className="text-gray-800 text-sm font-medium">30-60-90 Rollout</p>
                <p className="text-xs text-gray-600">Structured path from pilot to full production</p>
              </div>
            </div>
            
            <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link 
                href="/modules"
                className="inline-flex items-center gap-2 px-8 py-4 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 rounded-xl font-semibold text-lg transition-all shadow-lg shadow-emerald-500/30"
              >
                Start Enterprise Pilot
              </Link>
              <Link 
                href="#modules"
                className="inline-flex items-center gap-2 px-8 py-4 border border-gray-300 bg-white hover:border-emerald-500 text-gray-800 hover:text-emerald-700 rounded-xl font-semibold text-lg transition-all"
              >
                Explore Modules
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-200 py-12 px-4 bg-gray-50/50">
        <div className="max-w-7xl mx-auto">
          <div className="mb-8">
            <div className="flex items-center gap-2 mb-3">
              <span className="text-2xl">🧠</span>
              <span className="text-lg font-bold text-black">Kloud</span>
            </div>
            <p className="text-gray-600 text-sm max-w-xl">
              Sovereign Intelligence Fabric for production operations, behavioral integrity, and secure distributed execution.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 mb-8">
            <div>
              <h4 className="font-semibold mb-4 text-black">Platform</h4>
              <ul className="space-y-2 text-gray-600 text-sm">
                <li><Link href="/modules" className="hover:text-emerald-600 transition-colors">Dashboard</Link></li>
                <li><Link href="/modules/curiosity-ocean" className="hover:text-emerald-600 transition-colors">Curiosity Ocean</Link></li>
                <li><Link href="/modules/eeg-analysis" className="hover:text-emerald-600 transition-colors">EEG Analysis</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4 text-black">Resources</h4>
              <ul className="space-y-2 text-gray-600 text-sm">
                <li><Link href="/developers" className="hover:text-emerald-600 transition-colors">Documentation</Link></li>
                <li><Link href="/marketplace" className="hover:text-emerald-600 transition-colors">Marketplace</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4 text-black">Company</h4>
              <ul className="space-y-2 text-gray-600 text-sm">
                <li><span className="text-gray-700">Ledjan Ahmati</span></li>
                <li><span className="text-gray-700">ABA GmbH</span></li>
                <li><a href="mailto:clisonix@pm.me" className="hover:text-emerald-600 transition-colors">clisonix@pm.me</a></li>
              </ul>
            </div>
          </div>
          <div className="pt-8 border-t border-gray-200 text-center text-gray-500 text-sm">
            © 2026 Kloud. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  );
}

