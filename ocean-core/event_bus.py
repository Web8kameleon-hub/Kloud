# -*- coding: utf-8 -*-
"""
🌊 KLOUD UNIFIED EVENT BUS
=============================
Deti ku derdhen të gjitha valët - Unified Event Stream.

Çdo modul, sensor, shërbim dhe klient publikon këtu.
Curiosity Ocean dëgjon çdo puls.

Event = (source, type, payload, timestamp, confidence, tags)

Author: Kloud Team
Version: 1.0.0
"""

from __future__ import annotations
import logging
import asyncio
import json
from typing import Dict, List, Any, Optional, Callable, Awaitable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from collections import deque
import uuid
import threading

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("event_bus")


# =============================================================================
# EVENT TYPES
# =============================================================================

class EventType(Enum):
    """Llojet e ngjarjeve në sistem"""
    METRIC = "metric"
    LOG = "log"
    ANOMALY = "anomaly"
    INTERACTION = "interaction"
    HEALTH = "health"
    CALL = "call"
    RESPONSE = "response"
    ERROR = "error"
    STATE_CHANGE = "state_change"
    HEARTBEAT = "heartbeat"


class EventPriority(Enum):
    """Prioriteti i ngjarjeve"""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    DEBUG = 5


# =============================================================================
# EVENT DATA CLASS
# =============================================================================

@dataclass
class Event:
    """
    Një ngjarje në detin e sinjaleve.
    
    Çdo modul publikon ngjarje në formë të unifikuar.
    """
    event_id: str = field(default_factory=lambda: f"evt_{uuid.uuid4().hex[:12]}")
    source: str = ""
    event_type: EventType = EventType.LOG
    priority: EventPriority = EventPriority.NORMAL
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    confidence: float = 1.0
    tags: List[str] = field(default_factory=list)
    correlation_id: Optional[str] = None  # Për të lidhur ngjarje të ngjashme
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.event_id,
            "source": self.source,
            "type": self.event_type.value,
            "priority": self.priority.value,
            "payload": self.payload,
            "timestamp": self.timestamp.isoformat(),
            "confidence": self.confidence,
            "tags": self.tags,
            "correlation_id": self.correlation_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Event":
        return cls(
            event_id=data.get("id", f"evt_{uuid.uuid4().hex[:12]}"),
            source=data.get("source", ""),
            event_type=EventType(data.get("type", "log")),
            priority=EventPriority(data.get("priority", 3)),
            payload=data.get("payload", {}),
            timestamp=datetime.fromisoformat(data["timestamp"]) if "timestamp" in data else datetime.now(timezone.utc),
            confidence=float(data.get("confidence", 1.0)),
            tags=data.get("tags", []),
            correlation_id=data.get("correlation_id")
        )
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, json_str: str) -> "Event":
        return cls.from_dict(json.loads(json_str))


# =============================================================================
# EVENT HANDLER TYPE
# =============================================================================

# Sync handler: def handler(event: Event) -> None
SyncHandler = Callable[[Event], None]

# Async handler: async def handler(event: Event) -> None
AsyncHandler = Callable[[Event], Awaitable[None]]

# Filter: def filter(event: Event) -> bool
EventFilter = Callable[[Event], bool]


# =============================================================================
# SUBSCRIPTION
# =============================================================================

@dataclass
class Subscription:
    """Një abonim në bus-in e ngjarjeve."""
    subscription_id: str = field(default_factory=lambda: f"sub_{uuid.uuid4().hex[:8]}")
    handler: Optional[SyncHandler] = None
    async_handler: Optional[AsyncHandler] = None
    filter: Optional[EventFilter] = None
    event_types: Optional[List[EventType]] = None
    sources: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    priority_max: EventPriority = EventPriority.DEBUG
    active: bool = True


# =============================================================================
# UNIFIED EVENT BUS
# =============================================================================

