"""
NODENDB STIGMA PATTERN
======================
Universal node database system that adapts to any package through
dynamic introspection and stigma pattern matching.

Instead of rigid node scripts, this implements a fluid pattern that
discovers and adapts to every service's actual structure.
"""

import inspect
import asyncio
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime
from dataclasses import dataclass, asdict, field
from enum import Enum
import hashlib
import logging
import json
import os
from pathlib import Path

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

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "NodeMetadata":
        return NodeMetadata(
            node_id=str(data.get("node_id", "")),
            service_name=str(data.get("service_name", "")),
            service_type=str(data.get("service_type", "Generic")),
            package_name=str(data.get("package_name", "unknown")),
            version=str(data.get("version", "0.0.0")),
            capabilities=list(data.get("capabilities", [])),
            interfaces=dict(data.get("interfaces", {})),
            requirements=dict(data.get("requirements", {})),
            health_checks=list(data.get("health_checks", [])),
        )


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

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "NodeState":
        timestamp_raw = data.get("timestamp")
        last_hb_raw = data.get("last_heartbeat")

        timestamp = (
            datetime.fromisoformat(timestamp_raw)
            if isinstance(timestamp_raw, str) and timestamp_raw
            else datetime.utcnow()
        )
        last_heartbeat = (
            datetime.fromisoformat(last_hb_raw)
            if isinstance(last_hb_raw, str) and last_hb_raw
            else None
        )

        stigma_value = str(data.get("stigma_state", StigmaState.INITIALIZING.value))
        quality_value = str(data.get("ndb_quality", NDBQuality.FAIR.value))

        try:
            stigma_state = StigmaState(stigma_value)
        except ValueError:
            stigma_state = StigmaState.INITIALIZING

        try:
            ndb_quality = NDBQuality(quality_value)
        except ValueError:
            ndb_quality = NDBQuality.FAIR

        return NodeState(
            node_id=str(data.get("node_id", "")),
            stigma_state=stigma_state,
            ndb_quality=ndb_quality,
            timestamp=timestamp,
            metrics=dict(data.get("metrics", {})),
            ndb_delta=float(data.get("ndb_delta", 0.0)),
            tide_pressure=float(data.get("tide_pressure", 0.5)),
            last_heartbeat=last_heartbeat,
            consecutive_failures=int(data.get("consecutive_failures", 0)),
            recovery_attempts=int(data.get("recovery_attempts", 0)),
        )


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
        self.health_check_fn: Optional[Callable[[], Any]] = None
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
        """Generate stable node ID from package, service type, and service name."""
        base = (
            f"{package_name.strip().lower()}:"
            f"{service_type.strip().lower()}:"
            f"{self.service_name.strip().lower()}"
        )
        node_hash = hashlib.sha256(base.encode()).hexdigest()[:12]
        return f"node-{node_hash}"


