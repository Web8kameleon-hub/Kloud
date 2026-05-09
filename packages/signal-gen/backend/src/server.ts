/**
 * kloud INDUSTRIAL BACKEND SERVER
 * ===================================
 * High-performance TypeScript server për kloud ecosystem
 * Real-time processing, industrial grade, ALBI+ALBA+JONA integration
 */

import Fastify, { FastifyInstance } from "fastify";
import cors from "@fastify/cors";
import rateLimit from "@fastify/rate-limit";
import { registerRealApiRoutes } from "./real-api-routes.js";

// Industrial Server Configuration
const serverConfig = {
  logger: {
    level: "info",
    transport: {
      target: "pino-pretty",
      options: {
        colorize: true,
        translateTime: "yyyy-mm-dd HH:MM:ss",
        ignore: "pid,hostname"
      }
    }
  },
  trustProxy: true,
  requestTimeout: 30000,
  keepAliveTimeout: 5000
};

// Initialize Industrial Fastify Server
const industrialServer: FastifyInstance = Fastify(serverConfig);

// ================== RATE LIMITING (SECURITY) ==================
await industrialServer.register(rateLimit, {
  max: 100,  // max 100 requests
  timeWindow: '1 minute',
  errorResponseBuilder: function (request, context) {
    return {
      code: 429,
      error: 'Too Many Requests',
      message: `Rate limit exceeded. Max ${context.max} requests per ${context.after}`,
      date: new Date().toISOString(),
      expiresIn: context.ttl
    }
  }
});

// ================== INDUSTRIAL MIDDLEWARE ==================
await industrialServer.register(cors, {
  origin: ["http://localhost:3000", "http://127.0.0.1:3000"],
  credentials: true,
  methods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
});

// Request logging middleware
industrialServer.addHook("onRequest", async (request, reply) => {
  request.log.info(`Industrial Request: ${request.method} ${request.url}`);
});

// Response logging middleware
industrialServer.addHook("onResponse", async (request, reply) => {
  request.log.info(`Industrial Response: ${reply.statusCode} in ${reply.elapsedTime}ms`);
});

// ================== INDUSTRIAL HEALTH ENDPOINTS ==================

// System Health Check
industrialServer.get("/health", async (request, reply) => {
  const systemHealth = {
    service: "kloud-industrial-backend",
    status: "operational",
    version: "1.0.0",
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    memory: {
      used: Math.round(process.memoryUsage().heapUsed / 1024 / 1024),
      total: Math.round(process.memoryUsage().heapTotal / 1024 / 1024),
      rss: Math.round(process.memoryUsage().rss / 1024 / 1024)
    },
    industrial_grade: true,
    real_data_only: true
  };
  
  return systemHealth;
});

// System Status Dashboard
industrialServer.get("/status", async (request, reply) => {
  return {
    kloud_ecosystem: {
      albi: "active",
      alba: "collecting", 
      jona: "monitoring"
    },
    backend_status: "industrial_operational",
    data_processing: "real_time",
    timestamp: new Date().toISOString()
  };
});

// ================== REAL API ROUTES ==================

// Register all real API routes with ALBI+ALBA+JONA integration
await industrialServer.register(registerRealApiRoutes);

// ================== STATIC FRONTEND SERVING ==================

// Serve industrial dashboard
industrialServer.get("/", async (request, reply) => {
  const fs = await import("fs");
  const path = await import("path");
  
  const dashboardPath = path.resolve(process.cwd(), "../frontend/industrial-dashboard.html");
  
  try {
    const htmlContent = fs.readFileSync(dashboardPath, "utf-8");
    reply.type("text/html").send(htmlContent);
  } catch (error) {
    // If dashboard not found, return a simple status page
    const statusPage = `
    <!DOCTYPE html>
    <html>
    <head><title>kloud Industrial Backend</title></head>
    <body style="font-family: Arial; background: #1a1a2e; color: white; padding: 40px;">
      <h1>kloud Industrial Backend</h1>
      <p>Status: <strong style="color: #4ecdc4;">OPERATIONAL</strong></p>
      <p>Time: ${new Date().toISOString()}</p>
      <h3>Available Endpoints:</h3>
      <ul>
        <li><a href="/health" style="color: #00d4ff;">/health</a> - System health</li>
        <li><a href="/status" style="color: #00d4ff;">/status</a> - System status</li>
        <li><a href="/api/albi/health" style="color: #00d4ff;">/api/albi/health</a> - ALBI status</li>
        <li><a href="/api/alba/health" style="color: #00d4ff;">/api/alba/health</a> - ALBA status</li>
        <li><a href="/api/jona/health" style="color: #00d4ff;">/api/jona/health</a> - JONA status</li>
      </ul>
      <p style="color: #ff6b6b;"><strong>REAL DATA ONLY - NO MOCK - NO Math.random()</strong></p>
    </body>
    </html>`;
    reply.type("text/html").send(statusPage);
  }
});

// ================== ERROR HANDLING ==================

// Global error handler
industrialServer.setErrorHandler((error, request, reply) => {
  request.log.error(error);
  
  const industrialError = {
    error: "industrial_system_error",
    message: error.message,
    timestamp: new Date().toISOString(),
    request_id: request.id,
    industrial_handling: true
  };
  
  reply.status(500).send(industrialError);
});

// 404 Handler
industrialServer.setNotFoundHandler((request, reply) => {
  reply.status(404).send({
    error: "endpoint_not_found",
    message: `Industrial endpoint ${request.url} not available`,
    available_endpoints: ["/health", "/status", "/api/alba/*", "/api/albi/*", "/api/jona/*"],
    timestamp: new Date().toISOString()
  });
});

// ================== SERVER STARTUP ==================

const startIndustrialServer = async (): Promise<void> => {
  try {
    const port = process.env.PORT ? Number(process.env.PORT) : 8088;
    const host = process.env.HOST || "0.0.0.0";
    
    await industrialServer.listen({ 
      host,
      port 
    });
    
    console.log("==========================================");
    console.log("kloud INDUSTRIAL BACKEND STARTED");
    console.log("==========================================");
    console.log(`Server: http://127.0.0.1:${port}`);
    console.log(`Health: http://127.0.0.1:${port}/health`);
    console.log(`Status: http://127.0.0.1:${port}/status`);
    console.log("Industrial Grade: ACTIVE");
    console.log("Real Data Only: ENABLED");
    console.log("==========================================");
    
  } catch (error) {
    industrialServer.log.error(error);
    console.error("Industrial server startup failed:", error);
    process.exit(1);
  }
};

// Graceful shutdown
process.on("SIGINT", async () => {
  console.log("\nShutting down industrial server...");
  await industrialServer.close();
  console.log("Industrial server shutdown complete");
  process.exit(0);
});

process.on("SIGTERM", async () => {
  console.log("\nTerminating industrial server...");
  await industrialServer.close();
  process.exit(0);
});

// Start the industrial server
startIndustrialServer();

