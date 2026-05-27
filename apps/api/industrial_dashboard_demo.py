from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, NoReturn, Optional
import time


router = APIRouter()


def _raise_no_fake_unavailable(endpoint: str) -> NoReturn:
    raise HTTPException(
        status_code=503,
        detail={
            "error": "demo_data_unconfigured",
            "endpoint": endpoint,
            "message": "No fake ever: demo dashboard data is disabled until a real telemetry source is configured.",
            "expected_sources": [
                "prometheus",
                "victoriametrics",
                "postgres",
                "redis",
                "device_ingest",
            ],
            "timestamp": time.time(),
        },
    )


class DataSource(BaseModel):
    name: str
    status: str
    records: int
    size_gb: float
    throughput: str
    location: str
    health: int
    uptime: float
    error_rate: float
    last_updated: str
    state: str


class ActivityLogEntry(BaseModel):
    time: str
    type: str
    source: str
    message: str


class BulkCollectionRequest(BaseModel):
    dataset: str = Field(..., description="Dataset identifier to collect")
    priority: str = Field("normal", pattern=r"^(low|normal|high)$")
    retention_hours: int = Field(24, ge=1, le=720)
    notes: Optional[str] = None


class BulkCollectionResponse(BaseModel):
    success: bool
    message: str
    collection_id: str
    started_at: float


class PerformanceMetrics(BaseModel):
    cpu_usage: float
    storage_used_tb: float
    storage_total_tb: float
    storage_percent: float
    network_throughput: float
    network_percent: float
    error_rate: float
    system_load: float
    connections: int
    data_rate: float


class SystemStatus(BaseModel):
    core_services: str
    network: str
    maintenance: str
    data_integrity: str


class SimpleAlert(BaseModel):
    active: bool
    message: str


@router.get("/api/data-sources", response_model=List[DataSource])
def get_data_sources() -> List[DataSource]:
    _raise_no_fake_unavailable("/api/data-sources")


@router.get("/api/activity-log", response_model=List[ActivityLogEntry])
def get_activity_log() -> List[ActivityLogEntry]:
    _raise_no_fake_unavailable("/api/activity-log")


@router.post("/api/start-bulk-collection", response_model=BulkCollectionResponse)
def start_bulk_collection(payload: BulkCollectionRequest) -> BulkCollectionResponse:
    _raise_no_fake_unavailable("/api/start-bulk-collection")


@router.get("/api/performance-metrics", response_model=PerformanceMetrics)
def get_performance_metrics() -> PerformanceMetrics:
    _raise_no_fake_unavailable("/api/performance-metrics")


@router.get("/api/system-status", response_model=SystemStatus)
def get_system_status() -> SystemStatus:
    _raise_no_fake_unavailable("/api/system-status")


@router.get("/api/storage-alert", response_model=SimpleAlert)
def get_storage_alert() -> SimpleAlert:
    _raise_no_fake_unavailable("/api/storage-alert")


@router.get("/api/audio-spectrometer-error", response_model=SimpleAlert)
def get_audio_spectrometer_error() -> SimpleAlert:
    _raise_no_fake_unavailable("/api/audio-spectrometer-error")
