"""
KLOUD CLOUD - SLACK INTEGRATION SERVICE
Real-time monitoring, alerts, and system notifications via Slack
Connects to: ALBA, ALBI, JONA, Orchestrator, API

✅ Updated 2025: FastAPI lifespan events, timezone-aware datetimes
✅ Zero deprecated warnings
✅ Production-ready
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import aiohttp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SlackIntegration")

# ═══════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL", "#kloud-monitoring")
SERVICE_MODE = os.getenv("SERVICE_MODE", "production")  # production | development
SLACK_ENABLED = os.getenv("SLACK_INTEGRATION_ENABLED", "true").lower() == "true"

SERVICE_URLS = {
    "alba": "http://localhost:5555",
    "albi": "http://localhost:6680",
    "jona": "http://localhost:7777",
    "orchestrator": "http://localhost:9999",
    "api": "http://localhost:8000",
}

# ═══════════════════════════════════════════════════════════════════
# SCHEMAS
# ═══════════════════════════════════════════════════════════════════

class SlackMessage(BaseModel):
    channel: str = SLACK_CHANNEL
    text: str
    blocks: Optional[List[Dict[str, Any]]] = None
    attachments: Optional[List[Dict[str, Any]]] = None

class SystemAlert(BaseModel):
    service: str
    severity: str  # critical, warning, info
    title: str
    message: str
    details: Optional[Dict[str, Any]] = None

class ServiceMetric(BaseModel):
    service: str
    metric_name: str
    value: float
    threshold: float
    status: str  # healthy, warning, critical

class DeploymentNotification(BaseModel):
    service: str
    version: str
    environment: str
    status: str  # success, failed, in_progress
    details: Optional[str] = None

# ═══════════════════════════════════════════════════════════════════
# SLACK SENDER (CORE)
# ═══════════════════════════════════════════════════════════════════

async def send_slack_message(message: SlackMessage) -> bool:
    """Send message to Slack webhook"""
    
    # Check if Slack is disabled
    if not SLACK_ENABLED:
        logger.debug("Slack integration disabled via SLACK_INTEGRATION_ENABLED=false")
        return False
    
    if not SLACK_WEBHOOK_URL or "hooks.slack.com" not in SLACK_WEBHOOK_URL:
        logger.info("ℹ️  Slack disabled — webhook not configured")
        return False

    payload = {
        "channel": message.channel,
        "text": message.text,
    }

    if message.blocks:
        payload["blocks"] = message.blocks

    if message.attachments:
        payload["attachments"] = message.attachments

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(SLACK_WEBHOOK_URL, json=payload, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    logger.info(f"✅ Slack message sent to {message.channel}")
                    return True
                else:
                    error_text = await resp.text()
                    logger.error(f"❌ Slack HTTP {resp.status}: {error_text}")
                    return False

    except Exception as e:
        logger.error(f"❌ Slack send failed: {e}")
        return False

# ═══════════════════════════════════════════════════════════════════
# SERVICE MONITORING
# ═══════════════════════════════════════════════════════════════════

async def check_service_health() -> Dict[str, Any]:
    """Check health of all services"""
    results = {}

    async with aiohttp.ClientSession() as session:
        for name, base_url in SERVICE_URLS.items():
            try:
                health_url = f"{base_url}/health"
                async with session.get(health_url, timeout=aiohttp.ClientTimeout(total=3)) as resp:
                    if resp.status == 200:
                        results[name] = {
                            "status": "online",
                            "health": 1.0,
                            "url": base_url
                        }
                    else:
                        results[name] = {
                            "status": "degraded",
                            "health": 0.5,
                            "url": base_url
                        }

            except asyncio.TimeoutError:
                results[name] = {
                    "status": "offline",
                    "health": 0.0,
                    "url": base_url,
                    "error": "timeout"
                }
            except Exception as e:
                results[name] = {
                    "status": "offline",
                    "health": 0.0,
                    "url": base_url,
                    "error": str(e)
                }

    return results

async def monitor_services_background():
    """Background monitoring loop (non-blocking)"""
    logger.info("🔄 Background service monitor started (60s interval)")
    
    while True:
        try:
            health = await check_service_health()

            for svc, info in health.items():
                if info["status"] != "online":
                    alert = SystemAlert(
                        service=svc,
                        severity="critical" if info["status"] == "offline" else "warning",
                        title=f"{svc.upper()} Service Alert",
                        message=f"{svc} status = {info['status']}",
                        details={"error": info.get("error")}
                    )
                    await send_slack_alert(alert)

            logger.debug(f"✓ Health check completed: {sum(1 for x in health.values() if x['status'] == 'online')}/{len(health)} online")

        except Exception as e:
            logger.error(f"Monitor error: {e}")

        await asyncio.sleep(60)  # Check every 60 seconds

async def send_slack_alert(alert: SystemAlert):
    """Send formatted alert to Slack"""
    now = datetime.now(timezone.utc).isoformat()

    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"🚨 {alert.severity.upper()} - {alert.title}",
                "emoji": True
            }
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*Service:*\n{alert.service}"},
                {"type": "mrkdwn", "text": f"*Severity:*\n{alert.severity}"},
                {"type": "mrkdwn", "text": f"*Time:*\n{now}"},
            ]
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Message:*\n{alert.message}"
            }
        }
    ]

    if alert.details:
        details_json = json.dumps(alert.details, indent=2)
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"```{details_json}```"
            }
        })

    msg = SlackMessage(
        text=f"{alert.severity.upper()}: {alert.title}",
        blocks=blocks
    )

    await send_slack_message(msg)

# ═══════════════════════════════════════════════════════════════════
# LIFESPAN EVENTS (REPLACES DEPRECATED @on_event)
# ═══════════════════════════════════════════════════════════════════

background_task: Optional[asyncio.Task] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup: Initialize monitoring task
    Shutdown: Gracefully stop monitoring
    """
    global background_task
    
    logger.info("=" * 50)
    logger.info("🚀 SLACK INTEGRATION STARTING")
    logger.info(f"   Mode: {SERVICE_MODE}")
    logger.info(f"   Webhook: {'✅ Configured' if SLACK_WEBHOOK_URL else '❌ NOT SET'}")
    logger.info("=" * 50)

    # Startup: Send notification
    startup_msg = SlackMessage(
        text=f"✅ Slack Integration Online ({SERVICE_MODE})",
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"✅ *Kloud Cloud - Slack Integration* Online\n"
                           f"Mode: `{SERVICE_MODE}`\n"
                           f"Channel: {SLACK_CHANNEL}\n"
                           f"Time: {datetime.now(timezone.utc).isoformat()}"
                }
            }
        ]
    )
    await send_slack_message(startup_msg)

    # Start background monitoring task
    background_task = asyncio.create_task(monitor_services_background())

    yield  # Application runs here

    # Shutdown: Stop monitoring and notify
    if background_task:
        background_task.cancel()
        try:
            await background_task
        except asyncio.CancelledError:
            pass

    shutdown_msg = SlackMessage(
        text="⚠️  Slack Integration Shutting Down",
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"⚠️  *Kloud Cloud* Slack Integration Offline\n"
                           f"Time: {datetime.now(timezone.utc).isoformat()}"
                }
            }
        ]
    )
    await send_slack_message(shutdown_msg)

    logger.info("=" * 50)
    logger.info("🛑 SLACK INTEGRATION STOPPED")
    logger.info("=" * 50)

