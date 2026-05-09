"""
JONA COORDINATOR SERVICE (Port 7777)
Data synthesis and neural audio generation service
"""

import asyncio
import json
import time
import logging
import uuid
import io
from datetime import datetime, timezone
from typing import Dict, List, Any

from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from cors_policy import apply_standard_cors

# OpenTelemetry imports
from tracing import setup_tracing, instrument_fastapi_app, instrument_http_clients

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("JonaCoordinator")

# Initialize tracing
tracer = setup_tracing("jona")

app = FastAPI(
    title="JONA Coordinator",
    version="1.0.0",
    description="Data synthesis and neural audio generation service",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Instrument FastAPI app for automatic tracing
instrument_fastapi_app(app, "jona")

# Instrument HTTP clients
instrument_http_clients()

apply_standard_cors(app)

# ═══════════════════════════════════════════════════════════════════
# GLOBAL STATE
# ═══════════════════════════════════════════════════════════════════

START_TIME = time.time()
INSTANCE_ID = uuid.uuid4().hex[:8]

synthesis_queue = []
generated_files = {}
coordination_log = []

# ═══════════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════════


@app.post("/synthesize")
async def synthesize_data(config: Dict[str, Any]):
    """Synthesize neural audio from analysis data"""
    with tracer.start_as_current_span("synthesize_data") as span:
        synthesis_id = uuid.uuid4().hex

        mode = config.get(
            "mode", "relax"
        )  # relax, focus, sleep, motivation, creativity
        frequency = config.get("frequency", 10.0)  # Hz (alpha wave frequency)
        duration = config.get("duration", 30)  # seconds
        amplitude = config.get("amplitude", 0.7)

        span.set_attribute("synthesis_id", synthesis_id)
        span.set_attribute("mode", mode)
        span.set_attribute("frequency", frequency)
        span.set_attribute("duration", duration)

        # Simulate audio generation
        synthesis_result = {
            "synthesis_id": synthesis_id,
            "mode": mode,
            "frequency": frequency,
            "duration": duration,
            "amplitude": amplitude,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "format": "wav",
            "sample_rate": 44100,
            "status": "generated",
        }

        synthesis_queue.append(synthesis_result)
        generated_files[synthesis_id] = synthesis_result

        logger.info(
            f"[SYNTHESIZE] Mode: {mode}, Freq: {frequency}Hz, Duration: {duration}s"
        )

        return synthesis_result


@app.get("/synthesize/{synthesis_id}")
async def get_synthesis(synthesis_id: str):
    """Retrieve synthesis result"""
    if synthesis_id not in generated_files:
        raise HTTPException(status_code=404, detail="Synthesis not found")

    return generated_files[synthesis_id]


@app.get("/synthesize/{synthesis_id}/audio")
async def get_synthesis_audio(synthesis_id: str):
    """Stream generated audio"""
    if synthesis_id not in generated_files:
        raise HTTPException(status_code=404, detail="Synthesis not found")

    synthesis = generated_files[synthesis_id]

    # Generate synthetic WAV data
    import numpy as np

    sample_rate = 44100
    duration = synthesis["duration"]
    frequency = synthesis["frequency"]
    amplitude = synthesis["amplitude"]

    # Generate sine wave
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    audio = amplitude * np.sin(2 * np.pi * frequency * t)
    audio = np.int16(audio * 32767)

    # Convert to bytes
    wav_buffer = io.BytesIO()

    # Simple WAV header (PCM, mono, 44.1kHz, 16-bit)
    import struct

    # WAV header
    num_channels = 1
    byte_rate = sample_rate * num_channels * 2
    block_align = num_channels * 2

    wav_buffer.write(b"RIFF")
    wav_buffer.write(struct.pack("<I", 36 + len(audio) * 2))
    wav_buffer.write(b"WAVE")

    wav_buffer.write(b"fmt ")
    wav_buffer.write(struct.pack("<I", 16))
    wav_buffer.write(struct.pack("<H", 1))  # PCM
    wav_buffer.write(struct.pack("<H", num_channels))
    wav_buffer.write(struct.pack("<I", sample_rate))
    wav_buffer.write(struct.pack("<I", byte_rate))
    wav_buffer.write(struct.pack("<H", block_align))
    wav_buffer.write(struct.pack("<H", 16))  # bits per sample

    wav_buffer.write(b"data")
    wav_buffer.write(struct.pack("<I", len(audio) * 2))
    wav_buffer.write(audio.tobytes())

    wav_buffer.seek(0)

    return StreamingResponse(
        iter([wav_buffer.getvalue()]),
        media_type="audio/wav",
        headers={"Content-Disposition": f"attachment; filename={synthesis_id}.wav"},
    )


@app.post("/coordinate")
async def coordinate_services(coordination: Dict[str, Any]):
    """Coordinate synthesis with other services"""
    with tracer.start_as_current_span("coordinate_services") as span:
        action = coordination.get("action", "")
        span.set_attribute("action", action)

        coordination_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "coordination": coordination,
        }

        coordination_log.append(coordination_record)

        logger.info(f"[COORDINATE] Action: {action}")

        return {
            "status": "coordinated",
            "coordination_id": uuid.uuid4().hex,
            "services_involved": ["alba", "albi", "jona"],
        }


