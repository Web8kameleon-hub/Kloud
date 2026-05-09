#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║  BLERINA PILLAR CONTENT ENGINE                                                ║
║  Part of Kloud Cloud Industrial Backend                                    ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  Features:                                                                    ║
║  - Pillar Article Generation (3000-5000 words)                               ║
║  - Quality Gate Integration                                                   ║
║  - YouTube Channel Management                                                 ║
║  - Video Generator Integration                                                ║
║  - LLM-powered Content via Ollama                                            ║
╚═══════════════════════════════════════════════════════════════════════════════╝

Port: 8035
Date: 2026-02-09
Author: Ledjan Ahmati (CEO, ABA GmbH)
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
import re
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# ═══════════════════════════════════════════════════════════════════════════════
# LOGGING
# ═══════════════════════════════════════════════════════════════════════════════

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("Blerina")

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

PORT = int(os.getenv("PORT", "8035"))
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
MODEL = os.getenv("MODEL", "llama3.1:8b")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
YOUTUBE_CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID", "UCuCd7kgikh6CM2hAh5eAIMA")
VIDEO_GENERATOR_URL = os.getenv("VIDEO_GENERATOR_URL", "http://localhost:8029")

# Storage
PILLARS_DIR = Path(os.getenv("PILLARS_DIR", "./generated_pillars"))
PILLARS_DIR.mkdir(exist_ok=True)

# ═══════════════════════════════════════════════════════════════════════════════
# QUALITY STANDARDS
# ═══════════════════════════════════════════════════════════════════════════════

MIN_PILLAR_WORDS = 3000
MAX_PILLAR_WORDS = 5000
MIN_QUALITY_SCORE = 0.85
MIN_SUPPORTING_WORDS = 800

# Patterns to detect fake content
FAKE_IMPORT_PATTERNS = [
    r"from kloud\.alda import",
    r"from kloud\.liam import",
    r"from kloud_sdk import",
    r"from neural_mesh import",
    r"from tide_engine import",
]

FAKE_DATA_PATTERNS = [
    r"\| Example \| 42 \|",
    r"Example:\s*42",
    r"accuracy:\s*99\.9%",
    r"lorem ipsum",
]


# ═══════════════════════════════════════════════════════════════════════════════
# ENUMS & DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════

class PillarTopic(str, Enum):
    """Strategic pillar topics - deep dive articles"""
    EEG_CLINICAL_VALIDATION = "eeg_clinical_validation"
    ALDA_ARCHITECTURE = "alda_architecture"
    REALTIME_SIGNAL_PROCESSING = "realtime_signal_processing"
    EU_AI_ACT_COMPLIANCE = "eu_ai_act_compliance"
    EDGE_AI_MEDICAL = "edge_ai_medical"
    HIPAA_ML_PIPELINES = "hipaa_ml_pipelines"
    BCI_FUNDAMENTALS = "bci_fundamentals"
    NEURAL_SIGNAL_PROCESSING = "neural_signal_processing"


class ContentType(str, Enum):
    """Types of content Blerina generates"""
    PILLAR_ARTICLE = "pillar_article"       # 3000-5000 words
    SUPPORTING_BLOG = "supporting_blog"      # 800-1500 words
    VIDEO_SCRIPT = "video_script"            # For video generator
    SOCIAL_THREAD = "social_thread"          # LinkedIn/Twitter
    NEWSLETTER = "newsletter"                # Email content


class ContentStatus(str, Enum):
    """Content generation status"""
    PENDING = "pending"
    GENERATING = "generating"
    QUALITY_CHECK = "quality_check"
    APPROVED = "approved"
    REJECTED = "rejected"
    PUBLISHED = "published"


@dataclass
class QualityReport:
    """Report from quality validation"""
    passed: bool
    score: float
    word_count: int
    has_real_code: bool
    has_real_metrics: bool
    has_fake_imports: bool
    has_fake_data: bool
    issues: List[str]
    recommendations: List[str]


