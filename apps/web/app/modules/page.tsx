/**
 * Kloud Dashboard
 * Professional UI inspired by Figma, Postman, Datadog, Opera
 * No emoji - clean Lucide icons only
 */

'use client';

import Link from 'next/link';
import { useState } from 'react';
import { 
  Brain, 
  Settings, 
  Waves, 
  GraduationCap, 
  Plane, 
  Activity, 
  Zap, 
  Dumbbell,
  Cloud, 
  User, 
  BarChart3, 
  Layout, 
  Code2, 
  ChevronRight,
  Search,
  Bell,
  Command,
  ExternalLink,
  MessageSquare,
  Globe,
  Archive,
  Target,
  Users
} from 'lucide-react';

// Module definitions with Lucide icons
const publicModules = [
  {
    id: 'zurich',
    name: 'Zürich Engine',
    description: 'Deterministic 9-stage reasoning without AI randomness',
    icon: Target,
    category: 'AI Reasoning',
    href: '/zurich',
    accent: 'slate'
  },
  {
    id: 'debate',
    name: 'Trinity Debate',
    description: '5 AI personas debate any topic from different perspectives',
    icon: Users,
    category: 'AI Reasoning',
    href: '/debate',
    accent: 'slate'
  },
  {
    id: 'curiosity-ocean',
    name: 'Curiosity Ocean',
    description: 'AI-powered chat interface for exploring knowledge',
    icon: Waves,
    category: 'AI Chat',
    href: '/modules/curiosity-ocean',
    accent: 'slate'
  },
  {
    id: 'openmind',
    name: 'OpenMind',
    description: 'General AI cockpit: chat, memory, workflows, vision, and music from the 9999 engine',
    icon: Brain,
    category: 'AI Chat',
    href: '/modules/openmind',
    accent: 'slate'
  },
  {
    id: 'web-reader',
    name: 'Web Reader',
    description: 'Browse any webpage, search the web, and chat with page content',
    icon: Globe,
    category: 'AI Chat',
    href: '/modules/web-reader',
    accent: 'slate'
  },
  {
    id: 'archive',
    name: 'Archive & Research',
    description: 'Search ArXiv, Wikipedia, PubMed and 5000+ global data sources',
    icon: Archive,
    category: 'Research',
    href: '/modules/archive',
    accent: 'slate'
  },
  {
    id: 'specialized-chat',
    name: 'Specialized Expert Chat',
    description: 'Expert-level AI conversations in advanced domains',
    icon: GraduationCap,
    category: 'AI Chat',
    href: '/modules/specialized-chat',
    accent: 'slate'
  },
  {
    id: 'specialized-chat-backend',
    name: 'Specialized Chat (Backend)',
    description: 'Direct access to Ocean Core Specialized Chat HTML',
    icon: MessageSquare,
    category: 'AI Chat',
    href: 'http://localhost:8030/chat',
    accent: 'slate',
    external: true
  },
  {
    id: 'aviation-weather',
    name: 'Aviation Weather',
    description: 'METAR, TAF and real-time flight conditions',
    icon: Plane,
    category: 'Environment',
    href: '/modules/aviation-weather',
    accent: 'slate'
  },
  {
    id: 'eeg-analysis',
    name: 'EEG Analysis',
    description: 'Real-time brainwave pattern analysis',
    icon: Activity,
    category: 'Neuroscience',
    href: '/modules/eeg-analysis',
    accent: 'slate'
  },
  {
    id: 'neural-synthesis',
    name: 'Neural Synthesis',
    description: 'Synthesize neural patterns and waveforms',
    icon: Zap,
    category: 'Neuroscience',
    href: '/modules/neural-synthesis',
    accent: 'slate'
  },
  {
    id: 'fitness-dashboard',
    name: 'Fitness Dashboard',
    description: 'Health metrics and performance tracking',
    icon: Dumbbell,
    category: 'Health',
    href: '/modules/fitness-dashboard',
    accent: 'slate'
  },
  {
    id: 'weather-dashboard',
    name: 'Weather & Cognitive',
    description: 'How weather impacts cognitive performance',
    icon: Cloud,
    category: 'Environment',
    href: '/modules/weather-dashboard',
    accent: 'slate'
  },
  {
    id: 'account',
    name: 'Account & Billing',
    description: 'Manage your profile, subscriptions, payment methods and settings',
    icon: User,
    category: 'Account',
    href: '/modules/account',
    accent: 'slate'
  },
  {
    id: 'my-data-dashboard',
    name: 'My Data Dashboard',
    description: 'IoT devices, API integrations, LoRa/GSM networks',
    icon: BarChart3,
    category: 'Data',
    href: '/modules/my-data-dashboard',
    accent: 'slate'
  },
  {
    id: 'mymirror-now',
    name: 'MyMirror Now',
    description: 'Real-time client admin portal with live metrics & data sources',
    icon: Layout,
    category: 'Admin',
    href: '/modules/mymirror-now',
    accent: 'slate'
  },
  {
    id: 'nodedb-control-surface',
    name: 'NodeDB Control Surface',
    description: 'Live bootstrap, sync loop, and STIGMA runtime state for hybrid fabric',
    icon: Command,
    category: 'Admin',
    href: '/modules/nodedb-control-surface',
    accent: 'slate'
  },
  {
    id: 'developer-docs',
    name: 'Developer Documentation',
    description: 'API Reference, SDKs, Quick Start Guide',
    icon: Code2,
    category: 'Developer',
    href: '/developers',
    accent: 'slate'
  }
];

