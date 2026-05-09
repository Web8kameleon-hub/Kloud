"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                     KLOUD AGENTS - AGENT POOL                             ║
║             Autoscaling Pool for Managing Agent Instances                    ║
╚══════════════════════════════════════════════════════════════════════════════╝

AgentPool provides:
- Autoscaling based on load (min/max instances)
- Intelligent task routing
- Health monitoring
- Instance lifecycle management
- Load balancing across instances

Usage:
    from agents.pool import AgentPool
    
    pool = AgentPool()
    await pool.register_agent_type(WebScraperAgent)
    await pool.scale("web-scraper", instances=5)
    result = await pool.submit_task(task)
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Type, Callable
from dataclasses import dataclass, field
from collections import defaultdict
import uuid

from .base import (
    BaseAgent, AgentConfig, AgentType, AgentStatus,
    Task, TaskResult, TaskPriority, AgentMetrics
)


logger = logging.getLogger("kloud.agents.pool")


# ═══════════════════════════════════════════════════════════════════════════════
# POOL CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class PoolConfig:
    """Configuration for agent pool"""
    name: str = "default-pool"
    
    # Scaling parameters
    default_min_instances: int = 1
    default_max_instances: int = 10
    scale_up_threshold: float = 0.8      # Scale up when > 80% utilized
    scale_down_threshold: float = 0.2    # Scale down when < 20% utilized
    scale_check_interval: float = 30.0   # Check scaling every 30 seconds
    
    # Health check parameters
    health_check_interval: float = 15.0
    unhealthy_threshold: int = 3         # Remove after 3 failed health checks
    
    # Task queue parameters
    max_queue_size: int = 10000
    task_timeout: float = 300.0          # 5 minute default timeout
    
    # Performance tuning
    enable_autoscaling: bool = True
    enable_health_checks: bool = True


@dataclass
class PoolStats:
    """Real-time pool statistics"""
    total_instances: int = 0
    active_instances: int = 0
    idle_instances: int = 0
    tasks_queued: int = 0
    tasks_processing: int = 0
    tasks_completed: int = 0
    tasks_failed: int = 0
    avg_task_time_ms: float = 0.0
    utilization_percent: float = 0.0
    last_updated: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "total_instances": self.total_instances,
            "active_instances": self.active_instances,
            "idle_instances": self.idle_instances,
            "tasks_queued": self.tasks_queued,
            "tasks_processing": self.tasks_processing,
            "tasks_completed": self.tasks_completed,
            "tasks_failed": self.tasks_failed,
            "avg_task_time_ms": self.avg_task_time_ms,
            "utilization_percent": self.utilization_percent,
            "last_updated": self.last_updated
        }


# ═══════════════════════════════════════════════════════════════════════════════
# AGENT INSTANCE WRAPPER
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class AgentInstance:
    """Wrapper for managing agent instances in the pool"""
    id: str
    agent: BaseAgent
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    health_check_failures: int = 0
    current_task: Optional[str] = None  # task_id if processing
    
    @property
    def is_busy(self) -> bool:
        return self.current_task is not None
    
    @property
    def is_healthy(self) -> bool:
        return (
            self.health_check_failures < 3 and
            self.agent.status in [AgentStatus.IDLE, AgentStatus.RUNNING]
        )
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "agent_name": self.agent.config.name,
            "status": self.agent.status.value,
            "is_busy": self.is_busy,
            "is_healthy": self.is_healthy,
            "current_task": self.current_task,
            "health_failures": self.health_check_failures,
            "created_at": self.created_at.isoformat()
        }


# ═══════════════════════════════════════════════════════════════════════════════
# AGENT POOL
# ═══════════════════════════════════════════════════════════════════════════════

