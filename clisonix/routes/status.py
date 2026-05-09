"""Status and health related endpoints."""

from datetime import datetime
import time

import psutil
from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/status")
async def system_status():
    """Return real-time host metrics."""

    net_io = psutil.net_io_counters()
    stats = {
        "timestamp": datetime.utcnow().isoformat(),
        "cpu_percent": psutil.cpu_percent(interval=None),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage("/").percent,
        "net_io": {
            "sent_MB": round(net_io.bytes_sent / (1024**2), 2),
            "recv_MB": round(net_io.bytes_recv / (1024**2), 2),
        },
        "active_processes": len(psutil.pids()),
        "uptime_sec": round(time.time() - psutil.boot_time()),
    }
    return JSONResponse({"status": "ok", "metrics": stats})


@router.get("/ping")
async def ping():
    return {"message": "kloud active", "time": datetime.utcnow().isoformat()}


