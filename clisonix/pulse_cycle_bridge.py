# -*- coding: utf-8 -*-
"""
🔗 Pulse-Cycle Bridge - Lidhja Pulse Balancer ↔ Cycle Engine
==============================================================
Lidh Distributed Pulse Balancer me Cycle Engine për:
- Auto-pause cycles kur node humbet heartbeat
- Shpërndarje e cycles në cluster
- Centralizim i metrics për Grafana
- Health-aware cycle scheduling

Business: Ledjan Ahmati - WEB8euroweb GmbH
"""

import asyncio
import json
import time
import threading
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from enum import Enum
import httpx

logger = logging.getLogger("kloud.pulse_bridge")


class PulseState(Enum):
    """Gjendja e pulse/heartbeat"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    DEAD = "dead"


@dataclass
class PulseMetrics:
    """Metriks nga Pulse Balancer"""
    node_id: str
    node_name: str
    cpu: float = 0.0
    mem: float = 0.0
    disk: float = 0.0
    net_sent_MB: float = 0.0
    net_recv_MB: float = 0.0
    procs: int = 0
    uptime_sec: int = 0
    last_seen: str = ""
    is_leader: bool = False
    peer_count: int = 0
    state: PulseState = PulseState.HEALTHY
    capacity_score: float = 0.0
    
    def to_prometheus(self) -> str:
        """Eksporton si Prometheus metrics"""
        lines = [
            f'kloud_pulse_cpu{{node="{self.node_name}"}} {self.cpu}',
            f'kloud_pulse_mem{{node="{self.node_name}"}} {self.mem}',
            f'kloud_pulse_disk{{node="{self.node_name}"}} {self.disk}',
            f'kloud_pulse_net_sent_mb{{node="{self.node_name}"}} {self.net_sent_MB}',
            f'kloud_pulse_net_recv_mb{{node="{self.node_name}"}} {self.net_recv_MB}',
            f'kloud_pulse_procs{{node="{self.node_name}"}} {self.procs}',
            f'kloud_pulse_uptime_sec{{node="{self.node_name}"}} {self.uptime_sec}',
            f'kloud_pulse_is_leader{{node="{self.node_name}"}} {1 if self.is_leader else 0}',
            f'kloud_pulse_peer_count{{node="{self.node_name}"}} {self.peer_count}',
            f'kloud_pulse_capacity_score{{node="{self.node_name}"}} {self.capacity_score}',
            f'kloud_pulse_state{{node="{self.node_name}",state="{self.state.value}"}} 1',
        ]
        return "\n".join(lines)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "node_name": self.node_name,
            "cpu": self.cpu,
            "mem": self.mem,
            "disk": self.disk,
            "net_sent_MB": self.net_sent_MB,
            "net_recv_MB": self.net_recv_MB,
            "procs": self.procs,
            "uptime_sec": self.uptime_sec,
            "last_seen": self.last_seen,
            "is_leader": self.is_leader,
            "peer_count": self.peer_count,
            "state": self.state.value,
            "capacity_score": self.capacity_score,
        }


class PulseCycleBridge:
    """
    🔗 Bridge midis Pulse Balancer dhe Cycle Engine
    
    Përgjegjësitë:
    - Monitor pulse status nga Balancer API
    - Auto-pause cycles kur pulse degradohet
    - Resume cycles kur pulse rikthehet
    - Shpërndaj cycles nëpër cluster nodes
    - Mblidh metrics për Grafana
    """
    
    def __init__(
        self,
        balancer_url: str = "http://localhost:8091",
        check_interval: float = 5.0,
        pause_threshold: float = 85.0,  # CPU/MEM > 85% = pause
        resume_threshold: float = 60.0,  # CPU/MEM < 60% = resume
        dead_timeout: float = 30.0,      # Sekonda pa heartbeat = dead
    ):
        self.balancer_url = balancer_url.rstrip("/")
        self.check_interval = check_interval
        self.pause_threshold = pause_threshold
        self.resume_threshold = resume_threshold
        self.dead_timeout = dead_timeout
        
        # State
        self._running = False
        self._lock = threading.Lock()
        self._pulse_metrics: Optional[PulseMetrics] = None
        self._last_healthy_time: float = time.time()
        
        # Callbacks
        self._on_pause_callbacks: List[Callable[[PulseMetrics], None]] = []
        self._on_resume_callbacks: List[Callable[[PulseMetrics], None]] = []
        self._on_dead_callbacks: List[Callable[[PulseMetrics], None]] = []
        
        # Cycle Engine reference (set externally)
        self._cycle_engine = None
        
        # Metrics history (për Grafana)
        self._metrics_history: List[PulseMetrics] = []
        self._max_history = 1000
        
        # Paused cycles tracking
        self._paused_by_pulse: List[str] = []
    
    def set_cycle_engine(self, engine):
        """Lidh me Cycle Engine"""
        self._cycle_engine = engine
        logger.info("✓ Cycle Engine connected to Pulse Bridge")
    
    def on_pause(self, callback: Callable[[PulseMetrics], None]):
        """Regjistro callback për pause event"""
        self._on_pause_callbacks.append(callback)
    
    def on_resume(self, callback: Callable[[PulseMetrics], None]):
        """Regjistro callback për resume event"""
        self._on_resume_callbacks.append(callback)
    
    def on_dead(self, callback: Callable[[PulseMetrics], None]):
        """Regjistro callback për dead event"""
        self._on_dead_callbacks.append(callback)
    
    async def fetch_pulse_status(self) -> Optional[PulseMetrics]:
        """Merr statusin aktual nga Pulse Balancer"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self.balancer_url}/balancer/status")
                if resp.status_code != 200:
                    return None
                
                data = resp.json()
                self_info = data.get("self", {})
                metrics = self_info.get("metrics", {})
                
                # Calculate state
                cpu = metrics.get("cpu", 0)
                mem = metrics.get("mem", 0)
                capacity_score = 0.6 * cpu + 0.35 * mem + 0.05 * metrics.get("disk", 0)
                
                if capacity_score > self.pause_threshold:
                    state = PulseState.CRITICAL
                elif capacity_score > self.resume_threshold:
                    state = PulseState.DEGRADED
                else:
                    state = PulseState.HEALTHY
                
                pulse = PulseMetrics(
                    node_id=self_info.get("node_id", "unknown"),
                    node_name=self_info.get("node_name", "unknown"),
                    cpu=cpu,
                    mem=mem,
                    disk=metrics.get("disk", 0),
                    net_sent_MB=metrics.get("net_sent_MB", 0),
                    net_recv_MB=metrics.get("net_recv_MB", 0),
                    procs=metrics.get("procs", 0),
                    uptime_sec=metrics.get("uptime_sec", 0),
                    last_seen=data.get("now", ""),
                    is_leader=data.get("leader_id") == self_info.get("node_id"),
                    peer_count=len(data.get("peers", [])),
                    state=state,
                    capacity_score=round(capacity_score, 2),
                )
                return pulse
                
        except Exception as e:
            logger.warning(f"Failed to fetch pulse status: {e}")
            return None
    
    async def _check_and_react(self):
        """Kontrollo pulse dhe reago"""
        pulse = await self.fetch_pulse_status()
        
        with self._lock:
            old_state = self._pulse_metrics.state if self._pulse_metrics else PulseState.HEALTHY
            
            if pulse is None:
                # Nuk kemi lidhje me balancer
                if time.time() - self._last_healthy_time > self.dead_timeout:
                    if self._pulse_metrics:
                        self._pulse_metrics.state = PulseState.DEAD
                    # Fire dead callbacks
                    if old_state != PulseState.DEAD:
                        await self._handle_dead()
                return
            
            self._pulse_metrics = pulse
            self._metrics_history.append(pulse)
            if len(self._metrics_history) > self._max_history:
                self._metrics_history.pop(0)
            
            # State transitions
            if pulse.state == PulseState.HEALTHY:
                self._last_healthy_time = time.time()
                
                # Resume if was paused
                if old_state in (PulseState.CRITICAL, PulseState.DEAD):
                    await self._handle_resume(pulse)
            
            elif pulse.state == PulseState.CRITICAL:
                if old_state == PulseState.HEALTHY:
                    await self._handle_pause(pulse)
    
    async def _handle_pause(self, pulse: PulseMetrics):
        """Ndal cycles kur pulse është kritike"""
        logger.warning(f"⚠️ PULSE CRITICAL - Pausing cycles (score: {pulse.capacity_score})")
        
        # Pause all active cycles
        if self._cycle_engine:
            for cycle_id, cycle in self._cycle_engine.cycles.items():
                if cycle.status.value == "active":
                    await self._cycle_engine.pause_cycle(cycle_id)
                    self._paused_by_pulse.append(cycle_id)
                    logger.info(f"  ⏸️ Paused: {cycle_id}")
        
        # Fire callbacks
        for cb in self._on_pause_callbacks:
            try:
                cb(pulse)
            except Exception as e:
                logger.error(f"Pause callback error: {e}")
    
    async def _handle_resume(self, pulse: PulseMetrics):
        """Rifillo cycles kur pulse rikthehet"""
        logger.info(f"✅ PULSE RECOVERED - Resuming cycles (score: {pulse.capacity_score})")
        
        # Resume paused cycles
        if self._cycle_engine:
            for cycle_id in self._paused_by_pulse:
                try:
                    await self._cycle_engine.resume_cycle(cycle_id)
                    logger.info(f"  ▶️ Resumed: {cycle_id}")
                except Exception as e:
                    logger.error(f"Failed to resume {cycle_id}: {e}")
            self._paused_by_pulse.clear()
        
        # Fire callbacks
        for cb in self._on_resume_callbacks:
            try:
                cb(pulse)
            except Exception as e:
                logger.error(f"Resume callback error: {e}")
    
    async def _handle_dead(self):
        """Reago kur pulse është dead"""
        logger.error("💀 PULSE DEAD - No heartbeat received")
        
        pulse = self._pulse_metrics
        
        # Fire callbacks
        for cb in self._on_dead_callbacks:
            try:
                cb(pulse)
            except Exception as e:
                logger.error(f"Dead callback error: {e}")
    
    async def run(self):
        """Nis bridge monitoring loop"""
        self._running = True
        logger.info(f"🔗 Pulse-Cycle Bridge started (checking every {self.check_interval}s)")
        
        while self._running:
            try:
                await self._check_and_react()
            except Exception as e:
                logger.exception(f"Bridge error: {e}")
            
            await asyncio.sleep(self.check_interval)
    
    def stop(self):
        """Ndal bridge"""
        self._running = False
        logger.info("🔗 Pulse-Cycle Bridge stopped")
    
    def get_current_metrics(self) -> Optional[PulseMetrics]:
        """Merr metrics aktuale"""
        with self._lock:
            return self._pulse_metrics
    
    def get_prometheus_metrics(self) -> str:
        """Eksporto metrics për Prometheus/Grafana"""
        with self._lock:
            if self._pulse_metrics:
                return self._pulse_metrics.to_prometheus()
            return "# No pulse metrics available\n"
    
    def get_grafana_json(self) -> Dict[str, Any]:
        """Eksporto metrics si JSON për Grafana"""
        with self._lock:
            return {
                "current": self._pulse_metrics.to_dict() if self._pulse_metrics else None,
                "history_count": len(self._metrics_history),
                "paused_cycles": len(self._paused_by_pulse),
                "paused_cycle_ids": self._paused_by_pulse,
            }


