import sys
import types
from typing import Any

from fastapi import FastAPI
from fastapi.testclient import TestClient

# Stub optional reporting dependencies so router import works in lean test env.
ultra_reporting_stub: Any = types.ModuleType("ultra_reporting")


class _DummyExporter:
    def __init__(self, *args, **kwargs) -> None:
        pass


class _DummyMetricsSnapshot:
    def __init__(self, *args, **kwargs) -> None:
        pass


ultra_reporting_stub.UltraExcelExporter = _DummyExporter
ultra_reporting_stub.UltraPowerPointGenerator = _DummyExporter
ultra_reporting_stub.UltraReportGenerator = _DummyExporter
ultra_reporting_stub.MetricsSnapshot = _DummyMetricsSnapshot
sys.modules.setdefault("ultra_reporting", ultra_reporting_stub)

from apps.api.reporting_api import router as reporting_router


app = FastAPI()
app.include_router(reporting_router)
client = TestClient(app)


def test_reporting_dashboard_requires_real_sources() -> None:
    response = client.get("/api/reporting/dashboard")

    assert response.status_code == 503
    detail = response.json()["detail"]
    assert detail["error"] == "real_reporting_source_unconfigured"
    assert detail["endpoint"] == "/api/reporting/dashboard"
    assert "No fake ever" in detail["message"]


def test_reporting_export_excel_requires_real_sources() -> None:
    response = client.get("/api/reporting/export-excel")

    assert response.status_code == 503
    detail = response.json()["detail"]
    assert detail["error"] == "real_reporting_source_unconfigured"
    assert detail["endpoint"] == "/api/reporting/export-excel"
    assert "required_sources" in detail
