from fastapi.testclient import TestClient

from apps.api.master import app


client = TestClient(app)


def test_industrial_data_refuses_fabricated_sensor_values() -> None:
    response = client.get("/industrial/data")

    assert response.status_code == 503
    detail = response.json()["detail"]
    assert detail["error"] == "industrial_sensor_source_unconfigured"
    assert "No fake ever" in detail["message"]
    assert "host_metrics" in detail
    assert "temperature" not in detail
    assert "pressure" not in detail
    assert "humidity" not in detail