@app.get("/queue")
async def get_synthesis_queue():
    """Get synthesis queue status"""
    return {
        "queue_size": len(synthesis_queue),
        "pending": synthesis_queue,
        "completed": len(generated_files),
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.post("/api/coordination/event")
async def coordination_event(data: Dict[str, Any]):
    """Receive coordination events from AI agents"""
    with tracer.start_as_current_span("coordination_event") as span:
        agent = data.get("agent", "unknown")
        operation = data.get("operation", "unknown")
        status = data.get("status", "unknown")

        span.set_attribute("agent", agent)
        span.set_attribute("operation", operation)
        span.set_attribute("status", status)

        # Log coordination event
        event_record = {
            "agent": agent,
            "operation": operation,
            "status": status,
            "success": data.get("success", True),
            "error": data.get("error"),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        coordination_log.append(event_record)

        logger.info(f"[AGENT] {agent}.{operation} -> Jona ({status})")

        return {
            "status": "logged",
            "agent": agent,
            "timestamp": event_record["timestamp"],
        }


@app.get("/metrics")
async def get_metrics():
    """Get coordinator metrics"""
    uptime = time.time() - START_TIME

    return {
        "uptime_seconds": uptime,
        "total_syntheses": len(generated_files),
        "queue_size": len(synthesis_queue),
        "syntheses_per_minute": (len(generated_files) / max(uptime / 60, 1)),
        "coordination_events": len(coordination_log),
    }


@app.get("/health")
async def health():
    """Service health check"""
    with tracer.start_as_current_span("health_check") as span:
        uptime = time.time() - START_TIME

        span.set_attribute("status", "operational")
        span.set_attribute("uptime_seconds", uptime)

        return {
            "service": "jona-coordinator",
            "status": "operational",
            "instance_id": INSTANCE_ID,
            "uptime_seconds": uptime,
            "queue_size": len(synthesis_queue),
            "generated_files": len(generated_files),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


@app.post("/execute")
async def execute_action(action: Dict[str, Any]):
    """Execute service action"""
    with tracer.start_as_current_span("execute_action") as span:
        cmd = action.get("action", "")
        span.set_attribute("action", cmd)

        if cmd == "clear_queue":
            synthesis_queue.clear()
            return {"status": "queue_cleared"}
        elif cmd == "clear_files":
            generated_files.clear()
            return {"status": "files_cleared"}
        elif cmd == "status":
            return {
                "queue_size": len(synthesis_queue),
                "generated_files": len(generated_files),
                "coordination_events": len(coordination_log),
            }
        else:
            raise HTTPException(status_code=400, detail="Unknown action")


@app.post("/receive")
async def receive_packet(packet: Dict[str, Any]):
    """Receive inter-service communication"""
    with tracer.start_as_current_span("receive_packet") as span:
        source = packet.get("source", "unknown")
        packet_type = packet.get("packet_type", "unknown")
        span.set_attribute("source", source)
        span.set_attribute("packet_type", packet_type)

        logger.info(f"[RECEIVE] Packet from {source}: {packet_type}")
        return {"status": "received", "correlation_id": packet.get("correlation_id")}


if __name__ == "__main__":
    import os
    import uvicorn

    port = int(os.getenv("PORT", "7070"))
    print("\n╔═════════════════════════════════════════╗")
    print(f"║  JONA COORDINATOR (Port {port})          ║")
    print("║  Data Synthesis Service                ║")
    print("║  📊 With OpenTelemetry Tracing         ║")
    print("╚═════════════════════════════════════════╝\n")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
