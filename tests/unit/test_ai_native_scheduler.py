from fastapi.testclient import TestClient

from apps.api.master import app
from apps.api.modules.nodedb_control_plane import reset_control_plane
from apps.api.modules.sovereign_mode import STATE as SOVEREIGN_STATE


client = TestClient(app)


def setup_function() -> None:
    reset_control_plane()
    SOVEREIGN_STATE.switch("normal", "test_reset")


def _payload(policy_mode: str = "normal") -> dict:
    return {
        "scheduling": {
            "request_id": "req-1",
            "trace_id": "trace-1",
            "latency_budget_ms": 100,
            "privacy_level": "high",
            "cost_sensitivity": 0.6,
            "model_size_required": "medium",
            "compute_intensity": 0.5,
            "data_location": "edge",
            "task_type": "reasoning",
            "required_capabilities": ["llm"],
            "policy": {
                "mode": policy_mode,
                "w_latency": 0.3,
                "w_privacy": 0.2,
                "w_cost": 0.15,
                "w_load": 0.15,
                "w_trust": 0.1,
                "w_capability": 0.1,
            },
        },
        "candidates": [
            {
                "node_id": "edge-a",
                "runtime": "edge",
                "model": "local-llm",
                "latency_ms": 25,
                "estimated_cost": 0.1,
                "queue_depth": 10,
                "trust_score": 0.9,
                "capabilities": ["llm", "sensor"],
                "available": True,
            },
            {
                "node_id": "cloud-a",
                "runtime": "cloud",
                "model": "cloud-llm",
                "latency_ms": 40,
                "estimated_cost": 0.5,
                "queue_depth": 5,
                "trust_score": 0.95,
                "capabilities": ["llm"],
                "available": True,
            },
        ],
    }


def test_scheduler_enforces_high_privacy_prefers_edge() -> None:
    response = client.post("/v1/scheduler/decide", json=_payload())
    assert response.status_code == 200
    decision = response.json()["decision"]
    assert decision["target_runtime"] == "edge"
    assert "score_breakdown" in decision


def test_scheduler_decision_is_auditable() -> None:
    _ = client.post("/v1/scheduler/decide", json=_payload())
    history = client.get("/v1/scheduler/decisions?limit=5")
    assert history.status_code == 200
    decisions = history.json()["decisions"]
    assert len(decisions) >= 1
    assert "trace_id" in decisions[-1]
    assert "reason" in decisions[-1]


def test_scheduler_decide_auto_discovers_from_nodedb() -> None:
    heartbeat = client.post(
        "/v1/nodes/heartbeat",
        json={
            "node_id": "edge-auto",
            "role": "edge",
            "capabilities": ["llm", "sensor"],
            "status": "healthy",
            "latency_ms": 12,
            "queue_depth": 3,
        },
    )
    assert heartbeat.status_code == 200

    payload = _payload(policy_mode="edge-first")
    response = client.post(
        "/v1/scheduler/decide-auto",
        json={"scheduling": payload["scheduling"]},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["decision"]["candidate_source"] == "nodedb"
    assert body["decision"]["target_node_id"] == "edge-auto"


def test_scheduler_decide_auto_filters_cloud_when_sovereign_active() -> None:
    edge_heartbeat = client.post(
        "/v1/nodes/heartbeat",
        json={
            "node_id": "edge-sovereign",
            "role": "edge",
            "capabilities": ["llm"],
            "status": "healthy",
            "latency_ms": 18,
            "queue_depth": 2,
        },
    )
    cloud_heartbeat = client.post(
        "/v1/nodes/heartbeat",
        json={
            "node_id": "cloud-sovereign",
            "role": "cloud",
            "capabilities": ["llm"],
            "status": "healthy",
            "latency_ms": 5,
            "queue_depth": 1,
        },
    )
    assert edge_heartbeat.status_code == 200
    assert cloud_heartbeat.status_code == 200

    switch = client.post(
        "/v1/sovereign/switch",
        json={"mode": "sovereign", "reason": "test_filter"},
    )
    assert switch.status_code == 200

    payload = _payload(policy_mode="normal")
    payload["scheduling"]["privacy_level"] = "medium"
    response = client.post(
        "/v1/scheduler/decide-auto",
        json={"scheduling": payload["scheduling"]},
    )
    assert response.status_code == 200
    decision = response.json()["decision"]
    assert decision["sovereign_mode"] == "sovereign"
    assert decision["target_node_id"] == "edge-sovereign"
    assert all(
        candidate["runtime"] != "cloud" for candidate in decision["ranked_candidates"]
    )
