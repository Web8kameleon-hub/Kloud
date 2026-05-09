"""
╔════════════════════════════════════════════════════════════════════╗
║     KLOUD CLOUD - UNIFIED SAAS ORCHESTRATOR v3.0               ║
║     Features: Service Registry + Agent Scaling + Auto API Docs    ║
║     Coordinates: Alba/Albi/Jona + AI Agents + Inter-Service Mesh  ║
╚════════════════════════════════════════════════════════════════════╝

Combines:
1. Service Discovery & Health Monitoring
2. AI Agent Registration & Scaling
3. Auto-Generated API Documentation (OpenAPI 3.1)
4. Inter-Service Communication Proxy
5. Distributed Tracing (OpenTelemetry)
"""

import os
import asyncio
import logging
import json
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from collections import defaultdict

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import httpx

# OpenTelemetry imports
try:
    from tracing import setup_tracing, instrument_fastapi_app, instrument_http_clients
    TRACING_ENABLED = True
except ImportError:
    TRACING_ENABLED = False
    logger = logging.getLogger("Orchestrator")
    logger.warning("OpenTelemetry tracing not available - running without tracing")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Orchestrator")

# ═══════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════

# Service URLs (safe ports: 5050, 6060, 7070)
ALBA_URL = f"http://{os.getenv('SERVICE_ALBA_HOST', 'localhost')}:5050"
ALBI_URL = f"http://{os.getenv('SERVICE_ALBI_HOST', 'localhost')}:6060"
JONA_URL = f"http://{os.getenv('SERVICE_JONA_HOST', 'localhost')}:7070"

SERVICE_REGISTRY = {
    "alba": {"url": ALBA_URL, "port": 5050, "role": "Network telemetry collector"},
    "albi": {"url": ALBI_URL, "port": 6060, "role": "Neural analytics processor"},
    "jona": {"url": JONA_URL, "port": 7070, "role": "Data synthesis coordinator"}
}

START_TIME = time.time()
INSTANCE_ID = uuid.uuid4().hex[:8]

# ═══════════════════════════════════════════════════════════════════
# FASTAPI APP
# ═══════════════════════════════════════════════════════════════════