@dataclass
class PillarContent:
    """Generated pillar content"""
    id: str
    topic: PillarTopic
    title: str
    content: str
    word_count: int
    sections: List[str]
    status: ContentStatus
    quality_report: Optional[QualityReport]
    created_at: str
    published_at: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════════════════
# PILLAR DEFINITIONS - Deep Content Structure
# ═══════════════════════════════════════════════════════════════════════════════

PILLAR_DEFINITIONS: Dict[PillarTopic, Dict[str, Any]] = {
    PillarTopic.EEG_CLINICAL_VALIDATION: {
        "title": "Clinical Validation of EEG Algorithms: From Research to Production",
        "target_words": 4000,
        "sections": [
            "Introduction: The Gap Between Lab and Clinic",
            "Regulatory Landscape: FDA, MDR, and ISO 62304",
            "Our Validation Framework: Real Code Examples",
            "Case Study: ALBI Engine Clinical Trials",
            "Statistical Methods: Beyond Simple Accuracy",
            "Reproducibility and Audit Trails",
            "Lessons Learned: What Went Wrong and How We Fixed It",
            "Conclusion: Building Trust Through Transparency",
        ],
        "real_code_files": ["albi_core.py", "eeg_validator.py"],
        "supporting_pieces": [
            {"type": "blog", "title": "What is FDA 510(k) and Why It Matters for AI"},
            {"type": "video", "title": "ALBI Engine: 60-Second Demo"},
            {"type": "code_tutorial", "title": "Building an EEG Validation Pipeline"},
            {"type": "social_thread", "title": "5 Things We Learned Validating EEG Algorithms"},
        ],
    },
    PillarTopic.ALDA_ARCHITECTURE: {
        "title": "ALDA: Artificial Labor Dependency Architecture - A Deep Technical Dive",
        "target_words": 4500,
        "sections": [
            "Introduction: Why We Built ALDA",
            "The Problem: Scaling AI Operations at Enterprise Level",
            "Architecture Overview: Components and Data Flow",
            "ArtificialLaborEngine: The Core Implementation",
            "LIAM: Labor Intelligence Array Matrix",
            "Real Production Metrics: What We Actually Measure",
            "Scaling Challenges and Solutions",
            "Code Walkthrough: alda_core.py Explained",
            "Lessons for Building Your Own AI Operations Platform",
        ],
        "real_code_files": ["alda_core.py", "liam_core.py"],
        "supporting_pieces": [
            {"type": "blog", "title": "What is LIAM and How Does It Work?"},
            {"type": "video", "title": "ALDA Architecture in 2 Minutes"},
            {"type": "code_tutorial", "title": "Setting Up ALDA From Scratch"},
        ],
    },
    PillarTopic.BCI_FUNDAMENTALS: {
        "title": "Brain-Computer Interfaces: A Complete Technical Guide",
        "target_words": 4000,
        "sections": [
            "What is a Brain-Computer Interface?",
            "EEG Fundamentals: Recording Brain Activity",
            "Signal Processing Pipeline",
            "Machine Learning for BCI",
            "Real-time Processing Challenges",
            "Our ALBI Engine Implementation",
            "Clinical Applications",
            "Future Directions",
        ],
        "real_code_files": ["albi_core.py", "signal_processing_core.py"],
        "supporting_pieces": [
            {"type": "blog", "title": "EEG Frequency Bands Explained"},
            {"type": "video", "title": "How BCIs Read Your Mind"},
        ],
    },
    PillarTopic.NEURAL_SIGNAL_PROCESSING: {
        "title": "Real-Time Neural Signal Processing: Architecture and Implementation",
        "target_words": 3500,
        "sections": [
            "Introduction to Neural Signals",
            "Sampling and Digitization",
            "Filtering Techniques: IIR vs FIR",
            "Artifact Removal: EOG, EMG, and Motion",
            "Feature Extraction Methods",
            "Real-Time Constraints and Latency",
            "Our Production Pipeline",
            "Benchmarks and Performance",
        ],
        "real_code_files": ["signal_processing_core.py"],
        "supporting_pieces": [
            {"type": "blog", "title": "Understanding EEG Artifacts"},
            {"type": "video", "title": "Signal Processing Pipeline Demo"},
        ],
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# STORAGE
# ═══════════════════════════════════════════════════════════════════════════════

START_TIME = time.time()
PILLARS_GENERATED: List[PillarContent] = []
SUPPORTING_CONTENT: List[Dict[str, Any]] = []
GENERATION_QUEUE: List[Dict[str, Any]] = []


# ═══════════════════════════════════════════════════════════════════════════════
# FASTAPI APP
# ═══════════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="BLERINA - Pillar Content Engine",
    description="Generates high-quality pillar articles (3000-5000 words) with quality gate",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ═══════════════════════════════════════════════════════════════════════════════
# PYDANTIC MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class PillarRequest(BaseModel):
    """Request to generate a pillar article"""
    topic: str = Field(..., description="Pillar topic or custom topic")
    custom_title: Optional[str] = Field(None, description="Custom title override")
    target_words: int = Field(default=4000, ge=3000, le=6000)
    include_code: bool = Field(default=True)
    generate_supporting: bool = Field(default=True)


class ContentResponse(BaseModel):
    """Response with content generation result"""
    job_id: str
    status: str
    message: str
    estimated_time_minutes: int


class QualityCheckRequest(BaseModel):
    """Request to quality check content"""
    content: str
    content_type: str = "pillar_article"


# ═══════════════════════════════════════════════════════════════════════════════
# QUALITY GATE
# ═══════════════════════════════════════════════════════════════════════════════

def validate_content_quality(content: str, content_type: ContentType) -> QualityReport:
    """
    Validate content against quality standards.
    Returns detailed quality report.
    """
    issues: List[str] = []
    recommendations: List[str] = []
    
    # Word count
    words = len(content.split())
    
    if content_type == ContentType.PILLAR_ARTICLE:
        if words < MIN_PILLAR_WORDS:
            issues.append(f"Word count ({words}) below minimum ({MIN_PILLAR_WORDS})")
            recommendations.append("Expand sections with more detail and examples")
        if words > MAX_PILLAR_WORDS:
            issues.append(f"Word count ({words}) above maximum ({MAX_PILLAR_WORDS})")
    
    # Check for fake imports
    has_fake_imports = False
    for pattern in FAKE_IMPORT_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            has_fake_imports = True
            issues.append(f"Contains fake import pattern: {pattern}")
    
    # Check for fake data
    has_fake_data = False
    for pattern in FAKE_DATA_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            has_fake_data = True
            issues.append(f"Contains fake data pattern: {pattern}")
    
    # Check for real code indicators
    has_real_code = bool(re.search(r"```python|```typescript|def \w+\(|async def|class \w+:", content))
    if not has_real_code:
        issues.append("No real code examples found")
        recommendations.append("Add actual code snippets from the codebase")
    
    # Check for real metrics
    has_real_metrics = bool(re.search(r"\d+\.\d+ms|\d+\s*requests/s|\d+%\s*accuracy", content, re.IGNORECASE))
    
    # Calculate score
    score = 1.0
    score -= 0.1 * len(issues)
    score -= 0.2 if has_fake_imports else 0
    score -= 0.15 if has_fake_data else 0
    score += 0.1 if has_real_code else 0
    score += 0.05 if has_real_metrics else 0
    score = max(0.0, min(1.0, score))
    
    passed = score >= MIN_QUALITY_SCORE and not has_fake_imports
    
    return QualityReport(
        passed=passed,
        score=score,
        word_count=words,
        has_real_code=has_real_code,
        has_real_metrics=has_real_metrics,
        has_fake_imports=has_fake_imports,
        has_fake_data=has_fake_data,
        issues=issues,
        recommendations=recommendations,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# LLM INTEGRATION (OLLAMA)
# ═══════════════════════════════════════════════════════════════════════════════

async def generate_with_llm(prompt: str, max_tokens: int = 4000) -> str:
    """Generate content using Ollama LLM"""
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                f"{OLLAMA_HOST}/api/generate",
                json={
                    "model": MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": max_tokens,
                        "temperature": 0.7,
                    }
                }
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("response", "")
            else:
                logger.error(f"Ollama error: {response.status_code}")
                return ""
    except Exception as e:
        logger.error(f"LLM generation error: {e}")
        return ""


async def generate_pillar_article(topic: PillarTopic, title: str, sections: List[str]) -> str:
    """Generate a complete pillar article with multiple sections"""
    
    full_content = f"# {title}\n\n"
    full_content += "*Author: Ledjan Ahmati, CEO of ABA GmbH*\n"
    full_content += f"*Published: {datetime.now(timezone.utc).strftime('%B %d, %Y')}*\n\n"
    
    # Generate each section
    for i, section in enumerate(sections):
        logger.info(f"Generating section {i+1}/{len(sections)}: {section}")
        
        prompt = f"""You are an expert technical writer for Kloud Cloud, a company that builds 
Brain-Computer Interface (BCI) and EEG processing systems.

Write section "{section}" for the pillar article "{title}".

Requirements:
- Write 400-600 words for this section
- Use technical but accessible language
- Include specific details, not generic claims
- If discussing code, use REAL patterns from Python/FastAPI
- Include real-world examples and metrics
- DO NOT use placeholder data like "Example: 42"
- DO NOT invent fake libraries or imports
- Reference actual technologies: NumPy, SciPy, MNE-Python, PyTorch, FastAPI

Section content:"""

        section_content = await generate_with_llm(prompt, max_tokens=1000)
        
        if section_content:
            full_content += f"\n## {section}\n\n{section_content}\n"
        else:
            # Fallback with pre-written content
            full_content += f"\n## {section}\n\n*[Content generation in progress...]*\n"
        
        # Small delay to avoid overwhelming Ollama
        await asyncio.sleep(1)
    
    return full_content


# ═══════════════════════════════════════════════════════════════════════════════
# VIDEO GENERATOR INTEGRATION
# ═══════════════════════════════════════════════════════════════════════════════

async def trigger_video_generation(topic: str, title: str) -> Optional[str]:
    """Trigger video generation for supporting content"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{VIDEO_GENERATOR_URL}/generate",
                json={
                    "topic": topic,
                    "title": title,
                    "style": "educational",
                }
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("job_id")
    except Exception as e:
        logger.warning(f"Video generator not available: {e}")
    return None


# ═══════════════════════════════════════════════════════════════════════════════
# BACKGROUND TASKS
# ═══════════════════════════════════════════════════════════════════════════════

async def process_pillar_generation(job_id: str, request: PillarRequest) -> None:
    """Process pillar article generation in background"""
    logger.info(f"Starting pillar generation: {job_id}")
    
    # Find topic definition
    topic_enum = None
    for t in PillarTopic:
        if t.value == request.topic or request.topic.lower() in t.value:
            topic_enum = t
            break
    
    if topic_enum and topic_enum in PILLAR_DEFINITIONS:
        definition = PILLAR_DEFINITIONS[topic_enum]
        title = request.custom_title or definition["title"]
        sections = definition["sections"]
    else:
        # Custom topic
        topic_enum = PillarTopic.BCI_FUNDAMENTALS  # Default
        title = request.custom_title or f"Deep Dive: {request.topic}"
        sections = [
            "Introduction",
            "Background and Context",
            "Technical Overview",
            "Implementation Details",
            "Real-World Applications",
            "Best Practices",
            "Conclusion",
        ]
    
    # Generate content
    content = await generate_pillar_article(topic_enum, title, sections)
    word_count = len(content.split())
    
    # Quality check
    quality_report = validate_content_quality(content, ContentType.PILLAR_ARTICLE)
    
    status = ContentStatus.APPROVED if quality_report.passed else ContentStatus.REJECTED
    
    # Store pillar
    pillar = PillarContent(
        id=job_id,
        topic=topic_enum,
        title=title,
        content=content,
        word_count=word_count,
        sections=sections,
        status=status,
        quality_report=quality_report,
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    
    PILLARS_GENERATED.append(pillar)
    
    # Save to file
    output_file = PILLARS_DIR / f"{job_id}.md"
    output_file.write_text(content, encoding="utf-8")
    
    # Also save metadata
    meta_file = PILLARS_DIR / f"{job_id}.json"
    meta_file.write_text(json.dumps({
        "id": job_id,
        "topic": topic_enum.value,
        "title": title,
        "word_count": word_count,
        "status": status.value,
        "quality_score": quality_report.score,
        "quality_passed": quality_report.passed,
        "issues": quality_report.issues,
        "created_at": pillar.created_at,
    }, indent=2), encoding="utf-8")
    
    logger.info(f"Pillar generated: {job_id} - {word_count} words, quality={quality_report.score:.2f}")
    
    # Trigger supporting content generation
    if request.generate_supporting and topic_enum in PILLAR_DEFINITIONS:
        for piece in PILLAR_DEFINITIONS[topic_enum].get("supporting_pieces", []):
            if piece["type"] == "video":
                video_job = await trigger_video_generation(request.topic, piece["title"])
                if video_job:
                    logger.info(f"Triggered video generation: {video_job}")


# ═══════════════════════════════════════════════════════════════════════════════
# API ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "BLERINA Pillar Engine v2.0",
        "youtube_configured": bool(YOUTUBE_API_KEY),
        "ollama_host": OLLAMA_HOST,
        "documents_processed": len(PILLARS_GENERATED),
        "narratives_generated": sum(1 for p in PILLARS_GENERATED if p.status == ContentStatus.APPROVED),
        "uptime_seconds": time.time() - START_TIME,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/status")
async def get_status():
    """Detailed service status"""
    approved = [p for p in PILLARS_GENERATED if p.status == ContentStatus.APPROVED]
    rejected = [p for p in PILLARS_GENERATED if p.status == ContentStatus.REJECTED]
    
    return {
        "service": "BLERINA - Pillar Content Engine",
        "version": "2.0.0",
        "status": "operational",
        "config": {
            "min_pillar_words": MIN_PILLAR_WORDS,
            "max_pillar_words": MAX_PILLAR_WORDS,
            "min_quality_score": MIN_QUALITY_SCORE,
            "ollama_model": MODEL,
        },
        "statistics": {
            "pillars_total": len(PILLARS_GENERATED),
            "pillars_approved": len(approved),
            "pillars_rejected": len(rejected),
            "avg_word_count": sum(p.word_count for p in PILLARS_GENERATED) / len(PILLARS_GENERATED) if PILLARS_GENERATED else 0,
            "avg_quality_score": sum(p.quality_report.score for p in PILLARS_GENERATED if p.quality_report) / len(PILLARS_GENERATED) if PILLARS_GENERATED else 0,
        },
        "youtube": {
            "configured": bool(YOUTUBE_API_KEY),
            "channel_id": YOUTUBE_CHANNEL_ID,
        },
        "uptime_hours": (time.time() - START_TIME) / 3600,
    }


@app.get("/api/v1/topics")
async def list_topics():
    """List available pillar topics"""
    return {
        "topics": [
            {
                "id": topic.value,
                "title": PILLAR_DEFINITIONS.get(topic, {}).get("title", topic.value),
                "target_words": PILLAR_DEFINITIONS.get(topic, {}).get("target_words", 4000),
                "sections_count": len(PILLAR_DEFINITIONS.get(topic, {}).get("sections", [])),
            }
            for topic in PillarTopic
            if topic in PILLAR_DEFINITIONS
        ]
    }


@app.post("/api/v1/pillars/generate", response_model=ContentResponse)
async def generate_pillar(request: PillarRequest, background_tasks: BackgroundTasks):
    """Generate a new pillar article (3000-5000 words)"""
    job_id = f"pillar_{hashlib.sha256(f'{request.topic}{time.time()}'.encode()).hexdigest()[:12]}"
    
    # Add to background queue
    background_tasks.add_task(process_pillar_generation, job_id, request)
    
    return ContentResponse(
        job_id=job_id,
        status="pending",
        message=f"Pillar generation started for topic: {request.topic}",
        estimated_time_minutes=10,  # LLM generation takes time
    )


@app.get("/api/v1/pillars")
async def list_pillars():
    """List all generated pillars"""
    return {
        "total": len(PILLARS_GENERATED),
        "pillars": [
            {
                "id": p.id,
                "topic": p.topic.value,
                "title": p.title,
                "word_count": p.word_count,
                "status": p.status.value,
                "quality_score": p.quality_report.score if p.quality_report else None,
                "created_at": p.created_at,
            }
            for p in PILLARS_GENERATED
        ]
    }


@app.get("/api/v1/pillars/{pillar_id}")
async def get_pillar(pillar_id: str):
    """Get a specific pillar article"""
    for pillar in PILLARS_GENERATED:
        if pillar.id == pillar_id:
            return {
                "id": pillar.id,
                "topic": pillar.topic.value,
                "title": pillar.title,
                "content": pillar.content,
                "word_count": pillar.word_count,
                "sections": pillar.sections,
                "status": pillar.status.value,
                "quality_report": {
                    "passed": pillar.quality_report.passed,
                    "score": pillar.quality_report.score,
                    "issues": pillar.quality_report.issues,
                    "recommendations": pillar.quality_report.recommendations,
                } if pillar.quality_report else None,
                "created_at": pillar.created_at,
            }
    raise HTTPException(status_code=404, detail="Pillar not found")


@app.post("/api/v1/quality/check")
async def check_quality(request: QualityCheckRequest):
    """Run quality check on content"""
    content_type = ContentType.PILLAR_ARTICLE
    try:
        content_type = ContentType(request.content_type)
    except ValueError:
        pass
    
    report = validate_content_quality(request.content, content_type)
    
    return {
        "passed": report.passed,
        "score": report.score,
        "word_count": report.word_count,
        "has_real_code": report.has_real_code,
        "has_real_metrics": report.has_real_metrics,
        "has_fake_imports": report.has_fake_imports,
        "has_fake_data": report.has_fake_data,
        "issues": report.issues,
        "recommendations": report.recommendations,
    }


# Legacy endpoints for compatibility
@app.post("/api/v1/documents/analyze")
async def analyze_document_legacy(request: dict):
    """Legacy document analysis - redirects to quality check"""
    content = request.get("content", "")
    report = validate_content_quality(content, ContentType.PILLAR_ARTICLE)
    return {
        "document_id": f"doc_{len(PILLARS_GENERATED):04d}",
        "quality": "high" if report.passed else "low",
        "statistics": {
            "words": report.word_count,
            "quality_score": report.score,
        }
    }


@app.post("/api/v1/narratives/generate")
async def generate_narrative_legacy(request: dict, background_tasks: BackgroundTasks):
    """Legacy narrative generation - redirects to pillar generation"""
    topic = request.get("topic", "general")
    pillar_request = PillarRequest(topic=topic, custom_title=None, target_words=3000)
    return await generate_pillar(pillar_request, background_tasks)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    
    logger.info("=" * 70)
    logger.info("📖 BLERINA PILLAR CONTENT ENGINE v2.0")
    logger.info("=" * 70)
    logger.info(f"🔧 Port: {PORT}")
    logger.info(f"🤖 Ollama: {OLLAMA_HOST} (model: {MODEL})")
    logger.info(f"📺 YouTube: {'Configured' if YOUTUBE_API_KEY else 'Not configured'}")
    logger.info(f"🎬 Video Generator: {VIDEO_GENERATOR_URL}")
    logger.info(f"📁 Pillars Dir: {PILLARS_DIR}")
    logger.info("=" * 70)
    
    uvicorn.run(app, host="0.0.0.0", port=PORT)