# ============================================================
# Prometheus Metrics Exporter (për Grafana)
# ============================================================

class PrometheusMetricsExporter:
    """
    📊 Eksportues i metrics për Prometheus/Grafana
    
    Endpoints:
    - /metrics - Prometheus format
    - /metrics/json - JSON format
    """
    
    def __init__(self, bridge: PulseCycleBridge, cycle_engine=None):
        self.bridge = bridge
        self.cycle_engine = cycle_engine
    
    def get_all_metrics(self) -> str:
        """Gjenero të gjitha metrics në Prometheus format"""
        lines = []
        
        # Pulse metrics
        pulse = self.bridge.get_current_metrics()
        if pulse:
            lines.append("# HELP kloud_pulse_cpu CPU usage percentage")
            lines.append("# TYPE kloud_pulse_cpu gauge")
            lines.append(pulse.to_prometheus())
        
        # Cycle metrics
        if self.cycle_engine:
            lines.append("")
            lines.append("# HELP kloud_cycles_total Total cycles created")
            lines.append("# TYPE kloud_cycles_total counter")
            lines.append(f'kloud_cycles_total {self.cycle_engine.metrics.get("total_cycles", 0)}')
            
            lines.append("# HELP kloud_cycles_active Currently active cycles")
            lines.append("# TYPE kloud_cycles_active gauge")
            lines.append(f'kloud_cycles_active {self.cycle_engine.metrics.get("active_cycles", 0)}')
            
            lines.append("# HELP kloud_cycles_completed Completed cycles")
            lines.append("# TYPE kloud_cycles_completed counter")
            lines.append(f'kloud_cycles_completed {self.cycle_engine.metrics.get("completed_cycles", 0)}')
            
            lines.append("# HELP kloud_cycles_blocked Blocked cycles")
            lines.append("# TYPE kloud_cycles_blocked gauge")
            lines.append(f'kloud_cycles_blocked {self.cycle_engine.metrics.get("blocked_cycles", 0)}')
            
            lines.append("# HELP kloud_gaps_filled Knowledge gaps filled")
            lines.append("# TYPE kloud_gaps_filled counter")
            lines.append(f'kloud_gaps_filled {self.cycle_engine.metrics.get("gaps_filled", 0)}')
            
            # Per-cycle status
            lines.append("")
            lines.append("# HELP kloud_cycle_status Cycle status (1=active)")
            lines.append("# TYPE kloud_cycle_status gauge")
            for cid, cycle in self.cycle_engine.cycles.items():
                status_val = 1 if cycle.status.value == "active" else 0
                lines.append(f'kloud_cycle_status{{cycle="{cid}",domain="{cycle.domain}",task="{cycle.task}"}} {status_val}')
        
        # Bridge status
        lines.append("")
        lines.append("# HELP kloud_bridge_paused_cycles Cycles paused by pulse bridge")
        lines.append("# TYPE kloud_bridge_paused_cycles gauge")
        lines.append(f'kloud_bridge_paused_cycles {len(self.bridge._paused_by_pulse)}')
        
        return "\n".join(lines)


