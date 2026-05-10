#!/usr/bin/env python3
"""
Health Monitor - Monitors all 75 Kloud microservices
Provides real-time health status and service discovery
"""

import asyncio
import sys
from datetime import datetime
from typing import Dict, List, Optional

import httpx
import uvicorn
from fastapi import BackgroundTasks, FastAPI

app = FastAPI(
    title="Kloud Health Monitor",
    description="Real-time health monitoring for all 75 microservices",
    version="1.0.0",
)

# All services to monitor
SERVICES: Dict[str, int] = {
    # Infrastructure
    "postgres": 5432,
    "redis": 6379,
    "neo4j": 7474,
    "victoriametrics": 8428,
    "minio": 9000,
    # AI & CLX
    "clx": 11434,
    "clx-i": 4444,
    "ocean-core": 8030,
    # ASI Trinity
    "alba": 5555,
    "albi": 6680,
    "jona": 7777,
    "asi": 9094,
    # Core Engines
    "alphabet-layers": 8061,
    "liam": 8062,
    "alda": 8063,
    "alba-idle": 8031,
    "blerina": 8035,
    "cycle-engine": 8070,
    "saas-orchestrator": 9999,
    # Personas
    "personas": 9200,
    # AGIEM & DataSources
    "agiem": 9300,
    "datasource-europe": 9301,
    "datasource-americas": 9302,
    "datasource-asia": 9303,
    "datasource-india": 9304,
    "datasource-africa": 9305,
    "datasource-oceania": 9306,
    "datasource-central-asia": 9307,
    "datasource-antarctica": 9308,
    # Labs (23)
    "lab-elbasan": 9101,
    "lab-tirana": 9102,
    "lab-durres": 9103,
    "lab-vlore": 9104,
    "lab-shkoder": 9105,
    "lab-korce": 9106,
    "lab-saranda": 9107,
    "lab-prishtina": 9108,
    "lab-kostur": 9109,
    "lab-athens": 9110,
    "lab-rome": 9111,
    "lab-zurich": 9112,
    "lab-beograd": 9113,
    "lab-sofia": 9114,
    "lab-zagreb": 9115,
    "lab-ljubljana": 9116,
    "lab-vienna": 9117,
    "lab-prague": 9118,
    "lab-budapest": 9119,
    "lab-bucharest": 9120,
    "lab-istanbul": 9121,
    "lab-cairo": 9122,
    "lab-jerusalem": 9123,
    # SaaS & Marketplace
    "saas-api": 8040,
    "marketplace": 8004,
    "economy": 9093,
    # Services
    "reporting": 8001,
    "excel": 8002,
    "behavioral": 8003,
    "analytics": 8016,
    "neurosonix": 8015,
    "aviation": 8080,
    "multi-tenant": 8007,
    "quantum": 8008,
    "biometric": 8017,
    "userdata": 8018,
    "curiosity": 8019,
    # Frontend & Gateway
    "api": 8000,
    "web": 3000,
    "traefik": 80,
    # Monitoring
    "prometheus": 9090,
    "grafana": 3001,
    "loki": 3100,
    "jaeger": 16686,
    "tempo": 3200,
    # Cognitive
    "agent-telemetry": 8009,
    "cognitive-engine": 8010,
    "adaptive-router": 8011,
}

# Cache for health status
health_cache: Dict[str, Dict] = {}
last_check: Optional[datetime] = None


async def check_service_health(name: str, port: int) -> Dict:
    """Check health of a single service"""
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            # Try /health endpoint first
            try:
                r = await client.get(f"http://{name}:{port}/health")
                if r.status_code == 200:
                    return {
                        "status": "UP",
                        "response_time_ms": r.elapsed.total_seconds() * 1000,
                    }
            except:
                pass

            # Try root endpoint
            try:
                r = await client.get(f"http://{name}:{port}/")
                if r.status_code == 200:
                    return {
                        "status": "UP",
                        "response_time_ms": r.elapsed.total_seconds() * 1000,
                    }
            except:
                pass

            # Try localhost for same-host services
            try:
                r = await client.get(f"http://localhost:{port}/health")
                if r.status_code == 200:
                    return {
                        "status": "UP",
                        "response_time_ms": r.elapsed.total_seconds() * 1000,
                    }
            except:
                pass

    except Exception as e:
        pass

    return {"status": "DOWN", "response_time_ms": None}


