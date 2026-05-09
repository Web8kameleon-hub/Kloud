"""
OCEAN CORE 8030 API
===================
Standalone FastAPI application - completely isolated from main.py

Port: 8030
Features:
- Query endpoint (natural language → intelligent response)
- Data sources status
- Knowledge exploration
- Curiosity threads
"""

import os
import logging
from datetime import datetime
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio
from typing import Optional

# Language detection
try:
    from langdetect import detect, LangDetectException
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False
    logging.warning("langdetect not available - language detection disabled")

# Local imports
from data_sources import get_internal_data_sources
from query_processor import get_query_processor, QueryIntent
from knowledge_engine import get_knowledge_engine, KnowledgeResponse
from persona_router import PersonaRouter
from config import OCEAN_SYSTEM_PROMPT, LANGUAGE_CODES


async def get_knowledge_engine_hybrid(data_sources):
    """Create hybrid knowledge engine that only uses internal data"""
    # For now, use the standard knowledge engine but we'll filter external APIs
    # This is a wrapper that ensures no external data is used
    try:
        from knowledge_engine import KnowledgeEngine
        ke = KnowledgeEngine(data_sources, None)  # No external_apis_manager
        await ke.initialize()
        return ke
    except:
        # Fallback if full knowledge engine not available
        logger.info("Using lightweight knowledge engine for hybrid mode")
        return None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ocean_api")

