"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    KLOUD AGENTS - BASE CLASSES                           ║
║           Unified Base Agent, Config, Status, Task, Result                  ║
╚══════════════════════════════════════════════════════════════════════════════╝

This module provides the foundational classes for all Kloud agents.
All agents MUST inherit from BaseAgent to ensure consistency.

Usage:
    from agents.base import BaseAgent, AgentConfig, AgentStatus, Task, TaskResult
    
    class MyAgent(BaseAgent):
        @property
        def config(self) -> AgentConfig:
            return AgentConfig(name="my-agent", ...)
        
        async def execute(self, task: Task) -> Any:
            return {"processed": task.payload}
"""

import asyncio
import logging
import time
import uuid
import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Dict, Any, Optional, List, TypeVar

logger = logging.getLogger("agents.base")


# ═══════════════════════════════════════════════════════════════════════════════
# ENUMS
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
    COLLECTOR = "collector"  # Web scraper, API collector, File parser
    CUSTOM = "custom"


class TaskPriority(Enum):
    """Task priority levels"""
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3
    BACKGROUND = 4


class AgentCapability(Enum):
    """Standard agent capabilities"""
    # Core capabilities
    DATA_COLLECTION = "data_collection"
    DATA_PROCESSING = "data_processing"
    DATA_VALIDATION = "data_validation"
    TRANSFORMATION = "transformation"
    
    # Analytics capabilities
    PATTERN_RECOGNITION = "pattern_recognition"
    ANOMALY_DETECTION = "anomaly_detection"
    PREDICTIVE_MODELING = "predictive_modeling"
    ANALYSIS = "analysis"
    REPORTING = "reporting"
    
    # Integration capabilities
    INTEGRATION = "integration"
    API_COLLECTION = "api_collection"
    WEB_SCRAPING = "web_scraping"
    FILE_PARSING = "file_parsing"
    
    # Advanced capabilities
    ML_INFERENCE = "ml_inference"
    NEURAL_PROCESSING = "neural_processing"
    SYNTHESIS = "synthesis"
    NATURAL_LANGUAGE = "natural_language"
    INSIGHT_GENERATION = "insight_generation"
    
    # Neuro capabilities
    EEG_PROCESSING = "eeg_processing"
    AUDIO_SYNTHESIS = "audio_synthesis"
    SIGNAL_ANALYSIS = "signal_analysis"


# ═══════════════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class AgentConfig:
    """
    Agent configuration - defines agent properties and limits.
    
    Attributes:
        name: Unique agent name (e.g., "alba", "web-scraper")
        agent_type: Classification of agent
        version: Agent version string
        capabilities: List of what the agent can do
        max_concurrent_tasks: Maximum parallel tasks
        min_instances: Minimum pool instances
        max_instances: Maximum pool instances (for scaling)
        timeout_seconds: Default task timeout
        retry_count: Number of retries on failure
        retry_delay: Delay between retries (seconds)
        health_check_interval: How often to check health
        metadata: Additional custom data
    """
    name: str
    agent_type: AgentType = AgentType.CUSTOM
    version: str = "1.0.0"
    capabilities: List[AgentCapability] = field(default_factory=list)
    max_concurrent_tasks: int = 10
    min_instances: int = 1
    max_instances: int = 5
    timeout_seconds: float = 30.0
    retry_count: int = 3
    retry_delay: float = 1.0
    health_check_interval: float = 10.0
    rate_limit_per_second: int = 10
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "name": self.name,
            "agent_type": self.agent_type.value,
            "version": self.version,
            "capabilities": [c.value for c in self.capabilities],
            "max_concurrent_tasks": self.max_concurrent_tasks,
            "min_instances": self.min_instances,
            "max_instances": self.max_instances,
            "timeout_seconds": self.timeout_seconds,
            "retry_count": self.retry_count,
            "retry_delay": self.retry_delay,
            "health_check_interval": self.health_check_interval,
            "rate_limit_per_second": self.rate_limit_per_second,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentConfig":
        """Create from dictionary"""
        return cls(
            name=data["name"],
            agent_type=AgentType(data.get("agent_type", "custom")),
            version=data.get("version", "1.0.0"),
            capabilities=[AgentCapability(c) for c in data.get("capabilities", [])],
            max_concurrent_tasks=data.get("max_concurrent_tasks", 10),
            min_instances=data.get("min_instances", 1),
            max_instances=data.get("max_instances", 5),
            timeout_seconds=data.get("timeout_seconds", 30.0),
            retry_count=data.get("retry_count", 3),
            retry_delay=data.get("retry_delay", 1.0),
            health_check_interval=data.get("health_check_interval", 10.0),
            rate_limit_per_second=data.get("rate_limit_per_second", 10),
            metadata=data.get("metadata", {})
        )


@dataclass
class AgentMetrics:
    """
    Agent performance metrics - tracks execution statistics.
    
    Used for monitoring, load balancing decisions, and health checks.
    """
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
    
    def record_success(self, duration_ms: float):
        """Record a successful task completion"""
        self.total_tasks += 1
        self.completed_tasks += 1
        self.update_response_time(duration_ms)
        self._update_error_rate()
    
    def record_failure(self, duration_ms: float):
        """Record a failed task"""
        self.total_tasks += 1
        self.failed_tasks += 1
        self.update_response_time(duration_ms)
        self._update_error_rate()
    
    def _update_error_rate(self):
        """Update error rate percentage"""
        if self.total_tasks > 0:
            self.error_rate = (self.failed_tasks / self.total_tasks) * 100
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage"""
        if self.total_tasks == 0:
            return 100.0
        return (self.completed_tasks / self.total_tasks) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass 
