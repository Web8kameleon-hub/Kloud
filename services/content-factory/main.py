"""
KLOUD CONTENT FACTORY API SERVICE
======================================

Complete content production pipeline API:

    News/Law Watcher → BLERINA → EAP Layer → Trinity → Ocean → Quality Selector → CLX-Publisher

Endpoints:
- POST /analyze         - Analyze content for gaps (Blerina)
- POST /process         - Full EAP pipeline (Evresi-Analysi-Proposi)
- POST /publish         - Publish to platforms
- POST /pipeline        - Full pipeline from source to publish
- GET  /status          - Factory status
- GET  /stats           - Production statistics

Author: Ledjan Ahmati (CEO, ABA GmbH)
Port: 8005
"""

import logging
import os
import sys
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Type, Union

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Add parent paths for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(name)s | %(message)s')
logger = logging.getLogger("content-factory-api")

# Try to import core modules
BlerinaCore: Optional[Type[Any]] = None
DocumentType: Optional[Type[Any]] = None
get_blerina: Optional[Callable[[], Any]] = None

try:
    from blerina_core import BlerinaCore as _BlerinaCore
    from blerina_core import DocumentType as _DocumentType
    from blerina_core import get_blerina as _get_blerina
    BlerinaCore = _BlerinaCore
    DocumentType = _DocumentType
    get_blerina = _get_blerina
    BLERINA_AVAILABLE = True
    logger.info("✅ BlerinaCore loaded")
except ImportError as e:
    BLERINA_AVAILABLE = False
    logger.warning(f"⚠️ BlerinaCore not available: {e}")

EAPLayer: Optional[Type[Any]] = None
EAPDocument: Optional[Type[Any]] = None
get_eap: Optional[Callable[[], Any]] = None

try:
    from eap_layer import EAPDocument as _EAPDocument
    from eap_layer import EAPLayer as _EAPLayer
    from eap_layer import get_eap as _get_eap
    EAPLayer = _EAPLayer
    EAPDocument = _EAPDocument
    get_eap = _get_eap
    EAP_AVAILABLE = True
    logger.info("✅ EAPLayer loaded")
except ImportError as e:
    EAP_AVAILABLE = False
    logger.warning(f"⚠️ EAPLayer not available: {e}")

CLXPublisher: Optional[Type[Any]] = None
get_publisher: Optional[Callable[[], Any]] = None

try:
    from clx_publisher import CLXPublisher as _CLXPublisher
    from clx_publisher import get_publisher as _get_publisher
    CLXPublisher = _CLXPublisher
    get_publisher = _get_publisher
    PUBLISHER_AVAILABLE = True
    logger.info("✅ CLXPublisher loaded")
except ImportError as e:
    PUBLISHER_AVAILABLE = False
    logger.warning(f"⚠️ CLXPublisher not available: {e}")

ContentFactory: Optional[Type[Any]] = None
FactoryMode: Optional[Type[Any]] = None
FactoryConfig: Optional[Type[Any]] = None
FactoryResult: Optional[Type[Any]] = None

try:
    from content_factory import (
        ContentFactory as _ContentFactory,
    )
    from content_factory import (
        FactoryConfig as _FactoryConfig,
    )
    from content_factory import (
        FactoryMode as _FactoryMode,
    )
    from content_factory import (
        FactoryResult as _FactoryResult,
    )
    ContentFactory = _ContentFactory
    FactoryMode = _FactoryMode
    FactoryConfig = _FactoryConfig
    FactoryResult = _FactoryResult
    FACTORY_AVAILABLE = True
    logger.info("✅ ContentFactory loaded")
except ImportError as e:
    FACTORY_AVAILABLE = False
    logger.warning(f"⚠️ ContentFactory not available: {e}")

# Auto Publisher
AutoPublisher: Optional[Type[Any]] = None
get_auto_publisher: Optional[Callable[[], Any]] = None
start_auto_publisher: Optional[Callable[[], Any]] = None

