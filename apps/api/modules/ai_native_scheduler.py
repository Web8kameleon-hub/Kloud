from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Literal, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from apps.api.modules.nodedb_control_plane import CONTROL_PLANE
from apps.api.modules.sovereign_mode import STATE as SOVEREIGN_STATE

router = APIRouter(tags=["ai-native-scheduler"])

RuntimeType = Literal["edge", "cloud", "hybrid", "mesh"]
PolicyMode = Literal[
    "normal",
    "sovereign",
    "edge-first",
    "cloud-first",
    "cost-optimized",
    "latency-optimized",
]


class SchedulerPolicy(BaseModel):
    mode: PolicyMode = "normal"
    w_latency: float = 0.30
    w_privacy: float = 0.20
    w_cost: float = 0.15
    w_load: float = 0.15
    w_trust: float = 0.10
    w_capability: float = 0.10


class SchedulingRequest(BaseModel):
    request_id: str
    trace_id: str
    latency_budget_ms: float = Field(ge=1.0)
    privacy_level: Literal["low", "medium", "high", "sovereign"] = "medium"
    cost_sensitivity: float = Field(default=0.5, ge=0.0, le=1.0)
    model_size_required: Literal["small", "medium", "large"] = "medium"
    compute_intensity: float = Field(default=0.5, ge=0.0, le=1.0)
    data_location: str = "edge"
    task_type: str = "reasoning"
    required_capabilities: List[str] = Field(default_factory=list)
    policy: SchedulerPolicy = Field(default_factory=SchedulerPolicy)


class NodeCandidate(BaseModel):
    node_id: str
    runtime: RuntimeType
    model: str
    latency_ms: float = Field(ge=0.0)
    estimated_cost: float = Field(ge=0.0)
    queue_depth: int = Field(ge=0)
    trust_score: float = Field(default=1.0, ge=0.0, le=1.0)
    capabilities: List[str] = Field(default_factory=list)
    available: bool = True


class SchedulerEvaluateRequest(BaseModel):
    scheduling: SchedulingRequest
    candidates: List[NodeCandidate]


class SchedulerAutoRequest(BaseModel):
    scheduling: SchedulingRequest


