import type { Express, Request, Response, NextFunction } from "express";
import { AppConfig } from "../../config";
import os from "os";
import crypto from "crypto";
import { EventEmitter } from "events";
import { emitSignal } from "../_shared/signal";

interface AlbaStream {
  id: string;
  source: string;
  type: "neural" | "communication" | "biometric" | "telemetry";
  status: "active" | "idle" | "error" | "reconnecting";
  bandwidth: number;
  latency: number;
  signalQuality: number;
  encryption: number;
  lastUpdate: Date;
}

interface AlbaSystemStatus {
  status: "active" | "idle" | "degraded";
  totalStreams: number;
  activeStreams: number;
  degradedStreams: number;
  cpuLoad: number;
  memoryUsage: number;
  uptime: number;
  securityLevel: number;
  timestamp: string;
}

interface AlbaAlert {
  id: string;
  level: "info" | "warning" | "critical";
  message: string;
  timestamp: string;
}

export class AlbaCore extends EventEmitter {
  private streams: AlbaStream[] = [];
  private alerts: AlbaAlert[] = [];
  private started = Date.now();
  private interval: NodeJS.Timeout | null = null;
  private readonly MAX_STREAMS: number;
  private readonly RECOVERY_RATE = 0.4;

  constructor(maxStreams = 24) {
    super();
    this.MAX_STREAMS = maxStreams;
    this.bootstrapStreams();
    this.beginAutoDiagnostics();
  }

  private bootstrapStreams() {
    const types: AlbaStream["type"][] = ["neural", "communication", "biometric", "telemetry"];
    for (let i = 0; i < this.MAX_STREAMS; i++) {
      this.streams.push({
        id: `ALBA-STR-${crypto.randomUUID().split("-")[0]}`,
        source: `channel_${i + 1}`,
        type: types[i % types.length],
        status: "idle",
        bandwidth: Number((Math.random() * 10).toFixed(2)),
        latency: Number((Math.random() * 120).toFixed(1)),
        signalQuality: Number((Math.random() * 100).toFixed(1)),
        encryption: Number((Math.random() * 100).toFixed(1)),
        lastUpdate: new Date(),
      });
    }
  }

  getStreams() {
    return this.streams;
  }

  getStatus(): AlbaSystemStatus {
    const active = this.streams.filter((s) => s.status === "active").length;
    const degraded = this.streams.filter((s) => s.status === "error" || s.status === "reconnecting").length;
    const cpu = os.loadavg()[0] / os.cpus().length;
    const mem = 1 - os.freemem() / os.totalmem();
    const sec = Math.min(100, Math.round(100 - degraded * 4));
    return {
      status: degraded > 3 ? "degraded" : active > 0 ? "active" : "idle",
      totalStreams: this.streams.length,
      activeStreams: active,
      degradedStreams: degraded,
      cpuLoad: Number(cpu.toFixed(3)),
      memoryUsage: Number(mem.toFixed(3)),
      uptime: Math.round((Date.now() - this.started) / 1000),
      securityLevel: sec,
      timestamp: new Date().toISOString(),
    };
  }

  refreshStreams() {
    for (const s of this.streams) {
      if (s.status === "error" && Math.random() < this.RECOVERY_RATE) {
        s.status = "reconnecting";
        this.emit("log", `[ALBA] Recovering stream ${s.id}`);
        setTimeout(() => {
          s.status = "active";
          s.signalQuality = Number((70 + Math.random() * 30).toFixed(1));
          s.encryption = Number((80 + Math.random() * 20).toFixed(1));
          s.lastUpdate = new Date();
          this.emit("log", `[ALBA] Stream ${s.id} restored`);
        }, 2000);
      } else if (Math.random() < 0.05) {
        s.status = "error";
        s.signalQuality = Number((Math.random() * 30).toFixed(1));
        this.emit("alert", {
          id: crypto.randomUUID(),
          level: "warning",
          message: `Stream ${s.id} experienced signal drop`,
          timestamp: new Date().toISOString(),
        });
      } else {
        s.status = Math.random() > 0.2 ? "active" : "idle";
        s.signalQuality = Number((Math.random() * 100).toFixed(1));
        s.latency = Number((Math.random() * 120).toFixed(1));
        s.bandwidth = Number((Math.random() * 10).toFixed(2));
        s.encryption = Number((Math.random() * 100).toFixed(1));
        s.lastUpdate = new Date();
      }
    }
  }

  private beginAutoDiagnostics() {
    this.interval = setInterval(() => {
      this.refreshStreams();
      const degraded = this.streams.filter((s) => s.status === "error").length;
      if (degraded > this.MAX_STREAMS * 0.25) {
        this.createAlert("critical", "High degradation detected in stream integrity");
      }
    }, 5000);
  }

