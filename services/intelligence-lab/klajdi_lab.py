#!/usr/bin/env python3
"""
KLAJDI - Knost-Labor-Array-Jonify-Detective-Intelligence
=========================================================

Laboratori hetimor i sinjaleve të Kloud.
Mbledh, organizon, heton, dhe zbulon anomali në sistem.

Author: Ledjan Ahmati (CEO, ABA GmbH)
"""

import asyncio
import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set

import numpy as np

logger = logging.getLogger("klajdi")


# ═══════════════════════════════════════════════════════════════════════════════
# SIGNAL TYPES AND STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════

class SignalSource(Enum):
    """Burimet e sinjaleve"""
    OCEAN = "ocean"              # Curiosity Ocean - content generation
    BLERINA = "blerina"          # Gap detection & analysis
    EAP = "eap"                  # Evresi-Analysi-Proposi
    KLOUD = "kloud"              # Kloud Fabric - CRDT, Tide, PQ
    PUBLISHER = "publisher"      # Content Factory
    LIAM = "liam"                # Labor Intelligence Array Matrix
    ALDA = "alda"                # Artificial Labor Determined Array
    TRINITY = "trinity"          # ALBA-ALBI-JONA
    USER = "user"                # User actions
    SYSTEM = "system"            # System events
    EXTERNAL = "external"        # External APIs, webhooks


class SignalChannel(Enum):
    """Kanalet e sinjaleve"""
    HTTP = "http"
    WEBSOCKET = "websocket"
    WORKER = "worker"
    CRON = "cron"
    INTERNAL = "internal"
    CALLBACK = "callback"
    EVENT = "event"


