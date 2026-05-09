// Shared constants
export const API_ENDPOINTS = {
  AGI: '/api/agi',
  kloud: '/api/kloud', 
  DASHBOARD: '/api/dashboard',
  WORLD_BRAIN: '/api/world-brain'
} as const

export const SERVICE_PORTS = {
  API: 8000,
  WEB: 3000
} as const

export const EEG_CHANNELS = {
  STANDARD_10_20: [
    'Fp1', 'Fp2', 'F3', 'F4', 'C3', 'C4',
    'P3', 'P4', 'O1', 'O2', 'F7', 'F8',
    'T3', 'T4', 'T5', 'T6', 'Fz', 'Cz', 'Pz'
  ],
  HIGH_DENSITY: Array.from({ length: 64 }, (_, i) => `Ch${i + 1}`)
} as const

export const AUDIO_FORMATS = {
  INPUT: ['eeg', 'csv', 'json'],
  OUTPUT: ['wav', 'mp3', 'flac', 'ogg'],
  STREAMING: ['websocket', 'sse', 'webrtc']
} as const

export const THEME_COLORS = {
  PRIMARY: '#3b82f6',
  SECONDARY: '#6366f1', 
  SUCCESS: '#10b981',
  WARNING: '#f59e0b',
  ERROR: '#ef4444',
  DARK: '#1f2937',
  LIGHT: '#f9fafb'
} as const