# ============================================================
# Distributed Cycle Scheduler
# ============================================================

class DistributedCycleScheduler:
    """
    🌐 Shpërndarje e cycles nëpër cluster nodes
    
    Përdor Pulse Balancer për të zgjedhur node-in optimal
    për çdo cycle bazuar në load dhe kapacitet.
    """
    
    def __init__(self, balancer_url: str = "http://localhost:8091"):
        self.balancer_url = balancer_url.rstrip("/")
    
    async def schedule_cycle(self, cycle_id: str, weight: float = 1.0) -> Dict[str, Any]:
        """Zgjidh node-in optimal për një cycle"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.post(
                    f"{self.balancer_url}/balancer/request",
                    json={"work_id": cycle_id, "weight": weight}
                )
                if resp.status_code == 200:
                    data = resp.json()
                    return {
                        "ok": True,
                        "decision": data.get("decision"),
                        "target": data.get("target"),
                        "leader_id": data.get("leader_id"),
                        "self_score": data.get("self_score"),
                    }
                elif resp.status_code == 429:
                    return {"ok": False, "error": "rate_limited"}
                else:
                    return {"ok": False, "error": f"status_{resp.status_code}"}
        except Exception as e:
            return {"ok": False, "error": str(e)}
    
    async def report_feedback(self, node_id: str, success: bool) -> bool:
        """Raporto rezultatin e cycle execution"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.post(
                    f"{self.balancer_url}/balancer/feedback",
                    json={"node_id": node_id, "success": success}
                )
                return resp.status_code == 200
        except:
            return False


