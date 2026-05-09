/**
 * Kloud Cloud TypeScript SDK
 * @version 1.0.0
 * @description Official TypeScript SDK for Kloud Cloud API
 * 
 * Features:
 * - Neural harmonic processing APIs
 * - EEG signal analysis
 * - ASI Trinity monitoring
 * - Real-time data streaming
 * - Billing and subscription management
 */

// =============================================================================
// CONFIGURATION
// =============================================================================

export interface KloudConfig {
  apiKey: string;
  baseUrl?: string;
  timeout?: number;
  retries?: number;
}

const DEFAULT_CONFIG = {
  baseUrl: process.env.KLOUD_API_URL || 'https://api.kloud.com',
  timeout: 30000,
  retries: 3
};

// =============================================================================
// TYPES & INTERFACES
// =============================================================================

// Core Types
export interface HealthResponse {
  service: string;
  status: 'healthy' | 'degraded' | 'unhealthy';
  version: string;
  timestamp: string;
  instance_id: string;
  uptime_app_seconds: number;
  system: SystemMetrics;
  redis: ServiceStatus;
  database: ServiceStatus;
  environment: 'development' | 'staging' | 'production';
}

export interface StatusResponse {
  timestamp: string;
  instance_id: string;
  status: 'operational' | 'degraded' | 'maintenance';
  uptime: string;
  memory: {
    used: number;
    total: number;
  };
  system: SystemMetrics;
  redis: ServiceStatus;
  database: ServiceStatus;
}

export interface SystemMetrics {
  cpu_percent: number;
  memory_percent: number;
  memory_total: number;
  memory_available: number;
  disk_percent: number;
  disk_total: number;
  net_bytes_sent: number;
  net_bytes_recv: number;
  processes: number;
  hostname: string;
  boot_time: number;
  uptime_seconds: number;
}

export interface ServiceStatus {
  status: 'connected' | 'disconnected' | 'degraded';
  message?: string;
  connected_clients?: number;
  used_memory?: string;
  uptime_seconds?: number;
  response_time_ms?: number;
}

// Brain Types
export interface HarmonicAnalysis {
  frequencies: number[];
  amplitudes: number[];
  phases: number[];
  coherence_score: number;
  dominant_frequency: number;
  harmonic_ratios: number[];
}

export interface BrainSyncResult {
  sync_level: number;
  alpha_power: number;
  beta_power: number;
  theta_power: number;
  delta_power: number;
  gamma_power: number;
  overall_coherence: number;
  recommendations: string[];
}

export interface CortexAnalysisResult {
  pattern_type: string;
  confidence: number;
  features: Record<string, number>;
  classification: string;
  anomalies: string[];
}

// EEG Types
export interface EEGSession {
  session_id: string;
  channels: number;
  sample_rate: number;
  duration_seconds: number;
  started_at: string;
  status: 'recording' | 'paused' | 'completed';
}

export interface EEGData {
  timestamp: string;
  channels: Record<string, number[]>;
  quality_score: number;
  artifacts_detected: boolean;
}

export interface EEGFrequencyBands {
  delta: { min: number; max: number; power: number };
  theta: { min: number; max: number; power: number };
  alpha: { min: number; max: number; power: number };
  beta: { min: number; max: number; power: number };
  gamma: { min: number; max: number; power: number };
}

// ASI Types
export interface ASIStatus {
  asi_active: boolean;
  components: {
    alba: ComponentStatus;
    albi: ComponentStatus;
    jona: ComponentStatus;
  };
  overall_health: number;
  last_sync: string;
}

export interface ComponentStatus {
  active: boolean;
  health: number;
  last_heartbeat: string;
  metrics: Record<string, number>;
}

export interface ALBAMetrics {
  network_latency_ms: number;
  active_streams: number;
  buffer_utilization: number;
  throughput_mbps: number;
}

export interface ALBIMetrics {
  neural_load: number;
  pattern_matches: number;
  processing_queue: number;
  goroutines: number;
}

