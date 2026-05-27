from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(tags=["nodedb-control-plane"])


class NodeHeartbeat(BaseModel):
    node_id: str = Field(min_length=2)
    role: str = "edge"
    capabilities: List[str] = Field(default_factory=list)
    status: str = "healthy"
    latency_ms: float = 0.0
    queue_depth: int = 0
    zone: str = "default"
    battery: Optional[float] = None
    signal_strength: Optional[float] = None
    heartbeat_at: Optional[str] = None


class LeaseAcquireRequest(BaseModel):
    lease_id: str = Field(min_length=2)
    node_id: str = Field(min_length=2)
    ttl_ms: int = Field(default=10000, ge=1000, le=120000)


class LeaseRenewRequest(BaseModel):
    lease_id: str = Field(min_length=2)
    node_id: str = Field(min_length=2)
    ttl_ms: int = Field(default=10000, ge=1000, le=120000)


class NodeDBControlPlane:
    def __init__(self, degraded_after_s: int = 5, offline_after_s: int = 15):
        self._lock = Lock()
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.leases: Dict[str, Dict[str, Any]] = {}
        self.topology_events: List[Dict[str, Any]] = []
        self.degraded_after_s = degraded_after_s
        self.offline_after_s = offline_after_s
        wal_default = "./storage/nodedb_wal.jsonl"
        self.wal_path = Path(os.getenv("NODEDB_WAL_PATH", wal_default)).resolve()
        self.wal_path.parent.mkdir(parents=True, exist_ok=True)

    def reset(self) -> None:
        with self._lock:
            self.nodes.clear()
            self.leases.clear()
            self.topology_events.clear()

    def _utcnow(self) -> datetime:
        return datetime.now(timezone.utc)

    def _parse_timestamp(self, value: Optional[str]) -> datetime:
        if not value:
            return self._utcnow()
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed

    def _record_event(self, event_type: str, payload: Dict[str, Any]) -> None:
        event = {
            "event_type": event_type,
            "timestamp": self._utcnow().isoformat(),
            "payload": payload,
        }
        self.topology_events.append(event)
        if len(self.topology_events) > 1000:
            self.topology_events = self.topology_events[-1000:]
        self._append_wal(event)

    def _append_wal(self, event: Dict[str, Any]) -> None:
        try:
            with self.wal_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(event, ensure_ascii=False) + "\n")
        except OSError:
            # WAL write failures should not break control-plane APIs.
            return

    def read_wal(self, limit: int = 100) -> List[Dict[str, Any]]:
        limit = max(1, min(limit, 1000))
        if not self.wal_path.exists():
            return []
        lines: List[str] = []
        try:
            with self.wal_path.open("r", encoding="utf-8") as handle:
                lines = handle.readlines()[-limit:]
        except OSError:
            return []
        out: List[Dict[str, Any]] = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return out

    def refresh_status(self) -> None:
        now = self._utcnow()
        with self._lock:
            for node in self.nodes.values():
                last = self._parse_timestamp(node.get("last_heartbeat_at"))
                age = (now - last).total_seconds()
                if age > self.offline_after_s:
                    node["status"] = "offline"
                elif age > self.degraded_after_s:
                    node["status"] = "degraded"

    def heartbeat(self, payload: NodeHeartbeat) -> Dict[str, Any]:
        now = self._utcnow().isoformat()
        observed_at = self._parse_timestamp(payload.heartbeat_at).isoformat()
        with self._lock:
            existing = self.nodes.get(payload.node_id)
            node = {
                "node_id": payload.node_id,
                "role": payload.role,
                "capabilities": payload.capabilities,
                "status": payload.status,
                "latency_ms": payload.latency_ms,
                "queue_depth": payload.queue_depth,
                "zone": payload.zone,
                "battery": payload.battery,
                "signal_strength": payload.signal_strength,
                "last_heartbeat_at": observed_at,
                "updated_at": now,
            }
            self.nodes[payload.node_id] = node
            self._record_event(
                "node.join" if existing is None else "node.heartbeat",
                {"node_id": payload.node_id, "status": node["status"]},
            )
            return node

    def _next_fencing_token(self, lease_id: str) -> int:
        current = self.leases.get(lease_id)
        if current:
            return int(current.get("fencing_token", 0)) + 1
        return 1

    def acquire_lease(self, payload: LeaseAcquireRequest) -> Dict[str, Any]:
        now = self._utcnow()
        expires_at = now + timedelta(milliseconds=payload.ttl_ms)
        with self._lock:
            current = self.leases.get(payload.lease_id)
            if current is not None:
                current_exp = self._parse_timestamp(current["expires_at"])
                if current_exp > now and current["holder_node_id"] != payload.node_id:
                    raise HTTPException(
                        status_code=409,
                        detail={
                            "error": "lease_conflict",
                            "lease_id": payload.lease_id,
                            "holder_node_id": current["holder_node_id"],
                            "fencing_token": current["fencing_token"],
                        },
                    )

            lease = {
                "lease_id": payload.lease_id,
                "holder_node_id": payload.node_id,
                "acquired_at": now.isoformat(),
                "expires_at": expires_at.isoformat(),
                "renew_interval_ms": int(payload.ttl_ms / 2),
                "fencing_token": self._next_fencing_token(payload.lease_id),
            }
            self.leases[payload.lease_id] = lease
            self._record_event("lease.acquired", lease)
            return lease

    def renew_lease(self, payload: LeaseRenewRequest) -> Dict[str, Any]:
        now = self._utcnow()
        expires_at = now + timedelta(milliseconds=payload.ttl_ms)
        with self._lock:
            lease = self.leases.get(payload.lease_id)
            if lease is None:
                raise HTTPException(status_code=404, detail="lease_not_found")
            if lease["holder_node_id"] != payload.node_id:
                raise HTTPException(status_code=409, detail="lease_holder_mismatch")

            lease["expires_at"] = expires_at.isoformat()
            lease["renew_interval_ms"] = int(payload.ttl_ms / 2)
            self._record_event("lease.renewed", lease)
            return lease