  private createAlert(level: AlbaAlert["level"], message: string) {
    const alert: AlbaAlert = {
      id: crypto.randomUUID(),
      level,
      message,
      timestamp: new Date().toISOString(),
    };
    this.alerts.push(alert);
    this.emit("alert", alert);
  }

  getAlerts() {
    return this.alerts.slice(-10);
  }

  stop() {
    if (this.interval) clearInterval(this.interval);
  }

  optimizeSystem() {
    for (const s of this.streams) {
      s.signalQuality = Math.min(100, s.signalQuality + 10);
      s.encryption = Math.min(100, s.encryption + 15);
      s.latency = Math.max(5, s.latency - 10);
      s.lastUpdate = new Date();
    }
    this.createAlert("info", "ALBA optimization cycle completed");
  }

  securityAudit() {
    const issues = this.streams.filter((s) => s.encryption < 50);
    return {
      timestamp: new Date().toISOString(),
      totalStreams: this.streams.length,
      weakLinks: issues.length,
      recommendation:
        issues.length > 0
          ? "Reinforce encryption for weak streams and reinitialize ALBA secure core."
          : "All streams maintain secure encryption thresholds.",
    };
  }

  analyzePatterns() {
    const avgSignal = this.streams.reduce((sum, s) => sum + s.signalQuality, 0) / this.streams.length;
    const avgLatency = this.streams.reduce((sum, s) => sum + s.latency, 0) / this.streams.length;
    const trend =
      avgSignal > 70 && avgLatency < 60
        ? "stable"
        : avgSignal > 40
        ? "fluctuating"
        : "degraded";

    return {
      trend,
      averageSignal: Number(avgSignal.toFixed(2)),
      averageLatency: Number(avgLatency.toFixed(2)),
      timestamp: new Date().toISOString(),
    };
  }
}

// ============================
// ðŸŒ Express Mount Function
// ============================
export function mountAlba(app: Express, cfg: AppConfig): AlbaCore {
  console.log("ðŸ­ [L4] Initializing ALBA Industrial Core...");
  const alba = new AlbaCore(cfg.ALBA_MAX_STREAMS ?? 24);

  alba.on("alert", async (alert: AlbaAlert) => {
    console.log(`ðŸš¨ [ALBA ALERT] (${alert.level.toUpperCase()}): ${alert.message}`);
    try {
      await emitSignal("ALBA", "alert", alert);
    } catch (err) {
      console.error("[ALBA] Failed to emit alert signal", err);
    }
  });

  alba.on("log", async (msg: string) => {
    console.log(msg);
    try {
      await emitSignal("ALBA", "event", { message: msg });
    } catch (err) {
      console.error("[ALBA] Failed to emit log signal", err);
    }
  });

  app.get("/alba/status", (_req, res) => res.json(alba.getStatus()));

  app.get("/alba/streams", (_req, res) => res.json({ streams: alba.getStreams() }));

  app.get("/alba/streams/:id", (req, res) => {
    const stream = alba.getStreams().find((s) => s.id === req.params.id);
    if (!stream) return res.status(404).json({ error: "Stream not found" });
    res.json(stream);
  });

  app.post("/alba/refresh", (_req, res) => {
    alba.refreshStreams();
    res.json({ ok: true, updated: alba.getStreams().length });
  });

  app.post("/alba/optimize", (_req, res) => {
    alba.optimizeSystem();
    res.json({ ok: true, message: "Optimization executed" });
  });

  app.get("/alba/audit", (_req, res) => {
    res.json(alba.securityAudit());
  });

  app.get("/alba/analyze", (_req, res) => {
    res.json(alba.analyzePatterns());
  });

  app.get("/alba/alerts", (_req, res) => {
    res.json({ alerts: alba.getAlerts() });
  });

  app.get("/alba/info", (_req, res) => {
    res.json({
      system: "ALBA Industrial Monitoring Core",
      version: "7.3",
      developer: "Kloud / Trinity Systems",
      maxStreams: 24,
      uptime: `${Math.round((Date.now() - alba['started']) / 1000)}s`,
      lastDiagnostics: alba.getStatus().timestamp,
    });
  });

  // Error middleware
  app.use("/alba", (err: Error, _req: Request, res: Response, _next: NextFunction) => {
    console.error("âŒ [ALBA ERROR]", err);
    res.status(500).json({ error: err.message });
  });

  console.log(`âœ… [L4] ALBA Industrial Core mounted â€” monitoring ${cfg.ALBA_MAX_STREAMS ?? 24} streams`);
  return alba;
}

