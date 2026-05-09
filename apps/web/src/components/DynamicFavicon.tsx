'use client';

import { useEffect, useRef, useCallback } from 'react';
import { usePathname } from 'next/navigation';

// Type definition for window with favicon state setter
interface WindowWithFavicon extends Window {
  setFaviconState?: (state: FaviconState, duration?: number) => void;
}

/**
 * DYNAMIC FAVICON - Narrative Icon Based on User Navigation & Behavior
 * 
 * The favicon changes based on:
 * - Current page/route (modules, dashboard, analytics, etc.)
 * - Time of day (morning/afternoon/evening/night)
 * - User activity (idle, active, focused)
 * - System status (online, offline, loading)
 * 
 * Each module has its own unique favicon that tells the user's story!
 * This creates a living, breathing brand experience that follows the user journey.
 */

type FaviconState = 
    | 'default'      // 🧠 Standard brain - Home/Dashboard
  | 'thinking'     // 🧠💭 Processing/loading
    | 'happy'        // 😊 Mood module
    | 'focused'      // 🎯 Focus Timer module
    | 'sleeping'     // 😴 User idle / Sleep tracking
    | 'night'        // 🌙 Night mode / Late hours
    | 'morning'      // ☀️ Morning energy
    | 'alert'        // ⚠️ Notification/alert
    | 'success'      // ✅ Task completed
    | 'offline'      // 📴 No internet
    | 'analyzing'    // 📊 Analytics module
    | 'habits'       // 📋 Daily Habits module
    | 'meditation'   // 🧘 Mindfulness/Meditation
    | 'phone'        // 📱 Phone Sensors module
    | 'face'         // 👁️ Face Detection module
    | 'lifestyle'    // 🌿 Lifestyle modules
    | 'economy'      // 💰 Economy module
    | 'marketplace'  // 🛒 Marketplace
    | 'settings'     // ⚙️ Settings
    | 'music'        // 🎵 Music/Audio
    | 'health';      // ❤️ Health tracking

interface FaviconColors {
    primary: string;
    secondary: string;
  background: string;
  glow?: string;
    emoji: string;
}

const STATE_CONFIG: Record<FaviconState, FaviconColors> = {
    // Core states
    default: { primary: '#8b5cf6', secondary: '#a78bfa', background: '#1e1b4b', emoji: '🧠' },
    thinking: { primary: '#8b5cf6', secondary: '#a78bfa', background: '#1e1b4b', glow: '#c4b5fd', emoji: '💭' },
    success: { primary: '#22c55e', secondary: '#4ade80', background: '#052e16', glow: '#86efac', emoji: '✅' },
    alert: { primary: '#ef4444', secondary: '#f87171', background: '#450a0a', glow: '#fca5a5', emoji: '⚠️' },
    offline: { primary: '#6b7280', secondary: '#9ca3af', background: '#1f2937', emoji: '📴' },

    // Time-based states
    night: { primary: '#6366f1', secondary: '#818cf8', background: '#0f0d24', glow: '#a5b4fc', emoji: '🌙' },
    morning: { primary: '#f97316', secondary: '#fb923c', background: '#431407', glow: '#fdba74', emoji: '☀️' },
    sleeping: { primary: '#64748b', secondary: '#94a3b8', background: '#1e293b', emoji: '😴' },

    // Module-specific states - UNIQUE FAVICONS PER MODULE!
    happy: { primary: '#10b981', secondary: '#34d399', background: '#022c22', glow: '#6ee7b7', emoji: '😊' },
    focused: { primary: '#f59e0b', secondary: '#fbbf24', background: '#451a03', glow: '#fcd34d', emoji: '🎯' },
    analyzing: { primary: '#0ea5e9', secondary: '#38bdf8', background: '#082f49', glow: '#7dd3fc', emoji: '📊' },
    habits: { primary: '#06b6d4', secondary: '#22d3ee', background: '#083344', glow: '#67e8f9', emoji: '📋' },
    meditation: { primary: '#14b8a6', secondary: '#2dd4bf', background: '#042f2e', glow: '#5eead4', emoji: '🧘' },
    phone: { primary: '#3b82f6', secondary: '#60a5fa', background: '#1e3a5f', glow: '#93c5fd', emoji: '📱' },
    face: { primary: '#ec4899', secondary: '#f472b6', background: '#500724', glow: '#f9a8d4', emoji: '👁️' },
    lifestyle: { primary: '#84cc16', secondary: '#a3e635', background: '#1a2e05', glow: '#bef264', emoji: '🌿' },
    economy: { primary: '#eab308', secondary: '#facc15', background: '#422006', glow: '#fde047', emoji: '💰' },
    marketplace: { primary: '#f43f5e', secondary: '#fb7185', background: '#4c0519', glow: '#fda4af', emoji: '🛒' },
    settings: { primary: '#64748b', secondary: '#94a3b8', background: '#1e293b', glow: '#cbd5e1', emoji: '⚙️' },
    music: { primary: '#a855f7', secondary: '#c084fc', background: '#3b0764', glow: '#d8b4fe', emoji: '🎵' },
    health: { primary: '#ef4444', secondary: '#f87171', background: '#450a0a', glow: '#fca5a5', emoji: '❤️' },
};

