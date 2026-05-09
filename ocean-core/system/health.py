#!/usr/bin/env python3
"""
SYSTEM PIPELINE - Health, Admin, Logs
=====================================
Sistemi nervor i Kloud Cloud.
"""

import logging
import os
import platform
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import psutil

logger = logging.getLogger("SystemPipeline")


@dataclass
class HealthStatus:
    """Statusi i shëndetit të sistemit"""
    status: str  # healthy, degraded, unhealthy
    uptime: float
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    services: Dict[str, str]
    timestamp: str


@dataclass
class AdminCommand:
    """Një komandë administrative"""
    command: str
    args: Dict[str, Any]
    executed_by: str
    timestamp: float
    result: Optional[str] = None
    success: bool = False


class SystemPipeline:
    """Pipeline për operacione sistemi"""
    
    def __init__(self):
        self.start_time = time.time()
        self.admin_log: List[AdminCommand] = []
        self.allowed_admins = {"admin", "ledjan", "root"}
        logger.info("✅ SystemPipeline initialized")
    
    @property
    def uptime(self) -> float:
        """Koha që sistemi ka qenë aktiv"""
        return time.time() - self.start_time
    
    def health_check(self) -> HealthStatus:
        """Kontrollo shëndetin e sistemit"""
        try:
            cpu = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory().percent
            disk = psutil.disk_usage('/').percent
        except Exception:
            cpu = memory = disk = 0.0
        
        # Determine status
        if cpu > 90 or memory > 90 or disk > 95:
            status = "unhealthy"
        elif cpu > 70 or memory > 70 or disk > 85:
            status = "degraded"
        else:
            status = "healthy"
        
        return HealthStatus(
            status=status,
            uptime=self.uptime,
            cpu_percent=cpu,
            memory_percent=memory,
            disk_percent=disk,
            services=self._check_services(),
            timestamp=datetime.utcnow().isoformat()
        )
    
    def _check_services(self) -> Dict[str, str]:
        """Kontrollo statusin e shërbimeve"""
        services = {
            "ocean-core": "unknown",
            "ollama": "unknown",
            "redis": "unknown",
            "postgres": "unknown"
        }
        
        # Simple port checks
        import socket
        
        port_map = {
            "ocean-core": 8030,
            "ollama": 11434,
            "redis": 6379,
            "postgres": 5432
        }
        
        for service, port in port_map.items():
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.5)
                result = sock.connect_ex(('localhost', port))
                sock.close()
                services[service] = "up" if result == 0 else "down"
            except Exception:
                services[service] = "error"
        
        return services
    
    def execute_admin_command(
        self, 
        command: str, 
        args: Dict[str, Any],
        executed_by: str
    ) -> AdminCommand:
        """Ekzekuto një komandë administrative"""
        cmd = AdminCommand(
            command=command,
            args=args,
            executed_by=executed_by,
            timestamp=time.time()
        )
        
        # Check authorization
        if executed_by not in self.allowed_admins:
            cmd.result = "Unauthorized"
            cmd.success = False
            self.admin_log.append(cmd)
            return cmd
        
        # Execute command
        try:
            if command == "clear_cache":
                cmd.result = "Cache cleared"
                cmd.success = True
            elif command == "restart_service":
                service = args.get("service", "unknown")
                cmd.result = f"Restart requested for {service}"
                cmd.success = True
            elif command == "get_logs":
                lines = args.get("lines", 100)
                cmd.result = f"Last {lines} log lines"
                cmd.success = True
            elif command == "system_info":
                cmd.result = self._get_system_info()
                cmd.success = True
            else:
                cmd.result = f"Unknown command: {command}"
                cmd.success = False
        except Exception as e:
            cmd.result = str(e)
            cmd.success = False
        
        self.admin_log.append(cmd)
        
        # Keep only last 1000 commands
        if len(self.admin_log) > 1000:
            self.admin_log = self.admin_log[-1000:]
        
        return cmd
    
    def _get_system_info(self) -> str:
        """Merr informacion të sistemit"""
        info = {
            "platform": platform.platform(),
            "python": platform.python_version(),
            "cpu_count": psutil.cpu_count(),
            "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "uptime_hours": round(self.uptime / 3600, 2)
        }
        return str(info)
    
    def get_admin_log(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Merr logun e komandave administrative"""
        return [
            {
                "command": cmd.command,
                "executed_by": cmd.executed_by,
                "timestamp": datetime.fromtimestamp(cmd.timestamp).isoformat(),
                "success": cmd.success,
                "result": cmd.result[:100] if cmd.result else None
            }
            for cmd in self.admin_log[-limit:]
        ]
    
    def get_metrics(self) -> Dict[str, Any]:
        """Merr metrikat e sistemit"""
        health = self.health_check()
        return {
            "status": health.status,
            "uptime_seconds": self.uptime,
            "cpu_percent": health.cpu_percent,
            "memory_percent": health.memory_percent,
            "disk_percent": health.disk_percent,
            "services": health.services,
            "admin_commands_today": len([
                c for c in self.admin_log 
                if c.timestamp > time.time() - 86400
            ])
        }


# Singleton
_pipeline: Optional[SystemPipeline] = None


def get_system_pipeline() -> SystemPipeline:
    """Merr instancën singleton"""
    global _pipeline
    if _pipeline is None:
        _pipeline = SystemPipeline()
    return _pipeline

