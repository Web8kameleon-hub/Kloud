"""
NODENDB STIGMA PATTERN
======================
Universal node database system that adapts to any package through
dynamic introspection and stigma pattern matching.

Instead of rigid node scripts, this implements a fluid pattern that
discovers and adapts to every service's actual structure.
"""

import inspect
import json
import asyncio
from typing import Any, Dict, List, Optional, Type, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from enum import Enum
import hashlib
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StigmaState(str, Enum):
    """Stigma state enumeration for node lifecycle"""

    INITIALIZING = "initializing"
    READY = "ready"
    ACTIVE = "active"
    DEGRADED = "degraded"
    RECOVERING = "recovering"
    OFFLINE = "offline"


class NDBQuality(str, Enum):
    """NDB resonance quality signals"""

    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"


@dataclass
class NodeMetadata:
    """Metadata for any node type - extracted dynamically"""

    node_id: str
    service_name: str
    service_type: str
    package_name: str
    version: str
    capabilities: List[str] = field(default_factory=list)
    interfaces: Dict[str, Any] = field(default_factory=dict)
    requirements: Dict[str, Any] = field(default_factory=dict)
    health_checks: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class NodeState:
    """Runtime state of a node"""

    node_id: str
    stigma_state: StigmaState
    ndb_quality: NDBQuality
    timestamp: datetime
    metrics: Dict[str, Any] = field(default_factory=dict)
    ndb_delta: float = 0.0  # Change in NDB quality
    tide_pressure: float = 0.5  # 0.0-1.0, higher = more pressure
    last_heartbeat: Optional[datetime] = None
    consecutive_failures: int = 0
    recovery_attempts: int = 0

    def to_dict(self) -> Dict:
        return {
            **asdict(self),
            "timestamp": self.timestamp.isoformat(),
            "last_heartbeat": self.last_heartbeat.isoformat()
            if self.last_heartbeat
            else None,
            "stigma_state": self.stigma_state.value,
            "ndb_quality": self.ndb_quality.value,
        }


