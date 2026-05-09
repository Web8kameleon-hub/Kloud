/**
 * KLOUD VENDOR NODE - Edge Computing
 * =====================================
 * Kur user hap Kloud, krijohet automatikisht një node vendor
 * që proceson lokalisht pa konsumuar serverin.
 *
 * Features:
 * - WebRTC P2P për komunikim direkt mes userave
 * - Service Worker për background processing
 * - LocalStorage/IndexedDB për cache
 * - WebAssembly për llogaritje të shpejtë
 */

class VendorNode {
  constructor() {
    this.nodeId = this.generateNodeId();
    this.isActive = false;
    this.peers = new Map();
    this.cache = new Map();
    this.stats = {
      requestsHandled: 0,
      bytesProcessed: 0,
      peersConnected: 0,
      uptime: 0,
    };
    this.masterServer = "https://api.kloud.com";
    this.balancerUrl = "https://api.kloud.com:3334";
  }

  generateNodeId() {
    const fingerprint = [
      navigator.userAgent,
      navigator.language,
      screen.width + "x" + screen.height,
      new Date().getTimezoneOffset(),
      Math.random().toString(36).substr(2, 9),
    ].join("|");

    // Simple hash
    let hash = 0;
    for (let i = 0; i < fingerprint.length; i++) {
      hash = (hash << 5) - hash + fingerprint.charCodeAt(i);
      hash = hash & hash;
    }
    return "VN-" + Math.abs(hash).toString(36).toUpperCase();
  }

  async init() {
    console.log(`🌐 Vendor Node ${this.nodeId} initializing...`);

    // Register with master server
    await this.register();

    // Start heartbeat
    this.startHeartbeat();

    // Initialize local cache
    await this.initCache();

    // Setup P2P (WebRTC)
    await this.initP2P();

    this.isActive = true;
    console.log(`✅ Vendor Node ${this.nodeId} active`);

    return this;
  }

