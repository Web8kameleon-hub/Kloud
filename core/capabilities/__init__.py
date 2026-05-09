"""
═══════════════════════════════════════════════════════════════════════════════
CAPABILITIES MODULE - AI Capabilities Registry
═══════════════════════════════════════════════════════════════════════════════

Çdo capability lidhet me:
- Një ose disa modele
- Një persona / chain
- Një kontratë input/output

Shembuj: summarization, translation, code-gen, routing, classification, retrieval, planning, tool-use

Author: Ledjan Ahmati / Kloud
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class CapabilityType(Enum):
    """Llojet e aftësive"""
    SUMMARIZATION = "summarization"
    TRANSLATION = "translation"
    CODE_GENERATION = "code_generation"
    CODE_EXPLANATION = "code_explanation"
    CLASSIFICATION = "classification"
    ROUTING = "routing"
    RETRIEVAL = "retrieval"
    PLANNING = "planning"
    TOOL_USE = "tool_use"
    QA = "qa"
    CONVERSATION = "conversation"
    ANALYSIS = "analysis"


@dataclass
class Capability:
    """Aftësi AI"""
    id: str
    name: str
    type: CapabilityType
    description: str = ""
    
    # Resources
    default_engine: str = "ollama:kloud-ocean:v2"
    default_persona: Optional[str] = None
    default_pipeline: Optional[str] = None
    
    # Input/Output schema
    input_schema: Dict[str, str] = field(default_factory=lambda: {"text": "string"})
    output_schema: Dict[str, str] = field(default_factory=lambda: {"result": "string"})
    
    # Config
    config: Dict[str, Any] = field(default_factory=dict)
    active: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "description": self.description,
            "default_engine": self.default_engine,
            "default_persona": self.default_persona,
            "default_pipeline": self.default_pipeline,
            "active": self.active,
        }


# Built-in capabilities
BUILT_IN_CAPABILITIES = [
    Capability(
        id="summarization",
        name="Text Summarization",
        type=CapabilityType.SUMMARIZATION,
        description="Summarize long text into concise points",
        config={"max_length": 200, "style": "bullet_points"},
    ),
    Capability(
        id="translation",
        name="Translation",
        type=CapabilityType.TRANSLATION,
        description="Translate text between languages",
        config={"source_lang": "auto", "target_lang": "en"},
    ),
    Capability(
        id="code_gen",
        name="Code Generation",
        type=CapabilityType.CODE_GENERATION,
        description="Generate code from natural language",
        default_persona="code_companion",
        config={"language": "python", "style": "documented"},
    ),
    Capability(
        id="qa_rag",
        name="Question Answering with RAG",
        type=CapabilityType.QA,
        description="Answer questions using knowledge base",
        default_pipeline="rag_qa_v1",
    ),
    Capability(
        id="classification",
        name="Text Classification",
        type=CapabilityType.CLASSIFICATION,
        description="Classify text into categories",
    ),
    Capability(
        id="routing",
        name="Query Routing",
        type=CapabilityType.ROUTING,
        description="Route queries to appropriate handlers",
    ),
]


class CapabilityRegistry:
    """Regjistri i aftësive"""
    
    _instance: Optional["CapabilityRegistry"] = None
    _capabilities: Dict[str, Capability]
    _initialized: bool
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._capabilities = {}
            cls._instance._initialized = False
        return cls._instance
    
    def initialize(self) -> None:
        if self._initialized:
            return
        
        for cap in BUILT_IN_CAPABILITIES:
            self.register(cap)
        
        self._initialized = True
        logger.info(f"✅ Capability Registry initialized with {len(self._capabilities)} capabilities")
    
    def register(self, capability: Capability) -> None:
        self._capabilities[capability.id] = capability
    
    def get(self, cap_id: str) -> Optional[Capability]:
        if not self._initialized:
            self.initialize()
        return self._capabilities.get(cap_id)
    
    def list_capabilities(self) -> List[Dict[str, Any]]:
        if not self._initialized:
            self.initialize()
        return [c.to_dict() for c in self._capabilities.values() if c.active]


_registry = None


def get_capability_registry() -> CapabilityRegistry:
    global _registry
    if _registry is None:
        _registry = CapabilityRegistry()
        _registry.initialize()
    return _registry


def get_capability(cap_id: str) -> Optional[Capability]:
    return get_capability_registry().get(cap_id)


def list_capabilities() -> List[Dict[str, Any]]:
    return get_capability_registry().list_capabilities()


__all__ = [
    "CapabilityType",
    "Capability",
    "CapabilityRegistry",
    "BUILT_IN_CAPABILITIES",
    "get_capability_registry",
    "get_capability",
    "list_capabilities",
]

