from fastapi.testclient import TestClient

from apps.api.master import app
from apps.api.modules.nodedb_control_plane import reset_control_plane


client = TestClient(app)


def setup_function() -> None:
    reset_control_plane()


def test_heartbeat_expiry_transitions_to_offline() -> None:
    response = client.post(
        "/v1/nodes/heartbeat",
        json={
            "node_id": "edge-1",
            "status": "healthy",
            "latency_ms": 7.5,
            "capabilities": ["sensor", "mesh"],
            "heartbeat_at": "2000-01-01T00:00:00Z",
        },
    )
    assert response.status_code == 200

    nodes = client.get("/v1/nodes?refresh=true")
    assert nodes.status_code == 200
    payload = nodes.json()
    assert payload["count"] == 1
    assert payload["nodes"][0]["node_id"] == "edge-1"
    assert payload["nodes"][0]["status"] == "offline"


def test_lease_contention_returns_conflict() -> None:
    first = client.post(
        "/v1/leases/acquire",
        json={"lease_id": "global-leader", "node_id": "node-a", "ttl_ms": 10000},
    )
    assert first.status_code == 200
    first_token = first.json()["lease"]["fencing_token"]
    assert first_token == 1

    second = client.post(
        "/v1/leases/acquire",
        json={"lease_id": "global-leader", "node_id": "node-b", "ttl_ms": 10000},
    )
    assert second.status_code == 409
    detail = second.json()["detail"]
    assert detail["error"] == "lease_conflict"
    assert detail["holder_node_id"] == "node-a"
