import path from "path";
import { fileURLToPath } from "url";
import { AlbaCore } from "../../backend/layers/layer4-alba";
import { ALBISystem, type LaborData } from "../../backend/layers/layer5-albi";
import { emitSignal, nodeDiagnostics, initSignalCore, shutdownSignalCore } from "../../backend/layers/_shared/signal";
import { AudioSynthesizer } from "../Kloud/audio_synthesizer";
import { loadConfig, type AppConfig } from "../../backend/config";

type AlbaStream = ReturnType<AlbaCore["getStreams"]>[number];
	export type NeuroMode = "alpha" | "theta" | "beta";

export interface BAlphaThetaBetaOptions {
  outputDir?: string;
  toneDurationSeconds?: number;
}

export interface NeuroTrainingResult {
  timestamp: string;
  mode: NeuroMode;
  frequency: number;
  neuralPower: number;
  performanceIndex: number;
  stability: number;
  audioFile: string;
  diagnostics: ReturnType<typeof nodeDiagnostics>;
}

const DEFAULT_OUTPUT_DIR = path.join(process.cwd(), "generated_audio");

interface ModeParameters {
  label: string;
  frequency: number;
  amplitude: number;
  modulation: number;
}

export class BAlphaThetaBetaTrainer {
  private readonly options: Required<BAlphaThetaBetaOptions>;
  private lastResult: NeuroTrainingResult | null = null;
  private loopHandle: NodeJS.Timeout | null = null;

  constructor(
    private readonly alba: AlbaCore,
    private readonly albi: ALBISystem,
    private readonly jona: AudioSynthesizer,
    options: BAlphaThetaBetaOptions = {}
  ) {
    this.options = {
      outputDir: options.outputDir ?? DEFAULT_OUTPUT_DIR,
      toneDurationSeconds: options.toneDurationSeconds ?? 4,
    };
  }

  async runCycle(mode: NeuroMode): Promise<NeuroTrainingResult> {
    const streams = this.alba.getStreams();
    const laborInput = buildLaborInput(streams);
    const output = await this.albi.processLaborCycle(laborInput);

    const signalValues = streams.map((s) => Number.isFinite(s.signalQuality) ? s.signalQuality : 0);
    const average = signalValues.length > 0 ? signalValues.reduce((acc, val) => acc + val, 0) / signalValues.length : 0;
    const normalized = Math.max(0, Math.min(1, average / 100));

    const params = deriveModeParameters(mode);
    const neuralPower = Number((normalized * 100).toFixed(2));
    const performanceIndex = Math.min(100, Math.round(neuralPower + Math.random() * 10));
    const stability = Number((Math.random() * 0.2 + 0.8).toFixed(2));

    const filename = path.join(this.options.outputDir, `${mode}_${Date.now()}.wav`);
    await this.jona.writeTone(filename, {
      freq: params.frequency,
      amplitude: params.amplitude,
      mod: params.modulation,
      durationSeconds: this.options.toneDurationSeconds,
    });

    const diagnostics = nodeDiagnostics();
    const result: NeuroTrainingResult = {
      timestamp: new Date().toISOString(),
      mode,
      frequency: Number(params.frequency.toFixed(2)),
      neuralPower,
      performanceIndex,
      stability,
      audioFile: filename,
      diagnostics,
    };

    this.lastResult = result;

    try {
      await emitSignal(mode.toUpperCase(), "metric", {
        ...result,
        laborInputSample: summarizeLaborInput(laborInput),
        birthPotential: output.birthPotential,
        coherenceScore: output.coherenceScore,
        bornIntelligence: output.bornIntelligence ? {
          id: output.bornIntelligence.id,
          birthTimestamp: output.bornIntelligence.birthTimestamp,
        } : null,
      });
    } catch (err) {
      console.error(`[BAlphaThetaBeta] Failed to emit signal for ${mode} mode`, err);
    }

    console.log(`ðŸ§  [${mode.toUpperCase()}] ${params.label} â†’ ${params.frequency.toFixed(2)}Hz | Perf ${performanceIndex}%`);
    return result;
  }

  async runFullCycle(): Promise<void> {
    console.log("ðŸ§© [NeuroTrainer] Running full Alpha-Theta-Beta cycle...");
    await this.runCycle("alpha");
    await this.runCycle("theta");
    await this.runCycle("beta");
    console.log("âœ… [NeuroTrainer] Complete cycle executed.");
  }

