from __future__ import annotations

from datetime import datetime
from pathlib import Path
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from lagter_v1_excel import LagterV1ExcelBuilder

app = FastAPI(
    title="Clisonix LAGTER v1 API",
    description="Dedicated LAGTER v1 service for industrial Excel export",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

LAGTER_EXPORT_DIR = Path("excel-core/output")


@app.get("/")
async def root():
    return {
        "service": "LAGTER v1",
        "status": "operational",
        "port": int(os.environ.get("PORT", "4010")),
        "endpoints": [
            "/health",
            "/api/lagter/v1/meta",
            "/api/lagter/v1/template",
            "/api/lagter/v1/process-map",
            "/api/lagter/v1/export",
        ],
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "lagter-v1",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/api/lagter/v1/meta")
async def lagter_v1_meta():
    builder = LagterV1ExcelBuilder()
    payload = builder.build_payload()
    return {
        "module": "LAGTER v1",
        "version": payload["version"],
        "generated_at": payload["generated_at"],
        "data_mode": "real",
        "sheets": [
            "Overview",
            "KPI",
            "LawCompliance",
            "EnigmaRegistry",
            "Sketches",
        ],
        "counts": {
            "kpis": len(payload["kpis"]),
            "laws": len(payload["law_checks"]),
            "enigmas": len(payload["enigma_registry"]),
            "sketch_points": len(payload["sketch_points"]),
        },
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
    if not hasattr(builder, "process_map"):
        return {
            "module": "LAGTER v1",
            "steps": [
                "Signal",
                "Counter-Signal",
                "Tension",
                "Balance",
                "Enigma",
                "Audited Decision",
            ],
        }
    return {
        "module": "LAGTER v1",
        "steps": builder.process_map(),
    }


@app.get("/api/lagter/v1/export")
async def lagter_v1_export():
    try:
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
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"LAGTER export failed: {exc}")


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", "4010"))
    uvicorn.run(app, host="0.0.0.0", port=port)
