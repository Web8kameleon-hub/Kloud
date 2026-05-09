"""
Signal Generation API Routes
FastAPI routes for real-time system monitoring and signal processing
Integrated from TypeScript backend into Python
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from .services import SignalGenService
from typing import Dict, Any

router = APIRouter(prefix="/api/signal-gen", tags=["Signal Generation"])

# Initialize service
signal_service = SignalGenService()


@router.get("/health")
async def signal_gen_health():
    """Health check for signal generation service"""
    return {
        "status": "healthy",
        "service": "Kloud Signal Generation",
        "version": "1.0.0",
        "timestamp": signal_service.start_time
    }


@router.get("/status")
async def signal_gen_status():
    """Get real-time system status and ALBI+ALBA+JONA combined status"""
    try:
        return await signal_service.get_combined_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status error: {str(e)}")


@router.get("/data")
async def signal_gen_data():
    """Get real-time system data and metrics"""
    try:
        return await signal_service.get_real_system_metrics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Data error: {str(e)}")


@router.get("/albi")
async def get_albi_status():
    """Get ALBI (EEG Processing) specific status"""
    try:
        return await signal_service.get_albi_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ALBI error: {str(e)}")


@router.get("/alba")
async def get_alba_status():
    """Get ALBA (Brain Analytics) specific status"""
    try:
        return await signal_service.get_alba_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ALBA error: {str(e)}")


@router.get("/jona")
async def get_jona_status():
    """Get JONA (Neural Alignment) specific status"""
    try:
        return await signal_service.get_jona_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"JONA error: {str(e)}")


@router.get("/modules")
async def get_all_modules():
    """Get status of all neuroacoustic modules"""
    try:
        combined = await signal_service.get_combined_status()
        return combined["modules"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Modules error: {str(e)}")


@router.get("/system")
async def get_system_info():
    """Get detailed system information"""
    try:
        metrics = await signal_service.get_real_system_metrics()
        return metrics["system"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"System info error: {str(e)}")