class StigmaPattern:
    """
    Stigma Pattern: Dynamic introspection engine that adapts to any package
    structure without hardcoding node types.
    """

    def __init__(self, service_module: Any, service_name: str):
        """
        Initialize stigma pattern from a live service module.

        Args:
            service_module: The imported service/package module
            service_name: Human-readable service name
        """
        self.service_module = service_module
        self.service_name = service_name
        self.metadata = self._introspect_package()

    def _introspect_package(self) -> NodeMetadata:
        """
        Dynamically introspect the package to extract:
        - Service type (Flask, FastAPI, Django, etc.)
        - Available endpoints/methods
        - Configuration options
        - Health check patterns
        """
        module_name = self.service_module.__name__
        package_name = module_name.split(".")[0]

        # Detect service type by inspection
        service_type = self._detect_service_type()

        # Extract capabilities (public methods/endpoints)
        capabilities = self._extract_capabilities()

        # Extract interfaces (functions, classes)
        interfaces = self._extract_interfaces()

        # Extract requirements
        requirements = self._extract_requirements()

        # Find health check patterns
        health_checks = self._find_health_checks()

        node_id = self._generate_node_id(package_name, service_type)

        version = getattr(self.service_module, "__version__", "0.0.0")

        return NodeMetadata(
            node_id=node_id,
            service_name=self.service_name,
            service_type=service_type,
            package_name=package_name,
            version=version,
            capabilities=capabilities,
            interfaces=interfaces,
            requirements=requirements,
            health_checks=health_checks,
        )

    def _detect_service_type(self) -> str:
        """Detect service framework (FastAPI, Flask, Django, etc.)"""
        module_name = self.service_module.__name__.lower()

        if "fastapi" in str(self.service_module.__dict__):
            return "FastAPI"
        elif "flask" in module_name:
            return "Flask"
        elif "django" in module_name:
            return "Django"
        elif "grpc" in module_name:
            return "gRPC"
        elif "async" in module_name or asyncio.iscoroutinefunction(
            getattr(self.service_module, "main", None)
        ):
            return "AsyncIO"
        else:
            return "Generic"

    def _extract_capabilities(self) -> List[str]:
        """Extract public methods/endpoints"""
        capabilities = []

        for name, obj in inspect.getmembers(self.service_module):
            if name.startswith("_"):
                continue

            if inspect.isfunction(obj) or inspect.ismethod(obj):
                capabilities.append(f"function:{name}")
            elif inspect.isclass(obj):
                capabilities.append(f"class:{name}")
            elif inspect.ismodule(obj):
                capabilities.append(f"module:{name}")

        return capabilities

    def _extract_interfaces(self) -> Dict[str, Any]:
        """Extract method signatures and class definitions"""
        interfaces = {}

        for name, obj in inspect.getmembers(self.service_module):
            if name.startswith("_"):
                continue

            if inspect.isfunction(obj):
                sig = inspect.signature(obj)
                interfaces[name] = {
                    "type": "function",
                    "signature": str(sig),
                    "params": list(sig.parameters.keys()),
                    "return_annotation": str(sig.return_annotation),
                }
            elif inspect.isclass(obj):
                methods = [m for m in dir(obj) if not m.startswith("_")]
                interfaces[name] = {
                    "type": "class",
                    "methods": methods,
                }

        return interfaces

    def _extract_requirements(self) -> Dict[str, Any]:
        """Extract configuration and requirements"""
        requirements = {}

        # Check for common config attributes
        config_attrs = ["config", "settings", "CONFIG", "SETTINGS"]
        for attr in config_attrs:
            if hasattr(self.service_module, attr):
                cfg = getattr(self.service_module, attr)
                if isinstance(cfg, dict):
                    requirements["config"] = cfg

        # Check for environment variable patterns
        env_vars = {}
        for name, obj in inspect.getmembers(self.service_module):
            if isinstance(obj, str) and name.isupper():
                env_vars[name] = obj

        if env_vars:
            requirements["env_vars"] = env_vars

        return requirements

    def _find_health_checks(self) -> List[str]:
        """Find health check patterns in module"""
        patterns = ["health", "status", "ping", "ready", "liveness", "readiness"]
        found = []

        for name in dir(self.service_module):
            name_lower = name.lower()
            if any(pattern in name_lower for pattern in patterns):
                found.append(name)

        return found

    def _generate_node_id(self, package_name: str, service_type: str) -> str:
        """Generate unique node ID from package and service type"""
        base = f"{package_name}:{service_type}:{datetime.utcnow().isoformat()}"
        node_hash = hashlib.sha256(base.encode()).hexdigest()[:12]
        return f"node-{node_hash}"


