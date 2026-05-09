/**
 * DYNAMIC FAVICON API - Core Endpoint
 * 
 * This isolated API provides favicon state management and icon generation.
 * Independent of other services for reliability.
 * 
 * Endpoints:
 * GET /api/favicon - Get current state info
 * GET /api/favicon?state=focused - Get specific favicon as PNG
 * POST /api/favicon - Set custom state
 */

import { NextRequest, NextResponse } from 'next/server';

// Favicon states with their configurations
const FAVICON_STATES = {
  // Core states
  default:    { emoji: '🧠', primary: '#8b5cf6', background: '#1e1b4b', label: 'Kloud Brain' },
  thinking:   { emoji: '💭', primary: '#8b5cf6', background: '#1e1b4b', label: 'Processing' },
  success:    { emoji: '✅', primary: '#22c55e', background: '#052e16', label: 'Success' },
  alert:      { emoji: '⚠️', primary: '#ef4444', background: '#450a0a', label: 'Alert' },
  offline:    { emoji: '📴', primary: '#6b7280', background: '#1f2937', label: 'Offline' },
  
  // Time-based states
  night:      { emoji: '🌙', primary: '#6366f1', background: '#0f0d24', label: 'Night Mode' },
  morning:    { emoji: '☀️', primary: '#f97316', background: '#431407', label: 'Morning' },
  sleeping:   { emoji: '😴', primary: '#64748b', background: '#1e293b', label: 'Idle' },
  
  // Module-specific states
  happy:      { emoji: '😊', primary: '#10b981', background: '#022c22', label: 'Mood Journal' },
  focused:    { emoji: '🎯', primary: '#f59e0b', background: '#451a03', label: 'Focus Timer' },
  analyzing:  { emoji: '📊', primary: '#0ea5e9', background: '#082f49', label: 'Analytics' },
  habits:     { emoji: '📋', primary: '#06b6d4', background: '#083344', label: 'Daily Habits' },
  meditation: { emoji: '🧘', primary: '#14b8a6', background: '#042f2e', label: 'Meditation' },
  phone:      { emoji: '📱', primary: '#3b82f6', background: '#1e3a5f', label: 'Phone Sensors' },
  face:       { emoji: '👁️', primary: '#ec4899', background: '#500724', label: 'Face Detection' },
  lifestyle:  { emoji: '🌿', primary: '#84cc16', background: '#1a2e05', label: 'Lifestyle' },
  economy:    { emoji: '💰', primary: '#eab308', background: '#422006', label: 'Economy' },
  marketplace:{ emoji: '🛒', primary: '#f43f5e', background: '#4c0519', label: 'Marketplace' },
  settings:   { emoji: '⚙️', primary: '#64748b', background: '#1e293b', label: 'Settings' },
  music:      { emoji: '🎵', primary: '#a855f7', background: '#3b0764', label: 'Music' },
  health:     { emoji: '❤️', primary: '#ef4444', background: '#450a0a', label: 'Health' },
} as const;

type FaviconState = keyof typeof FAVICON_STATES;

// Route to state mapping
const ROUTE_STATE_MAP: Record<string, FaviconState> = {
  'mood': 'happy',
  'journal': 'happy',
  'focus': 'focused',
  'timer': 'focused',
  'analytics': 'analyzing',
  'reporting': 'analyzing',
  'dashboard': 'analyzing',
  'habits': 'habits',
  'daily': 'habits',
  'meditation': 'meditation',
  'mindfulness': 'meditation',
  'breathing': 'meditation',
  'phone': 'phone',
  'sensor': 'phone',
  'face': 'face',
  'camera': 'face',
  'detection': 'face',
  'lifestyle': 'lifestyle',
  'wellness': 'lifestyle',
  'economy': 'economy',
  'billing': 'economy',
  'subscription': 'economy',
  'marketplace': 'marketplace',
  'store': 'marketplace',
  'shop': 'marketplace',
  'settings': 'settings',
  'config': 'settings',
  'preferences': 'settings',
  'music': 'music',
  'audio': 'music',
  'sound': 'music',
  'health': 'health',
  'heart': 'health',
  'vital': 'health',
  'sleep': 'sleeping',
};

/**
 * GET /api/favicon
 * Returns favicon state info or generates PNG
 */
