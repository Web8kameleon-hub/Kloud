# -*- coding: utf-8 -*-
"""
KLOUD FABRIC CORE
=================
Sovereign Intelligence Fabric — 6 nyje globale të lidhura.

Rolet:
  ocean-hq    → CPX62   178.105.52.245  Nuremberg   (Ocean Core / Control Brain)
  compute-fsk → CCX33   91.98.47.131    Falkenstein  (Heavy AI / Inference Engine)
  failover-nbg→ CX43    46.224.203.89   Nuremberg    (Failover / Health Mirror)
  edge-hel    → CX23    37.27.216.254   Helsinki     (EU North Edge)
  edge-ash    → CPX21   5.161.114.189   Ashburn      (US East Edge)
  edge-sin    → CPX22   5.223.75.178    Singapore    (Asia Edge)

Port default fabric-api: 18800
"""

from __future__ import annotations

import asyncio
import logging
import os
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger("KloudFabric")

# ── Fabric node topology ─────────────────────────────────────────────────────

FABRIC_NODES: List[Dict[str, Any]] = [
    {
        "id": "ocean-hq",
        "role": "brain",
        "description": "Ocean Core — Control Brain, API Gateway, ASI Trinity Coordinator",
        "ip": os.getenv("FABRIC_OCEAN_HQ_IP", "178.105.52.245"),
        "port": int(os.getenv("FABRIC_OCEAN_HQ_PORT", "19080")),
        "location": "Nuremberg, DE",
        "provider": "Hetzner CPX62",
        "resources": {"vcpu": 16, "ram_gb": 32, "disk_gb": 640},
        "services": [
            "ocean-core",
            "api-gateway",
            "asi-trinity",
            "bti",
            "das",
            "pfd",
            "billing-webhooks",
            "user-sessions",
            "db-connections",
            "control-surface",
        ],
        "health_path": "/status",
        "is_hq": True,
    },
    {
        "id": "compute-fsk",
        "role": "compute",
        "description": "Compute Engine — Heavy AI Inference, ALBA/ALBI/JONA, Audio/EEG Pipelines",
        "ip": os.getenv("FABRIC_COMPUTE_FSK_IP", "91.98.47.131"),
        "port": int(os.getenv("FABRIC_COMPUTE_FSK_PORT", "19080")),
        "location": "Falkenstein, DE",
        "provider": "Hetzner CCX33",
        "resources": {"vcpu": 8, "ram_gb": 32, "disk_gb": 240},
        "services": [
            "alba",
            "albi",
            "jona",
            "audio-intelligence",
            "eeg-processing",
            "batch-jobs",
            "model-hosting",
            "heavy-inference",
        ],
        "health_path": "/status",
        "is_hq": False,
    },
    {
        "id": "failover-nbg",
        "role": "failover",
        "description": "Failover + Health Mirror — Ocean Core Backup, Telemetry Replication",
        "ip": os.getenv("FABRIC_FAILOVER_NBG_IP", "46.224.203.89"),
        "port": int(os.getenv("FABRIC_FAILOVER_NBG_PORT", "19080")),
        "location": "Nuremberg, DE",
        "provider": "Hetzner CX43",
        "resources": {"vcpu": 8, "ram_gb": 16, "disk_gb": 160},
        "services": [
            "ocean-core-failover",
            "health-mirror",
            "telemetry-replication",
            "backup-routing",
            "emergency-api",
        ],
        "health_path": "/status",
        "is_hq": False,
    },
    {
        "id": "edge-hel",
        "role": "edge",
        "description": "EU North Edge — Helsinki, serves Nordics, low-latency routing",
        "ip": os.getenv("FABRIC_EDGE_HEL_IP", "37.27.216.254"),
        "port": int(os.getenv("FABRIC_EDGE_HEL_PORT", "19080")),
        "location": "Helsinki, FI",
        "provider": "Hetzner CX23",
        "resources": {"vcpu": 2, "ram_gb": 4, "disk_gb": 40},
        "services": ["edge-routing", "inference-cache", "lightweight-telemetry"],
        "health_path": "/status",
        "is_hq": False,
        "geo": {
            "region": "eu-north",
            "countries": ["FI", "SE", "NO", "EE", "LV", "LT"],
        },
    },
    {
        "id": "edge-ash",
        "role": "edge",
        "description": "US East Edge — Ashburn VA, serves Americas",
        "ip": os.getenv("FABRIC_EDGE_ASH_IP", "5.161.114.189"),
        "port": int(os.getenv("FABRIC_EDGE_ASH_PORT", "19080")),
        "location": "Ashburn, VA, US",
        "provider": "Hetzner CPX21",
        "resources": {"vcpu": 2, "ram_gb": 4, "disk_gb": 80},
        "services": ["edge-routing", "inference-cache", "lightweight-telemetry"],
        "health_path": "/status",
        "is_hq": False,
        "geo": {"region": "us-east", "countries": ["US", "CA", "MX", "BR"]},
    },
    {
        "id": "edge-sin",
        "role": "edge",
        "description": "Asia Edge — Singapore, serves Asia-Pacific",
        "ip": os.getenv("FABRIC_EDGE_SIN_IP", "5.223.75.178"),
        "port": int(os.getenv("FABRIC_EDGE_SIN_PORT", "19080")),
        "location": "Singapore, SG",
        "provider": "Hetzner CPX22",
        "resources": {"vcpu": 3, "ram_gb": 4, "disk_gb": 80},
        "services": ["edge-routing", "inference-cache", "lightweight-telemetry"],
        "health_path": "/status",
        "is_hq": False,
        "geo": {
            "region": "ap-southeast",
            "countries": ["SG", "MY", "ID", "AU", "JP", "KR"],
        },
    },
]

