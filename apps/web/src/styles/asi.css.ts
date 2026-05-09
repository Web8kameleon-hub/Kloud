/**
 * ASI Styles with Vanilla Extract
 * ===============================
 * 
 * Type-safe CSS styles for Kloud ASI components
 */

import { style, keyframes, globalStyle } from '@vanilla-extract/css';

// Global theme variables
const theme = {
  colors: {
    primary: '#3b82f6',
    success: '#10b981',
    warning: '#f59e0b',
    danger: '#ef4444',
    alba: '#0ea5e9',      // Sky blue for Alba
    albi: '#10b981',      // Green for Albi
    jona: '#8b5cf6',      // Purple for Jona
    background: {
      primary: '#0f172a',
      secondary: '#1e293b',
      tertiary: '#334155'
    },
    text: {
      primary: '#f8fafc',
      secondary: '#cbd5e1',
      muted: '#64748b'
    }
  },
  spacing: {
    xs: '0.25rem',
    sm: '0.5rem',
    md: '1rem',
    lg: '1.5rem',
    xl: '2rem',
    '2xl': '3rem'
  },
  borderRadius: {
    sm: '4px',
    md: '8px',
    lg: '12px',
    xl: '16px'
  }
};

// Keyframe animations
const pulse = keyframes({
  '0%': { opacity: 1 },
  '50%': { opacity: 0.7 },
  '100%': { opacity: 1 }
});

const glow = keyframes({
  '0%, 100%': { 
    boxShadow: '0 0 5px rgba(59, 130, 246, 0.5)',
    borderColor: 'rgba(59, 130, 246, 0.5)'
  },
  '50%': { 
    boxShadow: '0 0 20px rgba(59, 130, 246, 0.8)',
    borderColor: 'rgba(59, 130, 246, 0.8)'
  }
});

const slideInFromBottom = keyframes({
  '0%': {
    transform: 'translateY(20px)',
    opacity: 0
  },
  '100%': {
    transform: 'translateY(0)',
    opacity: 1
  }
});

const rotateGradient = keyframes({
  '0%': { backgroundPosition: '0% 50%' },
  '50%': { backgroundPosition: '100% 50%' },
  '100%': { backgroundPosition: '0% 50%' }
});

// Global styles
globalStyle('*', {
  margin: 0,
  padding: 0,
  boxSizing: 'border-box'
});

globalStyle('body', {
  fontFamily: '"Inter", system-ui, sans-serif',
  backgroundColor: theme.colors.background.primary,
  color: theme.colors.text.primary,
  lineHeight: 1.6
});

// Main container
export const asiContainer = style({
  background: `linear-gradient(135deg, ${theme.colors.background.primary} 0%, ${theme.colors.background.secondary} 50%, #16213e 100%)`,
  minHeight: '100vh',
  color: theme.colors.text.primary,
  fontFamily: 'monospace, system-ui',
  position: 'relative',
  overflow: 'hidden'
});

// Terminal styles
export const asiTerminal = style({
  background: 'rgba(15, 23, 42, 0.8)',
  border: `1px solid ${theme.colors.background.tertiary}`,
  borderRadius: theme.borderRadius.lg,
  backdropFilter: 'blur(10px)',
  position: 'relative',
  overflow: 'hidden',
  transition: 'all 0.3s ease',
  
  ':before': {
    content: '""',
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    height: '2px',
    background: `linear-gradient(90deg, ${theme.colors.danger}, ${theme.colors.warning}, ${theme.colors.success}, ${theme.colors.primary})`,
    backgroundSize: '200% 100%',
    animation: `${rotateGradient} 3s ease infinite`
  },
  
  ':hover': {
    transform: 'translateY(-2px)',
    boxShadow: '0 8px 25px rgba(0, 0, 0, 0.3)'
  }
});

// Command input
export const commandInput = style({
  background: 'rgba(30, 41, 59, 0.8)',
  border: `1px solid ${theme.colors.background.tertiary}`,
  borderRadius: theme.borderRadius.md,
  color: theme.colors.text.primary,
  padding: `${theme.spacing.md} ${theme.spacing.lg}`,
  fontSize: '14px',
  fontFamily: 'monospace',
  width: '100%',
  transition: 'all 0.2s ease',
  
  ':focus': {
    outline: 'none',
    borderColor: theme.colors.primary,
    boxShadow: `0 0 0 2px rgba(59, 130, 246, 0.2)`,
    background: 'rgba(30, 41, 59, 0.95)'
  },
  
  '::placeholder': {
    color: theme.colors.text.muted
  }
});

// Status indicators
export const statusIndicator = style({
  padding: `${theme.spacing.xs} ${theme.spacing.sm}`,
  borderRadius: theme.borderRadius.sm,
  fontSize: '12px',
  fontWeight: 'bold',
  textTransform: 'uppercase',
  letterSpacing: '0.5px'
});

export const statusActive = style([statusIndicator, {
  background: 'rgba(16, 185, 129, 0.2)',
  color: theme.colors.success,
  border: `1px solid rgba(16, 185, 129, 0.3)`
}]);

export const statusProcessing = style([statusIndicator, {
  background: 'rgba(245, 158, 11, 0.2)',  
  color: theme.colors.warning,
  border: `1px solid rgba(245, 158, 11, 0.3)`,
  animation: `${pulse} 1.5s ease-in-out infinite`
}]);

export const statusRejected = style([statusIndicator, {
  background: 'rgba(239, 68, 68, 0.2)',
  color: theme.colors.danger,
  border: `1px solid rgba(239, 68, 68, 0.3)`
}]);

