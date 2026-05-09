"""
ENGINES MODULE - Engine Adapters për Kloud
"""

from .contract import (
    EngineType,
    EngineMode,
    EngineMessage,
    EngineParams,
    EngineContext,
    EngineRequest,
    EngineResponse,
    TokenUsage,
    BaseEngineAdapter,
    EngineRegistry,
    get_registry,
    get_engine,
    list_engines,
    generate,
)

from .ollama_adapter import (
    OllamaAdapter,
    create_ollama_adapter,
    test_ollama_connection,
)

__all__ = [
    # Contract
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
    # Ollama
    "OllamaAdapter",
    "create_ollama_adapter",
    "test_ollama_connection",
]

