"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                     KLOUD AGENTS - CYCLES                                 ║
║              Cycle Engine Integration for Agent Operations                   ║
╚══════════════════════════════════════════════════════════════════════════════╝

Bridges agents with the Cycle Engine:
- Link agents to cycle phases
- Maturity-aware processing
- Cycle-triggered agent actions

Usage:
    from agents.cycles import CycleAgentBridge, link_agent_to_cycle
    
    bridge = CycleAgentBridge()
    bridge.register_cycle_handler("extract", alba_agent)
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Callable, Type
from dataclasses import dataclass, field
from enum import Enum

from .base import BaseAgent, Task, TaskResult, AgentCapability
from .core import ALBAAgent, ALBIAgent, JONAAgent


logger = logging.getLogger("kloud.agents.cycles")


# ═══════════════════════════════════════════════════════════════════════════════
# CYCLE DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════════════

class CyclePhase(str, Enum):
    """Phases in the data cycle"""
    EXTRACT = "extract"          # Data extraction/collection
    VALIDATE = "validate"        # Data validation
    TRANSFORM = "transform"      # Data transformation
    ENRICH = "enrich"            # Data enrichment
    ANALYZE = "analyze"          # Data analysis
    SYNTHESIZE = "synthesize"    # Cross-source synthesis
    STORE = "store"              # Data storage
    PUBLISH = "publish"          # Data publishing


class MaturityState(str, Enum):
    """Data maturity states"""
    IMMATURE = "IMMATURE"        # Raw, unprocessed data
    DEVELOPING = "DEVELOPING"    # Partially processed
    MATURE = "MATURE"            # Fully processed, ready for ML


@dataclass
class CycleContext:
    """Context passed through cycle phases"""
    cycle_id: str
    phase: CyclePhase
    maturity: MaturityState
    data: Any
    metadata: Dict[str, Any] = field(default_factory=dict)
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "cycle_id": self.cycle_id,
            "phase": self.phase.value,
            "maturity": self.maturity.value,
            "metadata": self.metadata,
            "started_at": self.started_at.isoformat(),
            "errors": self.errors
        }


# ═══════════════════════════════════════════════════════════════════════════════
# CYCLE-AGENT MAPPING
# ═══════════════════════════════════════════════════════════════════════════════

# Default mapping of cycle phases to agent capabilities
PHASE_CAPABILITY_MAP: Dict[CyclePhase, List[AgentCapability]] = {
    CyclePhase.EXTRACT: [
        AgentCapability.DATA_COLLECTION,
        AgentCapability.WEB_SCRAPING,
        AgentCapability.API_COLLECTION,
        AgentCapability.FILE_PARSING
    ],
    CyclePhase.VALIDATE: [
        AgentCapability.DATA_VALIDATION
    ],
    CyclePhase.TRANSFORM: [
        AgentCapability.TRANSFORMATION,
        AgentCapability.DATA_PROCESSING
    ],
    CyclePhase.ENRICH: [
        AgentCapability.DATA_PROCESSING,
        AgentCapability.INTEGRATION
    ],
    CyclePhase.ANALYZE: [
        AgentCapability.ANALYSIS,
        AgentCapability.PREDICTIVE_MODELING
    ],
    CyclePhase.SYNTHESIZE: [
        AgentCapability.SYNTHESIS,
        AgentCapability.INSIGHT_GENERATION
    ],
    CyclePhase.STORE: [
        AgentCapability.DATA_PROCESSING
    ],
    CyclePhase.PUBLISH: [
        AgentCapability.REPORTING,
        AgentCapability.INTEGRATION
    ]
}

# Default mapping of cycle phases to core agents
PHASE_CORE_AGENT_MAP: Dict[CyclePhase, str] = {
    CyclePhase.EXTRACT: "alba",      # ALBA handles data collection
    CyclePhase.VALIDATE: "alba",
    CyclePhase.TRANSFORM: "albi",    # ALBI handles processing
    CyclePhase.ENRICH: "albi",
    CyclePhase.ANALYZE: "albi",
    CyclePhase.SYNTHESIZE: "jona",   # JONA handles synthesis
    CyclePhase.STORE: "alba",
    CyclePhase.PUBLISH: "jona"
}


