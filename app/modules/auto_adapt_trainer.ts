import os from "os";
import path from "path";
import { fileURLToPath } from "url";
import { AlbaCore } from "../../backend/layers/layer4-alba";
import { ALBISystem } from "../../backend/layers/layer5-albi";
import { emitSignal, nodeDiagnostics, initSignalCore, shutdownSignalCore } from "../../backend/layers/_shared/signal";
import { AudioSynthesizer } from "./audio_synthesizer";
import { loadConfig, type AppConfig } from "../../backend/config";
import { buildLaborInput, summarizeLaborInput } from "./alpha_theta_beta";

type AlbaStream = ReturnType<AlbaCore["getStreams"]>[number];

export type AdaptiveMode = "alpha" | "theta" | "beta";

export interface AutoAdaptOptions {
  outputDir?: string;
  toneDurationSeconds?: number;
}

export interface AdaptiveTrainingResult {
  timestamp: string;
  mode: AdaptiveMode;
  reason: string;
  frequency: number;
  neuralPower: number;
  stability: number;
  audioFile: string;
  diagnostics: ReturnType<typeof nodeDiagnostics>;
}

const DEFAULT_OUTPUT_DIR = path.join(process.cwd(), "generated_audio");

interface ModeDefinition {
  range: [number, number];
  amplitude: number;
  modulation: number;
}

const MODE_CONFIG: Record<AdaptiveMode, ModeDefinition> = {
  alpha: { range: [8, 13], amplitude: 0.7, modulation: 0.3 },
  theta: { range: [4, 8], amplitude: 0.5, modulation: 0.2 },
  beta: { range: [14, 30], amplitude: 0.8, modulation: 0.4 },
};

export class AutoAdaptTrainer {
  private readonly options: Required<AutoAdaptOptions>;
  private lastResult: AdaptiveTrainingResult | null = null;
  private loopHandle: NodeJS.Timeout | null = null;

  constructor(
    private readonly alba: AlbaCore,
    private readonly albi: ALBISystem,
    private readonly jona: AudioSynthesizer,
    options: AutoAdaptOptions = {}
  ) {
    this.options = {
      outputDir: options.outputDir ?? DEFAULT_OUTPUT_DIR,
      toneDurationSeconds: options.toneDurationSeconds ?? 4,
    };
  }

  async runAdaptiveCycle(): Promise<AdaptiveTrainingResult> {
    const { mode, reason, stress } = this.detectMode();
    const streams = this.alba.getStreams();
    const laborInput = buildLaborInput(streams);
    const output = await this.albi.processLaborCycle(laborInput);

    const signalValues = streams.map((s) => Number.isFinite(s.signalQuality) ? s.signalQuality : 0);
    const average = signalValues.length > 0 ? signalValues.reduce((acc, val) => acc + val, 0) / signalValues.length : 0;
    const normalized = Math.max(0, Math.min(1, average / 100));

    const modeConfig = MODE_CONFIG[mode];
    const freq = modeConfig.range[0] + Math.random() * (modeConfig.range[1] - modeConfig.range[0]);
    const neuralPower = Number((normalized * 100).toFixed(2));
    const stability = Number((Math.random() * 0.2 + 0.8).toFixed(2));

    const filename = path.join(this.options.outputDir, `${mode}_${Date.now()}.wav`);
    await this.jona.writeTone(filename, {
      freq,
      amplitude: modeConfig.amplitude,
      mod: modeConfig.modulation,
      durationSeconds: this.options.toneDurationSeconds,
    });

    const diagnostics = nodeDiagnostics();
    const result: AdaptiveTrainingResult = {
      timestamp: new Date().toISOString(),
      mode,
      reason,
      frequency: Number(freq.toFixed(2)),
      neuralPower,
      stability,
      audioFile: filename,
      diagnostics,
    };

    this.lastResult = result;

    try {
      await emitSignal("AUTO", "metric", {
        ...result,
        stress,
        laborInputSample: summarizeLaborInput(laborInput),
        birthPotential: output.birthPotential,
        coherenceScore: output.coherenceScore,
        bornIntelligence: output.bornIntelligence ? {
          id: output.bornIntelligence.id,
          birthTimestamp: output.bornIntelligence.birthTimestamp,
        } : null,
      });
    } catch (err) {
      console.error("[AutoAdapt] Failed to emit telemetry", err);
    }

    console.log(`ðŸ¤– [AutoAdapt] Mode: ${mode.toUpperCase()} @ ${freq.toFixed(2)}Hz | ${reason}`);
    return result;
  }