# Geo-routing table: region → preferred node ids (ordered)
GEO_ROUTING: Dict[str, List[str]] = {
    "eu-north": ["edge-hel", "ocean-hq", "failover-nbg"],
    "eu-central": ["ocean-hq", "failover-nbg", "compute-fsk"],
    "eu-west": ["ocean-hq", "failover-nbg"],
    "us-east": ["edge-ash"],
    "us-west": ["edge-ash"],
    "ap-southeast": ["edge-sin"],
    "ap-northeast": ["edge-sin"],
    "default": ["ocean-hq", "failover-nbg"],
}

# ── Node status store ─────────────────────────────────────────────────────────


@dataclass
class NodeStatus:
    node_id: str
    healthy: bool = False
    latency_ms: float = 0.0
    last_check: float = field(default_factory=time.time)
    last_error: Optional[str] = None
    consecutive_failures: int = 0
    # Rust StatusResponse fields
    node_state: str = "Offline"
    tide: str = "Low"
    ndb_score: float = 0.0
    ndb_delta: float = 0.0
    ndb_threshold: float = 0.65
    active_peers: int = 0
    bandwidth_kbps: float = 0.0
    load: float = 0.0
    stigma_state: str = "UNKNOWN"

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["last_check_iso"] = datetime.fromtimestamp(
            self.last_check, tz=timezone.utc
        ).isoformat()
        return d