// Agent cards
export const agentCard = style({
  background: 'rgba(30, 41, 59, 0.6)',
  border: `1px solid ${theme.colors.background.tertiary}`,
  borderRadius: theme.borderRadius.lg,
  padding: theme.spacing.xl,
  backdropFilter: 'blur(10px)',
  transition: 'all 0.3s ease',
  cursor: 'pointer',
  
  ':hover': {
    transform: 'translateY(-4px) scale(1.02)',
    boxShadow: '0 12px 30px rgba(0, 0, 0, 0.4)',
    borderColor: 'rgba(59, 130, 246, 0.5)'
  }
});

export const agentCardAlba = style([agentCard, {
  borderColor: theme.colors.alba,
  ':hover': {
    borderColor: theme.colors.alba,
    boxShadow: `0 12px 30px rgba(14, 165, 233, 0.3)`
  }
}]);

export const agentCardAlbi = style([agentCard, {
  borderColor: theme.colors.albi,
  ':hover': {
    borderColor: theme.colors.albi,
    boxShadow: `0 12px 30px rgba(16, 185, 129, 0.3)`
  }
}]);

export const agentCardJona = style([agentCard, {
  borderColor: theme.colors.jona,
  ':hover': {
    borderColor: theme.colors.jona,
    boxShadow: `0 12px 30px rgba(139, 92, 246, 0.3)`
  }
}]);

// Health bars
export const healthBar = style({
  width: '100%',
  height: '8px',
  background: theme.colors.background.tertiary,
  borderRadius: theme.borderRadius.sm,
  overflow: 'hidden',
  position: 'relative'
});

export const healthBarFill = style({
  height: '100%',
  borderRadius: theme.borderRadius.sm,
  transition: 'width 1s ease',
  background: `linear-gradient(90deg, ${theme.colors.success}, ${theme.colors.primary})`
});

// Command history
export const commandHistoryItem = style({
  padding: theme.spacing.md,
  borderRadius: theme.borderRadius.md,
  marginBottom: theme.spacing.sm,
  animation: `${slideInFromBottom} 0.3s ease`,
  transition: 'all 0.2s ease',
  
  ':hover': {
    transform: 'translateX(4px)'
  }
});

export const commandCompleted = style([commandHistoryItem, {
  background: 'rgba(16, 185, 129, 0.1)',
  border: `1px solid rgba(16, 185, 129, 0.2)`
}]);

export const commandRejected = style([commandHistoryItem, {
  background: 'rgba(239, 68, 68, 0.1)',
  border: `1px solid rgba(239, 68, 68, 0.2)`
}]);

export const commandExecuting = style([commandHistoryItem, {
  background: 'rgba(59, 130, 246, 0.1)',
  border: `1px solid rgba(59, 130, 246, 0.2)`,
  animation: `${pulse} 1.5s ease-in-out infinite`
}]);

// Sandbox shield
export const sandboxShield = style({
  background: 'rgba(139, 92, 246, 0.1)',
  border: `2px solid ${theme.colors.jona}`,
  borderRadius: theme.borderRadius.xl,
  padding: theme.spacing.xl,
  position: 'relative',
  overflow: 'hidden',
  
  ':before': {
    content: '""',
    position: 'absolute',
    top: '-2px',
    left: '-2px',
    right: '-2px',
    bottom: '-2px',
    background: `linear-gradient(45deg, ${theme.colors.jona}, ${theme.colors.primary}, ${theme.colors.jona})`,
    borderRadius: theme.borderRadius.xl,
    zIndex: -1,
    animation: `${glow} 2s ease-in-out infinite`
  }
});

// Gradient text
export const gradientText = style({
  background: `linear-gradient(45deg, ${theme.colors.primary}, ${theme.colors.jona}, ${theme.colors.alba})`,
  backgroundSize: '200% 200%',
  backgroundClip: 'text',
  WebkitBackgroundClip: 'text',
  color: 'transparent',
  animation: `${rotateGradient} 5s ease infinite`,
  fontWeight: 'bold'
});

// Processing animation
export const processingAnimation = style({
  animation: `${pulse} 1.5s ease-in-out infinite`
});

// Safe glow animation
export const safeGlow = style({
  animation: `${glow} 2s ease-in-out infinite`
});

// Button base (for use with CVA)
export const buttonBase = style({
  padding: `${theme.spacing.sm} ${theme.spacing.lg}`,
  borderRadius: theme.borderRadius.md,
  fontFamily: 'monospace',
  fontSize: '14px',
  fontWeight: 'bold',
  border: '1px solid',
  cursor: 'pointer',
  transition: 'all 0.2s ease',
  textTransform: 'uppercase',
  letterSpacing: '0.5px',
  
  ':focus': {
    outline: 'none',
    boxShadow: '0 0 0 2px rgba(59, 130, 246, 0.2)'
  },
  
  ':disabled': {
    opacity: 0.5,
    cursor: 'not-allowed',
    pointerEvents: 'none'
  }
});

// Terminal header
export const terminalHeader = style({
  display: 'flex',
  alignItems: 'center',
  padding: theme.spacing.md,
  borderBottom: `1px solid ${theme.colors.background.tertiary}`,
  background: 'rgba(0, 0, 0, 0.3)'
});

export const terminalDot = style({
  width: '12px',
  height: '12px',
  borderRadius: '50%',
  marginRight: theme.spacing.xs
});

export const terminalDotRed = style([terminalDot, {
  background: theme.colors.danger
}]);

export const terminalDotYellow = style([terminalDot, {
  background: theme.colors.warning
}]);

export const terminalDotGreen = style([terminalDot, {
  background: theme.colors.success
}]);


