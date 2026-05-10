/**
 * Sandbox Shield Component
 * =======================
 * 
 * Jona's safety sandbox monitoring and control interface
 */

'use client';

import { motion } from 'framer-motion';
import { useASIStore } from '@/lib/stores/asi-store';
import { clsx } from 'clsx';

// Tailwind classes instead of CSS module imports
const sandboxShield = 'bg-neutral-800/50 backdrop-blur-sm border border-purple-500/30 rounded-xl p-6';
const gradientText = 'bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent';
const safeGlow = 'shadow-lg shadow-purple-500/10';

// Progress bar helpers
const progressBar = ({ size }: { size?: string }) => {
  const base = 'w-full bg-gray-700/50 rounded-full overflow-hidden';
  const sizeClass = size === 'lg' ? 'h-4' : 'h-2';
  return `${base} ${sizeClass}`;
};

const progressBarFill = ({ level, color }: { level?: string; color?: string }) => {
  const base = 'h-full rounded-full transition-all duration-500';
  const colorMap: Record<string, string> = {
    safe: 'bg-green-500',
    moderate: 'bg-yellow-500',
    warning: 'bg-orange-500',
    critical: 'bg-red-500',
    success: 'bg-green-500',
    error: 'bg-red-500',
  };
  return `${base} ${colorMap[color || level || 'safe']}`;
};

// ASI Button helper
const asiButton = ({ variant, size }: { variant?: string; size?: string }) => {
  const base = 'inline-flex items-center justify-center rounded-lg font-medium transition-all focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-neutral-900';
  const sizeClasses: Record<string, string> = {
    sm: 'px-3 py-1.5 text-xs',
    default: 'px-4 py-2 text-sm',
    lg: 'px-6 py-3 text-base',
  };
  const variantClasses: Record<string, string> = {
    primary: 'bg-purple-600 hover:bg-purple-700 text-white focus:ring-purple-500',
    secondary: 'bg-neutral-600 hover:bg-neutral-700 text-white focus:ring-neutral-500',
    destructive: 'bg-red-600 hover:bg-red-700 text-white focus:ring-red-500',
    ghost: 'bg-transparent hover:bg-neutral-700 text-gray-300',
    outline: 'border border-purple-500 text-purple-400 hover:bg-purple-500/10',
  };
  return `${base} ${sizeClasses[size || 'default']} ${variantClasses[variant || 'primary']}`;
};

// Card helpers
const cardHeader = 'flex items-center justify-between mb-4';
const cardTitle = 'text-lg font-semibold text-white';

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

interface SandboxShieldProps {
  className?: string;
}

