# ============================================================================
# FALLBACKS - Graceful Degradation When Sources Are Unavailable
# ============================================================================
# Handles failures gracefully with fallback responses
# Ensures system never fails completely - always provides value
# ============================================================================

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS AND DATA CLASSES
# ============================================================================

class FallbackLevel(Enum):
    """Levels of fallback"""
    NONE = "none"               # No fallback needed
    PARTIAL = "partial"         # Some sources failed
    DEGRADED = "degraded"       # Most sources failed
    MINIMAL = "minimal"         # Almost all failed
    OFFLINE = "offline"         # Everything failed


class FallbackAction(Enum):
    """Actions to take on fallback"""
    RETRY = "retry"             # Retry the failed operation
    CACHE = "cache"             # Use cached data
    ALTERNATE = "alternate"     # Use alternate source
    SIMPLIFY = "simplify"       # Simplify the request
    DEFER = "defer"             # Defer for later
    FAIL = "fail"               # Accept failure gracefully


@dataclass
class FallbackResponse:
    """
    Response when fallback is needed
    
    Provides:
    - Alternative answer (if possible)
    - Explanation of what happened
    - Suggestions for user
    - Recovery options
    """
    level: FallbackLevel
    action_taken: FallbackAction
    original_query: str
    fallback_answer: str
    explanation: str
    suggestions: List[str]
    failed_sources: List[str]
    working_sources: List[str]
    recovered_data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "level": self.level.value,
            "action_taken": self.action_taken.value,
            "original_query": self.original_query,
            "fallback_answer": self.fallback_answer,
            "explanation": self.explanation,
            "suggestions": self.suggestions,
            "failed_sources": self.failed_sources,
            "working_sources": self.working_sources,
            "recovered_data_keys": list(self.recovered_data.keys()),
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class SourceHealth:
    """Health status of a source"""
    source_id: str
    is_healthy: bool
    last_success: Optional[datetime]
    last_failure: Optional[datetime]
    failure_count: int = 0
    success_count: int = 0
    avg_latency_ms: float = 0.0
    circuit_open: bool = False  # Circuit breaker pattern


# ============================================================================
# FALLBACK RESPONSES TEMPLATES
# ============================================================================

FALLBACK_TEMPLATES = {
    FallbackLevel.PARTIAL: {
        "answer": "I found partial information from {working_count} out of {total_count} sources.",
        "explanation": "Some data sources were temporarily unavailable. The answer may be incomplete.",
        "suggestions": [
            "Try again in a few minutes for complete results",
            "Narrow your search to specific regions that are working",
            "Use the /status endpoint to check source availability"
        ]
    },
    FallbackLevel.DEGRADED: {
        "answer": "Limited information available from {working_count} sources.",
        "explanation": "Most data sources are currently experiencing issues. Results are limited.",
        "suggestions": [
            "Try a simpler query",
            "Check back later when more sources are available",
            "Contact support if this persists"
        ]
    },
    FallbackLevel.MINIMAL: {
        "answer": "Only basic information available at this time.",
        "explanation": "Most systems are currently unavailable. Only cached data is accessible.",
        "suggestions": [
            "Please try again later",
            "Check the /health endpoint for system status",
            "This may be a temporary outage"
        ]
    },
    FallbackLevel.OFFLINE: {
        "answer": "Unable to retrieve information at this time.",
        "explanation": "All data sources are currently offline. The system is operating in maintenance mode.",
        "suggestions": [
            "The system is undergoing maintenance",
            "Please check back in 30 minutes",
            "Contact support@kloud.com for urgent matters"
        ]
    }
}


# ============================================================================
# CACHED FALLBACK DATA
# ============================================================================

# Basic fallback data for common queries when all else fails
CACHED_FALLBACKS = {
    "countries_count": "Kloud covers 155+ countries with 4053+ data sources",
    "api_count": "988 API endpoints available across all regions",
    "regions": ["Europe", "Asia-China", "India-South Asia", "Americas", "Africa-Middle East", 
                "Asia-Oceania", "Caribbean-Central America", "Pacific Islands",
                "Central Asia-Caucasus", "Eastern Europe-Balkans"],
    "categories": ["Government", "University", "Hospital", "Bank", "Statistics",
                  "Technology", "News", "Culture", "Sport", "Entertainment",
                  "Tourism", "Transport", "Energy", "Telecom", "Research",
                  "Industry", "Environmental", "Agriculture"],
    "services": {
        "hq": {"port": 8000, "status": "Primary API Gateway"},
        "alba": {"port": 5555, "status": "Data Streaming"},
        "albi": {"port": 6680, "status": "Analytics Engine"},
        "jona": {"port": 7777, "status": "Supervision Layer"}
    }
}