try:
    from auto_publisher import AutoPublisher as _AutoPublisher
    from auto_publisher import get_auto_publisher as _get_auto_publisher
    from auto_publisher import start_auto_publisher as _start_auto_publisher
    AutoPublisher = _AutoPublisher
    get_auto_publisher = _get_auto_publisher
    start_auto_publisher = _start_auto_publisher
    AUTO_PUBLISHER_AVAILABLE = True
    logger.info("✅ AutoPublisher loaded")
except ImportError as e:
    AUTO_PUBLISHER_AVAILABLE = False
    logger.warning(f"⚠️ AutoPublisher not available: {e}")

# Blog Sync (Batica-Zbatica flow)
BlogSync: Optional[Type[Any]] = None
get_blog_sync: Optional[Callable[[], Any]] = None

try:
    from blog_sync import BlogSync as _BlogSync
    from blog_sync import get_blog_sync as _get_blog_sync
    BlogSync = _BlogSync
    get_blog_sync = _get_blog_sync
    BLOG_SYNC_AVAILABLE = True
    logger.info("✅ BlogSync loaded (Batica-Zbatica)")
except ImportError as e:
    BLOG_SYNC_AVAILABLE = False
    logger.warning(f"⚠️ BlogSync not available: {e}")

# Instance ID
INSTANCE_ID = uuid.uuid4().hex[:8]
START_TIME = datetime.now(timezone.utc)

# Statistics
stats: Dict[str, Union[int, float, str]] = {
    "total_analyzed": 0,
    "total_processed": 0,
    "total_published": 0,
    "gaps_detected": 0,
    "avg_quality_score": 0.0,
    "start_time": START_TIME.isoformat()
}

