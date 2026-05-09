"""
ALBI PROCESSOR SERVICE (Port 6680)
Neural analytics and pattern detection service
"""

import asyncio
import json
import time
import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Any
from collections import defaultdict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from cors_policy import apply_standard_cors

# OpenTelemetry imports
from tracing import setup_tracing, instrument_fastapi_app, instrument_http_clients

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AlbiProcessor")

# Initialize tracing
tracer = setup_tracing("albi")

app = FastAPI(
    title="ALBI Processor",
    version="1.0.0",
    description="Neural analytics and pattern detection service",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Instrument FastAPI app for automatic tracing
instrument_fastapi_app(app, "albi")

# Instrument HTTP clients
instrument_http_clients()

apply_standard_cors(app)

# ═══════════════════════════════════════════════════════════════════
# GLOBAL STATE
# ═══════════════════════════════════════════════════════════════════

START_TIME = time.time()
INSTANCE_ID = uuid.uuid4().hex[:8]

analysis_cache = []
insights = []
anomalies = []

# ═══════════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════════


@app.post("/analyze")
async def analyze_data(data: Dict[str, Any]):
    """Analyze telemetry data for patterns and anomalies"""
    with tracer.start_as_current_span("analyze_data") as span:
        # Simulate neural analysis
        channels = data.get("channels", {})
        analysis_id = uuid.uuid4().hex

        span.set_attribute("channel_count", len(channels))

        # Simple statistical analysis
        stats = {}
        detected_anomalies = []

        for channel_name, values in channels.items():
            if isinstance(values, list) and len(values) > 0:
                try:
                    avg = sum(values) / len(values)
                    max_v = max(values)
                    min_v = min(values)

                    # Anomaly detection: values > 2 std devs
                    variance = sum((x - avg) ** 2 for x in values) / len(values)
                    std_dev = variance**0.5

                    outliers = [x for x in values if abs(x - avg) > 2 * std_dev]

                    stats[channel_name] = {
                        "mean": avg,
                        "max": max_v,
                        "min": min_v,
                        "std_dev": std_dev,
                        "outlier_count": len(outliers),
                    }

                    if len(outliers) > 0:
                        detected_anomalies.append(channel_name)
                except:
                    pass

        result = {
            "analysis_id": analysis_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "statistics": stats,
            "anomalies": detected_anomalies,
            "confidence": 0.92,
            "pattern_type": "neural_oscillation",
        }

        span.set_attribute("anomaly_count", len(detected_anomalies))
        span.set_attribute("analysis_id", analysis_id)

        analysis_cache.append(result)
        if len(detected_anomalies) > 0:
            anomalies.append(
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "channels": detected_anomalies,
                    "analysis_id": analysis_id,
                }
            )

        logger.info(
            f"[ANALYZE] {len(stats)} channels, {len(detected_anomalies)} anomalies"
        )

        return result


@app.get("/insights")
async def get_insights(limit: int = 50):
    """Get recent analysis insights"""
    with tracer.start_as_current_span("get_insights") as span:
        span.set_attribute("limit", limit)
        recent = analysis_cache[-limit:]
        span.set_attribute("insights_returned", len(recent))

        return {
            "count": len(recent),
            "insights": recent,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


@app.get("/anomalies")
async def get_anomalies(limit: int = 20):
    """Get detected anomalies"""
    with tracer.start_as_current_span("get_anomalies") as span:
        span.set_attribute("limit", limit)
        recent = anomalies[-limit:]
        span.set_attribute("anomalies_returned", len(recent))

        return {
            "count": len(recent),
            "anomalies": recent,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


@app.post("/api/analytics/agent")
async def agent_analytics(data: Dict[str, Any]):
    """Process analytics from AI agents"""
    with tracer.start_as_current_span("agent_analytics") as span:
        agent = data.get("agent", "unknown")
        operation = data.get("operation", "unknown")
        duration_ms = data.get("duration_ms", 0)
        tokens = data.get("tokens", {})

        span.set_attribute("agent", agent)
        span.set_attribute("operation", operation)
        span.set_attribute("duration_ms", duration_ms)

        # Store analytics
        analytics_entry = {
            "agent": agent,
            "operation": operation,
            "duration_ms": duration_ms,
            "input_tokens": tokens.get("input"),
            "output_tokens": tokens.get("output"),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "success": data.get("success", True),
        }

        insights.append(analytics_entry)

        logger.info(
            f"[AGENT] {agent}.{operation} -> Albi (duration: {duration_ms:.2f}ms)"
        )

        return {
            "status": "analyzed",
            "agent": agent,
            "timestamp": analytics_entry["timestamp"],
        }

        return {
            "count": len(recent),
            "anomalies": recent,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


@app.get("/metrics")
async def get_metrics():
    """Get processor metrics"""
    uptime = time.time() - START_TIME

    return {
        "uptime_seconds": uptime,
        "total_analyses": len(analysis_cache),
        "total_anomalies": len(anomalies),
        "analyses_per_minute": (len(analysis_cache) / max(uptime / 60, 1)),
        "cache_size": len(analysis_cache),
        "anomaly_rate": len(anomalies) / max(len(analysis_cache), 1),
    }


@app.get("/health")
async def health():
    """Service health check"""
    with tracer.start_as_current_span("health_check") as span:
        uptime = time.time() - START_TIME

        span.set_attribute("status", "operational")
        span.set_attribute("uptime_seconds", uptime)

        return {
            "service": "albi-processor",
            "status": "operational",
            "instance_id": INSTANCE_ID,
            "uptime_seconds": uptime,
            "processing_queue": len(analysis_cache),
            "anomalies_detected": len(anomalies),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


@app.get("/api/v1/status")
@app.get("/api/status")
async def api_status():
    """API v1 status endpoint"""
    return {
        "service": "ALBI Processor",
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

        if cmd == "clear_cache":
            analysis_cache.clear()
            return {"status": "cache_cleared"}
        elif cmd == "clear_anomalies":
            anomalies.clear()
            return {"status": "anomalies_cleared"}
        elif cmd == "reset":
            analysis_cache.clear()
            anomalies.clear()
            return {"status": "reset_complete"}
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

    port = int(os.getenv("PORT", "6680"))
    print("\n╔═════════════════════════════════════════╗")
    print(f"║  ALBI PROCESSOR (Port {port})            ║")
    print("║  Artificial Labor Bits Intelligence    ║")
    print("║  Neural Analytics Service              ║")
    print("║  📊 With OpenTelemetry Tracing         ║")
    print("╚═════════════════════════════════════════╝\n")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
