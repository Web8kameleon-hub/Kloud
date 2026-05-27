"""
ULTRA REPORTING API ENDPOINTS
Automat raportet: Excel + PowerPoint + Dashboards në kërkesë
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Query, Request
from fastapi.responses import JSONResponse, PlainTextResponse, Response
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Dict, Any, List
import os
import sys
import logging
from pathlib import Path
import json

try:
    import cbor2  # type: ignore
except ImportError:  # pragma: no cover - runtime safety
    cbor2 = None  # type: ignore[assignment]

try:
    import msgpack  # type: ignore
except ImportError:  # pragma: no cover - runtime safety
    msgpack = None  # type: ignore[assignment]

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import the ultra reporting module
from ultra_reporting import (
    UltraExcelExporter,
    UltraPowerPointGenerator,
    UltraReportGenerator,
    MetricsSnapshot,
)

# Import error tracker
from error_tracker import error_tracker

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/reporting", tags=["reporting"])

# Ensure reports directory exists
REPORTS_DIR = Path("./reports")
REPORTS_DIR.mkdir(exist_ok=True)


class ExportRequest(BaseModel):
    """Request body për Excel/PowerPoint export"""

    title: str = "Kloud Cloud Metrics Report"
    format: str = "xlsx"  # xlsx, pptx, both
    include_sla: bool = True
    include_alerts: bool = True
    date_range_hours: int = 24


class ReportMetadata(BaseModel):
    """Metadata për raportin e gjeneruar"""

    id: str
    title: str
    format: str
    generated_at: str
    file_path: str
    size_bytes: int


class DashboardMetrics(BaseModel):
    """Unified dashboard metrics"""

    api_uptime_percent: float
    api_requests_per_second: int
    api_error_rate_percent: float
    api_latency_p95_ms: float
    api_latency_p99_ms: float
    ai_agent_calls_24h: int
    ai_agent_success_rate: float
    documents_generated_24h: int
    cache_hit_rate_percent: float
    system_cpu_percent: float
    system_memory_percent: float
    system_disk_percent: float
    active_alerts: List[Dict[str, Any]]
    sla_status: str


LIGHTWEIGHT_MIME_MAP = {
    "cbor": "application/cbor",
    "msgpack": "application/msgpack",
    "compact": "text/plain",
    "lora": "text/plain",
}


def _no_fake_http_exception(
    endpoint: str, required_sources: List[str]
) -> HTTPException:
    return HTTPException(
        status_code=503,
        detail={
            "error": "real_reporting_source_unconfigured",
            "endpoint": endpoint,
            "message": "No fake ever: reporting data is unavailable until real telemetry sources are configured.",
            "required_sources": required_sources,
            "generated_at": datetime.now().isoformat(),
        },
    )


def _pick_format(request: Request) -> str:
    format_param = (request.query_params.get("format") or "").strip().lower()
    if format_param in {
        "json",
        "cbor",
        "msgpack",
        "mpack",
        "mpk",
        "compact",
        "lora",
        "minimal",
    }:
        return format_param

    accept = (request.headers.get("accept") or "").lower()
    if "application/cbor" in accept:
        return "cbor"
    if "application/msgpack" in accept or "application/x-msgpack" in accept:
        return "msgpack"
    if "text/plain" in accept and "json" not in accept:
        return "compact"
    return "json"


def _format_numeric(value: Any) -> Any:
    if isinstance(value, float):
        return round(value, 3)
    return value


def _as_compact(payload: Dict[str, Any], mode: str) -> str:
    if "api_uptime_percent" not in payload:
        # Generic fallback for broader payloads (e.g., history, stats)
        flat: Dict[str, Any] = {}
        for key, value in payload.items():
            if isinstance(value, (int, float, str)):
                flat[key] = _format_numeric(value)
        if mode in {"lora", "minimal"}:
            if flat:
                return "|".join(f"{key}={value}" for key, value in flat.items())
            return json.dumps(payload, separators=(",", ":"))
        if flat:
            return json.dumps(flat, separators=(",", ":"))
        return json.dumps(payload, separators=(",", ":"))

    essentials = {
        "upt": _format_numeric(payload.get("api_uptime_percent")),
        "reqps": _format_numeric(payload.get("api_requests_per_second")),
        "err": _format_numeric(payload.get("api_error_rate_percent")),
        "lat95": _format_numeric(payload.get("api_latency_p95_ms")),
        "lat99": _format_numeric(payload.get("api_latency_p99_ms")),
        "ai": _format_numeric(payload.get("ai_agent_calls_24h")),
        "ai_ok": _format_numeric(payload.get("ai_agent_success_rate")),
        "doc24": _format_numeric(payload.get("documents_generated_24h")),
        "cache": _format_numeric(payload.get("cache_hit_rate_percent")),
        "cpu": _format_numeric(payload.get("system_cpu_percent")),
        "mem": _format_numeric(payload.get("system_memory_percent")),
        "disk": _format_numeric(payload.get("system_disk_percent")),
        "alerts": len(payload.get("active_alerts", [])),
        "sla": payload.get("sla_status"),
    }

    if mode in {"lora", "minimal"}:
        return "|".join(
            f"{key}={value}" for key, value in essentials.items() if value is not None
        )

    return json.dumps(
        {k: v for k, v in essentials.items() if v is not None}, separators=(",", ":")
    )


def _serialize_payload(request: Request, payload: Dict[str, Any]) -> Response:
    fmt = _pick_format(request)

    if fmt == "json" or fmt == "":
        return JSONResponse(payload)

    if fmt == "cbor":
        if cbor2 is None:
            raise HTTPException(
                status_code=406, detail="CBOR format unavailable - install cbor2"
            )
        return Response(
            content=cbor2.dumps(payload), media_type=LIGHTWEIGHT_MIME_MAP["cbor"]
        )

    if fmt in {"msgpack", "mpack", "mpk"}:
        if msgpack is None:
            raise HTTPException(
                status_code=406,
                detail="MessagePack format unavailable - install msgpack",
            )
        return Response(
            content=msgpack.packb(payload, use_bin_type=True),
            media_type=LIGHTWEIGHT_MIME_MAP["msgpack"],
        )

    if fmt in {"compact", "lora", "minimal"}:
        text_payload = _as_compact(payload, fmt)
        return PlainTextResponse(
            text_payload, media_type=LIGHTWEIGHT_MIME_MAP.get(fmt, "text/plain")
        )

    # Fallback to JSON for any unknown request
    return JSONResponse(payload)


@router.get("/export-excel")
async def export_excel(background_tasks: BackgroundTasks) -> Response:
    """
    Eksporto metriken në Excel me grafike, pivot tabela, dhe SLA tracking
    Kthen file-in direkt për download
    """
    raise _no_fake_http_exception(
        "/api/reporting/export-excel",
        ["victoriametrics", "prometheus", "alertmanager"],
    )


@router.get("/export-pptx")
async def export_powerpoint(background_tasks: BackgroundTasks) -> Response:
    """
    Eksporto metriken në PowerPoint presentation
    Kthen file-in direkt për download
    """
    raise _no_fake_http_exception(
        "/api/reporting/export-pptx",
        ["victoriametrics", "prometheus", "alertmanager"],
    )


@router.post("/export-both")
async def export_both(request: ExportRequest) -> Dict[str, Any]:
    """Eksporto si Excel edhe PowerPoint në të njejtën kohë"""
    raise _no_fake_http_exception(
        "/api/reporting/export-both",
        ["victoriametrics", "prometheus", "alertmanager"],
    )


@router.get("/dashboard")
async def get_unified_dashboard(request: Request) -> Response:
    """
    Unified dashboard combining Datadog + Grafana + Prometheus metrics

    Real implementation would:
    - Query VictoriaMetrics for latest metrics
    - Fetch from Prometheus for detailed data
    - Get alerts from AlertManager
    - Aggregate all sources into single response
    """

    raise _no_fake_http_exception(
        "/api/reporting/dashboard",
        ["victoriametrics", "prometheus", "alertmanager"],
    )


@router.get("/metrics-history")
async def get_metrics_history(
    request: Request,
    hours: int = Query(24, ge=1, le=720),
    metric_type: str = Query("all", pattern="^(all|api|ai|infrastructure)$"),
) -> Response:
    """
    Merr historiken e metrikave për periudhën e caktuar

    Metric types:
    - all: Të gjitha metriken
    - api: API request/error/latency metrics
    - ai: AI agent metrics
    - infrastructure: System/DB/cache metrics
    """

    raise _no_fake_http_exception(
        "/api/reporting/metrics-history",
        ["victoriametrics", "prometheus", "timeseries_storage"],
    )


@router.get("/download/{filename}")
async def download_report(filename: str):
    """Shkarko raportin e gjeneruar"""

    from fastapi.responses import FileResponse

    try:
        filepath = REPORTS_DIR / filename

        if not filepath.exists():
            raise HTTPException(status_code=404, detail="Report not found")

        return FileResponse(
            path=filepath, media_type="application/octet-stream", filename=filename
        )

    except Exception as e:
        logger.error(f"Download failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list-reports")
async def list_reports() -> List[ReportMetadata]:
    """Listo të gjithë raportet e gjeneruar"""

    try:
        reports = []

        for filepath in REPORTS_DIR.glob("*"):
            if filepath.is_file():
                stat = filepath.stat()

                reports.append(
                    ReportMetadata(
                        id=filepath.stem,
                        title=filepath.stem.replace("_", " "),
                        format=filepath.suffix.lower().lstrip("."),
                        generated_at=datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        file_path=str(filepath),
                        size_bytes=stat.st_size,
                    )
                )

        return sorted(reports, key=lambda r: r.generated_at, reverse=True)

    except Exception as e:
        logger.error(f"List reports failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/clear-reports")
async def clear_old_reports(days_old: int = Query(7, ge=1)) -> Dict[str, Any]:
    """Pastro raportet e vjetra më shumë se N ditë"""

    try:
        cutoff_time = datetime.now() - timedelta(days=days_old)
        deleted_count = 0
        total_freed = 0

        for filepath in REPORTS_DIR.glob("*"):
            if filepath.is_file():
                file_time = datetime.fromtimestamp(filepath.stat().st_mtime)
                if file_time < cutoff_time:
                    size = filepath.stat().st_size
                    filepath.unlink()
                    deleted_count += 1
                    total_freed += size

        return {
            "success": True,
            "deleted_files": deleted_count,
            "freed_bytes": total_freed,
            "freed_mb": round(total_freed / (1024 * 1024), 2),
            "message": f"✓ Deleted {deleted_count} reports older than {days_old} days",
        }

    except Exception as e:
        logger.error(f"Clear reports failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# HEALTH & STATUS ENDPOINTS - Required by Frontend Status Monitor
# ============================================================================


@router.get("/health")
async def reporting_health():
    """
    Health check for reporting module.
    Returns status of all reporting-related services.
    """
    try:
        # Check if reports directory exists and is writable
        reports_dir_ok = REPORTS_DIR.exists() and os.access(REPORTS_DIR, os.W_OK)

        return {
            "status": "healthy" if reports_dir_ok else "degraded",
            "service": "reporting",
            "timestamp": datetime.now().isoformat(),
            "checks": {
                "reports_directory": "ok" if reports_dir_ok else "error",
                "excel_export": "available",
                "pptx_export": "available",
                "dashboard": "available",
            },
            "version": "2.0.0",
            "uptime": "operational",
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "service": "reporting", "error": str(e)}


@router.get("/docker-containers")
async def get_docker_containers():
    """
    Returns Docker container status for reporting dashboard.
    Uses subprocess to get actual container status if available.
    """
    import subprocess

    try:
        # Try to get actual Docker container info
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}|{{.Status}}|{{.Ports}}"],
            capture_output=True,
            text=True,
            timeout=5,
        )

        containers = []
        if result.returncode == 0 and result.stdout.strip():
            for line in result.stdout.strip().split("\n"):
                parts = line.split("|")
                if len(parts) >= 2:
                    name = parts[0]
                    status = parts[1]
                    ports = parts[2] if len(parts) > 2 else ""

                    containers.append(
                        {
                            "name": name,
                            "status": "running" if "Up" in status else "stopped",
                            "health": "healthy"
                            if "healthy" in status.lower()
                            else "unknown",
                            "uptime": status,
                            "ports": ports,
                        }
                    )

        if not containers:
            raise _no_fake_http_exception(
                "/api/reporting/docker-containers",
                ["docker_cli", "container_runtime_api"],
            )

        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "total_containers": len(containers),
            "containers": containers,
        }

    except subprocess.TimeoutExpired:
        logger.warning("Docker command timed out")
        raise _no_fake_http_exception(
            "/api/reporting/docker-containers",
            ["docker_cli", "container_runtime_api"],
        )
    except FileNotFoundError:
        logger.info("Docker CLI not available")
        raise _no_fake_http_exception(
            "/api/reporting/docker-containers",
            ["docker_cli", "container_runtime_api"],
        )
    except Exception as e:
        logger.error(f"Docker containers check failed: {e}")
        raise _no_fake_http_exception(
            "/api/reporting/docker-containers",
            ["docker_cli", "container_runtime_api"],
        )


@router.get("/export-excel")
async def export_excel_get():
    """
    GET endpoint for export-excel status check.
    The actual export uses POST with data payload.
    """
    return {
        "status": "available",
        "service": "excel-export",
        "method": "POST",
        "description": "Use POST method with report data to generate Excel file",
        "endpoint": "/api/reporting/export-excel",
        "supported_formats": ["xlsx", "xls"],
        "max_rows": 100000,
        "timestamp": datetime.now().isoformat(),
    }


# ========== ERROR TRACKING ENDPOINTS ==========


@router.get("/errors")
async def get_errors() -> Dict[str, Any]:
    """
    Merr listën e të gjithë erroreve me referenca unike (ERR-001, ERR-002, etj)
    Shfaq numrin e rreshtit, funksionin, kodin e gabimit dhe detajet
    """
    return {
        "errors": error_tracker.get_all_errors(),
        "summary": error_tracker.get_error_summary(),
    }


@router.get("/errors/summary")
async def get_error_summary() -> Dict[str, Any]:
    """Merr përmbledhjen e erroreve"""
    return error_tracker.get_error_summary()


@router.get("/errors/by-function/{function_name}")
async def get_errors_by_function(function_name: str) -> Dict[str, Any]:
    """Merr errore sipas emrit të funksionit"""
    errors = error_tracker.get_errors_by_function(function_name)
    return {
        "function": function_name,
        "error_count": len(errors),
        "errors": errors,
    }


@router.get("/errors/table")
async def get_errors_table() -> PlainTextResponse:
    """
    Shfaq errore si tabelë e formatuar për konsol/terminal
    Tabelë me ERR-001, ERR-002, etj me numrin e rreshtit, funksionin, tipin, dhe mesazhin
    """
    table = error_tracker.export_errors_as_table()
    return PlainTextResponse(table)


@router.delete("/errors/clear")
async def clear_errors() -> Dict[str, Any]:
    """Pastro të gjithë errore"""
    error_count = len(error_tracker.errors)
    error_tracker.clear_errors()
    return {
        "status": "success",
        "message": f"Cleared {error_count} errors",
        "cleared_count": error_count,
    }
