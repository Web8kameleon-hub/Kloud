"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                   KLOUD AGENTS - TELEMETRY                                ║
║             Logging, Metrics, and Observability for Agents                   ║
╚══════════════════════════════════════════════════════════════════════════════╝

Unified telemetry system for agent operations:
- Structured logging
- Metrics collection
- Event tracking
- Performance monitoring

Usage:
    from agents.telemetry import TelemetryService, log_task
    
    telemetry = TelemetryService()
    telemetry.log_event("task_started", {"agent": "alba", "task_id": "123"})
"""

import asyncio
import logging
import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict
import threading


logger = logging.getLogger("kloud.agents.telemetry")


# ═══════════════════════════════════════════════════════════════════════════════
# TELEMETRY TYPES
# ═══════════════════════════════════════════════════════════════════════════════

class EventType(str, Enum):
    """Types of telemetry events"""
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    AGENT_INITIALIZED = "agent_initialized"
    AGENT_SHUTDOWN = "agent_shutdown"
    AGENT_ERROR = "agent_error"
    POOL_SCALED = "pool_scaled"
    HEALTH_CHECK = "health_check"
    WORKFLOW_STARTED = "workflow_started"
    WORKFLOW_COMPLETED = "workflow_completed"
    CUSTOM = "custom"


class MetricType(str, Enum):
    """Types of metrics"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


@dataclass
class TelemetryEvent:
    """A single telemetry event"""
    event_type: EventType
    timestamp: datetime
    agent_name: Optional[str] = None
    task_id: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    duration_ms: Optional[float] = None
    success: Optional[bool] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "agent_name": self.agent_name,
            "task_id": self.task_id,
            "data": self.data,
            "duration_ms": self.duration_ms,
            "success": self.success,
            "error": self.error
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict())


@dataclass
class Metric:
    """A single metric measurement"""
    name: str
    metric_type: MetricType
    value: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    labels: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "type": self.metric_type.value,
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
            "labels": self.labels
        }


# ═══════════════════════════════════════════════════════════════════════════════
# METRICS COLLECTOR
# ═══════════════════════════════════════════════════════════════════════════════