async def check_all_services() -> Dict:
    """Check all services in parallel"""
    global health_cache, last_check

    tasks = [check_service_health(name, port) for name, port in SERVICES.items()]
    results = await asyncio.gather(*tasks)

    health_cache = {
        name: {**result, "port": port}
        for (name, port), result in zip(SERVICES.items(), results)
    }
    last_check = datetime.utcnow()

    return health_cache


@app.get("/")
def root():
    return {
        "service": "Kloud Health Monitor",
        "version": "1.0.0",
        "total_services": len(SERVICES),
        "status": "operational",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "health-monitor",
        "monitored_services": len(SERVICES),
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/status")
async def status():
    """Get status of all services"""
    await check_all_services()

    up_count = sum(1 for s in health_cache.values() if s["status"] == "UP")
    down_count = len(SERVICES) - up_count

    return {
        "services": health_cache,
        "summary": {
            "total": len(SERVICES),
            "up": up_count,
            "down": down_count,
            "health_percentage": round((up_count / len(SERVICES)) * 100, 1),
        },
        "last_check": last_check.isoformat() if last_check else None,
    }


@app.get("/status/{service_name}")
async def service_status(service_name: str):
    """Get status of a specific service"""
    if service_name not in SERVICES:
        return {"error": f"Unknown service: {service_name}"}

    port = SERVICES[service_name]
    result = await check_service_health(service_name, port)

    return {
        "service": service_name,
        "port": port,
        **result,
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/services")
def list_services():
    """List all monitored services"""
    categories = {
        "infrastructure": ["postgres", "redis", "neo4j", "victoriametrics", "minio"],
        "ai": ["clx", "clx-i", "ocean-core"],
        "asi_trinity": ["alba", "albi", "jona", "asi"],
        "core_engines": [
            "alphabet-layers",
            "liam",
            "alda",
            "alba-idle",
            "blerina",
            "cycle-engine",
            "saas-orchestrator",
        ],
        "personas": ["personas"],
        "datasources": [k for k in SERVICES if k.startswith("datasource-")],
        "labs": [k for k in SERVICES if k.startswith("lab-")],
        "saas": ["saas-api", "marketplace", "economy"],
        "services": [
            "reporting",
            "excel",
            "behavioral",
            "analytics",
            "neurosonix",
            "aviation",
            "multi-tenant",
            "quantum",
        ],
        "frontend": ["api", "web", "traefik"],
        "monitoring": ["prometheus", "grafana", "loki", "jaeger", "tempo"],
        "cognitive": ["agent-telemetry", "cognitive-engine", "adaptive-router"],
    }

    return {
        "total_services": len(SERVICES),
        "categories": {
            cat: {
                "count": len(services),
                "services": [{"name": s, "port": SERVICES.get(s)} for s in services],
            }
            for cat, services in categories.items()
        },
    }


@app.get("/summary")
async def summary():
    """Get quick summary without full health check"""
    if not health_cache:
        await check_all_services()

    up_count = sum(1 for s in health_cache.values() if s["status"] == "UP")

    return {
        "total": len(SERVICES),
        "up": up_count,
        "down": len(SERVICES) - up_count,
        "health_percentage": round((up_count / len(SERVICES)) * 100, 1),
        "last_check": last_check.isoformat() if last_check else "never",
    }


if __name__ == "__main__":
    PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8099
    print(f"📊 Starting Kloud Health Monitor on port {PORT}")
    print(f"   Monitoring {len(SERVICES)} services")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
