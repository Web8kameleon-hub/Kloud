/**
 * Layer 14: Logging & Monitoring
 * Centralized logging with Winston and Pino
 */

import winston from "winston";
import "winston-daily-rotate-file";

// ═══════════════════════════════════════════════════════════════════════════════
// WINSTON LOGGER CONFIGURATION
// ═══════════════════════════════════════════════════════════════════════════════

const logFormat = winston.format.combine(
  winston.format.timestamp({ format: "YYYY-MM-DD HH:mm:ss" }),
  winston.format.errors({ stack: true }),
  winston.format.printf(({ level, message, timestamp, stack, ...meta }) => {
    let log = `${timestamp} [${level.toUpperCase()}] ${message}`;
    if (Object.keys(meta).length) {
      log += ` ${JSON.stringify(meta)}`;
    }
    if (stack) {
      log += `\n${stack}`;
    }
    return log;
  }),
);

// Daily rotate file transport
const fileRotateTransport = new winston.transports.DailyRotateFile({
  filename: "logs/kloud-%DATE%.log",
  datePattern: "YYYY-MM-DD",
  maxSize: "20m",
  maxFiles: "14d",
  format: logFormat,
});

// Console transport with colors
const consoleTransport = new winston.transports.Console({
  format: winston.format.combine(winston.format.colorize(), logFormat),
});

// Main logger
export const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || "info",
  format: logFormat,
  defaultMeta: { service: "kloud-backend" },
  transports: [consoleTransport, fileRotateTransport],
});

// ═══════════════════════════════════════════════════════════════════════════════
// SPECIALIZED LOGGERS
// ═══════════════════════════════════════════════════════════════════════════════

export const securityLogger = logger.child({ module: "security" });
export const apiLogger = logger.child({ module: "api" });
export const dbLogger = logger.child({ module: "database" });
export const aiLogger = logger.child({ module: "ai" });

// ═══════════════════════════════════════════════════════════════════════════════
// MONITORING METRICS
// ═══════════════════════════════════════════════════════════════════════════════

interface Metrics {
  requests: number;
  errors: number;
  latency: number[];
  startTime: Date;
}

const metrics: Metrics = {
  requests: 0,
  errors: 0,
  latency: [],
  startTime: new Date(),
};

export const recordRequest = (duration: number, isError: boolean = false) => {
  metrics.requests++;
  if (isError) metrics.errors++;
  metrics.latency.push(duration);

  // Keep only last 1000 latency samples
  if (metrics.latency.length > 1000) {
    metrics.latency.shift();
  }
};

export const getMetrics = () => {
  const avgLatency =
    metrics.latency.length > 0
      ? metrics.latency.reduce((a, b) => a + b, 0) / metrics.latency.length
      : 0;

  return {
    uptime: Date.now() - metrics.startTime.getTime(),
    requests: metrics.requests,
    errors: metrics.errors,
    errorRate:
      metrics.requests > 0
        ? ((metrics.errors / metrics.requests) * 100).toFixed(2) + "%"
        : "0%",
    avgLatencyMs: Math.round(avgLatency),
  };
};

export default {
  logger,
  securityLogger,
  apiLogger,
  dbLogger,
  aiLogger,
  recordRequest,
  getMetrics,
};