export function SandboxShield({ className }: SandboxShieldProps) {
  const store = useASIStore();
  const jona = store.jona ?? { ethics: 'moderate', violations: [] };
  const sandbox = store.sandbox ?? { threatLevel: 'low', isActive: false };
  const sandboxState = sandbox as {
    active?: boolean;
    isActive?: boolean;
    threatLevel?: string;
    violations?: unknown[];
  };
  const sandboxIsActive = Boolean(sandboxState.isActive ?? sandboxState.active);
  const sandboxThreatLevel = sandboxState.threatLevel ?? 'low';
  const sandboxViolations = Array.isArray(sandboxState.violations) ? sandboxState.violations : [];

  const getThreatLevelColor = (level: string) => {
    switch (level) {
      case 'low': return 'active';
      case 'medium': return 'warning';
      case 'high': return 'error';
      default: return 'active';
    }
  };

  const getEthicsDescription = (ethics?: string) => {
    switch (ethics) {
      case 'strict': return '🔒 Maximum protection - Zero tolerance for risks';
      case 'moderate': return '⚖️ Balance between security and functionality';
      case 'flexible': return '🔓 Enhanced flexibility with careful monitoring';
      default: return '🔐 Default security configuration';
    }
  };

  const handleEmergencyStop = () => {
    console.log('Emergency stop activated by user');
    // In a real system, this would halt all operations
  };

  return (
    <div className={clsx(sandboxShield, safeGlow, className)}>
      {/* Header */}
      <div className="text-center mb-6">
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <div className="text-3xl mb-2">🛡️</div>
          <h2 className={clsx(gradientText, 'text-xl font-bold mb-2')}>
            Jona Sandbox
          </h2>
          <p className="text-sm text-gray-400">
            Safety & Ethics System
          </p>
        </motion.div>
      </div>

      {/* Status Overview */}
      <div className="space-y-4 mb-6">
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-300">Status:</span>
          <div className={statusBadge({ 
            status: sandboxIsActive ? 'active' : 'inactive',
            size: 'default'
          })}>
            {sandboxIsActive ? 'AKTIV' : 'JOAKTIV'}
          </div>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-300">Threat Level:</span>
          <div className={statusBadge({ 
            status: getThreatLevelColor(sandboxThreatLevel),
            size: 'default'
          })}>
            {sandboxThreatLevel.toUpperCase()}
          </div>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-300">Violations:</span>
          <span className={`text-sm font-mono ${
            sandboxViolations.length === 0 ? 'text-green-400' :
              sandboxViolations.length < 5 ? 'text-yellow-400' : 'text-red-400'
          }`}>
            {sandboxViolations.length}
          </span>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-300">Ethics:</span>
          <div className={statusBadge({ 
            status: jona?.ethics === 'strict' ? 'active' : 'warning',
            size: 'sm'
          })}>
            {(jona?.ethics ?? 'strict').toUpperCase()}
          </div>
        </div>
      </div>

      {/* Ethics Level Progress */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-gray-300">Ethics Level:</span>
          <span className="text-xs text-gray-500">
            {jona.ethics === 'strict' ? '100%' : 
             jona.ethics === 'moderate' ? '70%' : '40%'}
          </span>
        </div>
        
        <div className={progressBar({ size: 'default' })}>
          <motion.div
            initial={{ width: 0 }}
            animate={{ 
              width: jona.ethics === 'strict' ? '100%' : 
                     jona.ethics === 'moderate' ? '70%' : '40%'
            }}
            transition={{ duration: 1, delay: 0.5 }}
            className={progressBarFill({ 
              color: jona.ethics === 'strict' ? 'success' :
                jona.ethics === 'moderate' ? 'warning' : 'error'
            })}
          />
        </div>
        
        <div className="mt-1 text-xs text-gray-500">
          {getEthicsDescription(jona.ethics)}
        </div>
      </div>

      {/* Recent Violations */}
      {(jona.violations ?? []).length > 0 && (
        <div className="mb-6">
          <h3 className="text-sm font-semibold text-gray-300 mb-2">
            🚨 Recent Violations:
          </h3>
          <div className="space-y-1 max-h-32 overflow-y-auto">
            {(jona.violations ?? []).slice(-3).map((violation, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="text-xs text-red-400 bg-red-500/10 p-2 rounded border border-red-500/20"
              >
                {violation}
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {/* Control Buttons */}
      <div className="space-y-3">
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={handleEmergencyStop}
          className={clsx(
            asiButton({
              variant: 'destructive',
              size: 'default'
            }),
            'w-full'
          )}
        >
          🛑 EMERGENCY STOP
        </motion.button>

        <div className="grid grid-cols-2 gap-2">
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className={asiButton({ 
              variant: sandboxIsActive ? 'destructive' : 'default', 
              size: 'sm'
            })}
          >
            {sandboxIsActive ? 'Deactivate' : 'Activate'}
          </motion.button>

          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => console.log('System reset requested')}
            className={asiButton({ 
              variant: 'secondary', 
              size: 'sm'
            })}
          >
            Reset
          </motion.button>
        </div>
      </div>

      {/* Real-time Monitor */}
      <div className="mt-6 pt-4 border-t border-purple-500/20">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs text-gray-400">Real-time Monitoring:</span>
          <motion.div
            animate={{ 
              scale: [1, 1.1, 1],
              opacity: [0.5, 1, 0.5]
            }}
            transition={{ 
              duration: 2, 
              repeat: Infinity,
              ease: "easeInOut"
            }}
            className="w-2 h-2 bg-green-400 rounded-full"
          />
        </div>
        
        <div className="text-xs text-gray-500 space-y-1">
          {sandboxIsActive && (
            <>
              <div>✅ Commands being monitored</div>
              <div>🔍 Patterns being analyzed</div>
              <div>🛡️ Protection is active</div>
            </>
          )}
          {!sandboxIsActive && (
            <div className="text-red-400">
              ⚠️ Sandbox is deactivated
            </div>
          )}
        </div>
      </div>

      {/* Jona Signature */}
      <div className="mt-4 text-center">
        <div className="text-xs text-purple-400/70">
          💜 With love from Jona
        </div>
      </div>
    </div>
  );
}

