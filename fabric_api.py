#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KLOUD FABRIC API  (Port 7800)
==============================
Endpoints për menaxhimin e plotë të Kloud Sovereign Fabric.

GET  /health               → status i fabric-it
GET  /fabric/topology      → harta e plotë (të gjitha nyjet + status)
GET  /fabric/nodes         → listë nyjesh (me filtër ?role=brain|compute|failover|edge)
GET  /fabric/nodes/{id}    → detaje nyje specifike
POST /fabric/nodes/{id}/check  → health-check manual i një nyje
POST /fabric/check-all     → health-check të gjitha njëherazi
GET  /fabric/route?region=eu-central&service=inference  → routing recommendation
GET  /fabric/summary       → KPI overview
POST /fabric/telemetry     → ingest telemetry nga nyje (BTI/DAS/PFD)
GET  /fabric/telemetry     → lexo telemetry (?node_id=&limit=100)
"""

import asyncio
import logging
import os
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from fabric_core import get_fabric, FABRIC_NODES, GEO_ROUTING

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(name)s - %(message)s")
logger = logging.getLogger("FabricAPI")

PORT = int(os.getenv("FABRIC_API_PORT", "7800"))
HEALTH_INTERVAL = int(os.getenv("FABRIC_HEALTH_INTERVAL", "30"))


# ── Lifespan ─────────────────────────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI):
    fabric = get_fabric()
    # Kryej health-check fillestar (jo-bllokues)
    asyncio.create_task(fabric.check_all())
    # Nis health loop në background
    task = asyncio.create_task(fabric.start_health_loop(HEALTH_INTERVAL))
    logger.info("[FABRIC] Health loop started — interval=%ds", HEALTH_INTERVAL)
    yield
    task.cancel()


app = FastAPI(
    title="Kloud Fabric API",
    description="Sovereign Intelligence Fabric — 6 global nodes",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Schemas ───────────────────────────────────────────────────────────────────


class TelemetryPayload(BaseModel):
    node_id: str
    type: str = "generic"  # bti | das | pfd | health | custom
    data: Dict[str, Any] = {}


# ── Endpoints ────────────────────────────────────────────────────────────────


@app.get("/health")
async def health():
    fabric = get_fabric()
    s = fabric.summary()
    return {
        "service": "kloud-fabric",
        "status": "healthy" if s["hq_healthy"] else "degraded",
        **s,
    }


@app.get("/fabric/topology")
async def topology():
    return get_fabric().get_topology()


@app.get("/fabric/nodes")
async def list_nodes(
    role: Optional[str] = Query(None, description="brain|compute|failover|edge"),
):
    return {"nodes": get_fabric().list_nodes(role=role)}


@app.get("/fabric/nodes/{node_id}")
async def get_node(node_id: str):
    node = get_fabric().get_node(node_id)
    if not node:
        raise HTTPException(
            status_code=404, detail=f"Node '{node_id}' not found in fabric"
        )
    return node


@app.post("/fabric/nodes/{node_id}/check")
async def check_node(node_id: str):
    fabric = get_fabric()
    if node_id not in {n["id"] for n in FABRIC_NODES}:
        raise HTTPException(status_code=404, detail=f"Node '{node_id}' not found")
    status = await fabric.check_node(node_id)
    return status.to_dict()


@app.post("/fabric/check-all")
async def check_all():
    result = await get_fabric().check_all()
    return {nid: s.to_dict() for nid, s in result.items()}


@app.get("/fabric/route")
async def route(
    region: str = Query(
        "default",
        description="eu-north|eu-central|eu-west|us-east|us-west|ap-southeast|ap-northeast",
    ),
    service: Optional[str] = Query(
        None, description="alba|albi|jona|audio|eeg|inference|batch"
    ),
):
    return get_fabric().route(region=region, service=service)


@app.get("/fabric/route/compute")
async def route_compute():
    """Kthen nyjen më të mirë për heavy AI inference."""
    return get_fabric().best_for_compute()


@app.get("/fabric/summary")
async def summary():
    return get_fabric().summary()


@app.post("/fabric/telemetry")
async def ingest_telemetry(payload: TelemetryPayload):
    """
    Preson telemetry nga çdo nyje e fabric-it.
    Tipi mund të jetë: bti (Behavioral Trace Index),
                       das (Deviation Amplitude Score),
                       pfd (Propagation Field Dynamics).
    """
    known_ids = {n["id"] for n in FABRIC_NODES}
    if payload.node_id not in known_ids:
        raise HTTPException(
            status_code=400, detail=f"Unknown node_id: {payload.node_id}"
        )
    get_fabric().ingest_telemetry(
        payload.node_id, {"type": payload.type, "data": payload.data}
    )
    return {"ok": True, "node_id": payload.node_id}


@app.get("/fabric/telemetry")
async def get_telemetry(
    node_id: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
):
    return {"events": get_fabric().get_telemetry(node_id=node_id, limit=limit)}


@app.get("/fabric/geo-routing")
async def geo_routing():
    """Tabela e routing sipas rajoneve gjeografike."""
    return {"routing": GEO_ROUTING}


# ── Main entry ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run("fabric_api:app", host="0.0.0.0", port=PORT, reload=False)