export interface JONAMetrics {
  coordination_score: number;
  active_tasks: number;
  completed_today: number;
  error_rate: number;
}

// Billing Types
export interface BillingPlan {
  id: string;
  name: string;
  price_monthly: number;
  currency: string;
  features: string[];
  rate_limit: number;
  api_calls_per_day: number;
}

export interface Subscription {
  subscription_id: string;
  plan: BillingPlan;
  status: 'active' | 'cancelled' | 'past_due';
  current_period_start: string;
  current_period_end: string;
  usage: {
    api_calls_today: number;
    api_calls_this_month: number;
  };
}

// Error Types
export interface APIError {
  error: {
    code: string;
    message: string;
    details?: string;
    timestamp: string;
    request_id: string;
  };
}

// =============================================================================
// HTTP CLIENT
// =============================================================================

class HttpClient {
  private config: Required<KloudConfig>;

  constructor(config: KloudConfig) {
    this.config = {
      ...DEFAULT_CONFIG,
      ...config
    } as Required<KloudConfig>;
  }

  private async request<T>(
    method: string,
    path: string,
    body?: unknown,
    customHeaders?: Record<string, string>
  ): Promise<T> {
    const url = `${this.config.baseUrl}${path}`;
    
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      'X-API-Key': this.config.apiKey,
      ...customHeaders
    };

    let lastError: Error | null = null;
    
    for (let attempt = 0; attempt < this.config.retries; attempt++) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.config.timeout);

        const response = await fetch(url, {
          method,
          headers,
          body: body ? JSON.stringify(body) : undefined,
          signal: controller.signal
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
          const errorData = await response.json() as APIError;
          throw new KloudError(
            errorData.error.message,
            errorData.error.code,
            response.status
          );
        }

        return await response.json() as T;
      } catch (error) {
        lastError = error as Error;
        if (attempt < this.config.retries - 1) {
          await this.delay(Math.pow(2, attempt) * 1000);
        }
      }
    }

    throw lastError || new Error('Request failed');
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  async get<T>(path: string): Promise<T> {
    return this.request<T>('GET', path);
  }

  async post<T>(path: string, body?: unknown): Promise<T> {
    return this.request<T>('POST', path, body);
  }

  async put<T>(path: string, body?: unknown): Promise<T> {
    return this.request<T>('PUT', path, body);
  }

  async delete<T>(path: string): Promise<T> {
    return this.request<T>('DELETE', path);
  }
}

// =============================================================================
// ERROR HANDLING
// =============================================================================

export class KloudError extends Error {
  code: string;
  statusCode: number;

  constructor(message: string, code: string, statusCode: number) {
    super(message);
    this.name = 'KloudError';
    this.code = code;
    this.statusCode = statusCode;
  }
}

// =============================================================================
// API MODULES
// =============================================================================

/**
 * Core API - System health and status
 */
class CoreAPI {
  constructor(private client: HttpClient) {}

  /** Get system health status */
  async health(): Promise<HealthResponse> {
    return this.client.get('/health');
  }

  /** Get detailed system status */
  async status(): Promise<StatusResponse> {
    return this.client.get('/status');
  }

  /** Simple ping check */
  async ping(): Promise<{ pong: boolean; timestamp: string }> {
    return this.client.get('/ping');
  }
}

/**
 * Brain API - Neural harmonic processing
 */
class BrainAPI {
  constructor(private client: HttpClient) {}

  /** Analyze harmonic patterns */
  async analyzeHarmonics(data: { 
    frequencies: number[]; 
    amplitudes: number[] 
  }): Promise<HarmonicAnalysis> {
    return this.client.post('/brain/harmonics/analyze', data);
  }

  /** Get brain synchronization metrics */
  async getSync(): Promise<BrainSyncResult> {
    return this.client.get('/brain/sync');
  }

  /** Process cortex patterns */
  async analyzeCortex(data: {
    pattern_data: number[];
    analysis_type: 'quick' | 'deep' | 'realtime';
  }): Promise<CortexAnalysisResult> {
    return this.client.post('/brain/cortex/analyze', data);
  }