class SignalSeverity(Enum):
    """Niveli i rëndësisë"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    ANOMALY = "anomaly"
    SUCCESS = "success"


@dataclass
class SignalEvent:
    """
    Një sinjal i vetëm nga sistemi.
    Jona e inteligjencës.
    """
    id: str
    source: SignalSource
    channel: SignalChannel
    payload: Dict[str, Any]
    timestamp: str
    severity: SignalSeverity = SignalSeverity.INFO
    meta: Dict[str, Any] = field(default_factory=dict)
    
    # Për jonify - zbërthim në njësi
    ions: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "source": self.source.value,
            "channel": self.channel.value,
            "severity": self.severity.value,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "meta": self.meta,
            "ions": self.ions
        }
    
    def compute_hash(self) -> str:
        """Hash unik për sinjal"""
        content = f"{self.source.value}:{self.channel.value}:{json.dumps(self.payload, sort_keys=True)}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]


@dataclass
class InvestigationCase:
    """
    Një rast hetimi - dosje e sinjaleve të lidhura.
    """
    id: str
    title: str
    hypothesis: str
    status: str = "open"  # open, investigating, resolved, archived
    signals: List[SignalEvent] = field(default_factory=list)
    findings: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    timeline: List[Dict[str, Any]] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: Optional[str] = None
    
    def add_finding(self, finding: str) -> None:
        self.findings.append(finding)
        self.updated_at = datetime.now(timezone.utc).isoformat()
        self.timeline.append({
            "action": "finding_added",
            "content": finding,
            "at": self.updated_at
        })
    
    def add_risk(self, risk: str) -> None:
        self.risks.append(risk)
        self.updated_at = datetime.now(timezone.utc).isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "hypothesis": self.hypothesis,
            "status": self.status,
            "signals_count": len(self.signals),
            "findings": self.findings,
            "risks": self.risks,
            "recommendations": self.recommendations,
            "timeline": self.timeline,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


# ═══════════════════════════════════════════════════════════════════════════════
# KNOST LABOR - Mbledhja e fakteve
# ═══════════════════════════════════════════════════════════════════════════════

class KnostLabor:
    """
    KNOST - Knowledge Observation & Signal Tracking
    Mbledh fakte dhe sinjale nga gjithë sistemi.
    """
    
    def __init__(self) -> None:
        self._facts: Dict[str, Any] = {}
        self._observations: List[Dict[str, Any]] = []
        self._metrics_cache: Dict[str, Any] = {}
    
    async def observe_source(self, source: SignalSource) -> Dict[str, Any]:
        """Vëzhgo një burim specifik"""
        observation: Dict[str, Any] = {
            "source": source.value,
            "observed_at": datetime.now(timezone.utc).isoformat(),
            "facts": {}
        }
        
        # Simulate observation based on source
        if source == SignalSource.LIAM:
            observation["facts"] = await self._observe_liam()
        elif source == SignalSource.ALDA:
            observation["facts"] = await self._observe_alda()
        elif source == SignalSource.OCEAN:
            observation["facts"] = await self._observe_ocean()
        elif source == SignalSource.SYSTEM:
            observation["facts"] = await self._observe_system()
        
        self._observations.append(observation)
        return observation
    
    async def _observe_liam(self) -> Dict[str, Any]:
        """Observe LIAM metrics"""
        try:
            import httpx
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get("http://localhost:7575/status")
                if resp.status_code == 200:
                    return resp.json()
        except Exception:
            pass
        return {"status": "unavailable", "simulated": True}
    
    async def _observe_alda(self) -> Dict[str, Any]:
        """Observe ALDA metrics"""
        try:
            import httpx
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get("http://localhost:8063/status")
                if resp.status_code == 200:
                    return resp.json()
        except Exception:
            pass
        return {"status": "unavailable", "simulated": True}
    
    async def _observe_ocean(self) -> Dict[str, Any]:
        """Observe Curiosity Ocean"""
        try:
            import httpx
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get("http://localhost:8055/status")
                if resp.status_code == 200:
                    return resp.json()
        except Exception:
            pass
        return {"status": "unavailable", "simulated": True}
    
    async def _observe_system(self) -> Dict[str, Any]:
        """Observe system metrics"""
        try:
            import psutil
            return {
                "cpu_percent": psutil.cpu_percent(interval=0.1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage("/").percent
            }
        except ImportError:
            return {"simulated": True, "cpu": 50, "memory": 60, "disk": 40}


# ═══════════════════════════════════════════════════════════════════════════════
# ARRAY - Organizimi i të dhënave
# ═══════════════════════════════════════════════════════════════════════════════

class SignalArray:
    """
    ARRAY - Organizon sinjalet si seri kohore dhe dosje.
    """
    
    def __init__(self, max_size: int = 10000):
        self._signals: List[SignalEvent] = []
        self._max_size = max_size
        self._index_by_source: Dict[str, List[int]] = {}
        self._index_by_severity: Dict[str, List[int]] = {}
    
    def append(self, signal: SignalEvent) -> int:
        """Shto sinjal në array"""
        idx = len(self._signals)
        self._signals.append(signal)
        
        # Update indices
        source_key = signal.source.value
        if source_key not in self._index_by_source:
            self._index_by_source[source_key] = []
        self._index_by_source[source_key].append(idx)
        
        severity_key = signal.severity.value
        if severity_key not in self._index_by_severity:
            self._index_by_severity[severity_key] = []
        self._index_by_severity[severity_key].append(idx)
        
        # Cleanup if too large
        if len(self._signals) > self._max_size:
            self._compact()
        
        return idx
    
    def _compact(self) -> None:
        """Remove old signals"""
        keep_count = self._max_size // 2
        self._signals = self._signals[-keep_count:]
        self._rebuild_indices()
    
    def _rebuild_indices(self) -> None:
        """Rebuild all indices"""
        self._index_by_source = {}
        self._index_by_severity = {}
        for idx, signal in enumerate(self._signals):
            source_key = signal.source.value
            if source_key not in self._index_by_source:
                self._index_by_source[source_key] = []
            self._index_by_source[source_key].append(idx)
            
            severity_key = signal.severity.value
            if severity_key not in self._index_by_severity:
                self._index_by_severity[severity_key] = []
            self._index_by_severity[severity_key].append(idx)
    
    def get_by_source(self, source: SignalSource) -> List[SignalEvent]:
        """Merr sinjalet sipas burimit"""
        indices = self._index_by_source.get(source.value, [])
        return [self._signals[i] for i in indices]
    
    def get_by_severity(self, severity: SignalSeverity) -> List[SignalEvent]:
        """Merr sinjalet sipas rëndësisë"""
        indices = self._index_by_severity.get(severity.value, [])
        return [self._signals[i] for i in indices]
    
    def get_time_range(self, start: str, end: str) -> List[SignalEvent]:
        """Merr sinjalet në një interval kohor"""
        return [s for s in self._signals if start <= s.timestamp <= end]
    
    def to_numpy(self) -> np.ndarray:
        """Konverto në numpy array për analiza numerike"""
        if not self._signals:
            return np.array([])
        
        # Create numeric representation
        data = []
        source_map = {s.value: i for i, s in enumerate(SignalSource)}
        severity_map = {s.value: i for i, s in enumerate(SignalSeverity)}
        
        for signal in self._signals:
            row = [
                source_map.get(signal.source.value, 0),
                severity_map.get(signal.severity.value, 0),
                len(signal.payload),
                len(signal.ions)
            ]
            data.append(row)
        
        return np.array(data)


# ═══════════════════════════════════════════════════════════════════════════════
# JONIFY - Zbërthimi në njësi kuptimi
# ═══════════════════════════════════════════════════════════════════════════════

class Jonify:
    """
    JONIFY - Zbërthen sinjalet në njësi atomike (jone).
    Kush foli? Kur? Pse? Me çfarë toni?
    """
    
    def __init__(self) -> None:
        self._ion_patterns: Dict[str, Any] = {}
    
    def ionize(self, signal: SignalEvent) -> List[Dict[str, Any]]:
        """Zbërthen sinjalin në jone"""
        ions = []
        
        # Ion 1: Source identity
        ions.append({
            "type": "source_identity",
            "who": signal.source.value,
            "channel": signal.channel.value,
            "at": signal.timestamp
        })
        
        # Ion 2: Payload analysis
        payload = signal.payload
        if isinstance(payload, dict):
            for key, value in payload.items():
                ions.append({
                    "type": "payload_field",
                    "key": key,
                    "value_type": type(value).__name__,
                    "value_summary": str(value)[:100] if value else ""
                })
        
        # Ion 3: Severity context
        ions.append({
            "type": "severity_context",
            "severity": signal.severity.value,
            "is_critical": str(signal.severity in [SignalSeverity.CRITICAL, SignalSeverity.ANOMALY]),
            "requires_attention": str(signal.severity != SignalSeverity.INFO)
        })
        
        # Ion 4: Timing analysis
        try:
            ts = datetime.fromisoformat(signal.timestamp.replace('Z', '+00:00'))
            ions.append({
                "type": "timing",
                "hour": str(ts.hour),
                "weekday": str(ts.weekday()),
                "is_business_hours": str(9 <= ts.hour <= 17),
                "is_weekend": str(ts.weekday() >= 5)
            })
        except Exception:
            pass
        
        # Store ions in signal
        signal.ions = ions
        return ions
    
    def find_patterns(self, ions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Gjen pattern-e në jone"""
        patterns = []
        
        # Count by type
        type_counts: Dict[str, int] = {}
        for ion in ions:
            ion_type = ion.get("type", "unknown")
            type_counts[ion_type] = type_counts.get(ion_type, 0) + 1
        
        # Detect patterns
        for ion_type, count in type_counts.items():
            if count > 5:
                patterns.append({
                    "pattern": "repeated_type",
                    "type": ion_type,
                    "count": count,
                    "significance": "high" if count > 10 else "medium"
                })
        
        return patterns


