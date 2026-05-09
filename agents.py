"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    KLOUD CLOUD - UNIFIED AGENTS SYSTEM                   ║
║           Scalable Agent Registry + Pool + Communication + Telemetry        ║
╚══════════════════════════════════════════════════════════════════════════════╝

Architecture:
┌─────────────────────────────────────────────────────────────────────────────┐
│                           AgentOrchestrator                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ AgentPool    │  │ AgentRegistry│  │ LoadBalancer │  │ TelemetryHub │    │
│  │ - workers    │  │ - agents     │  │ - round_robin│  │ - metrics    │    │
│  │ - queue      │  │ - discovery  │  │ - least_conn │  │ - alerts     │    │
│  │ - autoscale  │  │ - health     │  │ - weighted   │  │ - tracing    │    │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘

Usage:
    from agents import AgentOrchestrator, BaseAgent, AgentConfig
    
    # Create orchestrator
    orchestrator = AgentOrchestrator()
    
    # Register agent
    orchestrator.register(ALBAAgent())
    
    # Scale agent pool
    orchestrator.scale("alba", min_instances=2, max_instances=10)
    
    # Submit task
    result = await orchestrator.submit("alba", task_data)
"""

import asyncio
import logging
import time
import uuid
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum, auto
from typing import (
    Dict, Any, Optional, List, Callable, 
    TypeVar, Generic, Awaitable, Union
)
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
import threading
import queue
import weakref

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AgentSystem")


# ═══════════════════════════════════════════════════════════════════════════════
# ENUMS & TYPES
# ═══════════════════════════════════════════════════════════════════════════════

class AgentStatus(Enum):
    """Agent operational status"""
    INITIALIZING = "initializing"
    READY = "ready"
    BUSY = "busy"
    PAUSED = "paused"
    DRAINING = "draining"  # Finishing current tasks, not accepting new
    ERROR = "error"
    TERMINATED = "terminated"


class AgentType(Enum):
    """Agent type classification"""
    CORE = "core"           # ALBA, ALBI, JONA
    PROCESSING = "processing"
    ANALYTICS = "analytics"
    INTEGRATION = "integration"
    ML = "ml"
    CUSTOM = "custom"


class TaskPriority(Enum):
    """Task priority levels"""
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3
    BACKGROUND = 4


class LoadBalanceStrategy(Enum):
    """Load balancing strategies"""
    ROUND_ROBIN = auto()
    LEAST_CONNECTIONS = auto()
    WEIGHTED = auto()
    RANDOM = auto()
    CAPABILITY_MATCH = auto()


T = TypeVar("T")
TaskResult = TypeVar("TaskResult")


# ═══════════════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class AgentConfig:
    """Agent configuration"""
    name: str
    agent_type: AgentType = AgentType.CUSTOM
    version: str = "1.0.0"
    capabilities: List[str] = field(default_factory=list)
    max_concurrent_tasks: int = 10
    min_instances: int = 1
    max_instances: int = 5
    timeout_seconds: float = 30.0
    retry_count: int = 3
    retry_delay: float = 1.0
    health_check_interval: float = 10.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "agent_type": self.agent_type.value
        }


@dataclass
class AgentMetrics:
    """Agent performance metrics"""
    agent_id: str
    agent_name: str
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    avg_response_time_ms: float = 0.0
    current_load: int = 0
    uptime_seconds: float = 0.0
    last_heartbeat: Optional[str] = None
    error_rate: float = 0.0
    
    def update_response_time(self, duration_ms: float):
        """Update average response time with exponential moving average"""
        alpha = 0.1  # Smoothing factor
        if self.avg_response_time_ms == 0:
            self.avg_response_time_ms = duration_ms
        else:
            self.avg_response_time_ms = alpha * duration_ms + (1 - alpha) * self.avg_response_time_ms
    
    @property
    def success_rate(self) -> float:
        if self.total_tasks == 0:
            return 100.0
        return (self.completed_tasks / self.total_tasks) * 100


@dataclass 
class Task:
    """Task representation"""
    task_id: str
    agent_name: str
    payload: Dict[str, Any]
    priority: TaskPriority = TaskPriority.NORMAL
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    timeout: float = 30.0
    retry_count: int = 0
    max_retries: int = 3
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __lt__(self, other: "Task") -> bool:
        """For priority queue ordering"""
        return self.priority.value < other.priority.value


@dataclass
class TaskResult:
    """Task execution result"""
    task_id: str
    agent_id: str
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    duration_ms: float = 0.0
    completed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ═══════════════════════════════════════════════════════════════════════════════
# BASE AGENT CLASS
# ═══════════════════════════════════════════════════════════════════════════════

class BaseAgent(ABC):
    """
    Abstract base class for all agents.
    Inherit this to create custom agents.
    
    Example:
        class MyAgent(BaseAgent):
            def get_config(self) -> AgentConfig:
                return AgentConfig(
                    name="my-agent",
                    agent_type=AgentType.PROCESSING,
                    capabilities=["data-transform", "validation"]
                )
            
            async def execute(self, task: Task) -> Any:
                # Process the task
                return {"processed": task.payload}
    """
    
    def __init__(self):
        self._id = f"{self.config.name}_{uuid.uuid4().hex[:8]}"
        self._status = AgentStatus.INITIALIZING
        self._metrics = AgentMetrics(
            agent_id=self._id,
            agent_name=self.config.name
        )
        self._start_time = time.time()
        self._current_tasks: Dict[str, Task] = {}
        self._lock = threading.Lock()
    
    @property
    def id(self) -> str:
        return self._id
    
    @property 
    def status(self) -> AgentStatus:
        return self._status
    
    @status.setter
    def status(self, value: AgentStatus):
        self._status = value
    
    @property
    def metrics(self) -> AgentMetrics:
        self._metrics.uptime_seconds = time.time() - self._start_time
        self._metrics.current_load = len(self._current_tasks)
        return self._metrics
    
    @property
    @abstractmethod
    def config(self) -> AgentConfig:
        """Return agent configuration. Must be implemented."""
        pass
    
    @abstractmethod
    async def execute(self, task: Task) -> Any:
        """
        Execute a task. Must be implemented.
        
        Args:
            task: The task to execute
            
        Returns:
            Task result (any type)
            
        Raises:
            Exception: If task fails
        """
        pass
    
    async def initialize(self) -> bool:
        """Initialize the agent. Override for custom initialization."""
        self._status = AgentStatus.READY
        logger.info(f"✅ Agent initialized: {self._id}")
        return True
    
    async def shutdown(self) -> bool:
        """Shutdown the agent gracefully. Override for custom cleanup."""
        self._status = AgentStatus.DRAINING
        # Wait for current tasks to complete
        while self._current_tasks:
            await asyncio.sleep(0.1)
        self._status = AgentStatus.TERMINATED
        logger.info(f"🛑 Agent shutdown: {self._id}")
        return True
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check endpoint. Override for custom health logic."""
        return {
            "agent_id": self._id,
            "status": self._status.value,
            "healthy": self._status in [AgentStatus.READY, AgentStatus.BUSY],
            "metrics": asdict(self.metrics),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def can_accept_task(self) -> bool:
        """Check if agent can accept new tasks"""
        if self._status not in [AgentStatus.READY, AgentStatus.BUSY]:
            return False
        return len(self._current_tasks) < self.config.max_concurrent_tasks
    
    def has_capability(self, capability: str) -> bool:
        """Check if agent has a specific capability"""
        return capability in self.config.capabilities
    
    async def _run_task(self, task: Task) -> TaskResult:
        """Internal task runner with metrics tracking"""
        start_time = time.time()
        
        with self._lock:
            self._current_tasks[task.task_id] = task
            self._metrics.total_tasks += 1
        
        if len(self._current_tasks) > 0:
            self._status = AgentStatus.BUSY
        
        try:
            result = await asyncio.wait_for(
                self.execute(task),
                timeout=task.timeout
            )
            
            duration_ms = (time.time() - start_time) * 1000
            self._metrics.completed_tasks += 1
            self._metrics.update_response_time(duration_ms)
            
            return TaskResult(
                task_id=task.task_id,
                agent_id=self._id,
                success=True,
                result=result,
                duration_ms=duration_ms
            )
            
        except asyncio.TimeoutError:
            self._metrics.failed_tasks += 1
            return TaskResult(
                task_id=task.task_id,
                agent_id=self._id,
                success=False,
                error=f"Task timed out after {task.timeout}s",
                duration_ms=(time.time() - start_time) * 1000
            )
            
        except Exception as e:
            self._metrics.failed_tasks += 1
            logger.error(f"Task {task.task_id} failed: {e}")
            return TaskResult(
                task_id=task.task_id,
                agent_id=self._id,
                success=False,
                error=str(e),
                duration_ms=(time.time() - start_time) * 1000
            )
            
        finally:
            with self._lock:
                self._current_tasks.pop(task.task_id, None)
            
            if len(self._current_tasks) == 0:
                self._status = AgentStatus.READY


# ═══════════════════════════════════════════════════════════════════════════════
# CORE AGENTS - ALBA / ALBI / JONA
# ═══════════════════════════════════════════════════════════════════════════════

class ALBAAgent(BaseAgent):
    """
    ALBA - Network Telemetry & Data Collection Agent
    Role: Collect, organize, and present system metrics
    """
    
    @property
    def config(self) -> AgentConfig:
        return AgentConfig(
            name="alba",
            agent_type=AgentType.CORE,
            version="2.0.0",
            capabilities=[
                "network-monitoring",
                "data-collection", 
                "metric-aggregation",
                "real-time-streaming",
                "health-monitoring"
            ],
            max_concurrent_tasks=20,
            min_instances=1,
            max_instances=5
        )
    
    async def execute(self, task: Task) -> Any:
        """Execute ALBA task"""
        action = task.payload.get("action", "collect")
        
        if action == "collect":
            return await self._collect_metrics(task.payload)
        elif action == "stream":
            return await self._start_stream(task.payload)
        elif action == "health":
            return await self._check_health(task.payload)
        else:
            return {"status": "unknown_action", "action": action}
    
    async def _collect_metrics(self, payload: Dict) -> Dict:
        """Collect system metrics"""
        return {
            "metrics": {
                "cpu_usage": 45.2,
                "memory_usage": 62.8,
                "network_io": {"rx_bytes": 1024000, "tx_bytes": 512000},
                "active_connections": 128
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": self._id
        }
    
    async def _start_stream(self, payload: Dict) -> Dict:
        """Start a metrics stream"""
        stream_id = f"stream_{uuid.uuid4().hex[:8]}"
        return {
            "stream_id": stream_id,
            "status": "started",
            "interval_ms": payload.get("interval_ms", 1000)
        }
    
    async def _check_health(self, payload: Dict) -> Dict:
        """Check component health"""
        targets = payload.get("targets", ["api", "database", "cache"])
        return {
            "health_checks": {t: "healthy" for t in targets},
            "checked_at": datetime.now(timezone.utc).isoformat()
        }


class ALBIAgent(BaseAgent):
    """
    ALBI - Neural Analytics & Pattern Recognition Agent
    Role: Identify anomalies, patterns, and correlations
    """
    
    @property
    def config(self) -> AgentConfig:
        return AgentConfig(
            name="albi",
            agent_type=AgentType.CORE,
            version="2.0.0",
            capabilities=[
                "pattern-recognition",
                "anomaly-detection",
                "correlation-analysis",
                "predictive-modeling",
                "neural-processing"
            ],
            max_concurrent_tasks=15,
            min_instances=1,
            max_instances=8
        )
    
    async def execute(self, task: Task) -> Any:
        """Execute ALBI task"""
        action = task.payload.get("action", "analyze")
        
        if action == "analyze":
            return await self._analyze_data(task.payload)
        elif action == "detect_anomaly":
            return await self._detect_anomalies(task.payload)
        elif action == "predict":
            return await self._predict(task.payload)
        else:
            return {"status": "unknown_action", "action": action}
    
    async def _analyze_data(self, payload: Dict) -> Dict:
        """Analyze data patterns"""
        data = payload.get("data", [])
        return {
            "analysis": {
                "patterns_found": 3,
                "correlations": [{"field_a": "cpu", "field_b": "memory", "correlation": 0.85}],
                "insights": ["High correlation between CPU and memory usage"]
            },
            "data_points_analyzed": len(data) if isinstance(data, list) else 1,
            "analyzed_by": self._id
        }
    
    async def _detect_anomalies(self, payload: Dict) -> Dict:
        """Detect anomalies in data"""
        return {
            "anomalies": [
                {"timestamp": "2026-01-29T10:30:00Z", "severity": "warning", "type": "spike"}
            ],
            "anomaly_count": 1,
            "threshold": payload.get("threshold", 0.95)
        }
    
    async def _predict(self, payload: Dict) -> Dict:
        """Make predictions"""
        return {
            "predictions": {
                "next_hour": {"cpu": 52.1, "memory": 68.5},
                "confidence": 0.87
            },
            "model": "neural_v2"
        }


class JONAAgent(BaseAgent):
    """
    JONA - Strategic Advisor & Synthesis Agent
    Role: Synthesize insights and provide actionable recommendations
    """
    
    @property
    def config(self) -> AgentConfig:
        return AgentConfig(
            name="jona",
            agent_type=AgentType.CORE,
            version="2.0.0",
            capabilities=[
                "insight-synthesis",
                "recommendation-engine",
                "strategy-planning",
                "decision-support",
                "natural-language"
            ],
            max_concurrent_tasks=10,
            min_instances=1,
            max_instances=3
        )
    
    async def execute(self, task: Task) -> Any:
        """Execute JONA task"""
        action = task.payload.get("action", "synthesize")
        
        if action == "synthesize":
            return await self._synthesize(task.payload)
        elif action == "recommend":
            return await self._recommend(task.payload)
        elif action == "strategize":
            return await self._strategize(task.payload)
        else:
            return {"status": "unknown_action", "action": action}
    
    async def _synthesize(self, payload: Dict) -> Dict:
        """Synthesize insights from multiple sources"""
        sources = payload.get("sources", [])
        return {
            "synthesis": {
                "key_findings": ["System performance is optimal", "No critical issues detected"],
                "summary": "Overall system health is good with minor optimization opportunities",
                "confidence": 0.92
            },
            "sources_processed": len(sources),
            "synthesized_by": self._id
        }
    
    async def _recommend(self, payload: Dict) -> Dict:
        """Generate recommendations"""
        context = payload.get("context", {})
        return {
            "recommendations": [
                {"priority": "medium", "action": "Consider scaling database", "impact": "high"},
                {"priority": "low", "action": "Enable caching for static assets", "impact": "medium"}
            ],
            "based_on": list(context.keys()) if context else ["general_analysis"]
        }
    
    async def _strategize(self, payload: Dict) -> Dict:
        """Create strategic plan"""
        goals = payload.get("goals", [])
        return {
            "strategy": {
                "short_term": ["Optimize current infrastructure"],
                "mid_term": ["Implement auto-scaling"],
                "long_term": ["Migrate to cloud-native architecture"]
            },
            "goals_addressed": len(goals)
        }


# ═══════════════════════════════════════════════════════════════════════════════
# AGENT POOL - MANAGES AGENT INSTANCES
# ═══════════════════════════════════════════════════════════════════════════════

class AgentPool:
    """
    Manages a pool of agent instances for a specific agent type.
    Handles autoscaling based on load.
    """
    
    def __init__(
        self, 
        agent_factory: Callable[[], BaseAgent],
        min_instances: int = 1,
        max_instances: int = 5
    ):
        self._factory = agent_factory
        self._min_instances = min_instances
        self._max_instances = max_instances
        self._agents: List[BaseAgent] = []
        self._lock = threading.Lock()
        self._task_queue: asyncio.Queue = asyncio.Queue()
        self._running = False
        self._workers: List[asyncio.Task] = []
    
    @property
    def size(self) -> int:
        return len(self._agents)
    
    @property
    def available_agents(self) -> List[BaseAgent]:
        return [a for a in self._agents if a.can_accept_task()]
    
    @property
    def pool_metrics(self) -> Dict[str, Any]:
        return {
            "total_instances": len(self._agents),
            "available": len(self.available_agents),
            "busy": len([a for a in self._agents if a.status == AgentStatus.BUSY]),
            "queue_size": self._task_queue.qsize(),
            "min_instances": self._min_instances,
            "max_instances": self._max_instances
        }
    
    async def initialize(self):
        """Initialize pool with minimum instances"""
        for _ in range(self._min_instances):
            await self._add_instance()
        self._running = True
        logger.info(f"✅ Pool initialized with {self._min_instances} instances")
    
    async def shutdown(self):
        """Shutdown all agents in pool"""
        self._running = False
        for worker in self._workers:
            worker.cancel()
        for agent in self._agents:
            await agent.shutdown()
        self._agents.clear()
        logger.info("🛑 Pool shutdown complete")
    
    async def _add_instance(self) -> Optional[BaseAgent]:
        """Add a new agent instance to pool"""
        if len(self._agents) >= self._max_instances:
            return None
        
        with self._lock:
            agent = self._factory()
            await agent.initialize()
            self._agents.append(agent)
            logger.info(f"📈 Added instance: {agent.id} (total: {len(self._agents)})")
            return agent
    
    async def _remove_instance(self) -> bool:
        """Remove an idle agent instance"""
        if len(self._agents) <= self._min_instances:
            return False
        
        with self._lock:
            # Find an idle agent
            for agent in self._agents:
                if agent.status == AgentStatus.READY:
                    await agent.shutdown()
                    self._agents.remove(agent)
                    logger.info(f"📉 Removed instance: {agent.id} (total: {len(self._agents)})")
                    return True
        return False
    
    def get_best_agent(self, task: Task) -> Optional[BaseAgent]:
        """Get the best available agent for a task"""
        available = self.available_agents
        if not available:
            return None
        
        # Sort by current load (least connections)
        available.sort(key=lambda a: a.metrics.current_load)
        return available[0]
    
    async def submit(self, task: Task) -> TaskResult:
        """Submit a task to the pool"""
        agent = self.get_best_agent(task)
        
        if not agent:
            # Try to scale up
            agent = await self._add_instance()
            if not agent:
                # All agents busy and at max capacity
                return TaskResult(
                    task_id=task.task_id,
                    agent_id="pool",
                    success=False,
                    error="No available agents, pool at maximum capacity"
                )
        
        return await agent._run_task(task)
    
    async def scale(self, target: int) -> Dict[str, Any]:
        """Scale pool to target number of instances"""
        target = max(self._min_instances, min(self._max_instances, target))
        current = len(self._agents)
        
        if target > current:
            for _ in range(target - current):
                await self._add_instance()
        elif target < current:
            for _ in range(current - target):
                await self._remove_instance()
        
        return {
            "previous": current,
            "current": len(self._agents),
            "target": target
        }


# ═══════════════════════════════════════════════════════════════════════════════
# AGENT REGISTRY - SERVICE DISCOVERY
# ═══════════════════════════════════════════════════════════════════════════════

class AgentRegistry:
    """
    Central registry for agent discovery and management.
    Provides service discovery, health tracking, and capability matching.
    """
    
    def __init__(self):
        self._pools: Dict[str, AgentPool] = {}
        self._agent_configs: Dict[str, AgentConfig] = {}
        self._lock = threading.Lock()
    
    def register(
        self, 
        agent_class: type,
        min_instances: int = 1,
        max_instances: int = 5
    ) -> str:
        """Register an agent type with the registry"""
        # Create a temporary instance to get config
        temp_agent = agent_class()
        config = temp_agent.config
        name = config.name
        
        if name in self._pools:
            logger.warning(f"Agent {name} already registered, skipping")
            return name
        
        # Create pool
        pool = AgentPool(
            agent_factory=agent_class,
            min_instances=min_instances,
            max_instances=max_instances
        )
        
        with self._lock:
            self._pools[name] = pool
            self._agent_configs[name] = config
        
        logger.info(f"✅ Registered agent: {name} ({config.agent_type.value})")
        return name
    
    def unregister(self, name: str) -> bool:
        """Unregister an agent type"""
        if name not in self._pools:
            return False
        
        with self._lock:
            del self._pools[name]
            del self._agent_configs[name]
        
        logger.info(f"🗑️ Unregistered agent: {name}")
        return True
    
    def get_pool(self, name: str) -> Optional[AgentPool]:
        """Get agent pool by name"""
        return self._pools.get(name)
    
    def get_config(self, name: str) -> Optional[AgentConfig]:
        """Get agent config by name"""
        return self._agent_configs.get(name)
    
    def find_by_capability(self, capability: str) -> List[str]:
        """Find agents with a specific capability"""
        matching = []
        for name, config in self._agent_configs.items():
            if capability in config.capabilities:
                matching.append(name)
        return matching
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """List all registered agents"""
        result = []
        for name, config in self._agent_configs.items():
            pool = self._pools.get(name)
            result.append({
                "name": name,
                "config": config.to_dict(),
                "pool": pool.pool_metrics if pool else None
            })
        return result
    
    async def initialize_all(self):
        """Initialize all agent pools"""
        for name, pool in self._pools.items():
            await pool.initialize()
        logger.info(f"✅ Initialized {len(self._pools)} agent pools")
    
    async def shutdown_all(self):
        """Shutdown all agent pools"""
        for pool in self._pools.values():
            await pool.shutdown()
        logger.info("🛑 All agent pools shutdown")


# ═══════════════════════════════════════════════════════════════════════════════
# AGENT ORCHESTRATOR - MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

class AgentOrchestrator:
    """
    Main orchestrator for the agent system.
    Provides a unified interface for agent management.
    
    Usage:
        orchestrator = AgentOrchestrator()
        await orchestrator.initialize()
        
        # Submit task
        result = await orchestrator.submit("alba", {"action": "collect"})
        
        # Scale agents
        await orchestrator.scale("alba", 3)
    """
    
    def __init__(self, auto_register_core: bool = True):
        self._registry = AgentRegistry()
        self._start_time = time.time()
        self._task_counter = 0
        self._lock = threading.Lock()
        
        if auto_register_core:
            self._register_core_agents()
    
    def _register_core_agents(self):
        """Register core ALBA/ALBI/JONA agents"""
        self._registry.register(ALBAAgent, min_instances=1, max_instances=5)
        self._registry.register(ALBIAgent, min_instances=1, max_instances=8)
        self._registry.register(JONAAgent, min_instances=1, max_instances=3)
    
    async def initialize(self):
        """Initialize the orchestrator and all agents"""
        await self._registry.initialize_all()
        logger.info("🚀 Agent Orchestrator initialized")
    
    async def shutdown(self):
        """Shutdown orchestrator and all agents"""
        await self._registry.shutdown_all()
        logger.info("🛑 Agent Orchestrator shutdown")
    
    def register(
        self, 
        agent_class: type,
        min_instances: int = 1,
        max_instances: int = 5
    ) -> str:
        """Register a new agent type"""
        return self._registry.register(agent_class, min_instances, max_instances)
    
    async def submit(
        self,
        agent_name: str,
        payload: Dict[str, Any],
        priority: TaskPriority = TaskPriority.NORMAL,
        timeout: float = 30.0
    ) -> TaskResult:
        """Submit a task to a specific agent"""
        pool = self._registry.get_pool(agent_name)
        if not pool:
            return TaskResult(
                task_id="unknown",
                agent_id="orchestrator",
                success=False,
                error=f"Agent '{agent_name}' not found"
            )
        
        with self._lock:
            self._task_counter += 1
            task_id = f"task_{self._task_counter}_{uuid.uuid4().hex[:6]}"
        
        task = Task(
            task_id=task_id,
            agent_name=agent_name,
            payload=payload,
            priority=priority,
            timeout=timeout
        )
        
        return await pool.submit(task)
    
    async def submit_by_capability(
        self,
        capability: str,
        payload: Dict[str, Any],
        priority: TaskPriority = TaskPriority.NORMAL
    ) -> TaskResult:
        """Submit task to an agent with matching capability"""
        agents = self._registry.find_by_capability(capability)
        if not agents:
            return TaskResult(
                task_id="unknown",
                agent_id="orchestrator",
                success=False,
                error=f"No agent found with capability '{capability}'"
            )
        
        # Use first matching agent
        return await self.submit(agents[0], payload, priority)
    
    async def broadcast(
        self,
        payload: Dict[str, Any],
        agent_names: Optional[List[str]] = None
    ) -> Dict[str, TaskResult]:
        """Broadcast a task to multiple agents"""
        if agent_names is None:
            agent_names = ["alba", "albi", "jona"]  # Default: core agents
        
        results = {}
        tasks = []
        
        for name in agent_names:
            tasks.append(self.submit(name, payload))
        
        task_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for name, result in zip(agent_names, task_results):
            if isinstance(result, Exception):
                results[name] = TaskResult(
                    task_id="unknown",
                    agent_id=name,
                    success=False,
                    error=str(result)
                )
            else:
                results[name] = result
        
        return results
    
    async def scale(self, agent_name: str, target: int) -> Dict[str, Any]:
        """Scale an agent pool"""
        pool = self._registry.get_pool(agent_name)
        if not pool:
            return {"error": f"Agent '{agent_name}' not found"}
        return await pool.scale(target)
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """List all registered agents"""
        return self._registry.list_agents()
    
    def find_agents(self, capability: str) -> List[str]:
        """Find agents by capability"""
        return self._registry.find_by_capability(capability)
    
    @property
    def status(self) -> Dict[str, Any]:
        """Get orchestrator status"""
        agents = self._registry.list_agents()
        total_instances = sum(a["pool"]["total_instances"] for a in agents if a["pool"])
        available = sum(a["pool"]["available"] for a in agents if a["pool"])
        
        return {
            "status": "operational",
            "uptime_seconds": time.time() - self._start_time,
            "total_tasks_processed": self._task_counter,
            "agents": {
                "registered": len(agents),
                "total_instances": total_instances,
                "available_instances": available
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

# Global orchestrator instance
_orchestrator: Optional[AgentOrchestrator] = None


def get_orchestrator() -> AgentOrchestrator:
    """Get or create the global orchestrator instance"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AgentOrchestrator()
    return _orchestrator


async def init_agents() -> AgentOrchestrator:
    """Initialize the global agent orchestrator"""
    orchestrator = get_orchestrator()
    await orchestrator.initialize()
    return orchestrator


async def shutdown_agents():
    """Shutdown the global agent orchestrator"""
    global _orchestrator
    if _orchestrator:
        await _orchestrator.shutdown()
        _orchestrator = None


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN - DEMO & TESTING
# ═══════════════════════════════════════════════════════════════════════════════

async def demo():
    """Demo the agent system"""
    print("\n" + "="*70)
    print("🤖 KLOUD UNIFIED AGENTS SYSTEM - DEMO")
    print("="*70 + "\n")
    
    # Create orchestrator
    orchestrator = AgentOrchestrator()
    await orchestrator.initialize()
    
    print("\n📋 Registered Agents:")
    for agent in orchestrator.list_agents():
        print(f"  • {agent['name']} ({agent['config']['agent_type']}) - {agent['pool']['total_instances']} instances")
    
    print("\n🔍 Agents with 'pattern-recognition' capability:")
    print(f"  {orchestrator.find_agents('pattern-recognition')}")
    
    # Submit tasks
    print("\n📨 Submitting tasks...")
    
    # Task to ALBA
    result = await orchestrator.submit("alba", {"action": "collect"})
    print(f"  ALBA result: success={result.success}, duration={result.duration_ms:.2f}ms")
    
    # Task to ALBI
    result = await orchestrator.submit("albi", {"action": "detect_anomaly"})
    print(f"  ALBI result: success={result.success}, duration={result.duration_ms:.2f}ms")
    
    # Task to JONA
    result = await orchestrator.submit("jona", {"action": "recommend"})
    print(f"  JONA result: success={result.success}, duration={result.duration_ms:.2f}ms")
    
    # Broadcast to all
    print("\n📡 Broadcasting to all core agents...")
    results = await orchestrator.broadcast({"action": "health_check"})
    for name, result in results.items():
        print(f"  {name.upper()}: success={result.success}")
    
    # Scale test
    print("\n📈 Scaling ALBA to 3 instances...")
    scale_result = await orchestrator.scale("alba", 3)
    print(f"  Scale result: {scale_result}")
    
    # Status
    print("\n📊 Orchestrator Status:")
    status = orchestrator.status
    print(f"  Total tasks: {status['total_tasks_processed']}")
    print(f"  Total instances: {status['agents']['total_instances']}")
    print(f"  Available: {status['agents']['available_instances']}")
    
    # Shutdown
    await orchestrator.shutdown()
    print("\n✅ Demo complete!")


if __name__ == "__main__":
    asyncio.run(demo())