  /** Ask the brain AI assistant */
  async ask(question: string, context?: string): Promise<{
    answer: string;
    modules_used: string[];
    processing_time_ms: number;
  }> {
    return this.client.post('/brain/ask', { question, context });
  }
}

/**
 * EEG API - EEG data collection and processing
 */
class EEGAPI {
  constructor(private client: HttpClient) {}

  /** Start a new EEG recording session */
  async startSession(params: {
    channels: number;
    sample_rate: number;
  }): Promise<EEGSession> {
    return this.client.post('/eeg/sessions/start', params);
  }

  /** Stop an EEG session */
  async stopSession(sessionId: string): Promise<EEGSession> {
    return this.client.post(`/eeg/sessions/${sessionId}/stop`);
  }

  /** Get session data */
  async getSessionData(sessionId: string): Promise<EEGData[]> {
    return this.client.get(`/eeg/sessions/${sessionId}/data`);
  }

  /** Analyze frequency bands */
  async analyzeFrequencies(sessionId: string): Promise<EEGFrequencyBands> {
    return this.client.get(`/eeg/sessions/${sessionId}/frequencies`);
  }

  /** Get all active sessions */
  async listSessions(): Promise<EEGSession[]> {
    return this.client.get('/eeg/sessions');
  }
}

/**
 * ASI API - ASI Trinity system interface
 */
class ASIAPI {
  constructor(private client: HttpClient) {}

  /** Get overall ASI status */
  async getStatus(): Promise<ASIStatus> {
    return this.client.get('/asi/status');
  }

  /** Get ASI health */
  async getHealth(): Promise<{ healthy: boolean; components: Record<string, boolean> }> {
    return this.client.get('/asi/health');
  }

  /** Get ALBA metrics */
  async getALBAMetrics(): Promise<ALBAMetrics> {
    return this.client.get('/asi/alba/metrics');
  }

  /** Get ALBI metrics */
  async getALBIMetrics(): Promise<ALBIMetrics> {
    return this.client.get('/asi/albi/metrics');
  }

  /** Get JONA metrics */
  async getJONAMetrics(): Promise<JONAMetrics> {
    return this.client.get('/asi/jona/metrics');
  }

  /** Trigger manual sync */
  async triggerSync(): Promise<{ synced: boolean; timestamp: string }> {
    return this.client.post('/asi/sync');
  }
}

/**
 * Billing API - Payment and subscription management
 */
class BillingAPI {
  constructor(private client: HttpClient) {}

  /** Get available plans */
  async getPlans(): Promise<BillingPlan[]> {
    return this.client.get('/billing/plans');
  }

  /** Get current subscription */
  async getSubscription(): Promise<Subscription> {
    return this.client.get('/billing/subscription');
  }

  /** Create checkout session */
  async createCheckout(planId: string): Promise<{ checkout_url: string; session_id: string }> {
    return this.client.post('/billing/checkout', { plan_id: planId });
  }

  /** Get usage statistics */
  async getUsage(): Promise<{
    api_calls_today: number;
    api_calls_this_month: number;
    rate_limit_remaining: number;
    reset_at: string;
  }> {
    return this.client.get('/billing/usage');
  }

  /** Cancel subscription */
  async cancelSubscription(): Promise<{ cancelled: boolean; effective_date: string }> {
    return this.client.post('/billing/subscription/cancel');
  }
}

/**
 * Reporting API - Docker and system metrics
 * Uses port 8001
 */
class ReportingAPI {
  private baseUrl: string;
  private apiKey: string;

  constructor(apiKey: string, baseUrl: string = process.env.KLOUD_REPORTING_URL || 'https://reporting.kloud.com') {
    this.apiKey = apiKey;
    this.baseUrl = baseUrl;
  }

  private async request<T>(path: string): Promise<T> {
    const response = await fetch(`${this.baseUrl}${path}`, {
      headers: { 'X-API-Key': this.apiKey }
    });
    return response.json() as Promise<T>;
  }