# ============================================================================
# FALLBACK MANAGER CLASS
# ============================================================================

class FallbackManager:
    """
    Manages fallback strategies for the Internal AGI Engine
    
    Implements:
    - Circuit breaker pattern for sources
    - Graceful degradation
    - Cached fallback responses
    - Recovery suggestions
    
    Philosophy: Never fail completely. Always provide some value.
    """
    
    def __init__(self):
        self._source_health: Dict[str, SourceHealth] = {}
        self._fallback_cache: Dict[str, Any] = CACHED_FALLBACKS.copy()
        self._circuit_threshold = 5  # Failures before opening circuit
        self._circuit_timeout = timedelta(minutes=5)  # Time before retry
    
    def record_success(self, source_id: str, latency_ms: float = 0):
        """Record successful source access"""
        if source_id not in self._source_health:
            self._source_health[source_id] = SourceHealth(
                source_id=source_id,
                is_healthy=True,
                last_success=datetime.now(),
                last_failure=None
            )
        
        health = self._source_health[source_id]
        health.last_success = datetime.now()
        health.success_count += 1
        health.is_healthy = True
        health.circuit_open = False
        
        # Update average latency
        if health.avg_latency_ms == 0:
            health.avg_latency_ms = latency_ms
        else:
            health.avg_latency_ms = (health.avg_latency_ms * 0.9) + (latency_ms * 0.1)
    
    def record_failure(self, source_id: str, error: Optional[str] = None):
        """Record source failure"""
        if source_id not in self._source_health:
            self._source_health[source_id] = SourceHealth(
                source_id=source_id,
                is_healthy=False,
                last_success=None,
                last_failure=datetime.now()
            )
        
        health = self._source_health[source_id]
        health.last_failure = datetime.now()
        health.failure_count += 1
        health.is_healthy = False
        
        # Open circuit if too many failures
        if health.failure_count >= self._circuit_threshold:
            health.circuit_open = True
            logger.warning(f"Circuit opened for source: {source_id}")
    
    def is_source_available(self, source_id: str) -> bool:
        """Check if a source is available (circuit not open)"""
        if source_id not in self._source_health:
            return True  # Unknown sources are assumed available
        
        health = self._source_health[source_id]
        
        # Check if circuit should be half-open (time for retry)
        if health.circuit_open and health.last_failure:
            if datetime.now() - health.last_failure > self._circuit_timeout:
                return True  # Allow retry
        
        return not health.circuit_open
    
    def get_fallback_level(self, failed: List[str], total: List[str]) -> FallbackLevel:
        """Determine the fallback level based on failures"""
        if not failed:
            return FallbackLevel.NONE
        
        failure_ratio = len(failed) / len(total) if total else 0
        
        if failure_ratio < 0.25:
            return FallbackLevel.PARTIAL
        elif failure_ratio < 0.50:
            return FallbackLevel.DEGRADED
        elif failure_ratio < 0.90:
            return FallbackLevel.MINIMAL
        else:
            return FallbackLevel.OFFLINE
    
    def build_fallback_response(
        self,
        query: str,
        failed_sources: List[str],
        working_sources: List[str],
        partial_data: Dict[str, Any] = None
    ) -> FallbackResponse:
        """
        Build a fallback response when sources fail
        
        Args:
            query: Original user query
            failed_sources: Sources that failed
            working_sources: Sources that succeeded
            partial_data: Any data we managed to retrieve
        
        Returns:
            FallbackResponse with alternative answer and suggestions
        """
        total = failed_sources + working_sources
        level = self.get_fallback_level(failed_sources, total)
        
        # Determine best action
        if level == FallbackLevel.NONE:
            action = FallbackAction.RETRY  # Actually no action needed
        elif level == FallbackLevel.PARTIAL:
            action = FallbackAction.CACHE if partial_data else FallbackAction.ALTERNATE
        elif level == FallbackLevel.DEGRADED:
            action = FallbackAction.SIMPLIFY
        elif level == FallbackLevel.MINIMAL:
            action = FallbackAction.CACHE
        else:
            action = FallbackAction.FAIL
        
        # Get template
        template = FALLBACK_TEMPLATES.get(level, FALLBACK_TEMPLATES[FallbackLevel.MINIMAL])
        
        # Build answer
        answer = template["answer"].format(
            working_count=len(working_sources),
            total_count=len(total)
        )
        
        # Add any cached fallback data if relevant to query
        recovered_data = partial_data or {}
        if not recovered_data:
            recovered_data = self._find_cached_fallback(query)
        
        return FallbackResponse(
            level=level,
            action_taken=action,
            original_query=query,
            fallback_answer=answer,
            explanation=template["explanation"],
            suggestions=template["suggestions"],
            failed_sources=failed_sources,
            working_sources=working_sources,
            recovered_data=recovered_data
        )
    
    def _find_cached_fallback(self, query: str) -> Dict[str, Any]:
        """Find relevant cached fallback data for a query"""
        query_lower = query.lower()
        result = {}
        
        # Check for relevant cached data
        if any(word in query_lower for word in ["country", "countries", "nation"]):
            result["countries_info"] = self._fallback_cache.get("countries_count")
            result["regions"] = self._fallback_cache.get("regions")
        
        if any(word in query_lower for word in ["api", "endpoint", "service"]):
            result["api_info"] = self._fallback_cache.get("api_count")
            result["services"] = self._fallback_cache.get("services")
        
        if any(word in query_lower for word in ["category", "type", "sector"]):
            result["categories"] = self._fallback_cache.get("categories")
        
        # If nothing matched, return general info
        if not result:
            result["general"] = "Kloud Internal AGI - 4053+ sources across 155+ countries"
        
        return result
    
    def get_alternative_sources(self, failed_source: str) -> List[str]:
        """Get alternative sources when one fails"""
        # Source alternatives mapping
        alternatives = {
            "europe_sources": ["global_data_sources", "eastern_europe_balkans_sources"],
            "americas_sources": ["global_data_sources", "caribbean_central_america_sources"],
            "asia_china_sources": ["global_data_sources", "asia_oceania_global_sources"],
            "india_south_asia_sources": ["global_data_sources", "asia_oceania_global_sources"],
            "africa_middle_east_sources": ["global_data_sources"],
            "eastern_europe_balkans_sources": ["europe_sources", "global_data_sources"],
            "caribbean_central_america_sources": ["americas_sources", "global_data_sources"],
            "pacific_islands_sources": ["asia_oceania_global_sources", "global_data_sources"],
            "central_asia_caucasus_sources": ["asia_oceania_global_sources", "global_data_sources"],
        }
        
        # Filter out sources that are also down
        alts = alternatives.get(failed_source, ["global_data_sources"])
        return [a for a in alts if self.is_source_available(a)]
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get summary of all source health"""
        healthy = [sid for sid, h in self._source_health.items() if h.is_healthy]
        unhealthy = [sid for sid, h in self._source_health.items() if not h.is_healthy]
        circuits_open = [sid for sid, h in self._source_health.items() if h.circuit_open]
        
        return {
            "total_tracked": len(self._source_health),
            "healthy_count": len(healthy),
            "unhealthy_count": len(unhealthy),
            "circuits_open": len(circuits_open),
            "healthy_sources": healthy,
            "unhealthy_sources": unhealthy,
            "circuit_breakers": circuits_open
        }
    
    def reset_circuit(self, source_id: str):
        """Manually reset a circuit breaker"""
        if source_id in self._source_health:
            self._source_health[source_id].circuit_open = False
            self._source_health[source_id].failure_count = 0
            logger.info(f"Circuit reset for source: {source_id}")
    
    def reset_all_circuits(self):
        """Reset all circuit breakers (use with caution)"""
        for source_id in self._source_health:
            self._source_health[source_id].circuit_open = False
            self._source_health[source_id].failure_count = 0
        logger.info("All circuits reset")


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def format_fallback_for_user(response: FallbackResponse) -> str:
    """Format a fallback response for end user display"""
    lines = [
        f"📢 {response.fallback_answer}",
        f"",
        f"ℹ️ {response.explanation}",
        f"",
        f"💡 Suggestions:"
    ]
    
    for i, suggestion in enumerate(response.suggestions, 1):
        lines.append(f"   {i}. {suggestion}")
    
    if response.recovered_data:
        lines.append("")
        lines.append("📊 Available information:")
        for key, value in list(response.recovered_data.items())[:3]:
            if isinstance(value, str):
                lines.append(f"   • {value}")
            elif isinstance(value, list):
                lines.append(f"   • {key}: {', '.join(str(v) for v in value[:5])}")
    
    return "\n".join(lines)


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================

_manager_instance: Optional[FallbackManager] = None

def get_manager() -> FallbackManager:
    """Get the global fallback manager singleton"""
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = FallbackManager()
    return _manager_instance