# ═══════════════════════════════════════════════════════════════════════════════
# DETECTIVE INTELLIGENCE - Zbulimi i anomalive
# ═══════════════════════════════════════════════════════════════════════════════

class DetectiveIntelligence:
    """
    DETECTIVE - Gjen anomali, pattern-e, boshllëqe, rreziqe.
    """
    
    def __init__(self) -> None:
        self._anomaly_thresholds: Dict[str, Any] = {
            "signal_rate": 100,  # signals per minute
            "error_rate": 0.1,   # 10% error rate
            "response_time": 5000,  # 5 seconds
        }
        self._known_patterns: Set[str] = set()
    
    def detect_anomalies(self, signals: List[SignalEvent]) -> List[Dict[str, Any]]:
        """Zbulon anomali në sinjale"""
        anomalies: List[Dict[str, Any]] = []
        
        if not signals:
            return anomalies
        
        # Check for unusual severity spikes
        critical_count = sum(1 for s in signals if s.severity == SignalSeverity.CRITICAL)
        if critical_count > len(signals) * 0.2:  # More than 20% critical
            anomalies.append({
                "type": "severity_spike",
                "description": f"High critical signal rate: {critical_count}/{len(signals)}",
                "severity": "high",
                "recommendation": "Investigate system health immediately"
            })
        
        # Check for source concentration
        source_counts: Dict[str, int] = {}
        for s in signals:
            source_counts[s.source.value] = source_counts.get(s.source.value, 0) + 1
        
        for source, count in source_counts.items():
            if count > len(signals) * 0.8:  # One source > 80%
                anomalies.append({
                    "type": "source_concentration",
                    "source": source,
                    "percentage": str(round(count / len(signals) * 100, 1)),
                    "description": f"Single source dominance: {source}",
                    "recommendation": "Check if other sources are functioning"
                })
        
        # Check for gaps in timeline
        if len(signals) >= 2:
            timestamps = sorted([s.timestamp for s in signals])
            for i in range(1, len(timestamps)):
                try:
                    t1 = datetime.fromisoformat(timestamps[i-1].replace('Z', '+00:00'))
                    t2 = datetime.fromisoformat(timestamps[i].replace('Z', '+00:00'))
                    gap = (t2 - t1).total_seconds()
                    if gap > 300:  # 5 minute gap
                        anomalies.append({
                            "type": "timeline_gap",
                            "gap_seconds": str(gap),
                            "between": str([timestamps[i-1], timestamps[i]]),
                            "description": f"Signal gap of {gap:.0f} seconds detected",
                            "recommendation": "Check for service interruptions"
                        })
                except Exception:
                    pass
        
        return anomalies
    
    def detect_risks(self, signals: List[SignalEvent], cases: List[InvestigationCase]) -> List[Dict[str, Any]]:
        """Identifikon rreziqe potenciale"""
        risks = []
        
        # Risk: Too many open cases
        open_cases = [c for c in cases if c.status == "open"]
        if len(open_cases) > 10:
            risks.append({
                "type": "case_overload",
                "count": len(open_cases),
                "description": "Too many open investigation cases",
                "mitigation": "Prioritize and resolve older cases"
            })
        
        # Risk: Unresolved anomalies
        anomaly_signals = [s for s in signals if s.severity == SignalSeverity.ANOMALY]
        if anomaly_signals:
            risks.append({
                "type": "unresolved_anomalies",
                "count": len(anomaly_signals),
                "description": f"{len(anomaly_signals)} anomaly signals detected",
                "mitigation": "Create investigation cases for anomalies"
            })
        
        return risks


