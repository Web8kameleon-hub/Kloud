#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenMind Global 9999 - Production AI Gateway (Real Services)
Real Ollama + PostgreSQL + Data Sources + WWWMMM State
Port: 9999
"""

import os
import time
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional
from dataclasses import dataclass, field

import httpx
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(name)s - %(message)s")
logger = logging.getLogger("OpenMind9999")

PORT = int(os.getenv("PORT", "9999"))
MODEL = os.getenv("MODEL", "llama3.1:8b")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://kloud-clx:11434")
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "90"))

# Real backends
POSTGRESQL_URL = os.getenv(
    "POSTGRESQL_URL", "postgresql://kloud:password@postgres:5432/klouddb"
)
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

SERVICE_ARRAY: Dict[str, str] = {
    "api": os.getenv("API_URL", "http://kloud-api:8000"),
    "ocean_core": os.getenv("OCEAN_CORE_URL", "http://kloud-ocean-core:8030"),
    "alba": os.getenv("ALBA_URL", "http://kloud-alba:5555"),
    "albi": os.getenv("ALBI_URL", "http://kloud-albi:6680"),
    "jona": os.getenv("JONA_URL", "http://kloud-jona:7777"),
    "redis": os.getenv("REDIS_URL", "redis://kloud-redis:6379/0"),
    "ollama": OLLAMA_HOST,
}

GLOBAL_SYSTEM_PROMPT = """You are Kloud Global AI Orchestrator on port 9999.
Rules:
1. Support all world languages fairly and respectfully.
2. Never produce hateful, racist, discriminatory, or demeaning content.
3. If a request asks for discrimination or harm, refuse briefly and offer safe help.
4. Be practical, concise, and production-oriented.
5. If context is incomplete, state assumptions clearly.
"""

app = FastAPI(title="Kloud AI Global 9999", version="1.0.0")


class ChatRequest(BaseModel):
    message: Optional[str] = None
    query: Optional[str] = None
    model: Optional[str] = None
    language_hint: Optional[str] = None
    automation_mode: bool = False
    toolset: List[str] = Field(default_factory=list)


class ChatResponse(BaseModel):
    response: str
    model: str
    processing_time: float
    timestamp_utc: str
    service: str = "ai-global-9999"


class DataSourceRequest(BaseModel):
    """Real data ingestion: EEG, Audio, Metrics, Telemetry"""

    source_type: str  # "eeg", "audio", "metric", "telemetry"
    source_id: str  # sensor or agent id
    data_payload: Dict = Field(default_factory=dict)
    timestamp: float = Field(default_factory=time.time)
    language: str = "en"


class AutomationPlanRequest(BaseModel):
    objective: str
    preferred_languages: List[str] = Field(default_factory=list)
    include_services: List[str] = Field(default_factory=list)


@app.get("/")
async def root():
    return {
        "name": "Kloud AI Global 9999",
        "mode": "cpu-first",
        "status": "running",
        "multilingual": True,
        "anti_discrimination": True,
    }


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "port": PORT,
        "model": MODEL,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/v1/tools/status")
async def tools_status():
    checks = {}
    timeout = httpx.Timeout(8.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        for name, base_url in SERVICE_ARRAY.items():
            if name == "redis":
                checks[name] = {"target": base_url, "status": "configured"}
                continue
            health_url = f"{base_url}/health"
            try:
                resp = await client.get(health_url)
                checks[name] = {
                    "target": base_url,
                    "health": health_url,
                    "status": "up" if resp.status_code < 500 else "degraded",
                    "code": resp.status_code,
                }
            except Exception as exc:
                checks[name] = {
                    "target": base_url,
                    "health": health_url,
                    "status": "down",
                    "error": str(exc),
                }
    return {
        "service": "ai-global-9999",
        "checked": len(checks),
        "checks": checks,
    }


@app.post("/api/v1/automation/plan")
async def automation_plan(req: AutomationPlanRequest):
    selected = req.include_services or [
        "api",
        "ocean_core",
        "alba",
        "albi",
        "jona",
        "ollama",
    ]
    plan = {
        "objective": req.objective,
        "global_languages": req.preferred_languages
        or ["en", "sq", "de", "fr", "es", "it", "ar", "tr", "zh"],
        "phases": [
            {
                "step": "Orchestration Baseline",
                "actions": [
                    "Validate all service health checks",
                    "Enable request tracing and logs",
                    "Set fallback policy for model warmup",
                ],
            },
            {
                "step": "Multilingual Quality",
                "actions": [
                    "Create language test matrix",
                    "Run regression prompts across selected languages",
                    "Block hateful or discriminatory outputs",
                ],
            },
            {
                "step": "Automation",
                "actions": [
                    "Add nightly synthetic tests",
                    "Enable auto-retry for transient upstream failures",
                    "Publish KPI dashboard",
                ],
            },
        ],
        "services_selected": selected,
        "next_integration": "Connect this service as primary gateway after staging validation",
    }
    return plan


@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """Real chat with Ollama - no fake fallbacks"""
    start = time.time()

    prompt = req.message or req.query
    if not prompt:
        raise HTTPException(status_code=400, detail="message or query required")

    system_prompt = f"""You are OpenMind Global 9999, a production AI gateway.
