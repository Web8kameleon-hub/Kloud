"""
═══════════════════════════════════════════════════════════════════════════════
ENGINE ADAPTER CONTRACT - Kontrata Unike për të Gjithë Motorët AI
═══════════════════════════════════════════════════════════════════════════════

Çdo motor (CLX, Llama.cpp, vLLM, OpenAI, etc.) implementon këtë kontratë.
Kloud nuk pyet "kush" është motori—vetëm flet me adapterin.

Request:
{
    "engine_id": "clx:clx",
  "mode": "chat" | "completion" | "embedding",
  "messages": [...],
  "params": { "temperature": 0.4, "max_tokens": 1024 },
  "context": { "user_id": "xyz", "session_id": "abc" }
}

Response:
{
  "text": "...",
  "tokens": { "input": 512, "output": 230 },
  "latency_ms": 1234,
    "engine_id": "clx:clx",
  "metadata": {...}
}

Author: Ledjan Ahmati / Kloud
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Literal
from datetime import datetime
from enum import Enum
import uuid
import time
import logging

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# ENUMS & TYPES
# ═══════════════════════════════════════════════════════════════════════════════


class EngineType(Enum):
    """Llojet e motorëve"""

    LLM = "llm"  # Language Model
    EMBEDDING = "embedding"  # Vector Embeddings
    CLASSIFIER = "classifier"  # Classification
    RERANKER = "reranker"  # Reranking
    VISION = "vision"  # Image/Vision
    AUDIO = "audio"  # Audio/Speech
    TOOL_CALLER = "tool_caller"  # Function Calling


class EngineMode(Enum):
    """Mënyrat e funksionimit"""

    CHAT = "chat"
    COMPLETION = "completion"
    EMBEDDING = "embedding"
    CLASSIFICATION = "classification"
    RERANK = "rerank"


# ═══════════════════════════════════════════════════════════════════════════════
# REQUEST / RESPONSE DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class EngineMessage:
    """Mesazh për motorin"""

    role: Literal["system", "user", "assistant", "tool"]
    content: str
    name: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EngineParams:
    """Parametrat e motorit"""

    temperature: float = 0.7
    max_tokens: int = 1024
    top_p: float = 0.9
    top_k: int = 40
    stop_sequences: List[str] = field(default_factory=list)
    presence_penalty: float = 0.0
    frequency_penalty: float = 0.0
    seed: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "top_k": self.top_k,
            "stop_sequences": self.stop_sequences,
            "presence_penalty": self.presence_penalty,
            "frequency_penalty": self.frequency_penalty,
            "seed": self.seed,
        }


@dataclass
class EngineContext:
    """Konteksti i kërkesës"""

    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    trace_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EngineRequest:
    """
    KONTRATA E KËRKESËS - Unike për të gjithë motorët
    """

    engine_id: str  # "clx:clx", "vllm:mistral"
    mode: EngineMode = EngineMode.CHAT
    messages: List[EngineMessage] = field(default_factory=list)
    prompt: Optional[str] = None  # Për completion mode
    input_text: Optional[str] = None  # Për embedding/classification
    params: EngineParams = field(default_factory=EngineParams)
    context: EngineContext = field(default_factory=EngineContext)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "engine_id": self.engine_id,
            "mode": self.mode.value,
            "messages": [{"role": m.role, "content": m.content} for m in self.messages],
            "prompt": self.prompt,
            "input_text": self.input_text,
            "params": self.params.to_dict(),
            "context": {
                "user_id": self.context.user_id,
                "session_id": self.context.session_id,
                "request_id": self.context.request_id,
            },
        }


@dataclass
class TokenUsage:
    """Përdorimi i tokeneve"""

    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0

    def __post_init__(self):
        if self.total_tokens == 0:
            self.total_tokens = self.input_tokens + self.output_tokens


@dataclass
class EngineResponse:
    """
    KONTRATA E PËRGJIGJES - Unike për të gjithë motorët
    """

    text: str  # Përgjigja e gjeneruar
    engine_id: str  # Cili motor u përdor
    tokens: TokenUsage = field(default_factory=TokenUsage)
    latency_ms: float = 0.0  # Koha e përgjigjes
    success: bool = True
    error: Optional[str] = None

    # Për embedding
    embedding: Optional[List[float]] = None

    # Për classification
    labels: Optional[Dict[str, float]] = None

    # Metadata
    model_name: Optional[str] = None
    finish_reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "engine_id": self.engine_id,
            "tokens": {
                "input": self.tokens.input_tokens,
                "output": self.tokens.output_tokens,
                "total": self.tokens.total_tokens,
            },
            "latency_ms": self.latency_ms,
            "success": self.success,
            "error": self.error,
            "model_name": self.model_name,
            "finish_reason": self.finish_reason,
            "timestamp": self.timestamp.isoformat(),
        }


# ═══════════════════════════════════════════════════════════════════════════════
# ABSTRACT BASE ADAPTER
# ═══════════════════════════════════════════════════════════════════════════════


class BaseEngineAdapter(ABC):
    """
    KONTRATA BAZË - Të gjithë adapterët e trashëgojnë këtë klasë
    """

    def __init__(self, engine_id: str, config: Optional[Dict[str, Any]] = None):
        self.engine_id = engine_id
        self.config = config or {}
        self.engine_type: EngineType = EngineType.LLM
        self.supported_modes: List[EngineMode] = [EngineMode.CHAT]
        self._initialized = False
        self._stats = {
            "total_requests": 0,
            "total_tokens": 0,
            "total_latency_ms": 0.0,
            "errors": 0,
        }

    @abstractmethod
    async def initialize(self) -> bool:
        """Inicializon adapterin"""
        pass

    @abstractmethod
    async def generate(self, request: EngineRequest) -> EngineResponse:
        """Gjeneron përgjigje - METODA KRYESORE"""
        pass

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Kontrollon statusin e motorit"""
        pass

    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Liston modelet e disponueshme"""
        pass

    # ─────────────────────────────────────────────────────────────────────────
    # Helper methods
    # ─────────────────────────────────────────────────────────────────────────

    def _update_stats(self, response: EngineResponse):
        """Përditëson statistikat"""
        self._stats["total_requests"] += 1
        self._stats["total_tokens"] += response.tokens.total_tokens
        self._stats["total_latency_ms"] += response.latency_ms
        if not response.success:
            self._stats["errors"] += 1

    def get_stats(self) -> Dict[str, Any]:
        """Kthen statistikat"""
        return {
            **self._stats,
            "avg_latency_ms": (
                self._stats["total_latency_ms"] / self._stats["total_requests"]
                if self._stats["total_requests"] > 0
                else 0
            ),
            "error_rate": (
                self._stats["errors"] / self._stats["total_requests"]
                if self._stats["total_requests"] > 0
                else 0
            ),
        }

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} engine_id={self.engine_id}>"


# ═══════════════════════════════════════════════════════════════════════════════
# ENGINE REGISTRY
# ═══════════════════════════════════════════════════════════════════════════════


class EngineRegistry:
    """
    Regjistri i të gjithë motorëve të disponueshëm
    """

    _instance: Optional["EngineRegistry"] = None
    _engines: Dict[str, BaseEngineAdapter]
    _initialized: bool

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._engines = {}
            cls._instance._initialized = False
        return cls._instance

    def register(self, adapter: BaseEngineAdapter) -> None:
        """Regjistron një adapter"""
        self._engines[adapter.engine_id] = adapter
        logger.info(f"✅ Engine registered: {adapter.engine_id}")

    def get(self, engine_id: str) -> Optional[BaseEngineAdapter]:
        """Merr adapterin sipas ID"""
        return self._engines.get(engine_id)

    def list_engines(self) -> List[Dict[str, Any]]:
        """Liston të gjithë motorët"""
        return [
            {
                "engine_id": e.engine_id,
                "type": e.engine_type.value,
                "modes": [m.value for m in e.supported_modes],
                "stats": e.get_stats(),
            }
            for e in self._engines.values()
        ]

    async def generate(self, request: EngineRequest) -> EngineResponse:
        """
        ENTRY POINT KRYESOR - Dërgon kërkesë te motori i duhur
        """
        engine = self.get(request.engine_id)

        if not engine:
            # Provo të gjesh sipas prefiksit (p.sh. "clx:*" → merr cilindo CLX)
            prefix = (
                request.engine_id.split(":")[0] if ":" in request.engine_id else None
            )
            if prefix:
                for eid, adapter in self._engines.items():
                    if eid.startswith(prefix):
                        engine = adapter
                        break

        if not engine:
            return EngineResponse(
                text="",
                engine_id=request.engine_id,
                success=False,
                error=f"Engine not found: {request.engine_id}",
            )

        start = time.time()
        try:
            response = await engine.generate(request)
            response.latency_ms = (time.time() - start) * 1000
            engine._update_stats(response)
            return response
        except Exception as e:
            logger.error(f"Engine error: {e}")
            return EngineResponse(
                text="",
                engine_id=request.engine_id,
                success=False,
                error=str(e),
                latency_ms=(time.time() - start) * 1000,
            )


# ═══════════════════════════════════════════════════════════════════════════════
# GLOBAL ACCESS
# ═══════════════════════════════════════════════════════════════════════════════

_registry = None


def get_registry() -> EngineRegistry:
    """Merr regjistrin global"""
    global _registry
    if _registry is None:
        _registry = EngineRegistry()
    return _registry


def get_engine(engine_id: str) -> Optional[BaseEngineAdapter]:
    """Merr një motor sipas ID"""
    return get_registry().get(engine_id)


def list_engines() -> List[Dict[str, Any]]:
    """Liston të gjithë motorët"""
    return get_registry().list_engines()


async def generate(request: EngineRequest) -> EngineResponse:
    """Gjeneron përgjigje nga motori i duhur"""
    return await get_registry().generate(request)


__all__ = [
    "EngineType",
    "EngineMode",
    "EngineMessage",
    "EngineParams",
    "EngineContext",
    "EngineRequest",
    "EngineResponse",
    "TokenUsage",
    "BaseEngineAdapter",
    "EngineRegistry",
    "get_registry",
    "get_engine",
    "list_engines",
    "generate",
]