export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const stateParam = searchParams.get('state');
  const routeParam = searchParams.get('route');
  const format = searchParams.get('format') || 'json';
  
  // Determine state from route or explicit state
  let state: FaviconState = 'default';
  
  if (stateParam && stateParam in FAVICON_STATES) {
    state = stateParam as FaviconState;
  } else if (routeParam) {
    // Find matching route
    const routeLower = routeParam.toLowerCase();
    for (const [keyword, mappedState] of Object.entries(ROUTE_STATE_MAP)) {
      if (routeLower.includes(keyword)) {
        state = mappedState;
        break;
      }
    }
    
    // Check time-based if no route match
    if (state === 'default') {
      const hour = new Date().getHours();
      if (hour >= 5 && hour < 9) state = 'morning';
      else if (hour >= 22 || hour < 5) state = 'night';
    }
  }
  
  const config = FAVICON_STATES[state];
  
  // Return JSON info
  if (format === 'json') {
    const response = NextResponse.json({
      success: true,
      state,
      config: {
        emoji: config.emoji,
        primary: config.primary,
        background: config.background,
        label: config.label,
      },
      availableStates: Object.keys(FAVICON_STATES),
      routeMappings: ROUTE_STATE_MAP,
      timestamp: new Date().toISOString(),
    });
    // Cache for 5 minutes to reduce requests
    response.headers.set('Cache-Control', 'public, max-age=300, stale-while-revalidate=60');
    return response;
  }
  
  // Return SVG favicon
  if (format === 'svg') {
    const svg = generateSVGFavicon(state);
    return new NextResponse(svg, {
      headers: {
        'Content-Type': 'image/svg+xml',
        'Cache-Control': 'public, max-age=3600, immutable',
      },
    });
  }
  
  // Return all states info
  if (format === 'all') {
    const response = NextResponse.json({
      success: true,
      states: FAVICON_STATES,
      routeMappings: ROUTE_STATE_MAP,
      currentTime: new Date().toISOString(),
      currentHour: new Date().getHours(),
      suggestedTimeState: getSuggestedTimeState(),
    });
    response.headers.set('Cache-Control', 'public, max-age=300');
    return response;
  }
  
  const response = NextResponse.json({
    success: true,
    state,
    ...config,
  });
  response.headers.set('Cache-Control', 'public, max-age=300, stale-while-revalidate=60');
  return response;
}

/**
 * POST /api/favicon
 * Trigger a temporary state change (for notifications, etc.)
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { state, duration = 3000 } = body;
    
    if (!state || !(state in FAVICON_STATES)) {
      return NextResponse.json({
        success: false,
        error: 'Invalid state',
        availableStates: Object.keys(FAVICON_STATES),
      }, { status: 400 });
    }
    
    const config = FAVICON_STATES[state as FaviconState];
    
    return NextResponse.json({
      success: true,
      message: `Favicon state set to '${state}' for ${duration}ms`,
      state,
      config,
      duration,
      // Client should revert to route-based state after duration
      revertAfter: new Date(Date.now() + duration).toISOString(),
    });
  } catch {
    return NextResponse.json({
      success: false,
      error: 'Invalid request body',
    }, { status: 400 });
  }
}

/**
 * Generate SVG favicon for a state
 */
function generateSVGFavicon(state: FaviconState): string {
  const config = FAVICON_STATES[state];
  
  return `<?xml version="1.0" encoding="UTF-8"?>
<svg width="64" height="64" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <radialGradient id="glow" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="${config.primary}" stop-opacity="0.3"/>
      <stop offset="100%" stop-color="${config.background}" stop-opacity="1"/>
    </radialGradient>
  </defs>
  
  <!-- Background circle -->
  <circle cx="32" cy="32" r="30" fill="url(#glow)"/>
  
  <!-- Border -->
  <circle cx="32" cy="32" r="28" fill="none" stroke="${config.primary}" stroke-width="3"/>
  
  <!-- Emoji (as text) -->
  <text x="32" y="40" font-size="28" text-anchor="middle" font-family="Segoe UI Emoji, Apple Color Emoji, Noto Color Emoji">${config.emoji}</text>
</svg>`;
}

/**
 * Get suggested time-based state
 */
function getSuggestedTimeState(): FaviconState {
  const hour = new Date().getHours();
  if (hour >= 5 && hour < 9) return 'morning';
  if (hour >= 22 || hour < 5) return 'night';
  return 'default';
}