class MetricsCollector:
    """
    Collects and aggregates metrics.
    
    Supports:
    - Counters: Incrementing values
    - Gauges: Point-in-time values
    - Histograms: Distribution of values
    - Timers: Duration measurements
    """
    
    def __init__(self):
        self._counters: Dict[str, float] = defaultdict(float)
        self._gauges: Dict[str, float] = {}
        self._histograms: Dict[str, List[float]] = defaultdict(list)
        self._timers: Dict[str, List[float]] = defaultdict(list)
        self._lock = threading.Lock()
        self._max_histogram_size = 10000
    
    def increment(self, name: str, value: float = 1.0, labels: Optional[Dict] = None) -> None:
        """Increment a counter"""
        key = self._make_key(name, labels)
        with self._lock:
            self._counters[key] += value
    
    def gauge(self, name: str, value: float, labels: Optional[Dict] = None) -> None:
        """Set a gauge value"""
        key = self._make_key(name, labels)
        with self._lock:
            self._gauges[key] = value
    
    def histogram(self, name: str, value: float, labels: Optional[Dict] = None) -> None:
        """Record a histogram value"""
        key = self._make_key(name, labels)
        with self._lock:
            hist = self._histograms[key]
            hist.append(value)
            if len(hist) > self._max_histogram_size:
                self._histograms[key] = hist[-5000:]
    
    def timer(self, name: str, duration_ms: float, labels: Optional[Dict] = None) -> None:
        """Record a timer value"""
        key = self._make_key(name, labels)
        with self._lock:
            timers = self._timers[key]
            timers.append(duration_ms)
            if len(timers) > self._max_histogram_size:
                self._timers[key] = timers[-5000:]
    
    def _make_key(self, name: str, labels: Optional[Dict]) -> str:
        """Create a unique key for a metric"""
        if not labels:
            return name
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"
    
    def get_counter(self, name: str, labels: Optional[Dict] = None) -> float:
        """Get current counter value"""
        key = self._make_key(name, labels)
        return self._counters.get(key, 0.0)
    
    def get_gauge(self, name: str, labels: Optional[Dict] = None) -> Optional[float]:
        """Get current gauge value"""
        key = self._make_key(name, labels)
        return self._gauges.get(key)
    
    def get_histogram_stats(self, name: str, labels: Optional[Dict] = None) -> Dict:
        """Get histogram statistics"""
        key = self._make_key(name, labels)
        values = self._histograms.get(key, [])
        
        if not values:
            return {"count": 0}
        
        sorted_values = sorted(values)
        count = len(sorted_values)
        
        return {
            "count": count,
            "min": sorted_values[0],
            "max": sorted_values[-1],
            "avg": sum(sorted_values) / count,
            "p50": sorted_values[int(count * 0.50)],
            "p90": sorted_values[int(count * 0.90)],
            "p99": sorted_values[int(count * 0.99)] if count >= 100 else sorted_values[-1]
        }
    
    def get_timer_stats(self, name: str, labels: Optional[Dict] = None) -> Dict:
        """Get timer statistics"""
        key = self._make_key(name, labels)
        values = self._timers.get(key, [])
        
        if not values:
            return {"count": 0}
        
        sorted_values = sorted(values)
        count = len(sorted_values)
        
        return {
            "count": count,
            "min_ms": sorted_values[0],
            "max_ms": sorted_values[-1],
            "avg_ms": sum(sorted_values) / count,
            "p50_ms": sorted_values[int(count * 0.50)],
            "p90_ms": sorted_values[int(count * 0.90)],
            "p99_ms": sorted_values[int(count * 0.99)] if count >= 100 else sorted_values[-1]
        }
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all metrics"""
        with self._lock:
            return {
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
                "histograms": {k: self.get_histogram_stats(k) for k in self._histograms},
                "timers": {k: self.get_timer_stats(k) for k in self._timers}
            }
    
    def reset(self) -> None:
        """Reset all metrics"""
        with self._lock:
            self._counters.clear()
            self._gauges.clear()
            self._histograms.clear()
            self._timers.clear()


# ═══════════════════════════════════════════════════════════════════════════════
# TELEMETRY SERVICE
# ═══════════════════════════════════════════════════════════════════════════════

class TelemetryService:
    """
    Centralized telemetry service for agent operations.
    
    Features:
    - Event logging
    - Metrics collection
    - Event subscriptions
    - Export to various backends
    
    Example:
        telemetry = TelemetryService()
        
        # Log events
        telemetry.log_event(EventType.TASK_STARTED, agent_name="alba", task_id="123")
        
        # Record metrics
        telemetry.metrics.increment("tasks.total", labels={"agent": "alba"})
        telemetry.metrics.timer("task.duration", 150.5, labels={"agent": "alba"})
        
        # Subscribe to events
        telemetry.subscribe(EventType.TASK_FAILED, lambda e: print(f"Failed: {e.task_id}"))
    """
    
    def __init__(self, max_events: int = 10000):
        self.metrics = MetricsCollector()
        self._events: List[TelemetryEvent] = []
        self._max_events = max_events
        self._subscribers: Dict[EventType, List[Callable]] = defaultdict(list)
        self._lock = threading.Lock()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # EVENT LOGGING
    # ═══════════════════════════════════════════════════════════════════════════
    
    def log_event(
        self,
        event_type: EventType,
        agent_name: Optional[str] = None,
        task_id: Optional[str] = None,
        data: Optional[Dict] = None,
        duration_ms: Optional[float] = None,
        success: Optional[bool] = None,
        error: Optional[str] = None
    ) -> TelemetryEvent:
        """
        Log a telemetry event.
        
        Args:
            event_type: Type of event
            agent_name: Agent that generated the event
            task_id: Related task ID
            data: Additional event data
            duration_ms: Duration if applicable
            success: Success status if applicable
            error: Error message if failed
            
        Returns:
            The created event
        """
        event = TelemetryEvent(
            event_type=event_type,
            timestamp=datetime.now(timezone.utc),
            agent_name=agent_name,
            task_id=task_id,
            data=data or {},
            duration_ms=duration_ms,
            success=success,
            error=error
        )
        
        with self._lock:
            self._events.append(event)
            if len(self._events) > self._max_events:
                self._events = self._events[-5000:]
        
        # Notify subscribers
        self._notify(event)
        
        # Log to standard logger
        log_level = logging.ERROR if event_type == EventType.TASK_FAILED else logging.INFO
        logger.log(log_level, event.to_json())
        
        # Update metrics
        self._update_metrics(event)
        
        return event
    
    def _update_metrics(self, event: TelemetryEvent) -> None:
        """Update metrics based on event"""
        labels = {"agent": event.agent_name or "unknown"}
        
        if event.event_type == EventType.TASK_STARTED:
            self.metrics.increment("tasks.started", labels=labels)
        
        elif event.event_type == EventType.TASK_COMPLETED:
            self.metrics.increment("tasks.completed", labels=labels)
            if event.duration_ms:
                self.metrics.timer("task.duration", event.duration_ms, labels=labels)
        
        elif event.event_type == EventType.TASK_FAILED:
            self.metrics.increment("tasks.failed", labels=labels)
        
        elif event.event_type == EventType.AGENT_ERROR:
            self.metrics.increment("agent.errors", labels=labels)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # CONVENIENCE METHODS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def task_started(self, task_id: str, agent_name: str, action: str) -> None:
        """Log task started event"""
        self.log_event(
            EventType.TASK_STARTED,
            agent_name=agent_name,
            task_id=task_id,
            data={"action": action}
        )
    
    def task_completed(
        self,
        task_id: str,
        agent_name: str,
        duration_ms: float,
        result: Optional[Dict] = None
    ) -> None:
        """Log task completed event"""
        self.log_event(
            EventType.TASK_COMPLETED,
            agent_name=agent_name,
            task_id=task_id,
            duration_ms=duration_ms,
            success=True,
            data={"result_preview": str(result)[:200] if result else None}
        )
    
    def task_failed(
        self,
        task_id: str,
        agent_name: str,
        error: str,
        duration_ms: Optional[float] = None
    ) -> None:
        """Log task failed event"""
        self.log_event(
            EventType.TASK_FAILED,
            agent_name=agent_name,
            task_id=task_id,
            duration_ms=duration_ms,
            success=False,
            error=error
        )
    
    def agent_initialized(self, agent_name: str) -> None:
        """Log agent initialized event"""
        self.log_event(EventType.AGENT_INITIALIZED, agent_name=agent_name)
    
    def agent_shutdown(self, agent_name: str) -> None:
        """Log agent shutdown event"""
        self.log_event(EventType.AGENT_SHUTDOWN, agent_name=agent_name)
    
    def agent_error(self, agent_name: str, error: str) -> None:
        """Log agent error event"""
        self.log_event(EventType.AGENT_ERROR, agent_name=agent_name, error=error)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # SUBSCRIPTIONS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def subscribe(
        self,
        event_type: EventType,
        callback: Callable[[TelemetryEvent], None]
    ) -> None:
        """Subscribe to events of a specific type"""
        self._subscribers[event_type].append(callback)
    
    def unsubscribe(
        self,
        event_type: EventType,
        callback: Callable[[TelemetryEvent], None]
    ) -> None:
        """Unsubscribe from events"""
        if callback in self._subscribers[event_type]:
            self._subscribers[event_type].remove(callback)
    
    def _notify(self, event: TelemetryEvent) -> None:
        """Notify subscribers of an event"""
        for callback in self._subscribers[event.event_type]:
            try:
                callback(event)
            except Exception as e:
                logger.error(f"Error in telemetry subscriber: {e}")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # QUERIES
    # ═══════════════════════════════════════════════════════════════════════════
    
    def get_events(
        self,
        event_type: Optional[EventType] = None,
        agent_name: Optional[str] = None,
        limit: int = 100
    ) -> List[TelemetryEvent]:
        """
        Query recent events.
        
        Args:
            event_type: Filter by event type
            agent_name: Filter by agent name
            limit: Maximum events to return
            
        Returns:
            List of matching events
        """
        with self._lock:
            events = list(self._events)
        
        # Filter
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        if agent_name:
            events = [e for e in events if e.agent_name == agent_name]
        
        # Return most recent
        return events[-limit:]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get telemetry summary"""
        with self._lock:
            events = list(self._events)
        
        # Count by type
        by_type = defaultdict(int)
        for e in events:
            by_type[e.event_type.value] += 1
        
        # Count by agent
        by_agent = defaultdict(int)
        for e in events:
            if e.agent_name:
                by_agent[e.agent_name] += 1
        
        # Success rate
        completed = [e for e in events if e.event_type == EventType.TASK_COMPLETED]
        failed = [e for e in events if e.event_type == EventType.TASK_FAILED]
        total_tasks = len(completed) + len(failed)
        success_rate = len(completed) / total_tasks if total_tasks > 0 else 1.0
        
        return {
            "total_events": len(events),
            "events_by_type": dict(by_type),
            "events_by_agent": dict(by_agent),
            "tasks_completed": len(completed),
            "tasks_failed": len(failed),
            "success_rate": round(success_rate, 4),
            "metrics": self.metrics.get_all_metrics(),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def export_events(self, format: str = "json") -> str:
        """Export events to string"""
        with self._lock:
            events = [e.to_dict() for e in self._events]
        
        if format == "json":
            return json.dumps(events, indent=2)
        elif format == "jsonl":
            return "\n".join(json.dumps(e) for e in events)
        else:
            raise ValueError(f"Unknown format: {format}")


# ═══════════════════════════════════════════════════════════════════════════════
# GLOBAL TELEMETRY INSTANCE
# ═══════════════════════════════════════════════════════════════════════════════

_global_telemetry: Optional[TelemetryService] = None


def get_telemetry() -> TelemetryService:
    """Get global telemetry service"""
    global _global_telemetry
    if _global_telemetry is None:
        _global_telemetry = TelemetryService()
    return _global_telemetry


# Convenience functions
def log_task_started(task_id: str, agent_name: str, action: str) -> None:
    """Log task started to global telemetry"""
    get_telemetry().task_started(task_id, agent_name, action)


def log_task_completed(
    task_id: str,
    agent_name: str,
    duration_ms: float,
    result: Optional[Dict] = None
) -> None:
    """Log task completed to global telemetry"""
    get_telemetry().task_completed(task_id, agent_name, duration_ms, result)


def log_task_failed(task_id: str, agent_name: str, error: str) -> None:
    """Log task failed to global telemetry"""
    get_telemetry().task_failed(task_id, agent_name, error)