class AgentPool:
    """
    Autoscaling pool for managing agent instances.
    
    Features:
    - Register agent types (classes)
    - Autoscale instances based on load
    - Route tasks to available instances
    - Health monitoring and auto-recovery
    - Task queue management
    
    Example:
        pool = AgentPool(PoolConfig(name="my-pool"))
        await pool.start()
        
        pool.register_agent_type("web-scraper", WebScraperAgent)
        await pool.scale("web-scraper", min_instances=2, max_instances=10)
        
        task = Task(task_id="t1", agent_name="web-scraper", payload={"action": "scrape"})
        result = await pool.submit_task(task)
        
        await pool.stop()
    """
    
    def __init__(self, config: Optional[PoolConfig] = None):
        self.config = config or PoolConfig()
        self._running = False
        
        # Agent type registry: name -> agent class
        self._agent_types: Dict[str, Type[BaseAgent]] = {}
        
        # Agent instances: name -> list of instances
        self._instances: Dict[str, List[AgentInstance]] = defaultdict(list)
        
        # Scaling config per agent type
        self._scaling: Dict[str, Dict[str, int]] = {}  # name -> {min, max}
        
        # Task queues per agent type
        self._task_queues: Dict[str, asyncio.Queue] = {}
        
        # Task tracking
        self._pending_tasks: Dict[str, Task] = {}
        self._task_results: Dict[str, TaskResult] = {}
        
        # Background tasks
        self._background_tasks: List[asyncio.Task] = []
        
        # Statistics
        self._stats: Dict[str, PoolStats] = {}
        self._task_times: List[float] = []
        
        # Locks
        self._lock = asyncio.Lock()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # LIFECYCLE
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def start(self) -> None:
        """Start the agent pool and background tasks"""
        if self._running:
            return
        
        self._running = True
        logger.info(f"Starting AgentPool: {self.config.name}")
        
        # Start background tasks
        if self.config.enable_autoscaling:
            task = asyncio.create_task(self._autoscaling_loop())
            self._background_tasks.append(task)
        
        if self.config.enable_health_checks:
            task = asyncio.create_task(self._health_check_loop())
            self._background_tasks.append(task)
        
        # Start task dispatchers for each registered agent
        for agent_name in self._agent_types:
            task = asyncio.create_task(self._task_dispatcher(agent_name))
            self._background_tasks.append(task)
    
    async def stop(self) -> None:
        """Stop the agent pool and all instances"""
        self._running = False
        logger.info(f"Stopping AgentPool: {self.config.name}")
        
        # Cancel background tasks
        for task in self._background_tasks:
            task.cancel()
        
        # Wait for cancellation
        if self._background_tasks:
            await asyncio.gather(*self._background_tasks, return_exceptions=True)
        
        # Shutdown all agent instances
        for agent_name, instances in self._instances.items():
            for instance in instances:
                try:
                    await instance.agent.shutdown()
                except Exception as e:
                    logger.error(f"Error shutting down {instance.id}: {e}")
        
        self._instances.clear()
        self._background_tasks.clear()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # AGENT TYPE REGISTRATION
    # ═══════════════════════════════════════════════════════════════════════════
    
    def register_agent_type(
        self,
        name: str,
        agent_class: Type[BaseAgent],
        min_instances: Optional[int] = None,
        max_instances: Optional[int] = None
    ) -> None:
        """
        Register an agent type with the pool.
        
        Args:
            name: Unique name for this agent type
            agent_class: The agent class to instantiate
            min_instances: Minimum instances to maintain (default from config)
            max_instances: Maximum instances allowed (default from config)
        """
        self._agent_types[name] = agent_class
        self._scaling[name] = {
            "min": min_instances or self.config.default_min_instances,
            "max": max_instances or self.config.default_max_instances
        }
        self._task_queues[name] = asyncio.Queue(maxsize=self.config.max_queue_size)
        self._stats[name] = PoolStats()
        
        logger.info(
            f"Registered agent type: {name} "
            f"(min={self._scaling[name]['min']}, max={self._scaling[name]['max']})"
        )
    
    def unregister_agent_type(self, name: str) -> None:
        """Unregister an agent type"""
        if name in self._agent_types:
            del self._agent_types[name]
            del self._scaling[name]
            if name in self._task_queues:
                del self._task_queues[name]
            if name in self._stats:
                del self._stats[name]
            logger.info(f"Unregistered agent type: {name}")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # INSTANCE MANAGEMENT
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def scale(
        self,
        agent_name: str,
        instances: Optional[int] = None,
        min_instances: Optional[int] = None,
        max_instances: Optional[int] = None
    ) -> int:
        """
        Scale agent instances.
        
        Args:
            agent_name: Name of the agent type
            instances: Target number of instances (optional)
            min_instances: New minimum (optional)
            max_instances: New maximum (optional)
            
        Returns:
            Current number of instances after scaling
        """
        if agent_name not in self._agent_types:
            raise ValueError(f"Unknown agent type: {agent_name}")
        
        async with self._lock:
            # Update scaling limits if provided
            if min_instances is not None:
                self._scaling[agent_name]["min"] = min_instances
            if max_instances is not None:
                self._scaling[agent_name]["max"] = max_instances
            
            current = len(self._instances[agent_name])
            target = instances if instances is not None else current
            
            # Clamp to limits
            min_limit = self._scaling[agent_name]["min"]
            max_limit = self._scaling[agent_name]["max"]
            target = max(min_limit, min(max_limit, target))
            
            if target > current:
                # Scale up
                for _ in range(target - current):
                    await self._create_instance(agent_name)
            elif target < current:
                # Scale down - remove idle instances
                to_remove = current - target
                removed = 0
                for instance in list(self._instances[agent_name]):
                    if removed >= to_remove:
                        break
                    if not instance.is_busy:
                        await self._remove_instance(agent_name, instance.id)
                        removed += 1
            
            return len(self._instances[agent_name])
    
    async def _create_instance(self, agent_name: str) -> AgentInstance:
        """Create a new agent instance"""
        if agent_name not in self._agent_types:
            raise ValueError(f"Unknown agent type: {agent_name}")
        
        agent_class = self._agent_types[agent_name]
        agent = agent_class()
        
        instance = AgentInstance(
            id=f"{agent_name}-{uuid.uuid4().hex[:8]}",
            agent=agent
        )
        
        # Initialize the agent
        await agent.initialize()
        
        self._instances[agent_name].append(instance)
        logger.debug(f"Created instance: {instance.id}")
        
        return instance
    
    async def _remove_instance(self, agent_name: str, instance_id: str) -> bool:
        """Remove an agent instance"""
        instances = self._instances[agent_name]
        
        for i, instance in enumerate(instances):
            if instance.id == instance_id:
                # Shutdown the agent
                await instance.agent.shutdown()
                instances.pop(i)
                logger.debug(f"Removed instance: {instance_id}")
                return True
        
        return False
    
    # ═══════════════════════════════════════════════════════════════════════════
    # TASK SUBMISSION
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def submit_task(
        self,
        task: Task,
        wait: bool = True,
        timeout: Optional[float] = None
    ) -> Optional[TaskResult]:
        """
        Submit a task to the pool.
        
        Args:
            task: Task to execute
            wait: If True, wait for result; otherwise return immediately
            timeout: Maximum time to wait for result
            
        Returns:
            TaskResult if wait=True, else None
        """
        agent_name = task.agent_name
        
        if agent_name not in self._agent_types:
            return TaskResult(
                task_id=task.task_id,
                success=False,
                error=f"Unknown agent type: {agent_name}"
            )
        
        # Ensure minimum instances exist
        if len(self._instances[agent_name]) < self._scaling[agent_name]["min"]:
            await self.scale(agent_name, self._scaling[agent_name]["min"])
        
        # Add to queue
        self._pending_tasks[task.task_id] = task
        await self._task_queues[agent_name].put(task)
        
        # Update stats
        self._stats[agent_name].tasks_queued += 1
        
        if not wait:
            return None
        
        # Wait for result
        timeout = timeout or self.config.task_timeout
        start = datetime.now(timezone.utc)
        
        while True:
            if task.task_id in self._task_results:
                return self._task_results.pop(task.task_id)
            
            elapsed = (datetime.now(timezone.utc) - start).total_seconds()
            if elapsed > timeout:
                return TaskResult(
                    task_id=task.task_id,
                    success=False,
                    error="Task timeout"
                )
            
            await asyncio.sleep(0.1)
    
    async def submit_batch(
        self,
        tasks: List[Task],
        wait: bool = True
    ) -> List[TaskResult]:
        """
        Submit multiple tasks.
        
        Args:
            tasks: List of tasks
            wait: If True, wait for all results
            
        Returns:
            List of TaskResults
        """
        if wait:
            # Submit all and gather results
            results = await asyncio.gather(
                *[self.submit_task(task, wait=True) for task in tasks],
                return_exceptions=True
            )
            
            return [
                r if isinstance(r, TaskResult) else TaskResult(
                    task_id=task.task_id,
                    success=False,
                    error=str(r)
                )
                for task, r in zip(tasks, results)
            ]
        else:
            for task in tasks:
                await self.submit_task(task, wait=False)
            return []
    
    # ═══════════════════════════════════════════════════════════════════════════
    # BACKGROUND TASKS
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def _task_dispatcher(self, agent_name: str) -> None:
        """Background task that dispatches tasks to agent instances"""
        queue = self._task_queues[agent_name]
        
        while self._running:
            try:
                # Get task with timeout
                try:
                    task = await asyncio.wait_for(queue.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue
                
                # Find available instance
                instance = await self._get_available_instance(agent_name)
                
                if instance is None:
                    # No instance available, try to scale up
                    current = len(self._instances[agent_name])
                    max_limit = self._scaling[agent_name]["max"]
                    
                    if current < max_limit:
                        instance = await self._create_instance(agent_name)
                    else:
                        # Put task back and wait
                        await queue.put(task)
                        await asyncio.sleep(0.5)
                        continue
                
                # Dispatch task to instance
                asyncio.create_task(self._execute_on_instance(instance, task, agent_name))
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Dispatcher error for {agent_name}: {e}")
                await asyncio.sleep(1.0)
    
    async def _get_available_instance(self, agent_name: str) -> Optional[AgentInstance]:
        """Find an available (idle) instance"""
        for instance in self._instances[agent_name]:
            if not instance.is_busy and instance.is_healthy:
                return instance
        return None
    
    async def _execute_on_instance(
        self,
        instance: AgentInstance,
        task: Task,
        agent_name: str
    ) -> None:
        """Execute a task on a specific instance"""
        instance.current_task = task.task_id
        self._stats[agent_name].tasks_processing += 1
        self._stats[agent_name].tasks_queued -= 1
        
        start_time = datetime.now(timezone.utc)
        
        try:
            result = await instance.agent.run_task(task)
            
            # Record success
            self._stats[agent_name].tasks_completed += 1
            
        except Exception as e:
            result = TaskResult(
                task_id=task.task_id,
                success=False,
                error=str(e)
            )
            self._stats[agent_name].tasks_failed += 1
        
        # Record timing
        elapsed_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
        self._task_times.append(elapsed_ms)
        if len(self._task_times) > 1000:
            self._task_times = self._task_times[-500:]
        
        # Update stats
        self._stats[agent_name].tasks_processing -= 1
        if self._task_times:
            self._stats[agent_name].avg_task_time_ms = sum(self._task_times) / len(self._task_times)
        
        # Store result
        self._task_results[task.task_id] = result
        
        # Cleanup
        instance.current_task = None
        if task.task_id in self._pending_tasks:
            del self._pending_tasks[task.task_id]
    
    async def _autoscaling_loop(self) -> None:
        """Background task for autoscaling"""
        while self._running:
            try:
                await asyncio.sleep(self.config.scale_check_interval)
                
                for agent_name in list(self._agent_types.keys()):
                    await self._check_scaling(agent_name)
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Autoscaling error: {e}")
    
    async def _check_scaling(self, agent_name: str) -> None:
        """Check if scaling is needed for an agent type"""
        instances = self._instances[agent_name]
        if not instances:
            return
        
        busy = sum(1 for i in instances if i.is_busy)
        total = len(instances)
        utilization = busy / total if total > 0 else 0
        
        # Update stats
        self._stats[agent_name].total_instances = total
        self._stats[agent_name].active_instances = busy
        self._stats[agent_name].idle_instances = total - busy
        self._stats[agent_name].utilization_percent = utilization * 100
        self._stats[agent_name].last_updated = datetime.now(timezone.utc).isoformat()
        
        min_limit = self._scaling[agent_name]["min"]
        max_limit = self._scaling[agent_name]["max"]
        
        # Scale up if utilization is high
        if utilization > self.config.scale_up_threshold and total < max_limit:
            await self.scale(agent_name, total + 1)
            logger.info(f"Scaled up {agent_name}: {total} -> {total + 1}")
        
        # Scale down if utilization is low
        elif utilization < self.config.scale_down_threshold and total > min_limit:
            await self.scale(agent_name, total - 1)
            logger.info(f"Scaled down {agent_name}: {total} -> {total - 1}")
    
    async def _health_check_loop(self) -> None:
        """Background task for health checks"""
        while self._running:
            try:
                await asyncio.sleep(self.config.health_check_interval)
                
                for agent_name, instances in list(self._instances.items()):
                    for instance in list(instances):
                        is_healthy = await self._check_instance_health(instance)
                        
                        if not is_healthy:
                            instance.health_check_failures += 1
                            
                            if instance.health_check_failures >= self.config.unhealthy_threshold:
                                logger.warning(f"Removing unhealthy instance: {instance.id}")
                                await self._remove_instance(agent_name, instance.id)
                                
                                # Replace if below minimum
                                if len(self._instances[agent_name]) < self._scaling[agent_name]["min"]:
                                    await self._create_instance(agent_name)
                        else:
                            instance.health_check_failures = 0
                            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check error: {e}")
    
    async def _check_instance_health(self, instance: AgentInstance) -> bool:
        """Check if an instance is healthy"""
        try:
            return await instance.agent.health_check()
        except Exception:
            return False
    
    # ═══════════════════════════════════════════════════════════════════════════
    # STATUS & METRICS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def get_stats(self, agent_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get pool statistics.
        
        Args:
            agent_name: Specific agent type, or None for all
            
        Returns:
            Statistics dictionary
        """
        if agent_name:
            return self._stats.get(agent_name, PoolStats()).to_dict()
        
        return {
            name: stats.to_dict()
            for name, stats in self._stats.items()
        }
    
    def get_instances(self, agent_name: Optional[str] = None) -> List[Dict]:
        """
        Get instance information.
        
        Args:
            agent_name: Specific agent type, or None for all
            
        Returns:
            List of instance dictionaries
        """
        if agent_name:
            return [i.to_dict() for i in self._instances.get(agent_name, [])]
        
        result = []
        for instances in self._instances.values():
            result.extend([i.to_dict() for i in instances])
        return result
    
    def get_pool_summary(self) -> Dict[str, Any]:
        """Get overall pool summary"""
        total_instances = sum(len(instances) for instances in self._instances.values())
        total_busy = sum(
            sum(1 for i in instances if i.is_busy)
            for instances in self._instances.values()
        )
        
        return {
            "pool_name": self.config.name,
            "running": self._running,
            "agent_types_registered": len(self._agent_types),
            "total_instances": total_instances,
            "busy_instances": total_busy,
            "idle_instances": total_instances - total_busy,
            "pending_tasks": len(self._pending_tasks),
            "agent_types": list(self._agent_types.keys()),
            "stats_by_agent": self.get_stats()
        }


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

# Global default pool
_default_pool: Optional[AgentPool] = None


def get_default_pool() -> AgentPool:
    """Get or create the default agent pool"""
    global _default_pool
    if _default_pool is None:
        _default_pool = AgentPool(PoolConfig(name="default"))
    return _default_pool


async def create_pool(config: Optional[PoolConfig] = None) -> AgentPool:
    """Create and start a new pool"""
    pool = AgentPool(config)
    await pool.start()
    return pool

