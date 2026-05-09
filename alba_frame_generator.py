#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Continuous ALBA telemetry frame generator for local testing."""

from __future__ import annotations

import json
import random
import time
from datetime import datetime, timezone

import psutil
import requests

API_URL = "http://127.0.0.1:9091/alba/frame"


def generate_frame() -> dict[str, object]:
    """Build a telemetry frame with live system stats and synthetic context."""
    now = datetime.now(timezone.utc).isoformat()
    net = psutil.net_io_counters()
    frame = {
        "source": random.choice(["Zurich-Lab", "Tirana-Lab", "Berlin-Mesh"]),
        "timestamp": now,
        "sensors": {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage("/").percent,
            "temperature_c": round(random.uniform(25, 45), 2),
            "network_sent_mb": round(net.bytes_sent / (1024 * 1024), 2),
            "network_recv_mb": round(net.bytes_recv / (1024 * 1024), 2),
        },
        "environment": {
            "weather": random.choice(["clear", "rain", "cloudy", "storm"]),
            "energy_level": round(random.uniform(70, 100), 2),
        },
        "tags": ["simulation", "Kloud"],
    }
    return frame


def send_frame(frame: dict[str, object]) -> None:
    try:
        response = requests.post(API_URL, json=frame, timeout=5)
        response.raise_for_status()
        payload = response.json()
        status = payload.get("status", "unknown")
        print(f"[{frame['timestamp']}] -> {status}")
    except Exception as exc:
        print(f"[ERROR] Failed to send frame: {exc}")
        try:
            print(f"Payload: {json.dumps(frame)[:512]}")
        except Exception:
            pass


if __name__ == "__main__":
    print("Starting ALBA frame generator...")
    while True:
        frame = generate_frame()
        send_frame(frame)
        time.sleep(10)


