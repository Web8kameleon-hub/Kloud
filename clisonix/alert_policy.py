# -*- coding: utf-8 -*-
"""
🔔 KLOUD ALERT POLICY
=========================
Politikat e alarmeve për Slack - pa spam, pa panik kot.

CRITICAL → dërgohet GJITHMONË
WARNING  → 1 herë / 30 minuta (cooldown)
INFO     → Daily digest ose disabled

Business: Ledjan Ahmati - WEB8euroweb GmbH
"""

import json
import time
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

logger = logging.getLogger("kloud.alert_policy")


class AlertLevel(Enum):
    """Nivelet e alarmeve"""
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"
    DEBUG = "debug"


class AlertCategory(Enum):
    """Kategoritë e alarmeve"""
    SERVICE_DOWN = "service_down"
    CPU_HIGH = "cpu_high"
    MEMORY_HIGH = "memory_high"
    DISK_HIGH = "disk_high"
    AUTO_LEARNING = "auto_learning"
    SECURITY = "security"
    QUEUE_BACKLOG = "queue_backlog"
    PERFORMANCE = "performance"
    BILLING = "billing"
    DEPLOYMENT = "deployment"


@dataclass
class AlertPolicy:
    """Politika për një nivel alarmi"""
    level: AlertLevel
    send: bool = True
    cooldown_sec: int = 0  # 0 = pa cooldown
    digest: Optional[str] = None  # "daily", "hourly", None
    channels: list = field(default_factory=lambda: ["slack"])


@dataclass
class Alert:
    """Një alarm individual"""
    level: AlertLevel
    category: AlertCategory
    title: str
    message: str
    service: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "level": self.level.value,
            "category": self.category.value,
            "title": self.title,
            "message": self.message,
            "service": self.service,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
        }


# ═══════════════════════════════════════════════════════════════════
# DEFAULT POLICIES
# ═══════════════════════════════════════════════════════════════════

DEFAULT_POLICIES: Dict[AlertLevel, AlertPolicy] = {
    AlertLevel.CRITICAL: AlertPolicy(
        level=AlertLevel.CRITICAL,
        send=True,
        cooldown_sec=0,  # Dërgo GJITHMONË
    ),
    AlertLevel.WARNING: AlertPolicy(
        level=AlertLevel.WARNING,
        send=True,
        cooldown_sec=1800,  # 30 minuta cooldown
    ),
    AlertLevel.INFO: AlertPolicy(
        level=AlertLevel.INFO,
        send=False,
        digest="daily",  # Daily digest
    ),
    AlertLevel.DEBUG: AlertPolicy(
        level=AlertLevel.DEBUG,
        send=False,
    ),
}


# ═══════════════════════════════════════════════════════════════════
# ALERT MANAGER
# ═══════════════════════════════════════════════════════════════════

