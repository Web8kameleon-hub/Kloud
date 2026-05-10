#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCEAN ORCHESTRATOR v1.0 - Dynamic Multi-Service Router
=======================================================
Lightweight orchestration layer that:
1. Routes requests to 56+ microservices dynamically
2. No hardcoded logic - configuration-driven
3. Health monitoring & service discovery
4. Intent-based routing
5. Fallback chains

Port: 8030
"""

import asyncio
import logging
import os
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel

# ═══════════════════════════════════════════════════════════════════
# LOGGING & CONFIG
# ═══════════════════════════════════════════════════════════════════
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(name)s - %(message)s")
logger = logging.getLogger("OceanOrchestrator")

PORT = int(os.getenv("PORT", "8030"))
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://kloud-clx:11434")
DEFAULT_MODEL = os.getenv("MODEL", "llama3.1:8b")


# ═══════════════════════════════════════════════════════════════════
# SERVICE REGISTRY - Dynamic Configuration
# ═══════════════════════════════════════════════════════════════════
@dataclass
class ServiceConfig:
    """Service configuration with routing info"""

    name: str
    host: str
    port: int
    endpoints: Dict[str, str] = field(default_factory=dict)
    health_path: str = "/health"
    priority: int = 1
    timeout: float = 30.0
    is_healthy: bool = False
    last_check: float = 0
    capabilities: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)


# ═══════════════════════════════════════════════════════════════════
# SERVICES CONFIGURATION - Add new services here only
# ═══════════════════════════════════════════════════════════════════
SERVICES: Dict[str, ServiceConfig] = {
    # Core AI
    "ollama": ServiceConfig(
        name="Ollama LLM",
        host=OLLAMA_HOST.replace("http://", "").split(":")[0],
        port=11434,
        endpoints={
            "chat": "/api/chat",
            "generate": "/api/generate",
            "models": "/api/tags",
        },
        health_path="/api/tags",
        priority=1,
        timeout=120.0,  # ✅ 120s, NOT 300s
        capabilities=["chat", "generate", "reasoning"],
        keywords=["chat", "ask", "explain", "help", "write"],
    ),
    # ASI Trinity
    "alba": ServiceConfig(
        name="ALBA - Analytical Intelligence",
        host="kloud-alba",
        port=5555,
        endpoints={
            "analyze": "/api/v1/analyze",
            "signals": "/api/v1/signals",
            "patterns": "/api/v1/patterns",
        },
        capabilities=["eeg", "analysis", "signals", "patterns"],
        keywords=["eeg", "brain", "signal", "analyze", "pattern", "neural"],
    ),
    "albi": ServiceConfig(
        name="ALBI - Creative Intelligence",
        host="kloud-albi",
        port=6680,
        endpoints={
            "create": "/api/v1/create",
            "learn": "/api/v1/learn",
            "adapt": "/api/v1/adapt",
        },
        capabilities=["creativity", "learning", "adaptation"],
        keywords=["create", "learn", "creative", "generate", "adapt"],
    ),
    "jona": ServiceConfig(
        name="JONA - Emotional Intelligence",
        host="kloud-jona",
        port=6681,
        endpoints={
            "emotion": "/api/v1/emotion",
            "sentiment": "/api/v1/sentiment",
        },
        capabilities=["emotion", "sentiment", "empathy"],
        keywords=["emotion", "feel", "sentiment", "mood", "empathy"],
    ),
    "asi": ServiceConfig(
        name="ASI - Superintelligence Core",
        host="kloud-asi",
        port=8020,
        endpoints={
            "think": "/api/v1/think",
            "reason": "/api/v1/reason",
        },
        capabilities=["reasoning", "superintelligence", "complex_tasks"],
        keywords=["reason", "think", "complex", "solve", "superintelligent"],
    ),
    # Translation
    "translation": ServiceConfig(
        name="Translation Node",
        host="kloud-translation",
        port=8036,
        endpoints={
            "translate": "/api/v1/translate",
            "detect": "/api/v1/detect",
        },
        capabilities=["translation", "language_detection"],
        keywords=["translate", "language", "përkthe", "gjuhë"],
    ),
    # Backend API
    "api": ServiceConfig(
        name="Main API",
        host="kloud-api",
        port=8000,
        endpoints={
            "fitness": "/fitness",
            "weather": "/weather",
            "crypto": "/crypto",
            "users": "/users",
        },
        capabilities=["fitness", "weather", "crypto", "users"],
        keywords=["fitness", "workout", "weather", "crypto", "bitcoin", "user"],
    ),
    # Aviation Weather
    "aviation": ServiceConfig(
        name="Aviation Weather",
        host="kloud-aviation",
        port=8040,
        endpoints={
            "metar": "/api/v1/metar",
            "taf": "/api/v1/taf",
            "notam": "/api/v1/notam",
        },
        capabilities=["metar", "taf", "aviation_weather"],
        keywords=["metar", "taf", "aviation", "flight", "airport", "notam"],
    ),
    # Reporting
    "reporting": ServiceConfig(
        name="Reporting Service",
        host="kloud-reporting",
        port=8010,
        endpoints={
            "generate": "/api/v1/report",
            "export": "/api/v1/export",
        },
        capabilities=["reports", "pdf", "export"],
        keywords=["report", "pdf", "export", "raport"],
    ),
    # Excel Service
    "excel": ServiceConfig(
        name="Excel Service",
        host="kloud-excel",
        port=8011,
        endpoints={
            "process": "/api/v1/process",
            "analyze": "/api/v1/analyze",
        },
        capabilities=["excel", "spreadsheet", "data"],
        keywords=["excel", "spreadsheet", "csv", "data", "tabela"],
    ),
    # Behavioral Science
    "behavioral": ServiceConfig(
        name="Behavioral Science",
        host="kloud-behavioral",
        port=8012,
        endpoints={
            "analyze": "/api/v1/analyze",
            "predict": "/api/v1/predict",
        },
        capabilities=["behavior", "psychology", "prediction"],
        keywords=["behavior", "psychology", "predict", "human", "sjellje"],
    ),
    # Economy
    "economy": ServiceConfig(
        name="Economy Service",
        host="kloud-economy",
        port=8013,
        endpoints={
            "market": "/api/v1/market",
            "forecast": "/api/v1/forecast",
        },
        capabilities=["economy", "market", "forecast"],
        keywords=["economy", "market", "stock", "finance", "ekonomi"],
    ),
}


# ═══════════════════════════════════════════════════════════════════
# INTENT ROUTER - Match query to service
# ═══════════════════════════════════════════════════════════════════
class IntentRouter:
    """Routes queries to appropriate services based on intent"""

    def __init__(self, services: Dict[str, ServiceConfig]):
        self.services = services
        self._build_keyword_index()

    def _build_keyword_index(self):
        """Build keyword -> service mapping"""
        self.keyword_map: Dict[str, List[str]] = {}
        for svc_id, svc in self.services.items():
            for kw in svc.keywords:
                if kw not in self.keyword_map:
                    self.keyword_map[kw] = []
                self.keyword_map[kw].append(svc_id)

    def route(self, query: str) -> List[str]:
        """Return list of service IDs that match the query"""
        query_lower = query.lower()
        matches: Dict[str, int] = {}

        for keyword, services in self.keyword_map.items():
            if keyword in query_lower:
                for svc_id in services:
                    matches[svc_id] = matches.get(svc_id, 0) + 1

        # Sort by match count, then by priority
        sorted_matches = sorted(matches.keys(), key=lambda x: (matches[x], self.services[x].priority), reverse=True)

        # Default to ollama if no specific match
        if not sorted_matches:
            return ["ollama"]

        return sorted_matches


# ═══════════════════════════════════════════════════════════════════
# HEALTH CHECKER - Background service monitoring
# ═══════════════════════════════════════════════════════════════════
class HealthChecker:
    """Monitors health of all registered services"""

    def __init__(self, services: Dict[str, ServiceConfig]):
        self.services = services
        self.check_interval = 30  # seconds

    async def check_service(self, svc_id: str, svc: ServiceConfig) -> bool:
        """Check if a single service is healthy"""
        url = f"http://{svc.host}:{svc.port}{svc.health_path}"
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(url)
                is_healthy = resp.status_code == 200
                svc.is_healthy = is_healthy
                svc.last_check = time.time()
                return is_healthy
        except Exception:
            svc.is_healthy = False
            svc.last_check = time.time()
            return False

    async def check_all(self) -> Dict[str, bool]:
        """Check all services concurrently"""
        tasks = [self.check_service(svc_id, svc) for svc_id, svc in self.services.items()]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return {svc_id: result if isinstance(result, bool) else False for svc_id, result in zip(self.services.keys(), results)}

    async def run_background_checks(self, max_iterations: int = 1000):
        """Run health checks in background - LIMITED iterations, not infinite"""
        iteration = 0
        while iteration < max_iterations:
            iteration += 1
            try:
                await self.check_all()
                logger.debug(f"Health check iteration {iteration}/{max_iterations}")
            except Exception as e:
                logger.error(f"Health check error: {e}")
            await asyncio.sleep(self.check_interval)
        logger.info("Health checker completed max iterations, stopping")


# ═══════════════════════════════════════════════════════════════════
# SERVICE CALLER - Execute requests to services
# ═══════════════════════════════════════════════════════════════════
class ServiceCaller:
    """Calls services with fallback support"""

    def __init__(self, services: Dict[str, ServiceConfig]):
        self.services = services

    async def call(self, svc_id: str, endpoint: str, method: str = "POST", data: Optional[Dict] = None, stream: bool = False):
        """Call a service endpoint"""
        svc = self.services.get(svc_id)
        if not svc:
            raise HTTPException(404, f"Service {svc_id} not found")

        # Build URL
        endpoint_path = svc.endpoints.get(endpoint, endpoint)
        url = f"http://{svc.host}:{svc.port}{endpoint_path}"

        timeout = httpx.Timeout(svc.timeout, connect=10.0)

        if stream:
            return self._stream_call(url, method, data, timeout)
        else:
            return await self._simple_call(url, method, data, timeout)

    async def _simple_call(self, url: str, method: str, data: Optional[Dict], timeout: httpx.Timeout):
        """Non-streaming call"""
        async with httpx.AsyncClient(timeout=timeout) as client:
            if method == "GET":
                resp = await client.get(url, params=data)
            else:
                resp = await client.post(url, json=data)

            if resp.status_code != 200:
                raise HTTPException(resp.status_code, resp.text)

            return resp.json()

    async def _stream_call(self, url: str, method: str, data: Optional[Dict], timeout: httpx.Timeout):
        """Streaming call - returns async generator"""

        async def stream_generator():
            async with httpx.AsyncClient(timeout=timeout) as client:
                async with client.stream(method, url, json=data) as response:
                    async for line in response.aiter_lines():
                        if line:
                            yield line + "\n"

        return StreamingResponse(stream_generator(), media_type="text/event-stream")


# ═══════════════════════════════════════════════════════════════════
# FASTAPI APP
# ═══════════════════════════════════════════════════════════════════
app = FastAPI(title="Ocean Orchestrator", version="1.0.0", description="Dynamic Multi-Service Router for Kloud Cloud")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# Initialize components
intent_router = IntentRouter(SERVICES)
health_checker = HealthChecker(SERVICES)
service_caller = ServiceCaller(SERVICES)


# ═══════════════════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════════════════
class ChatRequest(BaseModel):
    message: Optional[str] = None
    query: Optional[str] = None
    model: Optional[str] = None
    stream: bool = False
    target_service: Optional[str] = None  # Override routing


class ChatResponse(BaseModel):
    response: str
    service: str
    model: Optional[str] = None
    latency_ms: int = 0


# ═══════════════════════════════════════════════════════════════════
# STARTUP EVENT
# ═══════════════════════════════════════════════════════════════════
@app.on_event("startup")
async def startup():
    """Startup with LIMITED background health checks"""
    logger.info(f"🌊 Ocean Orchestrator starting on port {PORT}")
    logger.info(f"📡 Registered {len(SERVICES)} services")
    logger.info(f"🔗 Ollama: {OLLAMA_HOST}")
    logger.info(f"🤖 Default model: {DEFAULT_MODEL}")

    # Initial health check
    try:
        health_status = await health_checker.check_all()
        healthy_count = sum(1 for v in health_status.values() if v)
        logger.info(f"✅ {healthy_count}/{len(SERVICES)} services healthy")
    except Exception as e:
        logger.warning(f"⚠️ Initial health check failed: {e}")

    # Start LIMITED background health monitoring (max 1000 iterations = ~8 hours)
    # ✅ NOT infinite - will stop after max_iterations
    asyncio.create_task(health_checker.run_background_checks(max_iterations=1000))


# ═══════════════════════════════════════════════════════════════════
# MAIN CHAT ENDPOINT - Intelligent Routing
# ═══════════════════════════════════════════════════════════════════
@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """
    Main chat endpoint with intelligent service routing.
    Routes to appropriate service based on query intent.
    """
    start = time.time()
    prompt = req.message or req.query

    if not prompt:
        raise HTTPException(400, "message or query required")

    # Route to specific service if requested
    if req.target_service:
        service_ids = [req.target_service]
    else:
        # Intelligent routing based on intent
        service_ids = intent_router.route(prompt)

    logger.info(f"🎯 Routing to: {service_ids[0]} (matched: {service_ids})")

    # Try primary service, fallback to ollama
    for svc_id in service_ids:
        svc = SERVICES.get(svc_id)
        if not svc:
            continue

        try:
            if svc_id == "ollama":
                # Direct Ollama call
                response = await _call_ollama(prompt, req.model or DEFAULT_MODEL)
            else:
                # Call other service
                endpoint = list(svc.endpoints.keys())[0] if svc.endpoints else "/"
                response = await service_caller.call(svc_id, endpoint, "POST", {"query": prompt})
                if isinstance(response, dict):
                    response = response.get("response", str(response))

            latency = int((time.time() - start) * 1000)
            return ChatResponse(
                response=response, service=svc_id, model=req.model or DEFAULT_MODEL if svc_id == "ollama" else None, latency_ms=latency
            )
        except Exception as e:
            logger.warning(f"⚠️ Service {svc_id} failed: {e}")
            continue

    # Final fallback
    raise HTTPException(503, "No available services")


async def _call_ollama(prompt: str, model: str) -> str:
    """Direct Ollama call with strict timeouts"""
    # STRICT: 120s timeout, NOT 300s
    timeout = httpx.Timeout(120.0, connect=10.0)

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            logger.info(f"🤖 Ollama request: model={model}, prompt_len={len(prompt)}")
            start = time.time()

            resp = await client.post(
                f"{OLLAMA_HOST}/api/chat",
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": False,
                    "keep_alive": "5m",  # ✅ 5 minutes, NOT -1 (infinite)
                    "options": {
                        "num_predict": 4096,  # ✅ Reasonable limit, NOT 50000
                        "num_ctx": 4096,
                        "temperature": 0.7,
                    },
                },
            )

            latency = time.time() - start
            logger.info(f"✅ Ollama response in {latency:.2f}s")

            data = resp.json()
            return data.get("message", {}).get("content", "")
    except httpx.TimeoutException:
        logger.error(f"❌ Ollama timeout after 120s")
        raise HTTPException(504, "Ollama request timed out")
    except Exception as e:
        logger.error(f"❌ Ollama error: {e}")
        raise HTTPException(502, f"Ollama error: {str(e)}")


# ═══════════════════════════════════════════════════════════════════
# STREAMING CHAT
# ═══════════════════════════════════════════════════════════════════
@app.post("/api/v1/chat/stream")
async def chat_stream(req: ChatRequest):
    """Streaming chat endpoint"""
    prompt = req.message or req.query
    if not prompt:
        raise HTTPException(400, "message required")

    model = req.model or DEFAULT_MODEL

    logger.info(f"🌊 Stream request: model={model}, prompt_len={len(prompt)}")

    async def stream_ollama():
        # STRICT: 180s timeout for streaming (longer than non-streaming)
        timeout = httpx.Timeout(180.0, connect=10.0)
        start = time.time()
        token_count = 0

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                async with client.stream(
                    "POST",
                    f"{OLLAMA_HOST}/api/chat",
                    json={
                        "model": model,
                        "messages": [{"role": "user", "content": prompt}],
                        "stream": True,
                        "keep_alive": "5m",  # ✅ 5 minutes, NOT -1
                        "options": {
                            "num_predict": 4096,  # ✅ Reasonable limit
                            "num_ctx": 4096,
                        },
                    },
                ) as response:
                    import json as json_lib

                    async for line in response.aiter_lines():
                        if line:
                            try:
                                data = json_lib.loads(line)
                                if "message" in data and "content" in data["message"]:
                                    token_count += 1
                                    yield data["message"]["content"]
                                if data.get("done", False):
                                    break
                            except json_lib.JSONDecodeError:
                                pass

            latency = time.time() - start
            logger.info(f"✅ Stream completed: {token_count} tokens in {latency:.2f}s")
        except httpx.TimeoutException:
            logger.error("❌ Stream timeout after 180s")
            yield "\n[Error: Request timed out]"
        except Exception as e:
            logger.error(f"❌ Stream error: {e}")
            yield f"\n[Error: {str(e)}]"

    return StreamingResponse(stream_ollama(), media_type="text/plain")


# ═══════════════════════════════════════════════════════════════════
# SERVICE MANAGEMENT ENDPOINTS
# ═══════════════════════════════════════════════════════════════════
@app.get("/api/v1/services")
async def list_services():
    """List all registered services with health status"""
    return {
        "services": {
            svc_id: {
                "name": svc.name,
                "host": svc.host,
                "port": svc.port,
                "healthy": svc.is_healthy,
                "capabilities": svc.capabilities,
                "endpoints": list(svc.endpoints.keys()),
            }
            for svc_id, svc in SERVICES.items()
        },
        "total": len(SERVICES),
        "healthy": sum(1 for s in SERVICES.values() if s.is_healthy),
    }


@app.get("/api/v1/services/{service_id}")
async def get_service(service_id: str):
    """Get details for a specific service"""
    svc = SERVICES.get(service_id)
    if not svc:
        raise HTTPException(404, f"Service {service_id} not found")

    return {
        "id": service_id,
        "name": svc.name,
        "host": svc.host,
        "port": svc.port,
        "endpoints": svc.endpoints,
        "capabilities": svc.capabilities,
        "keywords": svc.keywords,
        "healthy": svc.is_healthy,
        "last_check": svc.last_check,
    }


@app.post("/api/v1/services/{service_id}/call")
async def call_service(service_id: str, request: Request):
    """Direct call to a specific service"""
    body = await request.json()
    endpoint = body.pop("endpoint", None)

    if not endpoint:
        raise HTTPException(400, "endpoint required in body")

    result = await service_caller.call(service_id, endpoint, "POST", body)
    return result


@app.get("/api/v1/health")
async def health():
    """Health check endpoint"""
    healthy_services = sum(1 for s in SERVICES.values() if s.is_healthy)
    return {
        "status": "healthy" if healthy_services > 0 else "degraded",
        "services_total": len(SERVICES),
        "services_healthy": healthy_services,
    }


@app.get("/health")
async def health_simple():
    """Simple health check"""
    return {"status": "ok"}


@app.get("/")
async def root():
    """Root endpoint"""
    return {"service": "Ocean Orchestrator", "version": "1.0.0", "services_registered": len(SERVICES), "docs": "/docs"}


# ═══════════════════════════════════════════════════════════════════
# PROXY ENDPOINTS - Route to specific services
# ═══════════════════════════════════════════════════════════════════
@app.api_route("/api/alba/{path:path}", methods=["GET", "POST"])
async def proxy_alba(path: str, request: Request):
    """Proxy to ALBA service"""
    return await _proxy_to_service("alba", path, request)


@app.api_route("/api/albi/{path:path}", methods=["GET", "POST"])
async def proxy_albi(path: str, request: Request):
    """Proxy to ALBI service"""
    return await _proxy_to_service("albi", path, request)


@app.api_route("/api/asi/{path:path}", methods=["GET", "POST"])
async def proxy_asi(path: str, request: Request):
    """Proxy to ASI service"""
    return await _proxy_to_service("asi", path, request)


@app.api_route("/api/aviation/{path:path}", methods=["GET", "POST"])
async def proxy_aviation(path: str, request: Request):
    """Proxy to Aviation Weather service"""
    return await _proxy_to_service("aviation", path, request)


@app.api_route("/api/translate/{path:path}", methods=["GET", "POST"])
async def proxy_translation(path: str, request: Request):
    """Proxy to Translation service"""
    return await _proxy_to_service("translation", path, request)


async def _proxy_to_service(service_id: str, path: str, request: Request):
    """Generic proxy handler"""
    svc = SERVICES.get(service_id)
    if not svc:
        raise HTTPException(404, f"Service {service_id} not found")

    url = f"http://{svc.host}:{svc.port}/{path}"

    async with httpx.AsyncClient(timeout=svc.timeout) as client:
        if request.method == "GET":
            resp = await client.get(url, params=dict(request.query_params))
        else:
            body = await request.json() if request.headers.get("content-type") == "application/json" else {}
            resp = await client.post(url, json=body)

        return JSONResponse(content=resp.json(), status_code=resp.status_code)


# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import uvicorn

    logger.info(f"🌊 Ocean Orchestrator v1.0")
    logger.info(f"📡 Registered {len(SERVICES)} services")
    logger.info(f"🔗 Ollama: {OLLAMA_HOST}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