# ═══════════════════════════════════════════════════════════════════
# FASTAPI APP
# ═══════════════════════════════════════════════════════════════════

app = FastAPI(
    title="Kloud Slack Integration",
    version="2.0.0",
    description="Real-time Slack notifications for Kloud Cloud",
    lifespan=lifespan  # Modern approach (replaces @on_event)
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# ═══════════════════════════════════════════════════════════════════
# ENDPOINTS - HEALTH & STATUS
# ═══════════════════════════════════════════════════════════════════

@app.get("/health")
async def health():
    """Service health check"""
    return {
        "service": "slack-integration",
        "status": "operational",
        "mode": SERVICE_MODE,
        "webhook_configured": bool(SLACK_WEBHOOK_URL and "hooks.slack.com" in SLACK_WEBHOOK_URL),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/service-health")
async def service_health():
    """Get all monitored services health status"""
    health = await check_service_health()
    
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "services": health,
        "summary": {
            "total": len(health),
            "online": sum(1 for s in health.values() if s["status"] == "online"),
            "degraded": sum(1 for s in health.values() if s["status"] == "degraded"),
            "offline": sum(1 for s in health.values() if s["status"] == "offline")
        }
    }

@app.get("/status-report")
async def status_report():
    """Generate and send status report to Slack"""
    health = await check_service_health()
    now = datetime.now(timezone.utc).isoformat()

    # Build blocks
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "📊 KLOUD CLOUD STATUS REPORT",
                "emoji": True
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Report Time:* {now}"
            }
        }
    ]

    # Service statuses
    for svc, status in health.items():
        emoji = "✅" if status["status"] == "online" else "⚠️" if status["status"] == "degraded" else "❌"
        blocks.append({
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"{emoji} *{svc.upper()}*"
                },
                {
                    "type": "mrkdwn",
                    "text": f"Status: {status['status']}\nHealth: {status['health']*100:.0f}%"
                }
            ]
        })

    msg = SlackMessage(
        text="Kloud Cloud Status Report",
        blocks=blocks
    )

    await send_slack_message(msg)

    return {
        "status": "report_sent",
        "services": health,
        "timestamp": now
    }