class NodeDBCore:
    """
    NodeDB Core: Central repository of all nodes with stigma pattern adaptation.
    Replaces rigid per-service node definitions with fluid, adaptive tracking.
    """

    def __init__(self):
        self.nodes: Dict[str, NodeMetadata] = {}
        self.states: Dict[str, NodeState] = {}
        self.stigma_patterns: Dict[str, StigmaPattern] = {}
        self.ndb_quality_baseline = 0.95
        self.tide_pressure = 0.5
        self.lock = asyncio.Lock()

    async def register_service(
        self,
        service_module: Any,
        service_name: str,
        health_check_fn: Optional[Callable] = None,
    ) -> NodeMetadata:
        """
        Register any service dynamically using stigma pattern analysis.

        Args:
            service_module: The service module to register
            service_name: Human-readable name
            health_check_fn: Optional async function that returns health status

        Returns:
            NodeMetadata describing the discovered service
        """
        async with self.lock:
            # Analyze service through stigma pattern
            pattern = StigmaPattern(service_module, service_name)
            node_id = pattern.metadata.node_id

            # Store metadata
            self.nodes[node_id] = pattern.metadata
            self.stigma_patterns[node_id] = pattern

            # Initialize state
            self.states[node_id] = NodeState(
                node_id=node_id,
                stigma_state=StigmaState.INITIALIZING,
                ndb_quality=NDBQuality.FAIR,
                timestamp=datetime.utcnow(),
            )

            logger.info(f"✅ Registered node: {node_id} ({service_name})")

            # Store health check function if provided
            if health_check_fn:
                setattr(pattern, "health_check_fn", health_check_fn)

            return pattern.metadata

    async def update_node_state(
        self,
        node_id: str,
        state: StigmaState,
        metrics: Optional[Dict[str, Any]] = None,
        ndb_quality: Optional[NDBQuality] = None,
    ) -> NodeState:
        """
        Update node's stigma state and NDB quality.

        Args:
            node_id: ID of node to update
            state: New stigma state
            metrics: Runtime metrics (latency, errors, etc.)
            ndb_quality: NDB resonance quality signal

        Returns:
            Updated NodeState
        """
        async with self.lock:
            if node_id not in self.states:
                raise ValueError(f"Unknown node: {node_id}")

            current = self.states[node_id]

            # Calculate NDB delta
            old_quality = self._quality_to_float(current.ndb_quality)
            new_quality = (
                self._quality_to_float(ndb_quality) if ndb_quality else old_quality
            )
            ndb_delta = new_quality - old_quality

            # Update state
            self.states[node_id] = NodeState(
                node_id=node_id,
                stigma_state=state,
                ndb_quality=ndb_quality or current.ndb_quality,
                timestamp=datetime.utcnow(),
                metrics=metrics or current.metrics,
                ndb_delta=ndb_delta,
                tide_pressure=self.tide_pressure,
                last_heartbeat=datetime.utcnow(),
                consecutive_failures=0
                if state == StigmaState.ACTIVE
                else current.consecutive_failures + 1,
            )

            logger.info(
                f"🔄 Updated {node_id}: {state.value} (NDB: {self._quality_to_float(ndb_quality):.2f})"
            )

            return self.states[node_id]

    async def trigger_recovery(self, node_id: str) -> NodeState:
        """
        Trigger recovery workflow for degraded node.
        Uses stigma pattern to determine recovery path.
        """
        if node_id not in self.states:
            raise ValueError(f"Unknown node: {node_id}")

        current = self.states[node_id]
        recovery_attempts = current.recovery_attempts + 1

        logger.warning(
            f"⚠️ Recovery triggered for {node_id} (attempt {recovery_attempts})"
        )

        # Update to recovering state
        return await self.update_node_state(
            node_id,
            state=StigmaState.RECOVERING,
            ndb_quality=NDBQuality.POOR,
        )

    @staticmethod
    def _quality_to_float(quality: NDBQuality) -> float:
        """Convert NDB quality enum to float (0.0-1.0)"""
        mapping = {
            NDBQuality.EXCELLENT: 1.0,
            NDBQuality.GOOD: 0.8,
            NDBQuality.FAIR: 0.6,
            NDBQuality.POOR: 0.3,
            NDBQuality.CRITICAL: 0.0,
        }
        return mapping.get(quality, 0.5)

    async def get_node_info(self, node_id: str) -> Dict[str, Any]:
        """Get complete node information (metadata + state)"""
        if node_id not in self.nodes:
            raise ValueError(f"Unknown node: {node_id}")

        metadata = self.nodes[node_id].to_dict()
        state = self.states[node_id].to_dict()

        return {
            "metadata": metadata,
            "state": state,
        }

    async def list_nodes(self) -> List[Dict[str, Any]]:
        """List all registered nodes with their current state"""
        nodes = []
        for node_id in self.nodes:
            nodes.append(await self.get_node_info(node_id))
        return nodes

    async def health_check(self, node_id: str) -> Dict[str, Any]:
        """
        Execute health check for a node using its registered function.
        Falls back to basic state checks if no custom function.
        """
        if node_id not in self.nodes:
            raise ValueError(f"Unknown node: {node_id}")

        pattern = self.stigma_patterns[node_id]
        metadata = self.nodes[node_id]

        result = {
            "node_id": node_id,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {},
        }

        # Custom health check if available
        if hasattr(pattern, "health_check_fn"):
            try:
                custom_result = await pattern.health_check_fn()
                result["checks"]["custom"] = custom_result
            except Exception as e:
                logger.error(f"Health check failed for {node_id}: {e}")
                result["checks"]["custom"] = {"status": "error", "error": str(e)}

        # Check known endpoints from introspection
        for endpoint in metadata.health_checks:
            result["checks"][endpoint] = {"status": "detected", "type": "endpoint"}

        return result

    async def simulate_tide_pressure(self, pressure: float) -> None:
        """
        Simulate system-wide tide pressure (0.0-1.0).
        Affects all nodes' resource availability and recovery behavior.
        """
        self.tide_pressure = max(0.0, min(1.0, pressure))

        # Update all nodes' tide pressure
        async with self.lock:
            for node_id in self.states:
                self.states[node_id].tide_pressure = self.tide_pressure

        logger.info(f"🌊 Tide pressure updated: {self.tide_pressure:.2f}")


