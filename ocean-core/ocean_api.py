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

import asyncio
import logging
import os
import time
from datetime import datetime

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles

# Binary protocol support (CBOR2, MessagePack)
try:
    import cbor2

    HAS_CBOR2 = True
except ImportError:
    HAS_CBOR2 = False

try:
    import msgpack

    HAS_MSGPACK = True
except ImportError:
    HAS_MSGPACK = False

# Local imports - NANOGRID: Minimal
# DISABLED: from query_processor import get_query_processor, QueryIntent
# DISABLED: from knowledge_engine import get_knowledge_engine, KnowledgeResponse
# DISABLED: from persona_router import PersonaRouter
# DISABLED: from laboratories import get_laboratory_network
# DISABLED: from real_data_engine import get_real_data_engine
# DISABLED: from specialized_chat_engine import get_specialized_chat, initialize_specialized_chat
# ORCHESTRATOR - Ollama only
from response_orchestrator_v5 import ResponseOrchestratorV5, get_orchestrator_v5

from data_sources import get_internal_data_sources as get_all_sources

# DISABLED: from autolearning_engine import get_autolearning_engine, AutolearningEngine
# DISABLED: Curiosity Algebra - creates loops
# from curiosity_algebra.api import router as curiosity_router


async def get_knowledge_engine_hybrid(data_sources):
    """Create hybrid knowledge engine that only uses internal data"""
    # For now, use the standard knowledge engine but we'll filter external APIs
    # This is a wrapper that ensures no external data is used
    try:
        from knowledge_engine import KnowledgeEngine

        if data_sources is None:
            logger.error("❌ Cannot initialize knowledge engine: data_sources is None!")
            return None

        logger.info("🧠 Initializing KnowledgeEngine with internal data sources...")
        ke = KnowledgeEngine(data_sources, None)  # No external_apis_manager

        if ke is None:
            logger.error("❌ KnowledgeEngine() returned None!")
            return None

        logger.info("⏳ Initializing knowledge engine...")
        await ke.initialize()
        logger.info("✅ Knowledge engine initialized successfully!")
        return ke
    except Exception as e:
        logger.error(f"❌ Error initializing hybrid knowledge engine: {type(e).__name__}: {str(e)}")
        import traceback

        logger.error(f"Traceback: {traceback.format_exc()}")
        return None


# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("ocean_api")

# API Version prefix - SECURITY REQUIREMENT
API_VERSION = "v1"
API_PREFIX = f"/api/{API_VERSION}"

# Initialize FastAPI app
app = FastAPI(
    title="Curiosity Ocean",
    description="Universal Knowledge Aggregation Engine with 14 Expert Personas - Internal Data Only",
    version="4.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DISABLED: Curiosity Algebra - creates loops
# app.include_router(curiosity_router)
# logger.info("✅ Curiosity Algebra System integrated - /api/curiosity endpoints active")

# Global instances - NANOGRID: Minimal
internal_data_sources = None
persona_router = None
query_processor = None
knowledge_engine = None
laboratory_network = None
real_data_engine = None
specialized_chat = None
orchestrator = None
autolearning_engine = None  # New: Autolearning Engine


@app.on_event("startup")
async def startup_event():
    """Initialize all managers on startup"""
    global \
        internal_data_sources, \
        persona_router, \
        query_processor, \
        knowledge_engine, \
        laboratory_network, \
        real_data_engine, \
        specialized_chat, \
        orchestrator

    logger.info("[OCEAN] Ocean Core 8030 starting up with 14 personas...")

    try:
        # Initialize all managers in parallel
        logger.info("→ Initializing internal data sources...")
        internal_data_sources = get_all_sources()

        if internal_data_sources is None:
            logger.error("❌ CRITICAL: get_all_sources() returned None!")
            raise RuntimeError("Failed to initialize data sources")

        logger.info(f"[OK] Data sources initialized")

        # NANOGRID: Minimal initialization - only what's needed
        persona_router = None  # DISABLED
        query_processor = None  # DISABLED - Ollama handles queries
        laboratory_network = None  # DISABLED
        real_data_engine = None  # DISABLED
        specialized_chat = None  # DISABLED
        knowledge_engine = None  # DISABLED
        autolearning_engine = None  # DISABLED

        # Initialize orchestrator v5 - ONLY OLLAMA
        logger.info("→ Initializing Orchestrator (Ollama only)...")
        orchestrator = get_orchestrator_v5()
        logger.info("🦙 [OK] Orchestrator ready - Ollama ONLY!")

        logger.info(f"✅ Ocean Core 8030 initialized - NANOGRID mode")
        logger.info(f"   - Ollama: ✅ Ready")
    except Exception as e:
        logger.error(f"❌ Ocean Core 8030 initialization failed: {type(e).__name__}: {str(e)}")
        import traceback

        logger.error(f"Traceback: {traceback.format_exc()}")
        raise


@app.get("/api/info")
@app.get(f"{API_PREFIX}/info")
async def api_info():
    """API info endpoint"""
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
            "Curiosity threads",
        ],
        "endpoints": [
            "GET /api/personas - List all 14 specialists",
            "POST /api/query - Query with persona routing",
            "GET /api/status - Service status",
            "GET /api/labs - Location lab data",
            "GET /api/agents - Agent telemetry",
            "GET /health - Health check",
        ],
    }


@app.get("/favicon.ico")
async def favicon():
    """Serve favicon - Ocean blue icon"""
    # Return a simple 1x1 pixel transparent GIF to prevent 404
    import base64

    # Minimal valid ICO (1x1 blue pixel)
    favicon_bytes = base64.b64decode(
        "AAABAAEAEBAAAAEAIABoBAAAFgAAACgAAAAQAAAAIAAAAAEAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
        "AAD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP//"
        "/wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP//"
        "/wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP//"
        "/wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP//"
        "/wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP//"
        "/wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP//"
        "/wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP//"
        "/wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP//"
        "/wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP//"
        "/wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP//"
        "/wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP//"
        "/wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP//"
        "/wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP//"
        "/wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP//"
        "/wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AAAA"
        "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    )
    from fastapi.responses import Response

    return Response(content=favicon_bytes, media_type="image/x-icon")


@app.get("/")
async def root_chat_ui():
    """Serve the specialized chat interface at root"""
    import os

    file_path = os.path.join(os.path.dirname(__file__), "specialized_chat.html")
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="text/html")
    return {"error": "Chat UI not found", "tip": "Try /api/info for API info"}


@app.get("/chat")
async def chat_ui():
    """Serve the specialized chat interface"""
    import os

    file_path = os.path.join(os.path.dirname(__file__), "specialized_chat.html")
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="text/html")
    else:
        return {"error": "Chat UI not found"}