  /** Get Docker containers */
  async getDockerContainers(): Promise<{
    containers: Array<{
      id: string;
      name: string;
      status: string;
      image: string;
      ports: string;
      created: string;
    }>;
    total: number;
    healthy: number;
    data_type: string;
  }> {
    return this.request('/api/reporting/docker-containers');
  }

  /** Get Docker stats */
  async getDockerStats(): Promise<{
    stats: Array<{
      container: string;
      cpu_percent: number;
      memory_usage: string;
      network_rx: string;
      network_tx: string;
    }>;
  }> {
    return this.request('/api/reporting/docker-stats');
  }

  /** Get system metrics */
  async getSystemMetrics(): Promise<{
    cpu: number;
    memory: number;
    disk: number;
    uptime: string;
  }> {
    return this.request('/api/reporting/system-metrics');
  }
}

/**
 * Excel API - Excel and reporting operations
 * Uses port 8002
 */
class ExcelAPI {
  private baseUrl: string;
  private apiKey: string;

  constructor(apiKey: string, baseUrl: string = process.env.KLOUD_EXCEL_URL || 'https://excel.kloud.com') {
    this.apiKey = apiKey;
    this.baseUrl = baseUrl;
  }

  private async request<T>(method: string, path: string, body?: unknown): Promise<T> {
    const response = await fetch(`${this.baseUrl}${path}`, {
      method,
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': this.apiKey
      },
      body: body ? JSON.stringify(body) : undefined
    });
    return response.json() as Promise<T>;
  }

  /** Generate Excel report */
  async generateReport(params: {
    report_type: string;
    date_range?: { start: string; end: string };
    format?: 'xlsx' | 'csv';
  }): Promise<{ download_url: string; expires_at: string }> {
    return this.request('POST', '/api/excel/generate', params);
  }

  /** Get report templates */
  async getTemplates(): Promise<Array<{
    id: string;
    name: string;
    description: string;
  }>> {
    return this.request('GET', '/api/excel/templates');
  }

  /** Regenerate Excel data */
  async regenerate(): Promise<{ success: boolean; message: string }> {
    return this.request('POST', '/api/excel/regenerate');
  }
}

// =============================================================================
// MAIN SDK CLASS
// =============================================================================

/**
 * Kloud Cloud SDK
 * 
 * @example
 * ```typescript
 * const kloud = new Kloud({
 *   apiKey: 'your-api-key'
 * });
 * 
 * // Get system health
 * const health = await kloud.core.health();
 * 
 * // Analyze brain harmonics
 * const analysis = await kloud.brain.analyzeHarmonics({
 *   frequencies: [8, 10, 12, 14],
 *   amplitudes: [0.5, 0.8, 0.6, 0.4]
 * });
 * 
 * // Get ASI Trinity status
 * const asiStatus = await kloud.asi.getStatus();
 * ```
 */
export class Kloud {
  private client: HttpClient;
  
  // API Modules
  public core: CoreAPI;
  public brain: BrainAPI;
  public eeg: EEGAPI;
  public asi: ASIAPI;
  public billing: BillingAPI;
  public reporting: ReportingAPI;
  public excel: ExcelAPI;

  constructor(config: KloudConfig) {
    this.client = new HttpClient(config);
    
    // Initialize API modules
    this.core = new CoreAPI(this.client);
    this.brain = new BrainAPI(this.client);
    this.eeg = new EEGAPI(this.client);
    this.asi = new ASIAPI(this.client);
    this.billing = new BillingAPI(this.client);
    
    // Separate microservices
    this.reporting = new ReportingAPI(config.apiKey);
    this.excel = new ExcelAPI(config.apiKey);
  }

  /**
   * Quick health check
   */
  async isHealthy(): Promise<boolean> {
    try {
      const health = await this.core.health();
      return health.status === 'healthy';
    } catch {
      return false;
    }
  }
}

// =============================================================================
// EXPORTS
// =============================================================================

export default Kloud;

// Named exports for convenience
export { Kloud as KloudClient };