class NodeDBClient:
    """
    Client interface for NodeDB - used by services to report state and metrics.
    """

    def __init__(self, core: NodeDBCore, node_id: str):
        self.core = core
        self.node_id = node_id

    async def set_state(
        self,
        state: StigmaState,
        metrics: Optional[Dict[str, Any]] = None,
        ndb_quality: Optional[NDBQuality] = None,
    ):
        """Service reports its current state"""
        return await self.core.update_node_state(
            self.node_id,
            state,
            metrics,
            ndb_quality,
        )

    async def report_metric(self, metric_name: str, value: float) -> None:
        """Service reports a performance metric"""
        state = self.core.states[self.node_id]
        state.metrics[metric_name] = {
            "value": value,
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def request_recovery(self) -> None:
        """Service signals that it needs recovery"""
        await self.core.trigger_recovery(self.node_id)


# ============================================================================
# GLOBAL NODEDB INSTANCE
# ============================================================================

_global_nodedb: Optional[NodeDBCore] = None


async def initialize_nodendb() -> NodeDBCore:
    """Initialize global NodeDB instance"""
    global _global_nodedb
    _global_nodedb = NodeDBCore()
    logger.info("🚀 NodeDB Stigma Pattern initialized")
    return _global_nodedb


def get_nodedb() -> NodeDBCore:
    """Get global NodeDB instance"""
    global _global_nodedb
    if _global_nodedb is None:
        raise RuntimeError("NodeDB not initialized. Call initialize_nodendb() first.")
    return _global_nodedb


async def register_service_with_nodedb(
    service_module: Any,
    service_name: str,
    health_check_fn: Optional[Callable] = None,
) -> str:
    """
    Convenience function to register a service with global NodeDB.

    Returns:
        node_id of registered service
    """
    nodedb = get_nodedb()
    metadata = await nodedb.register_service(
        service_module, service_name, health_check_fn
    )
    return metadata.node_id


# ============================================================================
# EXAMPLE USAGE
# ============================================================================


async def example_usage():
    """Demonstration of NodeDB Stigma Pattern"""

    # Initialize global NodeDB
    nodedb = await initialize_nodendb()

    # Simulate registering different services
    # In real usage, you'd pass actual service modules

    class MockFastAPIService:
        __name__ = "fastapi_service"
        __version__ = "1.0.0"

        def health():
            pass

        def status():
            pass

    class MockAsyncService:
        __name__ = "async_service"
        __version__ = "2.1.0"

        async def process():
            pass

    # Register services
    api_metadata = await nodedb.register_service(
        MockFastAPIService(), "FastAPI Backend"
    )
    async_metadata = await nodedb.register_service(MockAsyncService(), "Async Worker")

    print("\n📊 Registered Nodes:")
    for node in await nodedb.list_nodes():
        print(f"  - {node['metadata']['node_id']}: {node['metadata']['service_name']}")

    # Simulate state updates
    print("\n🔄 Simulating state transitions...")

    await nodedb.update_node_state(
        api_metadata.node_id,
        StigmaState.READY,
        metrics={"latency_ms": 10, "error_rate": 0.01},
        ndb_quality=NDBQuality.GOOD,
    )

    await nodedb.update_node_state(
        async_metadata.node_id,
        StigmaState.ACTIVE,
        metrics={"throughput_rps": 1000, "memory_mb": 512},
        ndb_quality=NDBQuality.EXCELLENT,
    )

    # Simulate tide pressure
    print("\n🌊 Simulating tide pressure increase...")
    await nodedb.simulate_tide_pressure(0.8)

    # Final state
    print("\n✅ Final Node States:")
    for node in await nodedb.list_nodes():
        state = node["state"]
        print(
            f"  {state['node_id']}: {state['stigma_state']} (NDB: {state['ndb_quality']})"
        )


if __name__ == "__main__":
    asyncio.run(example_usage())