class AlertManager:
    """
    Menaxhon alarmet me politika dhe throttling.
    
    Përdorim:
        manager = AlertManager()
        manager.on_send(my_slack_sender)
        
        alert = Alert(
            level=AlertLevel.CRITICAL,
            category=AlertCategory.SERVICE_DOWN,
            title="ALBA DOWN",
            message="ALBA service is not responding"
        )
        
        manager.process(alert)  # Dërgohet menjëherë
    """
    
    def __init__(self, policies: Optional[Dict[AlertLevel, AlertPolicy]] = None):
        self.policies = policies or DEFAULT_POLICIES
        self._last_sent: Dict[str, float] = {}  # category:level -> timestamp
        self._digest_queue: list = []
        self._send_handlers: list = []
        self._enabled = True
    
    def on_send(self, handler: Callable[[Alert], bool]):
        """Regjistro handler për dërgim (p.sh. Slack)"""
        self._send_handlers.append(handler)
    
    def set_enabled(self, enabled: bool):
        """Aktivizo/deaktivizo alarmet"""
        self._enabled = enabled
        logger.info(f"AlertManager {'enabled' if enabled else 'disabled'}")
    
    def should_send(self, alert: Alert) -> bool:
        """Vendos nëse alarmi duhet të dërgohet"""
        if not self._enabled:
            return False
        
        policy = self.policies.get(alert.level)
        if not policy or not policy.send:
            return False
        
        # CRITICAL → gjithmonë
        if alert.level == AlertLevel.CRITICAL:
            return True
        
        # Check cooldown
        key = f"{alert.category.value}:{alert.level.value}"
        last = self._last_sent.get(key, 0)
        now = time.time()
        
        if now - last < policy.cooldown_sec:
            logger.debug(f"Alert throttled: {key} (cooldown {policy.cooldown_sec}s)")
            return False
        
        return True
    
    def process(self, alert: Alert) -> bool:
        """Proceso një alarm sipas politikave"""
        policy = self.policies.get(alert.level)
        
        # Digest mode - ruaj për më vonë
        if policy and policy.digest and not policy.send:
            self._digest_queue.append(alert)
            logger.debug(f"Alert queued for {policy.digest} digest: {alert.title}")
            return False
        
        # Check if should send
        if not self.should_send(alert):
            return False
        
        # Update last sent
        key = f"{alert.category.value}:{alert.level.value}"
        self._last_sent[key] = time.time()
        
        # Send via handlers
        sent = False
        for handler in self._send_handlers:
            try:
                if handler(alert):
                    sent = True
            except Exception as e:
                logger.error(f"Alert handler error: {e}")
        
        if sent:
            logger.info(f"✅ Alert sent: [{alert.level.value}] {alert.title}")
        
        return sent
    
    def get_digest(self, level: Optional[AlertLevel] = None) -> list:
        """Merr alarmet e grumbulluara për digest"""
        if level:
            return [a for a in self._digest_queue if a.level == level]
        return self._digest_queue.copy()
    
    def clear_digest(self):
        """Pastro digest queue"""
        count = len(self._digest_queue)
        self._digest_queue.clear()
        return count
    
    def get_stats(self) -> Dict[str, Any]:
        """Statistika të alarmeve"""
        return {
            "enabled": self._enabled,
            "handlers": len(self._send_handlers),
            "digest_queue": len(self._digest_queue),
            "cooldowns": {k: time.time() - v for k, v in self._last_sent.items()},
        }


# ═══════════════════════════════════════════════════════════════════
# ALERT BUILDERS (shortcuts)
# ═══════════════════════════════════════════════════════════════════

def alert_service_down(service: str, error: Optional[str] = None) -> Alert:
    """Alert për service që nuk përgjigjet"""
    return Alert(
        level=AlertLevel.CRITICAL,
        category=AlertCategory.SERVICE_DOWN,
        title=f"🔴 {service.upper()} DOWN",
        message=f"{service} service is not responding",
        service=service,
        details={"error": error} if error else None,
    )


def alert_cpu_high(node: str, cpu_percent: float, duration_sec: int = 0) -> Alert:
    """Alert për CPU të lartë"""
    level = AlertLevel.CRITICAL if cpu_percent > 90 else AlertLevel.WARNING
    return Alert(
        level=level,
        category=AlertCategory.CPU_HIGH,
        title=f"🔥 CPU {cpu_percent:.1f}% on {node}",
        message=f"CPU usage is {cpu_percent:.1f}% for {duration_sec}s",
        service=node,
        details={"cpu_percent": cpu_percent, "duration_sec": duration_sec},
    )


def alert_memory_high(node: str, mem_percent: float) -> Alert:
    """Alert për memorie të lartë"""
    level = AlertLevel.CRITICAL if mem_percent > 95 else AlertLevel.WARNING
    return Alert(
        level=level,
        category=AlertCategory.MEMORY_HIGH,
        title=f"💾 Memory {mem_percent:.1f}% on {node}",
        message=f"Memory usage is {mem_percent:.1f}%",
        service=node,
        details={"mem_percent": mem_percent},
    )


