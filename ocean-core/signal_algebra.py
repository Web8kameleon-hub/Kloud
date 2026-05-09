# -*- coding: utf-8 -*-
"""
🌊 KLOUD SIGNAL ALGEBRA ENGINE
=================================
Motori matematikor që kupton valët e sinjaleve.

OPERACIONET BAZË:
================
✅ Superpozim: S = Σᵢ Sᵢ
✅ Filtrim: F(S, condition) → S'
✅ Devijim: D = S_real - S_expected
✅ Agregim: A(S, window) → metrics
✅ Korelacion: Corr(Sᵢ, Sⱼ)

Author: Kloud Team
Version: 1.0.0
"""

from __future__ import annotations
import logging
import statistics
import math
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("signal_algebra")


# =============================================================================
# SIGNAL TYPES
# =============================================================================

class SignalType(Enum):
    """Llojet e sinjaleve në sistem"""
    METRIC = "metric"
    LOG = "log"
    ANOMALY = "anomaly"
    INTERACTION = "interaction"
    HEALTH = "health"
    CYCLE = "cycle"
    ALIGNMENT = "alignment"
    PROPOSAL = "proposal"
    DATA_SOURCE = "data_source"
    LORA = "lora"
    NANOGRID = "nanogrid"
    NODE = "node"
    EXTERNAL = "external"


class SignalPriority(Enum):
    """Prioriteti i sinjaleve"""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    BACKGROUND = 5


# =============================================================================
# SIGNAL DATA CLASS
# =============================================================================

@dataclass
class Signal:
    """
    Një sinjal në sistem - njësia bazë e komunikimit.
    
    Çdo sinjal është një puls në detin e Curiosity Ocean.
    """
    signal_id: str = field(default_factory=lambda: f"sig_{uuid.uuid4().hex[:12]}")
    source: str = ""
    signal_type: SignalType = SignalType.METRIC
    priority: SignalPriority = SignalPriority.NORMAL
    payload: Dict[str, Any] = field(default_factory=dict)
    value: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    confidence: float = 1.0
    tags: List[str] = field(default_factory=list)
    processed: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "signal_id": self.signal_id,
            "source": self.source,
            "type": self.signal_type.value,
            "priority": self.priority.value,
            "payload": self.payload,
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
            "confidence": self.confidence,
            "tags": self.tags,
            "processed": self.processed
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Signal":
        return cls(
            signal_id=data.get("signal_id", f"sig_{uuid.uuid4().hex[:12]}"),
            source=data.get("source", ""),
            signal_type=SignalType(data.get("type", "metric")),
            priority=SignalPriority(data.get("priority", 3)),
            payload=data.get("payload", {}),
            value=float(data.get("value", 0.0)),
            timestamp=datetime.fromisoformat(data["timestamp"]) if "timestamp" in data else datetime.now(timezone.utc),
            confidence=float(data.get("confidence", 1.0)),
            tags=data.get("tags", []),
            processed=data.get("processed", False)
        )


# =============================================================================
# SIGNAL ALGEBRA ENGINE
# =============================================================================