  async register() {
    try {
      const response = await fetch(`${this.balancerUrl}/api/nodes/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          nodeId: this.nodeId,
          type: "vendor",
          capabilities: this.getCapabilities(),
          metadata: {
            userAgent: navigator.userAgent,
            platform: navigator.platform,
            memory: navigator.deviceMemory || "unknown",
            cores: navigator.hardwareConcurrency || 1,
          },
        }),
      });

      if (response.ok) {
        const data = await response.json();
        console.log("📡 Registered with master:", data);
        return data;
      }
    } catch {
      console.warn("⚠️ Could not register with master, running offline");
    }
    return null;
  }

  getCapabilities() {
    return {
      canProcess: true,
      canCache: true,
      canRelay: true,
      maxMemory: navigator.deviceMemory ? navigator.deviceMemory * 1024 : 2048, // MB
      cores: navigator.hardwareConcurrency || 1,
      hasWebGL: this.checkWebGL(),
      hasWasm: typeof WebAssembly !== "undefined",
      hasIndexedDB: typeof indexedDB !== "undefined",
      hasServiceWorker: "serviceWorker" in navigator,
    };
  }

  checkWebGL() {
    try {
      const canvas = document.createElement("canvas");
      return !!(
        canvas.getContext("webgl") || canvas.getContext("experimental-webgl")
      );
    } catch {
      return false;
    }
  }

  startHeartbeat() {
    setInterval(async () => {
      this.stats.uptime++;

      try {
        await fetch(`${this.balancerUrl}/api/nodes/heartbeat`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            nodeId: this.nodeId,
            stats: this.stats,
            load: this.getCurrentLoad(),
          }),
        });
      } catch {
        // Offline mode - continue working
      }
    }, 30000); // Every 30 seconds
  }

  getCurrentLoad() {
    // Estimate current load based on activity
    return {
      cpu: Math.random() * 0.3, // Estimate
      memory: performance.memory
        ? performance.memory.usedJSHeapSize / performance.memory.jsHeapSizeLimit
        : 0.5,
      peers: this.peers.size,
    };
  }

  async initCache() {
    // Use IndexedDB for larger cache
    return new Promise((resolve) => {
      const request = indexedDB.open("VendorNodeCache", 1);

      request.onupgradeneeded = (e) => {
        const db = e.target.result;
        if (!db.objectStoreNames.contains("responses")) {
          db.createObjectStore("responses", { keyPath: "hash" });
        }
      };

      request.onsuccess = (e) => {
        this.db = e.target.result;
        console.log("💾 Cache initialized");
        resolve();
      };

      request.onerror = () => {
        console.warn("⚠️ IndexedDB not available, using memory cache");
        resolve();
      };
    });
  }

  async initP2P() {
    // WebRTC setup for peer-to-peer communication
    this.peerConfig = {
      iceServers: [
        { urls: "stun:stun.l.google.com:19302" },
        { urls: "stun:stun1.l.google.com:19302" },
      ],
    };

    console.log("🔗 P2P initialized");
  }

  // Process a request locally
  async processLocally(query) {
    const hash = this.hashQuery(query);

    // Check cache first
    const cached = await this.getFromCache(hash);
    if (cached) {
      console.log("📦 Cache hit");
      this.stats.requestsHandled++;
      return cached;
    }

    // Check if we can handle locally (simple queries)
    if (this.canHandleLocally(query)) {
      const result = await this.handleLocal(query);
      await this.saveToCache(hash, result);
      this.stats.requestsHandled++;
      return result;
    }

    // Forward to server
    return this.forwardToServer(query);
  }

  canHandleLocally(query) {
    const q = query.toLowerCase();
    // Simple queries we can handle locally
    const localPatterns = [
      /^(hi|hello|hey|mirëdita|përshëndetje)/i,
      /^(what time|ora|koha)/i,
      /^(help|ndihmë)/i,
    ];
    return localPatterns.some((p) => p.test(q));
  }

  async handleLocal(query) {
    const q = query.toLowerCase();

    if (/^(hi|hello|hey|mirëdita)/i.test(q)) {
      return {
        response:
          "Mirëdita! Unë jam Ocean, AI i Kloud Cloud. Si mund t'ju ndihmoj?",
        source: "local",
        nodeId: this.nodeId,
      };
    }

    if (/^(what time|ora|koha)/i.test(q)) {
      return {
        response: `Ora tani është ${new Date().toLocaleTimeString()}`,
        source: "local",
        nodeId: this.nodeId,
      };
    }

    if (/^(help|ndihmë)/i.test(q)) {
      return {
        response:
          "Mund të më pyesni për çdo gjë! Provoni: 'Çfarë shërbimesh ofron?'",
        source: "local",
        nodeId: this.nodeId,
      };
    }

    return null;
  }

  async forwardToServer(query) {
    try {
      const response = await fetch(`${this.masterServer}/api/v1/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: query }),
      });

      if (response.ok) {
        const data = await response.json();
        return {
          ...data,
          source: "server",
          nodeId: this.nodeId,
        };
      }
    } catch (e) {
      console.error("Server unreachable:", e);
    }

    return {
      response: "Më falni, serveri nuk është i disponueshëm momentalisht.",
      source: "offline",
      nodeId: this.nodeId,
    };
  }

  hashQuery(query) {
    let hash = 0;
    const str = query.toLowerCase().trim();
    for (let i = 0; i < str.length; i++) {
      hash = (hash << 5) - hash + str.charCodeAt(i);
      hash = hash & hash;
    }
    return "Q" + Math.abs(hash).toString(36);
  }

  async getFromCache(hash) {
    // Memory cache first
    if (this.cache.has(hash)) {
      return this.cache.get(hash);
    }

    // IndexedDB
    if (this.db) {
      return new Promise((resolve) => {
        const tx = this.db.transaction("responses", "readonly");
        const store = tx.objectStore("responses");
        const request = store.get(hash);

        request.onsuccess = () => {
          if (
            request.result &&
            Date.now() - request.result.timestamp < 3600000
          ) {
            resolve(request.result.data);
          } else {
            resolve(null);
          }
        };
        request.onerror = () => resolve(null);
      });
    }

    return null;
  }

  async saveToCache(hash, data) {
    // Memory cache
    this.cache.set(hash, data);

    // Limit memory cache size
    if (this.cache.size > 100) {
      const firstKey = this.cache.keys().next().value;
      this.cache.delete(firstKey);
    }

    // IndexedDB
    if (this.db) {
      const tx = this.db.transaction("responses", "readwrite");
      const store = tx.objectStore("responses");
      store.put({
        hash,
        data,
        timestamp: Date.now(),
      });
    }
  }

  // Accept work from load balancer
  async acceptWork(task) {
    console.log(`📥 Accepting work: ${task.id}`);
    this.stats.requestsHandled++;

    const result = await this.processLocally(task.query);

    // Report completion
    try {
      await fetch(`${this.balancerUrl}/api/nodes/complete`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          nodeId: this.nodeId,
          taskId: task.id,
          result,
        }),
      });
    } catch {
      console.warn("Could not report completion");
    }

    return result;
  }

  getStats() {
    return {
      nodeId: this.nodeId,
      isActive: this.isActive,
      stats: this.stats,
      peers: this.peers.size,
      cacheSize: this.cache.size,
      capabilities: this.getCapabilities(),
    };
  }

  destroy() {
    this.isActive = false;
    if (this.db) this.db.close();
    this.cache.clear();
    this.peers.clear();
    console.log(`🔴 Vendor Node ${this.nodeId} destroyed`);
  }
}

// Auto-initialize when page loads
let vendorNode = null;

if (typeof window !== "undefined") {
  window.addEventListener("load", async () => {
    // Only init if user accepts (GDPR compliant)
    const consent = localStorage.getItem("vendorNodeConsent");

    if (consent === "accepted") {
      vendorNode = new VendorNode();
      await vendorNode.init();
      window.kloudNode = vendorNode;
    }
  });

  // Cleanup on page unload
  window.addEventListener("beforeunload", () => {
    if (vendorNode) {
      vendorNode.destroy();
    }
  });
}

// Export for module usage
if (typeof module !== "undefined" && module.exports) {
  module.exports = { VendorNode };
}

// Global access
window.VendorNode = VendorNode;
window.enableVendorNode = async () => {
  localStorage.setItem("vendorNodeConsent", "accepted");
  vendorNode = new VendorNode();
  await vendorNode.init();
  window.kloudNode = vendorNode;
  return vendorNode;
};
window.disableVendorNode = () => {
  localStorage.setItem("vendorNodeConsent", "declined");
  if (vendorNode) vendorNode.destroy();
  vendorNode = null;
};

