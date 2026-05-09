#!/usr/bin/env python3
"""
Generic Service Stub - For any microservice that needs a placeholder
Usage: python service_stub.py <service_name> <port>
"""
import sys
import uvicorn
from fastapi import FastAPI
from datetime import datetime
from typing import Dict, Any

# Parse arguments
SERVICE_NAME = sys.argv[1] if len(sys.argv) > 1 else "generic-service"
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 8080

app = FastAPI(
    title=f"Kloud {SERVICE_NAME}",
    description=f"{SERVICE_NAME} microservice",
    version="1.0.0"
)

@app.get("/")
def root():
    return {
        "service": SERVICE_NAME,
        "port": PORT,
        "status": "operational",
        "version": "1.0.0"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": SERVICE_NAME,
        "port": PORT,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/info")
def info():
    return {
        "name": SERVICE_NAME,
        "port": PORT,
        "type": "microservice",
        "platform": "Kloud Cloud",
        "endpoints": ["/", "/health", "/info", "/api"]
    }

@app.get("/api")
def api():
    return {
        "service": SERVICE_NAME,
        "api_version": "v1",
        "endpoints": ["GET /", "GET /health", "GET /info", "POST /process"],
        "documentation": f"http://localhost:{PORT}/docs"
    }

@app.post("/process")
def process(data: Dict[str, Any] = None):
    return {
        "service": SERVICE_NAME,
        "status": "processed",
        "input": data,
        "result": {"success": True},
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    print(f"🚀 Starting {SERVICE_NAME} on port {PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)