class EventBus:
    """
    🌊 UNIFIED EVENT BUS
    
    Deti ku derdhen të gjitha valët.
    Çdo modul publikon këtu, Curiosity Ocean dëgjon.
    """
    
    def __init__(self, max_history: int = 10000):
        self.subscriptions: Dict[str, Subscription] = {}
        self.history: deque[Event] = deque(maxlen=max_history)
        self.max_history = max_history
        self._lock = threading.Lock()
        self._stats = {
            "total_published": 0,
            "total_delivered": 0,
            "by_type": {},
            "by_source": {}
        }
        logger.info("🌊 Event Bus initialized")
    
    # =========================================================================
    # PUBLISH
    # =========================================================================
    
    def publish(self, event: Event) -> str:
        """
        Publiko një ngjarje në bus.
        
        Çdo abonim që përputhet do të marrë ngjarjen.
        """
        with self._lock:
            self.history.append(event)
            self._update_stats(event)
        
        # Dorëzo tek abonentët
        delivered = 0
        for sub in self.subscriptions.values():
            if sub.active and self._matches(event, sub):
                try:
                    if sub.handler:
                        sub.handler(event)
                        delivered += 1
                except Exception as e:
                    logger.error(f"Handler error for subscription {sub.subscription_id}: {e}")
        
        self._stats["total_delivered"] += delivered
        
        logger.debug(f"📨 Event {event.event_id} published to {delivered} subscribers")
        return event.event_id
    
    async def publish_async(self, event: Event) -> str:
        """
        Publiko ngjarje asinkrone.
        """
        with self._lock:
            self.history.append(event)
            self._update_stats(event)
        
        # Dorëzo tek abonentët async
        delivered = 0
        for sub in self.subscriptions.values():
            if sub.active and self._matches(event, sub):
                try:
                    if sub.async_handler:
                        await sub.async_handler(event)
                        delivered += 1
                    elif sub.handler:
                        sub.handler(event)
                        delivered += 1
                except Exception as e:
                    logger.error(f"Async handler error for subscription {sub.subscription_id}: {e}")
        
        self._stats["total_delivered"] += delivered
        return event.event_id
    
    def publish_simple(self, 
                       source: str, 
                       event_type: EventType, 
                       payload: Dict[str, Any],
                       tags: Optional[List[str]] = None) -> str:
        """
        Publiko një ngjarje të thjeshtë.
        """
        event = Event(
            source=source,
            event_type=event_type,
            payload=payload,
            tags=tags or []
        )
        return self.publish(event)
    
    def _update_stats(self, event: Event):
        """Përditëso statistikat."""
        self._stats["total_published"] += 1
        
        t = event.event_type.value
        if t not in self._stats["by_type"]:
            self._stats["by_type"][t] = 0
        self._stats["by_type"][t] += 1
        
        s = event.source
        if s not in self._stats["by_source"]:
            self._stats["by_source"][s] = 0
        self._stats["by_source"][s] += 1
    
    def _matches(self, event: Event, sub: Subscription) -> bool:
        """Kontrollo nëse ngjarja përputhet me abonimin."""
        # Kontrollo filter-in custom
        if sub.filter and not sub.filter(event):
            return False
        
        # Kontrollo llojin
        if sub.event_types and event.event_type not in sub.event_types:
            return False
        
        # Kontrollo burimin
        if sub.sources and event.source not in sub.sources:
            return False
        
        # Kontrollo tag-at
        if sub.tags and not any(t in event.tags for t in sub.tags):
            return False
        
        # Kontrollo prioritetin
        if event.priority.value > sub.priority_max.value:
            return False
        
        return True
    
    # =========================================================================
    # SUBSCRIBE
    # =========================================================================
    
    def subscribe(self,
                  handler: Optional[SyncHandler] = None,
                  async_handler: Optional[AsyncHandler] = None,
                  event_types: Optional[List[EventType]] = None,
                  sources: Optional[List[str]] = None,
                  tags: Optional[List[str]] = None,
                  filter: Optional[EventFilter] = None) -> str:
        """
        Abonohu për të marrë ngjarje.
        
        Returns:
            ID e abonimit për unsubscribe.
        """
        sub = Subscription(
            handler=handler,
            async_handler=async_handler,
            event_types=event_types,
            sources=sources,
            tags=tags,
            filter=filter
        )
        
        self.subscriptions[sub.subscription_id] = sub
        logger.info(f"✅ New subscription: {sub.subscription_id}")
        return sub.subscription_id
    
    def unsubscribe(self, subscription_id: str) -> bool:
        """Hiq abonimin."""
        if subscription_id in self.subscriptions:
            del self.subscriptions[subscription_id]
            logger.info(f"❌ Unsubscribed: {subscription_id}")
            return True
        return False
    
    def pause_subscription(self, subscription_id: str) -> bool:
        """Pauso abonimin."""
        if subscription_id in self.subscriptions:
            self.subscriptions[subscription_id].active = False
            return True
        return False
    
    def resume_subscription(self, subscription_id: str) -> bool:
        """Rifillo abonimin."""
        if subscription_id in self.subscriptions:
            self.subscriptions[subscription_id].active = True
            return True
        return False
    
    # =========================================================================
    # QUERY HISTORY
    # =========================================================================
    
    def get_history(self,
                    limit: int = 100,
                    event_type: Optional[EventType] = None,
                    source: Optional[str] = None,
                    since: Optional[datetime] = None) -> List[Event]:
        """
        Merr historinë e ngjarjeve.
        """
        result = list(self.history)
        
        if event_type:
            result = [e for e in result if e.event_type == event_type]
        
        if source:
            result = [e for e in result if source in e.source]
        
        if since:
            result = [e for e in result if e.timestamp >= since]
        
        # Kthe të fundit (më të rejat)
        return result[-limit:]
    
    def get_last(self, count: int = 1) -> List[Event]:
        """Merr ngjarjet e fundit."""
        return list(self.history)[-count:]
    
    def get_by_correlation(self, correlation_id: str) -> List[Event]:
        """Merr të gjitha ngjarjet me të njëjtin correlation_id."""
        return [e for e in self.history if e.correlation_id == correlation_id]
    
    def search(self, query: str) -> List[Event]:
        """Kërko në payload të ngjarjeve."""
        results = []
        query_lower = query.lower()
        
        for event in self.history:
            payload_str = json.dumps(event.payload).lower()
            if query_lower in payload_str or query_lower in event.source.lower():
                results.append(event)
        
        return results
    
    # =========================================================================
    # STATISTICS
    # =========================================================================
    
    def get_stats(self) -> Dict[str, Any]:
        """Merr statistikat e bus-it."""
        return {
            **self._stats,
            "history_size": len(self.history),
            "max_history": self.max_history,
            "active_subscriptions": len([s for s in self.subscriptions.values() if s.active]),
            "total_subscriptions": len(self.subscriptions)
        }
    
    def clear_history(self):
        """Pastro historinë."""
        self.history.clear()
        self._stats = {
            "total_published": 0,
            "total_delivered": 0,
            "by_type": {},
            "by_source": {}
        }
    
    # =========================================================================
    # CONVENIENCE METHODS
    # =========================================================================
    
    def emit_metric(self, source: str, name: str, value: float, tags: Optional[List[str]] = None) -> str:
        """Publiko një metrikë."""
        return self.publish_simple(
            source=source,
            event_type=EventType.METRIC,
            payload={"name": name, "value": value},
            tags=tags
        )
    
    def emit_log(self, source: str, message: str, level: str = "info") -> str:
        """Publiko një log."""
        return self.publish_simple(
            source=source,
            event_type=EventType.LOG,
            payload={"message": message, "level": level}
        )
    
    def emit_error(self, source: str, error: str, details: Optional[Dict] = None) -> str:
        """Publiko një gabim."""
        return self.publish(Event(
            source=source,
            event_type=EventType.ERROR,
            priority=EventPriority.HIGH,
            payload={"error": error, "details": details or {}}
        ))
    
    def emit_anomaly(self, source: str, description: str, severity: float) -> str:
        """Publiko një anomali."""
        priority = EventPriority.CRITICAL if severity > 0.8 else EventPriority.HIGH if severity > 0.5 else EventPriority.NORMAL
        return self.publish(Event(
            source=source,
            event_type=EventType.ANOMALY,
            priority=priority,
            payload={"description": description, "severity": severity},
            tags=["anomaly"]
        ))
    
    def emit_heartbeat(self, source: str, status: str = "alive") -> str:
        """Publiko një heartbeat."""
        return self.publish(Event(
            source=source,
            event_type=EventType.HEARTBEAT,
            priority=EventPriority.DEBUG,
            payload={"status": status}
        ))


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

_bus_instance: Optional[EventBus] = None

def get_event_bus() -> EventBus:
    """Get or create the Event Bus singleton."""
    global _bus_instance
    if _bus_instance is None:
        _bus_instance = EventBus()
    return _bus_instance


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    bus = get_event_bus()
    
    # Test handler
    def my_handler(event: Event):
        print(f"  Received: {event.event_type.value} from {event.source}")
    
    # Subscribe
    sub_id = bus.subscribe(
        handler=my_handler,
        event_types=[EventType.METRIC, EventType.ANOMALY]
    )
    print(f"Subscribed with ID: {sub_id}")
    
    # Publish some events
    print("\nPublishing events...")
    bus.emit_metric("sensor-01", "temperature", 22.5)
    bus.emit_metric("sensor-02", "humidity", 65.0)
    bus.emit_anomaly("sensor-01", "Temperature spike detected", 0.85)
    bus.emit_log("system", "Everything is running fine")  # Won't trigger handler
    
    # Stats
    print(f"\nStats: {bus.get_stats()}")
    
    # History
    print(f"\nLast 3 events:")
    for e in bus.get_last(3):
        print(f"  - {e.event_type.value}: {e.payload}")

