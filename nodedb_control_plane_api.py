"""
NodeDB + Nanogrid Control Plane API
===================================

Fluid, controlled transition control-plane for:
- production gap tracking
- real-time state sync
- multi-node membership
- recovery orchestration
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from nodendb_stigma import get_nodedb
from nodendb_kloud_integration import (
    initialize_kloud_nodedb_real,
    monitor_real_services,
    check_jona_sandbox_health,
    evaluate_governance_proposal,
)

NANOGRID_BASE_URL = "http://localhost:9999"
MEMBERSHIP_FILE = Path("output/nodedb/membership_registry.json")

app = FastAPI(title="NodeDB Control Plane", version="1.0.0")


@app.get("/")
async def root() -> Dict[str, Any]:
    return {
        "service": "nodedb-control-plane",
        "status": "ok",
        "message": "Use /health or /api/v1/control-plane/* endpoints",
        "routes": [
            "/health",
            "/api/v1/control-plane/bootstrap",
            "/api/v1/control-plane/sync",
            "/api/v1/control-plane/sync/loop/status",
            "/api/v1/control-plane/nodes",
            "/api/v1/control-plane/scan-print",
        ],
    }


class MembershipJoinRequest(BaseModel):
    node_id: str
    endpoint: str
    role: str = "peer"
    transport_tags: List[str] = Field(
        default_factory=lambda: ["loawan", "mesh", "any-wave", "cxl", "cxl.i"]
    )
    capabilities: Dict[str, Any] = Field(default_factory=dict)


class MembershipLeaveRequest(BaseModel):
    node_id: str
    reason: str = "graceful-leave"


class RecoveryTriggerRequest(BaseModel):
    node_id: str
    reason: str = "degraded"
    strategy: str = "fluid-gradual"


class GovernanceProposalRequest(BaseModel):
    proposal_id: str
    node_id: Optional[str] = None
    title: str
    requested_scope: str = "runtime-protocol"
    requires_self_learning: bool = False
    requires_self_writing: bool = False
    risk_score: float = 0.0
    tide: str = "normal"
    ndb_quality: str = "fair"
    payload: Dict[str, Any] = Field(default_factory=dict)


class ControlPlaneState:
    def __init__(self) -> None:
        self.context: Optional[Dict[str, Any]] = None
        self.membership: Dict[str, Dict[str, Any]] = {}
        self.recovery_plans: Dict[str, Dict[str, Any]] = {}
        self.sync_task: Optional[asyncio.Task[Any]] = None
        self.sync_interval_seconds: int = 5
        self.sync_last_run_utc: Optional[str] = None
        self.sync_cycles: int = 0
        MEMBERSHIP_FILE.parent.mkdir(parents=True, exist_ok=True)
        self._load_membership()

    def _load_membership(self) -> None:
        if not MEMBERSHIP_FILE.exists():
            self.membership = {}
            return
        try:
            self.membership = json.loads(MEMBERSHIP_FILE.read_text(encoding="utf-8"))
        except Exception:
            self.membership = {}

    def _save_membership(self) -> None:
        MEMBERSHIP_FILE.write_text(
            json.dumps(self.membership, ensure_ascii=True, indent=2), encoding="utf-8"
        )


state = ControlPlaneState()


async def _sync_loop_runner() -> None:
    while True:
        if state.context is None:
            state.context = await initialize_kloud_nodedb_real()

        await monitor_real_services(state.context)
        state.sync_cycles += 1
        state.sync_last_run_utc = datetime.now(timezone.utc).isoformat()
        await asyncio.sleep(max(1, state.sync_interval_seconds))


async def _ensure_nodedb_initialized() -> Any:
    if state.context is None:
        state.context = await initialize_kloud_nodedb_real()
    return get_nodedb()


@app.get("/health")
async def health() -> Dict[str, Any]:
    return {
        "status": "ok",
        "service": "nodedb-control-plane",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/api/v1/control-plane/bootstrap")
async def bootstrap() -> Dict[str, Any]:
    state.context = await initialize_kloud_nodedb_real()
    ctx = state.context or {}
    return {
        "status": "bootstrapped",
        "available_count": ctx.get("available_count", 0),
        "registered_services": list(ctx.get("services", {}).keys()),
    }


@app.post("/api/v1/control-plane/sync")
async def sync_now() -> Dict[str, Any]:
    if state.context is None:
        state.context = await initialize_kloud_nodedb_real()

    await monitor_real_services(state.context)
    nodedb = get_nodedb()
    nodes = await nodedb.list_nodes()

    return {
        "status": "synced",
        "nodes_total": len(nodes),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/api/v1/control-plane/sync/loop/start")
@app.post("/api/v1/control-plane/sync-loop/start")
async def sync_loop_start(interval_seconds: int = 5) -> Dict[str, Any]:
    state.sync_interval_seconds = max(1, interval_seconds)

    if state.sync_task is not None and not state.sync_task.done():
        return {
            "status": "already-running",
            "interval_seconds": state.sync_interval_seconds,
            "cycles": state.sync_cycles,
            "last_run_utc": state.sync_last_run_utc,
        }

    state.sync_task = asyncio.create_task(_sync_loop_runner(), name="nodedb-sync-loop")
    return {
        "status": "started",
        "interval_seconds": state.sync_interval_seconds,
        "cycles": state.sync_cycles,
    }


@app.post("/api/v1/control-plane/sync/loop/stop")
@app.post("/api/v1/control-plane/sync-loop/stop")
async def sync_loop_stop() -> Dict[str, Any]:
    if state.sync_task is None or state.sync_task.done():
        return {
            "status": "not-running",
            "cycles": state.sync_cycles,
            "last_run_utc": state.sync_last_run_utc,
        }

    state.sync_task.cancel()
    try:
        await state.sync_task
    except asyncio.CancelledError:
        pass
    finally:
        state.sync_task = None

    return {
        "status": "stopped",
        "cycles": state.sync_cycles,
        "last_run_utc": state.sync_last_run_utc,
    }


@app.get("/api/v1/control-plane/sync/loop/status")
@app.get("/api/v1/control-plane/sync-loop/status")
async def sync_loop_status() -> Dict[str, Any]:
    running = state.sync_task is not None and not state.sync_task.done()
    return {
        "running": running,
        "interval_seconds": state.sync_interval_seconds,
        "cycles": state.sync_cycles,
        "last_run_utc": state.sync_last_run_utc,
    }


@app.get("/api/v1/control-plane/nodes")
async def list_nodes() -> Dict[str, Any]:
    nodedb = await _ensure_nodedb_initialized()
    nodes = await nodedb.list_nodes()
    return {
        "count": len(nodes),
        "items": nodes,
    }


@app.get("/api/v1/control-plane/scan-print")
async def scan_print(limit: int = 200, output: str = "json") -> Dict[str, Any]:
    """Fast compact node scan for quick reading and terminal-friendly printing."""
    nodedb = await _ensure_nodedb_initialized()
    nodes = await nodedb.list_nodes()

    clipped = nodes[: max(1, min(limit, 1000))]
    compact: List[Dict[str, Any]] = []
    text_lines: List[str] = []

    for node in clipped:
        meta = node.get("metadata", {})
        state = node.get("state", {})
        metrics = (
            state.get("metrics", {}) if isinstance(state.get("metrics"), dict) else {}
        )

        row = {
            "node_id": meta.get("node_id"),
            "service": meta.get("service_name"),
            "type": meta.get("service_type"),
            "state": state.get("stigma_state"),
            "ndb_quality": state.get("ndb_quality"),
            "ndb_delta": state.get("ndb_delta"),
            "quality_score": metrics.get("quality_score"),
            "response_time_ms": metrics.get("response_time_ms"),
            "error_rate": metrics.get("error_rate"),
            "updated_at": state.get("updated_at"),
        }
        compact.append(row)

        text_lines.append(
            " | ".join(
                [
                    str(row.get("node_id") or "-"),
                    str(row.get("service") or "-"),
                    str(row.get("state") or "-"),
                    str(row.get("ndb_quality") or "-"),
                    str(row.get("quality_score") or "-"),
                ]
            )
        )

    payload: Dict[str, Any] = {
        "fabric_profile": "wwwmmm-ndb-stigma-tide-nanogrid-cxl-cxl.i",
        "count": len(compact),
        "items": compact,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }

    if output == "text":
        payload["printable"] = "\n".join(text_lines)

    return payload


@app.post("/api/v1/control-plane/governance/evaluate")
async def evaluate_governance(request: GovernanceProposalRequest) -> Dict[str, Any]:
    nodedb = await _ensure_nodedb_initialized()
    sandbox_health = await check_jona_sandbox_health()
    node_state = None

    if request.node_id:
        try:
            node_info = await nodedb.get_node_info(request.node_id)
            node_state = node_info.get("state", {})
        except Exception:
            node_state = None

    proposal = {
        "proposal_id": request.proposal_id,
        "title": request.title,
        "requested_scope": request.requested_scope,
        "requires_self_learning": request.requires_self_learning,
        "requires_self_writing": request.requires_self_writing,
        "risk_score": request.risk_score,
        "tide": request.tide,
        "ndb_quality": request.ndb_quality,
        "payload": request.payload,
    }

    decision = evaluate_governance_proposal(proposal, sandbox_health, node_state)

    state.recovery_plans[request.proposal_id] = {
        "proposal": proposal,
        "decision": decision,
        "sandbox": sandbox_health,
        "updated_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    state._save_membership()

    return {
        "status": decision.get("decision", "sandbox_only"),
        "proposal_id": request.proposal_id,
        "decision": decision,
        "sandbox": sandbox_health,
    }


@app.get("/api/v1/control-plane/nodes/{node_id}")
async def get_node(node_id: str) -> Dict[str, Any]:
    nodedb = await _ensure_nodedb_initialized()
    try:
        node = await nodedb.get_node_info(node_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return node


@app.get("/api/v1/control-plane/nanogrid/status")
async def nanogrid_status() -> Dict[str, Any]:
    async with httpx.AsyncClient(timeout=8.0) as client:
        status_resp = await client.get(f"{NANOGRID_BASE_URL}/api/v1/resonant/status")
        metrics_resp = await client.get(f"{NANOGRID_BASE_URL}/api/v1/resonant/metrics")

    return {
        "resonant_status": status_resp.json() if status_resp.status_code == 200 else {},
        "resonant_metrics": metrics_resp.json()
        if metrics_resp.status_code == 200
        else {},
        "source": NANOGRID_BASE_URL,
    }


@app.get("/api/v1/control-plane/membership")
async def membership_list() -> Dict[str, Any]:
    return {
        "count": len(state.membership),
        "items": list(state.membership.values()),
    }


@app.post("/api/v1/control-plane/membership/join")
async def membership_join(req: MembershipJoinRequest) -> Dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat()
    member = {
        "node_id": req.node_id,
        "endpoint": req.endpoint,
        "role": req.role,
        "transport_tags": req.transport_tags,
        "capabilities": req.capabilities,
        "membership_state": "active",
        "joined_at": now,
        "updated_at": now,
    }
    state.membership[req.node_id] = member
    state._save_membership()
    return {
        "status": "joined",
        "member": member,
    }


@app.post("/api/v1/control-plane/membership/leave")
async def membership_leave(req: MembershipLeaveRequest) -> Dict[str, Any]:
    member = state.membership.get(req.node_id)
    if member is None:
        raise HTTPException(status_code=404, detail=f"Unknown member: {req.node_id}")

    member["membership_state"] = "left"
    member["leave_reason"] = req.reason
    member["updated_at"] = datetime.now(timezone.utc).isoformat()
    state.membership[req.node_id] = member
    state._save_membership()

    return {
        "status": "left",
        "member": member,
    }


@app.post("/api/v1/control-plane/recovery/trigger")
async def recovery_trigger(req: RecoveryTriggerRequest) -> Dict[str, Any]:
    nodedb = get_nodedb()
    try:
        node_state = await nodedb.trigger_recovery(req.node_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    now = datetime.now(timezone.utc).isoformat()
    recovery_plan = {
        "node_id": req.node_id,
        "strategy": req.strategy,
        "reason": req.reason,
        "steps": [
            "isolate-node-soft",
            "run-health-probe",
            "resync-from-nanogrid-chain",
            "restore-active-state-gradually",
        ],
        "created_at": now,
        "updated_at": now,
        "status": "in-progress",
    }
    state.recovery_plans[req.node_id] = recovery_plan

    return {
        "status": "recovery-triggered",
        "node_state": node_state.to_dict(),
        "recovery_plan": recovery_plan,
    }


@app.get("/api/v1/control-plane/recovery/{node_id}")
async def recovery_status(node_id: str) -> Dict[str, Any]:
    plan = state.recovery_plans.get(node_id)
    if plan is None:
        raise HTTPException(status_code=404, detail=f"No recovery plan for: {node_id}")
    return plan


@app.get("/api/v1/control-plane/topology")
async def topology() -> Dict[str, Any]:
    nodedb = await _ensure_nodedb_initialized()
    nodes = await nodedb.list_nodes()

    edges = []
    for member in state.membership.values():
        if member.get("membership_state") == "active":
            edges.append(
                {
                    "node_id": member.get("node_id"),
                    "endpoint": member.get("endpoint"),
                    "transport": member.get("transport_tags", []),
                }
            )

    return {
        "fabric_profile": "wwwmmm-ndb-stigma-tide-nanogrid-cxl-cxl.i",
        "nodes_total": len(nodes),
        "active_members": len(edges),
        "members": edges,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
