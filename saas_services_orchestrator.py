"""
SAAS Services Orchestrator
Coordinates Alba, Albi, Jona + AI Agents
Provides unified API + self-documentation + agent scaling
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
from pydantic import BaseModel
import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Orchestrator")

# Service URLs
ALBA_URL = f"http://{os.getenv('SERVICE_ALBA_HOST', 'localhost')}:5050"
ALBI_URL = f"http://{os.getenv('SERVICE_ALBI_HOST', 'localhost')}:6060"
JONA_URL = f"http://{os.getenv('SERVICE_JONA_HOST', 'localhost')}:7070"

app = FastAPI(
    title="Kloud SAAS Orchestrator",
    version="2.0.0",
    description="Coordinates Alba/Albi/Jona + AI agents with self-documentation and scaling",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# ═══════════════════════════════════════════════════════════════════
# GLOBAL STATE
# ═══════════════════════════════════════════════════════════════════

START_TIME = time.time()
INSTANCE_ID = uuid.uuid4().hex[:8]

# Agent registry - tracks active agents
agent_registry: Dict[str, Dict[str, Any]] = {}

# API documentation cache - auto-generated docs from agents
api_docs_cache: Dict[str, Dict[str, Any]] = {}

# Service health cache
service_health: Dict[str, Dict[str, Any]] = {}

# ═══════════════════════════════════════════════════════════════════
# HEALTH & STATUS
# ═══════════════════════════════════════════════════════════════════

@app.get("/health")
async def health_check():
    """Orchestrator health check"""
    return {
        "status": "operational",
        "instance_id": INSTANCE_ID,
        "uptime_seconds": time.time() - START_TIME,
        "registered_agents": len(agent_registry),
        "api_endpoints": len(api_docs_cache),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/status")
async def get_status():
    """Get comprehensive orchestrator status"""
    async with httpx.AsyncClient() as client:
        # Check service health
        services_status = {}
        
        for name, url in [("alba", ALBA_URL), ("albi", ALBI_URL), ("jona", JONA_URL)]:
            try:
                resp = await client.get(f"{url}/health", timeout=3)
                services_status[name] = {
                    "status": "healthy" if resp.status_code == 200 else "unhealthy",
                    "response_time_ms": resp.elapsed.total_seconds() * 1000,
                    "url": url
                }
            except Exception as e:
                services_status[name] = {
                    "status": "unreachable",
                    "error": str(e),
                    "url": url
                }
    
    return {
        "orchestrator": {
            "status": "operational",
            "uptime_seconds": time.time() - START_TIME,
            "instance_id": INSTANCE_ID
        },
        "services": services_status,
        "agents": {
            "registered": len(agent_registry),
            "active": sum(1 for a in agent_registry.values() if a.get("status") == "active")
        },
        "api_docs": {
            "endpoints_documented": len(api_docs_cache),
            "total_operations": sum(len(doc.get("operations", [])) for doc in api_docs_cache.values())
        }
    }

# ═══════════════════════════════════════════════════════════════════
# AGENT REGISTRY & SCALING
# ═══════════════════════════════════════════════════════════════════

class AgentRegistration(BaseModel):
    agent_name: str
    agent_type: str  # "agiem", "asi", "blerina", "saas", "custom"
    version: str
    capabilities: List[str]
    endpoints: Optional[List[Dict[str, Any]]] = None
    max_instances: int = 1
    metadata: Optional[Dict[str, Any]] = None

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
    
    # Simulate scaling (in production, would trigger container orchestration)
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
# AUTO-GENERATED API DOCUMENTATION
# ═══════════════════════════════════════════════════════════════════

@app.post("/api-docs/generate")
async def generate_api_docs(
    agent_id: str,
    doc_request: Dict[str, Any]
):
    """Generate OpenAPI documentation for agent endpoints"""
    if agent_id not in agent_registry:
        raise HTTPException(status_code=404, detail="agent_not_found")
    
    agent = agent_registry[agent_id]
    endpoints = doc_request.get("endpoints", [])
    
    # Generate OpenAPI 3.1.0 specification
    openapi_spec = {
        "openapi": "3.1.0",
        "info": {
            "title": f"{agent['agent_name']} API",
            "version": agent['version'],
            "description": f"Auto-generated API documentation for {agent['agent_name']}",
            "x-agent-id": agent_id,
            "x-agent-type": agent['agent_type']
        },
        "servers": [
            {
                "url": "http://localhost:9999",
                "description": "Orchestrator (development)"
            }
        ],
        "paths": {},
        "components": {
            "schemas": {}
        }
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
                    "content": {
                        "application/json": {
                            "schema": {"type": "object"}
                        }
                    }
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
# SERVICE PROXY (Alba/Albi/Jona)
# ═══════════════════════════════════════════════════════════════════

@app.api_route("/services/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_to_service(service: str, path: str, request: Request):
    """Proxy requests to Alba/Albi/Jona services"""
    service_urls = {
        "alba": ALBA_URL,
        "albi": ALBI_URL,
        "jona": JONA_URL
    }
    
    if service not in service_urls:
        raise HTTPException(status_code=404, detail=f"service_{service}_not_found")
    
    target_url = f"{service_urls[service]}/{path}"
    
    async with httpx.AsyncClient() as client:
        try:
            # Forward request
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=dict(request.headers),
                content=await request.body(),
                timeout=30
            )
            
            return JSONResponse(
                content=response.json() if response.headers.get("content-type", "").startswith("application/json") else {"response": response.text},
                status_code=response.status_code
            )
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"service_proxy_error: {str(e)}")

# ═══════════════════════════════════════════════════════════════════
# STARTUP
# ═══════════════════════════════════════════════════════════════════

@app.on_event("startup")
async def startup():
    logger.info("🚀 Kloud SAAS Orchestrator starting...")
    logger.info(f"   Instance ID: {INSTANCE_ID}")
    logger.info(f"   Alba: {ALBA_URL}")
    logger.info(f"   Albi: {ALBI_URL}")
    logger.info(f"   Jona: {JONA_URL}")
    logger.info("✅ Orchestrator ready")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "9999"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")


