# ============================================================================
# MODULE REGISTRY - Registers all 23 Kloud Modules
# ============================================================================
# All internal modules that feed the AGI Engine
# ============================================================================

import asyncio
import logging
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Any, Callable, Set
from datetime import datetime
import json

logger = logging.getLogger(__name__)

# ============================================================================
# ENUMS AND DATA CLASSES
# ============================================================================

class ModuleStatus(Enum):
    """Module operational status"""
    ACTIVE = "active"
    STANDBY = "standby"
    DEGRADED = "degraded"
    OFFLINE = "offline"
    INITIALIZING = "initializing"
    ERROR = "error"


class ModuleType(Enum):
    """Types of Kloud modules"""
    CORE = "core"                   # Core system (HQ, ALBA, ALBI, JONA)
    DATA_SOURCE = "data_source"     # Data ingestion modules
    ANALYTICS = "analytics"         # Analytics and processing
    ORCHESTRATOR = "orchestrator"   # Orchestration and balancing
    AGENT = "agent"                 # AI agents
    PROTOCOL = "protocol"           # Protocol handlers
    SECURITY = "security"           # Security modules
    UI = "ui"                       # User interface layers
    INTEGRATION = "integration"     # External integrations


class ModuleCapability(Enum):
    """Capabilities that modules can provide"""
    DATA_INGEST = auto()
    DATA_TRANSFORM = auto()
    REASONING = auto()
    SEARCH = auto()
    STREAMING = auto()
    ANALYTICS = auto()
    REPORTING = auto()
    SCHEDULING = auto()
    SECURITY = auto()
    AUTHENTICATION = auto()
    ROUTING = auto()
    BALANCING = auto()
    CACHING = auto()
    PERSISTENCE = auto()
    MESSAGING = auto()
    IOT = auto()
    CBOR = auto()
    TELEMETRY = auto()


@dataclass
class KloudModule:
    """
    Represents a single Kloud module
    
    Each module in the system has:
    - Unique identifier and name
    - Service endpoint (port/URL)
    - List of capabilities
    - Status tracking
    - Metadata for the AGI engine
    """
    id: str
    name: str
    module_type: ModuleType
    port: Optional[int]
    endpoint: str
    capabilities: List[ModuleCapability]
    status: ModuleStatus = ModuleStatus.STANDBY
    version: str = "1.0.0"
    description: str = ""
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    last_health_check: Optional[datetime] = None
    health_score: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert module to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.module_type.value,
            "port": self.port,
            "endpoint": self.endpoint,
            "capabilities": [c.name for c in self.capabilities],
            "status": self.status.value,
            "version": self.version,
            "description": self.description,
            "dependencies": self.dependencies,
            "health_score": self.health_score,
            "last_health_check": self.last_health_check.isoformat() if self.last_health_check else None
        }


# ============================================================================
# MODULE REGISTRY CLASS
# ============================================================================