// Accent color mapping
const accentColors = {
  slate: {
    bg: 'bg-gray-100',
    border: 'border-black',
    borderHover: 'hover:border-gray-600',
    text: 'text-black',
    icon: 'text-black',
    badge: 'bg-gray-100 text-black'
  },
  violet: {
    bg: 'bg-gray-100',
    border: 'border-black',
    borderHover: 'hover:border-gray-600',
    text: 'text-black',
    icon: 'text-black',
    badge: 'bg-gray-100 text-black'
  },
  orange: {
    bg: 'bg-gray-100',
    border: 'border-black',
    borderHover: 'hover:border-gray-600',
    text: 'text-black',
    icon: 'text-black',
    badge: 'bg-gray-100 text-black'
  },
  green: {
    bg: 'bg-gray-100',
    border: 'border-black',
    borderHover: 'hover:border-gray-600',
    text: 'text-black',
    icon: 'text-black',
    badge: 'bg-gray-100 text-black'
  },
  neutral: {
    bg: 'bg-gray-100',
    border: 'border-black',
    borderHover: 'hover:border-gray-600',
    text: 'text-black',
    icon: 'text-black',
    badge: 'bg-gray-100 text-black'
  }
};

export default function DashboardPage() {
  const [activeCategory, setActiveCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');

  const categories = ['all', ...new Set(publicModules.map(m => m.category))];

  const filteredModules = publicModules.filter(m => {
    const matchesCategory = activeCategory === 'all' || m.category === activeCategory;
    const matchesSearch = m.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         m.description.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  return (
    <div className="min-h-screen bg-white text-slate-900">
      {/* Sidebar */}
      <aside className="fixed left-0 top-0 h-full w-64 bg-gray-50 border-r border-slate-200 z-50">
        {/* Logo */}
        <div className="h-16 flex items-center px-5 border-b border-slate-200">
          <Link href="/" className="flex items-center gap-3 hover:opacity-80 transition">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-slate-700 to-slate-800 flex items-center justify-center">
              <Brain className="w-5 h-5 text-white" />
            </div>
            <span className="text-lg font-semibold tracking-tight">Kloud</span>
          </Link>
        </div>

        {/* Navigation */}
        <nav className="p-4 space-y-1">
          <div className="text-[11px] font-medium text-black uppercase tracking-wider px-3 mb-3">
            Modules
          </div>
          {categories.map(cat => (
            <button
              key={cat}
              onClick={() => setActiveCategory(cat)}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                activeCategory === cat
                  ? 'bg-gray-100 text-black border-2 border-black'
                  : 'text-black hover:text-black hover:bg-gray-100'
              }`}
            >
              {cat === 'all' ? 'All Modules' : cat}
            </button>
          ))}
        </nav>

        {/* Bottom */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-slate-200">
          <Link 
            href="/modules/account"
            className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-black hover:text-black hover:bg-gray-100 transition-all"
          >
            <Settings className="w-4 h-4" />
            Settings
          </Link>
        </div>
      </aside>

      {/* Main Content */}
      <main className="ml-64">
        {/* Top Bar */}
        <header className="h-16 flex items-center justify-between px-8 border-b border-slate-200 bg-white/80 backdrop-blur-xl sticky top-0 z-40">
          {/* Search */}
          <div className="relative w-96">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-black" />
            <input
              type="text"
              placeholder="Search modules..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full h-10 pl-10 pr-4 bg-slate-50 border border-slate-200 rounded-lg text-sm text-black placeholder:text-black/50 focus:outline-none focus:border-black transition-colors"
            />
            <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-1 text-black">
              <Command className="w-3 h-3" />
              <span className="text-xs">K</span>
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-4">
            <button className="relative p-2 rounded-lg hover:bg-white/[0.04] transition-colors">
              <Bell className="w-5 h-5 text-black" />
              <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-slate-800 rounded-full" />
            </button>
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-slate-700 to-slate-800 flex items-center justify-center text-sm font-medium">
              L
            </div>
          </div>
        </header>

        {/* Content */}
        <div className="p-8">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-2xl font-semibold tracking-tight mb-2">
              {activeCategory === 'all' ? 'All Modules' : activeCategory}
            </h1>
            <p className="text-black text-sm">
              {filteredModules.length} {filteredModules.length === 1 ? 'module' : 'modules'} available
            </p>
          </div>

          {/* Modules Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {filteredModules.map(module => {
              const colors = accentColors[module.accent as keyof typeof accentColors];
              const Icon = module.icon;
              const isExternal = 'external' in module && module.external;
              
              const CardContent = (
                <>
                  {/* Icon & Category */}
                  <div className="flex items-start justify-between mb-4">
                    <div className={`w-10 h-10 rounded-lg ${colors.bg} flex items-center justify-center`}>
                      <Icon className={`w-5 h-5 ${colors.icon}`} />
                    </div>
                    <div className="flex items-center gap-2">
                      {isExternal && <ExternalLink className="w-3 h-3 text-slate-500" />}
                      <span className={`px-2 py-1 rounded text-[11px] font-medium ${colors.badge}`}>
                        {module.category}
                      </span>
                    </div>
                  </div>

                  {/* Title & Description */}
                  <h3 className="text-[15px] font-medium mb-1.5 group-hover:text-white transition-colors">
                    {module.name}
                  </h3>
                  <p className="text-sm text-black leading-relaxed mb-4">
                    {module.description}
                  </p>

                  {/* Action */}
                  <div className={`flex items-center gap-1 text-sm font-medium ${colors.text} opacity-0 group-hover:opacity-100 transition-opacity`}>
                    <span>{isExternal ? 'Open in new tab' : 'Open'}</span>
                    {isExternal ? <ExternalLink className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                  </div>
                </>
              );
              
              return isExternal ? (
                <a
                  key={module.id}
                  href={module.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className={`group relative p-5 rounded-lg border-2 border-black bg-white shadow-sm ${colors.border} ${colors.borderHover} transition-all duration-200 hover:bg-gray-100`}
                >
                  {CardContent}
                </a>
              ) : (
                <Link
                  key={module.id}
                  href={module.href}
                  className={`group relative p-5 rounded-lg border-2 border-black bg-white shadow-sm ${colors.border} ${colors.borderHover} transition-all duration-200 hover:bg-gray-100`}
                >
                  {CardContent}
                </Link>
              );
            })}
          </div>

          {/* Empty State */}
          {filteredModules.length === 0 && (
            <div className="flex flex-col items-center justify-center py-16">
              <div className="w-12 h-12 rounded-lg bg-slate-800 flex items-center justify-center mb-4">
                <Search className="w-6 h-6 text-black" />
              </div>
              <h3 className="text-lg font-medium mb-2">No modules found</h3>
              <p className="text-black text-sm">
                Try adjusting your search or filter criteria
              </p>
            </div>
          )}
        </div>

        {/* Footer */}
        <footer className="border-t border-slate-200 mt-8">
          <div className="px-8 py-6 flex items-center justify-between text-sm text-black">
            <div className="flex items-center gap-6">
              <Link href="/developers" className="hover:text-black transition-colors">
                Documentation
              </Link>
              <a href="https://github.com/Web8kameleon-hub/kloud.com" className="hover:text-black transition-colors">
                GitHub
              </a>
              <a href="mailto:support@kloud.com" className="hover:text-black transition-colors">
                Support
              </a>
            </div>
            <div className="flex items-center gap-2">
              <span>Kloud</span>
              <span className="text-black">·</span>
              <span className="text-black">© 2026</span>
            </div>
          </div>
        </footer>
      </main>
    </div>
  );
}