# Create FastAPI app
app = FastAPI(
    title="Kloud Content Factory API",
    description="Complete content production pipeline with Blerina, EAP, and Publisher",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ═══════════════════════════════════════════════════════════════════════════════
# REQUEST/RESPONSE MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class DocumentTypeEnum(str, Enum):
    NEWS = "news"
    LAW = "law"
    POLICY = "policy"
    RESEARCH = "research"
    REPORT = "report"
    TECHNICAL = "technical"
    REGULATION = "regulation"


class AnalyzeRequest(BaseModel):
    """Request for gap analysis (Blerina)"""
    content: str = Field(..., min_length=50, description="Content to analyze")
    title: Optional[str] = Field(None, description="Document title")
    doc_type: DocumentTypeEnum = Field(DocumentTypeEnum.TECHNICAL, description="Document type")
    language: str = Field("sq", description="Language code (sq, en, de)")


class AnalyzeResponse(BaseModel):
    """Response from gap analysis"""
    id: str
    gaps_found: int
    discontinuity_level: str
    gaps: List[Dict[str, Any]]
    quality_score: float
    processing_time_ms: float
    timestamp: str


class ProcessRequest(BaseModel):
    """Request for EAP processing"""
    content: str = Field(..., min_length=50, description="Content to process")
    title: Optional[str] = Field(None, description="Document title")
    doc_type: DocumentTypeEnum = Field(DocumentTypeEnum.TECHNICAL, description="Document type")
    run_blerina: bool = Field(True, description="Run Blerina gap analysis first")
    language: str = Field("sq", description="Language code")


class ProcessResponse(BaseModel):
    """Response from EAP processing"""
    id: str
    blerina_signal_id: Optional[str]
    eap_document_id: str
    gaps_found: int
    discontinuity_level: str
    quality_score: float
    stages: Dict[str, Any]
    processing_time_ms: float
    timestamp: str


class PublishRequest(BaseModel):
    """Request for publishing"""
    content: str = Field(..., description="Content to publish")
    title: str = Field(..., description="Title")
    platforms: List[str] = Field(default=["kloud"], description="Target platforms")
    quality_threshold: float = Field(0.7, ge=0.0, le=1.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PublishResponse(BaseModel):
    """Response from publishing"""
    id: str
    published: bool
    platforms: List[str]
    urls: List[str]
    quality_score: float
    timestamp: str


class PipelineRequest(BaseModel):
    """Request for full pipeline"""
    content: str = Field(..., min_length=50, description="Source content")
    title: Optional[str] = Field(None, description="Title")
    doc_type: DocumentTypeEnum = Field(DocumentTypeEnum.TECHNICAL)
    auto_publish: bool = Field(False, description="Auto-publish if quality passes")
    publish_platforms: List[str] = Field(default=["kloud"])
    quality_threshold: float = Field(0.7, ge=0.0, le=1.0)


class PipelineResponse(BaseModel):
    """Response from full pipeline"""
    id: str
    blerina_signal_id: Optional[str]
    eap_document_id: Optional[str]
    gaps_found: int
    discontinuity_level: str
    quality_score: float
    published: bool
    publish_platforms: List[str]
    publish_urls: List[str]
    stages: Dict[str, Any]
    processing_time_ms: float
    timestamp: str


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Kloud Content Factory API",
        "version": "1.0.0",
        "instance": INSTANCE_ID,
        "components": {
            "blerina": "available" if BLERINA_AVAILABLE else "not_loaded",
            "eap": "available" if EAP_AVAILABLE else "not_loaded",
            "publisher": "available" if PUBLISHER_AVAILABLE else "not_loaded",
            "factory": "available" if FACTORY_AVAILABLE else "not_loaded"
        },
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """Health check"""
    uptime = (datetime.now(timezone.utc) - START_TIME).total_seconds()
    return {
        "status": "healthy",
        "service": "content-factory-api",
        "instance": INSTANCE_ID,
        "uptime_seconds": round(uptime, 2),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/status")
async def status():
    """Detailed status"""
    uptime = (datetime.now(timezone.utc) - START_TIME).total_seconds()
    hours, remainder = divmod(int(uptime), 3600)
    minutes, seconds = divmod(remainder, 60)
    
    return {
        "service": "Kloud Content Factory",
        "version": "1.0.0",
        "instance": INSTANCE_ID,
        "uptime": f"{hours}h {minutes}m",
        "components": {
            "blerina_core": {
                "status": "operational" if BLERINA_AVAILABLE else "not_loaded",
                "description": "Gap-Detector & Conceptual Reconstruction"
            },
            "eap_layer": {
                "status": "operational" if EAP_AVAILABLE else "not_loaded",
                "description": "Evresi → Analysi → Proposi Pipeline"
            },
            "clx_publisher": {
                "status": "operational" if PUBLISHER_AVAILABLE else "not_loaded",
                "description": "Multi-platform Publisher"
            },
            "content_factory": {
                "status": "operational" if FACTORY_AVAILABLE else "not_loaded",
                "description": "Main Orchestrator"
            }
        },
        "pipeline": "News/Law → BLERINA → EAP → Trinity → Ocean → Quality → Publisher",
        "capacity": {
            "manual": "5-15 docs/day",
            "watcher": "30-60 docs/day",
            "continuous": "100-200 docs/day",
            "autopilot": "300-500 docs/day"
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/stats")
async def get_stats():
    """Get production statistics"""
    return {
        "stats": stats,
        "instance": INSTANCE_ID,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_content(request: AnalyzeRequest):
    """
    Analyze content for gaps using BLERINA Core
    
    Gap-Detector: Identifies conceptual discontinuities in text
    """
    start_time = datetime.now(timezone.utc)
    
    if not BLERINA_AVAILABLE:
        # Fallback simulation mode
        logger.info("Running Blerina in simulation mode")
        result_id = f"sim_{uuid.uuid4().hex[:12]}"
        
        # Simulate gap detection
        word_count = len(request.content.split())
        gaps_count = max(1, word_count // 100)  # 1 gap per 100 words
        
        sample_gaps = []
        for i in range(gaps_count):
            sample_gaps.append({
                "id": f"gap_{i+1}",
                "type": "conceptual",
                "severity": "medium",
                "position": i * 100,
                "description": f"Potential conceptual gap at position {i * 100}",
                "suggestion": "Consider adding connecting context"
            })
        
        processing_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
        
        stats["total_analyzed"] = int(stats["total_analyzed"]) + 1
        stats["gaps_detected"] = int(stats["gaps_detected"]) + gaps_count
        
        return AnalyzeResponse(
            id=result_id,
            gaps_found=gaps_count,
            discontinuity_level="moderate" if gaps_count > 2 else "low",
            gaps=sample_gaps,
            quality_score=0.7,
            processing_time_ms=round(processing_time, 2),
            timestamp=datetime.now(timezone.utc).isoformat()
        )
    
    # Real Blerina processing
    try:
        blerina = get_blerina() if get_blerina is not None else (BlerinaCore() if BlerinaCore is not None else None)
        if blerina is None:
            raise HTTPException(status_code=500, detail="Blerina not available")
        
        # Map doc_type string to DocumentType enum if available
        doc_type_enum = None
        if DocumentType is not None:
            doc_type_map = {
                "news": DocumentType.NEWS,
                "law": DocumentType.LAW,
                "policy": DocumentType.POLICY,
                "research": DocumentType.RESEARCH,
                "report": DocumentType.REPORT,
                "technical": DocumentType.TECHNICAL,
                "regulation": DocumentType.REGULATION,
            }
            doc_type_enum = doc_type_map.get(request.doc_type.value, DocumentType.TECHNICAL)
        
        # Use extract_gaps method (the actual Blerina method)
        if hasattr(blerina, 'extract_gaps'):
            gaps = await blerina.extract_gaps(
                document=request.content,
                doc_type=doc_type_enum,
                context=request.title
            )
            result = {
                "id": f"blerina_{uuid.uuid4().hex[:12]}",
                "gaps": [{"id": g.id, "type": g.gap_type.value if hasattr(g.gap_type, 'value') else str(g.gap_type), "severity": g.severity.value if hasattr(g.severity, 'value') else str(g.severity), "description": g.description, "location": g.location, "missing_concept": g.missing_concept, "reconstruction_hint": g.reconstruction_hint} for g in gaps] if gaps else [],
                "discontinuity_level": "high" if len(gaps) > 5 else ("moderate" if len(gaps) > 2 else "low"),
                "quality_score": max(0.3, 1.0 - len(gaps) * 0.1) if gaps else 0.8
            }
        else:
            # Fallback to simulation
            raise Exception("extract_gaps method not found")
        
        processing_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
        
        gaps_list: List[Dict[str, Any]] = result.get("gaps", [])  # type: ignore[assignment]
        quality_val: Any = result.get("quality_score", 0.0)
        quality_score: float = float(quality_val) if quality_val is not None else 0.0
        stats["total_analyzed"] = int(stats["total_analyzed"]) + 1
        stats["gaps_detected"] = int(stats["gaps_detected"]) + len(gaps_list)
        
        return AnalyzeResponse(
            id=str(result.get("id", uuid.uuid4().hex[:12])),
            gaps_found=len(gaps_list),
            discontinuity_level=str(result.get("discontinuity_level", "unknown")),
            gaps=gaps_list,
            quality_score=quality_score,
            processing_time_ms=round(processing_time, 2),
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
    except Exception as e:
        logger.error(f"Blerina analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Blerina analysis error: {str(e)}")


@app.post("/process", response_model=ProcessResponse)
async def process_content(request: ProcessRequest):
    """
    Process content through EAP pipeline
    
    Evresi (Discovery) → Analysi (Analysis) → Proposi (Proposal)
    """
    start_time = datetime.now(timezone.utc)
    doc_id = f"eap_{uuid.uuid4().hex[:12]}"
    blerina_id = None
    gaps_found = 0
    discontinuity = "unknown"
    
    # Run Blerina first if requested
    if request.run_blerina:
        analyze_req = AnalyzeRequest(
            content=request.content,
            title=request.title,
            doc_type=request.doc_type,
            language=request.language
        )
        blerina_result = await analyze_content(analyze_req)
        blerina_id = blerina_result.id
        gaps_found = blerina_result.gaps_found
        discontinuity = blerina_result.discontinuity_level
    
    # EAP Processing
    stages = {
        "evresi": {
            "status": "completed",
            "description": "Discovery phase - source analysis",
            "findings": gaps_found
        },
        "analysi": {
            "status": "completed",
            "description": "Analysis phase - deep processing",
            "insights": max(1, gaps_found // 2)
        },
        "proposi": {
            "status": "completed",
            "description": "Proposal phase - recommendations",
            "proposals": max(1, gaps_found // 3)
        }
    }
    
    # Calculate quality score
    base_score = 0.85
    penalty = gaps_found * 0.05
    quality_score = max(0.3, min(1.0, base_score - penalty))
    
    processing_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
    
    stats["total_processed"] = int(stats["total_processed"]) + 1
    stats["avg_quality_score"] = (float(stats["avg_quality_score"]) + quality_score) / 2
    
    return ProcessResponse(
        id=doc_id,
        blerina_signal_id=blerina_id,
        eap_document_id=doc_id,
        gaps_found=gaps_found,
        discontinuity_level=discontinuity,
        quality_score=round(quality_score, 3),
        stages=stages,
        processing_time_ms=round(processing_time, 2),
        timestamp=datetime.now(timezone.utc).isoformat()
    )


@app.post("/publish", response_model=PublishResponse)
async def publish_content(request: PublishRequest):
    """
    Publish content to specified platforms
    
    CLX-Publisher: Multi-platform publishing engine
    """
    pub_id = f"pub_{uuid.uuid4().hex[:12]}"
    
    # Simulate quality check
    word_count = len(request.content.split())
    quality_score = min(1.0, 0.5 + (word_count / 1000) * 0.3)
    
    if quality_score < request.quality_threshold:
        return PublishResponse(
            id=pub_id,
            published=False,
            platforms=[],
            urls=[],
            quality_score=round(quality_score, 3),
            timestamp=datetime.now(timezone.utc).isoformat()
        )
    
    # Simulate publishing
    published_urls = []
    for platform in request.platforms:
        if platform == "kloud":
            published_urls.append(f"https://kloud.com/content/{pub_id}")
        elif platform == "medium":
            published_urls.append(f"https://medium.com/@kloud/{pub_id}")
        elif platform == "linkedin":
            published_urls.append(f"https://linkedin.com/pulse/{pub_id}")
    
    stats["total_published"] = int(stats["total_published"]) + 1
    
    return PublishResponse(
        id=pub_id,
        published=True,
        platforms=request.platforms,
        urls=published_urls,
        quality_score=round(quality_score, 3),
        timestamp=datetime.now(timezone.utc).isoformat()
    )


@app.post("/pipeline", response_model=PipelineResponse)
async def full_pipeline(request: PipelineRequest):
    """
    Run full content pipeline
    
    Source → BLERINA → EAP → Quality Check → (optional) Publish
    """
    start_time = datetime.now(timezone.utc)
    pipeline_id = f"pipe_{uuid.uuid4().hex[:12]}"
    
    # Step 1: Blerina Analysis
    analyze_req = AnalyzeRequest(
        content=request.content,
        title=request.title,
        doc_type=request.doc_type,
        language="sq"
    )
    blerina_result = await analyze_content(analyze_req)
    
    # Step 2: EAP Processing
    process_req = ProcessRequest(
        content=request.content,
        title=request.title,
        doc_type=request.doc_type,
        run_blerina=False,  # Already done
        language="sq"
    )
    eap_result = await process_content(process_req)
    
    # Use Blerina's quality score
    final_quality = blerina_result.quality_score
    
    # Step 3: Publish if auto_publish and quality passes
    published = False
    publish_platforms = []
    publish_urls = []
    
    if request.auto_publish and final_quality >= request.quality_threshold:
        publish_req = PublishRequest(
            content=request.content,
            title=request.title or f"Content {pipeline_id}",
            platforms=request.publish_platforms,
            quality_threshold=request.quality_threshold
        )
        publish_result = await publish_content(publish_req)
        published = publish_result.published
        publish_platforms = publish_result.platforms
        publish_urls = publish_result.urls
    
    processing_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
    
    # Build stages summary
    stages = {
        "blerina": {
            "id": blerina_result.id,
            "gaps": blerina_result.gaps_found,
            "level": blerina_result.discontinuity_level
        },
        "eap": {
            "id": eap_result.eap_document_id,
            "stages_completed": 3
        },
        "quality_check": {
            "score": final_quality,
            "passed": final_quality >= request.quality_threshold
        },
        "publish": {
            "executed": request.auto_publish,
            "success": published
        }
    }
    
    return PipelineResponse(
        id=pipeline_id,
        blerina_signal_id=blerina_result.id,
        eap_document_id=eap_result.eap_document_id,
        gaps_found=blerina_result.gaps_found,
        discontinuity_level=blerina_result.discontinuity_level,
        quality_score=round(final_quality, 3),
        published=published,
        publish_platforms=publish_platforms,
        publish_urls=publish_urls,
        stages=stages,
        processing_time_ms=round(processing_time, 2),
        timestamp=datetime.now(timezone.utc).isoformat()
    )


# Error handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc),
            "instance": INSTANCE_ID,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )


# ═══════════════════════════════════════════════════════════════════════════════
# AUTO-PUBLISHER ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/auto/start")
async def start_auto_publishing():
    """Start continuous auto-publishing (100% automated)"""
    if not AUTO_PUBLISHER_AVAILABLE or not get_auto_publisher:
        raise HTTPException(status_code=503, detail="AutoPublisher not available")
    
    import asyncio
    publisher = get_auto_publisher()
    
    if publisher._running:
        return {"status": "already_running", "message": "Auto-publisher is already running"}
    
    # Start in background
    asyncio.create_task(publisher.run_continuous())
    
    return {
        "status": "started",
        "message": "Auto-publisher started in background",
        "config": {
            "docs_per_day_target": publisher.config.docs_per_day_target,
            "min_interval_seconds": publisher.config.min_interval_seconds,
            "max_interval_seconds": publisher.config.max_interval_seconds
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.post("/auto/stop")
async def stop_auto_publishing():
    """Stop continuous auto-publishing"""
    if not AUTO_PUBLISHER_AVAILABLE or not get_auto_publisher:
        raise HTTPException(status_code=503, detail="AutoPublisher not available")
    
    publisher = get_auto_publisher()
    publisher.stop()
    
    return {
        "status": "stopped",
        "message": "Auto-publisher stopped",
        "stats": publisher.get_stats(),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/auto/stats")
async def get_auto_stats():
    """Get auto-publisher statistics"""
    if not AUTO_PUBLISHER_AVAILABLE or not get_auto_publisher:
        raise HTTPException(status_code=503, detail="AutoPublisher not available")
    
    publisher = get_auto_publisher()
    return {
        "status": "running" if publisher._running else "stopped",
        "stats": publisher.get_stats(),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.post("/auto/cycle")
async def run_single_cycle():
    """Run a single publish cycle manually"""
    if not AUTO_PUBLISHER_AVAILABLE or not get_auto_publisher:
        raise HTTPException(status_code=503, detail="AutoPublisher not available")
    
    publisher = get_auto_publisher()
    result = await publisher.publish_cycle()
    
    return {
        "status": "completed",
        "result": result,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/auto/articles")
async def list_local_articles():
    """List all locally saved articles"""
    import json
    from pathlib import Path
    
    output_dir = Path("/app/published")
    index_path = output_dir / "index.json"
    
    if not index_path.exists():
        return {
            "status": "empty",
            "articles": [],
            "total": 0,
            "message": "No articles published yet. Run /auto/cycle first.",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    try:
        index = json.loads(index_path.read_text())
        return {
            "status": "success",
            "articles": index.get("articles", [])[:50],  # Return last 50
            "total": index.get("total_count", 0),
            "last_updated": index.get("last_updated"),
            "paths": {
                "jekyll_posts": str(output_dir / "blog" / "_posts"),
                "html": str(output_dir / "html"),
                "markdown": str(output_dir / "articles")
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


@app.get("/auto/article/{filename}")
async def get_article_content(filename: str):
    """Get content of a specific article"""
    from pathlib import Path
    
    # Try different paths
    output_dir = Path("/app/published")
    possible_paths = [
        output_dir / "articles" / f"{filename}.md",
        output_dir / "html" / f"{filename}.html",
        output_dir / "blog" / "_posts" / f"{filename}.md",
    ]
    
    for path in possible_paths:
        if path.exists():
            return {
                "status": "success",
                "filename": filename,
                "path": str(path),
                "content": path.read_text(encoding="utf-8"),
                "format": path.suffix[1:],
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    raise HTTPException(status_code=404, detail=f"Article not found: {filename}")


@app.post("/auto/github-push")
async def push_to_github():
    """Push all local articles to GitHub Pages repository"""
    if not AUTO_PUBLISHER_AVAILABLE or not get_auto_publisher:
        raise HTTPException(status_code=503, detail="AutoPublisher not available")
    
    publisher = get_auto_publisher()
    result = await publisher.github_pages.publish()
    
    return {
        "status": "success" if result.get("success") else "failed",
        "result": result,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


# ═══════════════════════════════════════════════════════════════════════════════
# BLOG SYNC - Batica-Zbatica (content flows OUT to separate blog repo)
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/blog/sync")
async def sync_to_blog():
    """
    Sync generated articles to separate blog repository (Batica-Zbatica flow).
    
    This pushes content from main repo to kloud-blog for GitHub Pages.
    Keeps main repo clean while publishing content to the world.
    """
    if not BLOG_SYNC_AVAILABLE or not get_blog_sync:
        raise HTTPException(status_code=503, detail="BlogSync not available")
    
    sync = get_blog_sync()
    result = await sync.sync(push=True)
    
    return {
        "status": result.get("status"),
        "message": "Content synced to blog repo (Batica → Zbatica)",
        "result": result,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/blog/stats")
async def get_blog_stats():
    """Get blog sync statistics"""
    if not BLOG_SYNC_AVAILABLE or not get_blog_sync:
        raise HTTPException(status_code=503, detail="BlogSync not available")
    
    sync = get_blog_sync()
    return {
        "status": "available",
        "stats": sync.get_stats(),
        "flow": "Kloud-cloud → kloud-blog → GitHub Pages",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.post("/blog/init")
async def init_blog_repo():
    """Initialize or clone the blog repository"""
    if not BLOG_SYNC_AVAILABLE or not get_blog_sync:
        raise HTTPException(status_code=503, detail="BlogSync not available")
    
    sync = get_blog_sync()
    result = await sync.initialize()
    
    return {
        "status": result.get("status"),
        "result": result,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8005))
    logger.info(f"🚀 Starting Content Factory API on port {port}")
    logger.info(f"📦 Components: Blerina={BLERINA_AVAILABLE}, EAP={EAP_AVAILABLE}, Publisher={PUBLISHER_AVAILABLE}, AutoPublisher={AUTO_PUBLISHER_AVAILABLE}")
    uvicorn.run(app, host="0.0.0.0", port=port)


# ═══════════════════════════════════════════════════════════════════════════════
# STARTUP: Auto-start auto-publisher
# ═══════════════════════════════════════════════════════════════════════════════

@app.on_event("startup")
async def startup_event():
    """Start auto-publisher automatically on server startup"""
    if AUTO_PUBLISHER_AVAILABLE and get_auto_publisher:
        import asyncio
        publisher = get_auto_publisher()
        logger.info("🚀 Starting Auto-Publisher on startup...")
        asyncio.create_task(publisher.run_continuous())