class ModuleRegistry:
    """
    Central registry for all 23+ Kloud modules
    
    The registry:
    - Maintains state of all modules
    - Routes queries to appropriate modules
    - Tracks health and capabilities
    - Enables AGI engine to access any module
    """
    
    def __init__(self):
        self.modules: Dict[str, KloudModule] = {}
        self.capability_index: Dict[ModuleCapability, List[str]] = {}
        self.type_index: Dict[ModuleType, List[str]] = {}
        self._health_check_interval = 30  # seconds
        self._initialized = False
        
        # Auto-register all core modules
        self._register_core_modules()
    
    def _register_core_modules(self):
        """Register all 23 core Kloud modules"""
        
        # ====================================================================
        # CORE SERVICES (The Trinity + HQ)
        # ====================================================================
        
        self.register(KloudModule(
            id="hq",
            name="HQ Main API",
            module_type=ModuleType.CORE,
            port=8000,
            endpoint="http://localhost:8000",
            capabilities=[
                ModuleCapability.ROUTING,
                ModuleCapability.AUTHENTICATION,
                ModuleCapability.DATA_INGEST
            ],
            description="Main API Gateway - Central control for all services",
            status=ModuleStatus.ACTIVE
        ))
        
        self.register(KloudModule(
            id="alba",
            name="ALBA Streaming Service",
            module_type=ModuleType.CORE,
            port=5555,
            endpoint="http://localhost:5555",
            capabilities=[
                ModuleCapability.STREAMING,
                ModuleCapability.DATA_INGEST,
                ModuleCapability.MESSAGING
            ],
            description="Real-time data streaming and frame generation",
            dependencies=["hq"],
            status=ModuleStatus.ACTIVE
        ))
        
        self.register(KloudModule(
            id="albi",
            name="ALBI Analytics Engine",
            module_type=ModuleType.CORE,
            port=6680,
            endpoint="http://localhost:6680",
            capabilities=[
                ModuleCapability.ANALYTICS,
                ModuleCapability.DATA_TRANSFORM,
                ModuleCapability.REPORTING
            ],
            description="Analytics and intelligence processing",
            dependencies=["hq", "alba"],
            status=ModuleStatus.ACTIVE
        ))
        
        self.register(KloudModule(
            id="jona",
            name="JONA Supervision Layer",
            module_type=ModuleType.CORE,
            port=7777,
            endpoint="http://localhost:7777",
            capabilities=[
                ModuleCapability.REASONING,
                ModuleCapability.SCHEDULING,
                ModuleCapability.ROUTING
            ],
            description="Supervision, orchestration, and cross-module reasoning",
            dependencies=["hq", "alba", "albi"],
            status=ModuleStatus.ACTIVE
        ))
        
        # ====================================================================
        # DATA SOURCES MODULE
        # ====================================================================
        
        self.register(KloudModule(
            id="data_sources",
            name="Global Data Sources",
            module_type=ModuleType.DATA_SOURCE,
            port=None,
            endpoint="internal://data_sources",
            capabilities=[
                ModuleCapability.DATA_INGEST,
                ModuleCapability.SEARCH
            ],
            description="4053+ data sources from 155+ countries, 988 API endpoints",
            metadata={
                "total_sources": 4053,
                "api_sources": 988,
                "countries": 155,
                "regions": [
                    "europe", "asia_china", "india_south_asia",
                    "americas", "africa_middle_east", "asia_oceania",
                    "caribbean_central_america", "pacific_islands",
                    "central_asia_caucasus", "eastern_europe_balkans"
                ]
            },
            status=ModuleStatus.ACTIVE
        ))
        
        # ====================================================================
        # AI & AGENTS
        # ====================================================================
        
        self.register(KloudModule(
            id="agiem",
            name="AGIEM Core",
            module_type=ModuleType.AGENT,
            port=None,
            endpoint="internal://agiem_core",
            capabilities=[
                ModuleCapability.REASONING,
                ModuleCapability.DATA_TRANSFORM
            ],
            description="AGI Engine Module - Core intelligence processing",
            dependencies=["jona"],
            status=ModuleStatus.ACTIVE
        ))
        
        self.register(KloudModule(
            id="agents",
            name="Agent Orchestration",
            module_type=ModuleType.AGENT,
            port=None,
            endpoint="internal://agents",
            capabilities=[
                ModuleCapability.REASONING,
                ModuleCapability.SCHEDULING
            ],
            description="Multi-agent orchestration system",
            dependencies=["agiem", "jona"],
            status=ModuleStatus.ACTIVE
        ))
        
        self.register(KloudModule(
            id="asi",
            name="ASI Realtime Engine",
            module_type=ModuleType.AGENT,
            port=None,
            endpoint="internal://asi_core",
            capabilities=[
                ModuleCapability.REASONING,
                ModuleCapability.ANALYTICS,
                ModuleCapability.STREAMING
            ],
            description="Advanced Superintelligence Interface",
            dependencies=["agiem", "alba"],
            status=ModuleStatus.ACTIVE
        ))
        
        # ====================================================================
        # ORCHESTRATION & BALANCING
        # ====================================================================
        
        self.register(KloudModule(
            id="orchestrator",
            name="SAAS Orchestrator",
            module_type=ModuleType.ORCHESTRATOR,
            port=None,
            endpoint="internal://orchestrator",
            capabilities=[
                ModuleCapability.SCHEDULING,
                ModuleCapability.BALANCING,
                ModuleCapability.ROUTING
            ],
            description="Service orchestration and lifecycle management",
            dependencies=["hq"],
            status=ModuleStatus.ACTIVE
        ))
        
        self.register(KloudModule(
            id="balancer",
            name="Distributed Pulse Balancer",
            module_type=ModuleType.ORCHESTRATOR,
            port=None,
            endpoint="internal://balancer",
            capabilities=[
                ModuleCapability.BALANCING,
                ModuleCapability.ROUTING
            ],
            description="Load balancing and request distribution",
            dependencies=["orchestrator"],
            status=ModuleStatus.ACTIVE
        ))
        
        # ====================================================================
        # PROTOCOL & DATA HANDLING
        # ====================================================================
        
        self.register(KloudModule(
            id="hybrid_protocol",
            name="Hybrid Protocol Pipeline",
            module_type=ModuleType.PROTOCOL,
            port=None,
            endpoint="internal://hybrid_protocol",
            capabilities=[
                ModuleCapability.DATA_TRANSFORM,
                ModuleCapability.CBOR
            ],
            description="Multi-protocol data pipeline with CBOR support",
            dependencies=["alba"],
            status=ModuleStatus.ACTIVE
        ))
        
        self.register(KloudModule(
            id="iot",
            name="IoT Gateway",
            module_type=ModuleType.PROTOCOL,
            port=None,
            endpoint="internal://iot",
            capabilities=[
                ModuleCapability.IOT,
                ModuleCapability.STREAMING,
                ModuleCapability.CBOR
            ],
            description="IoT device communication and data ingestion",
            dependencies=["hybrid_protocol", "alba"],
            status=ModuleStatus.ACTIVE
        ))
        
        self.register(KloudModule(
            id="cbor2",
            name="CBOR2 Encoder",
            module_type=ModuleType.PROTOCOL,
            port=None,
            endpoint="internal://cbor2",
            capabilities=[
                ModuleCapability.CBOR,
                ModuleCapability.DATA_TRANSFORM
            ],
            description="Binary data encoding/decoding with CBOR2",
            dependencies=["hybrid_protocol"],
            status=ModuleStatus.ACTIVE
        ))
        
        # ====================================================================
        # CYCLE ENGINE & LABS
        # ====================================================================
        
        self.register(KloudModule(
            id="cycle_engine",
            name="Cycle Engine",
            module_type=ModuleType.ANALYTICS,
            port=None,
            endpoint="internal://cycle_engine",
            capabilities=[
                ModuleCapability.ANALYTICS,
                ModuleCapability.SCHEDULING
            ],
            description="Temporal cycle analysis and prediction",
            dependencies=["albi"],
            status=ModuleStatus.ACTIVE
        ))
        
        self.register(KloudModule(
            id="labs",
            name="Research Labs",
            module_type=ModuleType.ANALYTICS,
            port=None,
            endpoint="internal://labs",
            capabilities=[
                ModuleCapability.ANALYTICS,
                ModuleCapability.REASONING
            ],
            description="Experimental research and development",
            dependencies=["cycle_engine"],
            status=ModuleStatus.ACTIVE
        ))
        
        # ====================================================================
        # SECURITY & MONITORING
        # ====================================================================
        
        self.register(KloudModule(
            id="security",
            name="Security & DDoS Protection",
            module_type=ModuleType.SECURITY,
            port=None,
            endpoint="internal://security",
            capabilities=[
                ModuleCapability.SECURITY,
                ModuleCapability.AUTHENTICATION
            ],
            description="Security layer with DDoS protection",
            dependencies=["hq"],
            status=ModuleStatus.ACTIVE
        ))
        
        self.register(KloudModule(
            id="telemetry",
            name="Agent Telemetry",
            module_type=ModuleType.ANALYTICS,
            port=None,
            endpoint="internal://telemetry",
            capabilities=[
                ModuleCapability.TELEMETRY,
                ModuleCapability.ANALYTICS
            ],
            description="System-wide telemetry and observability",
            dependencies=["albi"],
            status=ModuleStatus.ACTIVE
        ))
        
        # ====================================================================
        # BILLING & REPORTING
        # ====================================================================
        
        self.register(KloudModule(
            id="billing",
            name="Billing Plans",
            module_type=ModuleType.INTEGRATION,
            port=None,
            endpoint="internal://billing",
            capabilities=[
                ModuleCapability.PERSISTENCE,
                ModuleCapability.REPORTING
            ],
            description="Subscription and billing management",
            status=ModuleStatus.ACTIVE
        ))
        
        self.register(KloudModule(
            id="blerina",
            name="Blerina Reformatter",
            module_type=ModuleType.DATA_SOURCE,
            port=None,
            endpoint="internal://blerina",
            capabilities=[
                ModuleCapability.DATA_TRANSFORM
            ],
            description="Data formatting and normalization",
            dependencies=["data_sources"],
            status=ModuleStatus.ACTIVE
        ))
        
        # ====================================================================
        # NODE & INFRASTRUCTURE
        # ====================================================================
        
        self.register(KloudModule(
            id="nodes_py",
            name="Python Nodes",
            module_type=ModuleType.INTEGRATION,
            port=None,
            endpoint="internal://nodes",
            capabilities=[
                ModuleCapability.ROUTING,
                ModuleCapability.MESSAGING
            ],
            description="Python node infrastructure",
            status=ModuleStatus.ACTIVE
        ))
        
        self.register(KloudModule(
            id="nodes_npm",
            name="NPM Nodes",
            module_type=ModuleType.INTEGRATION,
            port=None,
            endpoint="internal://nodes_npm",
            capabilities=[
                ModuleCapability.ROUTING
            ],
            description="Node.js/NPM infrastructure",
            status=ModuleStatus.ACTIVE
        ))
        
        # ====================================================================
        # UI & TOKENS
        # ====================================================================
        
        self.register(KloudModule(
            id="css_panda_tokens",
            name="CSS Panda Tokens",
            module_type=ModuleType.UI,
            port=None,
            endpoint="internal://css_tokens",
            capabilities=[
                ModuleCapability.DATA_TRANSFORM
            ],
            description="Design system tokens with Panda CSS",
            status=ModuleStatus.ACTIVE
        ))
        
        # ====================================================================
        # PROSPALIS & GENERATION
        # ====================================================================
        
        self.register(KloudModule(
            id="prospalis",
            name="Generated Prospalis",
            module_type=ModuleType.DATA_SOURCE,
            port=None,
            endpoint="internal://prospalis",
            capabilities=[
                ModuleCapability.DATA_INGEST,
                ModuleCapability.PERSISTENCE
            ],
            description="Automated data prospecting and generation",
            dependencies=["data_sources", "blerina"],
            status=ModuleStatus.ACTIVE
        ))
        
        logger.info(f"Registered {len(self.modules)} core modules")
        self._initialized = True
    
    def register(self, module: KloudModule) -> bool:
        """Register a new module"""
        if module.id in self.modules:
            logger.warning(f"Module {module.id} already registered, updating")
        
        self.modules[module.id] = module
        
        # Update capability index
        for cap in module.capabilities:
            if cap not in self.capability_index:
                self.capability_index[cap] = []
            if module.id not in self.capability_index[cap]:
                self.capability_index[cap].append(module.id)
        
        # Update type index
        if module.module_type not in self.type_index:
            self.type_index[module.module_type] = []
        if module.id not in self.type_index[module.module_type]:
            self.type_index[module.module_type].append(module.id)
        
        return True
    
    def get_module(self, module_id: str) -> Optional[KloudModule]:
        """Get a module by ID"""
        return self.modules.get(module_id)
    
    def get_modules_by_capability(self, capability: ModuleCapability) -> List[KloudModule]:
        """Get all modules with a specific capability"""
        module_ids = self.capability_index.get(capability, [])
        return [self.modules[mid] for mid in module_ids if mid in self.modules]
    
    def get_modules_by_type(self, module_type: ModuleType) -> List[KloudModule]:
        """Get all modules of a specific type"""
        module_ids = self.type_index.get(module_type, [])
        return [self.modules[mid] for mid in module_ids if mid in self.modules]
    
    def get_active_modules(self) -> List[KloudModule]:
        """Get all active modules"""
        return [m for m in self.modules.values() if m.status == ModuleStatus.ACTIVE]
    
    def get_core_services(self) -> List[KloudModule]:
        """Get HQ, ALBA, ALBI, JONA"""
        return [self.modules[m] for m in ["hq", "alba", "albi", "jona"] if m in self.modules]
    
    def update_status(self, module_id: str, status: ModuleStatus, health_score: float = 1.0) -> bool:
        """Update module status"""
        if module_id not in self.modules:
            return False
        
        self.modules[module_id].status = status
        self.modules[module_id].health_score = health_score
        self.modules[module_id].last_health_check = datetime.now()
        return True
    
    def get_summary(self) -> Dict[str, Any]:
        """Get registry summary"""
        return {
            "total_modules": len(self.modules),
            "active_modules": len([m for m in self.modules.values() if m.status == ModuleStatus.ACTIVE]),
            "core_services": len(self.get_core_services()),
            "capabilities_indexed": len(self.capability_index),
            "types_indexed": len(self.type_index),
            "modules": {mid: m.to_dict() for mid, m in self.modules.items()}
        }
    
    def find_modules_for_query(self, query: str, capabilities: List[ModuleCapability] = None) -> List[KloudModule]:
        """Find best modules to handle a query"""
        candidates = []
        
        if capabilities:
            for cap in capabilities:
                candidates.extend(self.get_modules_by_capability(cap))
        else:
            # Default: use core + data sources
            candidates = self.get_core_services()
            candidates.extend(self.get_modules_by_type(ModuleType.DATA_SOURCE))
        
        # Remove duplicates and sort by health
        seen = set()
        unique = []
        for m in candidates:
            if m.id not in seen:
                seen.add(m.id)
                unique.append(m)
        
        return sorted(unique, key=lambda x: x.health_score, reverse=True)


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================

_registry_instance: Optional[ModuleRegistry] = None

def get_registry() -> ModuleRegistry:
    """Get the global module registry singleton"""
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = ModuleRegistry()
    return _registry_instance