app = FastAPI(
    title="Kloud Unified SAAS Orchestrator",
    version="3.0.0",
    description="Service Registry + Agent Scaling + Auto API Docs + Inter-Service Mesh",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Initialize tracing if available
if TRACING_ENABLED:
    tracer = setup_tracing("orchestrator")
    instrument_fastapi_app(app, "orchestrator")
    instrument_http_clients()
else:
    tracer = None

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# ═══════════════════════════════════════════════════════════════════
# GLOBAL STATE
# ═══════════════════════════════════════════════════════════════════

# Agent registry - tracks active AI agents
agent_registry: Dict[str, Dict[str, Any]] = {}

# API documentation cache - auto-generated OpenAPI specs
api_docs_cache: Dict[str, Dict[str, Any]] = {}

# Service health cache
service_health_cache: Dict[str, Dict[str, Any]] = {}

# Inter-service communication log
communication_log: List[Dict[str, Any]] = []

# ═══════════════════════════════════════════════════════════════════
# PYDANTIC MODELS
# ═══════════════════════════════════════════════════════════════════

class AgentRegistration(BaseModel):
    agent_name: str
    agent_type: str  # "agiem", "asi", "blerina", "saas", "custom"
    version: str
    capabilities: List[str]
    endpoints: Optional[List[Dict[str, Any]]] = None
    max_instances: int = 1
    metadata: Optional[Dict[str, Any]] = None

class DataPacket(BaseModel):
    """Inter-service communication packet"""
    source: str
    destination: str
    packet_type: str  # "telemetry", "analytics", "synthesis", "heartbeat"
    payload: Dict[str, Any]
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    correlation_id: str = Field(default_factory=lambda: uuid.uuid4().hex)

class ServiceRequest(BaseModel):
    action: str
    parameters: Dict[str, Any] = {}

# ═══════════════════════════════════════════════════════════════════
# SERVICE DISCOVERY & HEALTH MONITORING
# ═══════════════════════════════════════════════════════════════════

async def check_service_health(service_name: str, url: str) -> Dict[str, Any]:
    """Check if service is responding"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{url}/health", timeout=3.0)
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "healthy",
                    "health_score": 1.0,
                    "response_time_ms": response.elapsed.total_seconds() * 1000,
                    "data": data
                }
            else:
                return {
                    "status": "degraded",
                    "health_score": 0.5,
                    "response_code": response.status_code
                }
    except httpx.TimeoutException:
        return {"status": "timeout", "health_score": 0.2}
    except Exception as e:
        return {"status": "unreachable", "health_score": 0.0, "error": str(e)}

async def refresh_service_health():
    """Refresh health status for all services"""
    for service_name, config in SERVICE_REGISTRY.items():
        health = await check_service_health(service_name, config["url"])
        service_health_cache[service_name] = {
            **health,
            "service": service_name,
            "url": config["url"],
            "port": config["port"],
            "role": config["role"],
            "last_check": datetime.now(timezone.utc).isoformat()
        }

# ═══════════════════════════════════════════════════════════════════
# ENDPOINTS - HEALTH & STATUS
# ═══════════════════════════════════════════════════════════════════

@app.get("/health")
async def health_check():
    """Orchestrator health check"""
    return {
        "status": "operational",
        "instance_id": INSTANCE_ID,
        "uptime_seconds": time.time() - START_TIME,
        "registered_agents": len(agent_registry),
        "api_endpoints_documented": len(api_docs_cache),
        "services_monitored": len(SERVICE_REGISTRY),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/status")
async def get_comprehensive_status():
    """Get comprehensive orchestrator status"""
    await refresh_service_health()
    
    healthy_services = sum(1 for s in service_health_cache.values() if s.get("status") == "healthy")
    active_agents = sum(1 for a in agent_registry.values() if a.get("status") == "active")
    
    return {
        "orchestrator": {
            "status": "operational",
            "version": "3.0.0",
            "uptime_seconds": time.time() - START_TIME,
            "instance_id": INSTANCE_ID
        },
        "services": {
            "total": len(SERVICE_REGISTRY),
            "healthy": healthy_services,
            "health_details": service_health_cache
        },
        "agents": {
            "registered": len(agent_registry),
            "active": active_agents,
            "total_instances": sum(a.get("current_instances", 0) for a in agent_registry.values())
        },
        "api_docs": {
            "endpoints_documented": len(api_docs_cache),
            "total_operations": sum(len(doc.get("spec", {}).get("paths", {})) for doc in api_docs_cache.values())
        },
        "communication": {
            "messages_logged": len(communication_log)
        }
    }

@app.get("/registry")
async def get_service_registry():
    """Get service registry with current health status"""
    await refresh_service_health()
    
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "instance_id": INSTANCE_ID,
        "services": service_health_cache,
        "total_services": len(SERVICE_REGISTRY),
        "healthy_count": sum(1 for s in service_health_cache.values() if s.get("status") == "healthy")
    }

# ═══════════════════════════════════════════════════════════════════
# ENDPOINTS - AGENT REGISTRY & SCALING
# ═══════════════════════════════════════════════════════════════════

@app.post("/agents/register")
async def register_agent(registration: AgentRegistration):
    """Register a new AI agent with the orchestrator"""
    agent_id = f"{registration.agent_name}_{uuid.uuid4().hex[:6]}"
    
    agent_entry = {
        "agent_id": agent_id,
        "agent_name": registration.agent_name,
        "agent_type": registration.agent_type,
        "version": registration.version,
        "capabilities": registration.capabilities,
        "endpoints": registration.endpoints or [],
        "max_instances": registration.max_instances,
        "current_instances": 1,
        "status": "active",
        "registered_at": datetime.now(timezone.utc).isoformat(),
        "last_heartbeat": datetime.now(timezone.utc).isoformat(),
        "metadata": registration.metadata or {}
    }
    
    agent_registry[agent_id] = agent_entry
    
    # Auto-generate API docs if endpoints provided
    if registration.endpoints:
        api_docs_cache[agent_id] = {
            "agent": registration.agent_name,
            "operations": registration.endpoints,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
    
    logger.info(f"✅ Agent registered: {registration.agent_name} ({agent_id})")
    
    return {
        "status": "registered",
        "agent_id": agent_id,
        "agent_name": registration.agent_name,
        "capabilities": registration.capabilities
    }

@app.post("/agents/{agent_id}/heartbeat")
async def agent_heartbeat(agent_id: str, metrics: Optional[Dict[str, Any]] = None):
    """Receive heartbeat from agent"""
    if agent_id not in agent_registry:
        raise HTTPException(status_code=404, detail="agent_not_found")
    
    agent_registry[agent_id]["last_heartbeat"] = datetime.now(timezone.utc).isoformat()
    agent_registry[agent_id]["status"] = "active"
    
    if metrics:
        agent_registry[agent_id]["last_metrics"] = metrics
    
    return {"status": "acknowledged"}

@app.post("/agents/{agent_id}/scale")
async def scale_agent(agent_id: str, target_instances: int):
    """Scale agent instances up or down"""
    if agent_id not in agent_registry:
        raise HTTPException(status_code=404, detail="agent_not_found")
    
    agent = agent_registry[agent_id]
    current = agent["current_instances"]
    max_allowed = agent["max_instances"]
    
    if target_instances > max_allowed:
        raise HTTPException(
            status_code=400,
            detail=f"target_instances ({target_instances}) exceeds max_instances ({max_allowed})"
        )
    
    if target_instances < 1:
        raise HTTPException(status_code=400, detail="target_instances must be >= 1")
    
    agent["current_instances"] = target_instances
    agent["scaled_at"] = datetime.now(timezone.utc).isoformat()
    
    logger.info(f"📈 Scaled {agent['agent_name']}: {current} → {target_instances} instances")
    
    return {
        "status": "scaled",
        "agent_id": agent_id,
        "previous_instances": current,
        "current_instances": target_instances,
        "max_instances": max_allowed
    }

@app.get("/agents")
async def list_agents():
    """List all registered agents"""
    return {
        "count": len(agent_registry),
        "agents": list(agent_registry.values())
    }

@app.get("/agents/{agent_id}")
async def get_agent(agent_id: str):
    """Get specific agent details"""
    if agent_id not in agent_registry:
        raise HTTPException(status_code=404, detail="agent_not_found")
    
    return agent_registry[agent_id]

# ═══════════════════════════════════════════════════════════════════
# ENDPOINTS - AUTO-GENERATED API DOCUMENTATION
# ═══════════════════════════════════════════════════════════════════

@app.post("/api-docs/generate")
async def generate_api_docs(agent_id: str, doc_request: Dict[str, Any]):
    """Generate OpenAPI 3.1.0 documentation for agent endpoints"""
    if agent_id not in agent_registry:
        raise HTTPException(status_code=404, detail="agent_not_found")
    
    agent = agent_registry[agent_id]
    endpoints = doc_request.get("endpoints", [])
    
    # Generate OpenAPI spec
    openapi_spec = {
        "openapi": "3.1.0",
        "info": {
            "title": f"{agent['agent_name']} API",
            "version": agent['version'],
            "description": f"Auto-generated API documentation for {agent['agent_name']} ({agent['agent_type']} agent)",
            "x-agent-id": agent_id,
            "x-agent-type": agent['agent_type'],
            "x-capabilities": agent['capabilities']
        },
        "servers": [
            {"url": "http://localhost:9999", "description": "Orchestrator (local)"},
            {"url": f"http://{os.getenv('PUBLIC_HOST', 'api.kloud.com')}", "description": "Production"}
        ],
        "paths": {},
        "components": {"schemas": {}}
    }
    
    # Build paths from endpoint definitions
    for endpoint in endpoints:
        path = endpoint.get("path", "/")
        method = endpoint.get("method", "get").lower()
        
        if path not in openapi_spec["paths"]:
            openapi_spec["paths"][path] = {}
        
        openapi_spec["paths"][path][method] = {
            "summary": endpoint.get("summary", ""),
            "description": endpoint.get("description", ""),
            "operationId": endpoint.get("operation_id", f"{agent['agent_name']}_{path.replace('/', '_')}_{method}"),
            "tags": [agent['agent_name']],
            "responses": endpoint.get("responses", {
                "200": {
                    "description": "Successful response",
                    "content": {"application/json": {"schema": {"type": "object"}}}
                }
            })
        }
        
        if "parameters" in endpoint:
            openapi_spec["paths"][path][method]["parameters"] = endpoint["parameters"]
        
        if "requestBody" in endpoint:
            openapi_spec["paths"][path][method]["requestBody"] = endpoint["requestBody"]
    
    # Cache the generated docs
    api_docs_cache[agent_id] = {
        "agent": agent['agent_name'],
        "agent_type": agent['agent_type'],
        "spec": openapi_spec,
        "generated_at": datetime.now(timezone.utc).isoformat()
    }
    
    logger.info(f"📝 Generated API docs for {agent['agent_name']}: {len(endpoints)} endpoints")
    
    return {
        "status": "generated",
        "agent_id": agent_id,
        "endpoints_count": len(endpoints),
        "spec": openapi_spec
    }

@app.get("/api-docs")
async def list_api_docs():
    """List all generated API documentation"""
    return {
        "count": len(api_docs_cache),
        "docs": list(api_docs_cache.values())
    }

@app.get("/api-docs/{agent_id}")
async def get_api_docs(agent_id: str):
    """Get specific agent's API documentation"""
    if agent_id not in api_docs_cache:
        raise HTTPException(status_code=404, detail="api_docs_not_found")
    
    return api_docs_cache[agent_id]

@app.get("/api-docs/{agent_id}/openapi.json")
async def get_openapi_spec(agent_id: str):
    """Get OpenAPI spec for specific agent"""
    if agent_id not in api_docs_cache:
        raise HTTPException(status_code=404, detail="api_docs_not_found")
    
    return api_docs_cache[agent_id]["spec"]

# ═══════════════════════════════════════════════════════════════════
# ENDPOINTS - INTER-SERVICE COMMUNICATION
# ═══════════════════════════════════════════════════════════════════

@app.post("/communicate")
async def inter_service_communicate(packet: DataPacket):
    """Route communication between services"""
    communication_log.append(packet.dict())
    
    # Keep log size bounded
    if len(communication_log) > 1000:
        communication_log[:] = communication_log[-500:]
    
    dest_service = SERVICE_REGISTRY.get(packet.destination)
    if not dest_service:
        raise HTTPException(status_code=404, detail=f"Destination service '{packet.destination}' not found")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{dest_service['url']}/receive",
                json=packet.dict(),
                timeout=5.0
            )
            response_data = response.json()
            
            return {
                "status": "delivered",
                "correlation_id": packet.correlation_id,
                "destination": packet.destination,
                "response": response_data
            }
    except Exception as e:
        logger.error(f"Communication error to {packet.destination}: {e}")
        raise HTTPException(status_code=502, detail=f"Failed to reach destination: {str(e)}")

