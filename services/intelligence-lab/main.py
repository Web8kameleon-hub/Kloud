#!/usr/bin/env python3
"""
KLOUD INTELLIGENCE LAB API
==============================

FastAPI server për KLAJDI dhe MALI.

Endpoints:
- /klajdi/* - Detective Intelligence Lab
- /mali/* - Master Announced Labor Intelligence
- /tables/* - Excel-ready tables from real data

Port: 8098

Author: Ledjan Ahmati (CEO, ABA GmbH)
"""

import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.responses import JSONResponse
from cors_policy import apply_standard_cors

# Import lab modules
from klajdi_lab import (
    SignalChannel,
    SignalSeverity,
    SignalSource,
    get_klajdi_lab,
)
from mali_core import AnnouncementPriority, AnnouncementType, get_mali_core
from pydantic import BaseModel

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s'
)
logger = logging.getLogger("intelligence-lab")

# Port
PORT = int(os.environ.get("INTELLIGENCE_LAB_PORT", "8099"))


# ═══════════════════════════════════════════════════════════════════════════════
# LIFECYCLE
# ═══════════════════════════════════════════════════════════════════════════════

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle"""
    logger.info("🧪 Intelligence Lab starting...")
    
    # Initialize KLAJDI
    _klajdi = get_klajdi_lab()
    logger.info("🔬 KLAJDI Lab initialized")
    
    # Initialize MALI
    _mali = get_mali_core()
    logger.info("🏔️ MALI Core initialized")
    
    yield
    
    # Cleanup
    _mali.stop_monitoring()
    logger.info("🧪 Intelligence Lab shutting down...")


# ═══════════════════════════════════════════════════════════════════════════════
# APP SETUP
# ═══════════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="Kloud Intelligence Lab",
    description="KLAJDI Detective Lab + MALI Master Intelligence",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

apply_standard_cors(app)


# ═══════════════════════════════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class SignalInput(BaseModel):
    source: str  # ocean, blerina, liam, alda, system, etc.
    channel: str = "internal"  # http, websocket, worker, etc.
    payload: Dict[str, Any]
    severity: str = "info"  # info, warning, critical, anomaly, success
    meta: Optional[Dict[str, Any]] = None


class CaseInput(BaseModel):
    title: str
    hypothesis: str
    signal_ids: Optional[List[str]] = None


class AnnouncementInput(BaseModel):
    type: str  # alert, insight, report, discovery, warning, success
    priority: int = 2  # 1-5
    title: str
    content: str
    source_module: str = "manual"
    data: Optional[Dict[str, Any]] = None
    actions: Optional[List[str]] = None


# ═══════════════════════════════════════════════════════════════════════════════
# ROOT & HEALTH
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Kloud Intelligence Lab",
        "version": "1.0.0",
        "components": {
            "klajdi": "Knost-Labor-Array-Jonify-Detective-Intelligence",
            "mali": "Master Announced Labor Intelligence"
        },
        "endpoints": {
            "klajdi": ["/klajdi/signal", "/klajdi/case", "/klajdi/diagnostics", "/klajdi/stats"],
            "mali": ["/mali/cycle", "/mali/report", "/mali/announcements", "/mali/monitor"],
            "tables": ["/tables/all", "/tables/system", "/tables/docker", "/tables/liam", "/tables/alda"]
        }
    }


@app.get("/health")
async def health():
    """Health check"""
    klajdi = get_klajdi_lab()
    mali = get_mali_core()
    
    return {
        "status": "healthy",
        "service": "intelligence-lab",
        "components": {
            "klajdi": {
                "signals": klajdi.get_stats()["signals_ingested"],
                "cases": klajdi.get_stats()["cases_opened"]
            },
            "mali": {
                "cycles": mali.get_stats()["intake_cycles"],
                "running": mali._running
            }
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/status")
async def status():
    """Detailed status"""
    klajdi = get_klajdi_lab()
    mali = get_mali_core()
    
    return {
        "klajdi_stats": klajdi.get_stats(),
        "mali_stats": mali.get_stats(),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


# ═══════════════════════════════════════════════════════════════════════════════
# KLAJDI ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/klajdi/signal")
async def ingest_signal(signal: SignalInput):
    """Ingest a signal into KLAJDI"""
    klajdi = get_klajdi_lab()
    
    try:
        source = SignalSource[signal.source.upper()] if signal.source.upper() in SignalSource.__members__ else SignalSource.EXTERNAL
        channel = SignalChannel[signal.channel.upper()] if signal.channel.upper() in SignalChannel.__members__ else SignalChannel.INTERNAL
        severity = SignalSeverity[signal.severity.upper()] if signal.severity.upper() in SignalSeverity.__members__ else SignalSeverity.INFO
        
        result = await klajdi.ingest_signal(
            source=source,
            channel=channel,
            payload=signal.payload,
            severity=severity,
            meta=signal.meta
        )
        
        return {
            "status": "ingested",
            "signal_id": result.id,
            "ions_count": len(result.ions)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/klajdi/signals")
async def get_signals(
    source: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = 100
):
    """Get signals from KLAJDI"""
    klajdi = get_klajdi_lab()
    
    signals = klajdi.array._signals[-limit:]
    
    if source:
        try:
            source_enum = SignalSource[source.upper()]
            signals = [s for s in signals if s.source == source_enum]
        except KeyError:
            pass
    
    if severity:
        try:
            severity_enum = SignalSeverity[severity.upper()]
            signals = [s for s in signals if s.severity == severity_enum]
        except KeyError:
            pass
    
    return {
        "signals": [s.to_dict() for s in signals],
        "count": len(signals)
    }


@app.post("/klajdi/case")
async def open_case(case: CaseInput):
    """Open a new investigation case"""
    klajdi = get_klajdi_lab()
    
    # Get signals if IDs provided
    signals = []
    if case.signal_ids:
        for s in klajdi.array._signals:
            if s.id in case.signal_ids:
                signals.append(s)
    
    result = klajdi.open_case(
        title=case.title,
        hypothesis=case.hypothesis,
        signals=signals
    )
    
    return {
        "status": "opened",
        "case": result.to_dict()
    }


@app.get("/klajdi/cases")
async def get_cases(status: Optional[str] = None):
    """Get all investigation cases"""
    klajdi = get_klajdi_lab()
    return {
        "cases": klajdi.get_cases(status),
        "total": len(klajdi._cases)
    }


@app.post("/klajdi/case/{case_id}/analyze")
async def analyze_case(case_id: str):
    """Analyze an investigation case"""
    klajdi = get_klajdi_lab()
    
    case = None
    for c in klajdi._cases:
        if c.id == case_id:
            case = c
            break
    
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    result = await klajdi.analyze_case(case)
    
    return {
        "status": "analyzed",
        "case": result.to_dict()
    }


@app.get("/klajdi/diagnostics")
async def run_diagnostics():
    """Run full KLAJDI diagnostics"""
    klajdi = get_klajdi_lab()
    result = await klajdi.run_diagnostics()
    return result


@app.get("/klajdi/stats")
async def klajdi_stats():
    """Get KLAJDI statistics"""
    klajdi = get_klajdi_lab()
    return klajdi.get_stats()


@app.get("/klajdi/export")
async def export_klajdi():
    """Export KLAJDI data for Excel"""
    klajdi = get_klajdi_lab()
    return klajdi.export_to_excel()


# ═══════════════════════════════════════════════════════════════════════════════
# MALI ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/mali/cycle")
async def run_mali_cycle():
    """Run one MALI intake cycle"""
    mali = get_mali_core()
    result = await mali.run_intake_cycle()
    return result


@app.get("/mali/report")
async def get_mali_report():
    """Generate comprehensive MALI report"""
    mali = get_mali_core()
    report = await mali.generate_comprehensive_report()
    return report


@app.get("/mali/report/markdown")
async def get_mali_report_markdown():
    """Get MALI report as markdown"""
    mali = get_mali_core()
    report = await mali.generate_comprehensive_report()
    
    return JSONResponse(
        content={"markdown": report.get("markdown", "")},
        media_type="application/json"
    )


@app.post("/mali/monitor/start")
async def start_mali_monitoring(background_tasks: BackgroundTasks):
    """Start continuous MALI monitoring"""
    mali = get_mali_core()
    
    if mali._running:
        return {"status": "already_running"}
    
    background_tasks.add_task(mali.start_continuous_monitoring)
    
    return {
        "status": "started",
        "interval_seconds": mali._cycle_interval
    }


@app.post("/mali/monitor/stop")
async def stop_mali_monitoring():
    """Stop MALI monitoring"""
    mali = get_mali_core()
    mali.stop_monitoring()
    return {"status": "stopped"}


@app.get("/mali/announcements")
async def get_announcements(
    unacknowledged_only: bool = False,
    min_priority: int = 1,
    limit: int = 50
):
    """Get MALI announcements"""
    mali = get_mali_core()
    
    if unacknowledged_only:
        announcements = mali.announcements.get_unacknowledged()
    else:
        announcements = mali.announcements._announcements
    
    # Filter by priority
    announcements = [a for a in announcements if a.priority.value >= min_priority]
    
    return {
        "announcements": [a.to_dict() for a in announcements[-limit:]],
        "total": len(announcements)
    }


@app.post("/mali/announce")
async def make_announcement(ann: AnnouncementInput):
    """Create a manual announcement"""
    mali = get_mali_core()
    
    try:
        ann_type = AnnouncementType[ann.type.upper()]
        priority = AnnouncementPriority(ann.priority)
        
        result = mali.announcements.announce(
            type=ann_type,
            priority=priority,
            title=ann.title,
            content=ann.content,
            source_module=ann.source_module,
            data=ann.data,
            actions=ann.actions
        )
        
        return {
            "status": "announced",
            "announcement": result.to_dict()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/mali/acknowledge/{announcement_id}")
async def acknowledge_announcement(announcement_id: str):
    """Acknowledge an announcement"""
    mali = get_mali_core()
    
    success = mali.announcements.acknowledge(announcement_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Announcement not found")
    
    return {"status": "acknowledged", "id": announcement_id}


@app.get("/mali/stats")
async def mali_stats():
    """Get MALI statistics"""
    mali = get_mali_core()
    return mali.get_stats()


# ═══════════════════════════════════════════════════════════════════════════════
# TABLES ENDPOINTS - Excel-ready data
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/tables/all")
async def get_all_tables():
    """Get all tables for Excel/articles"""
    mali = get_mali_core()
    return await mali.tabulator.generate_all_tables()


@app.get("/tables/system")
async def get_system_table():
    """Get system metrics table"""
    mali = get_mali_core()
    return await mali.tabulator.generate_system_metrics_table()


@app.get("/tables/docker")
async def get_docker_table():
    """Get Docker stats table"""
    mali = get_mali_core()
    return await mali.tabulator.generate_docker_stats_table()


@app.get("/tables/liam")
async def get_liam_table():
    """Get LIAM matrix operations table"""
    mali = get_mali_core()
    return await mali.tabulator.generate_liam_matrix_table()


@app.get("/tables/alda")
async def get_alda_table():
    """Get ALDA labor statistics table"""
    mali = get_mali_core()
    return await mali.tabulator.generate_alda_labor_table()


# ═══════════════════════════════════════════════════════════════════════════════
# COMBINED ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/combined/dashboard")
async def get_combined_dashboard():
    """Get combined dashboard data from KLAJDI and MALI"""
    klajdi = get_klajdi_lab()
    mali = get_mali_core()
    
    return {
        "klajdi": {
            "stats": klajdi.get_stats(),
            "recent_signals": [s.to_dict() for s in klajdi.array._signals[-10:]],
            "open_cases": len([c for c in klajdi._cases if c.status == "open"])
        },
        "mali": {
            "stats": mali.get_stats(),
            "recent_announcements": [a.to_dict() for a in mali.announcements._announcements[-5:]],
            "source_status": mali.intake.get_source_status()
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/combined/article-data")
async def get_article_data():
    """Get data ready for article generation"""
    mali = get_mali_core()
    klajdi = get_klajdi_lab()
    
    # Get tables
    tables = await mali.tabulator.generate_all_tables()
    
    # Get recent insights
    insights = [
        a.to_dict() for a in mali.announcements._announcements
        if a.type.value == "insight"
    ][-5:]
    
    # Get patterns
    patterns = mali.intelligence._patterns[-10:]
    
    # Get KLAJDI findings
    findings = []
    for case in klajdi._cases[-5:]:
        findings.extend(case.findings)
    
    return {
        "tables": tables,
        "insights": insights,
        "patterns": patterns,
        "findings": findings[-10:],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)