# Initialize FastAPI app
app = FastAPI(
    title="Curiosity Ocean 8030",
    description="Universal Knowledge Aggregation Engine with 14 Expert Personas - Internal Data Only",
    version="4.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
internal_data_sources = None
persona_router = None
query_processor = None
knowledge_engine = None


def detect_language(text: str) -> Optional[str]:
    """
    Detect language of input text
    Returns ISO 639-1 language code (e.g., 'en', 'de', 'sq')
    """
    if not LANGDETECT_AVAILABLE:
        return None
    
    try:
        # Clean text for detection
        clean_text = text.strip().lower()
        if len(clean_text) < 3:
            return None
        
        detected = detect(clean_text)
        logger.debug(f"Detected language: {detected} for text: {clean_text[:50]}...")
        return detected
    except LangDetectException as e:
        logger.warning(f"Language detection failed: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in language detection: {e}")
        return None


def build_language_prompt(question: str, detected_lang: Optional[str] = None) -> str:
    """
    Build enhanced prompt with language instructions
    """
    # Detect language if not provided
    if detected_lang is None:
        detected_lang = detect_language(question)
    
    # Base prompt with system instructions
    enhanced_prompt = OCEAN_SYSTEM_PROMPT + "\n\n"
    
    # Add language-specific instruction
    if detected_lang and detected_lang in LANGUAGE_CODES:
        lang_name = LANGUAGE_CODES[detected_lang]
        enhanced_prompt += f"**USER LANGUAGE DETECTED: {lang_name} ({detected_lang})**\n"
        enhanced_prompt += f"IMPORTANT: You MUST respond ONLY in {lang_name}. Do not mix languages.\n\n"
    else:
        enhanced_prompt += "**USER LANGUAGE: Unknown - default to English**\n\n"
    
    # Add the actual question
    enhanced_prompt += f"**USER QUESTION:**\n{question}\n\n"
    enhanced_prompt += "**YOUR ANSWER (in the detected language):**\n"
    
    return enhanced_prompt


@app.on_event("startup")
async def startup_event():
    """Initialize all managers on startup"""
    global internal_data_sources, persona_router, query_processor, knowledge_engine
    
    logger.info("🌊 Ocean Core 8030 starting up with 14 personas...")
    
    try:
        # Initialize all managers in parallel
        internal_data_sources = get_internal_data_sources()
        persona_router = PersonaRouter()
        query_processor = await get_query_processor()
        
        # Try to use full knowledge engine, fallback to lightweight if not available
        try:
            knowledge_engine = await get_knowledge_engine_hybrid(internal_data_sources)
        except Exception as ke_error:
            logger.warning(f"Full knowledge engine not available: {ke_error}")
            knowledge_engine = None
        
        logger.info(f"✅ Ocean Core 8030 initialized successfully with {len(persona_router.mapping)} personas")
    except Exception as e:
        logger.error(f"❌ Ocean Core 8030 initialization failed: {e}")
        raise


@app.get("/")
async def root():
    """Root endpoint"""
    internal_data = internal_data_sources.get_all_data() if internal_data_sources else {}
    
    return {
        "service": "Curiosity Ocean 8030",
        "version": "4.0.0",
        "status": "operational",
        "personas": len(persona_router.mapping) if persona_router else 0,
        "data_sources": len(internal_data) if internal_data else 0,
        "description": "Universal Knowledge Aggregation Engine with 14 Expert Personas",
        "features": [
            "14 specialist personas",
            "Internal data sources only",
            "Query routing via personas",
            "Knowledge exploration",
            "Curiosity threads"
        ],
        "endpoints": [
            "GET /api/personas - List all 14 specialists",
            "POST /api/query - Query with persona routing",
            "GET /api/status - Service status",
            "GET /api/labs - Location lab data",
            "GET /api/agents - Agent telemetry",
            "GET /health - Health check"
        ]
    }


@app.get("/api/status")
async def get_status():
    """Get service status"""
    if not internal_data_sources:
        return {"status": "initializing"}
    
    try:
        internal_data = internal_data_sources.get_all_data()
        
        return {
            "service": "Curiosity Ocean 8030",
            "version": "4.0.0",
            "status": "operational",
            "initialized": True,
            "personas": len(persona_router.mapping),
            "timestamp": datetime.now().isoformat(),
            "data_sources": {
                "labs": len(internal_data.get("labs", [])),
                "agents": len(internal_data.get("agents", [])),
                "cycles": len(internal_data.get("cycles", [])),
                "metrics": len(internal_data.get("metrics", [])),
                "kpi": len(internal_data.get("kpi", []))
            },
            "components": {
                "persona_router": "operational",
                "internal_data_sources": "operational",
                "query_processor": "operational",
                "knowledge_engine": "operational"
            }
        }
    except Exception as e:
        logger.error(f"Status check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sources")
async def get_sources():
    """List available data sources (INTERNAL ONLY)"""
    if not internal_data_sources:
        raise HTTPException(status_code=503, detail="Service initializing")
    
    internal_data = internal_data_sources.get_all_data()
    
    return {
        "timestamp": datetime.now().isoformat(),
        "internal_sources": {
            "location_labs": {
                "description": "12 geographic laboratory network",
                "records": len(internal_data.get("labs", [])),
                "status": "operational"
            },
            "agent_telemetry": {
                "description": "5 intelligent agents (ALBA, ALBI, Blerina, AGIEM, ASI)",
                "records": len(internal_data.get("agents", [])),
                "status": "operational"
            },
            "cycle_engine": {
                "description": "Production cycle metrics",
                "records": len(internal_data.get("cycles", [])),
                "status": "operational"
            },
            "excel_dashboard": {
                "description": "Reporting service on port 8001",
                "status": "operational"
            },
            "system_metrics": {
                "description": "CPU, memory, disk via psutil",
                "records": len(internal_data.get("metrics", [])),
                "status": "operational"
            },
            "kpi_engine": {
                "description": "Business KPI metrics",
                "records": len(internal_data.get("kpi", [])),
                "status": "operational"
            }
        },
        "note": "ONLY internal Kloud APIs - NO external data sources"
    }


@app.get("/api/personas")
async def get_personas():
    """List all 14 specialist personas"""
    if not persona_router:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    personas_list = []
    for domain, keywords in persona_router.mapping.items():
        personas_list.append({
            "domain": domain,
            "keywords": keywords,
            "description": f"{domain} specialist analyst"
        })
    
    return {
        "total_personas": len(personas_list),
        "personas": personas_list,
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/query")
async def query_ocean(
    question: str = Query(..., description="Natural language question"),
    use_personas: bool = Query(True, description="Route through specialist personas"),
    limit_results: int = Query(5, description="Limit results per source")
):
    """
    Query Ocean with 14 Specialist Personas
    
    Routes to specialized analysts based on keywords:
    - Medical Science: brain, neuro, health, biology
    - LoRa IoT: lora, iot, sensor, gateway
    - Security: security, vulnerability, encrypted
    - Systems Architecture: api, infrastructure, system
    - Natural Science: physics, chemistry, energy, quantum
    - Industrial Process: cycle, production, factory
    - Business: kpi, revenue, growth, strategy
    - AGI Systems: agi, cognitive, autonomous
    - And 6 more specialized domains...
    """
    
    if not question or len(question.strip()) == 0:
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    if not query_processor or not knowledge_engine or not persona_router or not internal_data_sources:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        logger.info(f"🧠 Received query: {question}")
        
        # 0. Detect language and enhance prompt
        detected_lang = detect_language(question)
        if detected_lang:
            logger.info(f"🌐 Detected language: {detected_lang} ({LANGUAGE_CODES.get(detected_lang, 'Unknown')})")
        
        # Build enhanced prompt with language instructions
        enhanced_question = build_language_prompt(question, detected_lang)
        
        # 1. Get internal data
        internal_data = internal_data_sources.get_all_data()
        
        # 2. Route to specialist persona first (if enabled)
        persona_response = None
        if use_personas:
            persona = persona_router.route(question)
            persona_response = persona.answer(question, internal_data)
            logger.info(f"✅ Persona {persona.__class__.__name__} answered question")
        
        # 3. Process query with full knowledge engine
        processed = await query_processor.process(question)
        
        # 4. Generate comprehensive answer (with enhanced prompt)
        response = None
        if knowledge_engine:
            try:
                # Use enhanced question with language instructions
                response = await knowledge_engine.answer_query(enhanced_question, processed)
            except Exception as ke_error:
                logger.warning(f"Knowledge engine error: {ke_error}, using persona response")
        
        # If knowledge engine not available, create lightweight response
        if not response:
            response_dict = {
                "query": question,
                "intent": processed.intent.value if processed else "unknown",
                "response": persona_response or "Analyzed based on internal data sources",
                "persona_answer": persona_response if use_personas else None,
                "key_findings": [],
                "sources": {"internal": ["persona_analysis"], "external": []},
                "confidence": 0.8 if persona_response else 0.0,
                "processing_time_ms": 0,
                "curiosity_threads": [],
                "data_sources_used": ["internal_only"],
                "detected_language": detected_lang or "unknown",
                "language_name": LANGUAGE_CODES.get(detected_lang, "Unknown") if detected_lang else "Unknown",
                "timestamp": datetime.now().isoformat()
            }
        else:
            # Convert dataclass to dict
            response_dict = {
                "query": response.query,
                "intent": response.intent,
                "response": response.main_response,
                "persona_answer": persona_response if use_personas else None,
                "key_findings": response.key_findings,
                "sources": response.sources_cited,
                "confidence": response.confidence_score,
                "processing_time_ms": response.processing_time_ms,
                "curiosity_threads": [
                    {
                        "topic": thread.topic,
                        "question": thread.initial_question,
                        "related_topics": thread.related_topics,
                        "continue_with": thread.continue_suggestions,
                        "sources": thread.sources_used
                    }
                    for thread in response.curiosity_threads
                ],
                "data_sources_used": ["internal_only"],
                "detected_language": detected_lang or "unknown",
                "language_name": LANGUAGE_CODES.get(detected_lang, "Unknown") if detected_lang else "Unknown",
                "timestamp": response.timestamp
            }
        
        return response_dict
        
    except ValueError as e:
        logger.warning(f"Query validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Query processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/labs")
async def get_labs():
    """Get all location labs data"""
    if not internal_data_sources:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        internal_data = internal_data_sources.get_all_data()
        return {
            "labs": internal_data.get("labs", []),
            "total": len(internal_data.get("labs", [])),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Labs data error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/agents")
async def get_agents():
    """Get all agent telemetry"""
    if not internal_data_sources:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        internal_data = internal_data_sources.get_all_data()
        return {
            "agents": internal_data.get("agents", []),
            "total": len(internal_data.get("agents", [])),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Agents data error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/threads/{topic}")
async def get_curiosity_thread(topic: str):
    """Get curiosity threads for exploration"""
    
    if not topic:
        raise HTTPException(status_code=400, detail="Topic required")
    
    # Map common topics to threads
    threads_map = {
        "laboratory": {
            "topic": "Geographic Laboratory Networks",
            "related": ["Elbasan", "Tirana", "Durrës", "Shkodër", "Vlorë", "Korça"],
            "explore": [
                "What domains are most active?",
                "Which locations have highest quality data?",
                "What's the correlation between lab domains?",
                "How are labs interconnected across countries?"
            ]
        },
        "agents": {
            "topic": "Agent Intelligence & Decisions",
            "related": ["ALBA", "ALBI", "Blerina", "AGIEM", "ASI"],
            "explore": [
                "What are the top agent decisions?",
                "Which agent has highest confidence?",
                "What anomalies were detected?",
                "How do agents coordinate?"
            ]
        },
        "system": {
            "topic": "System Infrastructure & Performance",
            "related": ["CPU", "Memory", "Latency", "Uptime"],
            "explore": [
                "What are current metrics?",
                "Are there performance bottlenecks?",
                "How's resource utilization?",
                "What's the trend over time?"
            ]
        }
    }
    
    thread = threads_map.get(topic.lower())
    
    if not thread:
        raise HTTPException(status_code=404, detail=f"Topic '{topic}' not found")
    
    return {
        "topic": thread["topic"],
        "related_entities": thread["related"],
        "explore_further": thread["explore"],
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ocean-core-8030",
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info("🌊 Starting Curiosity Ocean 8030...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8030,
        log_level="info"
    )

