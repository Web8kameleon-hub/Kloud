"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         KLOUD AGENTS MODULE                               ║
║                   Unified Agent System - No Overlap                          ║
╚══════════════════════════════════════════════════════════════════════════════╝

This module consolidates ALL agent functionality into a single, organized system.
There is NO overlap with other agent implementations in the project.

Structure:
    agents/
    ├── __init__.py      - This file (exports)
    ├── base.py          - Base classes and types
    ├── core.py          - ALBA, ALBI, JONA (ASI Trinity)
    ├── specialized.py   - Data, Analytics, ML, Collectors
    ├── pool.py          - Autoscaling agent pool
    ├── registry.py      - Agent discovery
    ├── orchestrator.py  - Main entry point
    ├── telemetry.py     - Logging and metrics
    └── cycles.py        - Cycle engine integration

Quick Start:
    from agents import AgentOrchestrator
    
    async with AgentOrchestrator() as orchestrator:
        # Execute task
        result = await orchestrator.execute("web-scraper", {"action": "scrape", "url": "..."})
        
        # Use core agents
        await orchestrator.alba.collect({"source": "api"})
        await orchestrator.albi.analyze({"data": [...]})
        await orchestrator.jona.synthesize({"sources": [...]})

Available Exports:
    Base Types:
        - BaseAgent, AgentConfig, AgentType, AgentStatus
        - AgentCapability, Task, TaskResult, TaskPriority
    
    Core Agents:
        - ALBAAgent, ALBIAgent, JONAAgent, TrinitySystem
    
    Specialized Agents:
        - DataProcessingAgent, AnalyticsAgent, IntegrationAgent
        - MLAgent, WebScraperAgent, APICollectorAgent, FileParserAgent
    
    Infrastructure:
        - AgentPool, PoolConfig, PoolStats
        - AgentRegistry, RegistryEvent
        - AgentOrchestrator, OrchestratorConfig
        - TelemetryService, MetricsCollector
        - CycleAgentBridge, CyclePhase, MaturityState
"""

# ═══════════════════════════════════════════════════════════════════════════════
# BASE TYPES
# ═══════════════════════════════════════════════════════════════════════════════

from .base import (
    # Core classes
    BaseAgent,
    AgentConfig,
    Task,
    TaskResult,
    AgentMetrics,
    
    # Enums
    AgentStatus,
    AgentType,
    AgentCapability,
    TaskPriority,
)

# ═══════════════════════════════════════════════════════════════════════════════
# CORE AGENTS (ASI Trinity)
# ═══════════════════════════════════════════════════════════════════════════════

from .core import (
    ALBAAgent,      # Data Collection & Validation
    ALBIAgent,      # Neural Analytics & Processing
    JONAAgent,      # Synthesis & Insight Generation
    TrinitySystem,  # Coordinated Trinity
    create_core_agent,
)

# ═══════════════════════════════════════════════════════════════════════════════
# SPECIALIZED AGENTS
# ═══════════════════════════════════════════════════════════════════════════════

from .specialized import (
    DataProcessingAgent,
    AnalyticsAgent,
    IntegrationAgent,
    MLAgent,
    WebScraperAgent,
    APICollectorAgent,
    FileParserAgent,
    create_specialized_agent,
)

# ═══════════════════════════════════════════════════════════════════════════════
# INFRASTRUCTURE
# ═══════════════════════════════════════════════════════════════════════════════

from .pool import (
    AgentPool,
    PoolConfig,
    PoolStats,
    AgentInstance,
    get_default_pool,
    create_pool,
)

from .registry import (
    AgentRegistry,
    RegistryEntry,
    RegistryEvent,
    get_registry,
    register_agent,
    find_agents,
)

from .orchestrator import (
    AgentOrchestrator,
    OrchestratorConfig,
    Workflow,
    WorkflowStep,
    get_orchestrator,
    shutdown_orchestrator,
)

# ═══════════════════════════════════════════════════════════════════════════════
# TELEMETRY
# ═══════════════════════════════════════════════════════════════════════════════

from .telemetry import (
    TelemetryService,
    TelemetryEvent,
    MetricsCollector,
    Metric,
    EventType,
    MetricType,
    get_telemetry,
    log_task_started,
    log_task_completed,
    log_task_failed,
)

# ═══════════════════════════════════════════════════════════════════════════════
# CYCLE INTEGRATION
# ═══════════════════════════════════════════════════════════════════════════════

from .cycles import (
    CycleAgentBridge,
    CycleHandler,
    CycleContext,
    CyclePhase,
    MaturityState,
    PHASE_CAPABILITY_MAP,
    PHASE_CORE_AGENT_MAP,
    create_default_bridge,
    is_ml_ready,
    link_agent_to_cycle,
)


# ═══════════════════════════════════════════════════════════════════════════════
# VERSION & METADATA
# ═══════════════════════════════════════════════════════════════════════════════

__version__ = "2.0.0"
__author__ = "Kloud Team"
__description__ = "Unified Agent System - Consolidated without overlap"


# ═══════════════════════════════════════════════════════════════════════════════
# ALL EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Base
    "BaseAgent",
    "AgentConfig",
    "Task",
    "TaskResult",
    "AgentMetrics",
    "AgentStatus",
    "AgentType",
    "AgentCapability",
    "TaskPriority",
    
    # Core agents
    "ALBAAgent",
    "ALBIAgent",
    "JONAAgent",
    "TrinitySystem",
    "create_core_agent",
    
    # Specialized agents
    "DataProcessingAgent",
    "AnalyticsAgent",
    "IntegrationAgent",
    "MLAgent",
    "WebScraperAgent",
    "APICollectorAgent",
    "FileParserAgent",
    "create_specialized_agent",
    
    # Pool
    "AgentPool",
    "PoolConfig",
    "PoolStats",
    "AgentInstance",
    "get_default_pool",
    "create_pool",
    
    # Registry
    "AgentRegistry",
    "RegistryEntry",
    "RegistryEvent",
    "get_registry",
    "register_agent",
    "find_agents",
    
    # Orchestrator
    "AgentOrchestrator",
    "OrchestratorConfig",
    "Workflow",
    "WorkflowStep",
    "get_orchestrator",
    "shutdown_orchestrator",
    
    # Telemetry
    "TelemetryService",
    "TelemetryEvent",
    "MetricsCollector",
    "Metric",
    "EventType",
    "MetricType",
    "get_telemetry",
    "log_task_started",
    "log_task_completed",
    "log_task_failed",
    
    # Cycles
    "CycleAgentBridge",
    "CycleHandler",
    "CycleContext",
    "CyclePhase",
    "MaturityState",
    "PHASE_CAPABILITY_MAP",
    "PHASE_CORE_AGENT_MAP",
    "create_default_bridge",
    "is_ml_ready",
    "link_agent_to_cycle",
]