class Task:
    """
    Task representation - a unit of work for an agent.
    
    Attributes:
        task_id: Unique identifier
        agent_name: Target agent name
        payload: Task data/parameters
        priority: Execution priority
        created_at: Creation timestamp
        timeout: Task-specific timeout
        retry_count: Current retry attempt
        max_retries: Maximum retry attempts
        metadata: Additional task data
    """
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
        """For priority queue ordering - lower priority value = higher priority"""
        return self.priority.value < other.priority.value
    
    def can_retry(self) -> bool:
        """Check if task can be retried"""
        return self.retry_count < self.max_retries
    
    def increment_retry(self) -> "Task":
        """Create new task with incremented retry count"""
        return Task(
            task_id=self.task_id,
            agent_name=self.agent_name,
            payload=self.payload,
            priority=self.priority,
            created_at=self.created_at,
            timeout=self.timeout,
            retry_count=self.retry_count + 1,
            max_retries=self.max_retries,
            metadata=self.metadata
        )
    
    @classmethod
    def create(
        cls,
        agent_name: str,
        payload: Dict[str, Any],
        priority: TaskPriority = TaskPriority.NORMAL,
        timeout: float = 30.0,
        max_retries: int = 3
    ) -> "Task":
        """Factory method to create a new task with auto-generated ID"""
        return cls(
            task_id=f"task_{uuid.uuid4().hex[:12]}",
            agent_name=agent_name,
            payload=payload,
            priority=priority,
            timeout=timeout,
            max_retries=max_retries
        )


@dataclass
class TaskResult:
    """
    Task execution result.
    
    Attributes:
        task_id: Original task ID
        agent_id: Agent that executed the task
        success: Whether execution succeeded
        result: Task output (if successful)
        error: Error message (if failed)
        duration_ms: Execution time in milliseconds
        completed_at: Completion timestamp
    """
    task_id: str
    agent_id: str
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    duration_ms: float = 0.0
    completed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "task_id": self.task_id,
            "agent_id": self.agent_id,
            "success": self.success,
            "result": self.result,
            "error": self.error,
            "duration_ms": self.duration_ms,
            "completed_at": self.completed_at
        }


# ═══════════════════════════════════════════════════════════════════════════════
# BASE AGENT CLASS
# ═══════════════════════════════════════════════════════════════════════════════

