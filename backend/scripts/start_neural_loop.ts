import { setTimeout as delay } from "timers/promises";
import { loadConfig } from "../config";
import {
  initSignalCore,
  emitSignal,
  shutdownSignalCore,
  nodeDiagnostics,
} from "../layers/_shared/signal";
import { AlbaCore } from "../layers/layer4-alba";
import { ALBISystem, type LaborData } from "../layers/layer5-albi";
import {
  initEthicsSystem,
  isAllowed,
  addViolation,
} from "../layers/layer6-jona/ethics";

const LOOP_INTERVAL_MS = Number(process.env.NEURAL_LOOP_INTERVAL_MS ?? "7000");
const STATUS_INTERVAL_MS = Number(process.env.NEURAL_LOOP_STATUS_INTERVAL_MS ?? "15000");

async function main() {
  const cfg = loadConfig();

  await initSignalCore({
    redisUrl: cfg.REDIS_URL,
    httpWebhook: cfg.SIGNAL_HTTP,
    secretKey: process.env.SIGNAL_SECRET || "Kloud-key",
  });

  const alba = new AlbaCore(cfg.ALBA_MAX_STREAMS ?? 24);
  const albi = new ALBISystem(cfg);
  initEthicsSystem();

  await emitSignal("NEURAL_LOOP", "status", {
    state: "starting",
    intervalMs: LOOP_INTERVAL_MS,
    statusIntervalMs: STATUS_INTERVAL_MS,
    ...nodeDiagnostics(),
  });

  await albi.initialize();

  let running = true;
  const cleanup = async () => {
    if (!running) return;
    running = false;
    alba.stop();
    clearInterval(statusTicker);
    await emitSignal("NEURAL_LOOP", "status", {
      state: "shutting_down",
      ...nodeDiagnostics(),
    }).catch((err) => console.error("[NeuralLoop] Failed to emit shutdown signal", err));
    await shutdownSignalCore();
  };

  const statusTicker = setInterval(() => {
    const status = alba.getStatus();
    void emitSignal("ALBA", "status", {
      ...status,
      ...nodeDiagnostics(),
    }).catch((err) => console.error("[NeuralLoop] Failed to emit ALBA status", err));
  }, STATUS_INTERVAL_MS);

  const handleSignal = () => {
    void cleanup().finally(() => process.exit(0));
  };

  process.on("SIGINT", handleSignal);
  process.on("SIGTERM", handleSignal);
  process.on("uncaughtException", async (err) => {
    console.error("[NeuralLoop] Uncaught exception", err);
    await emitSignal("NEURAL_LOOP", "alert", {
      severity: "CRITICAL",
      error: err instanceof Error ? err.message : String(err),
      stack: err instanceof Error ? err.stack : undefined,
      ...nodeDiagnostics(),
    }).catch(() => null);
    await cleanup();
    process.exit(1);
  });

  let cycle = 0;
  while (running) {
    cycle += 1;
    try {
      await runLaborCycle({ cycle, alba, albi });
    } catch (err) {
      console.error(`[NeuralLoop] Cycle ${cycle} failed`, err);
      await emitSignal("NEURAL_LOOP", "alert", {
        severity: "HIGH",
        cycle,
        error: err instanceof Error ? err.message : String(err),
        ...nodeDiagnostics(),
      }).catch(() => null);
    }

    await delay(LOOP_INTERVAL_MS);
  }
}

type AlbaStream = ReturnType<AlbaCore["getStreams"]>[number];

async function runLaborCycle({
  cycle,
  alba,
  albi,
}: {
  cycle: number;
  alba: AlbaCore;
  albi: ALBISystem;
}) {
  const streams = alba.getStreams();
  const status = alba.getStatus();

  const laborInput = buildLaborInput(streams);
  const output = await albi.processLaborCycle(laborInput);

  const action = output.bornIntelligence ? "deploy_intelligence" : "update_cognitive_structures";
  const context = {
    contains_pii: false,
    cpu_usage: status.cpuLoad * 100,
    authenticated: true,
    verified: true,
    degraded_streams: status.degradedStreams,
  };

  const allowed = isAllowed(action, context);
  if (!allowed) {
    await addViolation({
      action,
      context,
      timestamp: new Date().toISOString(),
    });
  }

  const payload = {
    cycle,
    allowed,
    action,
    status,
    laborInputSample: {
      rawPatterns: laborInput.rawPatterns.length,
      semanticNetworks: laborInput.semanticNetworks.length,
      temporalSequences: laborInput.temporalSequences.length,
      learningTrajectories: laborInput.learningTrajectories.length,
    },
    birthPotential: output.birthPotential,
    coherenceScore: output.coherenceScore,
    bornIntelligence: output.bornIntelligence
      ? {
          id: output.bornIntelligence.id,
          birthTimestamp: output.bornIntelligence.birthTimestamp,
          capabilities: output.bornIntelligence.initialCapabilities,
        }
      : null,
    diagnostics: nodeDiagnostics(),
  };

  await emitSignal("NEURAL_LOOP", "event", payload);
}

function buildLaborInput(streams: AlbaStream[]): LaborData {
  const sampleSize = Math.max(1, Math.floor(streams.length / 4));
  const recent = streams.slice(0, sampleSize);
  const now = new Date().toISOString();

  return {
    rawPatterns: recent.map((stream) => ({
      id: stream.id,
      type: stream.type,
      quality: stream.signalQuality,
      latency: stream.latency,
      capturedAt: now,
    })),
    semanticNetworks: streams.map((stream) => ({
      node: stream.source,
      connections: Math.round(stream.bandwidth * 10),
      security: stream.encryption,
      status: stream.status,
    })),
    temporalSequences: streams.map((stream) => ({
      id: stream.id,
      latencyTrajectory: [stream.latency],
      lastUpdate: stream.lastUpdate,
    })),
    learningTrajectories: streams.map((stream) => ({
      channel: stream.source,
      signalQuality: stream.signalQuality,
      adjustments: stream.status === "error" ? ["reroute", "retrain"] : ["reinforce"],
    })),
  };
}

void main().catch(async (err) => {
  console.error("[NeuralLoop] Failed to start", err);
  await emitSignal("NEURAL_LOOP", "alert", {
    severity: "CRITICAL",
    error: err instanceof Error ? err.message : String(err),
    stack: err instanceof Error ? err.stack : undefined,
    ...nodeDiagnostics(),
  }).catch(() => null);
  await shutdownSignalCore();
  process.exit(1);
});