class SchedulerState:
    def __init__(self) -> None:
        self._lock = Lock()
        self.decisions: List[Dict[str, Any]] = []
        self.wal_path = Path(
            os.getenv(
                "SCHEDULER_DECISION_LOG_PATH", "./storage/scheduler_decisions.jsonl"
            )
        ).resolve()
        self.wal_path.parent.mkdir(parents=True, exist_ok=True)

    def _utcnow(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _append_wal(self, entry: Dict[str, Any]) -> None:
        try:
            with self.wal_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except OSError:
            return

    def record(self, entry: Dict[str, Any]) -> None:
        with self._lock:
            self.decisions.append(entry)
            if len(self.decisions) > 5000:
                self.decisions = self.decisions[-5000:]
            self._append_wal(entry)

    def list_decisions(self, limit: int = 100) -> List[Dict[str, Any]]:
        with self._lock:
            limit = max(1, min(limit, 1000))
            return self.decisions[-limit:]


STATE = SchedulerState()


def _privacy_cost(req: SchedulingRequest, candidate: NodeCandidate) -> float:
    if req.privacy_level in ("high", "sovereign") and candidate.runtime == "cloud":
        return 1.0
    if req.privacy_level == "medium" and candidate.runtime == "cloud":
        return 0.5
    return 0.0


def _latency_cost(req: SchedulingRequest, candidate: NodeCandidate) -> float:
    over = max(0.0, candidate.latency_ms - req.latency_budget_ms)
    return min(1.0, over / req.latency_budget_ms)


def _load_cost(candidate: NodeCandidate) -> float:
    return min(1.0, candidate.queue_depth / 100.0)


def _trust_cost(candidate: NodeCandidate) -> float:
    return 1.0 - candidate.trust_score


def _capability_penalty(req: SchedulingRequest, candidate: NodeCandidate) -> float:
    if not req.required_capabilities:
        return 0.0
    missing = [
        cap for cap in req.required_capabilities if cap not in candidate.capabilities
    ]
    if not req.required_capabilities:
        return 0.0
    return len(missing) / float(len(req.required_capabilities))


def _monetary_cost(req: SchedulingRequest, candidate: NodeCandidate) -> float:
    raw = min(1.0, candidate.estimated_cost)
    return raw * req.cost_sensitivity


def _is_candidate_allowed(req: SchedulingRequest, candidate: NodeCandidate) -> bool:
    sovereign_mode = SOVEREIGN_STATE.snapshot().get("mode") == "sovereign"
    if sovereign_mode and candidate.runtime == "cloud":
        return False
    if req.policy.mode == "sovereign" and candidate.runtime == "cloud":
        return False
    if req.privacy_level == "sovereign" and candidate.runtime == "cloud":
        return False
    if req.policy.mode == "edge-first" and candidate.runtime == "cloud":
        return False
    if not candidate.available:
        return False
    return True


def _default_model_for_node(req: SchedulingRequest, node: Dict[str, Any]) -> str:
    capabilities = set(node.get("capabilities") or [])
    if "vision" in capabilities:
        return "vision-core"
    if req.task_type in {"mesh", "control"} or "mesh" in capabilities:
        return "mesh-agent"
    if node.get("role") == "cloud":
        return "cloud-llm"
    return "local-llm"


def _default_runtime_for_node(node: Dict[str, Any]) -> RuntimeType:
    role = str(node.get("role") or "edge").lower()
    if role in {"cloud", "gateway", "scheduler"}:
        return "cloud"
    if role in {"mesh", "sensor"}:
        return "mesh"
    return "edge"


def discover_candidates(req: SchedulingRequest) -> List[NodeCandidate]:
    CONTROL_PLANE.refresh_status()
    discovered: List[NodeCandidate] = []
    for node in CONTROL_PLANE.nodes.values():
        runtime = _default_runtime_for_node(node)
        discovered.append(
            NodeCandidate(
                node_id=node["node_id"],
                runtime=runtime,
                model=_default_model_for_node(req, node),
                latency_ms=float(node.get("latency_ms") or 0.0),
                estimated_cost=0.6 if runtime == "cloud" else 0.1,
                queue_depth=int(node.get("queue_depth") or 0),
                trust_score=0.2
                if node.get("status") == "offline"
                else (0.5 if node.get("status") == "degraded" else 0.95),
                capabilities=list(node.get("capabilities") or []),
                available=node.get("status") in {"healthy", "degraded"},
            )
        )
    return discovered


def evaluate_candidate(
    req: SchedulingRequest, candidate: NodeCandidate
) -> Dict[str, Any]:
    breakdown = {
        "latency_cost": _latency_cost(req, candidate),
        "privacy_cost": _privacy_cost(req, candidate),
        "monetary_cost": _monetary_cost(req, candidate),
        "load_cost": _load_cost(candidate),
        "trust_cost": _trust_cost(candidate),
        "capability_penalty": _capability_penalty(req, candidate),
    }

    score = (
        req.policy.w_latency * breakdown["latency_cost"]
        + req.policy.w_privacy * breakdown["privacy_cost"]
        + req.policy.w_cost * breakdown["monetary_cost"]
        + req.policy.w_load * breakdown["load_cost"]
        + req.policy.w_trust * breakdown["trust_cost"]
        + req.policy.w_capability * breakdown["capability_penalty"]
    )

    return {
        "node_id": candidate.node_id,
        "runtime": candidate.runtime,
        "model": candidate.model,
        "score": round(score, 6),
        "score_breakdown": breakdown,
    }


def _make_decision(
    req: SchedulingRequest, candidates: List[NodeCandidate], discovery_mode: str
) -> Dict[str, Any]:
    allowed = [c for c in candidates if _is_candidate_allowed(req, c)]
    if not allowed:
        raise HTTPException(status_code=422, detail="no_eligible_candidates")

    evaluated = [evaluate_candidate(req, candidate) for candidate in allowed]
    winner = min(evaluated, key=lambda item: item["score"])

    decision = {
        "request_id": req.request_id,
        "trace_id": req.trace_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "target_node_id": winner["node_id"],
        "target_runtime": winner["runtime"],
        "target_model": winner["model"],
        "reason": f"min_score:{winner['score']}",
        "score_breakdown": winner["score_breakdown"],
        "ranked_candidates": sorted(evaluated, key=lambda item: item["score"]),
        "policy_mode": req.policy.mode,
        "sovereign_mode": SOVEREIGN_STATE.snapshot().get("mode"),
        "candidate_source": discovery_mode,
    }
    STATE.record(decision)
    return decision


@router.post("/v1/scheduler/decide")
def scheduler_decide(payload: SchedulerEvaluateRequest):
    decision = _make_decision(payload.scheduling, payload.candidates, "provided")
    return {"ok": True, "decision": decision}


@router.post("/v1/scheduler/decide-auto")
def scheduler_decide_auto(payload: SchedulerAutoRequest):
    candidates = discover_candidates(payload.scheduling)
    decision = _make_decision(payload.scheduling, candidates, "nodedb")
    return {"ok": True, "decision": decision, "discovered_candidates": len(candidates)}


@router.get("/v1/scheduler/decisions")
def scheduler_decisions(limit: int = 100):
    return {"ok": True, "decisions": STATE.list_decisions(limit=limit)}
