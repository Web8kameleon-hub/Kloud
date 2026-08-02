/**
 * Kloud Cloud Industrial Next.js Configuration
 * Production-ready with API rewrites for backend proxy
 */

import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// PRODUCTION: Docker internal communication via container names
// DEVELOPMENT: Use localhost for local backend
const isDev = process.env.NODE_ENV === "development";
const API_BASE =
  process.env.API_INTERNAL_URL ||
  (isDev ? "http://localhost:8000" : "http://kloud-api:8000");
const REPORTING_BASE =
  process.env.REPORTING_INTERNAL_URL ||
  (isDev ? "http://localhost:8000" : "http://kloud-api:8000");
const OCEAN_BASE =
  process.env.OCEAN_INTERNAL_URL ||
  (isDev ? "http://localhost:8030" : "http://kloud-ocean-core:8030");
// NodeDB control plane — resonant fabric host: nodedb, nodedb-fluid, resonant
// events, stigma, scan-print, nanogrid status (verified deployed on :9090).
const NODEDB_BASE =
  process.env.NODEDB_CONTROL_PLANE_URL ||
  (isDev ? "http://localhost:9090" : "http://kloud-nodedb-control-plane:9090");

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  transpilePackages: ["framer-motion"],
  staticPageGenerationTimeout: 600,

  // Fix for monorepo lockfile detection
  outputFileTracingRoot: path.resolve(__dirname, "../.."),

  // ==========================================================================
  // IMAGE OPTIMIZATION (85% size reduction with WebP/AVIF)
  // ==========================================================================
  images: {
    // Enable modern formats
    formats: ["image/avif", "image/webp"],

    // Allowed image domains
    remotePatterns: [
      {
        protocol: "https",
        hostname: "kloud.com",
      },
      {
        protocol: "https",
        hostname: "*.kloud.com",
      },
      {
        protocol: "https",
        hostname: "images.unsplash.com",
      },
      {
        protocol: "https",
        hostname: "*.githubusercontent.com",
      },
    ],

    // Responsive image sizes
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],

    // Optimization quality (75 is good balance)
    minimumCacheTTL: 60 * 60 * 24 * 30, // 30 days cache
  },

  // ==========================================================================
  // COMPRESSION & PERFORMANCE
  // ==========================================================================
  compress: true,
  poweredByHeader: false, // Security: hide X-Powered-By

  // Server-only packages (not bundled for client)
  serverExternalPackages: ["stripe"],

  // ==========================================================================
  // SECURITY HEADERS
  // ==========================================================================
  async headers() {
    return [
      {
        source: "/:path*",
        headers: [
          { key: "X-DNS-Prefetch-Control", value: "on" },
          { key: "X-Frame-Options", value: "SAMEORIGIN" },
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
        ],
      },
      // Cache favicon aggressively to prevent spam requests
      {
        source: "/favicon.ico",
        headers: [
          { key: "Cache-Control", value: "public, max-age=86400, immutable" },
        ],
      },
      // Cache static assets aggressively
      {
        source: "/static/:path*",
        headers: [
          {
            key: "Cache-Control",
            value: "public, max-age=31536000, immutable",
          },
        ],
      },
      {
        source: "/_next/static/:path*",
        headers: [
          {
            key: "Cache-Control",
            value: "public, max-age=31536000, immutable",
          },
        ],
      },
    ];
  },

  // CRITICAL: Proxy API requests to backend
  async rewrites() {
    return [
      // Crypto Market API
      {
        source: "/api/crypto/:path*",
        destination: `${API_BASE}/api/crypto/:path*`,
      },
      // Weather API
      {
        source: "/api/weather/:path*",
        destination: `${API_BASE}/api/weather/:path*`,
      },
      // Real Data Dashboard API
      {
        source: "/api/realdata/:path*",
        destination: `${API_BASE}/api/realdata/:path*`,
      },
      // AI Routes
      {
        source: "/api/ai/:path*",
        destination: `${API_BASE}/api/ai/:path*`,
      },
      // Monitoring
      {
        source: "/api/monitoring/:path*",
        destination: `${API_BASE}/api/monitoring/:path*`,
      },
      // System Status
      {
        source: "/api/system-status",
        destination: `${API_BASE}/api/system-status`,
      },
      // Health
      {
        source: "/api/health",
        destination: `${API_BASE}/health`,
      },
      // ASI Trinity Status (Phone Monitor)
      {
        source: "/api/asi-status",
        destination: `${API_BASE}/asi/status`,
      },
      // ASI Health
      {
        source: "/api/asi-health",
        destination: `${API_BASE}/asi/health`,
      },
      // ASI Metrics (all ASI routes)
      {
        source: "/asi/:path*",
        destination: `${API_BASE}/asi/:path*`,
      },
      // Backend proxy (for direct backend calls)
      {
        source: "/backend/:path*",
        destination: `${API_BASE}/:path*`,
      },
      // Backend status specifically
      {
        source: "/backend/status",
        destination: `${API_BASE}/health`,
      },
      // Direct /health endpoint proxy
      {
        source: "/health",
        destination: `${API_BASE}/health`,
      },
      // ===== REPORTING API (Port 8001) =====
      // Docker containers
      {
        source: "/api/reporting/:path*",
        destination: `${REPORTING_BASE}/api/reporting/:path*`,
      },
      // Direct docker stats
      {
        source: "/api/docker-containers",
        destination: `${REPORTING_BASE}/api/reporting/docker-containers`,
      },
      {
        source: "/api/docker-stats",
        destination: `${REPORTING_BASE}/api/reporting/docker-stats`,
      },
      {
        source: "/api/system-metrics",
        destination: `${REPORTING_BASE}/api/reporting/system-metrics`,
      },
      // ===== ALBI EEG API =====
      {
        source: "/api/albi/:path*",
        destination: `${API_BASE}/api/albi/:path*`,
      },
      // ===== ALBA API =====
      {
        source: "/api/alba/:path*",
        destination: `${API_BASE}/api/alba/:path*`,
      },
      // ===== ASI API (general) =====
      {
        source: "/api/asi/:path*",
        destination: `${API_BASE}/api/asi/:path*`,
      },
      // ===== JONA Neural Synthesis API =====
      {
        source: "/api/jona/:path*",
        destination: `${API_BASE}/api/jona/:path*`,
      },
      // ===== Security Status =====
      {
        source: "/api/security/:path*",
        destination: `${API_BASE}/api/security/:path*`,
      },
      // ===== System Health =====
      {
        source: "/api/system/:path*",
        destination: `${API_BASE}/api/system/:path*`,
      },
      // ===== OCEAN CORE (Port 8030) =====
      // Zürich Deterministic Engine
      {
        source: "/api/zurich/:path*",
        destination: `${OCEAN_BASE}/api/v1/zurich/:path*`,
      },
      {
        source: "/api/zurich",
        destination: `${OCEAN_BASE}/api/v1/zurich`,
      },
      // Trinity Debate Engine
      {
        source: "/api/debate/stream",
        destination: `${OCEAN_BASE}/api/v1/debate/stream`,
      },
      {
        source: "/api/debate/:path*",
        destination: `${OCEAN_BASE}/api/v1/debate/:path*`,
      },
      {
        source: "/api/debate",
        destination: `${OCEAN_BASE}/api/v1/debate`,
      },
      // Ocean Core general
      {
        source: "/api/ocean/:path*",
        destination: `${OCEAN_BASE}/api/v1/:path*`,
      },
      {
        source: "/api/ocean",
        destination: `${OCEAN_BASE}/api/v1/health`,
      },
      // ======================================================================
      // SOVEREIGN FABRIC ALIASES (proprietary modules -> real deployed backends)
      // Profile: wwwmmm-ndb-stigma-tide-rezonance-nanogrid
      // NOTE: exact routes MUST precede ":path*" (which also matches empty path).
      // Verified against deployed nodedb-control-plane:9090 (resonant fabric host).
      // ======================================================================
      // Rezonance (resonant event fabric) -> nodedb-control-plane
      {
        source: "/api/rezonance",
        destination: `${NODEDB_BASE}/api/v1/resonant/events`,
      },
      {
        source: "/api/rezonance/:path*",
        destination: `${NODEDB_BASE}/api/v1/resonant/:path*`,
      },
      {
        source: "/api/resonant/:path*",
        destination: `${NODEDB_BASE}/api/v1/resonant/:path*`,
      },
      // Nanogrid -> control-plane nanogrid status (exact first)
      {
        source: "/api/nanogrid/status",
        destination: `${NODEDB_BASE}/api/v1/control-plane/nanogrid/status`,
      },
      {
        source: "/api/nanogrid",
        destination: `${NODEDB_BASE}/api/v1/control-plane/nanogrid/status`,
      },
      {
        source: "/api/nanogrid/:path*",
        destination: `${NODEDB_BASE}/api/v1/control-plane/:path*`,
      },
      // NodeDB -> control plane discovery (exact first)
      {
        source: "/api/nodedb",
        destination: `${NODEDB_BASE}/api/v1/control-plane/discovery`,
      },
      {
        source: "/api/nodedb/:path*",
        destination: `${NODEDB_BASE}/api/v1/control-plane/:path*`,
      },
      // NodeDB Fluid -> sync-loop status (exact first)
      {
        source: "/api/nodedb-fluid",
        destination: `${NODEDB_BASE}/api/v1/control-plane/sync-loop/status`,
      },
      {
        source: "/api/nodedb-fluid/:path*",
        destination: `${NODEDB_BASE}/api/v1/control-plane/:path*`,
      },
      // Stigma (behavioral trace + film memory chain) -> nodedb resonant events
      {
        source: "/api/stigma/write",
        destination: `${NODEDB_BASE}/api/v1/stigma/write`,
      },
      {
        source: "/api/stigma/events",
        destination: `${NODEDB_BASE}/api/v1/resonant/events`,
      },
      {
        source: "/api/stigma/:path*",
        destination: `${NODEDB_BASE}/api/v1/resonant/:path*`,
      },
      // Scanner-Thinker-Printer -> control-plane scan-print (exact first)
      {
        source: "/api/scan-print",
        destination: `${NODEDB_BASE}/api/v1/control-plane/scan-print`,
      },
      {
        source: "/api/scan-print/:path*",
        destination: `${NODEDB_BASE}/api/v1/control-plane/:path*`,
      },
      // Fabric operational surfaces (real deployed control-plane endpoints)
      {
        source: "/api/fabric-monitoring",
        destination: `${NODEDB_BASE}/api/v1/control-plane/monitoring/status`,
      },
      {
        source: "/api/fabric-topology",
        destination: `${NODEDB_BASE}/api/v1/control-plane/topology`,
      },
    ];
  },

  webpack: (config) => {
    config.cache = false;
    return config;
  },

  onDemandEntries: {
    maxInactiveAge: 60 * 1000,
    pagesBufferLength: 5,
  },

  httpAgentOptions: {
    keepAlive: true,
  },
  allowedDevOrigins: ["localhost:3000", "127.0.0.1:3000", "kloud.com"],
};

export default nextConfig;

