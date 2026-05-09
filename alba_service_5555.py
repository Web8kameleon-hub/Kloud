"""
ALBA COLLECTOR SERVICE (Port 5555)
Network telemetry and data collection service
"""

import time
import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from collections import deque

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from cors_policy import apply_standard_cors

# OpenTelemetry imports
from tracing import setup_tracing, instrument_fastapi_app, instrument_http_clients

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AlbaCollector")

# Initialize tracing
tracer = setup_tracing("alba")

app = FastAPI(
    title="ALBA Collector",
    version="1.0.0",
    description="Network telemetry and data collection service",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Instrument FastAPI app for automatic tracing
instrument_fastapi_app(app, "alba")

# Instrument HTTP clients
instrument_http_clients()

apply_standard_cors(app)

# ═══════════════════════════════════════════════════════════════════
# DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════


class TelemetryEntry(BaseModel):
    id: Optional[str] = None
    source: str
    type: str
    payload: Dict[str, Any]
    timestamp: Optional[str] = None
    quality: float = 1.0
    metadata: Optional[Dict[str, Any]] = None


class CollectorMetrics(BaseModel):
    total_entries: int
    entries_per_second: float
    average_quality: float
    sources: Dict[str, int]
    types: Dict[str, int]


# ═══════════════════════════════════════════════════════════════════
# GLOBAL STATE
# ═══════════════════════════════════════════════════════════════════

START_TIME = time.time()
INSTANCE_ID = uuid.uuid4().hex[:8]

# Ring buffer for telemetry data
telemetry_buffer: deque = deque(maxlen=10000)
metrics_snapshot: Dict[str, Any] = {
    "total_entries": 0,
    "entries_per_second": 0.0,
    "sources": {},
    "types": {},
}

# ═══════════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════════


@app.post("/ingest")
async def ingest_telemetry(entry: TelemetryEntry):
    """Ingest telemetry from sensors/devices"""
    with tracer.start_as_current_span("ingest_telemetry") as span:
        span.set_attribute("source", entry.source)
        span.set_attribute("type", entry.type)

        entry.id = entry.id or uuid.uuid4().hex
        entry.timestamp = entry.timestamp or datetime.now(timezone.utc).isoformat()

        telemetry_buffer.append(entry.dict())

        # Update metrics
        metrics_snapshot["total_entries"] += 1
        metrics_snapshot["sources"][entry.source] = (
            metrics_snapshot["sources"].get(entry.source, 0) + 1
        )
        metrics_snapshot["types"][entry.type] = (
            metrics_snapshot["types"].get(entry.type, 0) + 1
        )

        span.set_attribute("buffer_size", len(telemetry_buffer))

        logger.info(
            f"[INGEST] {entry.type} from {entry.source} (total: {len(telemetry_buffer)})"
        )

        return {"status": "ingested", "id": entry.id, "timestamp": entry.timestamp}


@app.get("/data")
async def get_telemetry_data(limit: int = 100):
    """Retrieve collected telemetry"""
    with tracer.start_as_current_span("get_telemetry_data") as span:
        span.set_attribute("limit", limit)
        entries = list(telemetry_buffer)[-limit:]
        span.set_attribute("entries_returned", len(entries))

        return {
            "count": len(entries),
            "entries": entries,
            "buffer_size": len(telemetry_buffer),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


@app.get("/metrics")
async def get_metrics():
    """Get collector metrics"""
    with tracer.start_as_current_span("get_metrics") as span:
        uptime = time.time() - START_TIME
        eps = metrics_snapshot["total_entries"] / max(uptime, 1)

        span.set_attribute("uptime_seconds", uptime)
        span.set_attribute("total_entries", metrics_snapshot["total_entries"])
        span.set_attribute("entries_per_second", eps)

        return {
            "uptime_seconds": uptime,
            "total_entries": metrics_snapshot["total_entries"],
            "entries_per_second": eps,
            "buffer_size": len(telemetry_buffer),
            "sources": metrics_snapshot["sources"],
            "types": metrics_snapshot["types"],
        }


@app.post("/api/telemetry/ingest")
async def ingest_agent_telemetry(data: Dict[str, Any]):
    """Ingest telemetry from AI agents (AGIEM, ASI, Blerina)"""
    with tracer.start_as_current_span("ingest_agent_telemetry") as span:
        agent_name = data.get("source", "unknown_agent")
        agent_data = data.get("data", {})

        span.set_attribute("agent_name", agent_name)
        span.set_attribute("operation", agent_data.get("operation", "unknown"))

        # Store in telemetry buffer
        entry = TelemetryEntry(
            source=agent_name,
            type="agent_telemetry",
            payload=agent_data,  # Changed from 'data' to 'payload'
            metadata={"agent": True, "operation": agent_data.get("operation")},
        )

        telemetry_buffer.append(entry.dict())
        metrics_snapshot["total_entries"] += 1
        metrics_snapshot["sources"][agent_name] = (
            metrics_snapshot["sources"].get(agent_name, 0) + 1
        )

        logger.info(f"[AGENT] {agent_name}.{agent_data.get('operation')} -> Alba")

        return {"status": "ingested", "agent": agent_name, "timestamp": entry.timestamp}


@app.get("/health")
async def health():
    """Service health check"""
    with tracer.start_as_current_span("health_check") as span:
        uptime = time.time() - START_TIME
        buffer_capacity = len(telemetry_buffer) / 10000

        span.set_attribute("status", "operational")
        span.set_attribute("buffer_capacity", buffer_capacity)

        return {
            "service": "alba-collector",
            "status": "operational",
            "instance_id": INSTANCE_ID,
            "uptime_seconds": uptime,
            "buffer_usage": f"{buffer_capacity * 100:.1f}%",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


@app.get("/api/v1/status")
@app.get("/api/status")
async def api_status():
    """API v1 status endpoint"""
    return {
        "service": "ALBA Collector",
        "version": "1.0.0",
        "status": "operational",
        "uptime_seconds": time.time() - START_TIME,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/v1/spec")
async def api_spec():
    """OpenAPI specification"""
    return app.openapi()


@app.post("/execute")
async def execute_action(action: Dict[str, Any]):
    """Execute service action"""
    with tracer.start_as_current_span("execute_action") as span:
        cmd = action.get("action", "")
        span.set_attribute("action", cmd)

        if cmd == "clear":
            telemetry_buffer.clear()
            return {"status": "buffer_cleared"}
        elif cmd == "export":
            return {
                "status": "exported",
                "entries": list(telemetry_buffer),
                "count": len(telemetry_buffer),
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

    port = int(os.getenv("PORT", "5555"))
    print("\n╔═════════════════════════════════════════╗")
    print(f"║  ALBA COLLECTOR (Port {port})             ║")
    print("║  Artificial Labor Bits Array            ║")
    print("║  Network Telemetry Service              ║")
    print("╚═════════════════════════════════════════╝\n")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
