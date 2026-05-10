"""
NODENDB REAL SERVICE INTEGRATION FOR KLOUD
============================================

This module integrates NodeDB Stigma Pattern with ACTUAL running Kloud services.
NO MOCKS. NO FAKES. Only real HTTP calls to real service endpoints.

Real Services Connected To:
- API Backend (localhost:8000)
- Ocean Core ML Engine (localhost:8030)
- ASI Trinity (ALBA: 5555, ALBI: 6680, JONA: 7777)
- OLLAMA Multi API (localhost:4444)
- AI Global Nanogrid (localhost:9999)
- Aviation Weather (localhost:8080)
- Redis (localhost:6379)
- PostgreSQL (localhost:5432)
- Neo4j (localhost:7474, 7687)
"""

import asyncio
import logging
import sys
from types import ModuleType
from typing import Dict, Any, Optional
from datetime import datetime

from nodendb_stigma import (
    NDBQuality,
    StigmaState,
    get_nodedb,
    initialize_nodendb,
    register_service_with_nodedb,
)

try:
    import httpx
except ImportError:
    print("ERROR: httpx not installed. Install with: pip install httpx")
    sys.exit(1)

_redis_asyncio: ModuleType | None = None
try:
    import redis.asyncio as redis_asyncio_module
except ImportError:
    print("WARNING: redis.asyncio not available, some checks will be skipped")
else:
    _redis_asyncio = redis_asyncio_module

redis: ModuleType | None = _redis_asyncio

_psycopg2: ModuleType | None = None
try:
    import psycopg2 as psycopg2_module  # type: ignore[import-not-found]
except ImportError:
    print("WARNING: psycopg2 not available, some checks will be skipped")
else:
    _psycopg2 = psycopg2_module

psycopg2: ModuleType | None = _psycopg2

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# ============================================================================
# REAL SERVICE ENDPOINTS - NO MOCKS
# ============================================================================

SERVICE_ENDPOINTS = {
    "api": {"host": "127.0.0.1", "port": 7161, "scheme": "http"},
    "ocean-core": {"host": "127.0.0.1", "port": 7160, "scheme": "http"},
    "alba": {"host": "127.0.0.1", "port": 7152, "scheme": "http"},
    "albi": {"host": "127.0.0.1", "port": 7159, "scheme": "http"},
    "jona": {"host": "127.0.0.1", "port": 7157, "scheme": "http"},
    "clx-i": {"host": "127.0.0.1", "port": 7160, "scheme": "http"},
    "ai-global-9999": {"host": "127.0.0.1", "port": 9080, "scheme": "http"},
    "aviation": {"host": "127.0.0.1", "port": 8080, "scheme": "http"},
    "neo4j": {"host": "127.0.0.1", "port": 7474, "scheme": "http"},
}

SERVICE_HEALTH_PATHS = {
    "api": ["/health", "/status", "/api/v1/status", "/api/health"],
    "ocean-core": ["/health", "/status", "/"],
    "alba": ["/health", "/api/health", "/status"],
    "albi": ["/health", "/api/health", "/status", "/"],
    "jona": ["/health", "/status", "/"],
    "clx-i": ["/health", "/status", "/"],
    "ai-global-9999": ["/status", "/health", "/"],
    "aviation": ["/health", "/status", "/"],
    "neo4j": ["/health", "/"],
}

DATABASE_ENDPOINTS = {
    "redis": {"host": "localhost", "port": 6379},
    "postgres": {
        "host": "localhost",
        "port": 5432,
        "user": "kloud",
        "password": "kloud",
        "db": "klouddb",
    },
    "neo4j": {
        "host": "localhost",
        "port": 7687,
        "user": "neo4j",
        "password": "kloud123",
    },
}

# ============================================================================
# SOVEREIGN FABRIC NODES - SCALABLE CONFIGURATION
# ============================================================================
# Multi-node architecture with TIDE tracking, NDB scoring, and security posture
# Supports unlimited nodes (1-N) with radius-aware clustering

SOVEREIGN_FABRIC_NODES = {
    # Node #1 - Living Sovereign Fabric
    1: {
        "name": "Living Sovereign Fabric #1",
        "port": 9001,
        "host": "localhost",
        "scheme": "http",
        "region": "fsn1",
        "radius_km": 50,
        "description": "Primary sovereign fabric with full TIDE correlation",
        "active": True,
    },
    # Node #2 - Resilience & Coherence
    2: {
        "name": "Resilience Node #2",
        "port": 9002,
        "host": "localhost",
        "scheme": "http",
        "region": "fsn1",
        "radius_km": 75,
        "description": "Secondary node with coherence tracking",
        "active": True,
    },
    # Node #3 - Latency & Bandwidth Optimization
    3: {
        "name": "Optimization Node #3",
        "port": 9003,
        "host": "localhost",
        "scheme": "http",
        "region": "nbg1",
        "radius_km": 100,
        "description": "Tertiary node optimizing latency/bandwidth",
        "active": True,
    },
    # Node #4 - Security & Compliance
    4: {
        "name": "Security Node #4",
        "port": 9004,
        "host": "localhost",
        "scheme": "http",
        "region": "nbg1",
        "radius_km": 120,
        "description": "Quaternary node monitoring security posture",
        "active": True,
    },
    # Node #5+ can be added here following the same pattern
}


# ============================================================================
# REAL HTTP-BASED HEALTH CHECKS - NO MOCKS
# ============================================================================


