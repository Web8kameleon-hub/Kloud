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

from .clx_adapter import (
    ClxAdapter,
    create_clx_adapter,
    test_clx_connection,
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
    # CLX
    "ClxAdapter",
    "create_clx_adapter",
    "test_clx_connection",
]