@app.get("/status")
@app.get(f"{API_PREFIX}/status")
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
            "knowledge_engine": "operational" if knowledge_engine else "degraded",
            "timestamp": datetime.now().isoformat(),
            "data_sources": {
                "timestamp": internal_data.get("timestamp"),
                "source": internal_data.get("source"),
                "central_api_connected": internal_data.get("central_api_connected", False),
                "laboratories": len(internal_data.get("laboratories", {}).get("labs", [])),
                "system_metrics": len(internal_data.get("system_metrics", {})),
                "asi_status": bool(internal_data.get("asi_status")),
                "ocean_labs_list": len(internal_data.get("ocean_labs_list", {}).get("laboratories", [])),
                "ai_agents_status": len(internal_data.get("ai_agents_status", {})),
                "all_keys": list(internal_data.keys()),
            },
            "components": {
                "persona_router": "operational",
                "internal_data_sources": "operational",
                "query_processor": "operational",
                "knowledge_engine": "operational" if knowledge_engine else "not_initialized",
            },
        }
    except Exception as e:
        logger.error(f"Status check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(f"{API_PREFIX}/system-full")
async def get_full_system_status():
    """
    Get COMPLETE system status with ALL components:
    - 14 Personas
    - 23 Laboratories
    - 61 Alphabet Layers
    - 12 Backend Layers (0-12)
    - ASI Trinity (Alba/Albi/Jona)
    - Open Data Sources
    - Enforcement Manager
    - ML Manager
    - Cycle Engine
    """
    try:
        status = {
            "service": "Kloud Ocean Core",
            "version": "4.0.0 - Full Integration",
            "timestamp": datetime.now().isoformat(),
            "components": {},
        }

        # Personas
        status["components"]["personas"] = {
            "count": len(persona_router.mapping) if persona_router else 0,
            "status": "active" if persona_router else "unavailable",
            "list": list(persona_router.mapping.keys()) if persona_router else [],
        }

        # Laboratories
        if laboratory_network:
            labs = laboratory_network.get_all_labs()
            status["components"]["laboratories"] = {"count": len(labs), "status": "active", "locations": [lab.location for lab in labs[:5]]}
        else:
            status["components"]["laboratories"] = {"count": 0, "status": "unavailable"}

        # Orchestrator with Alphabet Layers & Universal Connector
        if orchestrator:
            status["components"]["orchestrator"] = {
                "status": "active",
                "alphabet_layers": orchestrator.alphabet_layers.alphabet["size"] if orchestrator.alphabet_layers else 0,
                "universal_connector": "connected"
                if hasattr(orchestrator, "universal_connector") and orchestrator.universal_connector
                else "not_connected",
            }

            # Get Universal Connector summary
            if hasattr(orchestrator, "universal_connector") and orchestrator.universal_connector:
                status["components"]["universal_system"] = orchestrator.universal_connector.get_system_summary()

        # Real Data Engine
        status["components"]["real_data_engine"] = {"status": "active" if real_data_engine else "unavailable"}

        # Knowledge Engine
        status["components"]["knowledge_engine"] = {"status": "active" if knowledge_engine else "degraded"}

        # Summary
        active_count = sum(1 for c in status["components"].values() if c.get("status") == "active" or c.get("status") == "connected")
        status["summary"] = {
            "total_components": len(status["components"]),
            "active_components": active_count,
            "health": "healthy" if active_count > 4 else "degraded",
        }

        return status

    except Exception as e:
        logger.error(f"Full system status error: {e}")
        return {"error": str(e), "status": "error"}


@app.get(f"{API_PREFIX}/sources")
async def get_sources():
    """List available data sources (INTERNAL ONLY)"""
    if not internal_data_sources:
        raise HTTPException(status_code=503, detail="Service initializing")

    internal_data = internal_data_sources.get_all_data()

    # REAL SOURCES from actual data
    return {
        "timestamp": datetime.now().isoformat(),
        "internal_sources_operational": list(internal_data.keys()),
        "central_api": {
            "url": internal_data.get("central_api_url", "http://localhost:8000"),
            "connected": internal_data.get("central_api_connected", False),
            "health": internal_data.get("health", {}),
            "status_code": internal_data.get("status"),
        },
        "laboratories_network": {
            "description": "23 Specialized Research Laboratories across EU",
            "total": internal_data.get("laboratories", {}).get("total_labs", 0),
            "list_count": len(internal_data.get("ocean_labs_list", {}).get("laboratories", [])),
            "status": "operational",
            "locations": [
                "Elbasan, Albania (AI)",
                "Tirana, Albania (Medical)",
                "Prishtina, Kosovo (Security)",
                "Vienna, Austria (Neuroscience)",
                "Zurich, Switzerland (Finance)",
                "Prague, Czech Republic (Robotics)",
                "Budapest, Hungary (Data)",
                "Ljubljana, Slovenia (Quantum)",
                "Zagreb, Croatia (Biotech)",
                "Sofia, Bulgaria (Chemistry)",
                "Beograd, Serbia (Industrial)",
                "Bucharest, Romania (Nanotechnology)",
                "Istanbul, Turkey (Trade)",
                "Cairo, Egypt (Archeology)",
                "Jerusalem, Palestine (Heritage)",
                "Rome, Italy (Architecture)",
                "Athens, Greece (Classical)",
                "Kostur, North Macedonia (Energy)",
                "Durrës, Albania (IoT)",
                "Shkodër, Albania (Marine)",
                "Vlorë, Albania (Environmental)",
                "Korça, Albania (Agricultural)",
                "Sarandë, Albania (Underwater)",
            ],
        },
        "agi_agents": {
            "description": "ASI Trinity - 3 Superintelligences",
            "alba": {
                "role": "Network Monitor",
                "health": internal_data.get("asi_status", {}).get("trinity", {}).get("alba", {}).get("health", 0),
                "operational": internal_data.get("asi_status", {}).get("trinity", {}).get("alba", {}).get("operational", False),
            },
            "albi": {
                "role": "Neural Processor",
                "health": internal_data.get("asi_status", {}).get("trinity", {}).get("albi", {}).get("health", 0),
                "operational": internal_data.get("asi_status", {}).get("trinity", {}).get("albi", {}).get("operational", False),
            },
            "jona": {
                "role": "Data Coordinator",
                "health": internal_data.get("asi_status", {}).get("trinity", {}).get("jona", {}).get("health", 0),
                "operational": internal_data.get("asi_status", {}).get("trinity", {}).get("jona", {}).get("operational", False),
            },
            "count": len(internal_data.get("ai_agents_status", {})),
            "status": "operational",
        },
        "system_metrics": {
            "description": "Real-time system health monitoring",
            "cpu_percent": internal_data.get("system_metrics", {}).get("cpu_percent"),
            "memory_percent": internal_data.get("system_metrics", {}).get("memory_percent"),
            "disk_percent": internal_data.get("system_metrics", {}).get("disk_percent"),
            "status": "operational",
        },
        "data_quality": {
            "laboratories": len(internal_data.get("laboratories", {}).get("labs", [])),
            "ocean_labs_list": len(internal_data.get("ocean_labs_list", {}).get("laboratories", [])),
            "ai_agents": len(internal_data.get("ai_agents_status", {})),
            "total_data_records": sum(
                [len(v) if isinstance(v, list) else (len(v) if isinstance(v, dict) else 1) for v in internal_data.values() if v]
            ),
        },
        "note": "✅ ONLY internal Kloud APIs - NO external data sources (Wikipedia, ArXiv, GitHub disabled)",
    }


def generate_key_findings(question: str, response: str) -> list:
    """Generate key findings from response"""
    findings = []

    # Extract sentences that look like findings
    if response:
        sentences = response.split(". ")
        for i, sentence in enumerate(sentences[:5]):  # Top 5 findings
            if len(sentence.strip()) > 20:
                findings.append({"finding": sentence.strip(), "importance": 0.8 - (i * 0.1), "source": "persona_analysis"})

    return findings


def generate_curiosity_threads(question: str, findings: list) -> list:
    """Generate curiosity threads for deeper exploration"""
    threads = []

    # Common curiosity thread patterns
    thread_templates = [
        {"title": "Deep Dive", "hook": f"Let's explore the underlying mechanisms behind: {question[:50]}...", "depth_level": "expert"},
        {"title": "Historical Context", "hook": f"How did our understanding of this topic evolve?", "depth_level": "medium"},
        {"title": "Practical Applications", "hook": f"How can we apply this knowledge in real-world scenarios?", "depth_level": "beginner"},
        {"title": "Related Concepts", "hook": f"What other topics are connected to this?", "depth_level": "medium"},
    ]

    return thread_templates[:3]  # Return top 3 threads


@app.get(f"{API_PREFIX}/personas")
async def get_personas():
    """List all 14 specialist personas"""
    if not persona_router:
        raise HTTPException(status_code=503, detail="Service not initialized")

    personas_list = []
    for domain, keywords in persona_router.mapping.items():
        personas_list.append({"domain": domain, "keywords": keywords, "description": f"{domain} specialist analyst"})

    return {"total_personas": len(personas_list), "personas": personas_list, "timestamp": datetime.now().isoformat()}


@app.post(f"{API_PREFIX}/query")
async def query_ocean(request: Request):
    """
    Query Ocean with 14 Specialist Personas

    Accepts JSON body with:
    - query: Natural language question (required)
    - use_personas: Route through specialist personas (default: true)
    - limit_results: Limit results per source (default: 5)

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

    # Parse JSON body
    try:
        body = await request.json()
    except Exception as e:
        logger.error(f"JSON parse error: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid JSON body: {str(e)}")

    question = body.get("query") or body.get("question") or ""
    use_personas = body.get("use_personas", True)
    curiosity_level = body.get("curiosity_level", "curious")

    # Start timing from 0.1ms precision
    start_time = time.perf_counter()

    if not question or len(question.strip()) == 0:
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    if not query_processor or not knowledge_engine or not persona_router or not internal_data_sources:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        logger.info(f"🧠 Received query: {question}")

        # 0. ORCHESTRATOR V5 (Brain with CLX/Knowledge Seeds) - First Priority!
        orchestrator_result = None
        if orchestrator:
            try:
                logger.info("🧠 Using Orchestrator v5 (CLX + Knowledge Seeds)...")
                orchestrator_result = await orchestrator.orchestrate(question)
                # OrchestratedResponse is a dataclass - use attributes, not .get()
                if orchestrator_result and hasattr(orchestrator_result, "fused_answer") and orchestrator_result.fused_answer:
                    sources = orchestrator_result.sources_cited if hasattr(orchestrator_result, "sources_cited") else []
                    source_str = sources[0] if sources else "orchestrator_v5"
                    logger.info(f"✅ Orchestrator v5 answered (source: {source_str})")
            except Exception as orch_err:
                logger.warning(f"Orchestrator v5 error: {orch_err}")

        # If orchestrator gave real answer, use it
        if orchestrator_result and hasattr(orchestrator_result, "fused_answer") and orchestrator_result.fused_answer:
            sources = orchestrator_result.sources_cited if hasattr(orchestrator_result, "sources_cited") else []
            response_source = sources[0] if sources else "orchestrator_v5"
            response_content = orchestrator_result.fused_answer
            confidence = orchestrator_result.confidence if hasattr(orchestrator_result, "confidence") else 0.9

            # Check if this is from CLX or Knowledge Seeds (not a fallback/template)
            is_real_answer = any(s.startswith(("clx", "knowledge_seed")) for s in sources) if sources else False

            if is_real_answer or (response_content and len(response_content) > 50):
                # Calculate elapsed time from 0.1ms to full response
                elapsed_ms = (time.perf_counter() - start_time) * 1000.0
                return {
                    "query": question,
                    "intent": str(orchestrator_result.query_category.value)
                    if hasattr(orchestrator_result, "query_category")
                    else "general",
                    "response": response_content,
                    "persona_answer": response_content,
                    "key_findings": [
                        {"finding": response_content[:500], "importance": 0.95, "source": response_source, "confidence": confidence}
                    ],
                    "sources": {"internal": sources, "external": []},
                    "confidence": confidence,
                    "processing_time_ms": round(elapsed_ms, 2),
                    "curiosity_threads": generate_curiosity_threads(question, []),
                    "data_sources_used": ["orchestrator_v5"] + sources,
                    "clx_used": any(s.startswith("clx") for s in sources),
                    "knowledge_seed_used": any(s.startswith("knowledge_seed") for s in sources),
                    "timestamp": datetime.now().isoformat(),
                }

        # 1. FALLBACK: Real laboratories data
        lab_data = None
        if real_data_engine:
            logger.info("🔬 Fallback: Querying real laboratories for data...")
            try:
                lab_data = await real_data_engine.get_comprehensive_response(question)
                logger.info(f"✅ Real labs returned {lab_data.get('total_labs_queried', 0)} responses")
            except Exception as e:
                logger.warning(f"⚠️  Real data engine error: {e}")

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

        # 4. Generate comprehensive answer
        response = None
        if knowledge_engine:
            try:
                response = await knowledge_engine.answer_query(question, processed)
            except Exception as ke_error:
                logger.warning(f"Knowledge engine error: {ke_error}, using persona response")

        # If knowledge engine not available, create lightweight response
        if not response:
            # Generate enhanced findings - use real lab data if available!
            if lab_data and lab_data.get("lab_responses"):
                # Use REAL lab data instead of generic findings
                key_findings = [
                    {
                        "finding": lab["answer"][:200] + "...",
                        "importance": lab["quality_score"],
                        "source": lab["lab_name"],
                        "lab_domain": lab["domain"],
                        "confidence": lab["confidence"],
                    }
                    for lab in lab_data.get("lab_responses", [])[:20]
                ]
            else:
                key_findings = generate_key_findings(question, persona_response)

            curiosity_threads = generate_curiosity_threads(question, key_findings)

            # Build ULTRA response with real lab data
            ultra_response = persona_response or "Analyzed based on internal data sources"
            if lab_data and lab_data.get("comprehensive_answer"):
                ultra_response = lab_data["comprehensive_answer"]

            # Calculate elapsed time from 0.1ms to full response
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0

            response_dict = {
                "query": question,
                "intent": processed.intent.value if processed else "unknown",
                "response": ultra_response,
                "persona_answer": persona_response if use_personas else None,
                "key_findings": key_findings,
                "sources": {"internal": ["persona_analysis", "real_laboratories"] if lab_data else ["persona_analysis"], "external": []},
                "confidence": lab_data.get("average_confidence", 0.75) if lab_data else (0.75 if persona_response else 0.5),
                "processing_time_ms": round(elapsed_ms, 2),
                "curiosity_threads": curiosity_threads,
                "data_sources_used": ["internal_only", "real_labs"] if lab_data else ["internal_only"],
                "labs_queried": lab_data.get("total_labs_queried", 0) if lab_data else 0,
                "real_lab_data": lab_data if lab_data else None,
                "timestamp": datetime.now().isoformat(),
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
                        "sources": thread.sources_used,
                    }
                    for thread in response.curiosity_threads
                ],
                "data_sources_used": ["internal_only"],
                "timestamp": response.timestamp,
            }

        return response_dict

    except ValueError as e:
        logger.warning(f"Query validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Query processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(f"{API_PREFIX}/chat/specialized")
async def specialized_chat_endpoint(request: Request):
    """
    Specialized Expert Chat - Clean Interface

    Returns real, expert answers in your advanced domains:
    - Neuroscience & Brain Research
    - AI/ML & Deep Learning
    - Quantum Physics & Energy
    - IoT/LoRa & Sensor Networks
    - Cybersecurity & Encryption
    - Bioinformatics & Genetics
    - Data Science & Analytics
    - Marine Biology & Environmental Science

    NO system status - JUST expert answers.
    """
    if not specialized_chat:
        raise HTTPException(status_code=503, detail="Specialized Chat Engine not initialized")

    try:
        body = await request.json()
        query = body.get("query", body.get("message", "")).strip()

        if not query:
            raise ValueError("Query cannot be empty")

        # Generate expert response
        response = await specialized_chat.generate_expert_response(query)

        return {
            "type": "specialized_chat",
            "query": query,
            "domain": response["domain"],
            "domain_expertise": response["domain_expertise"],
            "answer": response["answer"],
            "sources": response["sources"],
            "confidence": response["confidence"],
            "follow_up_topics": response["follow_up_topics"],
            "timestamp": response["timestamp"],
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Chat processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(f"{API_PREFIX}/chat/history")
async def get_chat_history(request: Request):
    """Get chat conversation history"""
    if not specialized_chat:
        raise HTTPException(status_code=503, detail="Specialized Chat Engine not initialized")

    try:
        body = await request.json()
        limit = body.get("limit", 20)

        history = specialized_chat.get_chat_history(limit)
        stats = specialized_chat.get_statistics()

        return {"messages": history, "statistics": stats, "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        logger.error(f"History retrieval error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(f"{API_PREFIX}/chat/clear")
async def clear_chat():
    """Clear chat history for new conversation"""
    if not specialized_chat:
        raise HTTPException(status_code=503, detail="Specialized Chat Engine not initialized")

    try:
        specialized_chat.clear_history()
        return {"status": "success", "message": "Chat history cleared", "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        logger.error(f"Clear history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(f"{API_PREFIX}/chat/spontaneous")
async def spontaneous_conversation(request: Request):
    """
    SPONTANEOUS CONVERSATION MODE
    ============================

    This is the NEW way to chat - with full context awareness!

    Features:
    - Understands references to previous discussion ("what we talked about")
    - Maintains conversation topic coherence
    - Adapts responses based on full conversation history
    - Can handle follow-ups and clarifications naturally
    - Natural multi-turn dialogue

    Returns:
    - context_aware: boolean (true if using previous context)
    - conversation_topic: the main topic being discussed
    - turn_number: which turn of conversation this is
    - follow_up_topics: context-aware suggestions

    Example flow:
    1. User: "Tell me about quantum computing"
    2. User: "How does error correction work?" → System remembers quantum context
    3. User: "And what about hardware?" → Continues quantum discussion
    """
    if not specialized_chat:
        raise HTTPException(status_code=503, detail="Specialized Chat Engine not initialized")

    try:
        body = await request.json()
        query = body.get("query", "").strip()
        use_context = body.get("use_context", True)  # Default: use conversation context

        if not query:
            raise ValueError("Query cannot be empty")

        # Generate spontaneous response with context awareness
        response = await specialized_chat.generate_spontaneous_response(query, use_context=use_context)

        return {
            "type": "spontaneous_chat",
            "query": response["query"],
            "domain": response["domain"],
            "domain_expertise": response["domain_expertise"],
            "answer": response["answer"],
            "sources": response["sources"],
            "confidence": response["confidence"],
            "follow_up_topics": response["follow_up_topics"],
            "context_aware": response["context_aware"],
            "conversation_topic": response["conversation_topic"],
            "turn_number": response["turn_number"],
            "timestamp": response["timestamp"],
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Spontaneous chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(f"{API_PREFIX}/chat")
async def chat_test(message: str = Query(default="Hello", description="Mesazhi për të testuar")):
    """
    GET CHAT ENDPOINT - Për testim në browser
    ==========================================

    Shembull: http://localhost:8030/api/chat?message=What%20is%20neuroplasticity
    """
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    try:
        logger.info(f"💬 GET chat test: {message[:50]}...")
        result = await orchestrator.process_query_async(message)

        # Extract intent and complexity from understanding
        understanding = result.understanding or {}
        intent = understanding.get("intent", "exploratory")
        complexity = understanding.get("complexity_level", "simple")

        return {
            "response": result.fused_answer,
            "sources": result.sources_cited,
            "confidence": result.confidence,
            "query_category": result.query_category.value if hasattr(result.query_category, "value") else str(result.query_category),
            "intent": intent,
            "complexity": complexity,
        }
    except Exception as e:
        logger.error(f"GET chat error: {e}")
        return {"response": f"Gabim: {e}", "sources": [], "confidence": 0.0, "intent": "error", "complexity": "unknown"}


@app.post(f"{API_PREFIX}/chat")
async def simple_chat(request: Request):
    """
    SIMPLE CHAT ENDPOINT - ORCHESTRATOR V5
    =======================================

    Fast path conversational - 100% lokal, pa API të jashtme.

    Body:
    {
        "message": "Përshëndetje! Si je?",
        "clerk_user_id": "user_xxx" (optional)
    }

    Returns:
    {
        "response": "Mirëdita! Jam mirë, faleminderit...",
        "sources": ["conversational_greeting"],
        "confidence": 0.98
    }
    """
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    try:
        body = await request.json()
        message = body.get("message", body.get("query", "")).strip()

        # Get user context from Clerk ID
        clerk_user_id = body.get("clerk_user_id") or request.headers.get("X-Clerk-User-Id")
        user_name = body.get("user_name")
        user_language = body.get("user_language", "sq")

        if not message:
            return {"response": "Ju lutem shkruani diçka për të vazhduar bisedën.", "sources": [], "confidence": 1.0}

        # Log with user context
        user_info = f"[User: {user_name or clerk_user_id or 'anonymous'}]" if clerk_user_id else ""
        logger.info(f"💬 Chat v5 {user_info}: {message[:50]}...")

        # Use Orchestrator v5 - fast conversational path
        # Pass user context for personalization
        result = await orchestrator.orchestrate(
            message,
            mode="conversational",
            user_context={"clerk_id": clerk_user_id, "name": user_name, "language": user_language} if clerk_user_id else None,
        )
        return {
            "response": result.fused_answer,
            "sources": result.sources_cited,
            "confidence": result.confidence,
            "language": result.language,
            "query_category": result.query_category.value if hasattr(result.query_category, "value") else str(result.query_category),
            "user_identified": bool(clerk_user_id),
        }

    except Exception as e:
        logger.error(f"Chat v5 error: {e}")
        return {"response": f"Ndodhi një gabim: {str(e)}. Ju lutem provoni përsëri.", "sources": [], "confidence": 0.0}


@app.post(f"{API_PREFIX}/chat/stream")
async def streaming_chat(request: Request):
    """
    STREAMING CHAT ENDPOINT - Real-time response
    =============================================

    Streams response tokens as they are generated by CLX.
    Text appears immediately instead of waiting for full response.

    Body:
    {
        "message": "Përshëndetje! Si je?"
    }

    Returns: SSE stream with chunks
    """
    from ollama_fast_engine import get_fast_engine

    try:
        body = await request.json()
        message = body.get("message", body.get("query", "")).strip()

        if not message:
            return StreamingResponse(iter(['data: {"error": "Message required"}\n\n']), media_type="text/event-stream")

        logger.info(f"🌊 Streaming chat: {message[:50]}...")

        async def generate_stream():
            engine = get_fast_engine()
            async for chunk in engine.generate_stream(message):
                # SSE format
                yield f'data: {{"chunk": "{chunk}"}}\n\n'
            yield "data: [DONE]\n\n"

        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"},
        )

    except Exception as e:
        logger.error(f"Streaming chat error: {e}")
        return StreamingResponse(iter([f'data: {{"error": "{str(e)}"}}\n\n']), media_type="text/event-stream")


@app.post(f"{API_PREFIX}/chat/binary")
async def binary_chat(request: Request):
    """
    BINARY CHAT ENDPOINT - CBOR2 / MessagePack
    ==========================================

    Pranon dhe kthen të dhëna në format binary (CBOR2 ose MessagePack).

    Content-Type pranuar:
    - application/cbor (CBOR2 - preferuar)
    - application/msgpack (MessagePack)
    - application/json (fallback)

    Returns: Same format as input (binary response)
    """
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    try:
        content_type = request.headers.get("content-type", "application/json")
        raw_body = await request.body()

        # Parse based on content type
        if "cbor" in content_type and HAS_CBOR2:
            body = cbor2.loads(raw_body)
            response_format = "cbor"
            logger.info("📦 CBOR2 request received")
        elif "msgpack" in content_type and HAS_MSGPACK:
            body = msgpack.loads(raw_body)
            response_format = "msgpack"
            logger.info("📦 MessagePack request received")
        else:
            import json

            body = json.loads(raw_body)
            response_format = "json"

        message = body.get("message", body.get("query", "")).strip()

        if not message:
            result_data = {"response": "Ju lutem shkruani diçka.", "sources": [], "confidence": 1.0, "format": response_format}
        else:
            logger.info(f"💬 Binary chat ({response_format}): {message[:50]}...")

            try:
                result = await orchestrator.process_query_async(message)
                result_data = {
                    "response": result.fused_answer,
                    "sources": result.sources_cited,
                    "confidence": result.confidence,
                    "query_category": result.query_category.value
                    if hasattr(result.query_category, "value")
                    else str(result.query_category),
                    "format": response_format,
                }
            except Exception as e:
                logger.warning(f"Async failed: {e}, using sync")
                result = orchestrator.process_query(message)
                result_data = {
                    "response": result.fused_answer,
                    "sources": result.sources_cited,
                    "confidence": result.confidence,
                    "format": response_format,
                }

        # Return in same format
        if response_format == "cbor" and HAS_CBOR2:
            return Response(content=cbor2.dumps(result_data), media_type="application/cbor")
        elif response_format == "msgpack" and HAS_MSGPACK:
            return Response(content=msgpack.dumps(result_data), media_type="application/msgpack")
        else:
            return result_data

    except Exception as e:
        logger.error(f"Binary chat error: {e}")
        error_data = {"response": f"Gabim: {str(e)}", "sources": [], "confidence": 0.0}
        return error_data


@app.post(f"{API_PREFIX}/chat/orchestrated")
async def orchestrated_response(request: Request):
    """
    ORCHESTRATED RESPONSE - ORCHESTRATOR V5 (DEEP MODE)
    ====================================================

    Deep mode - përdor edhe ekspertë kur ka sens.
    100% LOKAL - pa API të jashtme me pagesë.

    Features:
    - RealAnswerEngine (fast path)
    - Minimal experts (1 persona + 1 lab + 1 module)
    - Multilingual support
    - Timeouts për ekspertët
    """
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator v5 not initialized")

    try:
        body = await request.json()
        query = body.get("query", body.get("message", "")).strip()
        conversation_context = body.get("conversation_context", [])
        mode = body.get("mode", "deep")  # Default: deep mode për orchestrated

        if not query:
            raise ValueError("Query cannot be empty")

        logger.info(f"🧠 Orchestrator v5 ({mode}): {query[:60]}...")

        # Check Autolearning Engine for cached responses
        knowledge_id = None
        if autolearning_engine:
            learning_result = autolearning_engine.process_query(query)

            # Use cached if high-confidence
            if learning_result.get("cached_knowledge"):
                cached = learning_result["cached_knowledge"]
                if cached.get("helpfulness", 0) > 0.7 and cached.get("confidence", 0) > 0.85:
                    logger.info(f"   ✅ Using learned response")
                    return {
                        "type": "learned_response",
                        "query": query,
                        "query_category": "learned",
                        "fused_answer": cached["response"],
                        "sources_cited": ["autolearning"],
                        "confidence": cached["confidence"],
                        "timestamp": datetime.utcnow().isoformat(),
                    }

            # Use pattern response if available
            if learning_result.get("pattern_response"):
                return {
                    "type": "pattern_response",
                    "query": query,
                    "query_category": learning_result["pattern_type"],
                    "fused_answer": learning_result["pattern_response"],
                    "sources_cited": ["pattern_detector"],
                    "confidence": 0.95,
                    "timestamp": datetime.utcnow().isoformat(),
                }

        # Use Orchestrator v5
        orchestrated = await orchestrator.orchestrate(query, conversation_context, mode=mode)

        # Learn from response
        if autolearning_engine:
            knowledge_id = autolearning_engine.learn_from_response(
                query=query, response=orchestrated.fused_answer, sources=orchestrated.sources_cited, confidence=orchestrated.confidence
            )

        return {
            "type": "orchestrated_v5",
            "query": orchestrated.query,
            "query_category": orchestrated.query_category.value,
            "language": orchestrated.language,
            "understanding": orchestrated.understanding,
            "consulted_experts": [
                {
                    "type": c.expert_type,
                    "name": c.expert_name,
                    "confidence": c.confidence,
                    "relevance": c.relevance_score,
                }
                for c in orchestrated.consulted_experts
            ],
            "fused_answer": orchestrated.fused_answer,
            "sources_cited": orchestrated.sources_cited,
            "confidence": orchestrated.confidence,
            "narrative_quality": orchestrated.narrative_quality,
            "learning_record": {"knowledge_id": knowledge_id} if knowledge_id else {},
            "timestamp": orchestrated.timestamp,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Orchestrator v5 error: {e}")
        import traceback

        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@app.get(f"{API_PREFIX}/orchestrator/learning")
async def get_orchestrator_learning():
    """Get the learning stats from orchestrator v5"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator v5 not initialized")

    try:
        stats = orchestrator.get_stats()
        return {
            "type": "orchestrator_v5_stats",
            "version": stats.get("version", "v5"),
            "engine_active": stats.get("engine_active", False),
            "learning_history_count": stats.get("learning_history_count", 0),
            "expert_timeout_ms": stats.get("expert_timeout_ms", 500),
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Orchestrator stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(f"{API_PREFIX}/autolearning/stats")
async def get_autolearning_stats():
    """
    Get Autolearning Engine statistics

    Shows:
    - Total knowledge entries learned
    - Top queries used
    - Pattern statistics
    - Session learning info
    """
    if not autolearning_engine:
        raise HTTPException(status_code=503, detail="Autolearning Engine not initialized")

    try:
        stats = autolearning_engine.get_learning_stats()
        return {
            "type": "autolearning_stats",
            "knowledge_base": stats["knowledge_base"],
            "patterns": stats["patterns"],
            "session": stats["session"],
            "independence": {
                "internal_sources": True,
                "external_api_dependency": False,
                "description": "Sistemi mëson dhe funksionon pa varësi nga API të jashtme",
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Autolearning stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(f"{API_PREFIX}/autolearning/feedback")
async def autolearning_feedback(request: Request):
    """
    Record user feedback for a response

    Body:
    - knowledge_id: ID of the knowledge entry
    - helpful: true/false
    """
    if not autolearning_engine:
        raise HTTPException(status_code=503, detail="Autolearning Engine not initialized")

    try:
        body = await request.json()
        knowledge_id = body.get("knowledge_id")
        helpful = body.get("helpful", True)

        if not knowledge_id:
            raise ValueError("knowledge_id is required")

        autolearning_engine.record_feedback(knowledge_id, helpful)

        return {
            "status": "recorded",
            "knowledge_id": knowledge_id,
            "feedback": "helpful" if helpful else "not_helpful",
            "message": "Faleminderit për feedback-un! Sistemi do të mësojë nga kjo.",
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Feedback error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(f"{API_PREFIX}/chat/domains")
async def get_domains():
    """Get available expertise domains"""
    if not specialized_chat:
        raise HTTPException(status_code=503, detail="Specialized Chat Engine not initialized")

    domains = {}
    for domain_name, domain_info in specialized_chat.EXPERTISE_DOMAINS.items():
        domains[domain_name] = {
            "focus": domain_info["focus"],
            "expertise_level": domain_info["expertise_level"],
            "keywords": domain_info["keywords"][:5],  # Show first 5 keywords
            "labs": domain_info["labs"],
        }

    return {
        "domains": domains,
        "total_domains": len(domains),
        "total_labs": len(set(lab for d in domains.values() for lab in d["labs"])),
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get(f"{API_PREFIX}/labs")
async def get_labs():
    """Get all location labs data"""
    if not laboratory_network:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        labs_dicts = laboratory_network.get_all_labs()
        # labs_dicts is already a list of dicts from get_all_labs()
        return {"labs": labs_dicts, "total": len(labs_dicts), "timestamp": datetime.now().isoformat()}
    except Exception as e:
        logger.error(f"Labs data error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(f"{API_PREFIX}/agents")
async def get_agents():
    """Get all agent telemetry"""
    if not internal_data_sources:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        internal_data = internal_data_sources.get_all_data()
        return {
            "agents": internal_data.get("agents", []),
            "total": len(internal_data.get("agents", [])),
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Agents data error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(API_PREFIX + "/threads/{topic}")
async def get_curiosity_thread(topic: str):
    """Get curiosity threads for exploration"""

    if not topic:
        raise HTTPException(status_code=400, detail="Topic required")

    # Map common topics to threads
    threads_map = {
        "laboratory": {
            "topic": "Geographic Laboratory Networks",
            "related": ["Elbasan", "Tirana", "Durrës", "Shkodër", "Vlorë", "Korça", "Sarandë", "Zürich", "Roma"],
            "explore": [
                "What domains are most active?",
                "Which locations have highest quality data?",
                "What's the correlation between lab domains?",
                "How are labs interconnected across countries?",
            ],
        },
        "agents": {
            "topic": "Agent Intelligence & Decisions",
            "related": ["ALBA", "ALBI", "Blerina", "AGIEM", "ASI"],
            "explore": [
                "What are the top agent decisions?",
                "Which agent has highest confidence?",
                "What anomalies were detected?",
                "How do agents coordinate?",
            ],
        },
        "system": {
            "topic": "System Infrastructure & Performance",
            "related": ["CPU", "Memory", "Latency", "Uptime"],
            "explore": [
                "What are current metrics?",
                "Are there performance bottlenecks?",
                "How's resource utilization?",
                "What's the trend over time?",
            ],
        },
    }

    thread = threads_map.get(topic.lower())

    if not thread:
        raise HTTPException(status_code=404, detail=f"Topic '{topic}' not found")

    return {
        "topic": thread["topic"],
        "related_entities": thread["related"],
        "explore_further": thread["explore"],
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "ocean-core-8030", "timestamp": datetime.now().isoformat()}


# =============================================================================
# AI PROCESSING ENDPOINTS
# =============================================================================


@app.post(f"{API_PREFIX}/ai/sentiment")
async def analyze_sentiment(request: Request):
    """
    Analyze sentiment and emotions in text

    Body: {"text": "Your text here", "use_llm": true}
    """
    try:
        from ai_processes import get_sentiment_analyzer

        data = await request.json()
        text = data.get("text", "")
        use_llm = data.get("use_llm", True)

        if not text:
            raise HTTPException(status_code=400, detail="Text is required")

        analyzer = get_sentiment_analyzer()
        await analyzer.initialize()
        result = await analyzer.analyze(text, use_llm=use_llm)

        return {"success": True, "result": result.to_dict(), "timestamp": datetime.now().isoformat()}
    except Exception as e:
        logger.error(f"Sentiment analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(f"{API_PREFIX}/ai/summarize")
async def summarize_text(request: Request):
    """
    Generate summary of text

    Body: {"text": "Long text...", "type": "hybrid", "target_ratio": 0.3}
    Types: extractive, abstractive, hybrid, bullet_points, tldr
    """
    try:
        from ai_processes import get_text_summarizer, SummaryType

        data = await request.json()
        text = data.get("text", "")
        summary_type = data.get("type", "hybrid")
        target_ratio = data.get("target_ratio", 0.3)
        max_sentences = data.get("max_sentences", 5)

        if not text:
            raise HTTPException(status_code=400, detail="Text is required")

        # Map string to enum
        type_map = {
            "extractive": SummaryType.EXTRACTIVE,
            "abstractive": SummaryType.ABSTRACTIVE,
            "hybrid": SummaryType.HYBRID,
            "bullet_points": SummaryType.BULLET_POINTS,
            "tldr": SummaryType.TLDR,
        }
        stype = type_map.get(summary_type, SummaryType.HYBRID)

        summarizer = get_text_summarizer()
        await summarizer.initialize()
        result = await summarizer.summarize(text, summary_type=stype, target_ratio=target_ratio, max_sentences=max_sentences)

        return {"success": True, "result": result.to_dict(), "timestamp": datetime.now().isoformat()}
    except Exception as e:
        logger.error(f"Summarization error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(f"{API_PREFIX}/ai/entities")
async def extract_entities(request: Request):
    """
    Extract named entities from text (NER)

    Body: {"text": "Text with names, places, dates...", "use_llm": true}
    """
    try:
        from ai_processes import get_entity_extractor

        data = await request.json()
        text = data.get("text", "")
        use_llm = data.get("use_llm", True)

        if not text:
            raise HTTPException(status_code=400, detail="Text is required")

        extractor = get_entity_extractor()
        await extractor.initialize()
        result = await extractor.extract(text, use_llm=use_llm)

        return {"success": True, "result": result.to_dict(), "timestamp": datetime.now().isoformat()}
    except Exception as e:
        logger.error(f"Entity extraction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(f"{API_PREFIX}/ai/classify")
async def classify_text(request: Request):
    """
    Classify text into categories

    Body: {"text": "Text to classify...", "use_llm": true}
    """
    try:
        from ai_processes import get_text_classifier

        data = await request.json()
        text = data.get("text", "")
        use_llm = data.get("use_llm", True)

        if not text:
            raise HTTPException(status_code=400, detail="Text is required")

        classifier = get_text_classifier()
        await classifier.initialize()
        result = await classifier.classify(text, use_llm=use_llm)

        return {"success": True, "result": result.to_dict(), "timestamp": datetime.now().isoformat()}
    except Exception as e:
        logger.error(f"Classification error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(f"{API_PREFIX}/ai/analyze-code")
async def analyze_code(request: Request):
    """
    Analyze source code structure and quality

    Body: {"code": "def hello():\\n    pass", "language": "python"}
    """
    try:
        from ai_processes import get_code_analyzer

        data = await request.json()
        code = data.get("code", "")
        language = data.get("language")  # Optional, auto-detect if not provided

        if not code:
            raise HTTPException(status_code=400, detail="Code is required")

        analyzer = get_code_analyzer()
        await analyzer.initialize()
        result = await analyzer.analyze(code, language=language)

        return {"success": True, "result": result.to_dict(), "timestamp": datetime.now().isoformat()}
    except Exception as e:
        logger.error(f"Code analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(f"{API_PREFIX}/ai/detect-language")
async def detect_language(request: Request):
    """
    Detect language of text

    Body: {"text": "Përshëndetje, si jeni?"}
    """
    try:
        from ai_processes import get_language_detector

        data = await request.json()
        text = data.get("text", "")

        if not text:
            raise HTTPException(status_code=400, detail="Text is required")

        detector = get_language_detector()
        await detector.initialize()
        result = await detector.detect(text)

        return {"success": True, "result": result.to_dict(), "timestamp": datetime.now().isoformat()}
    except Exception as e:
        logger.error(f"Language detection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(f"{API_PREFIX}/ai/intent")
async def classify_intent(request: Request):
    """
    Classify user intent from message

    Body: {"message": "I want to order a pizza", "use_llm": true}
    """
    try:
        from ai_processes import get_intent_classifier

        data = await request.json()
        message = data.get("message", "")
        use_llm = data.get("use_llm", True)

        if not message:
            raise HTTPException(status_code=400, detail="Message is required")

        classifier = get_intent_classifier()
        await classifier.initialize()
        result = await classifier.classify(message, use_llm=use_llm)

        return {"success": True, "result": result.to_dict(), "timestamp": datetime.now().isoformat()}
    except Exception as e:
        logger.error(f"Intent classification error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(f"{API_PREFIX}/ai/process")
async def unified_ai_process(request: Request):
    """
    Unified AI processing endpoint - run multiple analyses at once

    Body: {
        "text": "Text to analyze...",
        "processes": ["sentiment", "entities", "language", "classify"]
    }
    """
    try:
        from ai_processes import (
            get_sentiment_analyzer,
            get_entity_extractor,
            get_language_detector,
            get_text_classifier,
            get_text_summarizer,
            get_intent_classifier,
        )

        data = await request.json()
        text = data.get("text", "")
        processes = data.get("processes", ["sentiment", "language"])

        if not text:
            raise HTTPException(status_code=400, detail="Text is required")

        results = {}

        if "sentiment" in processes:
            analyzer = get_sentiment_analyzer()
            await analyzer.initialize()
            results["sentiment"] = (await analyzer.analyze(text)).to_dict()

        if "entities" in processes:
            extractor = get_entity_extractor()
            await extractor.initialize()
            results["entities"] = (await extractor.extract(text)).to_dict()

        if "language" in processes:
            detector = get_language_detector()
            await detector.initialize()
            results["language"] = (await detector.detect(text)).to_dict()

        if "classify" in processes:
            classifier = get_text_classifier()
            await classifier.initialize()
            results["classification"] = (await classifier.classify(text)).to_dict()

        if "summarize" in processes:
            summarizer = get_text_summarizer()
            await summarizer.initialize()
            results["summary"] = (await summarizer.summarize(text)).to_dict()

        if "intent" in processes:
            intent_clf = get_intent_classifier()
            await intent_clf.initialize()
            results["intent"] = (await intent_clf.classify(text)).to_dict()

        return {
            "success": True,
            "text_preview": text[:200] + "..." if len(text) > 200 else text,
            "processes_run": list(results.keys()),
            "results": results,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Unified AI processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(f"{API_PREFIX}/ai/capabilities")
async def ai_capabilities():
    """List all available AI processing capabilities"""
    return {
        "capabilities": [
            {
                "name": "sentiment",
                "endpoint": f"{API_PREFIX}/ai/sentiment",
                "method": "POST",
                "description": "Sentiment and emotion analysis",
            },
            {"name": "summarize", "endpoint": f"{API_PREFIX}/ai/summarize", "method": "POST", "description": "Text summarization"},
            {"name": "entities", "endpoint": f"{API_PREFIX}/ai/entities", "method": "POST", "description": "Named Entity Recognition"},
            {"name": "classify", "endpoint": f"{API_PREFIX}/ai/classify", "method": "POST", "description": "Text classification"},
            {"name": "analyze-code", "endpoint": f"{API_PREFIX}/ai/analyze-code", "method": "POST", "description": "Source code analysis"},
            {
                "name": "detect-language",
                "endpoint": f"{API_PREFIX}/ai/detect-language",
                "method": "POST",
                "description": "Language detection",
            },
            {"name": "intent", "endpoint": f"{API_PREFIX}/ai/intent", "method": "POST", "description": "User intent classification"},
            {"name": "process", "endpoint": f"{API_PREFIX}/ai/process", "method": "POST", "description": "Unified multi-process analysis"},
        ],
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
    }


# =============================================================================
# END AI PROCESSING ENDPOINTS
# =============================================================================


@app.get(f"{API_PREFIX}/spec")
async def api_spec():
    """OpenAPI specification"""
    return app.openapi()


@app.get("/api/chat")
async def api_chat_redirect():
    """Redirect to chat UI"""
    return FileResponse("specialized_chat.html", media_type="text/html")


@app.get("/api/status")
async def api_status_short():
    """Short status endpoint without version"""
    return {"service": "Curiosity Ocean", "version": "4.0.0", "status": "operational", "timestamp": datetime.now().isoformat()}


@app.get(f"{API_PREFIX}/laboratories")
async def get_all_laboratories():
    """Get all 23 specialized laboratories with their functions"""
    try:
        lab_network = get_laboratory_network()
        return {
            "total_laboratories": len(lab_network.labs),
            "laboratories": lab_network.get_all_labs(),
            "network_stats": lab_network.get_network_stats(),
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Laboratories data error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(f"{API_PREFIX}/laboratories/summary")
async def get_laboratories_summary():
    """Get summary of all 23 laboratories"""
    try:
        lab_network = get_laboratory_network()
        return lab_network.get_all_labs_summary()
    except Exception as e:
        logger.error(f"Laboratories summary error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(f"{API_PREFIX}/laboratories/types")
async def get_laboratory_types():
    """Get all unique laboratory types"""
    try:
        lab_network = get_laboratory_network()
        return {"types": lab_network.get_lab_types(), "count": len(lab_network.get_lab_types()), "timestamp": datetime.now().isoformat()}
    except Exception as e:
        logger.error(f"Laboratory types error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(API_PREFIX + "/laboratories/{lab_id}")
async def get_laboratory(lab_id: str):
    """Get specific laboratory by ID"""
    try:
        lab_network = get_laboratory_network()
        lab = lab_network.get_lab_by_id(lab_id)

        if not lab:
            raise HTTPException(status_code=404, detail=f"Laboratory '{lab_id}' not found")

        return {"laboratory": lab.to_dict(), "status_summary": lab.get_status_summary(), "timestamp": datetime.now().isoformat()}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Laboratory lookup error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(API_PREFIX + "/laboratories/type/{lab_type}")
async def get_laboratories_by_type(lab_type: str):
    """Get laboratories by type"""
    try:
        lab_network = get_laboratory_network()
        labs = lab_network.get_labs_by_type(lab_type)

        if not labs:
            raise HTTPException(status_code=404, detail=f"No laboratories of type '{lab_type}' found")

        return {
            "type": lab_type,
            "count": len(labs),
            "laboratories": [lab.to_dict() for lab in labs],
            "timestamp": datetime.now().isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Laboratory type lookup error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(API_PREFIX + "/laboratories/location/{location}")
async def get_laboratories_by_location(location: str):
    """Get laboratories by location"""
    try:
        lab_network = get_laboratory_network()
        labs = lab_network.get_labs_by_location(location)

        if not labs:
            raise HTTPException(status_code=404, detail=f"No laboratories in '{location}' found")

        return {
            "location": location,
            "count": len(labs),
            "laboratories": [lab.to_dict() for lab in labs],
            "timestamp": datetime.now().isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Laboratory location lookup error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(API_PREFIX + "/laboratories/function/{keyword}")
async def get_laboratories_by_function(keyword: str):
    """Get laboratories by function keyword"""
    try:
        lab_network = get_laboratory_network()
        labs = lab_network.get_labs_by_function_keyword(keyword)

        if not labs:
            raise HTTPException(status_code=404, detail=f"No laboratories with function containing '{keyword}' found")

        return {
            "keyword": keyword,
            "count": len(labs),
            "laboratories": [lab.to_dict() for lab in labs],
            "timestamp": datetime.now().isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Laboratory function lookup error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# MEGA SIGNAL INTEGRATOR ENDPOINTS
# =============================================================================


@app.get(f"{API_PREFIX}/signals/overview")
async def get_signals_overview():
    """
    🌊 MEGA SIGNAL SYSTEM OVERVIEW

    Returns status of all signal managers:
    - Cycles, Alignments, Proposals
    - Kubernetes, CI/CD
    - News, Data Sources (5000+ from 200+ countries)
    """
    try:
        from mega_signal_integrator import get_mega_signal_integrator

        integrator = get_mega_signal_integrator()
        overview = integrator.get_system_overview()

        return {"type": "mega_signal_overview", "status": "connected", "overview": overview, "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        logger.error(f"Mega Signal overview error: {e}")
        return {"type": "mega_signal_overview", "status": "error", "error": str(e), "timestamp": datetime.utcnow().isoformat()}


@app.post(f"{API_PREFIX}/signals/query")
async def query_signals(request: Request):
    """
    🔍 QUERY MEGA SIGNAL SYSTEM

    Ask about cycles, alignments, proposals, kubernetes,
    data sources, and more!
    """
    try:
        from mega_signal_integrator import get_mega_signal_integrator

        integrator = get_mega_signal_integrator()

        body = await request.json()
        query = body.get("query", body.get("message", "")).strip()

        if not query:
            raise ValueError("Query cannot be empty")

        result = await integrator.process_query(query)

        return {
            "type": "mega_signal_query",
            "query": query,
            "response": result.get("response", ""),
            "sources_checked": result.get("sources_checked", []),
            "signals": result.get("signals", []),
            "timestamp": datetime.utcnow().isoformat(),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Mega Signal query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(f"{API_PREFIX}/signals/cycles")
async def get_cycles():
    """Get all active cycles"""
    try:
        from mega_signal_integrator import get_mega_signal_integrator

        integrator = get_mega_signal_integrator()
        cycles = integrator.cycle_manager.get_active_cycles()

        return {"type": "cycles", "count": len(cycles), "cycles": cycles, "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        logger.error(f"Cycles error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(f"{API_PREFIX}/signals/cycles")
async def create_cycle(request: Request):
    """Create a new cycle"""
    try:
        from mega_signal_integrator import get_mega_signal_integrator

        integrator = get_mega_signal_integrator()

        body = await request.json()
        domain = body.get("domain", "general")
        source = body.get("source", "api")
        interval = body.get("interval_seconds", 300)

        signal = integrator.cycle_manager.create_cycle(domain, source, interval)

        return {
            "type": "cycle_created",
            "signal": {"id": signal.signal_id, "message": signal.message, "data": signal.data},
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Create cycle error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(f"{API_PREFIX}/signals/proposals")
async def create_proposal(request: Request):
    """Create a new proposal"""
    try:
        from mega_signal_integrator import get_mega_signal_integrator

        integrator = get_mega_signal_integrator()

        body = await request.json()
        title = body.get("title", "New Proposal")
        domain = body.get("domain", "general")
        description = body.get("description", "")

        signal = integrator.proposal_manager.create_proposal(title, domain, description)

        return {
            "type": "proposal_created",
            "signal": {"id": signal.signal_id, "message": signal.message, "data": signal.data},
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Create proposal error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(f"{API_PREFIX}/signals/kubernetes")
async def get_kubernetes_status():
    """Get Kubernetes cluster status"""
    try:
        from mega_signal_integrator import get_mega_signal_integrator

        integrator = get_mega_signal_integrator()
        signal = integrator.devops_manager.get_kubernetes_status()

        return {"type": "kubernetes_status", "message": signal.message, "data": signal.data, "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        logger.error(f"Kubernetes status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(f"{API_PREFIX}/signals/data-sources")
async def get_data_sources_summary():
    """
    🌍 GET 5000+ DATA SOURCES FROM 200+ COUNTRIES

    Returns summary of all available data sources:
    - EEG/Neuro (OpenNeuro, PhysioNet)
    - Scientific (PubMed, ArXiv, NCBI)
    - Statistics EU (Eurostat, Destatis, INSEE)
    - Statistics Asia (China NBS, Japan, Korea)
    - Finance (ECB, IMF, World Bank, CoinGecko)
    - Environment (Copernicus, NASA, NOAA)
    - Health (WHO, CDC, ECDC)
    - News (NewsAPI, Guardian, NY Times)
    - IoT (FIWARE, Smart Data Models)
    - International (UN Data, WTO, ILO, FAO)
    """
    try:
        from mega_signal_integrator import get_mega_signal_integrator

        integrator = get_mega_signal_integrator()
        signal = integrator.news_data_manager.get_data_sources_summary()

        return {
            "type": "data_sources",
            "message": signal.message,
            "total_sources": signal.data.get("total", 0),
            "categories": signal.data.get("categories", {}),
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Data sources error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(f"{API_PREFIX}/signals/data-sources/search")
async def search_data_sources(query: str = Query(..., description="Search query for data sources")):
    """Search data sources by keyword"""
    try:
        from mega_signal_integrator import get_mega_signal_integrator

        integrator = get_mega_signal_integrator()
        results = integrator.news_data_manager.search_sources(query)

        return {
            "type": "data_sources_search",
            "query": query,
            "count": len(results),
            "results": results,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Data sources search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(f"{API_PREFIX}/signals/lora")
async def get_lora_status():
    """
    📡 GET LORA/LORAWAN NETWORK STATUS

    Returns status of LoRa gateways and nodes.
    Low-power wide-area network for IoT.
    """
    try:
        from mega_signal_integrator import get_mega_signal_integrator

        integrator = get_mega_signal_integrator()
        signal = integrator.lora_manager.get_network_status()

        return {"type": "lora_status", "message": signal.message, "data": signal.data, "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        logger.error(f"LoRa status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(f"{API_PREFIX}/signals/lora/nodes")
async def register_lora_node(request: Request):
    """Register a new LoRa node"""
    try:
        from mega_signal_integrator import get_mega_signal_integrator

        integrator = get_mega_signal_integrator()

        body = await request.json()
        node_id = body.get("node_id", f"node_{datetime.utcnow().timestamp()}")
        node_type = body.get("node_type", "sensor")
        metadata = body.get("metadata", {})

        signal = integrator.lora_manager.register_node(node_id, node_type, metadata)

        return {
            "type": "lora_node_registered",
            "signal": {"id": signal.signal_id, "message": signal.message, "data": signal.data},
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"LoRa node registration error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(f"{API_PREFIX}/signals/nanogrid")
async def get_nanogrid_status():
    """
    🔌 GET NANOGRID GATEWAY STATUS

    Returns status of embedded devices:
    - ESP32 (WiFi, BLE, I2C)
    - STM32 (LoRa, UART, DMA)
    - ASIC (LoRa, UART)
    - Raspberry Pi
    """
    try:
        from mega_signal_integrator import get_mega_signal_integrator

        integrator = get_mega_signal_integrator()
        signal = integrator.nanogrid_manager.get_gateway_status()

        return {"type": "nanogrid_status", "message": signal.message, "data": signal.data, "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        logger.error(f"Nanogrid status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(f"{API_PREFIX}/signals/nanogrid/devices")
async def register_nanogrid_device(request: Request):
    """Register a new Nanogrid device"""
    try:
        from mega_signal_integrator import get_mega_signal_integrator

        integrator = get_mega_signal_integrator()

        body = await request.json()
        device_id = body.get("device_id", f"dev_{datetime.utcnow().timestamp()}")
        model = body.get("model", "CUSTOM_IOT")
        metadata = body.get("metadata", {})

        signal = integrator.nanogrid_manager.register_device(device_id, model, metadata)

        return {
            "type": "nanogrid_device_registered",
            "signal": {"id": signal.signal_id, "message": signal.message, "data": signal.data},
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Nanogrid device registration error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(f"{API_PREFIX}/signals/nanogrid/telemetry")
async def receive_telemetry(request: Request):
    """Receive telemetry from Nanogrid device"""
    try:
        from mega_signal_integrator import get_mega_signal_integrator

        integrator = get_mega_signal_integrator()

        body = await request.json()
        device_id = body.get("device_id")
        payload = body.get("payload", {})

        if not device_id:
            raise ValueError("device_id is required")

        signal = integrator.nanogrid_manager.process_telemetry(device_id, payload)

        return {
            "type": "telemetry_received",
            "signal": {"id": signal.signal_id, "message": signal.message},
            "timestamp": datetime.utcnow().isoformat(),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Telemetry error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(f"{API_PREFIX}/signals/nodes")
async def get_nodes_status():
    """Get nodes, arrays, and buffers status"""
    try:
        from mega_signal_integrator import get_mega_signal_integrator

        integrator = get_mega_signal_integrator()
        status = integrator.node_array_manager.get_status()

        return {"type": "node_array_status", "data": status, "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        logger.error(f"Nodes status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(f"{API_PREFIX}/signals/formats")
async def get_data_formats():
    """
    📦 GET SUPPORTED DATA FORMATS

    Returns info about supported formats:
    - CBOR (39% smaller than JSON)
    - JSON (human readable)
    - YAML (config files)
    - MsgPack (30% smaller than JSON)
    """
    try:
        from mega_signal_integrator import get_mega_signal_integrator

        integrator = get_mega_signal_integrator()
        signal = integrator.format_manager.get_all_formats()

        return {"type": "data_formats", "message": signal.message, "formats": signal.data, "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        logger.error(f"Formats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("OCEAN_PORT", 8030))
    logger.info(f"🌊 Starting Curiosity Ocean on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