CONTROL_PLANE = NodeDBControlPlane()


def reset_control_plane() -> None:
    CONTROL_PLANE.reset()


@router.post("/v1/nodes/heartbeat")
def heartbeat(payload: NodeHeartbeat):
    node = CONTROL_PLANE.heartbeat(payload)
    return {"ok": True, "node": node}


@router.get("/v1/nodes")
def list_nodes(refresh: bool = True):
    if refresh:
        CONTROL_PLANE.refresh_status()
    return {
        "ok": True,
        "nodes": list(CONTROL_PLANE.nodes.values()),
        "count": len(CONTROL_PLANE.nodes),
    }


@router.post("/v1/leases/acquire")
def acquire_lease(payload: LeaseAcquireRequest):
    lease = CONTROL_PLANE.acquire_lease(payload)
    return {"ok": True, "lease": lease}


@router.post("/v1/leases/renew")
def renew_lease(payload: LeaseRenewRequest):
    lease = CONTROL_PLANE.renew_lease(payload)
    return {"ok": True, "lease": lease}


@router.get("/v1/leases/{lease_id}")
def get_lease(lease_id: str):
    lease = CONTROL_PLANE.leases.get(lease_id)
    if lease is None:
        raise HTTPException(status_code=404, detail="lease_not_found")
    return {"ok": True, "lease": lease}


@router.get("/v1/topology/events")
def list_topology_events(limit: int = 100):
    limit = max(1, min(limit, 500))
    events = CONTROL_PLANE.topology_events[-limit:]
    return {"ok": True, "events": events, "count": len(events)}


@router.get("/v1/nodedb/wal")
def read_nodedb_wal(limit: int = 100):
    events = CONTROL_PLANE.read_wal(limit=limit)
    return {"ok": True, "events": events, "count": len(events)}