@app.get("/communication/log")
async def get_communication_log(limit: int = 50):
    """Get recent inter-service communication log"""
    recent = communication_log[-limit:]
    return {
        "total_logged": len(communication_log),
        "recent": recent
    }

# ═══════════════════════════════════════════════════════════════════
# ENDPOINTS - SERVICE PROXY
# ═══════════════════════════════════════════════════════════════════

@app.api_route("/services/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_to_service(service: str, path: str, request: Request):
    """Proxy requests to Alba/Albi/Jona services"""
    if service not in SERVICE_REGISTRY:
        raise HTTPException(status_code=404, detail=f"service_{service}_not_found")
    
    target_url = f"{SERVICE_REGISTRY[service]['url']}/{path}"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=dict(request.headers),
                content=await request.body(),
                timeout=30.0
            )
            
            return JSONResponse(
                content=response.json() if response.headers.get("content-type", "").startswith("application/json") else {"response": response.text},
                status_code=response.status_code
            )
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"service_proxy_error: {str(e)}")

@app.post("/services/{service}/execute")
async def execute_service_action(service: str, request_data: ServiceRequest):
    """Execute action on specific service"""
    if service not in SERVICE_REGISTRY:
        raise HTTPException(status_code=404, detail=f"service_{service}_not_found")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{SERVICE_REGISTRY[service]['url']}/execute",
                json=request_data.dict(),
                timeout=10.0
            )
            result = response.json()
            
            return {
                "service": service,
                "action": request_data.action,
                "status": "executed",
                "result": result
            }
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Service error: {str(e)}")

