from fastapi.testclient import TestClient

from apps.api.master import app


client = TestClient(app)


def test_benchmark_targets_exposed() -> None:
    response = client.get("/v1/benchmarks/targets")
    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert "intra_node" in payload["targets"]


def test_benchmark_run_reports_standard_fields() -> None:
    response = client.post(
        "/v1/benchmarks/run",
        json={
            "test_name": "intra_node",
            "messages": 10,
            "target_url": "http://127.0.0.1:65534/not-reachable",
            "timeout_ms": 100,
            "method": "GET",
        },
    )
    assert response.status_code == 200
    result = response.json()["result"]
    for field in (
        "test_name",
        "messages",
        "p50_ms",
        "p95_ms",
        "p99_ms",
        "throughput_msg_sec",
        "errors",
        "timestamp",
    ):
        assert field in result
    assert result["messages"] == 10
    assert result["errors"] >= 1


def test_benchmark_threshold_evaluation_fails_when_errors_high() -> None:
    response = client.post(
        "/v1/benchmarks/evaluate",
        json={
            "result": {
                "test_name": "intra_node",
                "messages": 10,
                "p50_ms": 1.0,
                "p95_ms": 5.0,
                "p99_ms": 8.0,
                "throughput_msg_sec": 1000.0,
                "errors": 2,
                "timestamp": "2026-05-27T12:00:00Z",
            },
            "thresholds": {
                "p95_ms_max": 10.0,
                "p99_ms_max": 10.0,
                "error_count_max": 0,
            },
        },
    )
    assert response.status_code == 200
    evaluation = response.json()["evaluation"]
    assert evaluation["passed"] is False
    assert "errors>0" in evaluation["failures"]
