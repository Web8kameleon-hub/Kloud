"""
kloud Cloud Middleware Package
Industrial-grade middleware for real-time AI, sensor, and API traffic
Business: Ledjan Ahmati - WEB8euroweb GmbH
REAL DATA ONLY - NO MOCK/FAKE SIMULATION
"""

from datetime import datetime
import json
import logging
import os
import time
from typing import Callable

import psutil
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class QuotaGateMiddleware(BaseHTTPMiddleware):
    """Reject traffic when host resources are saturated."""

    async def dispatch(self, request: Request, call_next: Callable):
        start = time.time()
        cpu = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory().percent

        if cpu > 95 or mem > 95:
            return JSONResponse(
                {"status": "overload", "cpu": cpu, "memory": mem},
                status_code=503,
            )

        response = await call_next(request)
        duration = time.time() - start
        logging.info(
            "[QuotaGate] %s took %.3fs | CPU %.1f%% | MEM %.1f%%",
            request.url.path,
            duration,
            cpu,
            mem,
        )
        return response


class SecurityMiddleware(BaseHTTPMiddleware):
    """Attach security metadata and warn for suspicious clients."""

    async def dispatch(self, request: Request, call_next: Callable):
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")

        if not client_ip or "curl" in user_agent.lower():
            logging.warning(
                "[Security] Suspicious access from %s - UA: %s", client_ip, user_agent
            )

        response = await call_next(request)
        response.headers["X-Security-Level"] = "Industrial-Grade"
        response.headers["X-Verified-IP"] = client_ip
        return response


class MonitoringMiddleware(BaseHTTPMiddleware):
    """Persist request metrics for real-time observability."""

    async def dispatch(self, request: Request, call_next: Callable):
        timestamp = datetime.utcnow().isoformat()
        net_io = psutil.net_io_counters()
        metrics = {
            "timestamp": timestamp,
            "path": request.url.path,
            "method": request.method,
            "cpu": psutil.cpu_percent(interval=None),
            "mem": psutil.virtual_memory().percent,
            "disk": psutil.disk_usage("/").percent,
            "net_io": net_io.bytes_sent + net_io.bytes_recv,
        }

        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        with open(os.path.join(log_dir, "realtime_metrics.jsonl"), "a", encoding="utf-8") as handle:
            handle.write(json.dumps(metrics) + "\n")

        response = await call_next(request)
        response.headers["X-kloud-Monitor"] = "active"
        return response


__all__ = [
    "QuotaGateMiddleware",
    "SecurityMiddleware",
    "MonitoringMiddleware",
]


