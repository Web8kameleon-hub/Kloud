# === REPORTING PROXY ROUTES (Append to main.py) ===
# This code appends to existing FastAPI app - do NOT create new app
# noqa: F821 - APIRouter, Response, JSONResponse, StreamingResponse, app exist in main.py scope
import httpx
import traceback
import json
from io import BytesIO
from fastapi import APIRouter
from fastapi.responses import JSONResponse, StreamingResponse

# Microservices: Docker DNS, both containers in kloud-unified network
REPORTING_SERVICE_URL = "http://kloud-reporting:8001"

# Production-grade timeout: 90s for most endpoints (reporting is slow), 180s for Excel
PROXY_TIMEOUT = httpx.Timeout(90.0, connect=15.0)
EXCEL_TIMEOUT = httpx.Timeout(180.0, connect=15.0)

reporting_proxy_router = APIRouter(prefix="/api/reporting", tags=["reporting-proxy"])

def handle_proxy_error(e: Exception, endpoint: str) -> JSONResponse:
    """Production-grade error handler - NEVER swallow exceptions"""
    traceback.print_exc()
    error_type = e.__class__.__name__
    error_msg = str(e) or f"{error_type} (no message)"
    print(f"[PROXY ERROR] {endpoint}: {error_type} - {error_msg}")
    return JSONResponse(
        content={
            "status": "error",
            "type": error_type,
            "message": error_msg,
            "endpoint": endpoint
        },
        status_code=502
    )

@reporting_proxy_router.get("/health")
async def rp_health():
    try:
        async with httpx.AsyncClient(timeout=PROXY_TIMEOUT) as c:
            r = await c.get(f"{REPORTING_SERVICE_URL}/health")
            r.raise_for_status()
            return r.json()
    except Exception as e:
        return handle_proxy_error(e, "/health")

@reporting_proxy_router.get("/dashboard")
async def rp_dashboard():
    try:
        async with httpx.AsyncClient(timeout=PROXY_TIMEOUT) as c:
            r = await c.get(f"{REPORTING_SERVICE_URL}/api/reporting/dashboard")
            r.raise_for_status()
            return r.json()
    except Exception as e:
        return handle_proxy_error(e, "/dashboard")

@reporting_proxy_router.get("/docker-containers")
async def rp_containers():
    try:
        async with httpx.AsyncClient(timeout=PROXY_TIMEOUT) as c:
            r = await c.get(f"{REPORTING_SERVICE_URL}/api/reporting/docker-containers")
            r.raise_for_status()
            return r.json()
    except Exception as e:
        return handle_proxy_error(e, "/docker-containers")

@reporting_proxy_router.get("/docker-stats")
async def rp_stats():
    try:
        async with httpx.AsyncClient(timeout=PROXY_TIMEOUT) as c:
            r = await c.get(f"{REPORTING_SERVICE_URL}/api/reporting/docker-stats")
            r.raise_for_status()
            return r.json()
    except Exception as e:
        return handle_proxy_error(e, "/docker-stats")

@reporting_proxy_router.get("/system-metrics")
async def rp_metrics():
    try:
        async with httpx.AsyncClient(timeout=PROXY_TIMEOUT) as c:
            r = await c.get(f"{REPORTING_SERVICE_URL}/api/reporting/system-metrics")
            r.raise_for_status()
            return r.json()
    except Exception as e:
        return handle_proxy_error(e, "/system-metrics")

@reporting_proxy_router.get("/export-excel")
async def rp_excel():
    try:
        async with httpx.AsyncClient(timeout=EXCEL_TIMEOUT) as c:
            r = await c.get(f"{REPORTING_SERVICE_URL}/api/reporting/export-excel")
            r.raise_for_status()
            return StreamingResponse(
                BytesIO(r.content),
                media_type=r.headers.get("content-type", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
                headers={"Content-Disposition": r.headers.get("Content-Disposition", "attachment; filename=report.xlsx")}
            )
    except Exception as e:
        return handle_proxy_error(e, "/export-excel")

# NOTE: 'app', 'APIRouter', 'JSONResponse', 'StreamingResponse' exist in main.py scope (appended code)
try:
    app.include_router(reporting_proxy_router)
except NameError:
    from main import app
    app.include_router(reporting_proxy_router)
print(">>> REPORTING PROXY ENABLED ON PORT 8000 <<<")
# === END REPORTING PROXY ===

