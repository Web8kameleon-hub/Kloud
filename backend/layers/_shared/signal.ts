/**
 * Kloud Signal Core
 * ----------------------
 * Unified event propagation layer between modules (ALBA, ALBI, JONA, ASI).
 * Handles Redis Pub/Sub, HTTP webhooks, and local diagnostics.
 */

import os from "os";
import fetch from "node-fetch";
import { createClient, RedisClientType } from "redis";
import crypto from "crypto";

export interface SignalPayload {
  id: string;
  source: string;
  type: "alert" | "metric" | "status" | "event";
  data: any;
  timestamp: string;
  signature?: string;
}

export interface SignalConfig {
  redisUrl?: string;
  httpWebhook?: string;
  secretKey?: string;
  redisChannel?: string;
}

let redis: ReturnType<typeof createClient> | null = null;
let config: SignalConfig = {};

async function ensureRedisConnection(url?: string) {
  if (redis) return redis;
  const target = url ?? config.redisUrl;
  if (!target) return null;
  const client = createClient({ url: target });
  client.on("error", (e: any) => console.error("âŒ [SignalCore] Redis error:", e));
  await client.connect();
  redis = client;
  config.redisUrl = target;
  console.log(`ðŸ“¡ [SignalCore] Connected to Redis @ ${target}`);
  return redis;
}

async function dispatchHttp(url: string | undefined, body: string) {
  if (!url) return;
  try {
    const res = await fetch(url, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body,
    });
    if (!res.ok) {
      console.warn(`[SignalCore] HTTP sink responded with ${res.status}`);
    }
  } catch (err) {
    console.error("[SignalCore] HTTP dispatch failed:", err);
  }
}

async function dispatchRedis(channel: string | undefined, body: string) {
  if (!channel) return;
  const client = await ensureRedisConnection();
  if (!client) return;
  try {
    await client.publish(channel, body);
  } catch (err) {
    console.error("[SignalCore] Redis publish failed:", err);
  }
}

function signPayload(data: any) {
  if (!config.secretKey) return undefined;
  const json = typeof data === "string" ? data : JSON.stringify(data);
  return crypto.createHmac("sha256", config.secretKey).update(json).digest("hex");
}

/**
 * Initialize Redis connection and signal configuration
 */
export async function initSignalCore(cfg: SignalConfig) {
  config = { ...config, ...cfg };
  if (cfg.redisUrl) {
    await ensureRedisConnection(cfg.redisUrl);
  } else if (!redis) {
    console.log("âš™ï¸ [SignalCore] Redis not configured â€” operating in local-only mode.");
  }
}

export async function initSignalRedis(url?: string) {
  if (!url) return;
  await initSignalCore({ ...config, redisUrl: url });
}

export async function signalPush(httpUrl: string | undefined, channel: string | undefined, payload: any) {
  const body = JSON.stringify(payload);
  await Promise.all([
    dispatchHttp(httpUrl ?? config.httpWebhook, body),
    dispatchRedis(channel ?? config.redisChannel, body),
  ]);
}

/**
 * Send a signal to HTTP webhook and/or Redis
 */
export async function emitSignal(source: string, type: SignalPayload["type"], data: any, options?: { channel?: string }) {
  const payload: SignalPayload = {
    id: crypto.randomUUID(),
    source,
    type,
    data,
    timestamp: new Date().toISOString(),
    signature: signPayload(data),
  };

  const body = JSON.stringify(payload);

  await Promise.all([
    dispatchHttp(config.httpWebhook, body),
    dispatchRedis(options?.channel ?? config.redisChannel ?? "Kloud:signals", body),
  ]);

  console.log(`ðŸ“¢ [SignalCore] ${type.toUpperCase()} from ${source} @ ${payload.timestamp}`);
  return payload;
}

/**
 * Gather local node diagnostics
 */
export function nodeDiagnostics() {
  return {
    node: os.hostname(),
    platform: os.platform(),
    uptime: os.uptime(),
    load: os.loadavg()[0],
    memoryUsage: Math.round((1 - os.freemem() / os.totalmem()) * 100),
    timestamp: new Date().toISOString(),
  };
}

export function nodeInfo() {
  const diag = nodeDiagnostics();
  return { node: diag.node, ts: diag.timestamp };
}

/**
 * Graceful shutdown of the signal core
 */
export async function shutdownSignalCore() {
  if (redis) {
    await redis.quit();
    redis = null;
    console.log("ðŸ›‘ [SignalCore] Redis connection closed.");
  }
}