# ============================================================
# Integration Helper
# ============================================================

def create_integrated_system(
    balancer_url: str = "http://localhost:8091",
    check_interval: float = 5.0,
) -> tuple:
    """
    Krijon sistem të integruar Pulse + Cycles
    
    Returns:
        (bridge, exporter, scheduler)
    """
    bridge = PulseCycleBridge(
        balancer_url=balancer_url,
        check_interval=check_interval,
    )
    
    exporter = PrometheusMetricsExporter(bridge)
    scheduler = DistributedCycleScheduler(balancer_url)
    
    return bridge, exporter, scheduler


# ============================================================
# CLI / Standalone mode
# ============================================================

if __name__ == "__main__":
    import sys
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
    )
    
    balancer_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8091"
    
    bridge = PulseCycleBridge(balancer_url=balancer_url)
    
    # Demo callbacks
    bridge.on_pause(lambda p: print(f"🔴 PAUSED due to: {p.state.value}"))
    bridge.on_resume(lambda p: print(f"🟢 RESUMED: {p.state.value}"))
    bridge.on_dead(lambda p: print(f"💀 DEAD!"))
    
    print(f"🔗 Starting Pulse-Cycle Bridge → {balancer_url}")
    print("   Press Ctrl+C to stop\n")
    
    try:
        asyncio.run(bridge.run())
    except KeyboardInterrupt:
        bridge.stop()
        print("\n✓ Bridge stopped")

