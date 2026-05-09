"""
Kloud Cloud API - Minimal Production Version
Production-ready FastAPI backend for Kloud Cloud
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from datetime import datetime
import psutil
import socket

# ============ HEALTH CHECK ============
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Kloud API Starting...")
    yield
    print("⛔ Kloud API Shutting down...")

app = FastAPI(
    title="Kloud Cloud API",
    description="Industrial AI Cloud Platform",
    version="1.0.0",
    lifespan=lifespan
)

# ============ CORS ============
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ HEALTH ENDPOINTS ============
@app.get("/health")
async def health():
    """Basic health check - used by Kubernetes"""
    return {"status": "healthy", "service": "kloud-api"}

@app.get("/status")
async def status():
    """Comprehensive system status"""
    return {
        "service": "kloud-api",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "uptime_seconds": int(psutil.Process().create_time()),
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "hostname": socket.gethostname(),
    }

@app.get("/api/asi-status")
async def asi_status():
    """ASI Trinity architecture status endpoint"""
    return {
        "module": "ASI",
        "status": "operational",
        "health": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "trinity_core": "active",
            "reasoning_engine": "ready",
            "learning_system": "ready",
            "planning_module": "ready"
        }
    }

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "Kloud Cloud API",
        "service": "kloud-api",
        "version": "1.0.0",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat()
    }

# ============ ERROR HANDLERS ============
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "timestamp": datetime.utcnow().isoformat()}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        workers=1
    )