async def check_sovereign_node_health(
    node_id: int, node_config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Real health check for sovereign fabric nodes with TIDE tracking.
    Monitors: NDB Score, TIDE correlation, security posture, latency, bandwidth.
    """
    endpoint = f"{node_config['scheme']}://{node_config['host']}:{node_config['port']}"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Main health/status endpoint
            response = await client.get(f"{endpoint}/status")
            response.raise_for_status()
            status_data = response.json()

            # Get telemetry with NDB scoring
            try:
                telemetry_response = await client.get(
                    f"{endpoint}/telemetry", timeout=10.0
                )
                telemetry_data = (
                    telemetry_response.json()
                    if telemetry_response.status_code == 200
                    else {}
                )
            except Exception:
                telemetry_data = {}

            # Calculate metrics from real response
            response_time_ms = response.elapsed.total_seconds() * 1000
            ndb_score = float(
                telemetry_data.get("ndb_score", status_data.get("ndb_quality", 0.036))
            )
            tide = str(
                telemetry_data.get("tide", status_data.get("tide", "normal"))
            ).lower()
            security_posture = str(
                telemetry_data.get("security_posture", "stable")
            ).lower()
            events_tracked = int(
                telemetry_data.get("events_tracked", status_data.get("events", 0))
            )
            bandwidth_kbps = float(telemetry_data.get("bandwidth_kbps", 0.0))
            utilization_pct = float(telemetry_data.get("utilization_pct", 0.0))
            crdt_cardinality = int(telemetry_data.get("crdt_cardinality", 0))
            stigma_state = str(telemetry_data.get("stigma_state", "stable")).lower()

            # Quality scoring based on NDB and TIDE
            quality_score = ndb_score
            if tide == "low":
                quality_score *= 0.95
            elif tide == "high":
                quality_score *= 0.75
            elif tide == "critical":
                quality_score *= 0.5

            logger.info(
                f"✅ Sovereign Node #{node_id} ({node_config['name']}): "
                f"TIDE={tide} | NDB={ndb_score:.3f} | {response_time_ms:.1f}ms"
            )

            return {
                "status": "healthy",
                "node_id": node_id,
                "node_name": node_config.get("name"),
                "endpoint": endpoint,
                "region": node_config.get("region"),
                "radius_km": node_config.get("radius_km"),
                "response_time_ms": response_time_ms,
                "tide": tide,
                "ndb_score": ndb_score,
                "security_posture": security_posture,
                "events_tracked": events_tracked,
                "bandwidth_kbps": bandwidth_kbps,
                "utilization_pct": utilization_pct,
                "crdt_cardinality": crdt_cardinality,
                "stigma_state": stigma_state,
                "quality_score": max(0.0, quality_score),
                "status_data": status_data,
                "telemetry_data": telemetry_data,
            }
    except Exception as e:
        logger.error(f"❌ Sovereign Node #{node_id} health check failed: {e}")
        return {
            "status": "error",
            "node_id": node_id,
            "node_name": node_config.get("name"),
            "endpoint": endpoint,
            "region": node_config.get("region"),
            "error": str(e),
            "quality_score": 0.0,
            "tide": "critical",
            "ndb_score": 0.0,
        }


async def _get_first_ok_json(
    client: httpx.AsyncClient, endpoint: str, paths: list[str]
) -> tuple[httpx.Response, Dict[str, Any], str]:
    """Return first successful JSON response for the provided path candidates."""
    last_error: Optional[Exception] = None
    for path in paths:
        try:
            response = await client.get(f"{endpoint}{path}", timeout=10.0)
            if response.status_code in [200, 201, 202, 204]:
                try:
                    payload = response.json()
                except Exception:
                    payload = {}
                return response, payload, path
        except Exception as exc:
            last_error = exc

    if last_error:
        raise last_error
    raise RuntimeError(f"No healthy paths responded for {endpoint}")


async def check_api_health() -> Dict[str, Any]:
    """Real health check - HTTP call to actual API Backend"""
    endpoint = f"{SERVICE_ENDPOINTS['api']['scheme']}://{SERVICE_ENDPOINTS['api']['host']}:{SERVICE_ENDPOINTS['api']['port']}"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            health_response, health_data, health_path = await _get_first_ok_json(
                client,
                endpoint,
                SERVICE_HEALTH_PATHS.get(
                    "api", ["/health", "/status", "/api/v1/status"]
                ),
            )

            # Query execution time metrics
            status_data = {}
            for status_path in ["/api/v1/status", "/status", "/api/health"]:
                try:
                    status_response = await client.get(
                        f"{endpoint}{status_path}", timeout=10.0
                    )
                    if status_response.status_code == 200:
                        try:
                            status_data = status_response.json()
                        except Exception:
                            status_data = {}
                        break
                except Exception:
                    continue

            # Calculate NDB quality from real response time
            response_time = health_response.elapsed.total_seconds() * 1000
            quality_score = (
                1.0 if response_time < 100 else (1.0 - min(response_time / 1000, 0.5))
            )

            logger.info(
                f"✅ API Health: {health_data.get('status', 'unknown')} (path: {health_path}, response: {response_time:.1f}ms)"
            )

            return {
                "status": "healthy",
                "endpoint": endpoint,
                "health_path": health_path,
                "response_time_ms": response_time,
                "health_data": health_data,
                "status_data": status_data,
                "quality_score": max(0.0, quality_score),
            }
    except Exception as e:
        logger.error(f"❌ API health check failed: {e}")
        return {
            "status": "error",
            "endpoint": endpoint,
            "error": str(e),
            "quality_score": 0.0,
        }


async def check_ocean_core_health() -> Dict[str, Any]:
    """Real health check - HTTP call to actual Ocean Core"""
    endpoint = f"{SERVICE_ENDPOINTS['ocean-core']['scheme']}://{SERVICE_ENDPOINTS['ocean-core']['host']}:{SERVICE_ENDPOINTS['ocean-core']['port']}"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response, health_data, health_path = await _get_first_ok_json(
                client,
                endpoint,
                SERVICE_HEALTH_PATHS.get("ocean-core", ["/health", "/status", "/"]),
            )

            # Try to get model status
            try:
                models_response = await client.get(f"{endpoint}/models", timeout=10.0)
                models_data = (
                    models_response.json() if models_response.status_code == 200 else {}
                )
            except Exception:
                models_data = {}

            response_time = response.elapsed.total_seconds() * 1000

            # Quality based on model availability and response time
            model_ready = (
                health_data.get("model_ready", False)
                or health_data.get("status") == "ok"
            )
            quality = 0.95 if model_ready else 0.5
            quality = quality * max(0.0, 1.0 - response_time / 1000)

            logger.info(
                f"✅ Ocean Core Health: {health_data.get('status', 'unknown')} (response: {response_time:.1f}ms)"
            )

            return {
                "status": "healthy",
                "endpoint": endpoint,
                "health_path": health_path,
                "response_time_ms": response_time,
                "health_data": health_data,
                "models_data": models_data,
                "quality_score": max(0.0, quality),
            }
    except Exception as e:
        logger.error(f"❌ Ocean Core health check failed: {e}")
        return {
            "status": "error",
            "endpoint": endpoint,
            "error": str(e),
            "quality_score": 0.0,
        }


async def check_trinity_health() -> Dict[str, Any]:
    """Real health check - HTTP calls to actual ASI Trinity (ALBA, ALBI, JONA)"""
    trinity_components = {
        "alba": SERVICE_ENDPOINTS["alba"],
        "albi": SERVICE_ENDPOINTS["albi"],
        "jona": SERVICE_ENDPOINTS["jona"],
    }

    trinity_status = {}
    all_healthy = True
    response_times = []

    async with httpx.AsyncClient(timeout=10.0) as client:
        for component_name, endpoint_config in trinity_components.items():
            endpoint = f"{endpoint_config['scheme']}://{endpoint_config['host']}:{endpoint_config['port']}"
            try:
                response, health_data, health_path = await _get_first_ok_json(
                    client,
                    endpoint,
                    SERVICE_HEALTH_PATHS.get(
                        component_name, ["/health", "/api/health", "/status"]
                    ),
                )
                response_time = response.elapsed.total_seconds() * 1000
                response_times.append(response_time)

                trinity_status[component_name] = {
                    "status": "healthy",
                    "data": health_data,
                    "health_path": health_path,
                    "response_time_ms": response_time,
                }
                logger.info(
                    f"✅ {component_name.upper()} Health: {health_data.get('status', 'unknown')}"
                )
            except Exception as e:
                all_healthy = False
                logger.error(f"❌ {component_name.upper()} health check failed: {e}")
                trinity_status[component_name] = {
                    "status": "error",
                    "error": str(e),
                }

    # Calculate coherence based on all components healthy
    coherence = 1.0 if all_healthy else 0.5
    avg_response_time = (
        sum(response_times) / len(response_times) if response_times else 0
    )
    quality = coherence * max(0.0, 1.0 - avg_response_time / 1000)

    return {
        "status": "healthy" if all_healthy else "degraded",
        "trinity_status": trinity_status,
        "all_components_healthy": all_healthy,
        "coherence": coherence,
        "avg_response_time_ms": avg_response_time,
        "quality_score": max(0.0, quality),
    }


async def check_jona_sandbox_health() -> Dict[str, Any]:
    """Real health check for JONA sandbox and ethics surfaces."""
    jona_endpoint = (
        f"{SERVICE_ENDPOINTS['jona']['scheme']}://"
        f"{SERVICE_ENDPOINTS['jona']['host']}:{SERVICE_ENDPOINTS['jona']['port']}"
    )
    api_endpoint = (
        f"{SERVICE_ENDPOINTS['api']['scheme']}://"
        f"{SERVICE_ENDPOINTS['api']['host']}:{SERVICE_ENDPOINTS['api']['port']}"
    )
    endpoints = {
        "jona_service": [
            f"{jona_endpoint}/health",
            f"{jona_endpoint}/status",
            f"{jona_endpoint}/",
        ],
        "jona_api": [
            f"{api_endpoint}/api/jona/health",
            f"{api_endpoint}/api/health",
            f"{api_endpoint}/health",
        ],
        "asi_health": [
            f"{api_endpoint}/api/asi/health",
            f"{api_endpoint}/api/health",
            f"{api_endpoint}/status",
        ],
    }

    results: Dict[str, Any] = {}
    health_scores = []
    violations = []

    async with httpx.AsyncClient(timeout=10.0) as client:
        for name, candidate_urls in endpoints.items():
            try:
                response = None
                payload = {}
                chosen_url = None

                for url in candidate_urls:
                    try:
                        response = await client.get(url, timeout=10.0)
                        if response.status_code == 200:
                            chosen_url = url
                            break
                    except Exception:
                        continue

                if response is None:
                    raise RuntimeError("No endpoint responded")

                if response.status_code == 200:
                    try:
                        payload = response.json()
                    except Exception:
                        payload = {}
                component_health = payload.get(
                    "health_score",
                    payload.get("overall_health", payload.get("health", 0.0)),
                )
                if isinstance(component_health, str):
                    try:
                        component_health = float(component_health)
                    except ValueError:
                        component_health = 0.0
                if isinstance(component_health, bool):
                    component_health = 1.0 if component_health else 0.0
                component_health = float(component_health or 0.0)
                health_scores.append(component_health)
                results[name] = {
                    "status": "healthy" if response.status_code == 200 else "error",
                    "status_code": response.status_code,
                    "endpoint": chosen_url,
                    "health_score": round(component_health, 3),
                    "data": payload,
                }
            except Exception as exc:
                violations.append(f"{name}:{type(exc).__name__}")
                results[name] = {
                    "status": "error",
                    "error": str(exc),
                    "health_score": 0.0,
                }

    avg_health = sum(health_scores) / len(health_scores) if health_scores else 0.0
    active = avg_health >= 0.5 and not violations
    threat_level = (
        "low" if avg_health >= 0.75 else "medium" if avg_health >= 0.45 else "high"
    )

    return {
        "status": "healthy" if active else "degraded",
        "active": active,
        "threatLevel": threat_level,
        "health_score": round(avg_health, 3),
        "violations": violations,
        "components": results,
    }


def evaluate_governance_proposal(
    proposal: Dict[str, Any],
    sandbox_health: Dict[str, Any],
    node_state: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Evaluate a governance/self-writing proposal against JONA sandbox rules."""

    requires_self_learning = bool(proposal.get("requires_self_learning", False))
    requires_self_writing = bool(proposal.get("requires_self_writing", False))
    risk_score = float(proposal.get("risk_score", 0.0) or 0.0)
    tide = str(proposal.get("tide", "normal")).lower()
    ndb_quality = str(proposal.get("ndb_quality", "fair")).lower()
    sandbox_active = bool(sandbox_health.get("active", False))
    sandbox_threat = str(sandbox_health.get("threatLevel", "high")).lower()
    node_stigma = str((node_state or {}).get("stigma_state", "active")).lower()

    requires_gate = requires_self_learning or requires_self_writing
    forced_sandbox = (
        requires_gate
        or sandbox_threat != "low"
        or node_stigma in {"degraded", "recovering"}
    )

    if risk_score >= 0.85:
        decision = "rejected"
        reason = "risk score too high"
    elif forced_sandbox and (
        not sandbox_active
        or tide == "low"
        or risk_score > 0.35
        or ndb_quality not in {"good", "excellent"}
    ):
        decision = "sandbox_only"
        reason = "JONA sandbox required before promotion"
    else:
        decision = "approved"
        reason = "governance checks passed"

    return {
        "decision": decision,
        "reason": reason,
        "requires_self_learning": requires_self_learning,
        "requires_self_writing": requires_self_writing,
        "risk_score": risk_score,
        "tide": tide,
        "ndb_quality": ndb_quality,
        "sandbox": sandbox_health,
        "node_state": node_state or {},
    }


async def check_database_health() -> Dict[str, Any]:
    """Real health checks for all databases"""
    db_status = {}

    # Redis health check
    if redis:
        try:
            redis_client = await redis.from_url(
                f"redis://{DATABASE_ENDPOINTS['redis']['host']}:{DATABASE_ENDPOINTS['redis']['port']}"
            )
            pong = await redis_client.ping()
            info = await redis_client.info()
            await redis_client.close()

            db_status["redis"] = {
                "status": "healthy" if pong else "error",
                "info": {
                    "used_memory_mb": info.get("used_memory", 0) / (1024 * 1024),
                    "connected_clients": info.get("connected_clients", 0),
                    "total_commands_processed": info.get("total_commands_processed", 0),
                },
            }
            logger.info("✅ Redis Health: PONG")
        except Exception as e:
            logger.error(f"❌ Redis health check failed: {e}")
            db_status["redis"] = {"status": "error", "error": str(e)}

    # PostgreSQL health check
    if psycopg2:
        try:
            conn = psycopg2.connect(
                host=DATABASE_ENDPOINTS["postgres"]["host"],
                user=DATABASE_ENDPOINTS["postgres"]["user"],
                password=DATABASE_ENDPOINTS["postgres"]["password"],
                database=DATABASE_ENDPOINTS["postgres"]["db"],
                connect_timeout=5,
            )
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            conn.close()

            db_status["postgres"] = {
                "status": "healthy",
                "version": version.split(",")[0] if version else "unknown",
            }
            logger.info("✅ PostgreSQL Health: Connected")
        except Exception as e:
            logger.error(f"❌ PostgreSQL health check failed: {e}")
            db_status["postgres"] = {"status": "error", "error": str(e)}

    # Neo4j HTTP health check
    try:
        endpoint = f"http://{SERVICE_ENDPOINTS['neo4j']['host']}:{SERVICE_ENDPOINTS['neo4j']['port']}"
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{endpoint}/health")
            db_status["neo4j"] = {
                "status": "healthy" if response.status_code == 200 else "error",
                "response": response.text if response.status_code != 200 else "OK",
            }
            logger.info("✅ Neo4j Health: Responding")
    except Exception as e:
        logger.error(f"❌ Neo4j health check failed: {e}")
        db_status["neo4j"] = {"status": "error", "error": str(e)}

    return db_status


# ============================================================================
# REAL SERVICE REGISTRATION - NO MOCKS
# ============================================================================


async def initialize_kloud_nodedb_real():
    """
    Initialize NodeDB with ONLY REAL services.
    No mocks, no fakes - connects directly to running services.
    """

    logger.info("=" * 80)
    logger.info("🚀 INITIALIZING KLOUD NODEDB WITH REAL SERVICES")
    logger.info("=" * 80)

    # Initialize NodeDB core
    nodedb = await initialize_nodendb()
    logger.info("✅ NodeDB core initialized\n")

    # Remove historical duplicates from previous timestamp-based node IDs.
    dedupe_stats = await nodedb.dedupe_nodes()
    if dedupe_stats.get("removed", 0) > 0:
        logger.info(
            f"🧹 NodeDB dedupe: {dedupe_stats['before']} -> {dedupe_stats['after']}"
        )

    # ========================================================================
    # CHECK SERVICE AVAILABILITY FIRST
    # ========================================================================

    logger.info("🔍 Scanning for available real services...\n")

    available_services = {}
    async with httpx.AsyncClient(timeout=5.0) as client:
        for service_name, endpoint_config in SERVICE_ENDPOINTS.items():
            endpoint = f"{endpoint_config['scheme']}://{endpoint_config['host']}:{endpoint_config['port']}"
            try:
                paths = SERVICE_HEALTH_PATHS.get(
                    service_name, ["/health", "/status", "/"]
                )
                response, _, health_path = await _get_first_ok_json(
                    client, endpoint, paths
                )
                if response.status_code in [200, 201, 202, 204]:
                    available_services[service_name] = True
                    logger.info(
                        f"✓ {service_name}: Available at {endpoint}{health_path}"
                    )
            except Exception as e:
                logger.warning(f"✗ {service_name}: Not available ({type(e).__name__})")

    if not available_services:
        logger.critical("❌ NO SERVICES AVAILABLE!")
        logger.critical("   Please ensure docker-compose services are running:")
        logger.critical("   docker-compose up -d")
        return {"nodedb": nodedb, "services": {}, "available_count": 0}

    logger.info(f"\n✅ Found {len(available_services)} available services\n")

    # ========================================================================
    # REGISTER REAL SERVICES
    # ========================================================================

    registered = {}

    # 1. API Backend (REAL HTTP)
    if "api" in available_services:
        logger.info("📝 Registering API Backend (Real HTTP)...")
        try:
            # Create stub module for introspection
            class APIService:
                __name__ = "api"
                __version__ = "2.3.1"
                __doc__ = "FastAPI Backend Service - Real HTTP Service"

            node_id = await register_service_with_nodedb(
                APIService(), "API Backend", health_check_fn=check_api_health
            )
            registered["api"] = node_id
            logger.info(f"  ✓ API registered: {node_id}\n")
        except Exception as e:
            logger.error(f"  ✗ API registration failed: {e}\n")

    # 2. Ocean Core (REAL HTTP)
    if "ocean-core" in available_services:
        logger.info("📝 Registering Ocean Core (Real HTTP)...")
        try:

            class OceanCoreService:
                __name__ = "ocean_core"
                __version__ = "1.8.5"
                __doc__ = "Ocean Core ML Engine - Real HTTP Service"

            node_id = await register_service_with_nodedb(
                OceanCoreService(),
                "Ocean Core ML Engine",
                health_check_fn=check_ocean_core_health,
            )
            registered["ocean-core"] = node_id
            logger.info(f"  ✓ Ocean Core registered: {node_id}\n")
        except Exception as e:
            logger.error(f"  ✗ Ocean Core registration failed: {e}\n")

    # 3. ASI Trinity (REAL HTTP)
    if (
        "alba" in available_services
        or "albi" in available_services
        or "jona" in available_services
    ):
        logger.info("📝 Registering ASI Trinity (Real HTTP - ALBA, ALBI, JONA)...")
        try:

            class ASITrinityService:
                __name__ = "asi_trinity"
                __version__ = "3.1.0"
                __doc__ = "ASI Trinity Master Orchestrator - Real HTTP Service"

            node_id = await register_service_with_nodedb(
                ASITrinityService(),
                "ASI Trinity (ALBA, ALBI, JONA)",
                health_check_fn=check_trinity_health,
            )
            registered["asi-trinity"] = node_id
            logger.info(f"  ✓ ASI Trinity registered: {node_id}\n")
        except Exception as e:
            logger.error(f"  ✗ ASI Trinity registration failed: {e}\n")

    # 3b. JONA Sandbox Governance (REAL HTTP)
    if "jona" in available_services or "api" in available_services:
        logger.info("📝 Registering JONA Sandbox Governance (Real HTTP)...")
        try:

            class JonaSandboxService:
                __name__ = "jona_sandbox"
                __version__ = "1.0.0"
                __doc__ = "JONA sandbox governance and ethics guard - Real HTTP Service"

            node_id = await register_service_with_nodedb(
                JonaSandboxService(),
                "JONA Sandbox Governance",
                health_check_fn=check_jona_sandbox_health,
            )
            registered["jona-sandbox"] = node_id
            logger.info(f"  ✓ JONA Sandbox registered: {node_id}\n")
        except Exception as e:
            logger.error(f"  ✗ JONA Sandbox registration failed: {e}\n")

    # 4. CLX.I Multi API (REAL HTTP)
    if "clx-i" in available_services:
        logger.info("📝 Registering CLX.I Multi API (Real HTTP)...")
        try:

            class CLXIMultiService:
                __name__ = "clx_i"
                __version__ = "1.0.0"
                __doc__ = "CLX.I Multi-Model Router - Real HTTP Service"

            async def check_clx_i_health():
                endpoint = (
                    f"{SERVICE_ENDPOINTS['clx-i']['scheme']}://"
                    f"{SERVICE_ENDPOINTS['clx-i']['host']}:"
                    f"{SERVICE_ENDPOINTS['clx-i']['port']}"
                )
                try:
                    async with httpx.AsyncClient(timeout=10.0) as client:
                        response, health_data, health_path = await _get_first_ok_json(
                            client,
                            endpoint,
                            SERVICE_HEALTH_PATHS.get("clx-i", ["/health", "/status"]),
                        )
                        return {
                            "status": "healthy"
                            if response.status_code in [200, 201, 202, 204]
                            else "error",
                            "health_path": health_path,
                            "data": health_data,
                            "quality_score": 0.9
                            if response.status_code in [200, 201, 202, 204]
                            else 0.0,
                        }
                except Exception as e:
                    return {"status": "error", "error": str(e), "quality_score": 0.0}

            node_id = await register_service_with_nodedb(
                CLXIMultiService(),
                "CLX.I Multi-Model Router",
                health_check_fn=check_clx_i_health,
            )
            registered["clx-i"] = node_id
            logger.info(f"  ✓ CLX.I registered: {node_id}\n")
        except Exception as e:
            logger.error(f"  ✗ CLX.I registration failed: {e}\n")

    # 5. AI Global Nanogrid (REAL HTTP)
    if "ai-global-9999" in available_services:
        logger.info("📝 Registering AI Global Nanogrid (Real HTTP)...")
        try:

            class AIGlobalService:
                __name__ = "ai_global"
                __version__ = "1.0.0"
                __doc__ = "AI Global CPU Nanogrid - Real HTTP Service"

            async def check_ai_global_health():
                endpoint = "http://localhost:9999"
                try:
                    async with httpx.AsyncClient(timeout=10.0) as client:
                        response = await client.get(f"{endpoint}/health")
                        health_data = (
                            response.json() if response.status_code == 200 else {}
                        )
                        return {
                            "status": "healthy"
                            if response.status_code == 200
                            else "error",
                            "data": health_data,
                            "quality_score": 0.9
                            if response.status_code == 200
                            else 0.0,
                        }
                except Exception as e:
                    return {"status": "error", "error": str(e), "quality_score": 0.0}

            node_id = await register_service_with_nodedb(
                AIGlobalService(),
                "AI Global Nanogrid",
                health_check_fn=check_ai_global_health,
            )
            registered["ai-global"] = node_id
            logger.info(f"  ✓ AI Global registered: {node_id}\n")
        except Exception as e:
            logger.error(f"  ✗ AI Global registration failed: {e}\n")

    # 6. Aviation Weather (REAL HTTP)
    if "aviation" in available_services:
        logger.info("📝 Registering Aviation Weather Service (Real HTTP)...")
        try:

            class AviationService:
                __name__ = "aviation"
                __version__ = "1.0.0"
                __doc__ = "Aviation Weather API - Real HTTP Service"

            async def check_aviation_health():
                endpoint = "http://localhost:8080"
                try:
                    async with httpx.AsyncClient(timeout=10.0) as client:
                        response = await client.get(f"{endpoint}/health")
                        health_data = (
                            response.json() if response.status_code == 200 else {}
                        )
                        return {
                            "status": "healthy"
                            if response.status_code == 200
                            else "error",
                            "data": health_data,
                            "quality_score": 0.9
                            if response.status_code == 200
                            else 0.0,
                        }
                except Exception as e:
                    return {"status": "error", "error": str(e), "quality_score": 0.0}

            node_id = await register_service_with_nodedb(
                AviationService(),
                "Aviation Weather Service",
                health_check_fn=check_aviation_health,
            )
            registered["aviation"] = node_id
            logger.info(f"  ✓ Aviation registered: {node_id}\n")
        except Exception as e:
            logger.error(f"  ✗ Aviation registration failed: {e}\n")

    # 7. SOVEREIGN FABRIC NODES - SCALABLE MULTI-NODE ARCHITECTURE
    logger.info("=" * 80)
    logger.info("📝 Registering Sovereign Fabric Nodes (Scalable Architecture)...")
    logger.info("=" * 80 + "\n")

    sovereign_fabric_nodes = {}
    for node_id, node_config in SOVEREIGN_FABRIC_NODES.items():
        if not node_config.get("active", True):
            logger.info(f"  ⊘ Node #{node_id} ({node_config['name']}): INACTIVE\n")
            continue

        try:
            logger.info(
                f"  📌 Node #{node_id} ({node_config['name']}) @ {node_config['region']}..."
            )

            class SovereignFabricNode:
                pass

            node_instance = SovereignFabricNode()
            node_instance.__name__ = f"sovereign_node_{node_id}"
            node_instance.__version__ = "1.0.0"
            node_instance.__doc__ = (
                f"Sovereign Fabric Node #{node_id}: {node_config['description']}"
            )

            # Create health check closure for this specific node
            async def make_sovereign_health_check(nid: int, nconfig: Dict[str, Any]):
                async def _check():
                    return await check_sovereign_node_health(nid, nconfig)

                return _check

            registered_node_id = await register_service_with_nodedb(
                node_instance,
                f"Sovereign Fabric Node #{node_id}",
                health_check_fn=await make_sovereign_health_check(node_id, node_config),
            )
            sovereign_fabric_nodes[node_id] = registered_node_id
            registered[f"sovereign-node-{node_id}"] = registered_node_id

            logger.info(f"    ✓ Node #{node_id} registered: {registered_node_id}")
            logger.info(
                f"       Region: {node_config['region']} | "
                f"Radius: {node_config['radius_km']}km\n"
            )
        except Exception as e:
            logger.error(f"    ✗ Node #{node_id} registration failed: {e}\n")

    logger.info("=" * 80)
    logger.info(
        f"✅ REAL SERVICE REGISTRATION COMPLETE: {len(registered)}/{len(SERVICE_ENDPOINTS)} services + {len(sovereign_fabric_nodes)} sovereign nodes"
    )
    logger.info("=" * 80 + "\n")

    return {
        "nodedb": nodedb,
        "services": registered,
        "sovereign_nodes": sovereign_fabric_nodes,
        "available_count": len(registered),
    }


# ============================================================================
# REAL DATA MONITORING & REPORTING
# ============================================================================


async def monitor_real_services(context: Dict[str, Any]):
    """Monitor all real services and report actual health data"""

    logger.info("\n" + "=" * 80)
    logger.info("📊 REAL SERVICE HEALTH MONITORING")
    logger.info("=" * 80 + "\n")

    # Perform health checks
    logger.info("🔍 Running health checks on all services...\n")

    api_health = await check_api_health()
    ocean_health = await check_ocean_core_health()
    trinity_health = await check_trinity_health()
    jona_sandbox_health = await check_jona_sandbox_health()
    database_health = await check_database_health()

    # Monitor sovereign fabric nodes
    sovereign_nodes_health = {}
    if context.get("sovereign_nodes"):
        logger.info("🔍 Running health checks on sovereign fabric nodes...\n")
        for node_id, node_config in SOVEREIGN_FABRIC_NODES.items():
            if node_config.get("active", True):
                try:
                    node_health = await check_sovereign_node_health(
                        node_id, node_config
                    )
                    sovereign_nodes_health[node_id] = node_health
                except Exception as e:
                    logger.error(f"Failed to check Sovereign Node #{node_id}: {e}")
                    sovereign_nodes_health[node_id] = {
                        "status": "error",
                        "node_id": node_id,
                        "error": str(e),
                        "quality_score": 0.0,
                    }

    # Sync the latest health outputs into NodeDB states.
    await sync_health_to_nodedb(
        context,
        api_health,
        ocean_health,
        trinity_health,
        jona_sandbox_health,
    )

    # Sync sovereign node health to NodeDB
    if sovereign_nodes_health:
        await sync_sovereign_nodes_to_nodedb(context, sovereign_nodes_health)

    logger.info("\n" + "=" * 80)
    logger.info("📈 HEALTH CHECK RESULTS")
    logger.info("=" * 80)

    # API Status
    logger.info("\n🔹 API Backend:")
    if api_health["status"] == "healthy":
        logger.info("   Status: ✅ HEALTHY")
        logger.info(f"   Response Time: {api_health['response_time_ms']:.1f}ms")
        logger.info(f"   Quality Score: {api_health['quality_score']:.2f}")
    else:
        logger.info(f"   Status: ❌ ERROR - {api_health.get('error', 'unknown')}")

    # Ocean Core Status
    logger.info("\n🔹 Ocean Core:")
    if ocean_health["status"] == "healthy":
        logger.info("   Status: ✅ HEALTHY")
        logger.info(f"   Response Time: {ocean_health['response_time_ms']:.1f}ms")
        logger.info(f"   Quality Score: {ocean_health['quality_score']:.2f}")
    else:
        logger.info(f"   Status: ❌ ERROR - {ocean_health.get('error', 'unknown')}")

    # Trinity Status
    logger.info("\n🔹 ASI Trinity:")
    logger.info(
        f"   Overall: {'✅ HEALTHY' if trinity_health['all_components_healthy'] else '⚠️  DEGRADED'}"
    )
    logger.info(f"   Coherence: {trinity_health['coherence']:.2f}")
    logger.info(f"   Quality Score: {trinity_health['quality_score']:.2f}")
    for component, comp_status in trinity_health["trinity_status"].items():
        status_icon = "✅" if comp_status["status"] == "healthy" else "❌"
        logger.info(
            f"   {component.upper()}: {status_icon} {comp_status.get('status', 'unknown')}"
        )

    # Database Status
    logger.info("\n🔹 Databases:")
    for db_name, db_info in database_health.items():
        status_icon = "✅" if db_info["status"] == "healthy" else "❌"
        logger.info(f"   {db_name.upper()}: {status_icon} {db_info['status']}")

    # Sovereign Fabric Nodes Status
    if sovereign_nodes_health:
        logger.info("\n🔹 Sovereign Fabric Nodes (Multi-Node Architecture):")
        for node_id in sorted(sovereign_nodes_health.keys()):
            node_health = sovereign_nodes_health[node_id]
            if node_health.get("status") == "healthy":
                status_icon = "✅"
            elif node_health.get("status") == "degraded":
                status_icon = "⚠️ "
            elif node_health.get("status") == "error":
                status_icon = "❌"
            else:
                status_icon = "❓"

            tide = node_health.get("tide", "critical")
            tide_icon = "🟢" if tide == "low" else "🟡" if tide == "normal" else "🔴"
            ndb_score = node_health.get("ndb_score", 0.0)
            security = node_health.get("security_posture", "unknown")
            latency_ms = node_health.get("response_time_ms", 0)
            bandwidth = node_health.get("bandwidth_kbps", 0.0)
            region = node_health.get("region", "?")
            node_name = node_health.get("node_name", f"Node #{node_id}")

            logger.info(f"\n   {status_icon} Node #{node_id} ({node_name})")
            logger.info(f"       Region: {region} | TIDE: {tide_icon}{tide.upper()}")
            logger.info(
                f"       NDB Score: {ndb_score:.3f} | Security: {security.upper()}"
            )
            logger.info(
                f"       Latency: {latency_ms:.1f}ms | Bandwidth: {bandwidth:.1f}kbps"
            )

    logger.info("\n" + "=" * 80)
    logger.info(f"⏰ Health check completed at {datetime.utcnow().isoformat()}Z")
    logger.info("=" * 80)


def _quality_from_score(score: float) -> NDBQuality:
    if score >= 0.90:
        return NDBQuality.EXCELLENT
    if score >= 0.75:
        return NDBQuality.GOOD
    if score >= 0.50:
        return NDBQuality.FAIR
    if score >= 0.20:
        return NDBQuality.POOR
    return NDBQuality.CRITICAL


def _state_from_health(health_status: str) -> StigmaState:
    status = str(health_status).lower()
    if status == "healthy":
        return StigmaState.ACTIVE
    if status == "degraded":
        return StigmaState.DEGRADED
    if status == "initializing":
        return StigmaState.INITIALIZING
    return StigmaState.RECOVERING


async def sync_health_to_nodedb(
    context: Dict[str, Any],
    api_health: Dict[str, Any],
    ocean_health: Dict[str, Any],
    trinity_health: Dict[str, Any],
    jona_sandbox_health: Dict[str, Any],
) -> None:
    """Synchronize real service health output into NodeDB in near real-time."""

    nodedb = get_nodedb()
    services = context.get("services", {})

    sync_plan = [
        ("api", api_health),
        ("ocean-core", ocean_health),
        ("asi-trinity", trinity_health),
        ("jona-sandbox", jona_sandbox_health),
    ]

    for service_key, health in sync_plan:
        node_id = services.get(service_key)
        if not node_id:
            continue

        quality_score = float(health.get("quality_score", 0.0))
        stigma_state = _state_from_health(health.get("status", "error"))
        ndb_quality = _quality_from_score(quality_score)

        metrics = {
            "status": health.get("status", "unknown"),
            "quality_score": quality_score,
            "response_time_ms": health.get(
                "response_time_ms", health.get("avg_response_time_ms", 0)
            ),
            "synced_at": datetime.utcnow().isoformat() + "Z",
        }

        await nodedb.update_node_state(
            node_id=node_id,
            state=stigma_state,
            metrics=metrics,
            ndb_quality=ndb_quality,
        )


async def sync_sovereign_nodes_to_nodedb(
    context: Dict[str, Any], sovereign_nodes_health: Dict[int, Dict[str, Any]]
) -> None:
    """
    Synchronize sovereign fabric node health into NodeDB.
    Tracks: TIDE, NDB Score, Security Posture, Latency, Bandwidth, CRDT state.
    """
    nodedb = get_nodedb()
    sovereign_nodes = context.get("sovereign_nodes", {})

    for node_id, health in sovereign_nodes_health.items():
        node_registered_id = sovereign_nodes.get(node_id)
        if not node_registered_id:
            continue

        quality_score = float(health.get("quality_score", 0.0))
        stigma_state = _state_from_health(health.get("status", "error"))
        ndb_quality = _quality_from_score(quality_score)

        metrics = {
            "node_id": node_id,
            "status": health.get("status", "unknown"),
            "quality_score": quality_score,
            "ndb_score": health.get("ndb_score", 0.0),
            "tide": health.get("tide", "critical"),
            "security_posture": health.get("security_posture", "unknown"),
            "response_time_ms": health.get("response_time_ms", 0),
            "bandwidth_kbps": health.get("bandwidth_kbps", 0.0),
            "utilization_pct": health.get("utilization_pct", 0.0),
            "crdt_cardinality": health.get("crdt_cardinality", 0),
            "events_tracked": health.get("events_tracked", 0),
            "stigma_state": health.get("stigma_state", "unknown"),
            "region": health.get("region", "unknown"),
            "radius_km": health.get("radius_km", 0),
            "synced_at": datetime.utcnow().isoformat() + "Z",
        }

        await nodedb.update_node_state(
            node_id=node_registered_id,
            state=stigma_state,
            metrics=metrics,
            ndb_quality=ndb_quality,
        )

        logger.debug(
            f"✓ Sovereign Node #{node_id} synced: "
            f"TIDE={health.get('tide')} | NDB={health.get('ndb_score', 0.0):.3f}"
        )


async def run_health_sync_loop(
    context: Dict[str, Any], interval_seconds: int = 5
) -> None:
    """Continuous control loop for fluid, non-aggressive state synchronization."""

    logger.info(
        f"🔁 Starting health-to-NodeDB sync loop ({interval_seconds}s interval)"
    )
    while True:
        try:
            await monitor_real_services(context)
        except Exception as exc:
            logger.error(f"❌ Health sync loop error: {exc}")
        await asyncio.sleep(max(1, interval_seconds))


# ============================================================================
# MAIN EXECUTION - REAL DATA ONLY
# ============================================================================


async def main():
    """Real service integration entry point"""

    logger.info("\n" + "=" * 80)
    logger.info("🌐 KLOUD NODEDB REAL SERVICE INTEGRATION")
    logger.info("=" * 80)
    logger.info("\nThis integration uses ONLY real services - no mocks, no fakes.")
    logger.info("All data comes from actual running Kloud services.\n")

    # Initialize with real services
    context = await initialize_kloud_nodedb_real()

    if context["available_count"] == 0:
        logger.critical("Cannot proceed: no services available")
        return

    # Monitor and synchronize real services once by default.
    await monitor_real_services(context)

    logger.info("\n✅ Real service integration complete.")
    logger.info(f"   Registered {context['available_count']} real services")
    sovereign_count = len(context.get("sovereign_nodes", {}))
    if sovereign_count > 0:
        logger.info(
            f"   Registered {sovereign_count} sovereign fabric nodes (scalable)"
        )
    logger.info("   All data is from actual running services\n")


if __name__ == "__main__":
    asyncio.run(main())
