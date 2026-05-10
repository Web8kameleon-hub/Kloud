/**
 * Layer 18: Configuration Management
 * Centralized configuration with validation
 */

import convict from "convict";
import dotenv from "dotenv";

// Load environment variables
dotenv.config();

// ═══════════════════════════════════════════════════════════════════════════════
// CONFIGURATION SCHEMA
// ═══════════════════════════════════════════════════════════════════════════════

const config = convict({
  env: {
    doc: "Application environment",
    format: ["production", "development", "test"],
    default: "development",
    env: "NODE_ENV",
  },

  server: {
    host: {
      doc: "Server host",
      format: String,
      default: "0.0.0.0",
      env: "HOST",
    },
    port: {
      doc: "Server port",
      format: "port",
      default: 8000,
      env: "PORT",
    },
    cors: {
      origins: {
        doc: "Allowed CORS origins",
        format: Array,
        default: ["http://localhost:3000", "https://kloud.cloud"],
        env: "CORS_ORIGINS",
      },
    },
  },

  database: {
    postgres: {
      host: {
        doc: "PostgreSQL host",
        format: String,
        default: "localhost",
        env: "POSTGRES_HOST",
      },
      port: {
        doc: "PostgreSQL port",
        format: "port",
        default: 5432,
        env: "POSTGRES_PORT",
      },
      database: {
        doc: "Database name",
        format: String,
        default: "klouddb",
        env: "POSTGRES_DB",
      },
      user: {
        doc: "Database user",
        format: String,
        default: "kloud",
        env: "POSTGRES_USER",
      },
      password: {
        doc: "Database password",
        format: String,
        default: "",
        env: "POSTGRES_PASSWORD",
        sensitive: true,
      },
    },
    redis: {
      url: {
        doc: "Redis connection URL",
        format: String,
        default: "redis://localhost:6379",
        env: "REDIS_URL",
      },
    },
  },

  auth: {
    jwtSecret: {
      doc: "JWT signing secret",
      format: String,
      default: "change-me-in-production",
      env: "JWT_SECRET",
      sensitive: true,
    },
    jwtExpiresIn: {
      doc: "JWT expiration time",
      format: String,
      default: "24h",
      env: "JWT_EXPIRES_IN",
    },
  },

  ai: {
    clx: {
      host: {
        doc: "CLX API host",
        format: String,
        default: "http://localhost:11434",
        env: "CLX_HOST",
      },
      model: {
        doc: "Default AI model",
        format: String,
        default: "clx",
        env: "CLX_MODEL",
      },
    },
  },

  logging: {
    level: {
      doc: "Logging level",
      format: ["error", "warn", "info", "debug"],
      default: "info",
      env: "LOG_LEVEL",
    },
    format: {
      doc: "Log format",
      format: ["json", "pretty"],
      default: "pretty",
      env: "LOG_FORMAT",
    },
  },

  rateLimit: {
    windowMs: {
      doc: "Rate limit window in ms",
      format: Number,
      default: 900000, // 15 minutes
      env: "RATE_LIMIT_WINDOW_MS",
    },
    max: {
      doc: "Max requests per window",
      format: Number,
      default: 100,
      env: "RATE_LIMIT_MAX",
    },
  },
});

// Validate configuration
config.validate({ allowed: "strict" });

// ═══════════════════════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════════════════════

export const getConfig = () => config.getProperties();
export const get = <T>(key: string): T => config.get(key) as T;

export const isProduction = () => config.get("env") === "production";
export const isDevelopment = () => config.get("env") === "development";
export const isTest = () => config.get("env") === "test";

export default config;

