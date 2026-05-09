"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    KLOUD AGENTS - AGENT REGISTRY                          ║
║              Service Discovery and Registration for Agents                   ║
╚══════════════════════════════════════════════════════════════════════════════╝

AgentRegistry provides:
- Agent registration and discovery
- Capability-based lookups
- Service health tracking
- Event broadcasting

Usage:
    from agents.registry import AgentRegistry
    
    registry = AgentRegistry()
    registry.register(my_agent)
    agents = registry.find_by_capability(AgentCapability.WEB_SCRAPING)
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Set, Callable, Type
from dataclasses import dataclass, field
from enum import Enum
import uuid

from .base import (
    BaseAgent, AgentConfig, AgentType, AgentStatus,
    AgentCapability, Task, TaskResult
)


logger = logging.getLogger("kloud.agents.registry")


# ═══════════════════════════════════════════════════════════════════════════════
# REGISTRY EVENTS
# ═══════════════════════════════════════════════════════════════════════════════

class RegistryEvent(str, Enum):
    """Events that can be emitted by the registry"""
    AGENT_REGISTERED = "agent_registered"
    AGENT_UNREGISTERED = "agent_unregistered"
    AGENT_STATUS_CHANGED = "agent_status_changed"
    AGENT_HEALTH_CHANGED = "agent_health_changed"


@dataclass
class RegistryEntry:
    """Entry for a registered agent"""
    id: str
    agent: BaseAgent
    config: AgentConfig
    registered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_health_check: Optional[datetime] = None
    is_healthy: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.config.name,
            "type": self.config.agent_type.value,
            "version": self.config.version,
            "status": self.agent.status.value,
            "capabilities": [c.value for c in self.config.capabilities],
            "is_healthy": self.is_healthy,
            "registered_at": self.registered_at.isoformat(),
            "last_health_check": self.last_health_check.isoformat() if self.last_health_check else None,
            "metadata": self.metadata
        }


# ═══════════════════════════════════════════════════════════════════════════════
# AGENT REGISTRY
# ═══════════════════════════════════════════════════════════════════════════════

