from fastapi.testclient import TestClient

from apps.api.master import app


client = TestClient(app)


def test_cloud_outage_switches_to_sovereign() -> None:
    response = client.post(
        "/v1/sovereign/evaluate",
        json={"cloud_reachable": False, "cloud_latency_ms": 0.0},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["state"]["mode"] == "sovereign"
    assert payload["state"]["local_llm_active"] is True
    assert payload["state"]["node_db_mode"] == "local"


def test_sovereign_resync_replays_events() -> None:
    switch = client.post(
        "/v1/sovereign/switch",
        json={"mode": "sovereign", "reason": "test_mode"},
    )
    assert switch.status_code == 200

    event_push = client.post(
        "/v1/sovereign/events",
        json={"event_type": "clx.job.completed", "payload": {"job_id": "job-1"}},
    )
    assert event_push.status_code == 200

    replay = client.post("/v1/sovereign/resync?max_events=50")
    assert replay.status_code == 200
    body = replay.json()
    assert body["resync"]["events_replayed"] >= 1
    assert body["resync"]["idempotent"] is True
