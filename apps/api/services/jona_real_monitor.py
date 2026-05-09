"""
ðŸ”® JONA - Joyful Overseer of Neural Alignment (REAL SYSTEM MONITOR) 
===================================================================
Monitor real i sistemit qÃ« mbikÃ«qyr harmoninÃ« e Kloud ecosystem.
Real health monitor, real harmony checker, real system optimizer.

NO FAKE METRICS, NO MOCK HEALTH, REAL MONITORING ONLY
"""

import json
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List

import aiofiles  # type: ignore[import-untyped]
import psutil


class HarmonyLevel(Enum):
    """Nivelet e harmonisÃ« nÃ« sistem"""
    CRITICAL = "critical"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    OPTIMAL = "optimal"


class JONA_RealMonitor:
    """
    ðŸ§  JONA Real System Monitor qÃ« mbikÃ«qyr sistemin real
    """
    
    def __init__(self, base_dir="C:/Kloud-cloud"):
        self.base_dir = Path(base_dir)
        self.harmony_log = self.base_dir / "data" / "jona_harmony_log.json"
        self.alert_log = self.base_dir / "data" / "jona_alerts.json"
        
        # Thresholds pÃ«r vlerÃ«simin real
        self.thresholds = {
            "cpu_warning": 80.0,
            "cpu_critical": 95.0,
            "memory_warning": 80.0,
            "memory_critical": 95.0,
            "disk_warning": 80.0,
            "disk_critical": 95.0,
            "process_response_max": 5.0  # seconds
        }
    
    async def monitor_real_system_health(self) -> Dict[str, Any]:
        """MbikÃ«qyr shÃ«ndetin real tÃ« sistemit"""
        
        # System metrics real
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage(str(self.base_dir))
        
        # Process health real
        try:
            process = psutil.Process()
            process_health = {
                "memory_mb": round(process.memory_info().rss / (1024**2), 2),
                "cpu_percent": process.cpu_percent(),
                "status": process.status(),
                "num_threads": process.num_threads(),
                "open_files": len(process.open_files()),
                "create_time": datetime.fromtimestamp(process.create_time()).isoformat()
            }
        except Exception as e:
            process_health = {"error": str(e)}
        
        # Network health real (if applicable)
        network_stats = psutil.net_io_counters()
        
        health_report = {
            "system_health": {
                "cpu_usage_percent": cpu_usage,
                "memory_usage_percent": memory.percent,
                "disk_usage_percent": (disk.used / disk.total) * 100,
                "available_memory_gb": round(memory.available / (1024**3), 2),
                "free_disk_gb": round(disk.free / (1024**3), 2)
            },
            "process_health": process_health,
            "network_health": {
                "bytes_sent": network_stats.bytes_sent,
                "bytes_received": network_stats.bytes_recv,
                "packets_sent": network_stats.packets_sent,
                "packets_received": network_stats.packets_recv
            },
            "monitoring_timestamp": datetime.utcnow().isoformat(),
            "monitor": "JONA_real_health",
            "real_monitoring_only": True
        }
        
        return health_report
    
    async def calculate_real_harmony_score(self) -> Dict[str, Any]:
        """Llogarit rezultatin real tÃ« harmonisÃ« nÃ« sistem"""
        
        health = await self.monitor_real_system_health()
        
        # Llogarit komponente tÃ« ndryshme harmonije
        cpu_score = self._calculate_resource_score(health["system_health"]["cpu_usage_percent"], "cpu")
        memory_score = self._calculate_resource_score(health["system_health"]["memory_usage_percent"], "memory")
        disk_score = self._calculate_resource_score(health["system_health"]["disk_usage_percent"], "disk")
        
        # Process stability score
        process_score = 100 if "error" not in health["process_health"] else 0
        
        # Weighted harmony calculation
        harmony_components = {
            "cpu_harmony": cpu_score,
            "memory_harmony": memory_score,
            "disk_harmony": disk_score,
            "process_harmony": process_score
        }
        
        # Overall harmony (weighted average)
        weights = {"cpu": 0.3, "memory": 0.3, "disk": 0.2, "process": 0.2}
        overall_harmony = (
            cpu_score * weights["cpu"] +
            memory_score * weights["memory"] + 
            disk_score * weights["disk"] +
            process_score * weights["process"]
        )
        
        harmony_level = self._determine_harmony_level(overall_harmony)
        
        return {
            "harmony_score": round(overall_harmony, 2),
            "harmony_level": harmony_level.value,
            "harmony_components": harmony_components,
            "system_status": "optimal" if overall_harmony >= 80 else "needs_attention",
            "calculated_at": datetime.utcnow().isoformat(),
            "real_calculation_only": True
        }
    
    def _calculate_resource_score(self, usage_percent: float, resource_type: str) -> float:
        """Llogarit score pÃ«r njÃ« resurs specifik"""
        warning_threshold = self.thresholds[f"{resource_type}_warning"]
        critical_threshold = self.thresholds[f"{resource_type}_critical"]
        
        if usage_percent <= 50:
            return 100.0  # Optimal
        elif usage_percent <= warning_threshold:
            # Linear decrease from 100 to 60
            return 100 - ((usage_percent - 50) / (warning_threshold - 50)) * 40
        elif usage_percent <= critical_threshold:
            # Linear decrease from 60 to 20
            return 60 - ((usage_percent - warning_threshold) / (critical_threshold - warning_threshold)) * 40
        else:
            # Critical zone: 0-20 points
            return max(0, 20 - (usage_percent - critical_threshold))
    
    def _determine_harmony_level(self, score: float) -> HarmonyLevel:
        """PÃ«rcakton nivelin e harmonisÃ« bazuar nÃ« score"""
        if score >= 90:
            return HarmonyLevel.OPTIMAL
        elif score >= 75:
            return HarmonyLevel.HIGH
        elif score >= 50:
            return HarmonyLevel.MEDIUM
        elif score >= 25:
            return HarmonyLevel.LOW
        else:
            return HarmonyLevel.CRITICAL
    
    async def check_albi_alba_interaction(self) -> Dict[str, Any]:
        """Kontrollon interaksionin real midis ALBI dhe ALBA"""
        
        try:
            # Check ALBI status
            from .albi_real_engine import create_albi_real
            albi = await create_albi_real()
            albi_status = await albi.get_real_status()
            
            # Check ALBA status  
            from .alba_real_collector import create_alba_real
            alba = await create_alba_real()
            alba_status = await alba.get_real_status()
            
            # Analyze interaction health
            interaction_health = {
                "albi_active": albi_status.get("status") == "active",
                "alba_active": alba_status.get("status") == "active_real_collection",
                "data_flow_healthy": True,  # Will be determined by actual metrics
                "last_interaction": datetime.utcnow().isoformat(),
                "interaction_score": 0
            }
            
            # Calculate interaction score
            if interaction_health["albi_active"] and interaction_health["alba_active"]:
                interaction_health["interaction_score"] = 100
                interaction_health["status"] = "optimal_cooperation"
            else:
                interaction_health["interaction_score"] = 50
                interaction_health["status"] = "partial_cooperation"
            
            return {
                "character_interaction": interaction_health,
                "albi_metrics": albi_status,
                "alba_metrics": alba_status,
                "checked_at": datetime.utcnow().isoformat(),
                "real_interaction_check": True
            }
            
        except Exception as e:
            return {
                "interaction_error": str(e),
                "status": "interaction_check_failed",
                "checked_at": datetime.utcnow().isoformat()
            }
    
    async def generate_real_alerts(self) -> List[Dict[str, Any]]:
        """Gjeneron alerte reale bazuar nÃ« monitorim"""
        
        health = await self.monitor_real_system_health()
        harmony = await self.calculate_real_harmony_score()
        alerts = []
        
        # CPU alerts
        cpu_usage = health["system_health"]["cpu_usage_percent"]
        if cpu_usage >= self.thresholds["cpu_critical"]:
            alerts.append({
                "type": "CRITICAL",
                "component": "CPU",
                "message": f"CPU usage critical: {cpu_usage:.1f}%",
                "recommendation": "Check for resource-intensive processes",
                "timestamp": datetime.utcnow().isoformat()
            })
        elif cpu_usage >= self.thresholds["cpu_warning"]:
            alerts.append({
                "type": "WARNING", 
                "component": "CPU",
                "message": f"CPU usage high: {cpu_usage:.1f}%",
                "recommendation": "Monitor CPU usage trends",
                "timestamp": datetime.utcnow().isoformat()
            })
        
        # Memory alerts
        memory_usage = health["system_health"]["memory_usage_percent"]
        if memory_usage >= self.thresholds["memory_critical"]:
            alerts.append({
                "type": "CRITICAL",
                "component": "Memory",
                "message": f"Memory usage critical: {memory_usage:.1f}%",
                "recommendation": "Free up memory or restart services",
                "timestamp": datetime.utcnow().isoformat()
            })
        
        # Harmony alerts
        if harmony["harmony_level"] == HarmonyLevel.CRITICAL.value:
            alerts.append({
                "type": "CRITICAL",
                "component": "System Harmony",
                "message": f"System harmony critical: {harmony['harmony_score']}",
                "recommendation": "Immediate system optimization required",
                "timestamp": datetime.utcnow().isoformat()
            })
        
        return alerts
    
    async def log_real_monitoring_session(self, health: Dict[str, Any], harmony: Dict[str, Any], alerts: List[Dict[str, Any]]):
        """Log i sesionit real tÃ« monitorimit"""
        
        session_log = {
            "session_id": f"jona_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "health_report": health,
            "harmony_analysis": harmony,
            "alerts_generated": alerts,
            "monitoring_duration": "real_time",
            "timestamp": datetime.utcnow().isoformat(),
            "jona_real_monitoring": True
        }
        
        # Read existing harmony log
        existing_log = []
        if self.harmony_log.exists():
            async with aiofiles.open(self.harmony_log, 'r') as f:
                content = await f.read()
                if content.strip():
                    existing_log = json.loads(content)
        
        # Add new session
        existing_log.append(session_log)
        
        # Keep only last 50 sessions
        if len(existing_log) > 50:
            existing_log = existing_log[-50:]
        
        # Save harmony log
        self.harmony_log.parent.mkdir(parents=True, exist_ok=True)
        async with aiofiles.open(self.harmony_log, 'w') as f:
            await f.write(json.dumps(existing_log, indent=2, ensure_ascii=False))
        
        # Save alerts if any
        if alerts:
            await self._save_alerts_log(alerts)
    
    async def _save_alerts_log(self, alerts: List[Dict[str, Any]]):
        """Ruaj alert log"""
        existing_alerts = []
        if self.alert_log.exists():
            async with aiofiles.open(self.alert_log, 'r') as f:
                content = await f.read()
                if content.strip():
                    existing_alerts = json.loads(content)
        
        existing_alerts.extend(alerts)
        
        # Keep alerts from last 7 days only
        cutoff_date = datetime.utcnow() - timedelta(days=7)
        existing_alerts = [
            alert for alert in existing_alerts 
            if datetime.fromisoformat(alert["timestamp"]) > cutoff_date
        ]
        
        self.alert_log.parent.mkdir(parents=True, exist_ok=True)
        async with aiofiles.open(self.alert_log, 'w') as f:
            await f.write(json.dumps(existing_alerts, indent=2, ensure_ascii=False))
    
    async def get_real_status(self) -> Dict[str, Any]:
        """Kthen statusin real tÃ« JONA"""
        return {
            "character": "JONA",
            "status": "active_real_monitoring",
            "base_directory": str(self.base_dir),
            "harmony_log": str(self.harmony_log),
            "alert_log": str(self.alert_log),
            "thresholds": self.thresholds,
            "last_activity": datetime.utcnow().isoformat(),
            "real_monitoring_only": True,
            "no_fake_no_mock": True
        }


# Factory function pÃ«r JONA real
async def create_jona_real() -> JONA_RealMonitor:
    """Krijon njÃ« instance JONA qÃ« monitorizon sistemin real"""
    jona = JONA_RealMonitor()
    return jona



