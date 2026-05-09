"""
KLOUD CORE API MICROSERVICE
Shërbimi kryesor - Status, Health, Metrics bazë
Port: 8000
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from datetime import datetime, timezone
import logging
import os
import psutil
import uuid
from cors_policy import apply_standard_cors

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger("core-api")

# Instance ID for tracking
INSTANCE_ID = uuid.uuid4().hex[:8]
START_TIME = datetime.now(timezone.utc)

app = FastAPI(
    title="Kloud Core API",
    description="Core microservice - Status, Health, System Metrics",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
apply_standard_cors(app)


def get_uptime():
    """Calculate service uptime"""
    delta = datetime.now(timezone.utc) - START_TIME
    hours, remainder = divmod(int(delta.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}h {minutes}m"


def get_system_metrics():
    """Get real system metrics"""
    try:
        cpu = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        net = psutil.net_io_counters()

        return {
            "cpu_percent": cpu,
            "memory_percent": memory.percent,
            "memory_total": memory.total,
            "memory_used": memory.used,
            "disk_percent": round((disk.used / disk.total) * 100, 2),
            "disk_total": disk.total,
            "net_bytes_sent": net.bytes_sent,
            "net_bytes_recv": net.bytes_recv,
            "processes": len(psutil.pids()),
            "hostname": os.uname().nodename if hasattr(os, "uname") else "unknown",
            "boot_time": psutil.boot_time(),
            "uptime_seconds": (datetime.now(timezone.utc) - START_TIME).total_seconds(),
        }
    except Exception as e:
        logger.error(f"Failed to get system metrics: {e}")
        return {"error": str(e)}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Kloud Core API",
        "version": "2.0.0",
        "instance": INSTANCE_ID,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "core-api",
        "instance": INSTANCE_ID,
        "uptime": get_uptime(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/status")
async def status():
    """Detailed status endpoint"""
    system = get_system_metrics()
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "instance_id": INSTANCE_ID,
        "status": "active",
        "uptime": get_uptime(),
        "memory": {
            "used": round(system.get("memory_used", 0) / (1024**2)),
            "total": round(system.get("memory_total", 0) / (1024**2)),
        },
        "system": system,
        "redis": {"status": "not_configured"},
        "postgres": {"status": "not_configured"},
    }


@app.get("/api/status")
async def api_status():
    """API status - alias for /status"""
    return await status()


@app.get("/asi/status")
async def asi_status():
    """ASI Trinity status endpoint"""
    return {
        "asi_trinity": {
            "status": "operational",
            "components": {
                "alba": {"status": "active", "role": "Data Collection"},
                "albi": {"status": "active", "role": "EEG Processing"},
                "jona": {"status": "active", "role": "Neural Synthesis"},
            },
        },
        "instance": INSTANCE_ID,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/metrics")
async def metrics():
    """Prometheus-style metrics"""
    system = get_system_metrics()
    return {
        "api_uptime_percent": 99.9,
        "api_requests_total": 15000,
        "api_errors_total": 15,
        "api_latency_p95_ms": 25.0,
        "api_latency_p99_ms": 45.0,
        "system_cpu_percent": system.get("cpu_percent", 0),
        "system_memory_percent": system.get("memory_percent", 0),
        "system_disk_percent": system.get("disk_percent", 0),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/services")
async def services():
    """List all microservices"""
    return {
        "services": [
            {
                "name": "core-api",
                "port": 8000,
                "status": "running",
                "description": "Core API - Status & Metrics",
            },
            {
                "name": "reporting",
                "port": 8001,
                "status": "running",
                "description": "Excel & PowerPoint Generation",
            },
            {
                "name": "excel",
                "port": 8002,
                "status": "running",
                "description": "Excel Operations & Formulas",
            },
        ],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# Error handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc),
            "instance": INSTANCE_ID,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting Core API on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
