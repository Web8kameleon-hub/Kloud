/**
 * Kloud Cloud SDK – TypeScript/JavaScript Client
 * Part of UltraWebThinking / Euroweb
 */

interface KloudConfig {
  baseUrl?: string;
  token?: string;
  timeout?: number;
}

interface RequestOptions {
  method?: "GET" | "POST" | "PUT" | "DELETE";
  headers?: Record<string, string>;
  body?: any;
  timeout?: number;
}

export class KloudClient {
  private baseUrl: string;
  private token: string | null;
  private refreshToken: string | null;
  private apiKey: string | null;
  private timeout: number;

  constructor(config: KloudConfig = {}) {
    this.baseUrl = (config.baseUrl || "https://api.kloud.com").replace(/\/$/, "");
    this.token = config.token || null;
    this.refreshToken = null;
    this.apiKey = null;
    this.timeout = config.timeout || 30000;
  }

  private getHeaders(extra: Record<string, string> = {}): Record<string, string> {
    const headers: Record<string, string> = {
      "Accept": "application/json",
      "User-Agent": "Kloud-TypeScript-SDK/1.0",
      ...extra
    };

    if (this.token) {
      headers["Authorization"] = `Bearer ${this.token}`;
    }

    if (this.apiKey) {
      headers["X-API-Key"] = this.apiKey;
    }

    return headers;
  }

  /**
   * POST /auth/login – Login with email and password
   * Automatically stores token, refreshToken, and apiKey
   */
  async login(email: string, password: string): Promise<any> {
    const response: any = await this.request("/auth/login", {
      method: "POST",
      body: { email, password }
    });

    if (response.token) {
      this.token = response.token;
    }
    if (response.refresh_token) {
      this.refreshToken = response.refresh_token;
    }
    if (response.api_key) {
      this.apiKey = response.api_key;
    }

    return response;
  }

  /**
   * POST /auth/refresh – Refresh JWT token using refresh_token
   * Automatically updates stored token
   */
  async refresh(): Promise<any> {
    if (!this.refreshToken) {
      throw new Error("No refresh token available. Call login() first.");
    }

    const response: any = await this.request("/auth/refresh", {
      method: "POST",
      body: { refresh_token: this.refreshToken }
    });

    if (response.token) {
      this.token = response.token;
    }

    return response;
  }

  /**
   * POST /auth/api-key – Create a new API key
   * Requires authentication
   */
  async createApiKey(label: string): Promise<any> {
    if (!this.token) {
      throw new Error("Authentication required. Call login() first.");
    }

    const response: any = await this.request("/auth/api-key", {
      method: "POST",
      body: { label }
    });

    if (response.api_key) {
      this.apiKey = response.api_key;
    }

    return response;
  }

  /**
   * Manually set API key (e.g., from environment variable)
   */
  setApiKey(apiKey: string): void {
    this.apiKey = apiKey;
  }

  private async request<T>(
    endpoint: string,
    options: RequestOptions = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const controller = new AbortController();
    const timeoutId = setTimeout(
      () => controller.abort(),
      options.timeout || this.timeout
    );

    const fetchOptions: RequestInit = {
      method: options.method || "GET",
      headers: options.headers || this.getHeaders(),
      signal: controller.signal
    };

    if (options.body) {
      fetchOptions.body = JSON.stringify(options.body);
    }

    try {
      const response = await fetch(url, fetchOptions);

      if (!response.ok) {
        const error = await response.text();
        throw new Error(`HTTP ${response.status}: ${error}`);
      }

      const contentType = response.headers.get("content-type");
      if (contentType?.includes("application/json")) {
        return response.json() as Promise<T>;
      }

      return response.text() as any;
    } finally {
      clearTimeout(timeoutId);
    }
  }

  setToken(token: string): void {
    this.token = token;
  }

  // ==================== Health & Status ====================

  async health(): Promise<any> {
    return this.request("/health");
  }

  async status(): Promise<any> {
    return this.request("/status");
  }

  async systemStatus(): Promise<any> {
    return this.request("/api/system-status");
  }

  async dbPing(): Promise<any> {
    return this.request("/db/ping");
  }

  async redisPing(): Promise<any> {
    return this.request("/redis/ping");
  }

  // ==================== Ask & Neural Symphony ====================

  async ask(
    question: string,
    context?: string,
    includeDetails: boolean = true
  ): Promise<any> {
    return this.request("/api/ask", {
      method: "POST",
      headers: this.getHeaders(),
      body: {
        question,
        context,
        include_details: includeDetails
      }
    });
  }

