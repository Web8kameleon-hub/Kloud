"""
routes.py
----------
Real Kloud routes (no mocks)
---------------------------------
Ofron endpoint-e REST pÃ«r analizÃ«n e trurit, statusin e sistemit ALBI,
dhe metrikat e shÃ«ndetit kognitiv nÃ« kohÃ« reale.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime
import traceback

from app.kloud.cognitive_arch import CognitiveArchitecture

# Inicializo router-in
router = APIRouter()
architecture = CognitiveArchitecture({"center_name": "Zurich-Lab"})


@router.get("/health", tags=["system"])
async def get_system_health():
    """
    Jep njÃ« vlerÃ«sim tÃ« menjÃ«hershÃ«m tÃ« gjendjes kognitive dhe sistemike.
    """
    try:
        data = await architecture.get_health_metrics()
        return JSONResponse(
            {
                "timestamp": data["timestamp"],
                "center": data["center"],
                "status": data["status"],
                "health_score": data["health_score"],
                "stability": data["stability"],
                "focus": data["focus"],
                "metrics": data["metrics"],
            },
            status_code=200,
        )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics", tags=["system"])
async def get_detailed_metrics():
    """
    Jep metrika tÃ« detajuara tÃ« sistemit (CPU, RAM, disk, temperaturÃ«, etj.)
    """
    try:
        metrics = await architecture.get_system_metrics()
        return JSONResponse(
            {
                "timestamp": datetime.utcnow().isoformat(),
                "metrics": metrics,
            },
            status_code=200,
        )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", tags=["albi"])
async def get_albi_status():
    """
    Jep njÃ« status bazik tÃ« sistemit ALBI (placeholder pÃ«r integrim real me ALBISystem).
    """
    try:
        snapshot = await architecture.get_health_metrics()
        return JSONResponse(
            {
                "header": "âœ… ALBI Operational",
                "center": snapshot["center"],
                "status": snapshot["status"],
                "health": snapshot["health_score"],
                "insight": "System stable and responsive",
                "timestamp": snapshot["timestamp"],
            },
            status_code=200,
        )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/uptime", tags=["system"])
async def get_uptime():
    """
    Jep kohÃ«n qÃ« sistemi Ã«shtÃ« aktiv qÃ« nga nisja e analizuesit.
    """
    try:
        uptime_seconds = await architecture.get_uptime_seconds()
        return {"uptime_seconds": uptime_seconds}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