class AgentRegistry:
    """
    Central registry for agent discovery and management.
    
    Features:
    - Register/unregister agents
    - Find agents by name, type, or capability
    - Health monitoring
    - Event subscriptions
    
    Example:
        registry = AgentRegistry()
        
        # Register an agent
        agent = WebScraperAgent()
        await agent.initialize()
        registry.register(agent)
        
        # Find by capability
        scrapers = registry.find_by_capability(AgentCapability.WEB_SCRAPING)
        
        # Find by type
        collectors = registry.find_by_type(AgentType.COLLECTOR)
        
        # Subscribe to events
        registry.subscribe(RegistryEvent.AGENT_REGISTERED, my_callback)
    """
    
    def __init__(self):
        # Registry storage: id -> RegistryEntry
        self._entries: Dict[str, RegistryEntry] = {}
        
        # Indexes for fast lookup
        self._by_name: Dict[str, Set[str]] = {}  # name -> set of ids
        self._by_type: Dict[AgentType, Set[str]] = {}  # type -> set of ids
        self._by_capability: Dict[AgentCapability, Set[str]] = {}  # cap -> set of ids
        
        # Event subscribers
        self._subscribers: Dict[RegistryEvent, List[Callable]] = {
            event: [] for event in RegistryEvent
        }
        
        # Lock for thread safety
        self._lock = asyncio.Lock()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # REGISTRATION
    # ═══════════════════════════════════════════════════════════════════════════
    
    def register(
        self,
        agent: BaseAgent,
        agent_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Register an agent with the registry.
        
        Args:
            agent: Agent instance to register
            agent_id: Optional custom ID (auto-generated if not provided)
            metadata: Optional additional metadata
            
        Returns:
            The registered agent's ID
        """
        config = agent.config
        
        # Generate ID if not provided
        if agent_id is None:
            agent_id = f"{config.name}-{uuid.uuid4().hex[:8]}"
        
        # Create entry
        entry = RegistryEntry(
            id=agent_id,
            agent=agent,
            config=config,
            metadata=metadata or {}
        )
        
        # Store entry
        self._entries[agent_id] = entry
        
        # Update indexes
        if config.name not in self._by_name:
            self._by_name[config.name] = set()
        self._by_name[config.name].add(agent_id)
        
        if config.agent_type not in self._by_type:
            self._by_type[config.agent_type] = set()
        self._by_type[config.agent_type].add(agent_id)
        
        for capability in config.capabilities:
            if capability not in self._by_capability:
                self._by_capability[capability] = set()
            self._by_capability[capability].add(agent_id)
        
        # Emit event
        self._emit(RegistryEvent.AGENT_REGISTERED, {
            "agent_id": agent_id,
            "name": config.name,
            "type": config.agent_type.value
        })
        
        logger.info(f"Registered agent: {agent_id} ({config.name})")
        return agent_id
    
    def unregister(self, agent_id: str) -> bool:
        """
        Unregister an agent from the registry.
        
        Args:
            agent_id: ID of the agent to unregister
            
        Returns:
            True if agent was found and removed
        """
        if agent_id not in self._entries:
            return False
        
        entry = self._entries[agent_id]
        config = entry.config
        
        # Remove from indexes
        if config.name in self._by_name:
            self._by_name[config.name].discard(agent_id)
            if not self._by_name[config.name]:
                del self._by_name[config.name]
        
        if config.agent_type in self._by_type:
            self._by_type[config.agent_type].discard(agent_id)
            if not self._by_type[config.agent_type]:
                del self._by_type[config.agent_type]
        
        for capability in config.capabilities:
            if capability in self._by_capability:
                self._by_capability[capability].discard(agent_id)
                if not self._by_capability[capability]:
                    del self._by_capability[capability]
        
        # Remove entry
        del self._entries[agent_id]
        
        # Emit event
        self._emit(RegistryEvent.AGENT_UNREGISTERED, {
            "agent_id": agent_id,
            "name": config.name
        })
        
        logger.info(f"Unregistered agent: {agent_id}")
        return True
    
    # ═══════════════════════════════════════════════════════════════════════════
    # LOOKUP
    # ═══════════════════════════════════════════════════════════════════════════
    
    def get(self, agent_id: str) -> Optional[BaseAgent]:
        """Get an agent by ID"""
        entry = self._entries.get(agent_id)
        return entry.agent if entry else None
    
    def get_entry(self, agent_id: str) -> Optional[RegistryEntry]:
        """Get a registry entry by ID"""
        return self._entries.get(agent_id)
    
    def find_by_name(self, name: str) -> List[BaseAgent]:
        """Find all agents with a given name"""
        ids = self._by_name.get(name, set())
        return [self._entries[id].agent for id in ids if id in self._entries]
    
    def find_by_type(self, agent_type: AgentType) -> List[BaseAgent]:
        """Find all agents of a given type"""
        ids = self._by_type.get(agent_type, set())
        return [self._entries[id].agent for id in ids if id in self._entries]
    
    def find_by_capability(self, capability: AgentCapability) -> List[BaseAgent]:
        """Find all agents with a given capability"""
        ids = self._by_capability.get(capability, set())
        return [self._entries[id].agent for id in ids if id in self._entries]
    
    def find_by_capabilities(
        self,
        capabilities: List[AgentCapability],
        match_all: bool = True
    ) -> List[BaseAgent]:
        """
        Find agents with specified capabilities.
        
        Args:
            capabilities: List of required capabilities
            match_all: If True, agent must have ALL capabilities;
                      if False, agent must have at least ONE
        
        Returns:
            List of matching agents
        """
        if not capabilities:
            return list(self.all_agents())
        
        if match_all:
            # Intersection of all capability sets
            id_sets = [self._by_capability.get(cap, set()) for cap in capabilities]
            if not id_sets:
                return []
            matching_ids = set.intersection(*id_sets)
        else:
            # Union of all capability sets
            matching_ids = set()
            for cap in capabilities:
                matching_ids.update(self._by_capability.get(cap, set()))
        
        return [self._entries[id].agent for id in matching_ids if id in self._entries]
    
    def find_healthy(self, name: Optional[str] = None) -> List[BaseAgent]:
        """Find all healthy agents, optionally filtered by name"""
        agents = []
        for entry in self._entries.values():
            if entry.is_healthy:
                if name is None or entry.config.name == name:
                    agents.append(entry.agent)
        return agents
    
    def all_agents(self) -> List[BaseAgent]:
        """Get all registered agents"""
        return [entry.agent for entry in self._entries.values()]
    
    def all_entries(self) -> List[RegistryEntry]:
        """Get all registry entries"""
        return list(self._entries.values())
    
    # ═══════════════════════════════════════════════════════════════════════════
    # HEALTH MONITORING
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def check_health(self, agent_id: str) -> bool:
        """
        Check health of a specific agent.
        
        Args:
            agent_id: ID of agent to check
            
        Returns:
            True if healthy
        """
        entry = self._entries.get(agent_id)
        if not entry:
            return False
        
        try:
            is_healthy = await entry.agent.health_check()
        except Exception:
            is_healthy = False
        
        # Update entry
        old_health = entry.is_healthy
        entry.is_healthy = is_healthy
        entry.last_health_check = datetime.now(timezone.utc)
        
        # Emit event if changed
        if old_health != is_healthy:
            self._emit(RegistryEvent.AGENT_HEALTH_CHANGED, {
                "agent_id": agent_id,
                "is_healthy": is_healthy
            })
        
        return is_healthy
    
    async def check_all_health(self) -> Dict[str, bool]:
        """
        Check health of all registered agents.
        
        Returns:
            Dict of agent_id -> is_healthy
        """
        results = {}
        
        tasks = [
            (agent_id, self.check_health(agent_id))
            for agent_id in self._entries.keys()
        ]
        
        for agent_id, coro in tasks:
            results[agent_id] = await coro
        
        return results
    
    def update_health(self, agent_id: str, is_healthy: bool) -> None:
        """
        Manually update an agent's health status.
        
        Args:
            agent_id: Agent ID
            is_healthy: New health status
        """
        entry = self._entries.get(agent_id)
        if entry:
            old_health = entry.is_healthy
            entry.is_healthy = is_healthy
            entry.last_health_check = datetime.now(timezone.utc)
            
            if old_health != is_healthy:
                self._emit(RegistryEvent.AGENT_HEALTH_CHANGED, {
                    "agent_id": agent_id,
                    "is_healthy": is_healthy
                })
    
    # ═══════════════════════════════════════════════════════════════════════════
    # EVENTS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def subscribe(
        self,
        event: RegistryEvent,
        callback: Callable[[Dict[str, Any]], None]
    ) -> None:
        """
        Subscribe to registry events.
        
        Args:
            event: Event type to subscribe to
            callback: Callback function (receives event data dict)
        """
        self._subscribers[event].append(callback)
    
    def unsubscribe(
        self,
        event: RegistryEvent,
        callback: Callable[[Dict[str, Any]], None]
    ) -> None:
        """Unsubscribe from registry events"""
        if callback in self._subscribers[event]:
            self._subscribers[event].remove(callback)
    
    def _emit(self, event: RegistryEvent, data: Dict[str, Any]) -> None:
        """Emit an event to all subscribers"""
        data["event"] = event.value
        data["timestamp"] = datetime.now(timezone.utc).isoformat()
        
        for callback in self._subscribers[event]:
            try:
                callback(data)
            except Exception as e:
                logger.error(f"Error in event callback: {e}")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # STATUS & STATS
    # ═══════════════════════════════════════════════════════════════════════════
    
    @property
    def count(self) -> int:
        """Total number of registered agents"""
        return len(self._entries)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        by_type = {}
        for agent_type, ids in self._by_type.items():
            by_type[agent_type.value] = len(ids)
        
        by_capability = {}
        for capability, ids in self._by_capability.items():
            by_capability[capability.value] = len(ids)
        
        healthy_count = sum(1 for e in self._entries.values() if e.is_healthy)
        
        return {
            "total_agents": len(self._entries),
            "healthy_agents": healthy_count,
            "unhealthy_agents": len(self._entries) - healthy_count,
            "unique_names": len(self._by_name),
            "by_type": by_type,
            "by_capability": by_capability
        }
    
    def list_agents(self) -> List[Dict]:
        """List all agents as dictionaries"""
        return [entry.to_dict() for entry in self._entries.values()]


# ═══════════════════════════════════════════════════════════════════════════════
# GLOBAL REGISTRY INSTANCE
# ═══════════════════════════════════════════════════════════════════════════════

_global_registry: Optional[AgentRegistry] = None


def get_registry() -> AgentRegistry:
    """Get the global registry instance"""
    global _global_registry
    if _global_registry is None:
        _global_registry = AgentRegistry()
    return _global_registry


def register_agent(
    agent: BaseAgent,
    agent_id: Optional[str] = None
) -> str:
    """Convenience function to register with global registry"""
    return get_registry().register(agent, agent_id)


def find_agents(
    capability: Optional[AgentCapability] = None,
    agent_type: Optional[AgentType] = None,
    name: Optional[str] = None
) -> List[BaseAgent]:
    """Convenience function to find agents in global registry"""
    registry = get_registry()
    
    if capability:
        return registry.find_by_capability(capability)
    elif agent_type:
        return registry.find_by_type(agent_type)
    elif name:
        return registry.find_by_name(name)
    else:
        return registry.all_agents()

