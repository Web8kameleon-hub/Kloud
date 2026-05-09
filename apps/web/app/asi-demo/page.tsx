/**
 * ASI Demo Page
 * =============
 * 
 * Interactive demonstration of the Kloud ASI system
 * with Trinity architecture (Core-A, Core-B, Core-C)
 */

'use client';

import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';
import { ASITerminal } from '@/components/asi/ASITerminal';
import { SandboxShield } from '@/components/asi/SandboxShield';
import { useASIStore } from '@/lib/stores/asi-store';

// Tailwind classes instead of CSS module imports
const asiContainer = 'min-h-screen bg-gradient-to-br from-slate-900 via-gray-900 to-slate-800 text-white';
const gradientText = 'bg-gradient-to-r from-blue-600 via-purple-400 to-pink-400 bg-clip-text text-transparent';
const agentCardAlba = 'bg-slate-800/50 backdrop-blur-sm border border-blue-800/30 rounded-xl p-6 hover:border-blue-700/50 transition-all';
const agentCardAlbi = 'bg-slate-800/50 backdrop-blur-sm border border-blue-800/30 rounded-xl p-6 hover:border-blue-700/50 transition-all';
const agentCardJona = 'bg-slate-800/50 backdrop-blur-sm border border-purple-500/30 rounded-xl p-6 hover:border-purple-400/50 transition-all';
const healthBar = 'h-2 bg-gray-700 rounded-full overflow-hidden';
const healthBarFill = 'h-full rounded-full transition-all';

// Status badge helper
const statusBadge = ({ status, size }: { status: string; size?: string }) => {
  const base = 'inline-flex items-center rounded-full font-semibold transition-colors';
  const sizeClass = size === 'lg' ? 'px-4 py-2 text-sm' : 'px-3 py-1 text-xs';
  const statusColors: Record<string, string> = {
    active: 'bg-green-500/20 text-green-400 border border-green-500/30',
    inactive: 'bg-gray-500/20 text-gray-400 border border-gray-500/30',
    processing: 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30',
    warning: 'bg-orange-500/20 text-orange-400 border border-orange-500/30',
    error: 'bg-red-500/20 text-red-400 border border-red-500/30',
  };
  return `${base} ${sizeClass} ${statusColors[status] || statusColors.inactive}`;
};

// Client-only time display component to prevent hydration mismatch
function ClientTimeDisplay({ timestamp }: { timestamp: number }) {
  const [mounted, setMounted] = useState(false);
  
  useEffect(() => {
    setMounted(true);
  }, []);
  
  if (!mounted) {
    return <span>--:--:--</span>;
  }
  
  return <span>{new Date(timestamp).toLocaleTimeString()}</span>;
}

