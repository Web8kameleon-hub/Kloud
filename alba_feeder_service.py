#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ALBA Feeder Service
Simulates environmental and system metrics for the ALBA ingestion layer.
Feeds data frames every few seconds into data/alba/ for Kloud Cloud.
"""

from __future__ import annotations

import json
import random
import time
from datetime import datetime, timezone
from pathlib import Path

import psutil

# Folderi ku ALBA lexon tÃ« dhÃ«nat
ALBA_PATH = Path(r"C:\Kloud-cloud\data\alba")
ALBA_PATH.mkdir(parents=True, exist_ok=True)


def generate_alba_frame() -> Path:
    """Krijon njÃ« 'frame' tÃ« vetme tÃ« tÃ« dhÃ«nave qÃ« pÃ«rfaqÃ«son perceptimin e sistemit."""
    now = datetime.now(timezone.utc).isoformat()
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent
    net = psutil.net_io_counters()

    frame = {
        "timestamp": now,
        "node": random.choice(["Zurich-Lab", "Tirana-Lab", "Berlin-Mesh", "Tokyo-Core"]),
        "source": "system_telemetry",
        "sensors": {
            "cpu_percent": cpu,
            "memory_percent": mem,
            "disk_percent": disk,
            "net_sent_mb": round(net.bytes_sent / (1024**2), 2),
            "net_recv_mb": round(net.bytes_recv / (1024**2), 2),
            "temperature_c": round(random.uniform(25, 65), 2),
            "energy_level": round(random.uniform(70, 100), 2),
        },
        "environment": {
            "weather": random.choice(["clear", "rain", "cloudy", "storm"]),
            "ambient_noise": round(random.uniform(0.1, 0.8), 2),
            "light_intensity": round(random.uniform(300, 1000), 2),
        },
        "message": random.choice(
            [
                "Nominal operation",
                "Slight fluctuation detected",
                "Stable telemetry frame",
                "Environmental sync normal",
            ]
        ),
    }

    filename = f"frame_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    path = ALBA_PATH / filename

    with path.open("w", encoding="utf-8") as handle:
        json.dump(frame, handle, indent=2)

    print(f"[ALBA-FEEDER] Frame generated: {filename}")
    return path


def continuous_feed(interval: int = 10) -> None:
    """DÃ«rgon frames nÃ« mÃ«nyrÃ« tÃ« vazhdueshme pÃ«r ALBA."""
    print(f"[ALBA-FEEDER] Starting continuous data feed to {ALBA_PATH}")
    print(f"[ALBA-FEEDER] Interval: {interval}s per frame\n")
    while True:
        try:
            generate_alba_frame()
            time.sleep(interval)
        except KeyboardInterrupt:
            print("\n[ALBA-FEEDER] Stopped by user.")
            break
        except Exception as exc:  # pragma: no cover - telemetry loop protection
            print(f"[ERROR] {exc}")
            time.sleep(interval)


if __name__ == "__main__":
    continuous_feed(interval=10)