  startAutoLoop(intervalSeconds = 30): void {
    this.stopAutoLoop();
    const intervalMs = Math.max(5, intervalSeconds) * 1000;
    console.log(`ðŸ¤– [AutoAdaptTrainer] Autonomous loop every ${intervalSeconds}s`);
    this.loopHandle = setInterval(() => {
      this.runAdaptiveCycle().catch((err) => console.error("[AutoAdapt] Loop error", err));
    }, intervalMs);
  }

  stopAutoLoop(): void {
    if (this.loopHandle) {
      clearInterval(this.loopHandle);
      this.loopHandle = null;
    }
  }

  getLastResult(): AdaptiveTrainingResult | null {
    return this.lastResult;
  }

  private detectMode(): { mode: AdaptiveMode; reason: string; stress: number } {
    const loadAvg = os.loadavg()[0];
    const cpuCount = os.cpus().length || 1;
    const normalizedLoad = Number.isFinite(loadAvg) && loadAvg > 0 ? Math.min(1, loadAvg / cpuCount) : 0;
    const memUsage = 1 - os.freemem() / os.totalmem();

    const albaStatus = this.alba.getStatus();
    const degradedRatio = albaStatus.totalStreams > 0 ? albaStatus.degradedStreams / albaStatus.totalStreams : 0;

    const stress = Math.min(100, Math.max(0, normalizedLoad * 70 + memUsage * 20 + degradedRatio * 100 * 10 / 100));
    const stressLabel = `${stress.toFixed(1)}%`;

    if (stress < 30) {
      return { mode: "theta", reason: `Low load (${stressLabel}) â†’ Meditation`, stress };
    }

    if (stress < 65) {
      return { mode: "alpha", reason: `Moderate load (${stressLabel}) â†’ Calm focus`, stress };
    }

    return { mode: "beta", reason: `High load (${stressLabel}) â†’ High focus`, stress };
  }
}

function parseArgs(argv: string[]): Record<string, string | boolean> {
  return argv.slice(2).reduce<Record<string, string | boolean>>((acc, arg) => {
    if (arg.startsWith("--")) {
      const [key, value] = arg.replace(/^--/, "").split("=");
      acc[key] = value ?? true;
    }
    return acc;
  }, {});
}

function parseBoolean(value: string | boolean | undefined, defaultValue: boolean): boolean {
  if (typeof value === "undefined") return defaultValue;
  if (typeof value === "boolean") return value;
  const normalized = value.toLowerCase();
  if (["false", "0", "off", "no"].includes(normalized)) return false;
  if (["true", "1", "on", "yes"].includes(normalized)) return true;
  return defaultValue;
}

async function bootstrapAutoAdapt(config: AppConfig, interval: number, loop: boolean): Promise<AutoAdaptTrainer> {
  const alba = new AlbaCore(config.ALBA_MAX_STREAMS ?? 24);
  const albi = new ALBISystem(config);
  await albi.initialize();
  const synth = new AudioSynthesizer();
  const trainer = new AutoAdaptTrainer(alba, albi, synth);
  if (loop) {
    trainer.startAutoLoop(interval);
  } else {
    await trainer.runAdaptiveCycle();
  }
  return trainer;
}

async function main() {
  const args = parseArgs(process.argv);
  const loop = parseBoolean(args.loop, true);
  const interval = args.interval ? Number(args.interval) : 40;
  const cfg = loadConfig();

  await initSignalCore({
    redisUrl: cfg.REDIS_URL,
    httpWebhook: cfg.SIGNAL_HTTP,
    secretKey: process.env.SIGNAL_SECRET || "Kloud-key",
  });

  const trainer = await bootstrapAutoAdapt(cfg, interval, loop);

  const shutdown = async () => {
    trainer.stopAutoLoop();
    await emitSignal("AUTO", "status", { state: "auto_adapt_shutdown", diagnostics: nodeDiagnostics() }).catch(() => null);
    await shutdownSignalCore();
    process.exit(0);
  };

  process.on("SIGINT", shutdown);
  process.on("SIGTERM", shutdown);
}

const moduleUrl = fileURLToPath(import.meta.url);
if (moduleUrl === process.argv[1]) {
  main().catch(async (err) => {
    console.error("[AutoAdapt] Unhandled error", err);
    await emitSignal("AUTO", "alert", {
      error: err instanceof Error ? err.message : String(err),
      stack: err instanceof Error ? err.stack : undefined,
      diagnostics: nodeDiagnostics(),
    }).catch(() => null);
    await shutdownSignalCore();
    process.exit(1);
  });
}

