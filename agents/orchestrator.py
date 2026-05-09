"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                   KLOUD AGENTS - ORCHESTRATOR                             ║
║              Central Coordination for All Agent Operations                   ║
╚══════════════════════════════════════════════════════════════════════════════╝

AgentOrchestrator is the main entry point for the agent system.

Features:
- Unified interface for all agent operations
- Task routing and distribution
- Workflow orchestration
- Health monitoring
- Telemetry integration

Usage:
    from agents import AgentOrchestrator
    
    orchestrator = AgentOrchestrator()
    await orchestrator.start()
    
    result = await orchestrator.execute("web-scraper", {"action": "scrape", "url": "..."})
    
    await orchestrator.stop()
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
import uuid

from .base import (
    BaseAgent, AgentConfig, AgentType, AgentStatus,
    AgentCapability, Task, TaskResult, TaskPriority
)
from .pool import AgentPool, PoolConfig
from .registry import AgentRegistry, get_registry
from .core import (
    ALBAAgent, ALBIAgent, JONAAgent, TrinitySystem,
    create_core_agent
)
from .specialized import (
    DataProcessingAgent, AnalyticsAgent, IntegrationAgent,
    MLAgent, WebScraperAgent, APICollectorAgent, FileParserAgent,
    create_specialized_agent
)


logger = logging.getLogger("kloud.agents.orchestrator")


# ═══════════════════════════════════════════════════════════════════════════════
# ORCHESTRATOR CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class OrchestratorConfig:
    """Configuration for the orchestrator"""
    name: str = "kloud-orchestrator"
    
    # Pool settings
    enable_autoscaling: bool = True
    default_min_instances: int = 1
    default_max_instances: int = 10
    
    # Core agents (ASI Trinity)
    enable_alba: bool = True
    enable_albi: bool = True
    enable_jona: bool = True
    
    # Specialized agents
    enable_data_processor: bool = True
    enable_analytics: bool = True
    enable_integration: bool = True
    enable_ml: bool = True
    enable_web_scraper: bool = True
    enable_api_collector: bool = True
    enable_file_parser: bool = True
    
    # Health check
    health_check_interval: float = 30.0
    
    # Telemetry
    enable_telemetry: bool = True


# ═══════════════════════════════════════════════════════════════════════════════
# WORKFLOW DEFINITION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class WorkflowStep:
    """Single step in a workflow"""
    agent_name: str
    action: str
    params: Dict[str, Any]
    depends_on: Optional[List[str]] = None  # Step IDs this depends on
    step_id: Optional[str] = None
    
    def __post_init__(self):
        if self.step_id is None:
            self.step_id = f"step_{uuid.uuid4().hex[:8]}"


@dataclass
class Workflow:
    """Multi-step workflow definition"""
    name: str
    steps: List[WorkflowStep]
    workflow_id: Optional[str] = None
    
    def __post_init__(self):
        if self.workflow_id is None:
            self.workflow_id = f"wf_{uuid.uuid4().hex[:8]}"


# ═══════════════════════════════════════════════════════════════════════════════
# AGENT ORCHESTRATOR
# ═══════════════════════════════════════════════════════════════════════════════