class NodeDBCore:
    """
    NodeDB Core: Central repository of all nodes with stigma pattern adaptation.
    Replaces rigid per-service node definitions with fluid, adaptive tracking.
    """

    def __init__(self, snapshot_path: Optional[str] = None):
        self.nodes: Dict[str, NodeMetadata] = {}
        self.states: Dict[str, NodeState] = {}
        self.stigma_patterns: Dict[str, StigmaPattern] = {}
        self.ndb_quality_baseline = 0.95
        self.tide_pressure = 0.5
        self.lock = asyncio.Lock()
        base_path: str = (
            snapshot_path
            if snapshot_path is not None
            else os.getenv(
                "NODENDB_SNAPSHOT_PATH", "output/nodedb/nodedb_snapshot.json"
            )
        )
        self.snapshot_path = Path(base_path)
        self.snapshot_path.parent.mkdir(parents=True, exist_ok=True)

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

            # Reuse existing node id by service name to avoid duplicate/stale rows.
            for existing_id, existing_meta in self.nodes.items():
                if existing_meta.service_name == service_name:
                    node_id = existing_id
                    pattern.metadata.node_id = existing_id
                    break

            # Store metadata
            self.nodes[node_id] = pattern.metadata
            self.stigma_patterns[node_id] = pattern

            # Initialize state only if missing; keep current state for existing nodes.
            if node_id not in self.states:
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

            self._save_snapshot()

            return pattern.metadata

    async def dedupe_nodes(self) -> Dict[str, int]:
        """Remove duplicate node rows by service name and keep the best candidate."""
        async with self.lock:
            before = len(self.nodes)
            if before <= 1:
                return {"before": before, "after": before, "removed": 0}

            state_rank = {
                StigmaState.ACTIVE.value: 6,
                StigmaState.READY.value: 5,
                StigmaState.RECOVERING.value: 4,
                StigmaState.DEGRADED.value: 3,
                StigmaState.INITIALIZING.value: 2,
                StigmaState.OFFLINE.value: 1,
            }

            by_service: Dict[str, List[str]] = {}
            for node_id, meta in self.nodes.items():
                by_service.setdefault(meta.service_name, []).append(node_id)

            keep_ids = set()
            for _service_name, ids in by_service.items():
                if len(ids) == 1:
                    keep_ids.add(ids[0])
                    continue

                def score(node_id: str) -> tuple[int, datetime]:
                    st = self.states.get(node_id)
                    if st is None:
                        return (0, datetime.min)
                    rank = state_rank.get(st.stigma_state.value, 0)
                    return (rank, st.timestamp)

                best = max(ids, key=score)
                keep_ids.add(best)

            self.nodes = {
                node_id: meta
                for node_id, meta in self.nodes.items()
                if node_id in keep_ids
            }
            self.states = {
                node_id: st
                for node_id, st in self.states.items()
                if node_id in keep_ids
            }
            self.stigma_patterns = {
                node_id: p
                for node_id, p in self.stigma_patterns.items()
                if node_id in keep_ids
            }

            after = len(self.nodes)
            removed = max(0, before - after)
            if removed:
                logger.info(f"🧹 NodeDB dedupe removed {removed} stale duplicate nodes")
                self._save_snapshot()

            return {"before": before, "after": after, "removed": removed}

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
            effective_quality = ndb_quality or current.ndb_quality
            self.states[node_id] = NodeState(
                node_id=node_id,
                stigma_state=state,
                ndb_quality=effective_quality,
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
                f"🔄 Updated {node_id}: {state.value} (NDB: {self._quality_to_float(effective_quality):.2f})"
            )

            self._save_snapshot()

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

        checks: Dict[str, Any] = {}
        result: Dict[str, Any] = {
            "node_id": node_id,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": checks,
        }

        # Custom health check if available
        if pattern.health_check_fn is not None:
            try:
                custom_result = await pattern.health_check_fn()
                checks["custom"] = custom_result
            except Exception as e:
                logger.error(f"Health check failed for {node_id}: {e}")
                checks["custom"] = {"status": "error", "error": str(e)}

        # Check known endpoints from introspection
        for endpoint in metadata.health_checks:
            checks[endpoint] = {"status": "detected", "type": "endpoint"}

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

            self._save_snapshot()

        logger.info(f"🌊 Tide pressure updated: {self.tide_pressure:.2f}")

    def _save_snapshot(self) -> None:
        payload = {
            "timestamp": datetime.utcnow().isoformat(),
            "ndb_quality_baseline": self.ndb_quality_baseline,
            "tide_pressure": self.tide_pressure,
            "nodes": {node_id: meta.to_dict() for node_id, meta in self.nodes.items()},
            "states": {
                node_id: state.to_dict() for node_id, state in self.states.items()
            },
        }
        self.snapshot_path.write_text(
            json.dumps(payload, ensure_ascii=True), encoding="utf-8"
        )

    def load_snapshot(self) -> None:
        if not self.snapshot_path.exists():
            return

        try:
            payload = json.loads(self.snapshot_path.read_text(encoding="utf-8"))
        except Exception as exc:
            logger.warning(f"Could not load NodeDB snapshot: {exc}")
            return

        self.ndb_quality_baseline = float(payload.get("ndb_quality_baseline", 0.95))
        self.tide_pressure = float(payload.get("tide_pressure", 0.5))

        raw_nodes = dict(payload.get("nodes", {}))
        raw_states = dict(payload.get("states", {}))

        self.nodes.clear()
        self.states.clear()
        self.stigma_patterns.clear()

        for node_id, raw_meta in raw_nodes.items():
            try:
                metadata = NodeMetadata.from_dict(raw_meta)
                self.nodes[node_id] = metadata
            except Exception as exc:
                logger.warning(f"Skipping invalid node metadata {node_id}: {exc}")

        for node_id, raw_state in raw_states.items():
            try:
                state = NodeState.from_dict(raw_state)
                self.states[node_id] = state
            except Exception as exc:
                logger.warning(f"Skipping invalid node state {node_id}: {exc}")

        logger.info(
            f"📦 NodeDB snapshot loaded: {len(self.nodes)} nodes, {len(self.states)} states"
        )


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
    _global_nodedb.load_snapshot()
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

        @staticmethod
        def health():
            pass

        @staticmethod
        def status():
            pass

    class MockAsyncService:
        __name__ = "async_service"
        __version__ = "2.1.0"

        @staticmethod
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
