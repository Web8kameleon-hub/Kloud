"""
CLX SOVEREIGN API - Sovereign AI Router (40400)
================================================

Independent sovereign inference router for the Kloud fabric.
Routing chain (no-fake, real backends only):
    1. CLX  (ollama runtime, text)      -> OLLAMA_HOST
    2. CLX.I (multi-model router)        -> CLXI_HOST
    3. Structured error (never a fake numeric/canned answer)

Author: Ledjan Ahmati / WEB8euroweb GmbH
System: Kloud Cloud - Sovereign Runtime
"""
from __future__ import annotations

import os
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import httpx
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

PORT = int(os.getenv("PORT", "40400"))
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://kloud-clx:11434")
CLXI_HOST = os.getenv("CLXI_HOST", "http://kloud-clx-i:4444")
MODEL = os.getenv("MODEL", "llama3.1:8b")
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "120"))

app = FastAPI(
    title="CLX Sovereign Router",
    description="Sovereign AI inference router (CLX -> CLX.I -> structured error)",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

_stats: Dict[str, Any] = {"requests": 0, "clx_hits": 0, "clxi_hits": 0, "errors": 0}
_START = time.time()


class ChatRequest(BaseModel):
    message: Optional[str] = None
    query: Optional[str] = None
    model: Optional[str] = None
    system: Optional[str] = None
    language_hint: Optional[str] = None
    temperature: float = 0.7


class ChatResponse(BaseModel):
    response: str
    backend: str
    model: str
    processing_time: float


async def _try_clx(prompt: str, model: str, system: Optional[str], temperature: float) -> Optional[str]:
    """Primary backend: CLX (ollama /api/chat)."""
    messages: List[Dict[str, str]] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {"temperature": temperature, "num_ctx": 4096},
    }
    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            r = await client.post(f"{OLLAMA_HOST}/api/chat", json=payload)
            if r.status_code == 200:
                data = r.json()
                content = (data.get("message") or {}).get("content", "").strip()
                return content or None
    except Exception:
        return None
    return None


async def _try_clxi(prompt: str, model: str) -> Optional[str]:
    """Secondary backend: CLX.I multi-model router (/api/v1/chat)."""
    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            r = await client.post(
                f"{CLXI_HOST}/api/v1/chat",
                json={"message": prompt, "model": model},
            )
            if r.status_code == 200:
                data = r.json()
                content = (
                    data.get("response") or data.get("text") or data.get("output") or ""
                ).strip()
                return content or None
    except Exception:
        return None
    return None


@app.get("/health")
async def health() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "service": "clx-sovereign",
        "backends": {"clx": OLLAMA_HOST, "clx_i": CLXI_HOST},
        "model": MODEL,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/v1/models")
async def models() -> Dict[str, Any]:
    """List real models available on the CLX (ollama) backend."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(f"{OLLAMA_HOST}/api/tags")
            if r.status_code == 200:
                tags = r.json().get("models", [])
                return {"available": [m.get("name") for m in tags], "count": len(tags)}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"CLX backend unreachable: {e}")
    return {"available": [], "count": 0}


@app.get("/api/v1/sovereign/status")
async def sovereign_status() -> Dict[str, Any]:
    return {
        "sovereign": True,
        "external_paid_apis": False,
        "uptime_seconds": round(time.time() - _START, 2),
        "stats": _stats,
        "routing_chain": ["CLX", "CLX.I", "structured_error"],
    }


@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    prompt = (req.message or req.query or "").strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="message or query required")
    if req.language_hint:
        prompt_system = (req.system or "") + f"\nRespond in {req.language_hint}."
    else:
        prompt_system = req.system
    model = req.model or MODEL
    start = time.time()
    _stats["requests"] += 1

    answer = await _try_clx(prompt, model, prompt_system, req.temperature)
    if answer:
        _stats["clx_hits"] += 1
        return ChatResponse(
            response=answer, backend="CLX", model=model, processing_time=round(time.time() - start, 3)
        )

    answer = await _try_clxi(prompt, model)
    if answer:
        _stats["clxi_hits"] += 1
        return ChatResponse(
            response=answer, backend="CLX.I", model=model, processing_time=round(time.time() - start, 3)
        )

    _stats["errors"] += 1
    raise HTTPException(
        status_code=503,
        detail="No sovereign backend produced a response (CLX and CLX.I both unavailable).",
    )


if __name__ == "__main__":
    print(f"🛡️ CLX Sovereign Router starting on {PORT} | CLX={OLLAMA_HOST} CLX.I={CLXI_HOST}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
