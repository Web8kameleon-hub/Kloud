import { spawn } from "child_process";
import { AppConfig } from "../../config";
import fs from "fs";
import path from "path";

export interface AudioConversionResult {
  ok: boolean;
  file?: string;
  duration_seconds?: number;
  sample_rate?: number;
  format?: string;
  detail?: any;
}

export interface ConversionOptions {
  sample_rate: number;
  duration_limit: number;
  quality: "low" | "standard" | "high" | "studio";
  format: "wav" | "mp3" | "flac";
}

// SECURITY: Allowed directories for file operations
const ALLOWED_INPUT_DIRS = [
  path.resolve(process.cwd(), 'data'),
  path.resolve(process.cwd(), 'uploads'),
  '/tmp/kloud'
];

function isPathSafe(filePath: string, allowedDirs: string[]): boolean {
  const resolvedPath = path.resolve(filePath);
  return allowedDirs.some(baseDir => resolvedPath.startsWith(baseDir));
}

export async function eegToAudio(
  cfg: AppConfig, 
  eegFile: string, 
  options: ConversionOptions
): Promise<AudioConversionResult> {
  return new Promise((resolve) => {
    // SECURITY: Validate input path to prevent path traversal
    if (!isPathSafe(eegFile, ALLOWED_INPUT_DIRS)) {
      return resolve({ ok: false, detail: "Access denied: input path outside allowed directories" });
    }
    
    // Verify input file exists
    if (!fs.existsSync(eegFile)) {
      return resolve({ ok: false, detail: "Input file not found" });
    }

    // Ensure output directory exists
    const outputDir = process.env.NSX_OUT_AUDIO || "./data/exports";
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }

    // Generate unique output filename
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const outputFile = path.join(outputDir, `eeg_audio_${timestamp}.${options.format}`);

    // Python script arguments
    const args = [
      cfg.LIBROSA_SCRIPT || "./python/audio_analyze.py",
      eegFile,
      "--output", outputFile,
      "--sample-rate", options.sample_rate.toString(),
      "--duration-limit", options.duration_limit.toString(),
      "--quality", options.quality,
      "--format", options.format
    ];

    const py = spawn(cfg.PYTHON || "python", args, { 
      stdio: ["ignore", "pipe", "pipe"] 
    });

    let out = "";
    let err = "";

    py.stdout.on("data", (d) => out += d.toString());
    py.stderr.on("data", (d) => err += d.toString());

    py.on("close", (code) => {
      try {
        if (code !== 0) {
          return resolve({ 
            ok: false, 
            detail: `Python conversion failed with code ${code}: ${err}` 
          });
        }

        // Try to parse Python output
        let result;
        try {
          result = JSON.parse(out);
        } catch {
          // If JSON parsing fails, create basic result
          result = {
            output: outputFile,
            sr: options.sample_rate,
            len_samples: 0
          };
        }

        // Verify output file exists
        if (!fs.existsSync(outputFile)) {
          return resolve({ 
            ok: false, 
            detail: "Output file was not created" 
          });
        }

        // Get file stats
        const stats = fs.statSync(outputFile);
        const durationSeconds = estimateAudioDuration(stats.size, options.sample_rate);

        resolve({
          ok: true,
          file: outputFile,
          duration_seconds: durationSeconds,
          sample_rate: result.sr || options.sample_rate,
          format: options.format,
          detail: result
        });

      } catch (e: any) {
        resolve({ 
          ok: false, 
          detail: `Conversion processing error: ${e.message}` 
        });
      }
    });

    // Timeout after 5 minutes
    setTimeout(() => {
      py.kill();
      resolve({ 
        ok: false, 
        detail: "Conversion timeout (5 minutes)" 
      });
    }, 300000);
  });
}

// Estimate audio duration from file size (rough approximation)
function estimateAudioDuration(fileSizeBytes: number, sampleRate: number): number {
  // Rough estimation: 16-bit mono audio = 2 bytes per sample
  const bytesPerSecond = sampleRate * 2;
  return Math.round(fileSizeBytes / bytesPerSecond);
}

// Advanced EEG to Audio mapping algorithms
export class NeuroAcousticProcessor {
  static mapBrainwaveToFrequency(brainwaveHz: number): number {
    // Map EEG frequencies to musical/audio frequencies
    const frequencyMappings = {
      // Delta waves (0.5-4 Hz) -> Deep bass (40-100 Hz)
      delta: { min: 0.5, max: 4, audioMin: 40, audioMax: 100 },
      // Theta waves (4-8 Hz) -> Bass (100-250 Hz)  
      theta: { min: 4, max: 8, audioMin: 100, audioMax: 250 },
      // Alpha waves (8-13 Hz) -> Mid-range (250-500 Hz)
      alpha: { min: 8, max: 13, audioMin: 250, audioMax: 500 },
      // Beta waves (13-30 Hz) -> Treble (500-2000 Hz)
      beta: { min: 13, max: 30, audioMin: 500, audioMax: 2000 },
      // Gamma waves (30+ Hz) -> High frequencies (2000-8000 Hz)
      gamma: { min: 30, max: 100, audioMin: 2000, audioMax: 8000 }
    };

    for (const [bandName, band] of Object.entries(frequencyMappings)) {
      if (brainwaveHz >= band.min && brainwaveHz <= band.max) {
        // Linear interpolation within the band
        const ratio = (brainwaveHz - band.min) / (band.max - band.min);
        return band.audioMin + ratio * (band.audioMax - band.audioMin);
      }
    }

    // Default fallback
    return 440; // A4 note
  }

  static generateHarmonics(fundamentalFreq: number, harmonicCount: number = 3): number[] {
    const harmonics = [fundamentalFreq];
    for (let i = 2; i <= harmonicCount + 1; i++) {
      harmonics.push(fundamentalFreq * i);
    }
    return harmonics;
  }

  static applyPsychoacousticFilter(audioData: number[]): number[] {
    // Apply perceptual audio processing
    // This is a simplified version - real implementation would use proper DSP
    return audioData.map(sample => {
      // Soft compression
      const compressed = Math.sign(sample) * Math.pow(Math.abs(sample), 0.8);
      // Subtle harmonics
      return compressed * 0.9 + Math.sin(sample * 3) * 0.1;
    });
  }
}