class BaseAgent(ABC):
    """
    Abstract base class for all Kloud agents.
    
    ALL agents must inherit from this class and implement:
    - config property: Return agent configuration
    - execute method: Process a task and return result
    
    Optional overrides:
    - initialize: Custom initialization logic
    - shutdown: Custom cleanup logic
    - health_check: Custom health check
    
    Example:
        class MyAgent(BaseAgent):
            @property
            def config(self) -> AgentConfig:
                return AgentConfig(
                    name="my-agent",
                    agent_type=AgentType.PROCESSING,
                    capabilities=[AgentCapability.DATA_PROCESSING]
                )
            
            async def execute(self, task: Task) -> Any:
                data = task.payload.get("data")
                processed = self.process(data)
                return {"processed": processed}
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
        self._logger = logging.getLogger(f"agents.{self.config.name}")
    
    # ─────────────────────────────────────────────────────────────────────────
    # Properties
    # ─────────────────────────────────────────────────────────────────────────
    
    @property
    def id(self) -> str:
        """Unique agent instance ID"""
        return self._id
    
    @property 
    def status(self) -> AgentStatus:
        """Current agent status"""
        return self._status
    
    @status.setter
    def status(self, value: AgentStatus):
        self._status = value
    
    @property
    def metrics(self) -> AgentMetrics:
        """Agent performance metrics"""
        self._metrics.uptime_seconds = time.time() - self._start_time
        self._metrics.current_load = len(self._current_tasks)
        self._metrics.last_heartbeat = datetime.now(timezone.utc).isoformat()
        return self._metrics
    
    @property
    def logger(self) -> logging.Logger:
        """Agent-specific logger"""
        return self._logger
    
    # ─────────────────────────────────────────────────────────────────────────
    # Abstract methods - MUST implement
    # ─────────────────────────────────────────────────────────────────────────
    
    @property
    @abstractmethod
    def config(self) -> AgentConfig:
        """
        Return agent configuration. 
        
        MUST be implemented by all agents.
        """
        pass
    
    @abstractmethod
    async def execute(self, task: Task) -> Any:
        """
        Execute a task.
        
        MUST be implemented by all agents.
        
        Args:
            task: The task to execute
            
        Returns:
            Task result (any type - will be wrapped in TaskResult)
            
        Raises:
            Exception: If task fails (will be caught and converted to error result)
        """
        pass
    
    # ─────────────────────────────────────────────────────────────────────────
    # Lifecycle methods - CAN override
    # ─────────────────────────────────────────────────────────────────────────
    
    async def initialize(self) -> bool:
        """
        Initialize the agent.
        
        Override for custom initialization (e.g., connect to database).
        Called once when agent is first created.
        
        Returns:
            True if initialization succeeded
        """
        self._status = AgentStatus.READY
        self._logger.info(f"✅ Agent initialized: {self._id}")
        return True
    
    async def shutdown(self) -> bool:
        """
        Shutdown the agent gracefully.
        
        Override for custom cleanup (e.g., close connections).
        Will wait for current tasks to complete.
        
        Returns:
            True if shutdown succeeded
        """
        self._status = AgentStatus.DRAINING
        
        # Wait for current tasks to complete (max 30s)
        timeout = 30
        start = time.time()
        while self._current_tasks and (time.time() - start) < timeout:
            await asyncio.sleep(0.1)
        
        self._status = AgentStatus.TERMINATED
        self._logger.info(f"🛑 Agent shutdown: {self._id}")
        return True
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Health check endpoint.
        
        Override for custom health logic.
        
        Returns:
            Health status dictionary
        """
        return {
            "agent_id": self._id,
            "agent_name": self.config.name,
            "status": self._status.value,
            "healthy": self._status in [AgentStatus.READY, AgentStatus.BUSY],
            "metrics": self.metrics.to_dict(),
            "capabilities": [c.value for c in self.config.capabilities],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    # ─────────────────────────────────────────────────────────────────────────
    # Utility methods
    # ─────────────────────────────────────────────────────────────────────────
    
    def can_accept_task(self) -> bool:
        """Check if agent can accept new tasks"""
        if self._status not in [AgentStatus.READY, AgentStatus.BUSY]:
            return False
        return len(self._current_tasks) < self.config.max_concurrent_tasks
    
    def has_capability(self, capability: AgentCapability) -> bool:
        """Check if agent has a specific capability"""
        return capability in self.config.capabilities
    
    def has_any_capability(self, capabilities: List[AgentCapability]) -> bool:
        """Check if agent has any of the specified capabilities"""
        return any(c in self.config.capabilities for c in capabilities)
    
    def score_for_task(self, task: Task) -> float:
        """
        Score how well this agent matches a task (0.0 - 1.0).
        
        Higher score = better match.
        Override for custom scoring logic.
        
        Args:
            task: Task to evaluate
            
        Returns:
            Score between 0.0 and 1.0
        """
        if not self.can_accept_task():
            return 0.0
        
        score = 0.0
        
        # Capacity bonus (more capacity = higher score)
        available_capacity = self.config.max_concurrent_tasks - len(self._current_tasks)
        capacity_ratio = available_capacity / self.config.max_concurrent_tasks
        score += 0.3 * capacity_ratio
        
        # Low error rate bonus
        if self._metrics.error_rate < 5:
            score += 0.2
        elif self._metrics.error_rate < 10:
            score += 0.1
        
        # Fast response time bonus
        if self._metrics.avg_response_time_ms < 100:
            score += 0.2
        elif self._metrics.avg_response_time_ms < 500:
            score += 0.1
        
        # Experience bonus (more completed tasks = more reliable)
        if self._metrics.completed_tasks > 100:
            score += 0.2
        elif self._metrics.completed_tasks > 10:
            score += 0.1
        
        # Ready status bonus
        if self._status == AgentStatus.READY:
            score += 0.1
        
        return min(1.0, score)
    
    # ─────────────────────────────────────────────────────────────────────────
    # Internal task execution
    # ─────────────────────────────────────────────────────────────────────────
    
    async def run_task(self, task: Task) -> TaskResult:
        """
        Run a task with full lifecycle management.
        
        This method handles:
        - Task tracking
        - Status management
        - Timeout enforcement
        - Error handling
        - Metrics recording
        
        Args:
            task: Task to execute
            
        Returns:
            TaskResult with success/failure info
        """
        start_time = time.time()
        
        # Track task
        with self._lock:
            self._current_tasks[task.task_id] = task
        
        # Update status
        if len(self._current_tasks) > 0:
            self._status = AgentStatus.BUSY
        
        try:
            # Execute with timeout
            result = await asyncio.wait_for(
                self.execute(task),
                timeout=task.timeout
            )
            
            # Record success
            duration_ms = (time.time() - start_time) * 1000
            self._metrics.record_success(duration_ms)
            
            return TaskResult(
                task_id=task.task_id,
                agent_id=self._id,
                success=True,
                result=result,
                duration_ms=duration_ms
            )
            
        except asyncio.TimeoutError:
            duration_ms = (time.time() - start_time) * 1000
            self._metrics.record_failure(duration_ms)
            self._logger.error(f"Task {task.task_id} timed out after {task.timeout}s")
            
            return TaskResult(
                task_id=task.task_id,
                agent_id=self._id,
                success=False,
                error=f"Task timed out after {task.timeout}s",
                duration_ms=duration_ms
            )
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self._metrics.record_failure(duration_ms)
            self._logger.error(f"Task {task.task_id} failed: {e}")
            
            return TaskResult(
                task_id=task.task_id,
                agent_id=self._id,
                success=False,
                error=str(e),
                duration_ms=duration_ms
            )
            
        finally:
            # Remove from tracking
            with self._lock:
                self._current_tasks.pop(task.task_id, None)
            
            # Update status
            if len(self._current_tasks) == 0 and self._status == AgentStatus.BUSY:
                self._status = AgentStatus.READY
    
    # ─────────────────────────────────────────────────────────────────────────
    # String representation
    # ─────────────────────────────────────────────────────────────────────────
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self._id} status={self._status.value}>"
    
    def __str__(self) -> str:
        return f"{self.config.name}[{self._id}]"