  async neuralSymphony(saveTo?: string): Promise<ArrayBuffer> {
    const headers = this.getHeaders({ Accept: "audio/wav" });
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(`${this.baseUrl}/neural-symphony`, {
        headers,
        signal: controller.signal
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const buffer = await response.arrayBuffer();

      if (saveTo && typeof window === "undefined") {
        // Node.js environment
        const fs = await import("fs");
        fs.writeFileSync(saveTo, Buffer.from(buffer));
      }

      return buffer;
    } finally {
      clearTimeout(timeoutId);
    }
  }

  // ==================== Uploads & Processing ====================

  async uploadEeg(filePath: string): Promise<any> {
    if (typeof window !== "undefined") {
      throw new Error("Use uploadEegBrowser() in browser environment");
    }

    const fs = await import("fs");
    const FormData = (await import("form-data")).default;
    const form = new FormData();
    form.append("file", fs.createReadStream(filePath));

    return this.request("/api/uploads/eeg/process", {
      method: "POST",
      headers: {
        ...this.getHeaders(),
        ...form.getHeaders()
      },
      body: form
    });
  }

  async uploadEegBrowser(file: File): Promise<any> {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${this.baseUrl}/api/uploads/eeg/process`, {
      method: "POST",
      headers: this.getHeaders(),
      body: formData
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    return response.json();
  }

  async uploadAudio(filePath: string): Promise<any> {
    if (typeof window !== "undefined") {
      throw new Error("Use uploadAudioBrowser() in browser environment");
    }

    const fs = await import("fs");
    const FormData = (await import("form-data")).default;
    const form = new FormData();
    form.append("file", fs.createReadStream(filePath));

    return this.request("/api/uploads/audio/process", {
      method: "POST",
      headers: {
        ...this.getHeaders(),
        ...form.getHeaders()
      },
      body: form
    });
  }

  async uploadAudioBrowser(file: File): Promise<any> {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${this.baseUrl}/api/uploads/audio/process`, {
      method: "POST",
      headers: this.getHeaders(),
      body: formData
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    return response.json();
  }

  // ==================== Brain Engine ====================

  async brainYoutubeInsight(videoId: string): Promise<any> {
    return this.request(`/brain/youtube/insight?video_id=${videoId}`);
  }

  async brainEnergyCheck(filePath: string): Promise<any> {
    if (typeof window !== "undefined") {
      throw new Error("Use brainEnergyCheckBrowser() in browser");
    }

    const fs = await import("fs");
    const FormData = (await import("form-data")).default;
    const form = new FormData();
    form.append("file", fs.createReadStream(filePath));

    return this.request("/brain/energy/check", {
      method: "POST",
      headers: {
        ...this.getHeaders(),
        ...form.getHeaders()
      },
      body: form
    });
  }

  async brainEnergyCheckBrowser(file: File): Promise<any> {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${this.baseUrl}/brain/energy/check`, {
      method: "POST",
      headers: this.getHeaders(),
      body: formData
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    return response.json();
  }

  async brainHarmony(filePath: string): Promise<any> {
    if (typeof window !== "undefined") {
      throw new Error("Use brainHarmonyBrowser() in browser");
    }

    const fs = await import("fs");
    const FormData = (await import("form-data")).default;
    const form = new FormData();
    form.append("file", fs.createReadStream(filePath));

    return this.request("/brain/harmony", {
      method: "POST",
      headers: {
        ...this.getHeaders(),
        ...form.getHeaders()
      },
      body: form
    });
  }

  async brainHarmonyBrowser(file: File): Promise<any> {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${this.baseUrl}/brain/harmony`, {
      method: "POST",
      headers: this.getHeaders(),
      body: formData
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    return response.json();
  }

  async brainCortexMap(): Promise<any> {
    return this.request("/brain/cortex-map");
  }

  async brainTemperature(): Promise<any> {
    return this.request("/brain/temperature");
  }

  async brainQueue(): Promise<any> {
    return this.request("/brain/queue");
  }

  async brainThreads(): Promise<any> {
    return this.request("/brain/threads");
  }

  async brainNeuralLoad(): Promise<any> {
    return this.request("/brain/neural-load");
  }

  async brainErrors(): Promise<any[]> {
    return this.request("/brain/errors");
  }

  async brainRestart(): Promise<any> {
    return this.request("/brain/restart", {
      method: "POST",
      headers: this.getHeaders()
    });
  }

  // ==================== ALBA Data Collection ====================

  async albaStatus(): Promise<any> {
    return this.request("/api/alba/status");
  }

  async albaStreamsStart(
    streamId: string,
    samplingRateHz: number = 256,
    channels?: string[],
    description?: string,
    metadata?: Record<string, any>
  ): Promise<any> {
    return this.request("/api/alba/streams/start", {
      method: "POST",
      headers: this.getHeaders(),
      body: {
        stream_id: streamId,
        sampling_rate_hz: samplingRateHz,
        channels: channels || ["C3", "C4"],
        description,
        metadata: metadata || {}
      }
    });
  }

  async albaStreamsStop(streamId: string): Promise<any> {
    return this.request(`/api/alba/streams/${streamId}/stop`, {
      method: "POST",
      headers: this.getHeaders()
    });
  }

  async albaStreamsList(): Promise<any> {
    return this.request("/api/alba/streams");
  }

  async albaStreamsData(streamId: string, limit: number = 100): Promise<any> {
    return this.request(
      `/api/alba/streams/${streamId}/data?limit=${limit}`
    );
  }

  async albaMetrics(): Promise<any> {
    return this.request("/api/alba/metrics");
  }

  async albaHealth(): Promise<any> {
    return this.request("/api/alba/health");
  }
}

// ==================== Example Usage ====================

export const exampleUsage = async () => {
  // Initialize client
  const client = new KloudClient({
    baseUrl: "https://api.kloud.com",
    token: "your-jwt-token-here"
  });

  try {
    // Check health
    const health = await client.health();
    console.log("✓ Health:", health.status);

    // Ask a question
    const answer = await client.ask("Çfarë është Kloud?");
    console.log("✓ Answer:", answer.answer.substring(0, 100) + "...");

    // Start data stream
    const stream = await client.albaStreamsStart(
      "demo-stream",
      256,
      ["C3", "C4", "Pz"]
    );
    console.log("✓ Stream started:", stream.stream_id);

    // Get stream data
    const data = await client.albaStreamsData(stream.stream_id, 10);
    console.log(`✓ Retrieved ${data.data_points.length} data points`);

    // Stop stream
    const stopped = await client.albaStreamsStop(stream.stream_id);
    console.log("✓ Stream stopped:", stopped.status);
  } catch (error) {
    console.error("✗ Error:", error);
  }
};

export default KloudClient;

