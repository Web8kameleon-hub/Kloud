import os
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

PORT = int(os.getenv("PORT", "9999"))
MODEL = os.getenv("MODEL", "llama3.1:8b")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://clisonix-ollama:11434")
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "90"))

SERVICE_ARRAY: Dict[str, str] = {
    "api": os.getenv("API_URL", "http://clisonix-api:8000"),
    "ocean_core": os.getenv("OCEAN_CORE_URL", "http://clisonix-ocean-core:8030"),
    "alba": os.getenv("ALBA_URL", "http://clisonix-alba:5555"),
    "albi": os.getenv("ALBI_URL", "http://clisonix-albi:6680"),
    "jona": os.getenv("JONA_URL", "http://clisonix-jona:7777"),
    "redis": os.getenv("REDIS_URL", "redis://clisonix-redis:6379/0"),
    "ollama": OLLAMA_HOST,
}

GLOBAL_SYSTEM_PROMPT = """You are Clisonix Global AI Orchestrator on port 9999.
Rules:
1. Support all world languages fairly and respectfully.
2. Never produce hateful, racist, discriminatory, or demeaning content.
3. If a request asks for discrimination or harm, refuse briefly and offer safe help.
4. Be practical, concise, and production-oriented.
5. If context is incomplete, state assumptions clearly.
"""

app = FastAPI(title="Clisonix AI Global 9999", version="1.0.0")


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


class AutomationPlanRequest(BaseModel):
    objective: str
    preferred_languages: List[str] = Field(default_factory=list)
    include_services: List[str] = Field(default_factory=list)


@app.get("/")
async def root():
    return {
        "name": "Clisonix AI Global 9999",
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
        "global_languages": req.preferred_languages or ["en", "sq", "de", "fr", "es", "it", "ar", "tr", "zh"],
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
    start = time.time()
    prompt = req.message or req.query
    if not prompt:
        raise HTTPException(status_code=400, detail="message or query required")

    language_instruction = ""
    if req.language_hint:
        language_instruction = f"\nRespond in {req.language_hint}."

    automation_instruction = ""
    if req.automation_mode:
        automation_instruction = "\nUse an automation-first style with concrete steps and service-aware recommendations."

    tools_instruction = ""
    if req.toolset:
        tools_instruction = f"\nPrefer these tools/services when relevant: {', '.join(req.toolset)}."

    system_prompt = (
        GLOBAL_SYSTEM_PROMPT
        + language_instruction
        + automation_instruction
        + tools_instruction
    )

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
            text = (
                "Service is warming up. Please retry in a few seconds. "
                "Global multilingual mode is active."
            )
        else:
            text = response.json().get("message", {}).get("content", "").strip()
            if not text:
                text = (
                    "Model returned an empty response. Please retry. "
                    "Global multilingual mode remains active."
                )
    except Exception:
        text = (
            "Upstream model is temporarily unavailable. "
            "Please retry shortly. Gateway and automation endpoints stay online."
        )

    return ChatResponse(
        response=text,
        model=req.model or MODEL,
        processing_time=round(time.time() - start, 2),
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=PORT)
