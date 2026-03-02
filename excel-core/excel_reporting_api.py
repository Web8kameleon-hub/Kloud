"""
CLISONIX EXCEL CORE API
========================
API ekskluzive për Excel Dashboard
Port: 8010
Plotësisht e izoluar - pa konflikt!
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from datetime import datetime
import subprocess
import psutil
from pathlib import Path

from lagter_v1_excel import LagterV1ExcelBuilder
from lagter_v1_models import LagterPayload

app = FastAPI(
    title="Clisonix Excel Core",
    description="API ekskluzive për Excel Dashboard - Isolated",
    version="1.0.0"
)

LAGTER_EXPORT_DIR = Path("excel-core/output")
LAGTER_SHEETS = [
    "Overview",
    "KPI",
    "LawCompliance",
    "EnigmaRegistry",
    "Sketches"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def run_docker_cmd(cmd):
    """Run docker command safely"""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=10
        )
        return result.stdout.strip()
    except:
        return ""

@app.get("/")
async def root():
    return {
        "service": "Clisonix Excel Core",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": [
            "/health",
            "/api/reporting/system-metrics",
            "/api/reporting/docker-containers",
            "/api/reporting/docker-stats",
            "/api/lagter/v1/meta",
            "/api/lagter/v1/template",
            "/api/lagter/v1/process-map",
            "/api/lagter/v1/export",
            "/api/lagter/v1/export/custom"
        ]
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "excel-core",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/reporting/system-metrics")
async def system_metrics():
    """Real system metrics"""
    return {
        "cpu_percent": psutil.cpu_percent(interval=0.1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage("/").percent,
        "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
        "disk_total_gb": round(psutil.disk_usage("/").total / (1024**3), 2),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/reporting/docker-containers")
async def docker_containers():
    """Get all Docker containers"""
    output = run_docker_cmd("docker ps -a --format '{{.Names}}|{{.Status}}|{{.Image}}|{{.CreatedAt}}|{{.Ports}}'")
    
    containers = []
    for line in output.split("\n"):
        if "|" in line:
            parts = line.split("|")
            if len(parts) >= 4:
                containers.append({
                    "name": parts[0],
                    "status": parts[1],
                    "image": parts[2],
                    "created": parts[3],
                    "ports": parts[4] if len(parts) > 4 else ""
                })
    
    return {
        "containers": containers,
        "total": len(containers),
        "running": len([c for c in containers if "Up" in c["status"]]),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/reporting/docker-stats")
async def docker_stats():
    """Get Docker container stats"""
    output = run_docker_cmd("docker stats --no-stream --format '{{.Name}}|{{.CPUPerc}}|{{.MemPerc}}|{{.MemUsage}}'")
    
    stats = []
    for line in output.split("\n"):
        if "|" in line:
            parts = line.split("|")
            if len(parts) >= 4:
                stats.append({
                    "name": parts[0],
                    "cpu_percent": parts[1],
                    "memory_percent": parts[2],
                    "memory_usage": parts[3]
                })
    
    return {
        "stats": stats,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/lagter/v1/meta")
async def lagter_v1_meta():
    builder = LagterV1ExcelBuilder()
    payload = builder.build_payload()
    uptime_seconds = int((datetime.utcnow() - datetime.fromisoformat(payload["generated_at"].replace("Z", "+00:00").replace("+00:00", ""))).total_seconds()) if payload.get("generated_at") else 0
    return {
        "module": "LAGTER v1",
        "version": payload["version"],
        "generated_at": payload["generated_at"],
        "data_mode": "real",
        "sheets": LAGTER_SHEETS,
        "counts": {
            "kpis": len(payload["kpis"]),
            "laws": len(payload["law_checks"]),
            "enigmas": len(payload["enigma_registry"]),
            "sketch_points": len(payload["sketch_points"])
        },
        "observability": {
            "export_dir": str(LAGTER_EXPORT_DIR),
            "generated_files": len(list(LAGTER_EXPORT_DIR.glob("lagter_v1_dashboard_*.xlsx"))) if LAGTER_EXPORT_DIR.exists() else 0,
            "uptime_seconds_estimate": max(uptime_seconds, 0)
        }
    }


@app.get("/api/lagter/v1/template")
async def lagter_v1_template():
    return {
        "mode": "template",
        "description": "Schema contract for custom payload. No demo values.",
        "required": [
            "generated_at",
            "version",
            "kpis",
            "law_checks",
            "enigma_registry",
            "sketch_points",
        ],
        "fields": {
            "generated_at": "ISO-8601 string",
            "version": "string",
            "kpis": [
                {
                    "name": "string",
                    "target": "number",
                    "actual": "number",
                }
            ],
            "law_checks": [
                {
                    "law": "string",
                    "description": "string",
                    "pass_rate": "number (0..1)",
                }
            ],
            "enigma_registry": [
                {
                    "enigma_id": "string",
                    "title": "string",
                    "status": "open|testing|decoded|archived",
                    "confidence": "number (0..1)",
                    "hypothesis": "string",
                }
            ],
            "sketch_points": [
                {
                    "day": "string",
                    "bio": "number (0..1)",
                    "behavior": "number (0..1)",
                    "ambient": "number (0..1)",
                    "tension": "number (0..1)",
                }
            ],
        },
        "example_post_target": "/api/lagter/v1/export/custom",
    }


@app.get("/api/lagter/v1/process-map")
async def lagter_v1_process_map():
    builder = LagterV1ExcelBuilder()
    return {
        "module": "LAGTER v1",
        "steps": builder.process_map(),
    }


@app.get("/api/lagter/v1/export")
async def lagter_v1_export():
    builder = LagterV1ExcelBuilder()
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    LAGTER_EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    file_path = LAGTER_EXPORT_DIR / f"lagter_v1_dashboard_{timestamp}.xlsx"
    builder.write_workbook(file_path)

    return FileResponse(
        path=str(file_path),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=file_path.name,
    )


@app.post("/api/lagter/v1/export/custom")
async def lagter_v1_export_custom(payload: LagterPayload):
    try:
        builder = LagterV1ExcelBuilder()
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        LAGTER_EXPORT_DIR.mkdir(parents=True, exist_ok=True)
        file_path = LAGTER_EXPORT_DIR / f"lagter_v1_dashboard_custom_{timestamp}.xlsx"
        builder.write_workbook(file_path, payload.model_dump())
        return FileResponse(
            path=str(file_path),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=file_path.name,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid payload for LAGTER export: {exc}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8010)
