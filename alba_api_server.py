#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ALBA API Server - Live ingestion endpoint for Kloud Cloud.
Receives frames via HTTP POST and saves them into /data/alba.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from cors_policy import apply_standard_cors

# OpenTelemetry imports
from tracing import setup_tracing, instrument_fastapi_app, instrument_http_clients

# API Version
API_V1 = "/api/v1"

# Initialize tracing
tracer = setup_tracing("alba-api")

app = FastAPI(
    title="ALBA API Server",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Instrument FastAPI app for automatic tracing
instrument_fastapi_app(app, "alba-api")

# Instrument HTTP clients
instrument_http_clients()

apply_standard_cors(app)

DATA_DIR = Path(r"C:\Kloud-cloud\data\alba")
DATA_DIR.mkdir(parents=True, exist_ok=True)


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def save_frame(frame: dict[str, object]) -> Path:
    filename = f"frame_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    target = DATA_DIR / filename
    with target.open("w", encoding="utf-8") as handle:
        json.dump(frame, handle, ensure_ascii=False, indent=2)
    return target


@app.post("/alba/frame", response_model=None)
async def post_frame(request: Request) -> JSONResponse:
    with tracer.start_as_current_span("post_frame") as span:
        try:
            payload = await request.json()
            span.set_attribute("frame_received", True)
        except Exception as exc:  # pragma: no cover - input validation
            span.set_attribute("error", True)
            span.set_attribute("error.message", str(exc))
            return JSONResponse(
                {"status": "error", "message": f"Invalid JSON: {exc}"}, status_code=400
            )

        try:
            saved_path = save_frame(payload)
            span.set_attribute("saved_path", str(saved_path))
        except Exception as exc:  # pragma: no cover - filesystem safety
            span.set_attribute("error", True)
            span.set_attribute("error.message", str(exc))
            return JSONResponse(
                {"status": "error", "message": str(exc)}, status_code=500
            )

        return JSONResponse(
            {
                "status": "ok",
                "message": f"Frame saved at {saved_path}",
                "timestamp": _timestamp(),
            }
        )


@app.get("/alba/latest", response_model=None)
def get_latest() -> JSONResponse:
    with tracer.start_as_current_span("get_latest") as span:
        try:
            files = sorted(
                DATA_DIR.glob("frame_*.json"), key=os.path.getmtime, reverse=True
            )
            span.set_attribute("files_found", len(files))
        except Exception as exc:  # pragma: no cover - glob failure guard
            span.set_attribute("error", True)
            span.set_attribute("error.message", str(exc))
            return JSONResponse(
                {"status": "error", "message": str(exc)}, status_code=500
            )

        if not files:
            return JSONResponse({"status": "no-data", "message": "No frames found"})

        latest_file = files[0]
        try:
            with latest_file.open("r", encoding="utf-8-sig") as handle:
                frame = json.load(handle)
                span.set_attribute("file_name", latest_file.name)
        except Exception as exc:
            span.set_attribute("error", True)
            span.set_attribute("error.message", str(exc))
            return JSONResponse(
                {
                    "status": "error",
                    "message": f"Failed to read {latest_file.name}: {exc}",
                },
                status_code=500,
            )

        return JSONResponse({"status": "ok", "frame": frame, "file": latest_file.name})


@app.get("/")
def root() -> dict[str, object]:
    return {
        "status": "running",
        "service": "ALBA API Server",
        "endpoint": "/alba/frame",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "alba",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get(API_V1 + "/status")
def api_status():
    return {
        "status": "operational",
        "service": "alba",
        "api_version": "v1",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get(API_V1 + "/spec")
def api_spec():
    return app.openapi()


if __name__ == "__main__":
    port = int(os.getenv("ALBA_API_PORT", 9091))
    uvicorn.run("alba_api_server:app", host="127.0.0.1", port=port, reload=False)
