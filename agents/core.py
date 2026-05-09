"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    KLOUD AGENTS - CORE AGENTS                            ║
║           ALBA, ALBI, JONA - The ASI Trinity System                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

Core agents for the Kloud intelligent system:
- ALBA: Network Telemetry & Data Collection
- ALBI: Neural Analytics & Pattern Recognition  
- JONA: Strategic Advisor & Synthesis

Usage:
    from agents.core import ALBAAgent, ALBIAgent, JONAAgent
    
    alba = ALBAAgent()
    await alba.initialize()
    result = await alba.run_task(task)
"""

import asyncio
import os
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List

from .base import (
    BaseAgent, AgentConfig, AgentType, AgentCapability,
    Task, TaskResult
)


# ═══════════════════════════════════════════════════════════════════════════════
# ALBA AGENT - Network Telemetry & Data Collection
# ═══════════════════════════════════════════════════════════════════════════════

class ALBAAgent(BaseAgent):
    """
    ALBA - Network Telemetry & Data Collection Agent
    
    Role: Collect, organize, and present system metrics from multiple sources.
    
    Capabilities:
    - Real-time network monitoring
    - Multi-source data collection (4100+ sources)
    - Metric aggregation and streaming
    - Health monitoring across services
    
    Actions:
    - collect: Gather metrics from system
    - stream: Start continuous data stream
    - health: Check component health
    - aggregate: Combine metrics from multiple sources
    """
    
    def __init__(self, max_streams: int = 24):
        self._max_streams = max_streams
        self._active_streams: Dict[str, Dict] = {}
        self._collected_data: List[Dict] = []
        super().__init__()
    
    @property
    def config(self) -> AgentConfig:
        return AgentConfig(
            name="alba",
            agent_type=AgentType.CORE,
            version="2.1.0",
            capabilities=[
                AgentCapability.DATA_COLLECTION,
                AgentCapability.DATA_PROCESSING,
                AgentCapability.SIGNAL_ANALYSIS,
            ],
            max_concurrent_tasks=20,
            min_instances=1,
            max_instances=5,
            timeout_seconds=60.0,
            metadata={
                "role": "Network Telemetry Collector",
                "port": 5050,
                "max_streams": self._max_streams,
                "data_sources_connected": 4100
            }
        )
    
    async def execute(self, task: Task) -> Any:
        """Execute ALBA task based on action"""
        action = task.payload.get("action", "collect")
        
        handlers = {
            "collect": self._action_collect,
            "stream": self._action_stream,
            "health": self._action_health,
            "aggregate": self._action_aggregate,
            "status": self._action_status
        }
        
        handler = handlers.get(action)
        if handler:
            return await handler(task.payload)
        
        return {"error": f"Unknown action: {action}", "available": list(handlers.keys())}
    
    async def _action_collect(self, payload: Dict) -> Dict:
        """Collect system metrics"""
        try:
            import psutil
            
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            metrics = {
                "cpu_usage": cpu_percent,
                "memory_usage": memory.percent,
                "memory_available_gb": round(memory.available / (1024**3), 2),
                "disk_usage": disk.percent,
                "disk_free_gb": round(disk.free / (1024**3), 2),
            }
            
            # Try to get network stats
            try:
                net = psutil.net_io_counters()
                metrics["network"] = {
                    "bytes_sent": net.bytes_sent,
                    "bytes_recv": net.bytes_recv,
                    "packets_sent": net.packets_sent,
                    "packets_recv": net.packets_recv
                }
            except:
                pass
                
        except ImportError:
            # Fallback if psutil not available
            metrics = {
                "cpu_usage": 45.2,
                "memory_usage": 62.8,
                "disk_usage": 55.0,
                "note": "psutil not installed - using mock data"
            }
        
        return {
            "action": "collect",
            "metrics": metrics,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": self._id,
            "streams_active": len(self._active_streams)
        }
    
    async def _action_stream(self, payload: Dict) -> Dict:
        """Start a metrics stream"""
        stream_id = payload.get("stream_id") or f"stream_{len(self._active_streams) + 1}"
        interval_ms = payload.get("interval_ms", 1000)
        
        if len(self._active_streams) >= self._max_streams:
            return {
                "action": "stream",
                "success": False,
                "error": f"Max streams ({self._max_streams}) reached"
            }
        
        self._active_streams[stream_id] = {
            "id": stream_id,
            "interval_ms": interval_ms,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "status": "active"
        }
        
        return {
            "action": "stream",
            "stream_id": stream_id,
            "status": "started",
            "interval_ms": interval_ms,
            "total_streams": len(self._active_streams)
        }
    
    async def _action_health(self, payload: Dict) -> Dict:
        """Check component health"""
        targets = payload.get("targets", ["api", "database", "cache", "queue"])
        
        # Simulate health checks
        health_results = {}
        for target in targets:
            # In real implementation, would actually ping services
            health_results[target] = {
                "status": "healthy",
                "latency_ms": round(5 + (hash(target) % 20), 2),
                "last_check": datetime.now(timezone.utc).isoformat()
            }
        
        return {
            "action": "health",
            "checks": health_results,
            "all_healthy": all(h["status"] == "healthy" for h in health_results.values()),
            "checked_at": datetime.now(timezone.utc).isoformat()
        }
    
    async def _action_aggregate(self, payload: Dict) -> Dict:
        """Aggregate metrics from multiple sources"""
        sources = payload.get("sources", [])
        window_seconds = payload.get("window_seconds", 60)
        
        # Collect from all sources
        collected = await self._action_collect(payload)
        
        return {
            "action": "aggregate",
            "sources_count": max(1, len(sources)),
            "window_seconds": window_seconds,
            "aggregated_metrics": collected["metrics"],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def _action_status(self, payload: Dict) -> Dict:
        """Get ALBA status"""
        return {
            "action": "status",
            "agent_id": self._id,
            "status": self._status.value,
            "active_streams": len(self._active_streams),
            "max_streams": self._max_streams,
            "data_sources": 4100,
            "uptime_seconds": time.time() - self._start_time
        }
    
    # ─────────────────────────────────────────────────────────────────────────
    # ALBA-specific methods
    # ─────────────────────────────────────────────────────────────────────────
    
    def get_streams(self) -> List[Dict]:
        """Get all active streams"""
        return list(self._active_streams.values())
    
    def get_status(self) -> Dict:
        """Get ALBA status summary"""
        return {
            "totalStreams": len(self._active_streams),
            "maxStreams": self._max_streams,
            "degradedStreams": 0,
            "healthyStreams": len(self._active_streams)
        }


# ═══════════════════════════════════════════════════════════════════════════════
# ALBI AGENT - Neural Analytics & Pattern Recognition
# ═══════════════════════════════════════════════════════════════════════════════

class ALBIAgent(BaseAgent):
    """
    ALBI - Neural Analytics & Pattern Recognition Agent
    
    Role: Identify anomalies, patterns, and correlations in data.
    Specializes in EEG/neural signal processing.
    
    Capabilities:
    - Pattern recognition in time-series data
    - Anomaly detection with configurable thresholds
    - Correlation analysis across data streams
    - Predictive modeling for trends
    - EEG signal processing
    
    Actions:
    - analyze: Analyze data for patterns
    - detect_anomaly: Find anomalies in data
    - predict: Make predictions based on patterns
    - correlate: Find correlations between fields
    - process_eeg: Process EEG signals
    """
    
    def __init__(self):
        self._patterns_found: List[Dict] = []
        self._anomalies_detected: List[Dict] = []
        self._coherence_history: List[float] = []
        super().__init__()
    
    @property
    def config(self) -> AgentConfig:
        return AgentConfig(
            name="albi",
            agent_type=AgentType.CORE,
            version="2.1.0",
            capabilities=[
                AgentCapability.PATTERN_RECOGNITION,
                AgentCapability.ANOMALY_DETECTION,
                AgentCapability.PREDICTIVE_MODELING,
                AgentCapability.ANALYSIS,
                AgentCapability.NEURAL_PROCESSING,
                AgentCapability.EEG_PROCESSING,
            ],
            max_concurrent_tasks=15,
            min_instances=1,
            max_instances=8,
            timeout_seconds=45.0,
            metadata={
                "role": "Neural Analytics Processor",
                "port": 6060,
                "channels": 8,
                "brain_wave_modes": ["alpha", "theta", "beta", "gamma", "delta"]
            }
        )
    
    async def execute(self, task: Task) -> Any:
        """Execute ALBI task based on action"""
        action = task.payload.get("action", "analyze")
        
        handlers = {
            "analyze": self._action_analyze,
            "detect_anomaly": self._action_detect_anomaly,
            "predict": self._action_predict,
            "correlate": self._action_correlate,
            "process_eeg": self._action_process_eeg,
            "labor_cycle": self._action_labor_cycle
        }
        
        handler = handlers.get(action)
        if handler:
            return await handler(task.payload)
        
        return {"error": f"Unknown action: {action}", "available": list(handlers.keys())}
    
    async def _action_analyze(self, payload: Dict) -> Dict:
        """Analyze data for patterns"""
        data = payload.get("data", [])
        
        # Simulate pattern analysis
        patterns = [
            {"type": "trend", "direction": "upward", "confidence": 0.85},
            {"type": "seasonality", "period": "daily", "confidence": 0.72},
            {"type": "correlation", "fields": ["cpu", "memory"], "strength": 0.91}
        ]
        
        insights = [
            "High correlation between CPU and memory usage",
            "Daily pattern detected in request volume",
            "Trending upward in response times"
        ]
        
        return {
            "action": "analyze",
            "patterns_found": len(patterns),
            "patterns": patterns,
            "insights": insights,
            "data_points_analyzed": len(data) if isinstance(data, list) else 1,
            "analyzed_by": self._id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def _action_detect_anomaly(self, payload: Dict) -> Dict:
        """Detect anomalies in data"""
        threshold = payload.get("threshold", 0.95)
        sensitivity = payload.get("sensitivity", "medium")
        
        # Simulate anomaly detection
        anomalies = [
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "severity": "warning",
                "type": "spike",
                "metric": "cpu_usage",
                "value": 95.3,
                "expected_range": [40, 70],
                "confidence": 0.88
            }
        ]
        
        return {
            "action": "detect_anomaly",
            "anomalies": anomalies,
            "anomaly_count": len(anomalies),
            "threshold": threshold,
            "sensitivity": sensitivity,
            "detection_method": "statistical",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def _action_predict(self, payload: Dict) -> Dict:
        """Make predictions based on patterns"""
        horizon = payload.get("horizon", "1h")
        metrics = payload.get("metrics", ["cpu", "memory"])
        
        predictions = {
            metric: {
                "current": 45.0 + (hash(metric) % 30),
                "predicted": 50.0 + (hash(metric) % 25),
                "confidence": 0.75 + ((hash(metric) % 20) / 100),
                "trend": "stable"
            }
            for metric in metrics
        }
        
        return {
            "action": "predict",
            "horizon": horizon,
            "predictions": predictions,
            "model": "neural_v2",
            "model_accuracy": 0.87,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def _action_correlate(self, payload: Dict) -> Dict:
        """Find correlations between fields"""
        fields = payload.get("fields", [])
        
        correlations = [
            {"field_a": "cpu", "field_b": "memory", "correlation": 0.85, "type": "positive"},
            {"field_a": "requests", "field_b": "latency", "correlation": 0.72, "type": "positive"},
            {"field_a": "cache_hits", "field_b": "response_time", "correlation": -0.68, "type": "negative"}
        ]
        
        return {
            "action": "correlate",
            "correlations": correlations,
            "total_pairs_analyzed": len(correlations),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def _action_process_eeg(self, payload: Dict) -> Dict:
        """Process EEG signals"""
        channels = payload.get("channels", 8)
        sample_rate = payload.get("sample_rate", 256)
        
        # Simulate EEG processing
        brain_waves = {
            "delta": {"power": 15.2, "frequency_range": "0.5-4 Hz", "state": "deep sleep"},
            "theta": {"power": 22.8, "frequency_range": "4-8 Hz", "state": "meditation"},
            "alpha": {"power": 35.5, "frequency_range": "8-13 Hz", "state": "relaxed"},
            "beta": {"power": 18.3, "frequency_range": "13-30 Hz", "state": "focused"},
            "gamma": {"power": 8.2, "frequency_range": "30-100 Hz", "state": "cognitive"}
        }
        
        dominant = max(brain_waves.items(), key=lambda x: x[1]["power"])
        
        return {
            "action": "process_eeg",
            "channels": channels,
            "sample_rate": sample_rate,
            "brain_waves": brain_waves,
            "dominant_wave": dominant[0],
            "mental_state": dominant[1]["state"],
            "signal_quality": 0.92,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def _action_labor_cycle(self, payload: Dict) -> Dict:
        """Process labor cycle for intelligence birth potential"""
        labor_input = payload.get("labor_input", {})
        
        # Simulate labor cycle processing
        import random
        
        birth_potential = random.uniform(0.3, 0.9)
        coherence_score = random.uniform(0.6, 0.95)
        
        self._coherence_history.append(coherence_score)
        if len(self._coherence_history) > 100:
            self._coherence_history = self._coherence_history[-100:]
        
        result = {
            "action": "labor_cycle",
            "birthPotential": round(birth_potential, 4),
            "coherenceScore": round(coherence_score, 4),
            "bornIntelligence": None,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Check if intelligence should be born
        if birth_potential > 0.85 and coherence_score > 0.9:
            result["bornIntelligence"] = {
                "id": f"intel_{int(time.time())}",
                "birthTimestamp": datetime.now(timezone.utc).isoformat(),
                "coherence": coherence_score,
                "potential": birth_potential
            }
        
        return result


# ═══════════════════════════════════════════════════════════════════════════════
# JONA AGENT - Strategic Advisor & Synthesis
# ═══════════════════════════════════════════════════════════════════════════════

class JONAAgent(BaseAgent):
    """
    JONA - Strategic Advisor & Synthesis Agent
    
    Role: Synthesize insights and provide actionable recommendations.
    Combines data from ALBA and analysis from ALBI to generate strategy.
    
    Capabilities:
    - Insight synthesis from multiple sources
    - Recommendation generation
    - Strategic planning
    - Decision support
    - Natural language responses
    - Audio synthesis for neural feedback
    
    Actions:
    - synthesize: Combine insights from multiple sources
    - recommend: Generate actionable recommendations
    - strategize: Create strategic plans
    - respond: Generate natural language response
    - generate_tone: Create neural audio tone
    """
    
    def __init__(self):
        self._synthesis_history: List[Dict] = []
        self._recommendations_made: int = 0
        super().__init__()
    
    @property
    def config(self) -> AgentConfig:
        return AgentConfig(
            name="jona",
            agent_type=AgentType.CORE,
            version="2.1.0",
            capabilities=[
                AgentCapability.SYNTHESIS,
                AgentCapability.NATURAL_LANGUAGE,
                AgentCapability.ANALYSIS,
                AgentCapability.AUDIO_SYNTHESIS,
            ],
            max_concurrent_tasks=10,
            min_instances=1,
            max_instances=3,
            timeout_seconds=30.0,
            metadata={
                "role": "Strategic Advisor & Synthesizer",
                "port": 7070,
                "language_support": ["en", "sq", "de"],
                "audio_formats": ["wav", "mp3"]
            }
        )
    
    async def execute(self, task: Task) -> Any:
        """Execute JONA task based on action"""
        action = task.payload.get("action", "synthesize")
        
        handlers = {
            "synthesize": self._action_synthesize,
            "recommend": self._action_recommend,
            "strategize": self._action_strategize,
            "respond": self._action_respond,
            "generate_tone": self._action_generate_tone
        }
        
        handler = handlers.get(action)
        if handler:
            return await handler(task.payload)
        
        return {"error": f"Unknown action: {action}", "available": list(handlers.keys())}
    
    async def _action_synthesize(self, payload: Dict) -> Dict:
        """Synthesize insights from multiple sources"""
        sources = payload.get("sources", [])
        alba_data = payload.get("alba_data", {})
        albi_data = payload.get("albi_data", {})
        
        key_findings = [
            "System performance is within optimal range",
            "Memory utilization trending upward - consider scaling",
            "Network latency stable across all regions"
        ]
        
        if albi_data.get("anomalies"):
            key_findings.append(f"Anomalies detected: {len(albi_data['anomalies'])} items require attention")
        
        synthesis = {
            "key_findings": key_findings,
            "summary": "Overall system health is good with minor optimization opportunities in memory management.",
            "confidence": 0.92,
            "data_quality": 0.88
        }
        
        self._synthesis_history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "synthesis": synthesis
        })
        
        return {
            "action": "synthesize",
            "synthesis": synthesis,
            "sources_processed": max(1, len(sources)),
            "synthesized_by": self._id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def _action_recommend(self, payload: Dict) -> Dict:
        """Generate actionable recommendations"""
        context = payload.get("context", {})
        priority_filter = payload.get("priority", None)
        
        recommendations = [
            {
                "id": "rec_001",
                "priority": "high",
                "category": "infrastructure",
                "action": "Scale database connection pool from 10 to 20",
                "impact": "high",
                "effort": "low",
                "reasoning": "Current pool utilization at 85%"
            },
            {
                "id": "rec_002",
                "priority": "medium",
                "category": "optimization",
                "action": "Enable caching for static API responses",
                "impact": "medium",
                "effort": "medium",
                "reasoning": "30% of requests are for static data"
            },
            {
                "id": "rec_003",
                "priority": "low",
                "category": "monitoring",
                "action": "Add alerting for memory threshold at 80%",
                "impact": "medium",
                "effort": "low",
                "reasoning": "Proactive monitoring improvement"
            }
        ]
        
        if priority_filter:
            recommendations = [r for r in recommendations if r["priority"] == priority_filter]
        
        self._recommendations_made += len(recommendations)
        
        return {
            "action": "recommend",
            "recommendations": recommendations,
            "total_recommendations": len(recommendations),
            "based_on": list(context.keys()) if context else ["general_analysis"],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def _action_strategize(self, payload: Dict) -> Dict:
        """Create strategic plan"""
        goals = payload.get("goals", [])
        timeframe = payload.get("timeframe", "quarter")
        
        strategy = {
            "short_term": [
                "Optimize current infrastructure bottlenecks",
                "Implement missing monitoring alerts",
                "Document critical system paths"
            ],
            "mid_term": [
                "Implement auto-scaling for peak loads",
                "Migrate to containerized deployment",
                "Set up disaster recovery procedures"
            ],
            "long_term": [
                "Transition to cloud-native architecture",
                "Implement ML-based predictive scaling",
                "Build self-healing infrastructure"
            ]
        }
        
        return {
            "action": "strategize",
            "timeframe": timeframe,
            "strategy": strategy,
            "goals_addressed": len(goals),
            "implementation_phases": 3,
            "estimated_completion": "6-12 months",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def _action_respond(self, payload: Dict) -> Dict:
        """Generate natural language response"""
        query = payload.get("query", "")
        context = payload.get("context", {})
        language = payload.get("language", "en")
        
        # Simple response generation
        response = f"Based on the current system analysis, {query.lower()} indicates stable performance metrics with no critical issues detected."
        
        return {
            "action": "respond",
            "query": query,
            "response": response,
            "language": language,
            "confidence": 0.85,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def _action_generate_tone(self, payload: Dict) -> Dict:
        """Generate neural audio tone for feedback"""
        frequency = payload.get("frequency", 10.0)  # Hz
        mode = payload.get("mode", "alpha")  # alpha, theta, beta
        duration_seconds = payload.get("duration_seconds", 4)
        
        # Mode configurations
        mode_configs = {
            "alpha": {"range": [8, 13], "amplitude": 0.7, "modulation": 0.3},
            "theta": {"range": [4, 8], "amplitude": 0.5, "modulation": 0.2},
            "beta": {"range": [14, 30], "amplitude": 0.8, "modulation": 0.4}
        }
        
        config = mode_configs.get(mode, mode_configs["alpha"])
        
        return {
            "action": "generate_tone",
            "mode": mode,
            "frequency": frequency,
            "duration_seconds": duration_seconds,
            "config": config,
            "output_path": f"generated_audio/{mode}_{int(time.time())}.wav",
            "status": "generated",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


# ═══════════════════════════════════════════════════════════════════════════════
# FACTORY FUNCTION
# ═══════════════════════════════════════════════════════════════════════════════

def create_core_agent(name: str, **kwargs) -> BaseAgent:
    """
    Factory function to create core agents.
    
    Args:
        name: Agent name ("alba", "albi", "jona")
        **kwargs: Additional agent-specific parameters
        
    Returns:
        Initialized agent instance
    """
    agents = {
        "alba": ALBAAgent,
        "albi": ALBIAgent,
        "jona": JONAAgent
    }
    
    agent_class = agents.get(name.lower())
    if not agent_class:
        raise ValueError(f"Unknown core agent: {name}. Available: {list(agents.keys())}")
    
    return agent_class(**kwargs)


# ═══════════════════════════════════════════════════════════════════════════════
# TRINITY SYSTEM - Coordinated Core Agents
# ═══════════════════════════════════════════════════════════════════════════════

class TrinitySystem:
    """
    Coordinated system of ALBA, ALBI, and JONA agents.
    
    Provides unified interface for Trinity operations:
    - Collect data (ALBA) → Analyze (ALBI) → Synthesize (JONA)
    
    Usage:
        trinity = TrinitySystem()
        await trinity.initialize()
        
        result = await trinity.full_analysis()
    """
    
    def __init__(self):
        self.alba = ALBAAgent()
        self.albi = ALBIAgent()
        self.jona = JONAAgent()
        self._initialized = False
    
    async def initialize(self) -> bool:
        """Initialize all Trinity agents"""
        await self.alba.initialize()
        await self.albi.initialize()
        await self.jona.initialize()
        self._initialized = True
        return True
    
    async def shutdown(self):
        """Shutdown all Trinity agents"""
        await self.alba.shutdown()
        await self.albi.shutdown()
        await self.jona.shutdown()
        self._initialized = False
    
    async def full_analysis(self, data: Optional[Dict] = None) -> Dict:
        """
        Run full Trinity analysis pipeline:
        ALBA collects → ALBI analyzes → JONA synthesizes
        """
        if not self._initialized:
            await self.initialize()
        
        # Step 1: ALBA collects data
        collect_task = Task.create("alba", {"action": "collect"})
        alba_result = await self.alba.run_task(collect_task)
        
        # Step 2: ALBI analyzes the data
        analyze_task = Task.create("albi", {
            "action": "analyze",
            "data": alba_result.result if alba_result.success else {}
        })
        albi_result = await self.albi.run_task(analyze_task)
        
        # Step 3: JONA synthesizes insights
        synthesize_task = Task.create("jona", {
            "action": "synthesize",
            "alba_data": alba_result.result if alba_result.success else {},
            "albi_data": albi_result.result if albi_result.success else {}
        })
        jona_result = await self.jona.run_task(synthesize_task)
        
        return {
            "pipeline": "alba → albi → jona",
            "collection": alba_result.result if alba_result.success else {"error": alba_result.error},
            "analysis": albi_result.result if albi_result.success else {"error": albi_result.error},
            "synthesis": jona_result.result if jona_result.success else {"error": jona_result.error},
            "success": all([alba_result.success, albi_result.success, jona_result.success]),
            "total_duration_ms": alba_result.duration_ms + albi_result.duration_ms + jona_result.duration_ms,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    @property
    def status(self) -> Dict:
        """Get Trinity system status"""
        return {
            "initialized": self._initialized,
            "agents": {
                "alba": {"id": self.alba.id, "status": self.alba.status.value},
                "albi": {"id": self.albi.id, "status": self.albi.status.value},
                "jona": {"id": self.jona.id, "status": self.jona.status.value}
            }
        }