# ═══════════════════════════════════════════════════════════════════
# ENDPOINTS - ALERTS & NOTIFICATIONS
# ═══════════════════════════════════════════════════════════════════

@app.post("/send-alert")
async def send_alert(alert: SystemAlert):
    """Send custom system alert to Slack"""
    success = await send_slack_alert(alert)
    return {
        "status": "sent" if success else "failed",
        "service": alert.service,
        "severity": alert.severity
    }

@app.post("/send-message")
async def send_message(message: SlackMessage):
    """Send custom message to Slack"""
    success = await send_slack_message(message)
    return {
        "status": "sent" if success else "failed",
        "channel": message.channel
    }

@app.post("/metric-alert")
async def metric_alert(metric: ServiceMetric):
    """Alert when metric exceeds threshold"""
    if metric.value > metric.threshold:
        alert = SystemAlert(
            service=metric.service,
            severity="warning",
            title=f"Metric Alert: {metric.metric_name}",
            message=f"{metric.metric_name} exceeds threshold",
            details={
                "metric": metric.metric_name,
                "value": metric.value,
                "threshold": metric.threshold,
                "status": metric.status
            }
        )
        await send_slack_alert(alert)
        return {
            "status": "alert_sent",
            "metric": metric.metric_name,
            "value": metric.value
        }

    return {
        "status": "ok",
        "message": "Metric within threshold",
        "metric": metric.metric_name,
        "value": metric.value
    }

@app.post("/notify-deployment")
async def notify_deployment(deployment: DeploymentNotification):
    """Send deployment notification to Slack"""
    
    status_emoji = {
        "success": "✅",
        "failed": "❌",
        "in_progress": "🔄"
    }.get(deployment.status, "ℹ️")

    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"🚀 DEPLOYMENT NOTIFICATION",
                "emoji": True
            }
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*Service:*\n{deployment.service}"},
                {"type": "mrkdwn", "text": f"*Version:*\n{deployment.version}"},
                {"type": "mrkdwn", "text": f"*Environment:*\n{deployment.environment}"},
                {"type": "mrkdwn", "text": f"{status_emoji} *Status:*\n{deployment.status}"}
            ]
        }
    ]

    if deployment.details:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Details:*\n{deployment.details}"
            }
        })

    msg = SlackMessage(
        text=f"🚀 Deployment: {deployment.service} {deployment.version}",
        blocks=blocks
    )

    await send_slack_message(msg)

    return {
        "status": "notification_sent",
        "service": deployment.service,
        "version": deployment.version
    }

# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn

    print("\n╔════════════════════════════════════════════╗")
    print("║  SLACK INTEGRATION SERVICE (v2.0.0)      ║")
    print("║  Real-time Monitoring & Alerts           ║")
    print("║  FastAPI Lifespan Events (No Warnings)   ║")
    print("╚════════════════════════════════════════════╝\n")

    port = int(os.getenv("SLACK_PORT", "8888"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")