# ═══════════════════════════════════════════════════════════════════
# BACKGROUND TASKS
# ═══════════════════════════════════════════════════════════════════

@app.on_event("startup")
async def startup():
    logger.info("🚀 Kloud Unified SAAS Orchestrator v3.0 starting...")
    logger.info(f"   Instance ID: {INSTANCE_ID}")
    logger.info(f"   Alba: {ALBA_URL}")
    logger.info(f"   Albi: {ALBI_URL}")
    logger.info(f"   Jona: {JONA_URL}")
    logger.info(f"   Tracing: {'Enabled' if TRACING_ENABLED else 'Disabled'}")
    
    # Start background health checks
    asyncio.create_task(health_check_loop())
    
    logger.info("✅ Orchestrator ready")

async def health_check_loop():
    """Continuously check health of all services"""
    while True:
        try:
            await refresh_service_health()
            healthy = sum(1 for s in service_health_cache.values() if s.get("status") == "healthy")
            logger.debug(f"Health check: {healthy}/{len(SERVICE_REGISTRY)} services healthy")
            await asyncio.sleep(15)  # Check every 15 seconds
        except Exception as e:
            logger.error(f"Health check error: {e}")
            await asyncio.sleep(15)

# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "9999"))
    
    print("\n╔═══════════════════════════════════════════════════════════════╗")
    print("║  KLOUD UNIFIED SAAS ORCHESTRATOR v3.0                     ║")
    print("║  ──────────────────────────────────────────────────────────  ║")
    print(f"║  Port: {port}                                                    ║")
    print(f"║  API Docs: http://localhost:{port}/docs                          ║")
    print(f"║  Status: http://localhost:{port}/status                          ║")
    print(f"║  Registry: http://localhost:{port}/registry                      ║")
    print("║  ──────────────────────────────────────────────────────────  ║")
    print("║  Features:                                                    ║")
    print("║    ✓ Service Discovery & Health Monitoring                   ║")
    print("║    ✓ AI Agent Registration & Scaling                         ║")
    print("║    ✓ Auto-Generated API Documentation (OpenAPI 3.1)          ║")
    print("║    ✓ Inter-Service Communication Proxy                       ║")
    print("║    ✓ Distributed Tracing (OpenTelemetry)                     ║")
    print("╚═══════════════════════════════════════════════════════════════╝\n")
    
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")