  startAutoLoop(intervalSeconds = 30): void {
    this.stopAutoLoop();
    const intervalMs = Math.max(5, intervalSeconds) * 1000;
    console.log(`ðŸ§  [NeuroTrainer] Auto loop every ${intervalSeconds}s`);
    this.loopHandle = setInterval(() => {
      this.runFullCycle().catch((err) => console.error("[NeuroTrainer] Auto loop error", err));
    }, intervalMs);
  }

  stopAutoLoop(): void {
    if (this.loopHandle) {
      clearInterval(this.loopHandle);
      this.loopHandle = null;
    }
  }

  getLastResult(): NeuroTrainingResult | null {
    return this.lastResult;
  }
}

function deriveModeParameters(mode: NeuroMode): ModeParameters {
  switch (mode) {
    case "alpha":
      return {
        label: "Relaxation & Focus",
        frequency: 10 + Math.random() * 1.5,
        amplitude: 0.7,
        modulation: 0.3,
      };
    case "theta":
      return {
        label: "Deep Meditation",
        frequency: 5 + Math.random() * 2,
        amplitude: 0.5,
        modulation: 0.2,
      };
    case "beta":
      return {
        label: "High Cognitive Focus",
        frequency: 20 + Math.random() * 5,
        amplitude: 0.8,
        modulation: 0.4,
      };
    default:
      throw new Error(`Unsupported neuro mode: ${mode satisfies never}`);
  }
}

export function summarizeLaborInput(input: LaborData) {
  return {
    rawPatterns: Array.isArray(input.rawPatterns) ? input.rawPatterns.length : 0,
    semanticNetworks: Array.isArray(input.semanticNetworks) ? input.semanticNetworks.length : 0,
    temporalSequences: Array.isArray(input.temporalSequences) ? input.temporalSequences.length : 0,
    learningTrajectories: Array.isArray(input.learningTrajectories) ? input.learningTrajectories.length : 0,
  };
}

export function buildLaborInput(streams: AlbaStream[]): LaborData {
  const now = new Date().toISOString();
  const sampleSize = Math.max(1, Math.floor(streams.length / 4));
  const recent = streams.slice(0, sampleSize);

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

async function bootstrapTrainer(config: AppConfig, interval: number, loop: boolean, mode?: NeuroMode) {
  const alba = new AlbaCore(config.ALBA_MAX_STREAMS ?? 24);
  const albi = new ALBISystem(config);
  await albi.initialize();
  const synth = new AudioSynthesizer();
  const trainer = new BAlphaThetaBetaTrainer(alba, albi, synth);

  if (loop) {
    trainer.startAutoLoop(interval);
  } else if (mode) {
    await trainer.runCycle(mode);
  } else {
    await trainer.runFullCycle();
  }

  return trainer;
}

async function main() {
  const args = parseArgs(process.argv);
  const loop = parseBoolean(args.loop, false);
  const modeArg = typeof args.mode === "string" ? (args.mode.toLowerCase() as NeuroMode) : undefined;
  const interval = args.interval ? Number(args.interval) : 45;

  if (modeArg && !["alpha", "theta", "beta"].includes(modeArg)) {
    throw new Error(`Unsupported mode '${modeArg}'. Use alpha|theta|beta.`);
  }

  const cfg = loadConfig();
  await initSignalCore({
    redisUrl: cfg.REDIS_URL,
    httpWebhook: cfg.SIGNAL_HTTP,
    secretKey: process.env.SIGNAL_SECRET || "Kloud-key",
  });

  const trainer = await bootstrapTrainer(cfg, interval, loop, modeArg);

  const shutdown = async () => {
    trainer.stopAutoLoop();
    await emitSignal("NEURAL_LOOP", "status", { state: "trainer_shutdown", diagnostics: nodeDiagnostics() }).catch(() => null);
    await shutdownSignalCore();
    process.exit(0);
  };

  process.on("SIGINT", shutdown);
  process.on("SIGTERM", shutdown);
}

const moduleUrl = fileURLToPath(import.meta.url);
if (moduleUrl === process.argv[1]) {
  main().catch(async (err) => {
    console.error("[BAlphaThetaBeta] Unhandled error", err);
    await emitSignal("NEURAL_LOOP", "alert", {
      source: "BAlphaThetaBeta",
      error: err instanceof Error ? err.message : String(err),
      stack: err instanceof Error ? err.stack : undefined,
      diagnostics: nodeDiagnostics(),
    }).catch(() => null);
    await shutdownSignalCore();
    process.exit(1);
  });
}

