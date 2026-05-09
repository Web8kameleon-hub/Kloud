import { Router } from "express";
import os from "os";
import { AppConfig } from "../../config";

export function coreRoutes(cfg: AppConfig) {
  const r = Router();
  r.get("/health", (_req, res) => {
    res.json({
      status: "healthy",
      service: "Kloud Industrial Backend",
      version: "1.0.0",
      timestamp: new Date().toISOString(),
      hostname: os.hostname(),
    });
  });
  r.get("/status", (_req, res) => {
    const mem = process.memoryUsage();
    res.json({
      status: "operational",
      uptime: process.uptime(),
      memory_mb: { rss: Math.round(mem.rss / 1048576) },
      timestamp: new Date().toISOString(),
    });
  });
  return r;
}

