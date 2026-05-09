# -*- coding: utf-8 -*-
"""

 OLLAMA MULTI-MODEL API - Enterprise Microservice


Port: 7777
Endpoint: /api/v1/generate, /api/v1/chat, /health, /models

3 Modele (UPDATED - phi3:mini dhe kloud-ocean:latest hequr):
  * kloud-ocean:v2 (4.9GB) - BALANCED - DEFAULT
  * llama3.1:8b (4.9GB) - BALANCED - BACKUP
  * gpt-oss:120b (65GB) - DEEP - via microservice 8031

Author: Kloud Team
Version: 2.1.0
"""

import asyncio
import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Import Multi-Model Engine
from ollama_multi_engine import (
    get_ollama_multi_engine,
    OllamaMultiEngine,
    Strategy,
    ModelTier,
    AVAILABLE_MODELS
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ollama_multi_api")

# 
# CONFIG
# 

API_PORT = int(os.environ.get("OLLAMA_MULTI_PORT", 4444))
API_VERSION = "2.0.1"
SERVICE_NAME = "ollama-multi-engine"


# 
# PYDANTIC MODELS
# 

class GenerateRequest(BaseModel):
    """Request pr generate"""
    prompt: str = Field(..., description="Pyetja/prompt")
    strategy: str = Field("auto", description="Strategy: auto, fast, balanced, deep")
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(2048, ge=1, le=8192)
    force_model: Optional[str] = Field(None, description="Force specific model")


class ChatMessage(BaseModel):
    """Mesazh chat"""
    role: str = Field(..., description="user, assistant, system")
    content: str


class ChatRequest(BaseModel):
    """Request pr chat"""
    messages: List[ChatMessage]
    strategy: str = Field("auto")
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(2048, ge=1, le=8192)


class GenerateResponse(BaseModel):
    """Response nga generate"""
    content: str
    model: str
    tier: str
    strategy: str
    duration_ms: float
    tokens_per_second: float


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    service: str
    version: str
    models_available: int
    models: List[str]
    ollama_connected: bool
    timestamp: str


class ModelInfo(BaseModel):
    """Info pr nj model"""
    name: str
    size_gb: float
    tier: str
    description: str
    available: bool


# 
# LIFESPAN
# 

engine: Optional[OllamaMultiEngine] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown"""
    global engine
    
    logger.info(" Starting Ollama Multi-Model API...")
    engine = get_ollama_multi_engine()
    await engine.initialize()
    logger.info(f"[OK] Initialized with {len(engine._available_models)} models")
    
    yield
    
    if engine:
        await engine.close()
    logger.info("[STOP] Ollama Multi-Model API stopped")


# 
# FASTAPI APP
# 

app = FastAPI(
    title="Ollama Multi-Model API",
    description="Enterprise API pr 5 Ollama models me auto-selection",
    version=API_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 
# ENDPOINTS
# 

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    
    Kthen statusin e shrbimit dhe modelet e disponueshme.
    """
    global engine
    
    if not engine:
        return HealthResponse(
            status="unhealthy",
            service=SERVICE_NAME,
            version=API_VERSION,
            models_available=0,
            models=[],
            ollama_connected=False,
            timestamp=datetime.utcnow().isoformat()
        )
    
    return HealthResponse(
        status="healthy",
        service=SERVICE_NAME,
        version=API_VERSION,
        models_available=len(engine._available_models),
        models=engine._available_models,
        ollama_connected=engine._initialized,
        timestamp=datetime.utcnow().isoformat()
    )


@app.get("/models", response_model=List[ModelInfo], tags=["Models"])
async def list_models():
    """
    Lista e t gjitha modeleve.
    
    Kthen info pr secilin model: emri, madhsia, tier, disponueshmria.
    """
    global engine
    
    if not engine:
        raise HTTPException(status_code=503, detail="Engine not initialized")
    
    models = []
    for name, model in AVAILABLE_MODELS.items():
        models.append(ModelInfo(
            name=name,
            size_gb=model.size_gb,
            tier=model.tier.value,
            description=model.description,
            available=name in engine._available_models
        ))
    
    return models


@app.post("/api/v1/generate", response_model=GenerateResponse, tags=["Generate"])
async def generate(request: GenerateRequest):
    """
    Gjenero prgjigje me auto-model selection.
    
    Strategies:
    - **auto**: Zgjedh modelin sipas kompleksitetit t pyetjes
    - **balanced**: Prdor kloud-ocean:v2 ose llama3.1:8b (4.9GB) - DEFAULT
    - **deep**: Prdor gpt-oss:120b (65GB) pr analiza komplekse (microservice 8031)
    
    HEQUR: fast strategy (phi3:mini, kloud-ocean:latest nuk flasin shqip)
    """
    global engine
    
    if not engine:
        raise HTTPException(status_code=503, detail="Engine not initialized")
    
    # Parse strategy
    strategy_map = {
        "auto": Strategy.AUTO,
        "fast": Strategy.FAST,
        "balanced": Strategy.BALANCED,
        "deep": Strategy.DEEP,
        "fallback": Strategy.FALLBACK,
    }
    strategy = strategy_map.get(request.strategy.lower(), Strategy.AUTO)
    
    response = await engine.generate(
        prompt=request.prompt,
        strategy=strategy,
        temperature=request.temperature,
        max_tokens=request.max_tokens,
        force_model=request.force_model
    )
    
    if response.content.startswith("[WARN]"):
        raise HTTPException(status_code=500, detail=response.content)
    
    return GenerateResponse(
        content=response.content,
        model=response.model_used,
        tier=response.tier.value,
        strategy=strategy.value,
        duration_ms=response.total_duration_ms,
        tokens_per_second=response.tokens_per_second
    )


@app.post("/api/v1/chat", response_model=GenerateResponse, tags=["Chat"])
async def chat(request: ChatRequest):
    """
    Chat me histori bisede.
    
    Drgo list mesazhesh (role: user/assistant/system).
    """
    global engine
    
    if not engine:
        raise HTTPException(status_code=503, detail="Engine not initialized")
    
    strategy_map = {
        "auto": Strategy.AUTO,
        "fast": Strategy.FAST,
        "balanced": Strategy.BALANCED,
        "deep": Strategy.DEEP,
    }
    strategy = strategy_map.get(request.strategy.lower(), Strategy.AUTO)
    
    messages = [{"role": m.role, "content": m.content} for m in request.messages]
    
    response = await engine.chat(
        messages=messages,
        strategy=strategy,
        temperature=request.temperature,
        max_tokens=request.max_tokens
    )
    
    return GenerateResponse(
        content=response.content,
        model=response.model_used,
        tier=response.tier.value,
        strategy=strategy.value,
        duration_ms=response.total_duration_ms,
        tokens_per_second=response.tokens_per_second
    )


@app.get("/stats", tags=["Stats"])
async def get_stats():
    """
    Statistika e prdorimit.
    
    Requests by model, tier, success rate.
    """
    global engine
    
    if not engine:
        raise HTTPException(status_code=503, detail="Engine not initialized")
    
    return engine.get_stats()


# 
# MAIN
# 

if __name__ == "__main__":
    import uvicorn
    
    print("" * 60)
    print(" OLLAMA MULTI-MODEL API")
    print("" * 60)
    print(f"   Port: {API_PORT}")
    print(f"   Version: {API_VERSION}")
    print(f"   Docs: http://localhost:{API_PORT}/docs")
    print(f"   Health: http://localhost:{API_PORT}/health")
    print("" * 60)
    
    uvicorn.run(
        "ollama_multi_api:app",
        host="0.0.0.0",
        port=API_PORT,
        reload=False,
        log_level="info"
    )