def alert_disk_high(node: str, disk_percent: float) -> Alert:
    """Alert për disk të lartë"""
    level = AlertLevel.CRITICAL if disk_percent > 95 else AlertLevel.WARNING
    return Alert(
        level=level,
        category=AlertCategory.DISK_HIGH,
        title=f"💿 Disk {disk_percent:.1f}% on {node}",
        message=f"Disk usage is {disk_percent:.1f}%",
        service=node,
        details={"disk_percent": disk_percent},
    )


def alert_auto_learning(event: str, details: Optional[Dict] = None) -> Alert:
    """Alert për auto-learning events"""
    return Alert(
        level=AlertLevel.WARNING,
        category=AlertCategory.AUTO_LEARNING,
        title=f"🧠 Auto-Learning: {event}",
        message=event,
        details=details,
    )


def alert_security(event: str, severity: str = "critical", details: Optional[Dict] = None) -> Alert:
    """Alert për security events"""
    level = AlertLevel.CRITICAL if severity == "critical" else AlertLevel.WARNING
    return Alert(
        level=level,
        category=AlertCategory.SECURITY,
        title=f"🔒 Security: {event}",
        message=event,
        details=details,
    )


def info_deployment(service: str, version: str, status: str) -> Alert:
    """Info për deployment"""
    return Alert(
        level=AlertLevel.INFO,
        category=AlertCategory.DEPLOYMENT,
        title=f"🚀 Deploy: {service} v{version}",
        message=f"{service} deployment {status}",
        service=service,
        details={"version": version, "status": status},
    )


# ═══════════════════════════════════════════════════════════════════
# GLOBAL INSTANCE
# ═══════════════════════════════════════════════════════════════════

_manager: Optional[AlertManager] = None


def get_alert_manager() -> AlertManager:
    """Merr global AlertManager instance"""
    global _manager
    if _manager is None:
        _manager = AlertManager()
    return _manager


def send_alert(alert: Alert) -> bool:
    """Shortcut për të dërguar alert"""
    return get_alert_manager().process(alert)


# ═══════════════════════════════════════════════════════════════════
# CONFIG FILE
# ═══════════════════════════════════════════════════════════════════

def save_policy_config(path: Path):
    """Ruaj politikat në JSON"""
    config = {
        level.value: {
            "send": policy.send,
            "cooldown_sec": policy.cooldown_sec,
            "digest": policy.digest,
        }
        for level, policy in DEFAULT_POLICIES.items()
    }
    with open(path, "w") as f:
        json.dump(config, f, indent=2)
    logger.info(f"Policy config saved: {path}")


def load_policy_config(path: Path) -> Dict[AlertLevel, AlertPolicy]:
    """Ngarko politikat nga JSON"""
    with open(path) as f:
        config = json.load(f)
    
    policies = {}
    for level_str, data in config.items():
        level = AlertLevel(level_str)
        policies[level] = AlertPolicy(
            level=level,
            send=data.get("send", True),
            cooldown_sec=data.get("cooldown_sec", 0),
            digest=data.get("digest"),
        )
    return policies


# ═══════════════════════════════════════════════════════════════════
# CLI / TEST
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Create manager
    manager = AlertManager()
    
    # Demo handler (just print)
    manager.on_send(lambda a: print(f"📤 Would send: {a.to_dict()}") or True)
    
    print("=" * 60)
    print("🔔 ALERT POLICY TEST")
    print("=" * 60)
    
    # Test CRITICAL (should always send)
    print("\n1️⃣ Testing CRITICAL alert...")
    manager.process(alert_service_down("ALBA", "connection refused"))
    
    # Test WARNING with cooldown
    print("\n2️⃣ Testing WARNING alert (first time)...")
    manager.process(alert_cpu_high("node1", 78.5, 120))
    
    print("\n3️⃣ Testing WARNING alert (should be throttled)...")
    manager.process(alert_cpu_high("node1", 79.0, 180))  # Same category
    
    # Test INFO (should go to digest)
    print("\n4️⃣ Testing INFO alert (goes to digest)...")
    manager.process(info_deployment("API", "2.1.0", "success"))
    
    # Stats
    print("\n📊 Manager Stats:")
    print(json.dumps(manager.get_stats(), indent=2))
    
    print("\n✅ Alert Policy test complete!")

