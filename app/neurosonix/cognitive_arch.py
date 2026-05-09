"""
Cognitive architecture integration for the Kloud backend.

This module connects the ALBI layer with the lower-level BrainAnalyzer to
provide consistent health and metric snapshots that can be exposed through
API routes or reused by other services.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from app.Kloud.brain_analyzer import BrainAnalyzer


class CognitiveArchitecture:
    """Thin wrapper around :class:`BrainAnalyzer` for ALBI integration."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        config = config or {}
        center_name = config.get("center_name", "Default-Center")
        self.analyzer = BrainAnalyzer(center_name=center_name)

    async def get_health_metrics(self) -> Dict[str, Any]:
        """Return the current cognitive health snapshot."""
        return self.analyzer.compute_cognitive_health()

    async def get_system_metrics(self) -> Dict[str, Any]:
        """Expose raw system metrics (CPU, memory, disk, etc.)."""
        return self.analyzer.get_system_metrics()

    async def get_uptime_seconds(self) -> float:
        """Return the analyzer uptime in seconds."""
        return (datetime.utcnow() - self.analyzer.start_time).total_seconds()


