#!/usr/bin/env python3
"""
CURIOSITY OCEAN API ROUTER
==========================
Unifikon të gjitha pipeline-t në një API të vetme.

Endpoints:
- POST /api/v1/chat       - Chat me reasoning
- POST /api/v1/strict     - Chat me strict mode
- POST /api/v1/admin      - Admin chat
- GET  /health            - Health check
- GET  /metrics           - System metrics
- POST /admin/command     - Execute admin command
"""

import logging
import os
import time
from typing import Any, Dict, Optional

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from system import get_system_pipeline

from core import (
    ReasoningMode,
    get_context_manager,
    get_reasoning_pipeline,
    get_safety_filter,
)

# ═══════════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════════
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(name)s - %(message)s")
logger = logging.getLogger("OceanRouter")

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
MODEL = os.getenv("MODEL", "llama3.1:8b")
PORT = int(os.getenv("PORT", "8035"))

# ═══════════════════════════════════════════════════════════════════
# FASTAPI APP
# ═══════════════════════════════════════════════════════════════════
app = FastAPI(
    title="Curiosity Ocean API",
    description="Unified API for all Ocean pipelines",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ═══════════════════════════════════════════════════════════════════
# REQUEST/RESPONSE MODELS
# ═══════════════════════════════════════════════════════════════════

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    mode: Optional[str] = "normal"  # normal, strict, admin, debug


class ChatResponse(BaseModel):
    response: str
    session_id: str
    mode: str
    processing_time: float
    engines_used: list


class AdminCommandRequest(BaseModel):
    command: str
    args: Dict[str, Any] = {}


# ═══════════════════════════════════════════════════════════════════
# PIPELINE INSTANCES
# ═══════════════════════════════════════════════════════════════════
reasoning_pipeline = None
context_manager = None
safety_filter = None
system_pipeline = None


@app.on_event("startup")
async def startup():
    """Initialize all pipelines"""
    global reasoning_pipeline, context_manager, safety_filter, system_pipeline
    
    reasoning_pipeline = get_reasoning_pipeline()
    context_manager = get_context_manager()
    safety_filter = get_safety_filter()
    system_pipeline = get_system_pipeline()
    
    logger.info("🌊 Curiosity Ocean API started")
    logger.info(f"   Model: {MODEL}")
    logger.info(f"   Ollama: {OLLAMA_HOST}")


# ═══════════════════════════════════════════════════════════════════
# CHAT ENDPOINTS
# ═══════════════════════════════════════════════════════════════════

@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, request: Request):
    """Chat endpoint me reasoning të plotë"""
    return await _process_chat(req, request, ReasoningMode.NORMAL)


@app.post("/api/v1/strict", response_model=ChatResponse)
async def strict_chat(req: ChatRequest, request: Request):
    """Chat me strict mode - ndjek rregullat pa devijim"""
    return await _process_chat(req, request, ReasoningMode.STRICT)


@app.post("/api/v1/admin", response_model=ChatResponse)
async def admin_chat(req: ChatRequest, request: Request):
    """Admin chat - privilegje të plota"""
    # Check admin header
    admin_key = request.headers.get("X-Admin-Key", "")
    if admin_key != os.getenv("ADMIN_KEY", "kloud-admin"):
        raise HTTPException(403, "Admin access required")
    
    return await _process_chat(req, request, ReasoningMode.ADMIN)


async def _process_chat(
    req: ChatRequest, 
    request: Request, 
    mode: ReasoningMode
) -> ChatResponse:
    """Process chat request through all pipelines"""
    start = time.time()
    engines = []
    
    # 1. Safety check
    safety_result = safety_filter.check_input(req.message)
    if safety_result.level.value == "blocked":
        return ChatResponse(
            response="Kjo kërkesë nuk mund të përpunohet.",
            session_id=req.session_id or "blocked",
            mode=mode.value,
            processing_time=time.time() - start,
            engines_used=["SafetyFilter:blocked"]
        )
    engines.append("SafetyFilter")
    
    # 2. Get or create session
    session_id = req.session_id or f"session_{int(time.time())}"
    ctx = context_manager.get_or_create(session_id)
    engines.append("ContextManager")
    
    # 3. Process through reasoning pipeline
    pipeline_result = reasoning_pipeline.process(
        session_id=session_id,
        message=req.message,
        mode=mode
    )
    engines.append(f"ReasoningPipeline:{mode.value}")
    
    # 4. Call Ollama
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                f"{OLLAMA_HOST}/api/chat",
                json={
                    "model": MODEL,
                    "messages": pipeline_result["messages"],
                    "stream": False,
                    "options": pipeline_result["options"]
                }
            )
            
            if resp.status_code != 200:
                raise HTTPException(resp.status_code, "Ollama error")
            
            response_text = resp.json().get("message", {}).get("content", "")
            engines.append(f"Ollama:{MODEL}")
    
    except httpx.TimeoutException:
        raise HTTPException(504, "Timeout - modeli po mendon shumë gjatë")
    except Exception as e:
        logger.error(f"Ollama error: {e}")
        raise HTTPException(500, str(e))
    
    # 5. Sanitize output
    is_safe, sanitized = safety_filter.validate_response(response_text)
    if not is_safe:
        response_text = sanitized
        engines.append("OutputSanitizer")
    
    # 6. Record in history
    context_manager.add_message(session_id, "user", req.message)
    context_manager.add_message(session_id, "assistant", response_text)
    reasoning_pipeline.record_response(session_id, req.message, response_text)
    
    return ChatResponse(
        response=response_text,
        session_id=session_id,
        mode=mode.value,
        processing_time=round(time.time() - start, 2),
        engines_used=engines
    )


# ═══════════════════════════════════════════════════════════════════
# SYSTEM ENDPOINTS
# ═══════════════════════════════════════════════════════════════════

@app.get("/health")
async def health():
    """Health check endpoint"""
    status = system_pipeline.health_check()
    return {
        "status": status.status,
        "uptime": status.uptime,
        "services": status.services
    }


@app.get("/metrics")
async def metrics():
    """System metrics endpoint"""
    return system_pipeline.get_metrics()


@app.get("/stats")
async def stats():
    """Pipeline statistics"""
    return {
        "reasoning": reasoning_pipeline.get_stats() if reasoning_pipeline else {},
        "context": context_manager.get_stats() if context_manager else {},
        "safety": safety_filter.get_stats() if safety_filter else {},
        "system": system_pipeline.get_metrics() if system_pipeline else {}
    }


@app.post("/admin/command")
async def admin_command(req: AdminCommandRequest, request: Request):
    """Execute admin command"""
    admin_key = request.headers.get("X-Admin-Key", "")
    if admin_key != os.getenv("ADMIN_KEY", "kloud-admin"):
        raise HTTPException(403, "Admin access required")
    
    user = request.headers.get("X-User", "unknown")
    result = system_pipeline.execute_admin_command(req.command, req.args, user)
    
    return {
        "command": result.command,
        "success": result.success,
        "result": result.result
    }


@app.get("/admin/log")
async def admin_log(request: Request, limit: int = 50):
    """Get admin command log"""
    admin_key = request.headers.get("X-Admin-Key", "")
    if admin_key != os.getenv("ADMIN_KEY", "kloud-admin"):
        raise HTTPException(403, "Admin access required")
    
    return system_pipeline.get_admin_log(limit)


# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)

