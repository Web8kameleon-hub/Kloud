"""
═══════════════════════════════════════════════════════════════════════════════
KLOUD CORE - AI/ML Library Architecture A-Z
═══════════════════════════════════════════════════════════════════════════════

Arkitektura e plotë:
├── engines/      - Engine Adapters (Ollama, Llama.cpp, vLLM)
├── personas/     - Persona System (Tutor, Architect, Code Companion)
├── pipelines/    - Pipeline Framework (RAG, Chains)
├── knowledge/    - Knowledge Base (Vector, Keyword, Hybrid Search)
└── capabilities/ - Capability Registry (Summarization, Translation, etc.)

Author: Ledjan Ahmati / Kloud
Version: 1.0.0
"""

# Engine Layer
from core.engines import (
    EngineType,
    EngineMode,
    EngineRequest,
    EngineResponse,
    BaseEngineAdapter,
    EngineRegistry,
    OllamaAdapter,
    get_registry as get_engine_registry,
    get_engine,
    list_engines,
)

# Persona Layer
from core.personas import (
    PersonaStyle,
    PersonaMode,
    Persona,
    PersonaRegistry,
    BUILT_IN_PERSONAS,
    get_persona_registry,
    get_persona,
    list_personas,
    route_to_persona as auto_select_persona,
)

# Pipeline Layer
from core.pipelines import (
    StepType,
    PipelineStep,
    StepResult as PipelineContext,
    Pipeline,
    PipelineRegistry,
    PipelineExecutor,
    RAG_PIPELINE,
    SIMPLE_CHAT_PIPELINE,
    get_pipeline_registry,
    create_pipeline as get_pipeline,
    list_pipelines,
)

# Knowledge Layer
from core.knowledge import (
    DocumentMetadata,
    Document,
    SearchResult,
    KnowledgeBaseIndex,
    get_knowledge_base as create_knowledge_base,
)

# Capabilities Layer
from core.capabilities import (
    CapabilityType,
    Capability,
    CapabilityRegistry,
    BUILT_IN_CAPABILITIES,
    get_capability_registry,
    get_capability,
    list_capabilities,
)

# Auto Registry Layer (Service Discovery)
from core.auto_registry import (
    registry,
    discover_all,
    get_function,
    get_service,
    search as search_registry,
    export as export_registry,
    generate_env,
    FunctionInfo,
    ServiceInfo,
)

# Service Bridge Layer (Inter-service Communication)
from core.service_bridge import (
    bridge,
    call_service,
    call_service_sync,
    check_all_health,
    get_all_endpoints,
    get_service_url,
)

__version__ = "1.0.0"
__author__ = "Ledjan Ahmati"


__all__ = [
    # Engines
    "EngineType",
    "EngineMode",
    "EngineRequest",
    "EngineResponse",
    "BaseEngineAdapter",
    "EngineRegistry",
    "OllamaAdapter",
    "get_engine_registry",
    "get_engine",
    "list_engines",
    # Personas
    "PersonaStyle",
    "PersonaMode",
    "Persona",
    "PersonaRegistry",
    "BUILT_IN_PERSONAS",
    "get_persona_registry",
    "get_persona",
    "list_personas",
    "auto_select_persona",
    # Pipelines
    "StepType",
    "PipelineStep",
    "PipelineContext",
    "Pipeline",
    "PipelineRegistry",
    "PipelineExecutor",
    "RAG_PIPELINE",
    "SIMPLE_CHAT_PIPELINE",
    "get_pipeline_registry",
    "get_pipeline",
    "list_pipelines",
    # Knowledge
    "DocumentMetadata",
    "Document",
    "SearchResult",
    "KnowledgeBaseIndex",
    "create_knowledge_base",
    # Capabilities
    "CapabilityType",
    "Capability",
    "CapabilityRegistry",
    "BUILT_IN_CAPABILITIES",
    "get_capability_registry",
    "get_capability",
    "list_capabilities",
    # Auto Registry
    "registry",
    "discover_all",
    "get_function",
    "get_service",
    "search_registry",
    "export_registry",
    "generate_env",
    "FunctionInfo",
    "ServiceInfo",
    # Service Bridge
    "bridge",
    "call_service",
    "call_service_sync",
    "check_all_health",
    "get_all_endpoints",
    "get_service_url",
]


def init_core(scan_services: bool = True) -> None:
    """
    Inicializon të gjitha regjistrat e core.
    Thirret automatikisht ose manualisht.
    
    Args:
        scan_services: Nëse True, skanon automatikisht shërbimet
    """
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info("🚀 Initializing Kloud Core...")
    
    # Init all registries
    get_engine_registry()
    get_persona_registry()
    get_pipeline_registry()
    get_capability_registry()
    
    # Skano shërbimet nëse kërkohet
    if scan_services:
        logger.info("🔍 Scanning services...")
        discover_all()
    
    logger.info("✅ Kloud Core initialized successfully!")


def core_status() -> dict:
    """Kthen statusin e core"""
    # Ensure registry is discovered
    if not registry._discovered:
        discover_all()
    
    return {
        "version": __version__,
        "engines": len(get_engine_registry().list_engines()),
        "personas": len(get_persona_registry().list_personas()),
        "pipelines": len(get_pipeline_registry().list_pipelines()),
        "capabilities": len(list_capabilities()),
        "services": len(registry.services),
        "functions": len(registry.functions),
        "endpoints": len(registry.endpoints),
        "status": "ready",
    }