class SignalAlgebra:
    """
    🧠 SIGNAL ALGEBRA ENGINE
    
    Motori matematikor që procedon dhe kupton sinjalet.
    Ky është "truri analitik" i Curiosity Ocean.
    """
    
    def __init__(self):
        self.signal_buffer: List[Signal] = []
        self.max_buffer_size = 10000
        self.stats_cache: Dict[str, Any] = {}
        logger.info("🧮 Signal Algebra Engine initialized")
    
    # =========================================================================
    # SUPERPOZIM - Kombinimi i sinjaleve
    # =========================================================================
    
    def superpose(self, signals: List[Signal], weights: Optional[List[float]] = None) -> float:
        """
        Superpozim: S = Σᵢ wᵢ * Sᵢ
        
        Kombinon sinjale të shumta në një vlerë të vetme.
        """
        if not signals:
            return 0.0
        
        if weights is None:
            weights = [1.0] * len(signals)
        
        total = sum(s.value * w for s, w in zip(signals, weights))
        return total
    
    def superpose_by_confidence(self, signals: List[Signal]) -> float:
        """
        Superpozim i ponderuar me konfidencë.
        Sinjalet me konfidencë më të lartë kanë peshë më të madhe.
        """
        if not signals:
            return 0.0
        
        weights = [s.confidence for s in signals]
        total_weight = sum(weights)
        
        if total_weight == 0:
            return 0.0
        
        return sum(s.value * s.confidence for s in signals) / total_weight
    
    # =========================================================================
    # FILTRIM - Nxjerrja e sinjaleve sipas kushteve
    # =========================================================================
    
    def filter(self, signals: List[Signal], condition: Callable[[Signal], bool]) -> List[Signal]:
        """
        Filtrim: F(S, condition) → S'
        
        Nxjerr vetëm sinjalet që përmbushin kushtin.
        """
        return [s for s in signals if condition(s)]
    
    def filter_by_type(self, signals: List[Signal], signal_type: SignalType) -> List[Signal]:
        """Filtro sipas llojit të sinjalit."""
        return [s for s in signals if s.signal_type == signal_type]
    
    def filter_by_source(self, signals: List[Signal], source_pattern: str) -> List[Signal]:
        """Filtro sipas burimit (përmban pattern)."""
        return [s for s in signals if source_pattern in s.source]
    
    def filter_by_priority(self, signals: List[Signal], max_priority: SignalPriority) -> List[Signal]:
        """Filtro sipas prioritetit (më i ulët = më urgjent)."""
        return [s for s in signals if s.priority.value <= max_priority.value]
    
    def filter_by_confidence(self, signals: List[Signal], min_confidence: float) -> List[Signal]:
        """Filtro sipas konfidencës minimale."""
        return [s for s in signals if s.confidence >= min_confidence]
    
    def filter_by_tags(self, signals: List[Signal], required_tags: List[str]) -> List[Signal]:
        """Filtro sipas tag-ave të kërkuara."""
        return [s for s in signals if all(tag in s.tags for tag in required_tags)]
    
    def filter_by_time_window(self, signals: List[Signal], window_seconds: int) -> List[Signal]:
        """Filtro sinjalet brenda një dritareje kohore."""
        cutoff = datetime.now(timezone.utc) - timedelta(seconds=window_seconds)
        return [s for s in signals if s.timestamp >= cutoff]
    
    # =========================================================================
    # DEVIJIM - Dallimi mes realitetit dhe pritjes
    # =========================================================================
    
    def deviation(self, real: float, expected: float) -> float:
        """
        Devijim: D = S_real - S_expected
        
        Kjo është baza e kuriozitetit: ku realiteti nuk përputhet me modelin.
        """
        return real - expected
    
    def deviation_percent(self, real: float, expected: float) -> float:
        """Devijim në përqindje."""
        if expected == 0:
            return float('inf') if real != 0 else 0.0
        return ((real - expected) / abs(expected)) * 100
    
    def deviation_signals(self, real_signals: List[Signal], expected_values: List[float]) -> List[float]:
        """Devijim për një listë sinjalesh."""
        return [
            self.deviation(s.value, exp) 
            for s, exp in zip(real_signals, expected_values)
        ]
    
    def anomaly_score(self, signals: List[Signal]) -> float:
        """
        Vlerëso anomalinë: sa larg janë sinjalet nga mesatarja?
        """
        if not signals or len(signals) < 2:
            return 0.0
        
        values = [s.value for s in signals]
        mean = statistics.mean(values)
        stdev = statistics.stdev(values)
        
        if stdev == 0:
            return 0.0
        
        # Z-score për sinjalin e fundit
        latest = signals[-1].value
        return abs((latest - mean) / stdev)
    
    # =========================================================================
    # AGREGIM - Statistika në dritare kohore
    # =========================================================================
    
    def aggregate(self, signals: List[Signal], window_seconds: int = 60) -> Dict[str, Any]:
        """
        Agregim: A(S, window) → metrics
        
        Mesatare, variançë, trend — për të parë ritmin e detit.
        """
        windowed = self.filter_by_time_window(signals, window_seconds)
        
        if not windowed:
            return {
                "count": 0,
                "window_seconds": window_seconds,
                "metrics": {}
            }
        
        values = [s.value for s in windowed]
        
        metrics = {
            "count": len(windowed),
            "sum": sum(values),
            "mean": statistics.mean(values),
            "min": min(values),
            "max": max(values),
        }
        
        if len(values) >= 2:
            metrics["stdev"] = statistics.stdev(values)
            metrics["variance"] = statistics.variance(values)
            # Trend: diferenca mes mesatares së gjysmës së parë dhe të dytë
            mid = len(values) // 2
            first_half = statistics.mean(values[:mid]) if mid > 0 else values[0]
            second_half = statistics.mean(values[mid:])
            metrics["trend"] = second_half - first_half
        else:
            metrics["stdev"] = 0.0
            metrics["variance"] = 0.0
            metrics["trend"] = 0.0
        
        return {
            "count": len(windowed),
            "window_seconds": window_seconds,
            "first_timestamp": windowed[0].timestamp.isoformat(),
            "last_timestamp": windowed[-1].timestamp.isoformat(),
            "metrics": metrics
        }
    
    def moving_average(self, signals: List[Signal], window_size: int = 5) -> List[float]:
        """Mesatare lëvizëse për sinjalet."""
        if len(signals) < window_size:
            return [s.value for s in signals]
        
        values = [s.value for s in signals]
        result = []
        
        for i in range(len(values)):
            if i < window_size - 1:
                result.append(statistics.mean(values[:i+1]))
            else:
                result.append(statistics.mean(values[i-window_size+1:i+1]))
        
        return result
    
    # =========================================================================
    # KORELACION - Lidhja mes sinjaleve
    # =========================================================================
    
    def correlate(self, signals1: List[Signal], signals2: List[Signal]) -> float:
        """
        Korelacion: Corr(Sᵢ, Sⱼ)
        
        Gjen lidhjen mes dy serive të sinjaleve.
        """
        if len(signals1) != len(signals2) or len(signals1) < 2:
            return 0.0
        
        values1 = [s.value for s in signals1]
        values2 = [s.value for s in signals2]
        
        mean1 = statistics.mean(values1)
        mean2 = statistics.mean(values2)
        
        numerator = sum((v1 - mean1) * (v2 - mean2) for v1, v2 in zip(values1, values2))
        
        denom1 = math.sqrt(sum((v - mean1) ** 2 for v in values1))
        denom2 = math.sqrt(sum((v - mean2) ** 2 for v in values2))
        
        if denom1 == 0 or denom2 == 0:
            return 0.0
        
        return numerator / (denom1 * denom2)
    
    def cross_correlate(self, signals: Dict[str, List[Signal]]) -> Dict[str, Dict[str, float]]:
        """
        Korelacion i kryqëzuar mes shumë burimeve.
        
        Returns:
            Dict me korelacionet mes çdo çifti burimesh.
        """
        sources = list(signals.keys())
        correlations = {}
        
        for i, s1 in enumerate(sources):
            correlations[s1] = {}
            for s2 in sources[i+1:]:
                corr = self.correlate(signals[s1], signals[s2])
                correlations[s1][s2] = corr
        
        return correlations
    
    # =========================================================================
    # BUFFER MANAGEMENT
    # =========================================================================
    
    def add_signal(self, signal: Signal):
        """Shto sinjal në buffer."""
        self.signal_buffer.append(signal)
        
        # Mban bufferin brenda limiteve
        if len(self.signal_buffer) > self.max_buffer_size:
            self.signal_buffer = self.signal_buffer[-self.max_buffer_size:]
    
    def get_signals(self, 
                    source: Optional[str] = None,
                    signal_type: Optional[SignalType] = None,
                    window_seconds: Optional[int] = None) -> List[Signal]:
        """Merr sinjale nga bufferi me filtra."""
        result = self.signal_buffer.copy()
        
        if source:
            result = self.filter_by_source(result, source)
        
        if signal_type:
            result = self.filter_by_type(result, signal_type)
        
        if window_seconds:
            result = self.filter_by_time_window(result, window_seconds)
        
        return result
    
    def clear_buffer(self):
        """Pastro bufferin."""
        self.signal_buffer.clear()
        self.stats_cache.clear()
    
    # =========================================================================
    # ADVANCED OPERATIONS
    # =========================================================================
    
    def detect_silence(self, source: str, expected_interval_seconds: int = 30) -> bool:
        """
        Detekto heshtje të pazakontë nga një burim.
        
        "Cilat qeliza po heshtin prej shumë kohësh?"
        """
        source_signals = self.filter_by_source(self.signal_buffer, source)
        
        if not source_signals:
            return True  # Asnjë sinjal = heshtje
        
        latest = max(source_signals, key=lambda s: s.timestamp)
        time_since = (datetime.now(timezone.utc) - latest.timestamp).total_seconds()
        
        return time_since > expected_interval_seconds
    
    def detect_rhythm_change(self, source: str, window_seconds: int = 300) -> Dict[str, Any]:
        """
        Detekto ndryshimin e ritmit të një burimi.
        
        "Cilat sinjale po ndryshojnë ritmin?"
        """
        signals = self.filter_by_source(self.signal_buffer, source)
        signals = self.filter_by_time_window(signals, window_seconds)
        
        if len(signals) < 4:
            return {"changed": False, "reason": "insufficient_data"}
        
        # Ndaj në dy gjysmë
        mid = len(signals) // 2
        first_half = signals[:mid]
        second_half = signals[mid:]
        
        # Llogarit intervalin mesatar
        def avg_interval(sigs):
            if len(sigs) < 2:
                return 0
            intervals = [
                (sigs[i+1].timestamp - sigs[i].timestamp).total_seconds()
                for i in range(len(sigs) - 1)
            ]
            return statistics.mean(intervals) if intervals else 0
        
        interval1 = avg_interval(first_half)
        interval2 = avg_interval(second_half)
        
        if interval1 == 0:
            return {"changed": False, "reason": "no_first_interval"}
        
        change_percent = abs((interval2 - interval1) / interval1) * 100
        
        return {
            "changed": change_percent > 20,  # >20% ndryshim
            "first_interval": interval1,
            "second_interval": interval2,
            "change_percent": change_percent
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Statistika të përgjithshme të bufferit."""
        if not self.signal_buffer:
            return {"total_signals": 0}
        
        # Grupim sipas burimit
        sources = {}
        for s in self.signal_buffer:
            if s.source not in sources:
                sources[s.source] = 0
            sources[s.source] += 1
        
        # Grupim sipas llojit
        types = {}
        for s in self.signal_buffer:
            t = s.signal_type.value
            if t not in types:
                types[t] = 0
            types[t] += 1
        
        return {
            "total_signals": len(self.signal_buffer),
            "unique_sources": len(sources),
            "by_source": sources,
            "by_type": types,
            "buffer_capacity": f"{len(self.signal_buffer)}/{self.max_buffer_size}",
            "oldest_signal": self.signal_buffer[0].timestamp.isoformat() if self.signal_buffer else None,
            "newest_signal": self.signal_buffer[-1].timestamp.isoformat() if self.signal_buffer else None
        }


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

_algebra_instance: Optional[SignalAlgebra] = None

def get_signal_algebra() -> SignalAlgebra:
    """Get or create the Signal Algebra Engine singleton."""
    global _algebra_instance
    if _algebra_instance is None:
        _algebra_instance = SignalAlgebra()
    return _algebra_instance


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    algebra = get_signal_algebra()
    
    # Krijo disa sinjale test
    for i in range(10):
        signal = Signal(
            source="sensor-01",
            signal_type=SignalType.METRIC,
            value=20 + i * 0.5,
            tags=["temperature", "test"]
        )
        algebra.add_signal(signal)
    
    # Test operacionet
    signals = algebra.get_signals()
    print(f"Total signals: {len(signals)}")
    
    # Superpozim
    total = algebra.superpose(signals)
    print(f"Superposition: {total}")
    
    # Agregim
    agg = algebra.aggregate(signals, 60)
    print(f"Aggregation: {agg}")
    
    # Statistika
    stats = algebra.get_statistics()
    print(f"Statistics: {stats}")

