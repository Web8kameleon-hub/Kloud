"""
AGENT ORCHESTRATOR API - Scalable Agent Service (40401)
=======================================================

Exposes the Kloud AgentOrchestrator (agents.py) as a scalable HTTP service.
Real orchestrator, real ALBA/ALBI/JONA agent pools with autoscale.

Author: Ledjan Ahmati / WEB8euroweb GmbH
System: Kloud Cloud - Sovereign Runtime
"""
from __future__ import annotations

import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agents import AgentOrchestrator

PORT = int(os.getenv("PORT", "40401"))

_orch: Optional[AgentOrchestrator] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _orch
    _orch = AgentOrchestrator(auto_register_core=True)
    await _orch.initialize()
    yield
    if _orch:
        await _orch.shutdown()


app = FastAPI(
    title="Kloud Agent Orchestrator",
    description="Scalable ALBA/ALBI/JONA agent pools with autoscale",
    version="1.0.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)


class SubmitRequest(BaseModel):
    agent: str
    payload: Dict[str, Any] = {}
    timeout: float = 30.0


class ScaleRequest(BaseModel):
    agent: str
    target: int


class BroadcastRequest(BaseModel):
    payload: Dict[str, Any] = {}
    agents: Optional[List[str]] = None


def _require_orch() -> AgentOrchestrator:
    if _orch is None:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    return _orch


@app.get("/health")
async def health() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "service": "agent-orchestrator",
        "initialized": _orch is not None,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/status")
async def status() -> Dict[str, Any]:
    return _require_orch().status


@app.get("/agents")
async def list_agents() -> Dict[str, Any]:
    orch = _require_orch()
    agents = orch.list_agents()
    return {"total": len(agents), "agents": agents}


@app.post("/agents/submit")
async def submit(req: SubmitRequest) -> Dict[str, Any]:
    orch = _require_orch()
    result = await orch.submit(req.agent, req.payload, timeout=req.timeout)
    return {
        "task_id": result.task_id,
        "agent_id": result.agent_id,
        "success": result.success,
        "result": getattr(result, "result", None),
        "error": getattr(result, "error", None),
    }


@app.post("/agents/scale")
async def scale(req: ScaleRequest) -> Dict[str, Any]:
    orch = _require_orch()
    return await orch.scale(req.agent, req.target)


@app.post("/agents/broadcast")
async def broadcast(req: BroadcastRequest) -> Dict[str, Any]:
    orch = _require_orch()
    results = await orch.broadcast(req.payload, req.agents)
    return {
        name: {
            "success": r.success,
            "result": getattr(r, "result", None),
            "error": getattr(r, "error", None),
        }
        for name, r in results.items()
    }


if __name__ == "__main__":
    print(f"🤖 Agent Orchestrator API starting on {PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
