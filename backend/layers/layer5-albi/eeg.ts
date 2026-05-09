import { spawn } from "child_process";
import { AppConfig } from "../../config";
import fs from "fs";
import path from "path";

// SECURITY: Allowed directories for file operations
const ALLOWED_INPUT_DIRS = [
  path.resolve(process.cwd(), 'data'),
  path.resolve(process.cwd(), 'uploads'),
  '/tmp/kloud'
];

function isPathSafe(filePath: string): boolean {
  const resolvedPath = path.resolve(filePath);
  return ALLOWED_INPUT_DIRS.some(baseDir => resolvedPath.startsWith(baseDir));
}

export async function eegAnalyze(cfg: AppConfig, filePath: string):
  Promise<{ ok: boolean; dominant_hz?: number; bands?: Record<string, number>; detail?: any }>
{
  return new Promise((resolve) => {
    // SECURITY: Validate path to prevent path traversal attacks
    if (!isPathSafe(filePath)) {
      return resolve({ ok: false, detail: "Access denied: path outside allowed directories" });
    }
    
    // Verify file exists
    if (!fs.existsSync(filePath)) {
      return resolve({ ok: false, detail: "File not found" });
    }

    const py = spawn(cfg.PYTHON || "python", [cfg.MNE_SCRIPT || "./python/eeg_process.py", filePath], { 
      stdio: ["ignore", "pipe", "pipe"] 
    });
    
    let out = ""; 
    let err = "";
    
    py.stdout.on("data", (d) => out += d.toString());
    py.stderr.on("data", (d) => err += d.toString());
    
    py.on("close", (code) => {
      try {
        if (code !== 0) {
          return resolve({ ok: false, detail: `Python exit code: ${code}, stderr: ${err}` });
        }
        
        const j = JSON.parse(out);
        resolve({ 
          ok: true, 
          dominant_hz: j.dominant_hz, 
          bands: j.bands, 
          detail: j 
        });
      } catch {
        resolve({ ok: false, detail: err || out || "Failed to parse Python output" });
      }
    });

    // Timeout after 30 seconds
    setTimeout(() => {
      py.kill();
      resolve({ ok: false, detail: "Processing timeout (30s)" });
    }, 30000);
  });
}