# ═══════════════════════════════════════════════════════════════════════════════
# KLAJDI LAB - Laboratori i plotë
# ═══════════════════════════════════════════════════════════════════════════════

class KlajdiLab:
    """
    KLAJDI - Knost-Labor-Array-Jonify-Detective-Intelligence
    
    Laboratori hetimor i brendshëm i Kloud.
    - Mbledh sinjale nga gjithë sistemi
    - Organizon në seri dhe dosje
    - Zbërthen në njësi kuptimi
    - Zbulon anomali dhe rreziqe
    - Jep rekomandime për adminin
    """
    
    def __init__(self) -> None:
        self.knost: KnostLabor = KnostLabor()
        self.array: SignalArray = SignalArray()
        self.jonify: Jonify = Jonify()
        self.detective: DetectiveIntelligence = DetectiveIntelligence()
        self._cases: List[InvestigationCase] = []
        self._stats: Dict[str, Any] = {
            "signals_ingested": 0,
            "cases_opened": 0,
            "anomalies_detected": 0,
            "started_at": datetime.now(timezone.utc).isoformat()
        }
    
    async def ingest_signal(
        self,
        source: SignalSource,
        channel: SignalChannel,
        payload: Dict[str, Any],
        severity: SignalSeverity = SignalSeverity.INFO,
        meta: Optional[Dict[str, Any]] = None
    ) -> SignalEvent:
        """Ingest a new signal into the lab"""
        event_id = hashlib.md5(
            f"{source.value}{channel.value}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:12]
        
        signal = SignalEvent(
            id=event_id,
            source=source,
            channel=channel,
            payload=payload,
            timestamp=datetime.now(timezone.utc).isoformat(),
            severity=severity,
            meta=meta or {}
        )
        
        # Jonify the signal
        self.jonify.ionize(signal)
        
        # Add to array
        self.array.append(signal)
        
        # Update stats
        self._stats["signals_ingested"] += 1
        
        logger.info(f"📡 Signal ingested: {event_id} from {source.value}")
        
        return signal
    
    def open_case(
        self,
        title: str,
        hypothesis: str,
        signals: Optional[List[SignalEvent]] = None
    ) -> InvestigationCase:
        """Open a new investigation case"""
        case_id = hashlib.md5(
            f"{title}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:10]
        
        case = InvestigationCase(
            id=case_id,
            title=title,
            hypothesis=hypothesis,
            signals=signals or []
        )
        
        self._cases.append(case)
        self._stats["cases_opened"] += 1
        
        logger.info(f"📂 Case opened: {case_id} - {title}")
        
        return case
    
    async def analyze_case(self, case: InvestigationCase) -> InvestigationCase:
        """Analyze an investigation case"""
        case.status = "investigating"
        case.timeline.append({
            "action": "analysis_started",
            "at": datetime.now(timezone.utc).isoformat()
        })
        
        if not case.signals:
            case.add_finding("No signals attached to this case.")
            return case
        
        # Analyze sources
        sources = {s.source.value for s in case.signals}
        case.add_finding(f"Signals from {len(sources)} sources: {', '.join(sorted(sources))}")
        
        # Analyze severity distribution
        severity_counts: Dict[str, int] = {}
        for s in case.signals:
            severity_counts[s.severity.value] = severity_counts.get(s.severity.value, 0) + 1
        
        case.add_finding(f"Severity distribution: {severity_counts}")
        
        # Detect anomalies
        anomalies = self.detective.detect_anomalies(case.signals)
        for anomaly in anomalies:
            case.add_finding(f"Anomaly: {anomaly['description']}")
            case.recommendations.append(anomaly.get('recommendation', 'Investigate further'))
        
        # Collect all ions
        all_ions = []
        for signal in case.signals:
            all_ions.extend(signal.ions)
        
        # Find patterns
        patterns = self.jonify.find_patterns(all_ions)
        for pattern in patterns:
            case.add_finding(f"Pattern detected: {pattern['type']} ({pattern.get('count', 0)} occurrences)")
        
        self._stats["anomalies_detected"] += len(anomalies)
        
        return case
    
    async def run_diagnostics(self) -> Dict[str, Any]:
        """Run full system diagnostics"""
        logger.info("🔬 Running KLAJDI diagnostics...")
        
        observations: List[Dict[str, Any]] = []
        anomalies_list: List[Dict[str, Any]] = []
        risks_list: List[Dict[str, Any]] = []
        recommendations: List[str] = []
        
        # Observe all sources
        for source in [SignalSource.LIAM, SignalSource.ALDA, SignalSource.OCEAN, SignalSource.SYSTEM]:
            obs = await self.knost.observe_source(source)
            observations.append(obs)
        
        # Detect anomalies in recent signals
        recent_signals = self.array._signals[-100:] if self.array._signals else []
        anomalies_list = self.detective.detect_anomalies(recent_signals)
        
        # Detect risks
        risks_list = self.detective.detect_risks(recent_signals, self._cases)
        
        # Generate recommendations
        if anomalies_list:
            recommendations.append("Review detected anomalies and create investigation cases")
        if risks_list:
            recommendations.append("Address identified risks in priority order")
        if not recent_signals:
            recommendations.append("System appears quiet - verify signal ingestion is working")
        
        return {
            "observations": observations,
            "anomalies": anomalies_list,
            "risks": risks_list,
            "recommendations": recommendations,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get lab statistics"""
        return {
            **self._stats,
            "signals_in_array": len(self.array._signals),
            "cases_count": len(self._cases),
            "open_cases": len([c for c in self._cases if c.status == "open"]),
            "sources_tracked": list(self.array._index_by_source.keys())
        }
    
    def get_cases(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all cases, optionally filtered by status"""
        cases = self._cases
        if status:
            cases = [c for c in cases if c.status == status]
        return [c.to_dict() for c in cases]
    
    def export_to_excel(self) -> Dict[str, Any]:
        """Export signals and cases for Excel/tabular format"""
        signals_data = []
        for s in self.array._signals[-1000:]:  # Last 1000
            signals_data.append({
                "id": s.id,
                "source": s.source.value,
                "channel": s.channel.value,
                "severity": s.severity.value,
                "timestamp": s.timestamp,
                "payload_keys": list(s.payload.keys()) if isinstance(s.payload, dict) else [],
                "ions_count": len(s.ions)
            })
        
        cases_data = [c.to_dict() for c in self._cases]
        
        return {
            "signals": signals_data,
            "cases": cases_data,
            "stats": self.get_stats()
        }


# ═══════════════════════════════════════════════════════════════════════════════
# SINGLETON AND FACTORY
# ═══════════════════════════════════════════════════════════════════════════════

_klajdi_lab: Optional[KlajdiLab] = None


def get_klajdi_lab() -> KlajdiLab:
    """Get or create KLAJDI Lab instance"""
    global _klajdi_lab
    if _klajdi_lab is None:
        _klajdi_lab = KlajdiLab()
        logger.info("🧪 KLAJDI Lab initialized")
    return _klajdi_lab


# ═══════════════════════════════════════════════════════════════════════════════
# CLI INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    lab = get_klajdi_lab()
    
    async def main():
        # Ingest some test signals
        await lab.ingest_signal(
            SignalSource.SYSTEM,
            SignalChannel.INTERNAL,
            {"cpu": 75, "memory": 60},
            SignalSeverity.INFO
        )
        
        await lab.ingest_signal(
            SignalSource.LIAM,
            SignalChannel.HTTP,
            {"operation": "matrix_transform", "latency_ms": 120},
            SignalSeverity.INFO
        )
        
        await lab.ingest_signal(
            SignalSource.OCEAN,
            SignalChannel.WORKER,
            {"action": "content_generated", "words": 850},
            SignalSeverity.SUCCESS
        )
        
        # Run diagnostics
        results = await lab.run_diagnostics()
        print(json.dumps(results, indent=2))
        
        # Show stats
        print("\n📊 Lab Stats:")
        print(json.dumps(lab.get_stats(), indent=2))
    
    asyncio.run(main())