export function DynamicFavicon() {
    const pathname = usePathname();
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const lastActivityRef = useRef<number>(Date.now());
  const mouseMovementRef = useRef<number>(0);
  const currentStateRef = useRef<FaviconState>('default');
  const animationFrameRef = useRef<number>(0);
  const pulsePhaseRef = useRef<number>(0);
  const lastStateRef = useRef<FaviconState | null>(null);
  const lastDrawTimeRef = useRef<number>(0);

    // 🎯 PRIMARY: Determine state based on CURRENT ROUTE/PAGE
    const getRouteBasedState = useCallback((): FaviconState => {
        if (!pathname) return 'default';

        const path = pathname.toLowerCase();

        // Module-specific favicons - the user sees different icon per module!
        if (path.includes('mood') || path.includes('journal')) return 'happy';
        if (path.includes('focus') || path.includes('timer')) return 'focused';
        if (path.includes('analytics') || path.includes('reporting') || path.includes('dashboard')) return 'analyzing';
        if (path.includes('habits') || path.includes('daily')) return 'habits';
        if (path.includes('meditation') || path.includes('mindfulness') || path.includes('breathing')) return 'meditation';
        if (path.includes('phone') || path.includes('sensor')) return 'phone';
        if (path.includes('face') || path.includes('camera') || path.includes('detection')) return 'face';
        if (path.includes('lifestyle') || path.includes('wellness')) return 'lifestyle';
        if (path.includes('economy') || path.includes('billing') || path.includes('subscription')) return 'economy';
        if (path.includes('marketplace') || path.includes('store') || path.includes('shop')) return 'marketplace';
        if (path.includes('settings') || path.includes('config') || path.includes('preferences')) return 'settings';
        if (path.includes('music') || path.includes('audio') || path.includes('sound')) return 'music';
        if (path.includes('health') || path.includes('heart') || path.includes('vital')) return 'health';
        if (path.includes('sleep')) return 'sleeping';

        return 'default';
    }, [pathname]);

    // Determine state based on time of day (fallback)
  const getTimeBasedState = useCallback((): FaviconState => {
    const hour = new Date().getHours();
    if (hour >= 5 && hour < 9) return 'morning';
    if (hour >= 22 || hour < 5) return 'night';
    return 'default';
  }, []);

    // Determine final state with priority: Route > Activity > Time
    const getFinalState = useCallback((): FaviconState => {
    const now = Date.now();
    const idleTime = now - lastActivityRef.current;
    
      // Check offline first
      if (typeof navigator !== 'undefined' && !navigator.onLine) return 'offline';

      // Idle for more than 5 minutes = sleeping (overrides route)
    if (idleTime > 5 * 60 * 1000) return 'sleeping';
    
      // Route-based state takes priority when user is active
      const routeState = getRouteBasedState();
      if (routeState !== 'default') return routeState;
    
      // Fall back to time-based
    return getTimeBasedState();
  }, [getRouteBasedState, getTimeBasedState]);

    // Draw the emoji-based favicon with animated glow
  const drawFavicon = useCallback((state: FaviconState, pulse: number) => {
    if (!canvasRef.current) return;
    
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const size = 64;
    canvas.width = size;
    canvas.height = size;
    
      const config = STATE_CONFIG[state];
    const pulseIntensity = Math.sin(pulse) * 0.5 + 0.5;

    // Clear canvas
    ctx.clearRect(0, 0, size, size);

      // Circular background with gradient
      const bgGradient = ctx.createRadialGradient(
          size / 2, size / 2, 0,
          size / 2, size / 2, size / 2
      );
      bgGradient.addColorStop(0, config.primary + '40');
      bgGradient.addColorStop(0.7, config.background);
      bgGradient.addColorStop(1, config.background);
    
      ctx.fillStyle = bgGradient;
    ctx.beginPath();
      ctx.arc(size / 2, size / 2, size / 2 - 2, 0, Math.PI * 2);
    ctx.fill();

      // Animated glow ring for active states
      if (config.glow) {
          const glowSize = 4 + pulseIntensity * 3;
          ctx.strokeStyle = config.glow;
          ctx.lineWidth = glowSize;
          ctx.globalAlpha = 0.3 + pulseIntensity * 0.4;
          ctx.beginPath();
        ctx.arc(size / 2, size / 2, size / 2 - 6, 0, Math.PI * 2);
        ctx.stroke();
          ctx.globalAlpha = 1;
      }

      // Border
      ctx.strokeStyle = config.primary;
      ctx.lineWidth = 3;
    ctx.beginPath();
      ctx.arc(size / 2, size / 2, size / 2 - 4, 0, Math.PI * 2);
    ctx.stroke();

      // Draw the emoji in center
      ctx.font = '32px "Segoe UI Emoji", "Apple Color Emoji", "Noto Color Emoji", sans-serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(config.emoji, size / 2, size / 2 + 2);

      // Update browser favicon
      const link = document.querySelector<HTMLLinkElement>('link[rel="icon"]') ||
          document.createElement('link');
      link.rel = 'icon';
      link.type = 'image/png';
      link.href = canvas.toDataURL('image/png');
    
      if (!document.querySelector('link[rel="icon"]')) {
          document.head.appendChild(link);
      }

      // Also update title with emoji for extra visibility
      const baseTitle = 'Kloud';
      document.title = `${config.emoji} ${baseTitle}`;
  }, []);

  // Animation loop - throttled to reduce CPU usage
  const animate = useCallback(() => {
    const now = Date.now();
    const timeSinceLastDraw = now - lastDrawTimeRef.current;

    // Only update every 500ms instead of every frame (60fps -> 2fps)
    if (timeSinceLastDraw >= 500) {
      pulsePhaseRef.current += 0.5;
      const newState = getFinalState();

      // Only redraw if state changed or has glow animation
      if (newState !== lastStateRef.current || STATE_CONFIG[newState].glow) {
        currentStateRef.current = newState;
        lastStateRef.current = newState;
        drawFavicon(newState, pulsePhaseRef.current);
      }
      lastDrawTimeRef.current = now;
    }
    
    animationFrameRef.current = requestAnimationFrame(animate);
  }, [getFinalState, drawFavicon]);

  // Track user activity
  useEffect(() => {
    const canvas = document.createElement('canvas');
    canvasRef.current = canvas;

    const handleActivity = () => {
      lastActivityRef.current = Date.now();
    };

    const handleMouseMove = () => {
      mouseMovementRef.current++;
      lastActivityRef.current = Date.now();
    };

    // Reset mouse movement counter periodically
    const resetInterval = setInterval(() => {
      mouseMovementRef.current = 0;
    }, 10000);

    // Online/offline detection
    const handleOnline = () => {
      currentStateRef.current = 'success';
      drawFavicon('success', 0);
      setTimeout(() => {
        currentStateRef.current = getFinalState();
      }, 2000);
    };

    const handleOffline = () => {
      currentStateRef.current = 'offline';
      drawFavicon('offline', 0);
    };

    // Event listeners
    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('keydown', handleActivity);
    window.addEventListener('click', handleActivity);
    window.addEventListener('scroll', handleActivity);
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Check online status
    if (!navigator.onLine) {
      currentStateRef.current = 'offline';
    }

    // Start animation
    animationFrameRef.current = requestAnimationFrame(animate);

    // Initial draw
    drawFavicon(getFinalState(), 0);

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('keydown', handleActivity);
      window.removeEventListener('click', handleActivity);
      window.removeEventListener('scroll', handleActivity);
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      clearInterval(resetInterval);
      cancelAnimationFrame(animationFrameRef.current);
    };
  }, [animate, drawFavicon, getFinalState]);

  // Re-draw when route changes
  useEffect(() => {
    const newState = getFinalState();
    currentStateRef.current = newState;
    drawFavicon(newState, 0);
  }, [pathname, drawFavicon, getFinalState]);

  // Expose methods for external state changes
  useEffect(() => {
    // Global function to trigger favicon states from anywhere
    (window as WindowWithFavicon).setFaviconState = (state: FaviconState, duration?: number) => {
      currentStateRef.current = state;
      drawFavicon(state, pulsePhaseRef.current);
      
      if (duration) {
        setTimeout(() => {
          currentStateRef.current = getFinalState();
        }, duration);
      }
    };

    return () => {
      delete (window as WindowWithFavicon).setFaviconState;
    };
  }, [drawFavicon, getFinalState]);

  return null; // This component renders nothing visually
}

// Export utility functions for triggering states programmatically
export const faviconStates = {
  thinking: () => (window as WindowWithFavicon).setFaviconState?.('thinking'),
  success: () => (window as WindowWithFavicon).setFaviconState?.('success', 3000),
  alert: () => (window as WindowWithFavicon).setFaviconState?.('alert'),
  analyzing: () => (window as WindowWithFavicon).setFaviconState?.('analyzing'),
  happy: () => (window as WindowWithFavicon).setFaviconState?.('happy', 5000),
};

export default DynamicFavicon;
