// Shared types for kloud platform
export interface ServiceStatus {
  name: string
  url: string
  status: 'online' | 'offline' | 'error'
  icon: string
}

export interface AGIResponse {
  answer: string
  confidence: number
  sources: string[]
  timestamp: string
}

export interface EEGData {
  channels: Record<string, number[]>
  sampleRate: number
  timestamp?: string
}

export interface NeuroacousticSettings {
  conversionType: 'binaural' | 'monaural' | 'surround'
  frequencyRange: [number, number]
  quality: 'low' | 'medium' | 'high' | 'lossless'
}

export interface DashboardConfig {
  theme: 'light' | 'dark'
  layout: 'grid' | 'list'
  refreshInterval: number
}

