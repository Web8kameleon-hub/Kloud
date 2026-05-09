from __future__ import annotations
import os, json, time, asyncio
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

from .telemetry_service import TelemetryService
from .alert_service import evaluate, notify

TOPOLOGY_FILE = os.getenv("MESH_TOPOLOGY_FILE", os.path.join(os.path.dirname(__file__), "topology.json"))

@dataclass
class Node:
    id: str
    name: str
    type: str = "generic"
    continent: str = "Global"
    status: str = "active"
    ip: Optional[str] = None
    hostname: Optional[str] = None
    apis: Dict[str, str] = field(default_factory=dict)
    metrics: Dict[str, Any] = field(default_factory=dict)
    last_update: float = field(default_factory=lambda: time.time())

@dataclass
class Edge:
    source: str
    target: str
    latency_ms: Optional[float] = None
    strength: Optional[float] = None
    updated_at: float = field(default_factory=lambda: time.time())

class MeshCore:
    """
    Kloud Mesh Core — truri qendror i rrjetit.
    - Menaxhon nyjet (nodes) dhe lidhjet (edges)
    - Ruajtje e gjendjes: Redis via TelemetryService + file topology.json (persistent)
    - Pa simulime: pret telemetry reale nga node-t.
    """

    def __init__(self):
        self.telemetry = TelemetryService()
        self.nodes: Dict[str, Node] = {}
        self.edges: Dict[str, Edge] = {}  # key: f"{source}->{target}"
        self.health_score: float = 1.0
        self._load_topology()

    # ------------- Persistence -------------
    def _load_topology(self):
        if os.path.exists(TOPOLOGY_FILE):
            try:
                data = json.load(open(TOPOLOGY_FILE, "r", encoding="utf-8"))
                for n in data.get("nodes", []):
                    self.nodes[n["id"]] = Node(**n)
                for e in data.get("edges", []):
                    key = f'{e["source"]}->{e["target"]}'
                    self.edges[key] = Edge(**e)
            except Exception:
                # nëse file është korruptuar, e lëmë bosh
                self.nodes, self.edges = {}, {}

    def _save_topology(self):
        payload = {
            "nodes": [self._node_to_dict(n) for n in self.nodes.values()],
            "edges": [self._edge_to_dict(e) for e in self.edges.values()],
            "updated_at": time.time(),
            "health_score": self.health_score,
        }
        with open(TOPOLOGY_FILE, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

    # ------------- Node & Edge helpers -------------
    def _node_to_dict(self, n: Node) -> Dict[str, Any]:
        return {
            "id": n.id, "name": n.name, "type": n.type, "continent": n.continent,
            "status": n.status, "ip": n.ip, "hostname": n.hostname,
            "apis": n.apis, "metrics": n.metrics, "last_update": n.last_update,
        }

    def _edge_to_dict(self, e: Edge) -> Dict[str, Any]:
        return {
            "source": e.source, "target": e.target,
            "latency_ms": e.latency_ms, "strength": e.strength,
            "updated_at": e.updated_at,
        }

    # ------------- Public API -------------
    def register_node(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        node_id = payload.get("id") or payload.get("node") or "unknown"
        node = self.nodes.get(node_id)
        if node is None:
            node = Node(
                id=node_id,
                name=payload.get("name", node_id),
                type=payload.get("type", "generic"),
                continent=payload.get("continent", "Global"),
                status=payload.get("status", "active"),
                ip=payload.get("ip"),
                hostname=payload.get("hostname"),
                apis=payload.get("apis", {}),
                metrics=payload.get("metrics", {}),
            )
            self.nodes[node_id] = node
        else:
            # update meta
            node.name = payload.get("name", node.name)
            node.type = payload.get("type", node.type)
            node.continent = payload.get("continent", node.continent)
            node.status = payload.get("status", node.status)
            node.ip = payload.get("ip", node.ip)
            node.hostname = payload.get("hostname", node.hostname)
            node.apis = payload.get("apis", node.apis)
            node.metrics = payload.get("metrics", node.metrics)
            node.last_update = time.time()

        # persist and propagate to telemetry store
        rec = self.telemetry.save(node_id, self._node_to_dict(node))
        self._recalculate_health()
        self._save_topology()
        return rec

    def update_status(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        node_id = payload.get("id") or payload.get("node") or "unknown"
        if node_id not in self.nodes:
            # auto-create on first status push
            self.register_node({"id": node_id, "name": node_id})

        node = self.nodes[node_id]
        if "status" in payload:
            node.status = payload["status"]
        if "metrics" in payload:
            node.metrics = payload["metrics"]
        if "hostname" in payload:
            node.hostname = payload["hostname"]
        if "ip" in payload:
            node.ip = payload["ip"]
        node.last_update = time.time()

        rec = self.telemetry.save(node_id, self._node_to_dict(node))

        # alerts (cpu/ram/disk/latency)
        alerts = evaluate(rec)
        if alerts:
            notify(rec, alerts)

        self._recalculate_health()
        self._save_topology()
        return rec

    def remove_node(self, node_id: str) -> bool:
        removed = bool(self.nodes.pop(node_id, None))
        # fshi edges e lidhura
        to_del = [k for k in self.edges if k.startswith(f"{node_id}->") or k.endswith(f"->{node_id}")]
        for k in to_del:
            self.edges.pop(k, None)
        self._recalculate_health()
        self._save_topology()
        return removed

    def upsert_edge(self, source: str, target: str, latency_ms: Optional[float] = None, strength: Optional[float] = None) -> Dict[str, Any]:
        key = f"{source}->{target}"
        edge = self.edges.get(key)
        if edge is None:
            edge = Edge(source=source, target=target, latency_ms=latency_ms, strength=strength)
            self.edges[key] = edge
        else:
            edge.latency_ms = latency_ms if latency_ms is not None else edge.latency_ms
            edge.strength = strength if strength is not None else edge.strength
            edge.updated_at = time.time()
        self._save_topology()
        return self._edge_to_dict(edge)

    def nodes_snapshot(self) -> List[Dict[str, Any]]:
        # kombino këndvështrimin e Telemetry (Redis/memory) me cache lokale
        return self.telemetry.get_all()

    def topology(self) -> Dict[str, Any]:
        return {
            "nodes": [self._node_to_dict(n) for n in self.nodes.values()],
            "edges": [self._edge_to_dict(e) for e in self.edges.values()],
            "health_score": self.health_score,
            "updated_at": time.time(),
        }

    # ------------- Health -------------
    def _recalculate_health(self):
        # health bazuar te: online %, latency, CPU/RAM/Disk pragjet
        if not self.nodes:
            self.health_score = 1.0
            return

        ONLINE_WEIGHT = 0.4
        PERF_WEIGHT   = 0.4
        LAT_WEIGHT    = 0.2

        # online ratio
        online = sum(1 for n in self.nodes.values() if n.status == "active")
        online_ratio = online / max(1, len(self.nodes))

        # performance (cpu/ram/disk) — penalitete nëse kalojnë pragjet
        perf_score_acc = 0.0
        for n in self.nodes.values():
            m = n.metrics or {}
            cpu = float(m.get("cpu", 0.0))
            ram = float(m.get("ram", 0.0))
            disk = float(m.get("disk", 0.0))
            # 1.0 perfect; penalitete lineare
            s = 1.0
            if cpu > 85: s -= min((cpu - 85) / 30, 1.0) * 0.34
            if ram > 85: s -= min((ram - 85) / 30, 1.0) * 0.33
            if disk > 90: s -= min((disk - 90) / 10, 1.0) * 0.33
            perf_score_acc += max(0.0, s)
        perf_score = perf_score_acc / max(1, len(self.nodes))

        # latency score (sa më ulët, aq më mirë)
        lat_scores = []
        for n in self.nodes.values():
            m = n.metrics or {}
            lat = m.get("latency_ms")
            if lat is None: continue
            s = 1.0
            if lat > 250: s -= min((lat - 250) / 500, 1.0)  # 250–750ms → 0–1 penalitet
            lat_scores.append(max(0.0, s))
        latency_score = (sum(lat_scores) / len(lat_scores)) if lat_scores else 1.0

        self.health_score = round(
            ONLINE_WEIGHT * online_ratio +
            PERF_WEIGHT   * perf_score +
            LAT_WEIGHT    * latency_score, 3
        )

    # ------------- Security hooks (opsionale) -------------
    def verify_api_key(self, key: Optional[str]) -> bool:
        """Hook i thjeshtë API key. Përdose në server.py middleware-in."""
        required = os.getenv("MESH_API_KEY")
        if not required:
            return True  # nëse s’është vendosur, mos e blloko
        return key == required