class KloudFabric:
    """
    Central fabric manager.
    - Mban topologjinë e të gjitha nyjeve
    - Kryen health-checks asinkrone
    - Ruan telemetry BTI/DAS/PFD nga nyjet
    - Jep routing recommendations sipas geo/health
    """

    def __init__(self) -> None:
        self._nodes: Dict[str, Dict[str, Any]] = {n["id"]: n for n in FABRIC_NODES}
        self._status: Dict[str, NodeStatus] = {
            n["id"]: NodeStatus(n["id"]) for n in FABRIC_NODES
        }
        self._telemetry: List[Dict[str, Any]] = []
        self._hq_id = "ocean-hq"
        self._health_task: Optional[asyncio.Task] = None  # type: ignore[type-arg]

    # ── Topology ─────────────────────────────────────────────────────────────

    def get_topology(self) -> Dict[str, Any]:
        return {
            "nodes": [
                {**n, "status": self._status[n["id"]].to_dict()}
                for n in self._nodes.values()
            ],
            "routing": GEO_ROUTING,
            "hq": self._hq_id,
            "fabric_version": "1.0.0",
            "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        }

    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        node = self._nodes.get(node_id)
        if not node:
            return None
        return {**node, "status": self._status[node_id].to_dict()}

    def list_nodes(self, role: Optional[str] = None) -> List[Dict[str, Any]]:
        nodes = self._nodes.values()
        if role:
            nodes = [n for n in nodes if n["role"] == role]  # type: ignore[assignment]
        return [{**n, "status": self._status[n["id"]].to_dict()} for n in nodes]

    # ── Routing ──────────────────────────────────────────────────────────────

    def route(
        self, region: str = "default", service: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Kthen nyjen optimale për një region dhe (opsionalisht) service.
        Merr parasysh geo-routing dhe health aktual.
        """
        candidates = GEO_ROUTING.get(region, GEO_ROUTING["default"])

        # Nëse kërkohet heavy-inference shko te compute-fsk direkt
        if service in ("alba", "albi", "jona", "audio", "eeg", "inference", "batch"):
            candidates = ["compute-fsk"] + candidates

        for node_id in candidates:
            st = self._status.get(node_id)
            if st and st.healthy:
                node = self._nodes[node_id]
                return {
                    "node_id": node_id,
                    "ip": node["ip"],
                    "port": node["port"],
                    "role": node["role"],
                    "location": node["location"],
                    "latency_ms": st.latency_ms,
                    "region": region,
                }

        # Fallback: HQ gjithmonë
        hq = self._nodes[self._hq_id]
        return {
            "node_id": self._hq_id,
            "ip": hq["ip"],
            "port": hq["port"],
            "role": "brain",
            "location": hq["location"],
            "latency_ms": self._status[self._hq_id].latency_ms,
            "region": region,
            "fallback": True,
        }

    def best_for_compute(self) -> Dict[str, Any]:
        """Kthen compute-fsk nëse healthy, ose ocean-hq si fallback."""
        return self.route(region="eu-central", service="inference")

    # ── Health checks ────────────────────────────────────────────────────────

    async def check_node(self, node_id: str) -> NodeStatus:
        node = self._nodes.get(node_id)
        if not node:
            return NodeStatus(node_id, healthy=False, last_error="unknown node")

        url = f"http://{node['ip']}:{node['port']}{node['health_path']}"
        st = self._status[node_id]
        t0 = time.monotonic()
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(url)
            latency = round((time.monotonic() - t0) * 1000, 2)
            st.last_check = time.time()
            if resp.status_code < 500:
                st.healthy = True
                st.consecutive_failures = 0
                st.last_error = None
                try:
                    data = resp.json()
                    # Parse Rust StatusResponse
                    st.node_state = data.get("state", "Unknown")
                    st.tide = data.get("tide", "Low")
                    st.ndb_score = float(data.get("ndb_score", 0.0))
                    st.ndb_delta = float(data.get("ndb_delta", 0.0))
                    st.ndb_threshold = float(data.get("ndb_threshold", 0.65))
                    m = data.get("metrics", {})
                    st.active_peers = int(m.get("active_peers", 0))
                    st.bandwidth_kbps = float(m.get("bandwidth_kbps", 0.0))
                    st.load = float(m.get("load", 0.0))
                    # Use Rust-reported avg_latency if available, else HTTP round-trip
                    rust_lat = float(m.get("avg_latency_ms", 0))
                    st.latency_ms = rust_lat if rust_lat > 0 else latency
                    # STIGMA: fetch from resonant/status only if node is HQ to avoid N*M calls
                    if node.get("is_hq"):
                        await self._fetch_stigma(node, st)
                except Exception:
                    st.latency_ms = latency  # still healthy, just no JSON
            else:
                st.healthy = False
                st.consecutive_failures += 1
                st.last_error = f"HTTP {resp.status_code}"
                st.latency_ms = latency
                st.node_state = "Degraded"
        except Exception as exc:
            st.healthy = False
            st.latency_ms = 0.0
            st.last_check = time.time()
            st.consecutive_failures += 1
            st.last_error = str(exc)[:120]
            st.node_state = "Offline"

        return st

    async def _fetch_stigma(self, node: Dict[str, Any], st: NodeStatus) -> None:
        """Kërkon /resonant/status nga nyja HQ për të marrë STIGMA trace_state."""
        url = f"http://{node['ip']}:{node['port']}/resonant/status"
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                st.stigma_state = data.get("trace_state", "UNKNOWN")
        except Exception:
            pass  # non-critical — STIGMA stays UNKNOWN if unreachable

    async def check_all(self) -> Dict[str, NodeStatus]:
        tasks = [self.check_node(nid) for nid in self._nodes]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return {
            nid: r for nid, r in zip(self._nodes, results) if isinstance(r, NodeStatus)
        }

    async def start_health_loop(self, interval_s: int = 30) -> None:
        """Kryen health-checks çdo `interval_s` sekonda në background."""
        while True:
            try:
                await self.check_all()
                logger.info(
                    "[FABRIC] Health cycle complete: %s",
                    {nid: s.healthy for nid, s in self._status.items()},
                )
            except Exception as exc:
                logger.warning("[FABRIC] Health loop error: %s", exc)
            await asyncio.sleep(interval_s)

    # ── Telemetry ────────────────────────────────────────────────────────────

    def ingest_telemetry(self, node_id: str, payload: Dict[str, Any]) -> None:
        """
        Preson telemetry nga çdo nyje (BTI, DAS, PFD).
        Ruan në ring buffer (mban max 10_000 ngjarje).
        """
        entry = {
            "node_id": node_id,
            "ts": datetime.now(tz=timezone.utc).isoformat(),
            **payload,
        }
        self._telemetry.append(entry)
        if len(self._telemetry) > 10_000:
            self._telemetry = self._telemetry[-10_000:]

    def get_telemetry(
        self, node_id: Optional[str] = None, limit: int = 100
    ) -> List[Dict[str, Any]]:
        data = self._telemetry
        if node_id:
            data = [e for e in data if e.get("node_id") == node_id]
        return data[-limit:]

    # ── Summary ──────────────────────────────────────────────────────────────

    def summary(self) -> Dict[str, Any]:
        healthy = sum(1 for s in self._status.values() if s.healthy)
        hq_st = self._status[self._hq_id]
        healthy_statuses = [s for s in self._status.values() if s.healthy]
        avg_ndb = (
            round(sum(s.ndb_score for s in healthy_statuses) / len(healthy_statuses), 4)
            if healthy_statuses
            else 0.0
        )
        # Determine dominant TIDE across healthy nodes
        tide_counts: Dict[str, int] = {}
        for s in healthy_statuses:
            tide_counts[s.tide] = tide_counts.get(s.tide, 0) + 1
        dominant_tide = (
            max(tide_counts, key=lambda k: tide_counts[k]) if tide_counts else "Low"
        )
        return {
            "total_nodes": len(self._nodes),
            "healthy_nodes": healthy,
            "unhealthy_nodes": len(self._nodes) - healthy,
            "fabric_health_pct": round(healthy / max(len(self._nodes), 1) * 100, 1),
            "hq": self._hq_id,
            "hq_healthy": hq_st.healthy,
            "hq_ndb_score": hq_st.ndb_score,
            "hq_tide": hq_st.tide,
            "hq_stigma_state": hq_st.stigma_state,
            "fabric_avg_ndb": avg_ndb,
            "fabric_tide": dominant_tide,
            "telemetry_events": len(self._telemetry),
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        }


# ── Singleton ────────────────────────────────────────────────────────────────

_fabric_instance: Optional[KloudFabric] = None


def get_fabric() -> KloudFabric:
    global _fabric_instance
    if _fabric_instance is None:
        _fabric_instance = KloudFabric()
    return _fabric_instance
