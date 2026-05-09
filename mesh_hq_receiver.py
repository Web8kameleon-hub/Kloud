# -*- coding: utf-8 -*-
"""
Mesh HQ Receiver
Industrial Real-Data Sink for Kloud Distributed Systems
Business: Ledjan Ahmati - WEB8euroweb GmbH

Pranon Ã§do tÃ« dhÃ«nÃ« nga Integrated System / Pulse Balancer
Ruhet si JSONL nÃ« disk me timestamp real.
"""

from datetime import datetime
from pathlib import Path
import json
import os
import platform

import psutil
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn

from Kloud.colored_logger import setup_logger

# =========================================================
# ðŸ”§ KONFIGURIMET
# =========================================================
BASE_DIR = Path(r"C:\Kloud-cloud")
DATA_DIR = BASE_DIR / "mesh_data"
LOGS_DIR = BASE_DIR / "logs"
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

RECEIVED_FILE = DATA_DIR / "received.jsonl"
ERROR_FILE = LOGS_DIR / "mesh_errors.log"

APP_NAME = f"MeshHQ@{platform.node()}"

logger = setup_logger("KloudMeshHQ")

# =========================================================
# ðŸŒ FASTAPI APP
# =========================================================
app = FastAPI(
    title="Mesh HQ Receiver",
    description="Industrial endpoint for receiving Kloud data pulses in real time.",
    version="1.0.0-industrial",
)


# =========================================================
# ðŸ”¹ ENDPOINT: Upload metrics
# =========================================================
@app.post("/metrics/upload")
async def receive_metrics(request: Request):
    """
    Pranon Ã§do dÃ«rgim nga sistemet Kloud (Integrated System ose Balancer)
    dhe e ruan si JSONL nÃ« disk.
    """
    try:
        data = await request.json()
    except Exception as exc:  # pragma: no cover - defensive logging
        log_error(f"Invalid JSON: {exc}")
        return JSONResponse({"ok": False, "error": "invalid_json"}, status_code=400)

    record = {
        "timestamp_received": datetime.utcnow().isoformat(),
        "source_ip": request.client.host if request.client else "unknown",
        "payload": data,
    }

    append_jsonl(RECEIVED_FILE, record)

    return JSONResponse({"ok": True, "mesh_hq": APP_NAME, "ts": datetime.utcnow().isoformat()})


# =========================================================
# ðŸ”¹ ENDPOINT: Health check
# =========================================================
@app.get("/health")
async def health():
    stats = {
        "cpu_percent": psutil.cpu_percent(interval=None),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage("/").percent,
        "received_file_size_MB": round(RECEIVED_FILE.stat().st_size / (1024**2), 2)
        if RECEIVED_FILE.exists()
        else 0.0,
        "uptime_sec": round(time_since_boot(), 1),
    }
    return JSONResponse({"ok": True, "node": APP_NAME, "metrics": stats})


# =========================================================
# ðŸ”¹ ENDPOINT: View latest pulses
# =========================================================
@app.get("/metrics/latest")
async def latest_entries(limit: int = 5):
    if not RECEIVED_FILE.exists():
        return JSONResponse({"ok": True, "entries": []})
    lines = RECEIVED_FILE.read_text(encoding="utf-8").splitlines()[-limit:]
    entries = [json.loads(line) for line in lines if line.strip()]
    return JSONResponse({"ok": True, "count": len(entries), "entries": entries})


# =========================================================
# ðŸ”¹ HELPER FUNCTIONS
# =========================================================
def append_jsonl(path: Path, data: dict):
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(data, ensure_ascii=False) + "\n")


def log_error(msg: str):
    with open(ERROR_FILE, "a", encoding="utf-8") as handle:
        handle.write(f"{datetime.utcnow().isoformat()} | {msg}\n")


def time_since_boot() -> float:
    return float(datetime.utcnow().timestamp() - psutil.boot_time())


# =========================================================
# â–¶ï¸ MAIN ENTRY POINT
# =========================================================
if __name__ == "__main__":
    logger.info("Starting Mesh HQ Receiver on http://localhost:7777")
    logger.info("Saving data to: %s", RECEIVED_FILE)
    uvicorn.run(app, host="0.0.0.0", port=7777)