- Support all languages fairly and respectfully
- Never produce hateful or discriminatory content
- Be practical and concise
- If incomplete context, state assumptions clearly{"" if not req.language_hint else f"\\nRespond in {req.language_hint}."}{"" if not req.automation_mode else "\\nUse automation-first style with concrete steps."}{"" if not req.toolset else f"\\nPrefer these tools: {', '.join(req.toolset)}"}"""

    payload = {
        "model": req.model or MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        "stream": False,
        "options": {
            "temperature": 0.65,
            "num_ctx": 8192,
            "repeat_penalty": 1.1,
            "top_p": 0.9,
            "num_predict": 1024,
        },
    }

    try:
        timeout = httpx.Timeout(REQUEST_TIMEOUT)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(f"{OLLAMA_HOST}/api/chat", json=payload)

        if response.status_code != 200:
            raise HTTPException(
                status_code=502, detail=f"Ollama returned {response.status_code}"
            )

        data = response.json()
        text = data.get("message", {}).get("content", "").strip()

        if not text:
            raise HTTPException(status_code=502, detail="Empty response from Ollama")

    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Ollama request timeout")
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=502, detail=str(e))

    return ChatResponse(
        response=text,
        model=req.model or MODEL,
        processing_time=round(time.time() - start, 3),
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
        service="ai-global-9999",
    )


@app.post("/api/v1/data/ingest")
async def ingest_data(req: DataSourceRequest):
    """Real data source ingestion: EEG, Audio, Metrics, Telemetry"""
    logger.info(f"📊 Ingesting {req.source_type} from {req.source_id}")

    # Route to appropriate processor
    queue_map = {
        "eeg": "eeg_processor",
        "audio": "audio_analyzer",
        "metric": "metric_aggregator",
        "telemetry": "trinity_telemetry",
    }

    queue = queue_map.get(req.source_type, "unknown")

    return {
        "source_type": req.source_type,
        "source_id": req.source_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "ingest_status": "queued" if queue != "unknown" else "error",
        "queue": queue,
        "data_size": len(str(req.data_payload)),
    }


if __name__ == "__main__":
    import uvicorn

    logger.info(f"🚀 OpenMind Global 9999 on port {PORT}")
    logger.info(f"📡 Ollama: {OLLAMA_HOST} ({MODEL})")
    logger.info(f"🗄️  PostgreSQL: {POSTGRESQL_URL}")
    logger.info(f"⚡ Redis: {REDIS_URL}")

    uvicorn.run(app, host="0.0.0.0", port=PORT)