# ═══════════════════════════════════════════════════════════════════════════════
# CYCLE HANDLER
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class CycleHandler:
    """Handler for a cycle phase"""
    phase: CyclePhase
    agent: BaseAgent
    action: str
    condition: Optional[Callable[[CycleContext], bool]] = None
    transform_input: Optional[Callable[[CycleContext], Dict]] = None
    transform_output: Optional[Callable[[Any, CycleContext], Any]] = None


# ═══════════════════════════════════════════════════════════════════════════════
# CYCLE-AGENT BRIDGE
# ═══════════════════════════════════════════════════════════════════════════════

class CycleAgentBridge:
    """
    Bridges the Cycle Engine with the Agent system.
    
    Responsibilities:
    - Register agents for cycle phases
    - Route cycle data to appropriate agents
    - Track cycle progress
    - Handle maturity transitions
    
    Example:
        bridge = CycleAgentBridge()
        
        # Register handlers
        bridge.register_handler(CyclePhase.EXTRACT, alba_agent, "collect")
        bridge.register_handler(CyclePhase.ANALYZE, albi_agent, "analyze")
        bridge.register_handler(CyclePhase.SYNTHESIZE, jona_agent, "synthesize")
        
        # Process a cycle
        result = await bridge.process_cycle(context)
    """
    
    def __init__(self):
        self._handlers: Dict[CyclePhase, List[CycleHandler]] = {
            phase: [] for phase in CyclePhase
        }
        self._cycle_history: List[Dict] = []
        self._max_history = 1000
    
    def register_handler(
        self,
        phase: CyclePhase,
        agent: BaseAgent,
        action: str,
        condition: Optional[Callable[[CycleContext], bool]] = None,
        transform_input: Optional[Callable[[CycleContext], Dict]] = None,
        transform_output: Optional[Callable[[Any, CycleContext], Any]] = None
    ) -> None:
        """
        Register an agent to handle a cycle phase.
        
        Args:
            phase: Cycle phase to handle
            agent: Agent instance
            action: Action to execute on the agent
            condition: Optional condition function (returns True if should run)
            transform_input: Optional function to transform context to agent payload
            transform_output: Optional function to transform agent result
        """
        handler = CycleHandler(
            phase=phase,
            agent=agent,
            action=action,
            condition=condition,
            transform_input=transform_input,
            transform_output=transform_output
        )
        self._handlers[phase].append(handler)
        logger.info(f"Registered handler for {phase.value}: {agent.config.name}.{action}")
    
    def unregister_handler(self, phase: CyclePhase, agent: BaseAgent) -> bool:
        """Unregister an agent from a phase"""
        handlers = self._handlers[phase]
        for i, h in enumerate(handlers):
            if h.agent is agent:
                handlers.pop(i)
                return True
        return False
    
    async def process_phase(
        self,
        context: CycleContext
    ) -> CycleContext:
        """
        Process a single cycle phase.
        
        Args:
            context: Current cycle context
            
        Returns:
            Updated context after processing
        """
        handlers = self._handlers[context.phase]
        
        if not handlers:
            logger.warning(f"No handlers for phase: {context.phase.value}")
            return context
        
        for handler in handlers:
            # Check condition
            if handler.condition and not handler.condition(context):
                continue
            
            # Prepare payload
            if handler.transform_input:
                payload = handler.transform_input(context)
            else:
                payload = {
                    "action": handler.action,
                    "data": context.data,
                    "metadata": context.metadata
                }
            
            # Execute on agent
            try:
                task = Task(
                    task_id=f"{context.cycle_id}_{context.phase.value}",
                    agent_name=handler.agent.config.name,
                    payload=payload
                )
                result = await handler.agent.run_task(task)
                
                if result.success:
                    # Transform output
                    if handler.transform_output:
                        context.data = handler.transform_output(result.data, context)
                    else:
                        context.data = result.data
                else:
                    context.errors.append(f"{handler.agent.config.name}: {result.error}")
                    
            except Exception as e:
                context.errors.append(f"{handler.agent.config.name}: {str(e)}")
                logger.error(f"Handler error in {context.phase.value}: {e}")
        
        return context
    
    async def process_cycle(
        self,
        context: CycleContext,
        phases: Optional[List[CyclePhase]] = None
    ) -> CycleContext:
        """
        Process multiple cycle phases in sequence.
        
        Args:
            context: Initial cycle context
            phases: Phases to execute (default: all in order)
            
        Returns:
            Final context after all phases
        """
        if phases is None:
            phases = list(CyclePhase)
        
        logger.info(f"Processing cycle {context.cycle_id}: {len(phases)} phases")
        
        for phase in phases:
            context.phase = phase
            context = await self.process_phase(context)
            
            # Update maturity based on progress
            context = self._update_maturity(context, phase)
            
            # Check for critical errors
            if len(context.errors) > 5:
                logger.error(f"Too many errors in cycle {context.cycle_id}, stopping")
                break
        
        # Record in history
        self._cycle_history.append(context.to_dict())
        if len(self._cycle_history) > self._max_history:
            self._cycle_history = self._cycle_history[-500:]
        
        return context
    
    def _update_maturity(self, context: CycleContext, phase: CyclePhase) -> CycleContext:
        """Update maturity state based on completed phase"""
        # Simple maturity progression
        if phase in [CyclePhase.EXTRACT, CyclePhase.VALIDATE]:
            context.maturity = MaturityState.IMMATURE
        elif phase in [CyclePhase.TRANSFORM, CyclePhase.ENRICH]:
            context.maturity = MaturityState.DEVELOPING
        elif phase in [CyclePhase.ANALYZE, CyclePhase.SYNTHESIZE]:
            if not context.errors:
                context.maturity = MaturityState.MATURE
        
        return context
    
    def get_handlers(self, phase: CyclePhase) -> List[Dict]:
        """Get handlers for a phase"""
        return [
            {
                "agent": h.agent.config.name,
                "action": h.action,
                "has_condition": h.condition is not None
            }
            for h in self._handlers[phase]
        ]
    
    def get_cycle_history(self, limit: int = 100) -> List[Dict]:
        """Get recent cycle history"""
        return self._cycle_history[-limit:]


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def create_default_bridge(
    alba: Optional[ALBAAgent] = None,
    albi: Optional[ALBIAgent] = None,
    jona: Optional[JONAAgent] = None
) -> CycleAgentBridge:
    """
    Create a bridge with default core agent mappings.
    
    Args:
        alba: ALBA agent instance
        albi: ALBI agent instance
        jona: JONA agent instance
        
    Returns:
        Configured CycleAgentBridge
    """
    bridge = CycleAgentBridge()
    
    if alba:
        bridge.register_handler(CyclePhase.EXTRACT, alba, "collect")
        bridge.register_handler(CyclePhase.VALIDATE, alba, "validate")
        bridge.register_handler(CyclePhase.STORE, alba, "store")
    
    if albi:
        bridge.register_handler(CyclePhase.TRANSFORM, albi, "process")
        bridge.register_handler(CyclePhase.ENRICH, albi, "enrich")
        bridge.register_handler(CyclePhase.ANALYZE, albi, "analyze")
    
    if jona:
        bridge.register_handler(CyclePhase.SYNTHESIZE, jona, "synthesize")
        bridge.register_handler(CyclePhase.PUBLISH, jona, "publish")
    
    return bridge


def is_ml_ready(context: CycleContext) -> bool:
    """Check if data is ready for ML processing"""
    return context.maturity == MaturityState.MATURE and not context.errors


def link_agent_to_cycle(
    agent: BaseAgent,
    phase: CyclePhase,
    action: str = "execute",
    bridge: Optional[CycleAgentBridge] = None
) -> CycleAgentBridge:
    """
    Convenience function to link an agent to a cycle phase.
    
    Args:
        agent: Agent to link
        phase: Phase to handle
        action: Action to execute
        bridge: Existing bridge (creates new if None)
        
    Returns:
        The CycleAgentBridge
    """
    if bridge is None:
        bridge = CycleAgentBridge()
    
    bridge.register_handler(phase, agent, action)
    return bridge