export default function ASIDemoPage() {
  const { alba, albi, jona, sandbox } = useASIStore();

  const sandboxStatus = sandbox.status ?? 'inactive';
  const sandboxIsActive = sandbox.active ?? sandboxStatus === 'active';
  const sandboxThreatLevel = sandbox.threatLevel ?? 'low';
  const sandboxViolationCount = Array.isArray(sandbox.violations)
    ? sandbox.violations.length
    : sandbox.violations ?? 0;

  const agents = [
    {
      name: 'Core-A',
      role: 'Network Infrastructure Monitor',
      status: alba.status,
      health: 100 - (alba.workload ?? 0),
      color: '#0ea5e9',
      description: 'Monitors network and infrastructure',
      cardStyle: agentCardAlba
    },
    {
      name: 'Core-B',
      role: 'Intelligence Enhancement Engine',
      status: albi.consciousness === 'awake' ? 'active' : 'inactive',
      health: albi.creativity ?? 50,
      color: '#10b981',
      description: 'Artificial intelligence and creativity',
      cardStyle: agentCardAlbi
    },
    {
      name: 'Core-C',
      role: 'Safety & Ethics Guardian',
      status: jona.protection === 'enabled' ? 'active' : 'inactive',
      health: jona.ethics === 'strict' ? 100 : jona.ethics === 'moderate' ? 75 : 50,
      color: '#8b5cf6',
      description: 'System protection and ethics',
      cardStyle: agentCardJona
    }
  ];

  const getStatusBadgeVariant = (status: string) => {
    switch (status) {
      case 'active': return 'active';
      case 'inactive': return 'inactive';
      case 'processing': return 'processing';
      default: return 'warning';
    }
  };

  return (
    <div className={asiContainer}>
      <div className="container mx-auto p-8 max-w-7xl">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <motion.h1 
            className={`text-5xl font-bold mb-4 ${gradientText}`}
            animate={{
              backgroundPosition: ['0%', '100%', '0%']
            }}
            transition={{
              duration: 5,
              repeat: Infinity,
              ease: 'linear'
            }}
          >
            🧠 Kloud ASI
          </motion.h1>
          
          <motion.p 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
            className="text-xl text-slate-300 max-w-3xl mx-auto mb-6"
          >
            The world&apos;s first <span className="text-blue-600">Artificial General Intelligence</span> system 
            built on foundations of <span className="text-purple-400">love</span>, <span className="text-green-400">protection</span> and <span className="text-blue-700">cooperation</span>
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7 }}
            className="flex flex-wrap justify-center gap-4 mb-8"
          >
            <div className={statusBadge({ status: 'active', size: 'lg' })}>
              🌐 System Online
            </div>
            <div className={statusBadge({ 
              status: sandboxIsActive ? 'active' : 'error', 
              size: 'lg' 
            })}>
              🔐 Sandbox {sandboxIsActive ? 'Active' : 'Inactive'}
            </div>
            <div className={statusBadge({ 
              status: sandboxThreatLevel === 'low' ? 'active' : 'warning', 
              size: 'lg' 
            })}>
              🛡️ Security {sandboxThreatLevel === 'low' ? 'Normal' : 'Threat'}
            </div>
          </motion.div>
        </motion.div>

        {/* Agent Trinity Grid */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8"
        >
          {agents.map((agent, index) => (
            <motion.div
              key={agent.name}
              initial={{ opacity: 0, y: 20, scale: 0.9 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              transition={{ delay: 0.1 * index, duration: 0.5 }}
              whileHover={{ 
                scale: 1.03,
                y: -5,
                transition: { duration: 0.2 }
              }}
              className={agent.cardStyle}
            >
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-xl font-bold" style={{ color: agent.color }}>
                    {agent.name}
                  </h3>
                  <p className="text-sm text-gray-400">{agent.role}</p>
                </div>
                <div className={statusBadge({ 
                  status: getStatusBadgeVariant(agent.status) as 'active' | 'learning' | 'idle',
                  size: 'lg'
                })}>
                  {agent.status.toUpperCase()}
                </div>
              </div>

              <p className="text-sm text-gray-300 mb-4">
                {agent.description}
              </p>

              {/* Health Indicator */}
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Performanca:</span>
                  <span className={
                    agent.health > 80 ? 'text-green-400' : 
                    agent.health > 50 ? 'text-yellow-400' : 'text-red-400'
                  }>
                    {agent.health}%
                  </span>
                </div>
                
                <div className={healthBar}>
                  <motion.div
                    className={healthBarFill}
                    style={{ backgroundColor: agent.color }}
                    initial={{ width: 0 }}
                    animate={{ width: `${agent.health}%` }}
                    transition={{ duration: 1, delay: 0.5 + index * 0.2 }}
                  />
                </div>
              </div>

              {/* Agent Specific Info */}
              <div className="mt-4 pt-4 border-t border-gray-700 text-xs text-gray-400">
                {agent.name === 'Core-A' && (
                  <div>Workload: {alba.workload ?? 0}% | Last Ping: <ClientTimeDisplay timestamp={alba.lastPing instanceof Date ? alba.lastPing.getTime() : (alba.lastPing ?? Date.now())} /></div>
                )}
                {agent.name === 'Core-B' && (
                  <div>Insights: {albi.insights?.length ?? 0} | Creativity: {albi.creativity ?? 0}%</div>
                )}
                {agent.name === 'Core-C' && (
                  <div>Ethics: {jona.ethics ?? 'unknown'} | Violations: {jona.violations?.length ?? 0}</div>
                )}
              </div>
            </motion.div>
          ))}
        </motion.div>

        {/* Main Interface Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
          {/* Sandbox Shield */}
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 }}
            className="lg:col-span-1"
          >
            <SandboxShield />
          </motion.div>
          
          {/* ASI Terminal */}
          <motion.div
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.5 }}
            className="lg:col-span-2"
          >
            <ASITerminal />
          </motion.div>
        </div>

        {/* System Stats */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="bg-gray-900/50 backdrop-blur-sm border border-gray-700 rounded-xl p-6 mb-8"
        >
          <h3 className="text-lg font-semibold text-center mb-4">📊 System Statistics</h3>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-blue-700">
                {100 - (alba.workload ?? 0)}%
              </div>
              <div className="text-sm text-gray-400">Core-A Health</div>
            </div>
            
            <div>
              <div className="text-2xl font-bold text-blue-700">
                {albi.creativity ?? 0}%
              </div>
              <div className="text-sm text-gray-400">Core-B Creativity</div>
            </div>
            
            <div>
              <div className="text-2xl font-bold text-purple-400">
                {jona.ethics === 'strict' ? '100' : jona.ethics === 'moderate' ? '75' : '50'}%
              </div>
              <div className="text-sm text-gray-400">Core-C Ethics</div>
            </div>
            
            <div>
              <div className="text-2xl font-bold text-red-400">
                {sandboxViolationCount}
              </div>
              <div className="text-sm text-gray-400">Violations</div>
            </div>
          </div>
        </motion.div>

        {/* Footer */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
          className="text-center text-gray-500 text-sm space-y-2"
        >
          <p className="text-lg font-medium">
            🚀 <span className="text-blue-600">Powered by Trinity Architecture</span>
          </p>
          <p>
            <span className="text-blue-700">Core-A</span> (Body) • 
            <span className="text-blue-700"> Core-B</span> (Spirit) • 
            <span className="text-purple-400"> Core-C</span> (Heart)
          </p>
          <p className="pt-2">
            🔒 Sandbox enabled • ♻️ Strict ethics • 💝 Full protection
          </p>
          <p className="text-xs text-gray-600 pt-4">
            Kloud ASI Demo v2.1.0 • Built with 💜 using Zustand + Vanilla Extract + Framer Motion + CVA
          </p>
        </motion.div>
      </div>
    </div>
  );
}









