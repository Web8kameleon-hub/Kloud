from fastapi import APIRouter, HTTPException
import psutil
import time

router = APIRouter()


@router.get("/api/agi-stats", tags=["AGI"])
def get_agi_stats():
    """Kthen statistika reale tÃ« sistemit AGI industrial."""
    return {
        "agi_status": "active",
        "node_count": len(psutil.pids()),
        "cpu_percent": psutil.cpu_percent(),
        "memory": psutil.virtual_memory()._asdict(),
        "disk": psutil.disk_usage("/")._asdict(),
        "timestamp": time.time(),
        "hostname": psutil.users()[0].name if psutil.users() else "unknown",
    }


"""
Copyright (c) Kloud Cloud. All rights reserved.
Closed Source License.
"""


@router.get("/industrial/data", tags=["Industrial"])
def get_industrial_data():
    # Do not fabricate sensor values. Fail clearly until a real sensor source exists.
    raise HTTPException(
        status_code=503,
        detail={
            "error": "industrial_sensor_source_unconfigured",
            "message": "No fake ever: industrial sensor data is unavailable until a real source is configured.",
            "expected_sources": ["modbus", "opcua", "mqtt", "serial", "vendor_sdk"],
            "timestamp": time.time(),
            "host_metrics": {
                "cpu_percent": psutil.cpu_percent(),
                "memory": psutil.virtual_memory()._asdict(),
                "disk": psutil.disk_usage("/")._asdict(),
                "processes": len(psutil.pids()),
                "hostname": psutil.users()[0].name if psutil.users() else "unknown",
            },
        },
    )