class AgentOrchestrator:
    """
    Central orchestrator for all agent operations.
    
    This is the main entry point for:
    - Creating and managing agents
    - Submitting tasks
    - Running workflows
    - Monitoring system health
    
    Example:
        async with AgentOrchestrator() as orchestrator:
            # Simple task
            result = await orchestrator.execute(
                "web-scraper",
                {"action": "scrape", "url": "https://example.com"}
            )
            
            # Use core agent
            alba_result = await orchestrator.alba.collect({"source": "api"})
            
            # Run workflow
            workflow = Workflow(
                name="data-pipeline",
                steps=[
                    WorkflowStep("api-collector", "fetch", {"url": "..."}),
                    WorkflowStep("data-processor", "validate", {}, depends_on=["step_1"]),
                    WorkflowStep("analytics", "analyze", {}, depends_on=["step_2"])
                ]
            )
            results = await orchestrator.run_workflow(workflow)
    """
    
    def __init__(self, config: Optional[OrchestratorConfig] = None):
        self.config = config or OrchestratorConfig()
        self._running = False
        
        # Core components
        self._pool: Optional[AgentPool] = None
        self._registry: AgentRegistry = get_registry()
        
        # Core agents (ASI Trinity)
        self._alba: Optional[ALBAAgent] = None
        self._albi: Optional[ALBIAgent] = None
        self._jona: Optional[JONAAgent] = None
        self._trinity: Optional[TrinitySystem] = None
        
        # Background tasks
        self._background_tasks: List[asyncio.Task] = []
        
        # Task history
        self._task_history: List[TaskResult] = []
        self._max_history = 1000
    
    # ═══════════════════════════════════════════════════════════════════════════
    # CONTEXT MANAGER
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def __aenter__(self) -> "AgentOrchestrator":
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # LIFECYCLE
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def start(self) -> None:
        """Start the orchestrator and all components"""
        if self._running:
            return
        
        logger.info(f"Starting {self.config.name}...")
        
        # Initialize pool
        pool_config = PoolConfig(
            name=f"{self.config.name}-pool",
            enable_autoscaling=self.config.enable_autoscaling,
            default_min_instances=self.config.default_min_instances,
            default_max_instances=self.config.default_max_instances,
            health_check_interval=self.config.health_check_interval
        )
        self._pool = AgentPool(pool_config)
        
        # Register agent types with pool
        await self._register_agent_types()
        
        # Initialize core agents
        await self._initialize_core_agents()
        
        # Start pool
        await self._pool.start()
        
        # Start background tasks
        if self.config.health_check_interval > 0:
            task = asyncio.create_task(self._health_monitor_loop())
            self._background_tasks.append(task)
        
        self._running = True
        logger.info(f"{self.config.name} started successfully")
    
    async def stop(self) -> None:
        """Stop the orchestrator and all components"""
        if not self._running:
            return
        
        logger.info(f"Stopping {self.config.name}...")
        
        # Cancel background tasks
        for task in self._background_tasks:
            task.cancel()
        
        if self._background_tasks:
            await asyncio.gather(*self._background_tasks, return_exceptions=True)
        
        # Shutdown core agents
        if self._trinity:
            await self._trinity.shutdown()
        else:
            for agent in [self._alba, self._albi, self._jona]:
                if agent:
                    await agent.shutdown()
        
        # Stop pool
        if self._pool:
            await self._pool.stop()
        
        self._running = False
        logger.info(f"{self.config.name} stopped")
    
    async def _register_agent_types(self) -> None:
        """Register all agent types with the pool"""
        if not self._pool:
            return
        
        # Core agents
        if self.config.enable_alba:
            self._pool.register_agent_type("alba", ALBAAgent, min_instances=1)
        if self.config.enable_albi:
            self._pool.register_agent_type("albi", ALBIAgent, min_instances=1)
        if self.config.enable_jona:
            self._pool.register_agent_type("jona", JONAAgent, min_instances=1)
        
        # Specialized agents
        if self.config.enable_data_processor:
            self._pool.register_agent_type("data-processor", DataProcessingAgent)
        if self.config.enable_analytics:
            self._pool.register_agent_type("analytics", AnalyticsAgent)
        if self.config.enable_integration:
            self._pool.register_agent_type("integration", IntegrationAgent)
        if self.config.enable_ml:
            self._pool.register_agent_type("ml-agent", MLAgent, max_instances=3)
        if self.config.enable_web_scraper:
            self._pool.register_agent_type("web-scraper", WebScraperAgent, max_instances=20)
        if self.config.enable_api_collector:
            self._pool.register_agent_type("api-collector", APICollectorAgent, max_instances=15)
        if self.config.enable_file_parser:
            self._pool.register_agent_type("file-parser", FileParserAgent)
    
    async def _initialize_core_agents(self) -> None:
        """Initialize core ASI Trinity agents"""
        if self.config.enable_alba:
            self._alba = ALBAAgent()
            await self._alba.initialize()
            self._registry.register(self._alba, "alba-primary")
        
        if self.config.enable_albi:
            self._albi = ALBIAgent()
            await self._albi.initialize()
            self._registry.register(self._albi, "albi-primary")
        
        if self.config.enable_jona:
            self._jona = JONAAgent()
            await self._jona.initialize()
            self._registry.register(self._jona, "jona-primary")
        
        # Create Trinity if all three are available
        if self._alba and self._albi and self._jona:
            self._trinity = TrinitySystem(self._alba, self._albi, self._jona)
            await self._trinity.initialize()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # CORE AGENT ACCESS
    # ═══════════════════════════════════════════════════════════════════════════
    
    @property
    def alba(self) -> Optional[ALBAAgent]:
        """Access ALBA agent (Data Collection)"""
        return self._alba
    
    @property
    def albi(self) -> Optional[ALBIAgent]:
        """Access ALBI agent (Neural Analytics)"""
        return self._albi
    
    @property
    def jona(self) -> Optional[JONAAgent]:
        """Access JONA agent (Synthesis)"""
        return self._jona
    
    @property
    def trinity(self) -> Optional[TrinitySystem]:
        """Access Trinity System (coordinated core agents)"""
        return self._trinity
    
    # ═══════════════════════════════════════════════════════════════════════════
    # TASK EXECUTION
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def execute(
        self,
        agent_name: str,
        payload: Dict[str, Any],
        priority: TaskPriority = TaskPriority.NORMAL,
        timeout: Optional[float] = None
    ) -> TaskResult:
        """
        Execute a task on a specified agent.
        
        Args:
            agent_name: Name of the agent type
            payload: Task payload (must include 'action')
            priority: Task priority
            timeout: Optional timeout override
            
        Returns:
            TaskResult with execution results
        """
        if not self._running or not self._pool:
            return TaskResult(
                task_id="error",
                success=False,
                error="Orchestrator not running"
            )
        
        task = Task(
            task_id=f"task_{uuid.uuid4().hex[:12]}",
            agent_name=agent_name,
            payload=payload,
            priority=priority
        )
        
        result = await self._pool.submit_task(task, wait=True, timeout=timeout)
        
        # Record in history
        if result:
            self._task_history.append(result)
            if len(self._task_history) > self._max_history:
                self._task_history = self._task_history[-500:]
        
        return result
    
    async def execute_batch(
        self,
        tasks: List[Dict[str, Any]]
    ) -> List[TaskResult]:
        """
        Execute multiple tasks in parallel.
        
        Args:
            tasks: List of dicts with 'agent_name' and 'payload'
            
        Returns:
            List of TaskResults
        """
        task_objects = [
            Task(
                task_id=f"task_{uuid.uuid4().hex[:12]}",
                agent_name=t["agent_name"],
                payload=t["payload"],
                priority=t.get("priority", TaskPriority.NORMAL)
            )
            for t in tasks
        ]
        
        return await self._pool.submit_batch(task_objects, wait=True)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # WORKFLOW EXECUTION
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def run_workflow(
        self,
        workflow: Workflow
    ) -> Dict[str, TaskResult]:
        """
        Execute a multi-step workflow.
        
        Args:
            workflow: Workflow definition
            
        Returns:
            Dict mapping step_id to TaskResult
        """
        logger.info(f"Running workflow: {workflow.name} ({workflow.workflow_id})")
        
        results: Dict[str, TaskResult] = {}
        completed_steps: set = set()
        
        # Process steps respecting dependencies
        remaining = list(workflow.steps)
        
        while remaining:
            # Find steps that can run now
            runnable = []
            still_waiting = []
            
            for step in remaining:
                if step.depends_on is None or all(d in completed_steps for d in step.depends_on):
                    runnable.append(step)
                else:
                    still_waiting.append(step)
            
            if not runnable:
                # Deadlock - dependencies can't be satisfied
                logger.error(f"Workflow deadlock: {[s.step_id for s in still_waiting]}")
                break
            
            # Execute runnable steps in parallel
            step_tasks = []
            for step in runnable:
                # Merge previous results if depends_on exists
                payload = dict(step.params)
                if step.depends_on:
                    payload["_previous_results"] = {
                        dep_id: results[dep_id].data
                        for dep_id in step.depends_on
                        if dep_id in results and results[dep_id].data
                    }
                payload["action"] = step.action
                
                step_tasks.append((
                    step.step_id,
                    self.execute(step.agent_name, payload)
                ))
            
            # Wait for all runnable steps
            for step_id, coro in step_tasks:
                result = await coro
                results[step_id] = result
                completed_steps.add(step_id)
            
            remaining = still_waiting
        
        logger.info(f"Workflow {workflow.workflow_id} completed: {len(results)} steps")
        return results
    
    # ═══════════════════════════════════════════════════════════════════════════
    # CONVENIENCE METHODS
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def scrape(self, url: str, **kwargs) -> TaskResult:
        """Convenience: Scrape a URL"""
        return await self.execute("web-scraper", {"action": "scrape", "url": url, **kwargs})
    
    async def fetch_api(self, url: str, method: str = "GET", **kwargs) -> TaskResult:
        """Convenience: Fetch from API"""
        return await self.execute("api-collector", {
            "action": "fetch", "url": url, "method": method, **kwargs
        })
    
    async def process_data(self, data: Any, action: str = "validate", **kwargs) -> TaskResult:
        """Convenience: Process data"""
        return await self.execute("data-processor", {
            "action": action, "data": data, **kwargs
        })
    
    async def analyze(self, data: Any, **kwargs) -> TaskResult:
        """Convenience: Analyze data"""
        return await self.execute("analytics", {"action": "analyze", "data": data, **kwargs})
    
    async def predict(self, data: Dict, model: str = "classifier") -> TaskResult:
        """Convenience: Run ML prediction (requires MATURE data)"""
        return await self.execute("ml-agent", {
            "action": "predict", "data": data, "model": model
        })
    
    # ═══════════════════════════════════════════════════════════════════════════
    # MONITORING
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def _health_monitor_loop(self) -> None:
        """Background health monitoring"""
        while self._running:
            try:
                await asyncio.sleep(self.config.health_check_interval)
                await self._registry.check_all_health()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health monitor error: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get orchestrator status"""
        pool_summary = self._pool.get_pool_summary() if self._pool else {}
        registry_stats = self._registry.get_stats()
        
        return {
            "name": self.config.name,
            "running": self._running,
            "pool": pool_summary,
            "registry": registry_stats,
            "core_agents": {
                "alba": self._alba.status.value if self._alba else "disabled",
                "albi": self._albi.status.value if self._albi else "disabled",
                "jona": self._jona.status.value if self._jona else "disabled",
                "trinity": "active" if self._trinity else "disabled"
            },
            "task_history_count": len(self._task_history),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def get_task_history(self, limit: int = 100) -> List[Dict]:
        """Get recent task history"""
        return [r.to_dict() for r in self._task_history[-limit:]]


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

_global_orchestrator: Optional[AgentOrchestrator] = None


async def get_orchestrator() -> AgentOrchestrator:
    """Get or create global orchestrator"""
    global _global_orchestrator
    if _global_orchestrator is None:
        _global_orchestrator = AgentOrchestrator()
        await _global_orchestrator.start()
    return _global_orchestrator


async def shutdown_orchestrator() -> None:
    """Shutdown global orchestrator"""
    global _global_orchestrator
    if _global_orchestrator:
        await _global_orchestrator.stop()
        _global_orchestrator = None

