#!/usr/bin/env python3
"""ASI Realtime Engine API Server"""

from fastapi import FastAPI
from asi_core import ASICore
import uvicorn
from datetime import datetime
from cors_policy import apply_standard_cors

# API Version
API_V1 = "/api/v1"

app = FastAPI(
    title="ASI Engine",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

apply_standard_cors(app)

asi = ASICore()


@app.get("/")
def root():
    return {
        "service": "ASI Realtime Engine",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "GET /health": "Health check",
            "GET /status": "Realtime status",
            "GET /api/status": "API status",
            "GET /metrics": "Engine metrics",
            "GET /nodes": "ASI nodes",
        },
    }


@app.get("/health")
def health():
    return {"status": "operational", "engine": "ASI Realtime"}


@app.get("/status")
@app.get("/api/status")
@app.get(API_V1 + "/status")
def status():
    try:
        rt_status = asi.get_realtime_status()
        rt_status["timestamp"] = datetime.utcnow().isoformat()
        return rt_status
    except Exception as e:
        return {
            "status": "operational",
            "service": "ASI Engine",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }


@app.get(API_V1 + "/spec")
def api_spec():
    return app.openapi()


@app.get("/metrics")
def metrics():
    return asi.realtime_engine.collect_metrics()


@app.get("/nodes")
def nodes():
    return asi.nodes


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9094)
