#!/usr/bin/env python3
"""
AGIEM TELEMETRY SERVICE (Port 6680)
Agent Intelligence Metrics & Monitoring

Provides real-time monitoring of:
- ALBA: Data collection health
- ALBI: Neural analytics health
- JONA: Alignment verification health
- ASI: API generation & deployment health
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import json
from datetime import datetime, timezone
from agiem_core import AGIEMCore, MeshReporter, NodeReal
from typing import Optional, Dict, Any
from cors_policy import apply_standard_cors

# Initialize FastAPI app
app = FastAPI(
    title="AGIEM Telemetry Service",
    description="Real-time monitoring of AI agent pipeline health",
    version="1.0.0",
)

# Add CORS middleware
apply_standard_cors(app)

# Initialize core services
core = AGIEMCore()
mesh_reporter = MeshReporter(core)
node = NodeReal(core, node_id="agiem-telemetry-6680")

# Global state
SERVICE_START = datetime.now(timezone.utc).isoformat()
REQUEST_COUNT = 0


@app.on_event("startup")
async def startup():
    """Initialize service on startup"""
    core.log_event("AGIEM_TELEMETRY", "Service starting on port 6680", "INFO")
    # Register this node with Mesh HQ
    try:
        mesh_reporter.register(
            {
                "id": "agiem-telemetry-6680",
                "type": "telemetry",
                "port": 6680,
                "service": "AGIEM Telemetry Service",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
        core.log_event("AGIEM_TELEMETRY", "Registered with Mesh HQ", "INFO")
    except Exception as e:
        core.log_event("AGIEM_TELEMETRY", f"Mesh registration failed: {e}", "WARN")


@app.get("/health")
async def health():
    """Health check endpoint"""
    global REQUEST_COUNT
    REQUEST_COUNT += 1

    return {
        "status": "healthy",
        "service": "agiem-telemetry-6680",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "uptime_since": SERVICE_START,
        "requests_served": REQUEST_COUNT,
    }


@app.get("/status")
async def status():
    """Get detailed status of all agent nodes"""
    return {
        "service": "AGIEM Telemetry",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "nodes": core.nodes,
        "stages": {
            stage_name: {
                "name": stage.name,
                "role": stage.role,
                "description": stage.description,
                "metrics": stage.metrics,
            }
            for stage_name, stage in core.stages.items()
        },
    }


@app.get("/nodes")
async def get_nodes():
    """List all registered nodes"""
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "nodes": core.nodes,
        "total": len(core.nodes),
    }


@app.get("/nodes/{node_id}")
async def get_node(node_id: str):
    """Get specific node status"""
    if node_id not in core.nodes:
        raise HTTPException(status_code=404, detail=f"Node {node_id} not found")

    return {
        "node_id": node_id,
        "details": core.nodes[node_id],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.put("/nodes/{node_id}/status")
async def update_node_status(node_id: str, status: str):
    """Update node status"""
    core.update_node_status(node_id, status)
    return {
        "node_id": node_id,
        "new_status": status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/stages")
async def get_stages():
    """List all reproduction stages"""
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "stages": core.reproduction_inventory(),
    }


@app.get("/stages/{stage_name}")
async def get_stage(stage_name: str):
    """Get specific stage details"""
    if stage_name not in core.stages:
        raise HTTPException(status_code=404, detail=f"Stage {stage_name} not found")

    stage = core.stages[stage_name]
    return {
        "stage_name": stage_name,
        "name": stage.name,
        "role": stage.role,
        "description": stage.description,
        "metrics": stage.metrics,
        "notes": stage.notes,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/stages/{stage_name}/metrics")
async def record_stage_metric(stage_name: str, metric_key: str, value: Any):
    """Record a metric for a stage"""
    core.record_stage_metric(stage_name, metric_key, value)
    return {
        "stage_name": stage_name,
        "metric_key": metric_key,
        "value": value,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/metrics")
async def get_metrics():
    """Get system metrics from node"""
    try:
        metrics = node.collect_metrics()
        return {"timestamp": datetime.now(timezone.utc).isoformat(), "metrics": metrics}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to collect metrics: {str(e)}"
        )


@app.get("/logs")
async def get_logs(limit: int = 50):
    """Get recent log entries"""
    recent_logs = core.logs[-limit:] if core.logs else []
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "log_count": len(recent_logs),
        "logs": recent_logs,
    }


@app.post("/logs/event")
async def log_event(source: str, message: str, level: str = "INFO"):
    """Log an event"""
    core.log_event(source, message, level)
    return {
        "source": source,
        "message": message,
        "level": level,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/cycles")
async def get_cycles(limit: int = 20):
    """Get reproduction cycle history"""
    recent_cycles = (
        core.reproduction_history[-limit:] if core.reproduction_history else []
    )
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "cycle_count": len(core.reproduction_history),
        "recent_cycles": recent_cycles,
    }


@app.get("/multi-tenant")
async def get_multi_tenant():
    """Get multi-tenant metrics"""
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "metrics": core.multi_tenant_metrics(),
    }


@app.post("/register")
async def register_node(metadata: Optional[Dict[str, Any]] = None):
    """Register node with Mesh HQ"""
    result = mesh_reporter.register(metadata)
    return {"timestamp": datetime.now(timezone.utc).isoformat(), "registration": result}


@app.post("/report")
async def send_report():
    """Send status report to Mesh HQ"""
    metrics = node.collect_metrics()
    result = mesh_reporter.send_status(metrics)
    return {"timestamp": datetime.now(timezone.utc).isoformat(), "report": result}


@app.get("/info")
async def info():
    """Get service information"""
    return {
        "service": "AGIEM Telemetry Service",
        "port": 6680,
        "version": "1.0.0",
        "started_at": SERVICE_START,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "endpoints": {
            "health": "/health",
            "status": "/status",
            "nodes": "/nodes",
            "stages": "/stages",
            "metrics": "/metrics",
            "logs": "/logs",
            "cycles": "/cycles",
            "multi_tenant": "/multi-tenant",
            "register": "/register (POST)",
            "report": "/report (POST)",
        },
    }


if __name__ == "__main__":
    port = int(os.getenv("AGIEM_PORT", "6680"))
    host = os.getenv("AGIEM_HOST", "0.0.0.0")

    print(f"\n{'=' * 60}")
    print(f"  AGIEM TELEMETRY SERVICE")
    print(f"  Listening on {host}:{port}")
    print(f"  Real-time agent pipeline monitoring")
    print(f"{'=' * 60}\n")

    uvicorn.run(app, host=host, port=port, log_level="info")
