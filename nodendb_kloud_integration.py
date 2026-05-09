"""
NODENDB INTEGRATION EXAMPLE FOR KLOUD SERVICES
===============================================

This module demonstrates how to integrate NodeDB Stigma Pattern with actual Kloud services.
Shows registration, state tracking, and health monitoring for:
- FastAPI Backend (API)
- Ocean Core (ML Engine)
- ASI Trinity (ALBA, ALBI, JONA, ASI)
- Worker Services
- Analytics Engines
"""

import asyncio
import logging
from typing import Optional, Dict, Any
from datetime import datetime
import time
import random

from nodendb_stigma import (
    initialize_nodendb,
    register_service_with_nodedb,
    get_nodedb,
    StigmaState,
    NDBQuality,
    NodeDBClient,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


# ============================================================================
# MOCK SERVICES (Replace with actual imports in real deployment)
# ============================================================================


class MockAPIService:
    """Mock FastAPI Backend Service"""

    __name__ = "api"
    __version__ = "2.3.1"

    async def health(self) -> Dict:
        return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

    async def metrics(self) -> Dict:
        return {
            "requests_total": 150000,
            "errors_total": 45,
            "latency_p99_ms": 125,
            "active_connections": 2500,
        }


class MockOceanCoreService:
    """Mock Ocean Core ML Engine"""

    __name__ = "ocean_core"
    __version__ = "1.8.5"

    async def health(self) -> Dict:
        return {"status": "ok", "model_loaded": True}

    async def metrics(self) -> Dict:
        return {
            "inference_p99_ms": 450,
            "batch_size": 32,
            "gpu_memory_mb": 2048,
            "accuracy": 0.9847,
        }


class MockALBAService:
    """Mock ALBA (ASI Trinity Component)"""

    __name__ = "alba"
    __version__ = "3.1.0"

    async def health(self) -> Dict:
        return {"status": "ok", "frames_processed": 45000}


class MockALBIService:
    """Mock ALBI (ASI Trinity Component)"""

    __name__ = "albi"
    __version__ = "3.1.0"

    async def health(self) -> Dict:
        return {"status": "ok", "cycles_tracked": 12000}


class MockJONAService:
    """Mock JONA (ASI Trinity Component)"""

    __name__ = "jona"
    __version__ = "3.1.0"

    async def health(self) -> Dict:
        return {"status": "ok", "inferences": 50000}


class MockASIService:
    """Mock ASI (ASI Trinity Master Orchestrator)"""

    __name__ = "asi"
    __version__ = "3.1.0"

    async def health(self) -> Dict:
        return {
            "status": "ok",
            "trinity_status": "coherent",
            "resonance_strength": 0.94,
        }


class MockWorkerService:
    """Mock Async Worker Service"""

    __name__ = "worker"
    __version__ = "1.2.0"

    async def process_task(self):
        pass


class MockAnalyticsService:
    """Mock Analytics Engine"""

    __name__ = "analytics"
    __version__ = "2.0.0"

    async def generate_report(self):
        pass


# ============================================================================
# HEALTH CHECK FUNCTIONS
# ============================================================================


async def check_api_health() -> Dict[str, Any]:
    """Custom health check for API"""
    try:
        # In real deployment, would make actual HTTP call
        api_service = MockAPIService()
        health = await api_service.health()
        metrics = await api_service.metrics()

        # Calculate NDB quality based on metrics
        error_rate = metrics["errors_total"] / max(metrics["requests_total"], 1)
        latency_degradation = metrics["latency_p99_ms"] / 200  # 200ms baseline

        # Quality scoring
        quality_score = 1.0 - (error_rate * 0.5) - (latency_degradation * 0.3)
        quality_score = max(0.0, min(1.0, quality_score))

        return {
            "status": "healthy",
            "response_time_ms": 5,
            "error_rate": error_rate,
            "quality_score": quality_score,
            "metrics": metrics,
        }
    except Exception as e:
        logger.error(f"API health check failed: {e}")
        return {"status": "error", "error": str(e)}


async def check_ocean_health() -> Dict[str, Any]:
    """Custom health check for Ocean Core"""
    try:
        ocean = MockOceanCoreService()
        health = await ocean.health()
        metrics = await ocean.metrics()

        # Quality based on model accuracy and inference latency
        quality_score = (
            metrics["accuracy"] * 0.7 + (1.0 - metrics["inference_p99_ms"] / 1000) * 0.3
        )
        quality_score = max(0.0, min(1.0, quality_score))

        return {
            "status": "healthy",
            "model_accuracy": metrics["accuracy"],
            "inference_p99_ms": metrics["inference_p99_ms"],
            "quality_score": quality_score,
        }
    except Exception as e:
        logger.error(f"Ocean health check failed: {e}")
        return {"status": "error", "error": str(e)}


async def check_trinity_health() -> Dict[str, Any]:
    """Custom health check for ASI Trinity"""
    try:
        asi = MockASIService()
        health = await asi.health()

        # Quality based on trinity coherence
        trinity_coherent = health["trinity_status"] == "coherent"
        resonance = health["resonance_strength"]

        quality_score = resonance if trinity_coherent else resonance * 0.5

        return {
            "status": "healthy" if trinity_coherent else "degraded",
            "trinity_status": health["trinity_status"],
            "resonance_strength": resonance,
            "quality_score": quality_score,
        }
    except Exception as e:
        logger.error(f"Trinity health check failed: {e}")
        return {"status": "error", "error": str(e)}


# ============================================================================
# INTEGRATION SETUP
# ============================================================================


async def initialize_kloud_nodedb():
    """
    Initialize NodeDB and register all Kloud services.
    This replaces hardcoded node handlers with adaptive pattern.
    """

    logger.info("=" * 70)
    logger.info("🚀 INITIALIZING KLOUD NODEDB STIGMA PATTERN")
    logger.info("=" * 70)

    # Initialize NodeDB core
    nodedb = await initialize_nodendb()
    logger.info("✅ NodeDB core initialized")

    # Register core services
    logger.info("\n📝 Registering Kloud Services...")

    # 1. API Backend
    api_metadata = await register_service_with_nodedb(
        MockAPIService(), "FastAPI Backend", health_check_fn=check_api_health
    )
    logger.info(f"  ✓ API: {api_metadata.node_id}")

    # 2. Ocean Core ML Engine
    ocean_metadata = await register_service_with_nodedb(
        MockOceanCoreService(),
        "Ocean Core ML Engine",
        health_check_fn=check_ocean_health,
    )
    logger.info(f"  ✓ Ocean: {ocean_metadata.node_id}")

    # 3. ASI Trinity Components
    logger.info("\n📝 Registering ASI Trinity (4 components)...")

    trinity_services = [
        (MockALBAService(), "ALBA - Frame Generator"),
        (MockALBIService(), "ALBI - Cycle Engine"),
        (MockJONAService(), "JONA - Neural Synthesis"),
        (MockASIService(), "ASI - Master Orchestrator", check_trinity_health),
    ]

    trinity_metadata = []
    for service_tuple in trinity_services:
        if len(service_tuple) == 3:
            service, name, health_fn = service_tuple
            metadata = await register_service_with_nodedb(service, name, health_fn)
        else:
            service, name = service_tuple
            metadata = await register_service_with_nodedb(service, name)

        trinity_metadata.append(metadata)
        logger.info(f"  ✓ {name}: {metadata.node_id}")

    # 4. Worker Services
    logger.info("\n📝 Registering Worker Services...")

    worker_metadata = await register_service_with_nodedb(
        MockWorkerService(), "Async Task Worker"
    )
    logger.info(f"  ✓ Worker: {worker_metadata.node_id}")

    # 5. Analytics Engine
    analytics_metadata = await register_service_with_nodedb(
        MockAnalyticsService(), "Analytics Engine"
    )
    logger.info(f"  ✓ Analytics: {analytics_metadata.node_id}")

    return {
        "nodedb": nodedb,
        "api": api_metadata,
        "ocean": ocean_metadata,
        "trinity": trinity_metadata,
        "worker": worker_metadata,
        "analytics": analytics_metadata,
    }


# ============================================================================
# STATE SIMULATION
# ============================================================================


async def simulate_service_states(nodedb):
    """Simulate realistic service state changes"""

    logger.info("\n" + "=" * 70)
    logger.info("🔄 SIMULATING SERVICE STATE CHANGES")
    logger.info("=" * 70)

    # Get node IDs
    nodes = await nodedb.list_nodes()
    node_ids = [n["metadata"]["node_id"] for n in nodes]

    # Phase 1: All services ready
    logger.info("\n📋 Phase 1: Services Ready")
    for i, node_id in enumerate(node_ids):
        node = next(n for n in nodes if n["metadata"]["node_id"] == node_id)
        await nodedb.update_node_state(
            node_id,
            state=StigmaState.READY,
            metrics={
                "startup_time_ms": 100 + random.randint(0, 200),
                "config_loaded": True,
            },
            ndb_quality=NDBQuality.GOOD,
        )
        logger.info(f"  ✓ {node['metadata']['service_name']}: READY")

    await asyncio.sleep(1)

    # Phase 2: All services active
    logger.info("\n⚡ Phase 2: Services Active")
    for node_id in node_ids:
        node = next(n for n in nodes if n["metadata"]["node_id"] == node_id)
        await nodedb.update_node_state(
            node_id,
            state=StigmaState.ACTIVE,
            metrics={
                "latency_p99_ms": 15 + random.randint(0, 100),
                "throughput_rps": 500 + random.randint(0, 500),
                "memory_mb": 256 + random.randint(0, 512),
            },
            ndb_quality=NDBQuality.EXCELLENT,
        )
        logger.info(f"  ✓ {node['metadata']['service_name']}: ACTIVE (NDB: EXCELLENT)")

    await asyncio.sleep(2)

    # Phase 3: Simulate Ocean Core degradation
    logger.info("\n⚠️  Phase 3: Ocean Core Degradation Detected")
    ocean_node = next(
        (n for n in nodes if "Ocean" in n["metadata"]["service_name"]), None
    )
    if ocean_node:
        await nodedb.update_node_state(
            ocean_node["metadata"]["node_id"],
            state=StigmaState.DEGRADED,
            metrics={
                "inference_p99_ms": 2500,
                "gpu_memory_mb": 3072,
                "error_rate": 0.12,
            },
            ndb_quality=NDBQuality.POOR,
        )
        logger.warning(f"  ⚠️  Ocean Core degraded (inference latency spike)")

    await asyncio.sleep(1)


# ============================================================================
# MONITORING DASHBOARD
# ============================================================================


async def display_nodedb_dashboard(nodedb):
    """Display live NodeDB monitoring dashboard"""

    logger.info("\n" + "=" * 70)
    logger.info("📊 NODEDB MONITORING DASHBOARD")
    logger.info("=" * 70)

    nodes = await nodedb.list_nodes()

    logger.info(f"\n{'Service':<30} {'State':<12} {'NDB Quality':<12} {'Metrics'}")
    logger.info("-" * 80)

    for node in nodes:
        metadata = node["metadata"]
        state = node["state"]

        service_name = metadata["service_name"][:28]
        node_state = state["stigma_state"]
        ndb_quality = state["ndb_quality"]

        # Format metrics
        metrics_list = []
        for key, value in state["metrics"].items():
            if isinstance(value, dict) and "value" in value:
                metrics_list.append(f"{key}={value['value']:.1f}")
            else:
                metrics_list.append(f"{key}={value}")

        metrics_str = ", ".join(metrics_list[:2])  # Show first 2 metrics

        logger.info(
            f"{service_name:<30} {node_state:<12} {ndb_quality:<12} {metrics_str}"
        )

    logger.info("")


# ============================================================================
# NODEDB CLIENT EXAMPLE
# ============================================================================


class KloudService:
    """Example service using NodeDB Client for self-reporting"""

    def __init__(self, node_id: str, service_name: str):
        self.node_id = node_id
        self.service_name = service_name
        nodedb = get_nodedb()
        self.nodedb_client = NodeDBClient(nodedb, node_id)
        self.tasks_processed = 0
        self.errors = 0

    async def do_work(self):
        """Simulate work and report metrics"""

        try:
            # Simulate work
            start = time.time()
            work_time = random.uniform(10, 100)  # ms
            await asyncio.sleep(work_time / 1000)
            latency = (time.time() - start) * 1000

            self.tasks_processed += 1

            # Report success
            ndb_quality = (
                NDBQuality.EXCELLENT
                if latency < 50
                else NDBQuality.GOOD
                if latency < 100
                else NDBQuality.FAIR
            )

            await self.nodedb_client.set_state(
                StigmaState.ACTIVE,
                metrics={
                    "last_task_ms": latency,
                    "tasks_completed": self.tasks_processed,
                    "error_rate": self.errors / max(self.tasks_processed, 1),
                },
                ndb_quality=ndb_quality,
            )

            logger.info(f"  {self.service_name}: task completed in {latency:.1f}ms")

        except Exception as e:
            logger.error(f"  {self.service_name}: work failed: {e}")
            self.errors += 1
            await self.nodedb_client.request_recovery()


async def demo_nodedb_client():
    """Demonstrate NodeDB Client for self-reporting services"""

    logger.info("\n" + "=" * 70)
    logger.info("🔗 NODEDB CLIENT DEMO (Self-Reporting)")
    logger.info("=" * 70)

    nodedb = get_nodedb()

    # Get first node and create service instance
    nodes = await nodedb.list_nodes()
    if nodes:
        node_id = nodes[0]["metadata"]["node_id"]
        service_name = nodes[0]["metadata"]["service_name"]

        service = KloudService(node_id, service_name)

        logger.info(f"\n📤 Service self-reporting to NodeDB...")
        logger.info(f"   Service: {service_name}")
        logger.info(f"   Node ID: {node_id}\n")

        # Simulate work
        for i in range(3):
            await service.do_work()


# ============================================================================
# MAIN DEMO
# ============================================================================


async def main():
    """Run complete NodeDB Stigma Pattern demo"""

    try:
        # Initialize NodeDB with all services
        services = await initialize_kloud_nodedb()
        nodedb = services["nodedb"]

        # Simulate state changes
        await simulate_service_states(nodedb)

        # Display dashboard
        await display_nodedb_dashboard(nodedb)

        # Demo NodeDB Client
        await demo_nodedb_client()

        # Final dashboard
        logger.info("\n")
        await display_nodedb_dashboard(nodedb)

        # Summary
        logger.info("\n" + "=" * 70)
        logger.info("✅ NODEDB STIGMA PATTERN DEMO COMPLETE")
        logger.info("=" * 70)
        logger.info(f"Total nodes registered: {len(await nodedb.list_nodes())}")
        logger.info("All services tracked by single adaptive pattern ✨")

    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())
