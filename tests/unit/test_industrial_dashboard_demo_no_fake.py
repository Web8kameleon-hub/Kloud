from fastapi import FastAPI
from fastapi.testclient import TestClient

from apps.api.industrial_dashboard_demo import router as demo_router


app = FastAPI()
app.include_router(demo_router)
client = TestClient(app)


def test_demo_data_sources_disabled_until_real_source() -> None:
    response = client.get("/api/data-sources")

    assert response.status_code == 503
    detail = response.json()["detail"]
    assert detail["error"] == "demo_data_unconfigured"
    assert detail["endpoint"] == "/api/data-sources"
    assert "No fake ever" in detail["message"]


def test_demo_bulk_collection_disabled_until_real_source() -> None:
    response = client.post(
        "/api/start-bulk-collection",
        json={"dataset": "industrial.stream.v1"},
    )

    assert response.status_code == 503
    detail = response.json()["detail"]
    assert detail["error"] == "demo_data_unconfigured"
    assert detail["endpoint"] == "/api/start-bulk-collection"
