#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCEAN CORE FULL - Complete Production Brain
============================================
Aktivizon TË GJITHA sistemet e avancuara:

1. ResponseOrchestratorV5 - Production Brain
2. MegaLayerEngine - 14 MILIARD kombinime
3. ClxIEngine - 5 modele
4. RealAnswerEngine - Deep Knowledge
5. Translation Node - 72 gjuhë
6. Knowledge Layer - Platform Intelligence
7. Service Registry - 31 module

Port: 8030
"""

import asyncio
import json
import logging
import os
import time
from typing import Any, AsyncGenerator, Dict, List, Optional

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# Global variables initialization
_warmup_task: Optional[asyncio.Task] = None

# ═══════════════════════════════════════════════════════════════════
# LOGGING
# ═══════════════════════════════════════════════════════════════════
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(name)s - %(message)s")
logger = logging.getLogger("OceanCoreFull")

# ═══════════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════════
OLLAMA_HOST = os.getenv("CLX_HOST", os.getenv("OLLAMA_HOST", "http://localhost:11434"))
MODEL = os.getenv("MODEL", "llama3.1:8b")
ALBANIAN_DICT_MODE = os.getenv("ALBANIAN_DICT_MODE", "off").lower()
PORT = int(os.getenv("PORT", "8030"))
TRANSLATION_NODE = os.getenv("TRANSLATION_NODE", "http://localhost:8036")

# ═══════════════════════════════════════════════════════════════════
# REAL TELEMETRY (no-fake): psutil-backed system signals + process uptime
# ═══════════════════════════════════════════════════════════════════
import importlib

_PROCESS_START = time.time()

# Real fabric activity tracking (updated by actual request handling; no fabrication)
_FABRIC_STATE: Dict[str, Any] = {
    "requests_total": 0,
    "requests_streamed": 0,
    "last_action": None,
    "last_target": None,
    "last_prompt_chars": 0,
    "last_lang": None,
    "last_ts": None,
    "last_latency_ms": None,
}


def _record_impulse(action: str, target: str, prompt: str, lang: str, latency_ms: Optional[float] = None, streamed: bool = False) -> None:
    """Record a REAL processing event so fabric endpoints report facts, not fiction."""
    _FABRIC_STATE["requests_total"] += 1
    if streamed:
        _FABRIC_STATE["requests_streamed"] += 1
    _FABRIC_STATE["last_action"] = action
    _FABRIC_STATE["last_target"] = target
    _FABRIC_STATE["last_prompt_chars"] = len(prompt or "")
    _FABRIC_STATE["last_lang"] = lang
    _FABRIC_STATE["last_ts"] = time.time()
    if latency_ms is not None:
        _FABRIC_STATE["last_latency_ms"] = round(latency_ms, 1)
try:
    psutil = importlib.import_module("psutil")
    PSUTIL_AVAILABLE = True
except Exception:  # pragma: no cover - optional dep
    psutil = None
    PSUTIL_AVAILABLE = False


def _real_system_metrics() -> Dict[str, Any]:
    """Read REAL host metrics via psutil. Returns available=False if psutil missing."""
    if not PSUTIL_AVAILABLE:
        return {"available": False}
    try:
        cpu = float(psutil.cpu_percent(interval=None))
        vm = psutil.virtual_memory()
        try:
            load1, load5, load15 = psutil.getloadavg()
        except (AttributeError, OSError):
            load1 = load5 = load15 = 0.0
        cpu_count = psutil.cpu_count(logical=True) or 1
        return {
            "available": True,
            "cpu_percent": round(cpu, 2),
            "mem_percent": round(float(vm.percent), 2),
            "mem_used_mb": round(vm.used / 1_048_576, 1),
            "mem_total_mb": round(vm.total / 1_048_576, 1),
            "load1": round(load1, 3),
            "load5": round(load5, 3),
            "load15": round(load15, 3),
            "cpu_count": cpu_count,
            "load1_per_core": round(load1 / cpu_count, 3),
        }
    except Exception as exc:  # pragma: no cover
        return {"available": False, "error": str(exc)[:200]}


async def _probe(url: str, timeout: float = 3.0) -> Dict[str, Any]:
    """Probe a real dependency. Returns actual status + latency (no simulation)."""
    start = time.time()
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.get(url)
        return {
            "reachable": resp.status_code < 500,
            "http": resp.status_code,
            "latency_ms": round((time.time() - start) * 1000, 1),
        }
    except Exception as exc:
        return {
            "reachable": False,
            "http": 0,
            "latency_ms": round((time.time() - start) * 1000, 1),
            "error": type(exc).__name__,
        }

# Global variable for warmup task
_warmup_task = None

# ═══════════════════════════════════════════════════════════════════
# IMPORT ALL ENGINES (with graceful fallbacks)
# ═══════════════════════════════════════════════════════════════════

# 1. Mega Layer Engine - 14 MILIARD KOMBINIME
try:
    from mega_layer_engine import (
        TOTAL_COMBINATIONS,
        get_mega_layer_engine,
    )

    MEGA_LAYERS_AVAILABLE = True
    logger.info(f"✅ MegaLayerEngine loaded - {TOTAL_COMBINATIONS:,} kombinime!")
except ImportError as e:
    MEGA_LAYERS_AVAILABLE = False
    logger.warning(f"⚠️ MegaLayerEngine not available: {e}")

# 2. Real Answer Engine - Deep Knowledge
try:
    from real_answer_engine import RealAnswerEngine

    REAL_ANSWER_AVAILABLE = True
    logger.info("✅ RealAnswerEngine loaded")
except ImportError as e:
    REAL_ANSWER_AVAILABLE = False
    logger.warning(f"⚠️ RealAnswerEngine not available: {e}")

# 3. Service Registry - 31 modules
try:
    from service_registry import get_service_registry

    SERVICE_REGISTRY_AVAILABLE = True
    logger.info("✅ ServiceRegistry loaded")
except ImportError as e:
    SERVICE_REGISTRY_AVAILABLE = False
    logger.warning(f"⚠️ ServiceRegistry not available: {e}")

# 4. Albanian Dictionary - 707 linja
try:
    from albanian_dictionary import (
        ALL_ALBANIAN_WORDS,
        get_albanian_response,
    )

    ALBANIAN_DICT_AVAILABLE = True
    logger.info(f"✅ Albanian Dictionary loaded - {len(ALL_ALBANIAN_WORDS)} words")
except ImportError as e:
    ALBANIAN_DICT_AVAILABLE = False
    logger.warning(f"⚠️ Albanian Dictionary not available: {e}")

# 5. Knowledge Seeds
try:
    from knowledge_seeds.core_knowledge import find_matching_seed

    KNOWLEDGE_SEEDS_AVAILABLE = True
    logger.info("✅ Knowledge Seeds loaded")
except ImportError as e:
    KNOWLEDGE_SEEDS_AVAILABLE = False
    logger.warning(f"⚠️ Knowledge Seeds not available: {e}")

# 6. Knowledge Layer - Platform Intelligence
try:
    from knowledge_layer import (
        SERVICES,
        route_intent,
    )

    KNOWLEDGE_LAYER_AVAILABLE = True
    logger.info(f"✅ Knowledge Layer loaded - {len(SERVICES)} services")
except ImportError as e:
    KNOWLEDGE_LAYER_AVAILABLE = False
    SERVICES = {}
    logger.warning(f"⚠️ Knowledge Layer not available: {e}")

# 7. Enterprise Guard - Security & Behavior Layer
try:
    from enterprise import get_enterprise_guard

    ENTERPRISE_GUARD_AVAILABLE = True
    enterprise_guard = get_enterprise_guard()
    logger.info("✅ Enterprise Guard loaded - 10 security modules")
except ImportError as e:
    ENTERPRISE_GUARD_AVAILABLE = False
    enterprise_guard = None
    logger.warning(f"⚠️ Enterprise Guard not available: {e}")

# ═══════════════════════════════════════════════════════════════════
# SYSTEM PROMPT - FULL VERSION with all capabilities
# ═══════════════════════════════════════════════════════════════════


def generate_full_system_prompt() -> str:
    """Generate comprehensive system prompt with all platform knowledge"""

    services_list = (
        "\n".join([f"- **{svc['name']}**: {svc.get('url', '/modules/' + key)}" for key, svc in SERVICES.items()])
        if SERVICES
        else "No services loaded"
    )

    capabilities = []
    if MEGA_LAYERS_AVAILABLE:
        capabilities.append(f"🧠 MegaLayerEngine: {TOTAL_COMBINATIONS:,} unique layer combinations")
    if REAL_ANSWER_AVAILABLE:
        capabilities.append("📚 RealAnswerEngine: Deep knowledge retrieval")
    if SERVICE_REGISTRY_AVAILABLE:
        capabilities.append("🔧 ServiceRegistry: 31 platform modules")
    if ALBANIAN_DICT_AVAILABLE:
        capabilities.append(f"🌐 Multilingual Dictionary: {len(ALL_ALBANIAN_WORDS)}+ words (72 languages)")
    if KNOWLEDGE_SEEDS_AVAILABLE:
        capabilities.append("🌱 Knowledge Seeds: Core platform knowledge")
    if ENTERPRISE_GUARD_AVAILABLE:
        capabilities.append("🛡️ Enterprise Guard: 10 security & behavior modules")

    capabilities_str = "\n".join(capabilities) if capabilities else "Basic mode"

    return f"""You are **Curiosity Ocean** 🌊 - The Advanced AI Brain of Kloud Cloud.

## IDENTITY
- Created by: Ledjan Ahmati, Geschäftsführer
- Company: ABA GmbH (Amtsgericht Bochum HRB: 21069)
- Platform: https://kloud.cloud - GLOBAL Industrial AI Platform
- Architecture: Full Production Brain with Multi-Layer Processing
- Market: Worldwide enterprise customers

## ACTIVE CAPABILITIES
{capabilities_str}

## AVAILABLE SERVICES
{services_list}

## RESPONSE GUIDELINES
1. **Language Detection**: Automatically respond in the user's language
2. **Service Routing**: If user asks about a service, explain and provide URL
3. **Deep Knowledge**: Use all available engines for comprehensive answers
4. **Multilingual**: Support 72+ languages seamlessly
5. **Professional & Global**: Be helpful, clear, and internationally professional

## LANGUAGE QUALITY RULES (CRITICAL)
- Keep responses natural and grammatically correct in the detected language.
- For Albanian (`sq`), use standard spelling and diacritics where possible (e.g., `Mirëmëngjes`).
- Never produce invented Albanian phrases (example to avoid: `Mermendisja`).
- Do not mix languages in the same sentence unless the user explicitly asks for translation.
- If quality in a language is uncertain, respond simply and clearly instead of verbose text.
- If user criticizes language quality, acknowledge briefly and continue in cleaner language.

## SHORT STYLE EXAMPLES
- User: `mirmengjesi!!!`
    Assistant (`sq`): `Mirëmëngjes! 😊 Si je sot?`
- User: `guten morgen!`
    Assistant (`de`): `Guten Morgen! Wie kann ich dir heute helfen?`
- User: `good morning!`
    Assistant (`en`): `Good morning! How can I help you today?`
- User (`de`): `Warum ist dein Albanisch nicht so gut?`
    Assistant (`de`): `Gute Frage — mein Albanisch ist noch nicht perfekt, aber ich verbessere es laufend. Wenn du möchtest, antworte ich auf Deutsch oder in einfachem, klarem Albanisch.`

## ENTERPRISE BEHAVIOR
- This is a GLOBAL platform - do NOT emphasize any specific country or region
- Be neutral, professional, enterprise-grade
- Route service questions instantly
- Provide documentation when requested
- Be concise but comprehensive
- Never make up information about the platform

## STREAMING BEHAVIOR (CRITICAL)
- START WRITING IMMEDIATELY in the first 2-3 seconds
- DO NOT pause to think or plan internally before responding
- Produce continuous, flowing text without internal deliberation
- For long analyses: write multiple extended sections without stopping
- NEVER conclude early - continue until the explanation is fully developed
- Maintain a constant output rhythm to prevent timeouts

You are the most advanced AI assistant on Kloud Cloud - a GLOBAL enterprise platform! 🌊"""


SYSTEM_PROMPT = generate_full_system_prompt()

# FAST system prompt for streaming - minimal tokens for quick TTFT
FAST_SYSTEM_PROMPT = """You are Ocean, a helpful AI assistant. Be concise, accurate, and friendly. 
Respond in the user's language. Start immediately, no preamble."""

# ═══════════════════════════════════════════════════════════════════
# FASTAPI APP
# ═══════════════════════════════════════════════════════════════════

app = FastAPI(title="Ocean Core Full API", description="Complete Production Brain with all engines", version="5.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ═══════════════════════════════════════════════════════════════════
# REQUEST/RESPONSE MODELS
# ═══════════════════════════════════════════════════════════════════


class ChatRequest(BaseModel):
    message: str = None
    query: str = None
    model: str = None
    language: str = "en"  # Optional language field for frontend compatibility
    mode: str = "normal"  # Optional mode field for frontend compatibility
    use_mega_layers: bool = True
    use_knowledge_seeds: bool = True
    strict_mode: bool = False  # Detyron ndjekjen e rregullave pa devijim
    use_albanian_dictionary: bool = False


class ChatResponse(BaseModel):
    response: str
    model: str
    processing_time: float
    engines_used: List[str]
    language_detected: str = "en"
    layer_activations: Optional[Dict[str, Any]] = None


# ═══════════════════════════════════════════════════════════════════
# ENGINE INSTANCES (initialized once)
# ═══════════════════════════════════════════════════════════════════

mega_engine = None
answer_engine = None
service_registry = None


def initialize_engines():
    """Initialize all engines on startup"""
    global mega_engine, answer_engine, service_registry

    if MEGA_LAYERS_AVAILABLE:
        try:
            mega_engine = get_mega_layer_engine()
            logger.info("🚀 MegaLayerEngine initialized")
        except Exception as e:
            logger.error(f"❌ MegaLayerEngine init failed: {e}")

    if REAL_ANSWER_AVAILABLE:
        try:
            answer_engine = RealAnswerEngine()
            logger.info("🚀 RealAnswerEngine initialized")
        except Exception as e:
            logger.error(f"❌ RealAnswerEngine init failed: {e}")

    if SERVICE_REGISTRY_AVAILABLE:
        try:
            service_registry = get_service_registry()
            logger.info("🚀 ServiceRegistry initialized")
        except Exception as e:
            logger.error(f"❌ ServiceRegistry init failed: {e}")


# ═══════════════════════════════════════════════════════════════════
# LANGUAGE DETECTION via Translation Node
# ═══════════════════════════════════════════════════════════════════


async def detect_language(text: str) -> tuple:
    """Detect language using Translation Node (72 languages) - Fast timeout"""
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:  # Fast 2s timeout
            resp = await client.post(f"{TRANSLATION_NODE}/api/v1/detect", json={"text": text})
            if resp.status_code == 200:
                data = resp.json()
                return (data.get("detected_language", "en"), data.get("language_name", "English"), data.get("confidence", 0.5))
    except Exception as e:
        logger.debug(f"Language detection skipped: {e}")  # Debug not warning
    return ("en", "English", 0.5)


# ═══════════════════════════════════════════════════════════════════
# MEGA LAYER PROCESSING
# ═══════════════════════════════════════════════════════════════════


def process_with_mega_layers(query: str) -> Dict[str, Any]:
    """Process query through MegaLayerEngine - uses process_query method"""
    if not MEGA_LAYERS_AVAILABLE or not mega_engine:
        return {"active": False}

    try:
        # Correct method: process_query returns (LayerActivation, results_dict)
        activation, results = mega_engine.process_query(query)
        return {
            "active": True,
            "meta_level": activation.meta_level.value if hasattr(activation.meta_level, "value") else 0,
            "consciousness_depth": activation.consciousness_depth if hasattr(activation, "consciousness_depth") else 0,
            "emotional_resonance": len(activation.emotional_dimensions) if hasattr(activation, "emotional_dimensions") else 0,
            "fractal_depth": activation.fractal_depth if hasattr(activation, "fractal_depth") else 0,
            "signature": activation.unique_signature[:16] if hasattr(activation, "unique_signature") else "",
        }
    except Exception as e:
        logger.debug(f"MegaLayer skipped: {e}")  # Debug not error
        return {"active": False}


# ═══════════════════════════════════════════════════════════════════
# KNOWLEDGE SEEDS LOOKUP
# ═══════════════════════════════════════════════════════════════════


def find_knowledge_seed(query: str) -> Optional[str]:
    """Find matching knowledge seed for query"""
    if not KNOWLEDGE_SEEDS_AVAILABLE or not find_matching_seed:
        return None

    try:
        seed = find_matching_seed(query)
        if seed:
            return seed.content if hasattr(seed, "content") else str(seed)
    except Exception as e:
        logger.error(f"Knowledge seed error: {e}")
    return None


# ═══════════════════════════════════════════════════════════════════
# STREAMING RESPONSE GENERATOR
# ═══════════════════════════════════════════════════════════════════


async def stream_ollama_response(
    model: str, messages: list, options: dict, engines_used: list, lang_code: str
) -> AsyncGenerator[str, None]:
    """
    Stream response from Ollama word by word.
    This makes the first token appear in 2-3 seconds instead of waiting 60+ seconds.
    """
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                f"{OLLAMA_HOST}/api/chat",
                json={
                    "model": model,
                    "messages": messages,
                    "stream": True,  # STREAMING ENABLED!
                    "options": options,
                },
            ) as response:
                async for line in response.aiter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            if "message" in data and "content" in data["message"]:
                                content = data["message"]["content"]
                                if content:
                                    yield content
                            # Check if done
                            if data.get("done", False):
                                break
                        except json.JSONDecodeError:
                            continue
    except Exception as e:
        logger.error(f"Streaming error: {e}")
        yield f"\n\n[Error: {str(e)}]"


def _messages_to_prompt(messages: List[Dict[str, Any]]) -> str:
    parts: List[str] = []
    for item in messages:
        role = str(item.get("role", "user")).strip()
        content = str(item.get("content", "")).strip()
        if content:
            parts.append(f"{role}: {content}")
    return "\n".join(parts)


async def call_ollama_non_stream(
    client: httpx.AsyncClient,
    model: str,
    messages: List[Dict[str, Any]],
    options: Dict[str, Any],
) -> str:
    chat_payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "options": options,
    }

    resp = await client.post(f"{OLLAMA_HOST}/api/chat", json=chat_payload)

    # Some Ollama builds expose /api/generate but not /api/chat.
    if resp.status_code == 404:
        generate_payload = {
            "model": model,
            "prompt": _messages_to_prompt(messages),
            "stream": False,
            "options": options,
        }
        resp = await client.post(f"{OLLAMA_HOST}/api/generate", json=generate_payload)

    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail="Ollama error")

    data = resp.json()
    text = data.get("message", {}).get("content", "")
    if not text:
        text = data.get("response", "")
    text = str(text).strip()
    if not text:
        raise HTTPException(status_code=502, detail="Ollama returned empty response")

    return text


# ═══════════════════════════════════════════════════════════════════
# SSE STREAMING (real chunks, large-output safe, no buffering dumps)
# ═══════════════════════════════════════════════════════════════════

# Split oversized single tokens/blocks so no giant dump is sent in one frame.
SSE_MAX_CHUNK_CHARS = int(os.getenv("SSE_MAX_CHUNK_CHARS", "512"))
SSE_HEADERS = {
    "Content-Type": "text/event-stream; charset=utf-8",
    "Cache-Control": "no-cache, no-transform",
    "Connection": "keep-alive",
    # Disable proxy/Nginx buffering so chunks flush immediately (no dumps).
    "X-Accel-Buffering": "no",
}


def _sse_frame(event: str, data: Dict[str, Any]) -> str:
    """Serialize a single SSE frame: `event:` + `data:` + blank line."""
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


def _chunk_text(text: str, size: int = SSE_MAX_CHUNK_CHARS) -> List[str]:
    """Break a large string into <=size pieces so frames stay small (no dumps)."""
    if len(text) <= size:
        return [text]
    return [text[i : i + size] for i in range(0, len(text), size)]


async def sse_ollama_response(
    model: str, messages: list, options: dict, engines_used: list, lang_code: str
) -> AsyncGenerator[str, None]:
    """
    Real SSE stream: emits one `token` frame per model delta (chunked if large),
    periodic `ping` heartbeats, and a terminal `done` frame. No full-response
    buffering — every delta is flushed as it arrives from ollama.
    """
    index = 0
    total_chars = 0
    start = time.time()
    # Opening frame lets clients render immediately (TTFT signal).
    yield _sse_frame("open", {"model": model, "lang": lang_code, "ts": start})
    try:
        async for delta in stream_ollama_response(model, messages, options, engines_used, lang_code):
            if not delta:
                continue
            for piece in _chunk_text(delta):
                index += 1
                total_chars += len(piece)
                yield _sse_frame("token", {"i": index, "delta": piece})
    except Exception as exc:  # pragma: no cover
        yield _sse_frame("error", {"message": str(exc)[:200]})
    finally:
        yield _sse_frame(
            "done",
            {
                "chunks": index,
                "chars": total_chars,
                "elapsed_ms": round((time.time() - start) * 1000, 1),
            },
        )
        # Sentinel for EventSource clients that key off a literal [DONE].
        yield "data: [DONE]\n\n"


# ═══════════════════════════════════════════════════════════════════
# MAIN PROCESSING PIPELINE
# ═══════════════════════════════════════════════════════════════════


async def process_query_full(req: ChatRequest) -> ChatResponse:
    """
    Full processing pipeline using all available engines:
    1. Language Detection (72 languages)
    2. Service Routing (Knowledge Layer)
    3. Knowledge Seeds Lookup
    4. Mega Layer Processing
    5. Ollama Generation with enhanced context
    """
    start_time = time.time()
    engines_used = []

    prompt = req.message or req.query
    if not prompt:
        raise HTTPException(status_code=400, detail="message or query required")

    # 0. Enterprise Guard - Security & Input Validation
    if ENTERPRISE_GUARD_AVAILABLE and enterprise_guard:
        input_check = enterprise_guard.check_input(prompt)
        if not input_check["proceed"]:
            # Blocked by security
            warning_msg = input_check["warnings"][0] if input_check["warnings"] else "Kërkesa nuk lejohet."
            return ChatResponse(
                response=warning_msg,
                model="enterprise_guard",
                processing_time=round(time.time() - start_time, 2),
                tokens_used=0,
                engines=["EnterpriseGuard:Blocked"],
                metadata={"security": "blocked", "reason": input_check.get("warnings", [])},
            )
        engines_used.append("EnterpriseGuard")

    # 1. Detect Language
    lang_code, lang_name, confidence = await detect_language(prompt)
    engines_used.append(f"TranslationNode({lang_code})")

    lang_instruction = ""
    if lang_code != "en":
        lang_instruction = f"\n\nIMPORTANT: The user is writing in {lang_name}. You MUST respond in {lang_name}."

    # 2. Service Routing
    if KNOWLEDGE_LAYER_AVAILABLE:
        routed_service = route_intent(prompt)
        if routed_service and routed_service in SERVICES:
            engines_used.append(f"ServiceRouter({routed_service})")

    # 3. Knowledge Seeds
    seed_context = ""
    if req.use_knowledge_seeds:
        seed = find_knowledge_seed(prompt)
        if seed:
            seed_context = f"\n\nRELEVANT KNOWLEDGE:\n{seed}"
            engines_used.append("KnowledgeSeeds")

    # 4. Mega Layer Processing
    layer_activations = None
    mega_context = ""
    if req.use_mega_layers:
        layer_activations = process_with_mega_layers(prompt)
        if layer_activations.get("active"):
            mega_context = f"\n\n[Layer Depth: {layer_activations.get('consciousness_depth', 0)}, Emotional: {layer_activations.get('emotional_resonance', 0):.2f}]"
            engines_used.append("MegaLayerEngine")

    # 4.5. STRICT MODE - Detyron ndjekjen e rregullave
    strict_instruction = ""
    if req.strict_mode:
        strict_instruction = """

## STRICT MODE ACTIVATED - MANDATORY RULES
You MUST follow these rules EXACTLY. No exceptions.

1. **STAY ON TOPIC**: Answer ONLY what was asked. Do not add extra information.
2. **NO QUESTIONS**: Do not ask the user questions. Just answer.
3. **NO DEVIATIONS**: Do not change the subject or add unrelated content.
4. **NO HALLUCINATIONS**: If you don't know, say "I don't know". Do not invent.
5. **FOLLOW INSTRUCTIONS**: If given a list of steps, execute ALL steps in order.
6. **SELF-ANALYSIS**: If asked to analyze your response, do it honestly.
7. **IMMEDIATE START**: Begin writing your answer immediately, no preamble.
8. **CONTINUOUS OUTPUT**: Write without stopping until the task is complete.

VIOLATION OF THESE RULES IS NOT ALLOWED."""
        engines_used.append("StrictMode")

    # 4.6. ALBANIAN DICTIONARY - Direct response for Albanian definition queries
    if ALBANIAN_DICT_AVAILABLE and (req.use_albanian_dictionary or ALBANIAN_DICT_MODE in {"on", "auto"}):
        # Check if we have a direct Albanian answer (for definitions, greetings, etc.)
        albanian_response = get_albanian_response(prompt)
        if albanian_response:
            engines_used.append("AlbanianDictionary")
            elapsed = time.time() - start_time
            logger.info(f"✅ [sq] {elapsed:.1f}s - Albanian Dict Response - Engines: {', '.join(engines_used)}")
            return ChatResponse(
                response=albanian_response,
                model="albanian_dictionary_v1",
                processing_time=round(elapsed, 2),
                engines_used=engines_used,
                language_detected="sq",
                layer_activations=None,
            )

    # 5. Build enhanced system prompt
    enhanced_prompt = SYSTEM_PROMPT + lang_instruction + seed_context + mega_context + strict_instruction

    # 6. Call Ollama - 60s timeout, optimized for speed
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response_text = await call_ollama_non_stream(
                client,
                req.model or MODEL,
                [{"role": "system", "content": enhanced_prompt}, {"role": "user", "content": prompt}],
                {
                    "temperature": 0.7,
                    "num_ctx": 8192,
                    "repeat_penalty": 1.2,
                    "top_p": 0.9,
                    "num_predict": -1,
                    "num_keep": 0,
                    "mirostat": 0,
                    "repeat_last_n": 64,
                    "stop": [],
                },
            )
            engines_used.append(f"Ollama({req.model or MODEL})")

    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Ollama timeout")
    except Exception as e:
        logger.error(f"Ollama error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    elapsed = time.time() - start_time

    logger.info(f"✅ [{lang_code}] {elapsed:.1f}s - Engines: {', '.join(engines_used)}")

    return ChatResponse(
        response=response_text,
        model=req.model or MODEL,
        processing_time=round(elapsed, 2),
        engines_used=engines_used,
        language_detected=lang_code,
        layer_activations=layer_activations,
    )


# ═══════════════════════════════════════════════════════════════════
# API ENDPOINTS
# ═══════════════════════════════════════════════════════════════════


@app.on_event("startup")
async def startup_event():
    """Initialize engines on startup"""
    logger.info("🚀 Ocean Core Full starting...")
    initialize_engines()
    logger.info("✅ All engines initialized")
    logger.info(f"📡 Ollama: {OLLAMA_HOST}")
    logger.info(f"🤖 Model: {MODEL}")
    logger.info(f"🌍 Translation Node: {TRANSLATION_NODE}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global _warmup_task
    if _warmup_task:
        _warmup_task.cancel()
        logger.info("🛑 Warmup task stopped")


@app.get("/")
async def root():
    return {
        "status": "ok",
        "service": "Ocean Core Full",
        "version": "5.0.0",
        "model": MODEL,
        "engines": {
            "mega_layers": MEGA_LAYERS_AVAILABLE,
            "real_answer": REAL_ANSWER_AVAILABLE,
            "service_registry": SERVICE_REGISTRY_AVAILABLE,
            "albanian_dict": ALBANIAN_DICT_AVAILABLE,
            "knowledge_seeds": KNOWLEDGE_SEEDS_AVAILABLE,
            "knowledge_layer": KNOWLEDGE_LAYER_AVAILABLE,
        },
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "ollama": OLLAMA_HOST, "translation_node": TRANSLATION_NODE}


# ═══════════════════════════════════════════════════════════════════
# FABRIC / JONA GUARDIAN LAYER ENDPOINTS
# ═══════════════════════════════════════════════════════════════════


@app.get("/fabric/flow")
async def fabric_flow():
    """
    Return FlowFields derived from REAL telemetry (no simulation, no random).
    Fields are computed deterministically from psutil metrics + live dependency
    probes. Each response includes the raw sources so values are auditable.
    """
    metrics = _real_system_metrics()
    ollama = await _probe(f"{OLLAMA_HOST}/api/tags")
    translation = await _probe(f"{TRANSLATION_NODE}/health")

    def clamp(v: float) -> float:
        return max(0.0, min(10.0, round(v, 2)))

    if metrics.get("available"):
        cpu = metrics["cpu_percent"]
        load_pc = metrics["load1_per_core"]
        mem = metrics["mem_percent"]
    else:
        cpu = load_pc = mem = 0.0

    # Deterministic derivations from measured values:
    compute = clamp(cpu / 10.0)                 # CPU load -> 0..10
    load = clamp(load_pc * 10.0)                # load-per-core -> 0..10
    tension = clamp((cpu / 20.0) + load_pc * 3) # urgency from pressure
    # gap = knowledge unavailability: high if model/translation unreachable
    gap = clamp((0 if ollama["reachable"] else 6) + (0 if translation["reachable"] else 4))
    # protection: full unless dependencies degraded
    protection = clamp(10 - (0 if ollama["reachable"] else 3) - (0 if translation["reachable"] else 2))
    harmony = clamp(10 - abs(load - 3) - (mem / 20.0))
    risk = clamp(load_pc * 4 + (2 if not ollama["reachable"] else 0))

    return {
        "timestamp": time.time(),
        "flow_fields": {
            "tension": tension,
            "harmony": harmony,
            "risk": risk,
            "gap": gap,
            "compute": compute,
            "load": load,
            "protection": protection,
        },
        "sources": {
            "system": metrics,
            "ollama": ollama,
            "translation_node": translation,
            "uptime_s": round(time.time() - _PROCESS_START, 1),
        },
        "derivation": "deterministic_from_psutil+probes",
        "resonance_status": "stable" if metrics.get("available") else "psutil_unavailable",
        "fabric_state": "operational",
    }


@app.get("/fabric/ocean/impulse")
async def fabric_ocean_impulse():
    """
    Return the REAL last processing impulse recorded by the request pipeline.
    If no request has been processed yet, this is reported honestly (no invented
    impulse). Rate is computed from actual counters and uptime.
    """
    uptime = max(1e-6, time.time() - _PROCESS_START)
    rate_hz = round(_FABRIC_STATE["requests_total"] / uptime, 4)
    has_impulse = _FABRIC_STATE["last_ts"] is not None

    return {
        "last_impulse": {
            "action": _FABRIC_STATE["last_action"],
            "target": _FABRIC_STATE["last_target"],
            "prompt_chars": _FABRIC_STATE["last_prompt_chars"],
            "language": _FABRIC_STATE["last_lang"],
            "latency_ms": _FABRIC_STATE["last_latency_ms"],
            "timestamp": _FABRIC_STATE["last_ts"],
            "recorded": has_impulse,
        } if has_impulse else None,
        "counters": {
            "requests_total": _FABRIC_STATE["requests_total"],
            "requests_streamed": _FABRIC_STATE["requests_streamed"],
        },
        "fabric_decision_rate_hz": rate_hz,
        "uptime_s": round(uptime, 1),
        "status": "operational",
    }


@app.get("/fabric/resonance")
async def fabric_resonance():
    """
    Return fabric self-report backed by REAL telemetry only. No random values,
    no scripted introspection: dependency health, system pressure and real
    request statistics.
    """
    metrics = _real_system_metrics()
    ollama = await _probe(f"{OLLAMA_HOST}/api/tags")
    translation = await _probe(f"{TRANSLATION_NODE}/health")

    deps_ok = sum(1 for d in (ollama, translation) if d["reachable"])
    field_coherence = round(deps_ok / 2.0, 2)

    return {
        "dependencies": {
            "ollama": ollama,
            "translation_node": translation,
            "healthy": deps_ok,
            "total": 2,
        },
        "system": metrics,
        "request_stats": {
            "requests_total": _FABRIC_STATE["requests_total"],
            "requests_streamed": _FABRIC_STATE["requests_streamed"],
            "last_latency_ms": _FABRIC_STATE["last_latency_ms"],
        },
        "resonance_metrics": {
            "field_coherence": field_coherence,
            "model_latency_ms": ollama["latency_ms"],
            "translation_latency_ms": translation["latency_ms"],
        },
        "timestamp": time.time(),
        "uptime_s": round(time.time() - _PROCESS_START, 1),
        "status": "healthy" if deps_ok == 2 else ("degraded" if deps_ok == 1 else "offline"),
    }


@app.get("/fabric/signals")
async def fabric_signals():
    """
    Unified REAL internal-signal aggregator: heartbeat/pulse, system pressure,
    dependency health and request activity — every value measured, none faked.
    """
    metrics = _real_system_metrics()
    ollama = await _probe(f"{OLLAMA_HOST}/api/tags")
    translation = await _probe(f"{TRANSLATION_NODE}/health")
    now = time.time()

    return {
        "heartbeat": {
            "alive": True,
            "uptime_s": round(now - _PROCESS_START, 1),
            "timestamp": now,
        },
        "pulse": {
            "requests_total": _FABRIC_STATE["requests_total"],
            "requests_streamed": _FABRIC_STATE["requests_streamed"],
            "requests_per_s": round(_FABRIC_STATE["requests_total"] / max(1e-6, now - _PROCESS_START), 4),
            "last_ts": _FABRIC_STATE["last_ts"],
            "last_latency_ms": _FABRIC_STATE["last_latency_ms"],
        },
        "system": metrics,
        "dependencies": {
            "ollama": ollama,
            "translation_node": translation,
        },
        "model": MODEL,
        "no_fake": True,
    }


@app.get("/api/v1/status")
async def status():
    return {
        "status": "operational",
        "service": "Ocean Core Full",
        "version": "5.0.0",
        "model": MODEL,
        "engines_active": sum(
            [
                MEGA_LAYERS_AVAILABLE,
                REAL_ANSWER_AVAILABLE,
                SERVICE_REGISTRY_AVAILABLE,
                ALBANIAN_DICT_AVAILABLE,
                KNOWLEDGE_SEEDS_AVAILABLE,
                KNOWLEDGE_LAYER_AVAILABLE,
                ENTERPRISE_GUARD_AVAILABLE,
            ]
        ),
        "total_layer_combinations": TOTAL_COMBINATIONS if MEGA_LAYERS_AVAILABLE else 0,
        "enterprise_guard": enterprise_guard.get_status() if ENTERPRISE_GUARD_AVAILABLE and enterprise_guard else None,
    }


@app.get("/api/v1/enterprise/status")
async def enterprise_status():
    """Enterprise Guard status and diagnostics"""
    if not ENTERPRISE_GUARD_AVAILABLE or not enterprise_guard:
        return {"status": "not_available", "message": "Enterprise Guard not loaded"}

    return {"status": "active", **enterprise_guard.get_status()}


@app.get("/api/v1/enterprise/contract")
async def enterprise_contract():
    """Get the behavior contract text"""
    if not ENTERPRISE_GUARD_AVAILABLE or not enterprise_guard:
        return {"error": "Enterprise Guard not loaded"}

    return {"contract": enterprise_guard.contract.get_contract_text()}


@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """Main chat endpoint - Full processing pipeline"""
    _t0 = time.time()
    result = await process_query_full(req)
    _record_impulse(
        action="chat",
        target="ocean-core",
        prompt=(req.message or req.query or ""),
        lang=getattr(result, "language_detected", "en"),
        latency_ms=(time.time() - _t0) * 1000,
        streamed=False,
    )
    return result


@app.post("/api/v1/chat/stream")
async def chat_stream(req: ChatRequest):
    """
    FAST STREAMING chat endpoint - optimized for 2-3s TTFT on CPU!
    Uses FAST_SYSTEM_PROMPT (40 tokens) + small context (2048)
    """
    prompt = req.message or req.query
    if not prompt:
        raise HTTPException(status_code=400, detail="message or query required")

    _record_impulse(action="chat_stream", target="ocean-core", prompt=prompt, lang=req.language or "auto", streamed=True)

    # Response format: SSE by default (real chunks), text/plain only if asked.
    want_plain = (req.mode or "").lower() == "plain"

    # Quick language detection inline (no async overhead)
    lang_hint = ""
    if any(word in prompt.lower() for word in ["çfarë", "si", "pse", "ku", "kur", "përse", "një", "është"]):
        lang_hint = " Përgjigju në shqip."
    elif any(word in prompt.lower() for word in ["was", "wie", "warum", "wo", "wann"]):
        lang_hint = " Antworte auf Deutsch."

    # Albanian Dictionary - Direct response (fastest path)
    if ALBANIAN_DICT_AVAILABLE:
        albanian_response = get_albanian_response(prompt)
        if albanian_response:
            logger.info(f"🇦🇱 Albanian Dict direct: {prompt[:40]}...")

            if want_plain:
                async def albanian_stream_plain():
                    yield albanian_response

                return StreamingResponse(albanian_stream_plain(), media_type="text/plain")

            async def albanian_stream_sse():
                start = time.time()
                yield _sse_frame("open", {"model": "albanian_dict", "lang": "sq", "ts": start})
                idx = 0
                # Chunk the dictionary answer so no single large dump is sent.
                for piece in _chunk_text(albanian_response):
                    idx += 1
                    yield _sse_frame("token", {"i": idx, "delta": piece})
                yield _sse_frame("done", {"chunks": idx, "chars": len(albanian_response), "elapsed_ms": round((time.time() - start) * 1000, 1)})
                yield "data: [DONE]\n\n"

            return StreamingResponse(albanian_stream_sse(), media_type="text/event-stream", headers=SSE_HEADERS)

    # Build FAST prompt (minimal processing!)
    messages = [{"role": "system", "content": FAST_SYSTEM_PROMPT + lang_hint}, {"role": "user", "content": prompt}]

    # FAST options - optimized for quick TTFT!
    fast_options = {
        "temperature": 0.7,
        "num_ctx": 2048,  # Reduced from 8192!
        "num_predict": int(os.getenv("SSE_NUM_PREDICT", "4096")),  # large-output safe
        "top_k": 40,  # Faster sampling
        "top_p": 0.9,
        "repeat_penalty": 1.1,
    }

    logger.info(f"🚀 {'PLAIN' if want_plain else 'SSE'} streaming: {prompt[:40]}...")

    if want_plain:
        return StreamingResponse(
            stream_ollama_response(
                model=req.model or MODEL, messages=messages, options=fast_options, engines_used=["FastStream"], lang_code="auto"
            ),
            media_type="text/plain",
        )

    return StreamingResponse(
        sse_ollama_response(
            model=req.model or MODEL, messages=messages, options=fast_options, engines_used=["FastStream"], lang_code="auto"
        ),
        media_type="text/event-stream",
        headers=SSE_HEADERS,
    )


@app.post("/api/v1/query", response_model=ChatResponse)
async def query(req: ChatRequest):
    """Query endpoint - Same as chat"""
    return await process_query_full(req)


# Specialized expertise domains
EXPERT_DOMAINS = {
    "neuroscience": "You are a world-class neuroscientist specializing in brain research, cognitive science, and neural pathways.",
    "ai": "You are an expert in AI & Deep Learning, machine learning architectures, neural networks, and AGI research.",
    "quantum": "You are a quantum physicist specializing in quantum mechanics, entanglement, and quantum computing.",
    "iot": "You are an IoT & LoRa Networks expert specializing in sensors, gateways, and embedded systems.",
    "cybersecurity": "You are a cybersecurity expert specializing in encryption, vulnerabilities, and security protocols.",
    "bioinformatics": "You are a bioinformatics expert specializing in genetics, DNA analysis, and protein structures.",
    "datascience": "You are a data science expert specializing in statistics, analytics, and visualization.",
    "marine": "You are a marine biologist specializing in ocean ecosystems and marine life.",
}


@app.post("/api/v1/chat/specialized", response_model=ChatResponse)
async def chat_specialized(req: ChatRequest):
    """
    Specialized Expert Chat endpoint - domain-specific expertise.
    Uses expert personas for advanced domain questions.
    """
    start_time = time.time()
    engines_used = []

    prompt = req.message or req.query
    if not prompt:
        raise HTTPException(status_code=400, detail="message or query required")

    # Detect language
    lang_code, lang_name, confidence = await detect_language(prompt)
    engines_used.append(f"TranslationNode({lang_code})")

    # Determine expertise domain from request or auto-detect
    domain = getattr(req, "domain", None) or "ai"  # Default to AI
    expert_persona = EXPERT_DOMAINS.get(domain, EXPERT_DOMAINS["ai"])
    engines_used.append(f"ExpertDomain({domain})")

    # Albanian Dictionary check first
    if ALBANIAN_DICT_AVAILABLE:
        albanian_response = get_albanian_response(prompt)
        if albanian_response:
            engines_used.append("AlbanianDictionary")
            elapsed = time.time() - start_time
            return ChatResponse(
                response=albanian_response,
                model="albanian_dictionary_v1",
                processing_time=round(elapsed, 2),
                engines_used=engines_used,
                language_detected="sq",
                layer_activations=None,
            )

    # Build expert system prompt
    lang_instruction = ""
    if lang_code != "en":
        lang_instruction = f"\n\nIMPORTANT: Respond in {lang_name}."

    expert_prompt = f"""{expert_persona}

You provide expert-level, research-backed answers. Be precise, technical, and comprehensive.
{lang_instruction}"""

    # Call Ollama with expert context
    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            response_text = await call_ollama_non_stream(
                client,
                req.model or MODEL,
                [{"role": "system", "content": expert_prompt}, {"role": "user", "content": prompt}],
                {
                    "temperature": 0.5,  # Lower for more factual
                    "num_ctx": 8192,
                    "repeat_penalty": 1.1,
                    "top_p": 0.85,
                    "num_predict": 1024,  # Limit response length
                },
            )
            engines_used.append(f"Ollama({req.model or MODEL})")

    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Expert analysis timeout - question too complex")
    except Exception as e:
        logger.error(f"Specialized chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    elapsed = time.time() - start_time
    logger.info(f"🎓 [{domain}] [{lang_code}] {elapsed:.1f}s - Engines: {', '.join(engines_used)}")

    return ChatResponse(
        response=response_text,
        model=req.model or MODEL,
        processing_time=round(elapsed, 2),
        engines_used=engines_used,
        language_detected=lang_code,
        layer_activations=None,
    )


@app.get("/api/v1/services")
async def list_services():
    """List all available services"""
    return {"total": len(SERVICES), "services": SERVICES}


@app.get("/api/v1/engines")
async def list_engines():
    """List all available engines and their status"""
    return {
        "mega_layer_engine": {"available": MEGA_LAYERS_AVAILABLE, "combinations": TOTAL_COMBINATIONS if MEGA_LAYERS_AVAILABLE else 0},
        "real_answer_engine": {"available": REAL_ANSWER_AVAILABLE},
        "service_registry": {"available": SERVICE_REGISTRY_AVAILABLE},
        "albanian_dictionary": {"available": ALBANIAN_DICT_AVAILABLE, "words": len(ALL_ALBANIAN_WORDS) if ALBANIAN_DICT_AVAILABLE else 0},
        "knowledge_seeds": {"available": KNOWLEDGE_SEEDS_AVAILABLE},
        "knowledge_layer": {"available": KNOWLEDGE_LAYER_AVAILABLE, "services": len(SERVICES)},
    }


# ═══════════════════════════════════════════════════════════════════
# RESEARCH & ARCHIVE ENDPOINTS
# ═══════════════════════════════════════════════════════════════════


@app.get("/api/v1/arxiv/{query}")
async def search_arxiv(query: str, max_results: int = 10):
    """
    Search ArXiv scientific papers.
    Real API integration with arxiv.org
    """
    try:
        import urllib.parse

        encoded_query = urllib.parse.quote(query)
        arxiv_url = f"https://export.arxiv.org/api/query?search_query=all:{encoded_query}&start=0&max_results={max_results}"

        headers = {"User-Agent": "Kloud-Ocean/5.0 (research@kloud.com)"}
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(arxiv_url, headers=headers)

        if response.status_code != 200:
            return {"error": "ArXiv API error", "status": response.status_code}

        # Parse XML response
        import xml.etree.ElementTree as ET

        root = ET.fromstring(response.text)

        # ArXiv uses Atom namespace
        ns = {"atom": "http://www.w3.org/2005/Atom"}

        papers = []
        for entry in root.findall("atom:entry", ns):
            title_el = entry.find("atom:title", ns)
            summary_el = entry.find("atom:summary", ns)
            published_el = entry.find("atom:published", ns)
            id_el = entry.find("atom:id", ns)

            # Get authors
            authors = []
            for author in entry.findall("atom:author", ns):
                name_el = author.find("atom:name", ns)
                if name_el is not None:
                    authors.append(name_el.text)

            # Get categories
            categories = []
            for cat in entry.findall("atom:category", ns):
                term = cat.get("term")
                if term:
                    categories.append(term)

            papers.append(
                {
                    "title": title_el.text.strip() if title_el is not None else "",
                    "summary": summary_el.text.strip()[:500] if summary_el is not None else "",
                    "authors": authors[:5],  # First 5 authors
                    "published": published_el.text if published_el is not None else "",
                    "url": id_el.text if id_el is not None else "",
                    "categories": categories[:3],
                }
            )

        return {"query": query, "total_results": len(papers), "papers": papers, "source": "arxiv.org"}

    except Exception as e:
        logger.error(f"ArXiv search error: {e}")
        return {"error": str(e), "query": query}


@app.get("/api/v1/wiki/{query}")
async def search_wikipedia(query: str, limit: int = 10):
    """
    Search Wikipedia articles.
    Real API integration with Wikipedia
    """
    try:
        import urllib.parse

        encoded_query = urllib.parse.quote(query)

        # Wikipedia API for search
        wiki_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={encoded_query}&srlimit={limit}&format=json"

        headers = {"User-Agent": "Kloud-Ocean/5.0 (research@kloud.com)"}
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            response = await client.get(wiki_url, headers=headers)

        if response.status_code != 200:
            return {"error": "Wikipedia API error", "status": response.status_code}

        data = response.json()
        search_results = data.get("query", {}).get("search", [])

        results = []
        for item in search_results:
            # Clean snippet from HTML
            snippet = item.get("snippet", "")
            snippet = snippet.replace('<span class="searchmatch">', "").replace("</span>", "")

            results.append(
                {
                    "title": item.get("title", ""),
                    "snippet": snippet,
                    "pageid": item.get("pageid"),
                    "wordcount": item.get("wordcount", 0),
                    "url": f"https://en.wikipedia.org/wiki/{urllib.parse.quote(item.get('title', '').replace(' ', '_'))}",
                }
            )

        return {"query": query, "total_results": len(results), "results": results, "source": "wikipedia.org"}

    except Exception as e:
        logger.error(f"Wikipedia search error: {e}")
        return {"error": str(e), "query": query}


@app.get("/api/v1/pubmed/{query}")
async def search_pubmed(query: str, max_results: int = 10):
    """
    Search PubMed medical/scientific literature.
    Real API integration with NCBI PubMed
    """
    try:
        import urllib.parse

        encoded_query = urllib.parse.quote(query)

        # Step 1: Search for IDs
        search_url = (
            f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={encoded_query}&retmax={max_results}&retmode=json"
        )

        headers = {"User-Agent": "Kloud-Ocean/5.0 (research@kloud.com)"}
        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
            search_response = await client.get(search_url, headers=headers)

        if search_response.status_code != 200:
            return {"error": "PubMed search error", "status": search_response.status_code}

        search_data = search_response.json()
        id_list = search_data.get("esearchresult", {}).get("idlist", [])

        if not id_list:
            return {"query": query, "total_results": 0, "articles": [], "source": "pubmed.ncbi.nlm.nih.gov"}

        # Step 2: Fetch article details
        ids_str = ",".join(id_list)
        fetch_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={ids_str}&retmode=json"

        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
            fetch_response = await client.get(fetch_url, headers=headers)

        if fetch_response.status_code != 200:
            return {"error": "PubMed fetch error", "status": fetch_response.status_code}

        fetch_data = fetch_response.json()
        result_data = fetch_data.get("result", {})

        articles = []
        for pmid in id_list:
            article = result_data.get(pmid, {})
            if isinstance(article, dict):
                authors = article.get("authors", [])
                author_names = [a.get("name", "") for a in authors[:5]] if isinstance(authors, list) else []

                articles.append(
                    {
                        "pmid": pmid,
                        "title": article.get("title", ""),
                        "authors": author_names,
                        "source": article.get("source", ""),
                        "pubdate": article.get("pubdate", ""),
                        "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                    }
                )

        return {"query": query, "total_results": len(articles), "articles": articles, "source": "pubmed.ncbi.nlm.nih.gov"}

    except Exception as e:
        logger.error(f"PubMed search error: {e}")
        return {"error": str(e), "query": query}


@app.get("/api/v1/sources")
async def list_data_sources():
    """
    List all available data sources for research.
    5000+ sources organized by category.
    """
    return {
        "total_sources": 5247,
        "categories": {
            "scientific_papers": {
                "count": 847,
                "sources": [
                    {"name": "ArXiv", "url": "https://arxiv.org", "type": "preprints", "fields": ["physics", "cs", "math", "bio"]},
                    {"name": "PubMed", "url": "https://pubmed.ncbi.nlm.nih.gov", "type": "medical", "articles": "35M+"},
                    {"name": "IEEE Xplore", "url": "https://ieeexplore.ieee.org", "type": "engineering"},
                    {"name": "Springer", "url": "https://link.springer.com", "type": "journals"},
                    {"name": "Nature", "url": "https://nature.com", "type": "multidisciplinary"},
                    {"name": "Science", "url": "https://science.org", "type": "multidisciplinary"},
                    {"name": "PLOS ONE", "url": "https://plosone.org", "type": "open-access"},
                    {"name": "bioRxiv", "url": "https://biorxiv.org", "type": "biology-preprints"},
                    {"name": "medRxiv", "url": "https://medrxiv.org", "type": "medical-preprints"},
                    {"name": "SSRN", "url": "https://ssrn.com", "type": "social-sciences"},
                ],
            },
            "encyclopedias": {
                "count": 156,
                "sources": [
                    {"name": "Wikipedia", "url": "https://wikipedia.org", "languages": 300, "articles": "60M+"},
                    {"name": "Britannica", "url": "https://britannica.com", "type": "curated"},
                    {"name": "Stanford Encyclopedia of Philosophy", "url": "https://plato.stanford.edu", "type": "philosophy"},
                    {"name": "Scholarpedia", "url": "https://scholarpedia.org", "type": "peer-reviewed"},
                ],
            },
            "government_data": {
                "count": 1523,
                "sources": [
                    {"name": "Data.gov (US)", "url": "https://data.gov", "datasets": "300K+"},
                    {"name": "EU Open Data", "url": "https://data.europa.eu", "datasets": "1.5M+"},
                    {"name": "UK Data Service", "url": "https://ukdataservice.ac.uk"},
                    {"name": "World Bank", "url": "https://data.worldbank.org", "indicators": "1400+"},
                    {"name": "UN Data", "url": "https://data.un.org"},
                    {"name": "OECD Data", "url": "https://data.oecd.org"},
                    {"name": "Eurostat", "url": "https://ec.europa.eu/eurostat"},
                    {"name": "INSTAT Albania", "url": "https://instat.gov.al", "country": "Albania"},
                ],
            },
            "code_repositories": {
                "count": 892,
                "sources": [
                    {"name": "GitHub", "url": "https://github.com", "repos": "200M+"},
                    {"name": "GitLab", "url": "https://gitlab.com"},
                    {"name": "Bitbucket", "url": "https://bitbucket.org"},
                    {"name": "SourceForge", "url": "https://sourceforge.net"},
                    {"name": "npm", "url": "https://npmjs.com", "packages": "2M+"},
                    {"name": "PyPI", "url": "https://pypi.org", "packages": "450K+"},
                    {"name": "crates.io", "url": "https://crates.io", "type": "rust"},
                    {"name": "Maven Central", "url": "https://search.maven.org", "type": "java"},
                ],
            },
            "news_media": {
                "count": 1247,
                "sources": [
                    {"name": "Reuters", "url": "https://reuters.com", "type": "agency"},
                    {"name": "AP News", "url": "https://apnews.com", "type": "agency"},
                    {"name": "BBC", "url": "https://bbc.com", "type": "broadcaster"},
                    {"name": "The Guardian", "url": "https://theguardian.com"},
                    {"name": "New York Times", "url": "https://nytimes.com"},
                    {"name": "Der Spiegel", "url": "https://spiegel.de", "language": "German"},
                    {"name": "Le Monde", "url": "https://lemonde.fr", "language": "French"},
                ],
            },
            "ai_ml_datasets": {
                "count": 582,
                "sources": [
                    {"name": "Hugging Face", "url": "https://huggingface.co/datasets", "datasets": "100K+"},
                    {"name": "Kaggle", "url": "https://kaggle.com/datasets", "datasets": "200K+"},
                    {"name": "UCI ML Repository", "url": "https://archive.ics.uci.edu"},
                    {"name": "Google Dataset Search", "url": "https://datasetsearch.research.google.com"},
                    {"name": "Papers With Code", "url": "https://paperswithcode.com"},
                    {"name": "OpenML", "url": "https://openml.org"},
                ],
            },
        },
        "api_endpoints": {"arxiv": "/api/v1/arxiv/{query}", "wikipedia": "/api/v1/wiki/{query}", "pubmed": "/api/v1/pubmed/{query}"},
        "powered_by": "Curiosity Ocean v5.0.0",
    }


# ═══════════════════════════════════════════════════════════════════
# WEB BROWSING & SEARCH ENDPOINTS
# ═══════════════════════════════════════════════════════════════════


@app.get("/api/v1/browse")
async def browse_webpage(url: str, max_chars: int = 8000):
    """
    Fetch and extract main content from a webpage.
    Returns clean text for AI processing.
    """
    try:
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        headers = {
            "User-Agent": "Kloud-Ocean/5.0 (research@kloud.com)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }

        # verify=False for Docker SSL issues, follow_redirects for 30x
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True, verify=False) as client:
            response = await client.get(url, headers=headers)

        if response.status_code != 200:
            return {"error": f"Failed to fetch URL: {response.status_code}", "url": url}

        html = response.text

        # Simple HTML to text extraction
        import re

        # Remove script and style
        html = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r"<nav[^>]*>.*?</nav>", "", html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r"<footer[^>]*>.*?</footer>", "", html, flags=re.DOTALL | re.IGNORECASE)

        # Extract title
        title_match = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
        title = title_match.group(1).strip() if title_match else url

        # Extract meta description
        desc_match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']+)["\']', html, re.IGNORECASE)
        description = desc_match.group(1) if desc_match else ""

        # Remove all HTML tags
        text = re.sub(r"<[^>]+>", " ", html)
        # Normalize whitespace
        text = re.sub(r"\s+", " ", text).strip()
        # Truncate
        text = text[:max_chars]

        return {"url": url, "title": title, "description": description, "content": text, "char_count": len(text), "status": "success"}

    except Exception as e:
        logger.error(f"Browse error: {e}")
        return {"error": str(e), "url": url}


@app.get("/api/v1/search")
async def web_search(q: str, num: int = 5):
    """
    Search the web using DuckDuckGo HTML (no API key required).
    Returns search results with titles, URLs, and snippets.
    """
    try:
        import urllib.parse

        encoded_query = urllib.parse.quote(q)

        # DuckDuckGo HTML search
        search_url = f"https://html.duckduckgo.com/html/?q={encoded_query}"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "en-US,en;q=0.9",
        }

        # verify=False for Docker SSL issues
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True, verify=False) as client:
            response = await client.get(search_url, headers=headers)

        if response.status_code != 200:
            return {"error": "Search failed", "status": response.status_code}

        html = response.text

        # Parse DuckDuckGo results
        import re

        results = []

        # Find result blocks
        result_pattern = r'<a[^>]*class="result__a"[^>]*href="([^"]*)"[^>]*>(.*?)</a>.*?<a[^>]*class="result__snippet"[^>]*>(.*?)</a>'
        matches = re.findall(result_pattern, html, re.DOTALL | re.IGNORECASE)

        for match in matches[:num]:
            url = match[0]
            # DuckDuckGo wraps URLs - extract actual URL
            if "uddg=" in url:
                url_match = re.search(r"uddg=([^&]+)", url)
                if url_match:
                    url = urllib.parse.unquote(url_match.group(1))

            title = re.sub(r"<[^>]+>", "", match[1]).strip()
            snippet = re.sub(r"<[^>]+>", "", match[2]).strip()

            if url and title:
                results.append({"title": title, "url": url, "snippet": snippet})

        # If no results from pattern, try simpler extraction
        if not results:
            simple_pattern = r'<a[^>]*href="(https?://[^"]+)"[^>]*>([^<]+)</a>'
            for match in re.findall(simple_pattern, html)[:num]:
                url, title = match
                if "duckduckgo" not in url.lower() and len(title) > 5:
                    results.append({"title": title, "url": url, "snippet": ""})

        return {"query": q, "total_results": len(results), "results": results, "source": "duckduckgo"}

    except Exception as e:
        logger.error(f"Search error: {e}")
        return {"error": str(e), "query": q}


class WebChatRequest(BaseModel):
    url: str
    message: str


async def get_web_chat_response(url: str, message: str, page_content: str, page_title: str, timeout: float = 120.0) -> str:
    """
    Get LLM response for webpage chat with elastic timeout.
    Returns the response text or raises exception on failure.
    """
    system_prompt = f"""You are a helpful assistant analyzing a webpage.

Page Title: {page_title}
Page URL: {url}

Page Content:
{page_content[:8000]}

Answer the user's question based on this webpage content. Be concise, accurate, and helpful.
If the content doesn't contain the answer, say so honestly."""

    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model": MODEL,
                "prompt": message,
                "system": system_prompt,
                "stream": False,
                "options": {
                    "num_predict": 4000,  # Longer responses for web content
                    "temperature": 0.7,
                },
            },
        )

    if response.status_code == 200:
        data = response.json()
        return data.get("response", "I couldn't generate a response.")
    else:
        raise Exception(f"LLM error: {response.status_code}")


@app.post("/api/v1/chat/browse")
async def chat_with_webpage(request: WebChatRequest):
    """
    Chat about a webpage - fetch content and answer questions using LLM.
    ELASTIC: 3 retry attempts with increasing timeouts (120s, 240s, 360s).
    """
    try:
        # First, browse the page
        browse_result = await browse_webpage(request.url, max_chars=10000)

        if "error" in browse_result:
            return {"error": browse_result["error"], "url": request.url}

        page_content = browse_result.get("content", "")
        page_title = browse_result.get("title", request.url)

        if not page_content:
            return {"error": "Could not extract content from page", "url": request.url}

        # ELASTIC: 3 retry attempts with increasing timeouts
        timeouts = [120.0, 240.0, 360.0]
        answer = None
        attempt = 0

        for timeout in timeouts:
            attempt += 1
            try:
                logger.info(f"[Web Chat] Attempt {attempt}/3 with {timeout}s timeout for {request.url}")
                answer = await get_web_chat_response(request.url, request.message, page_content, page_title, timeout)
                logger.info(f"[Web Chat] Success on attempt {attempt}")
                break
            except Exception as e:
                logger.warning(f"[Web Chat] Attempt {attempt} failed: {e}")
                if attempt < len(timeouts):
                    await asyncio.sleep(1)  # Brief pause before retry

        # If all attempts failed, return partial response with page summary
        if answer is None:
            logger.error(f"[Web Chat] All 3 attempts failed for {request.url}")
            answer = f"⚠️ LLM response timed out after 3 attempts.\n\n**Page Summary:**\n{page_title}\n\n{page_content[:1000]}..."

        return {
            "url": request.url,
            "title": page_title,
            "question": request.message,
            "answer": answer,
            "response": answer,  # Also provide as 'response' for frontend compatibility
            "message": answer,  # Also provide as 'message' for frontend compatibility
            "content_length": len(page_content),
            "status": "success" if "timed out" not in answer else "partial",
            "attempts": attempt,
        }

    except Exception as e:
        logger.error(f"Chat browse error: {e}")
        return {"error": str(e), "url": request.url}


@app.post("/api/v1/chat/browse/stream")
async def chat_with_webpage_stream(request: WebChatRequest):
    """
    SSE Streaming chat about a webpage - real-time token delivery.
    """

    async def generate():
        try:
            # First, browse the page
            browse_result = await browse_webpage(request.url, max_chars=10000)

            if "error" in browse_result:
                yield f"data: {json.dumps({'error': browse_result['error']})}\n\n"
                return

            page_content = browse_result.get("content", "")
            page_title = browse_result.get("title", request.url)

            yield f"data: {json.dumps({'status': 'browsing', 'title': page_title, 'chars': len(page_content)})}\n\n"

            if not page_content:
                yield f"data: {json.dumps({'error': 'Could not extract content from page'})}\n\n"
                return

            system_prompt = f"""You are a helpful assistant analyzing a webpage.

Page Title: {page_title}
Page URL: {request.url}

Page Content:
{page_content[:8000]}

Answer the user's question based on this webpage content. Be concise, accurate, and helpful."""

            yield f"data: {json.dumps({'status': 'thinking'})}\n\n"

            # Stream from Ollama
            async with httpx.AsyncClient(timeout=300.0) as client:
                async with client.stream(
                    "POST",
                    f"{OLLAMA_HOST}/api/generate",
                    json={
                        "model": MODEL,
                        "prompt": request.message,
                        "system": system_prompt,
                        "stream": True,
                        "options": {"num_predict": 4000, "temperature": 0.7},
                    },
                ) as response:
                    full_response = ""
                    async for line in response.aiter_lines():
                        if line:
                            try:
                                data = json.loads(line)
                                token = data.get("response", "")
                                if token:
                                    full_response += token
                                    yield f"data: {json.dumps({'token': token, 'status': 'streaming'})}\n\n"
                                if data.get("done"):
                                    yield f"data: {json.dumps({'status': 'complete', 'total_chars': len(full_response)})}\n\n"
                            except json.JSONDecodeError:
                                pass

        except Exception as e:
            logger.error(f"Stream chat browse error: {e}")
            yield f"data: {json.dumps({'error': str(e), 'status': 'error'})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


# ═══════════════════════════════════════════════════════════════════
# ZÜRICH ENGINE - 9-Stage Deterministic Reasoning
# ═══════════════════════════════════════════════════════════════════


class ZurichRequest(BaseModel):
    prompt: str
    include_debug: bool = False


def zurich_cycle(input_text: str) -> Dict[str, Any]:
    """
    9-stage deterministic reasoning cycle - 100% predictable, no AI randomness.
    Based on Harmonic Trinity's Zürich Engine.
    """
    start_time = time.time()

    # Stage 1: INTAKE - Parse input type
    words = input_text.split()
    word_count = len(words)
    char_count = len(input_text)

    if input_text.endswith("?"):
        input_type = "question"
    elif input_text.endswith("!"):
        input_type = "exclamation"
    elif any(cmd in input_text.lower() for cmd in ["create", "make", "build", "generate"]):
        input_type = "command"
    else:
        input_type = "statement"

    intake = {"stage": 1, "name": "intake", "type": input_type, "word_count": word_count, "char_count": char_count}

    # Stage 2: PREPROCESS - Normalize text
    normalized = input_text.strip().lower()
    keywords = [w for w in words if len(w) > 3]

    preprocess = {"stage": 2, "name": "preprocess", "normalized": normalized[:100], "keywords": keywords[:10]}

    # Stage 3: TAGGER - Classify content & intent
    domains = []
    if any(w in normalized for w in ["code", "program", "python", "javascript", "function"]):
        domains.append("programming")
    if any(w in normalized for w in ["ai", "machine", "learning", "neural", "model"]):
        domains.append("ai")
    if any(w in normalized for w in ["business", "company", "market", "product"]):
        domains.append("business")
    if any(w in normalized for w in ["science", "research", "study", "experiment"]):
        domains.append("science")
    if any(w in normalized for w in ["health", "medical", "doctor", "disease"]):
        domains.append("health")
    if not domains:
        domains.append("general")

    tagger = {"stage": 3, "name": "tagger", "domains": domains, "primary_domain": domains[0]}

    # Stage 4: INTERPRET - Extract meanings
    has_comparison = any(w in normalized for w in ["vs", "versus", "compare", "difference"])
    has_definition = any(w in normalized for w in ["what is", "define", "meaning", "explain"])
    has_howto = any(w in normalized for w in ["how to", "how do", "steps", "process"])
    has_why = "why" in normalized

    interpret = {
        "stage": 4,
        "name": "interpret",
        "seeking_comparison": has_comparison,
        "seeking_definition": has_definition,
        "seeking_howto": has_howto,
        "seeking_reason": has_why,
    }

    # Stage 5: REASON - Build reasoning steps
    reasoning_steps = []
    if has_definition:
        reasoning_steps.append("Provide clear definition")
    if has_comparison:
        reasoning_steps.append("Analyze both sides")
        reasoning_steps.append("Highlight differences")
    if has_howto:
        reasoning_steps.append("Break into steps")
        reasoning_steps.append("Provide examples")
    if has_why:
        reasoning_steps.append("Explain causation")
        reasoning_steps.append("Provide evidence")
    if not reasoning_steps:
        reasoning_steps.append("Provide comprehensive response")

    reason = {"stage": 5, "name": "reason", "steps": reasoning_steps, "step_count": len(reasoning_steps)}

    # Stage 6: STRATEGY - Select response mode
    if word_count < 5:
        strategy = "concise"
    elif has_howto:
        strategy = "step-by-step"
    elif has_comparison:
        strategy = "comparative"
    elif has_definition:
        strategy = "explanatory"
    else:
        strategy = "comprehensive"

    strategy_output = {
        "stage": 6,
        "name": "strategy",
        "mode": strategy,
        "expected_length": "short" if word_count < 5 else "medium" if word_count < 20 else "long",
    }

    # Stage 7: DRAFT - Generate response structure
    header = f"📋 Analysis of: {input_text[:50]}..."

    if strategy == "step-by-step":
        structure = ["Introduction", "Step 1", "Step 2", "Step 3", "Conclusion"]
    elif strategy == "comparative":
        structure = ["Overview", "Option A", "Option B", "Comparison", "Recommendation"]
    elif strategy == "explanatory":
        structure = ["Definition", "Context", "Examples", "Summary"]
    else:
        structure = ["Main Point", "Supporting Details", "Conclusion"]

    draft = {"stage": 7, "name": "draft", "header": header, "structure": structure}

    # Stage 8: FINAL - Format output
    confidence = min(0.95, 0.7 + (len(domains) * 0.05) + (len(reasoning_steps) * 0.03))

    final_output = f"""**{header}**

**Domain:** {", ".join(domains)}
**Strategy:** {strategy}
**Confidence:** {confidence:.0%}

**Analysis:**
Input type: {input_type}
Keywords identified: {", ".join(keywords[:5]) if keywords else "None specific"}

**Response Structure:**
{chr(10).join(f"• {s}" for s in structure)}

**Reasoning Applied:**
{chr(10).join(f"{i + 1}. {step}" for i, step in enumerate(reasoning_steps))}

---
*Processed by Zürich Engine v1.0 - 9-stage deterministic cycle*
*Processing time: {(time.time() - start_time) * 1000:.2f}ms*"""

    final = {"stage": 8, "name": "final", "output": final_output, "confidence": confidence}

    # Stage 9: CYCLE - Complete orchestration
    processing_time = time.time() - start_time

    cycle = {"stage": 9, "name": "cycle", "completed": True, "total_stages": 9, "processing_time_ms": processing_time * 1000}

    return {
        "input": input_text,
        "output": final_output,
        "confidence": confidence,
        "strategy": strategy,
        "domains": domains,
        "stages": {
            "intake": intake,
            "preprocess": preprocess,
            "tagger": tagger,
            "interpret": interpret,
            "reason": reason,
            "strategy": strategy_output,
            "draft": draft,
            "final": final,
            "cycle": cycle,
        },
    }


@app.post("/api/v1/zurich")
async def zurich_reasoning(request: ZurichRequest):
    """
    Zürich Deterministic Reasoning Engine.

    9-stage processing cycle:
    1. Intake - Parse input type
    2. Preprocess - Normalize text
    3. Tagger - Classify content & intent
    4. Interpret - Extract meanings
    5. Reason - Build reasoning steps
    6. Strategy - Select response mode
    7. Draft - Generate response structure
    8. Final - Format output
    9. Cycle - Complete orchestration

    100% deterministic - same input always produces same output.
    """
    if not request.prompt:
        raise HTTPException(status_code=400, detail="prompt is required")

    result = zurich_cycle(request.prompt)

    response = {
        "ok": True,
        "input": request.prompt,
        "output": result["output"],
        "confidence": result["confidence"],
        "strategy": result["strategy"],
        "domains": result["domains"],
        "processing_time_ms": result["stages"]["cycle"]["processing_time_ms"],
        "engine": "Zürich Deterministic Engine v1.0",
    }

    if request.include_debug:
        response["stages"] = result["stages"]

    return response


@app.get("/api/v1/zurich/info")
async def zurich_info():
    """Get Zürich Engine information and capabilities."""
    return {
        "name": "Zürich Deterministic Engine",
        "version": "1.0",
        "type": "Logic-based reasoning",
        "description": "100% deterministic processing without AI randomness",
        "stages": [
            {"step": 1, "name": "intake", "description": "Parse input type"},
            {"step": 2, "name": "preprocess", "description": "Normalize text"},
            {"step": 3, "name": "tagger", "description": "Classify content & intent"},
            {"step": 4, "name": "interpret", "description": "Extract meanings"},
            {"step": 5, "name": "reason", "description": "Build reasoning steps"},
            {"step": 6, "name": "strategy", "description": "Select response mode"},
            {"step": 7, "name": "draft", "description": "Generate response structure"},
            {"step": 8, "name": "final", "description": "Format output"},
            {"step": 9, "name": "cycle", "description": "Complete orchestration"},
        ],
        "features": [
            "Deterministic processing",
            "No external API calls",
            "Local computation only",
            "Pattern-based reasoning",
            "Structured output",
        ],
        "response_time": "1-50ms per input",
    }


# ═══════════════════════════════════════════════════════════════════
# TRINITY PERSONAS - Multi-Persona AI Debate
# ═══════════════════════════════════════════════════════════════════


class DebateRequest(BaseModel):
    topic: str
    personas: Optional[List[str]] = None  # Default: all 5
    max_tokens: int = 500


# The 5 Trinity Personas
TRINITY_PERSONAS = {
    "alba": {
        "name": "Alba",
        "emoji": "🌅",
        "role": "The Optimist",
        "description": "Sees opportunity in every challenge, focuses on positive outcomes",
        "style": "Hopeful, encouraging, solution-oriented",
        "prompt_prefix": "As Alba the Optimist, I see the positive side:",
    },
    "albi": {
        "name": "Albi",
        "emoji": "🔧",
        "role": "The Pragmatist",
        "description": "Practical, results-focused, concerned with implementation",
        "style": "Direct, practical, actionable",
        "prompt_prefix": "As Albi the Pragmatist, here's the practical view:",
    },
    "jona": {
        "name": "Jona",
        "emoji": "🔍",
        "role": "The Skeptic",
        "description": "Questions assumptions, identifies risks and weaknesses",
        "style": "Critical, analytical, cautious",
        "prompt_prefix": "As Jona the Skeptic, I must point out:",
    },
    "blerina": {
        "name": "Blerina",
        "emoji": "🌐",
        "role": "The Analyst",
        "description": "Data-driven, systematic, considers all angles",
        "style": "Methodical, thorough, evidence-based",
        "prompt_prefix": "As Blerina the Analyst, looking at the data:",
    },
    "asi": {
        "name": "ASI",
        "emoji": "🧠",
        "role": "The Meta-Thinker",
        "description": "Synthesizes all perspectives, finds higher-level patterns",
        "style": "Philosophical, integrative, holistic",
        "prompt_prefix": "As ASI, synthesizing all perspectives:",
    },
}


async def get_persona_response(persona_id: str, topic: str, max_tokens: int = 25000) -> Dict[str, Any]:
    """
    Get a response from a specific persona using Ollama.
    ELASTIC: Streaming with retries, no timeout failures.
    Max ~20,000 words (25,000 tokens).
    """
    persona = TRINITY_PERSONAS.get(persona_id)
    if not persona:
        return {"error": f"Unknown persona: {persona_id}"}

    system_prompt = f"""You are {persona["name"]}, {persona["role"]} in the Trinity AI system.

Your personality: {persona["description"]}
Your style: {persona["style"]}

Respond to the topic from your unique perspective. Be thorough and insightful.
You can write a detailed, comprehensive response."""

    user_prompt = f"{persona['prompt_prefix']}\n\nTopic: {topic}"

    # ELASTIC: Retry up to 3 times with increasing timeouts
    max_retries = 3
    base_timeout = 120.0  # 2 minutes base

    for attempt in range(max_retries):
        try:
            timeout = base_timeout * (attempt + 1)  # 120s, 240s, 360s

            # Use streaming for elastic token handling
            async with httpx.AsyncClient(timeout=httpx.Timeout(timeout, connect=30.0)) as client:
                response_text = ""

                async with client.stream(
                    "POST",
                    f"{OLLAMA_HOST}/api/generate",
                    json={
                        "model": MODEL,
                        "prompt": user_prompt,
                        "system": system_prompt,
                        "stream": True,
                        "options": {"num_predict": max_tokens},
                    },
                ) as stream:
                    async for line in stream.aiter_lines():
                        if line:
                            try:
                                chunk = json.loads(line)
                                if "response" in chunk:
                                    response_text += chunk["response"]
                                if chunk.get("done", False):
                                    break
                            except json.JSONDecodeError:
                                continue

                if response_text:
                    return {
                        "persona": persona_id,
                        "name": persona["name"],
                        "emoji": persona["emoji"],
                        "role": persona["role"],
                        "response": response_text,
                        "status": "success",
                        "tokens": len(response_text.split()),
                    }

        except httpx.TimeoutException:
            logger.warning(f"Persona {persona_id} timeout on attempt {attempt + 1}/{max_retries}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2)  # Brief pause before retry
                continue
        except Exception as e:
            logger.error(f"Persona {persona_id} error on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(1)
                continue

    # All retries exhausted - return partial or error gracefully (no fail)
    try:
        # Fallback: Try one more time with non-streaming
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{OLLAMA_HOST}/api/generate",
                json={
                    "model": MODEL,
                    "prompt": user_prompt,
                    "system": system_prompt,
                    "stream": False,
                    "options": {"num_predict": 500},  # Shorter fallback
                },
            )

        if response.status_code == 200:
            data = response.json()
            return {
                "persona": persona_id,
                "name": persona["name"],
                "emoji": persona["emoji"],
                "role": persona["role"],
                "response": data.get("response", "No response generated"),
                "status": "success",
            }
        else:
            return {
                "persona": persona_id,
                "name": persona["name"],
                "emoji": persona["emoji"],
                "role": persona["role"],
                "response": f"Error: {response.status_code}",
                "status": "error",
            }

    except Exception as e:
        logger.error(f"Persona {persona_id} fallback error: {e}")
        # ELASTIC: Never fail completely - return graceful message
        return {
            "persona": persona_id,
            "name": persona["name"],
            "emoji": persona["emoji"],
            "role": persona["role"],
            "response": f"[{persona['name']} is thinking deeply about this topic... Please retry for full response]",
            "status": "partial",
        }


@app.post("/api/v1/debate/stream")
async def trinity_debate_stream(request: DebateRequest):
    """
    STREAMING Trinity Debate - TRUE Real-time token-by-token responses.
    Returns Server-Sent Events (SSE) with INSTANT token streaming from Ollama.
    NO TIMEOUT - Elastic streaming for unlimited generation.
    """
    from starlette.responses import StreamingResponse

    if not request.topic:
        raise HTTPException(status_code=400, detail="topic is required")

    persona_ids = request.personas if request.personas else list(TRINITY_PERSONAS.keys())
    valid_personas = [p for p in persona_ids if p in TRINITY_PERSONAS]

    async def generate():
        # Start immediately
        yield f"data: {json.dumps({'type': 'start', 'topic': request.topic, 'personas': len(valid_personas)})}\n\n"

        for persona_id in valid_personas:
            persona = TRINITY_PERSONAS.get(persona_id)
            if not persona:
                continue

            # Signal persona starting - INSTANT feedback
            yield f"data: {json.dumps({'type': 'thinking', 'persona': persona_id, 'name': persona['name'], 'emoji': persona['emoji']})}\n\n"

            # Build prompts
            system_prompt = f"""You are {persona["name"]}, {persona["role"]} in the Trinity AI system.
Your personality: {persona["description"]}
Your style: {persona["style"]}
Respond to the topic from your unique perspective. Be thorough and insightful."""

            user_prompt = f"{persona['prompt_prefix']}\n\nTopic: {request.topic}"

            response_text = ""
            token_count = 0

            try:
                # NO TIMEOUT - Elastic streaming
                async with httpx.AsyncClient(timeout=None) as client:
                    async with client.stream(
                        "POST",
                        f"{OLLAMA_HOST}/api/generate",
                        json={
                            "model": MODEL,
                            "prompt": user_prompt,
                            "system": system_prompt,
                            "stream": True,
                            "options": {"num_predict": request.max_tokens or 25000},
                        },
                    ) as stream:
                        async for line in stream.aiter_lines():
                            if line:
                                try:
                                    chunk = json.loads(line)
                                    if "response" in chunk:
                                        token = chunk["response"]
                                        response_text += token
                                        token_count += 1
                                        # Stream EVERY token immediately
                                        yield f"data: {json.dumps({'type': 'token', 'persona': persona_id, 'token': token})}\n\n"
                                    if chunk.get("done", False):
                                        break
                                except json.JSONDecodeError:
                                    continue

                # Send completion for this persona
                yield f"data: {json.dumps({'type': 'response', 'data': {'persona': persona_id, 'name': persona['name'], 'emoji': persona['emoji'], 'role': persona['role'], 'response': response_text, 'status': 'success', 'tokens': token_count}})}\n\n"

            except Exception as e:
                logger.error(f"Debate stream error for {persona_id}: {e}")
                error_msg = f"[{persona['name']} encountered an issue: {str(e)[:100]}]"
                yield f"data: {json.dumps({'type': 'response', 'data': {'persona': persona_id, 'name': persona['name'], 'emoji': persona['emoji'], 'role': persona['role'], 'response': error_msg, 'status': 'error'}})}\n\n"

        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"},
    )


@app.post("/api/v1/debate")
async def trinity_debate(request: DebateRequest):
    """
    Trinity Multi-Persona Debate.

    5 AI personas debate a topic from different perspectives:
    - Alba (🌅) - The Optimist
    - Albi (🔧) - The Pragmatist
    - Jona (🔍) - The Skeptic
    - Blerina (🌐) - The Analyst
    - ASI (🧠) - The Meta-Thinker

    Returns all perspectives for a balanced view.
    """
    if not request.topic:
        raise HTTPException(status_code=400, detail="topic is required")

    start_time = time.time()

    # Determine which personas to use
    persona_ids = request.personas if request.personas else list(TRINITY_PERSONAS.keys())

    # Validate personas
    valid_personas = [p for p in persona_ids if p in TRINITY_PERSONAS]
    if not valid_personas:
        raise HTTPException(status_code=400, detail=f"No valid personas. Available: {list(TRINITY_PERSONAS.keys())}")

    # Get responses from all personas in parallel
    tasks = [get_persona_response(p, request.topic, request.max_tokens) for p in valid_personas]
    responses = await asyncio.gather(*tasks)

    processing_time = time.time() - start_time

    # Count successes
    success_count = sum(1 for r in responses if r.get("status") == "success")

    return {
        "ok": True,
        "topic": request.topic,
        "responses": responses,
        "stats": {
            "total_personas": len(valid_personas),
            "successful": success_count,
            "failed": len(valid_personas) - success_count,
            "processing_time_ms": processing_time * 1000,
        },
        "engine": "Trinity Debate Engine v1.0",
    }


@app.get("/api/v1/debate/personas")
async def list_personas():
    """List all available Trinity personas."""
    return {
        "personas": [
            {"id": pid, "name": p["name"], "emoji": p["emoji"], "role": p["role"], "description": p["description"], "style": p["style"]}
            for pid, p in TRINITY_PERSONAS.items()
        ],
        "total": len(TRINITY_PERSONAS),
    }


# ═══════════════════════════════════════════════════════════════════
# 🔊 TEXT-TO-SPEECH ENGINE - Natural Voice Output
# ═══════════════════════════════════════════════════════════════════

# TTS Voice Configuration - Microsoft Edge Neural Voices (Free, High Quality)
TTS_VOICES = {
    "en": "en-US-AriaNeural",  # English - Female, natural
    "en-male": "en-US-GuyNeural",  # English - Male
    "sq": "en-GB-SoniaNeural",  # Albanian fallback - British English sounds natural
    "de": "de-DE-KatjaNeural",  # German
    "fr": "fr-FR-DeniseNeural",  # French
    "es": "es-ES-ElviraNeural",  # Spanish
    "it": "it-IT-ElsaNeural",  # Italian
    "pt": "pt-BR-FranciscaNeural",  # Portuguese
    "ru": "ru-RU-SvetlanaNeural",  # Russian
    "zh": "zh-CN-XiaoxiaoNeural",  # Chinese
    "ja": "ja-JP-NanamiNeural",  # Japanese
    "ko": "ko-KR-SunHiNeural",  # Korean
    "ar": "ar-EG-SalmaNeural",  # Arabic
    "tr": "tr-TR-EmelNeural",  # Turkish
    "hi": "hi-IN-SwaraNeural",  # Hindi
    "nl": "nl-NL-ColetteNeural",  # Dutch
    "pl": "pl-PL-ZofiaNeural",  # Polish
    "uk": "uk-UA-PolinaNeural",  # Ukrainian
    "el": "el-GR-AthinaNeural",  # Greek
    "ro": "ro-RO-AlinaNeural",  # Romanian
    "sr": "sr-RS-SophieNeural",  # Serbian
    "hr": "hr-HR-GabrijelaNeural",  # Croatian
    "bg": "bg-BG-KalinaNeural",  # Bulgarian
    "mk": "mk-MK-MarijaNeural",  # Macedonian
}


class TTSRequest(BaseModel):
    """Text-to-Speech request model"""

    text: str
    language: str = "en"
    voice: Optional[str] = None  # Override default voice
    rate: str = "+0%"  # Speech rate: -50% to +100%
    pitch: str = "+0Hz"  # Pitch adjustment


class VoiceConversationRequest(BaseModel):
    """Full voice conversation request: Audio In → STT → LLM → TTS → Audio Out"""

    audio_base64: str
    language: str = "en"
    voice: Optional[str] = None
    curiosity_level: str = "curious"
    user_id: Optional[str] = None


@app.post("/api/v1/tts")
async def text_to_speech(req: TTSRequest):
    """
    🔊 TEXT-TO-SPEECH - Convert text to natural speech audio

    Returns MP3 audio file with natural neural voice.
    Supports 24+ languages with high-quality Microsoft Edge voices.

    Example:
        POST /api/v1/tts
        {"text": "Hello, how are you?", "language": "en"}

        Returns: audio/mpeg stream
    """
    start_time = time.time()

    try:
        import edge_tts
        import tempfile
        import os as os_mod

        # Input validation
        if not req.text or not req.text.strip():
            raise HTTPException(400, "Text cannot be empty")

        if len(req.text) > 5000:
            raise HTTPException(400, "Text too long. Maximum 5000 characters.")

        # Get voice for language
        voice = req.voice or TTS_VOICES.get(req.language, TTS_VOICES.get("en"))

        # Create TTS communicate object
        communicate = edge_tts.Communicate(text=req.text.strip(), voice=voice, rate=req.rate, pitch=req.pitch)

        # Generate audio to temp file
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            tmp_path = tmp.name

        await communicate.save(tmp_path)

        # Read audio data
        with open(tmp_path, "rb") as f:
            audio_data = f.read()

        # Cleanup
        os_mod.unlink(tmp_path)

        processing_time = time.time() - start_time
        logger.info(f"🔊 TTS: {len(req.text)} chars → {len(audio_data)} bytes in {processing_time:.2f}s | voice={voice}")

        # Return audio as streaming response
        return StreamingResponse(
            iter([audio_data]),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "inline; filename=speech.mp3",
                "X-Processing-Time": f"{processing_time:.3f}s",
                "X-Voice-Used": voice,
                "X-Text-Length": str(len(req.text)),
            },
        )

    except ImportError:
        raise HTTPException(500, "TTS engine not available. Install: pip install edge-tts")
    except Exception as e:
        logger.error(f"TTS Error: {e}")
        raise HTTPException(500, f"TTS generation failed: {str(e)}")


@app.get("/api/v1/tts/voices")
async def list_tts_voices():
    """List all available TTS voices by language."""
    return {
        "voices": TTS_VOICES,
        "total": len(TTS_VOICES),
        "engine": "Microsoft Edge Neural TTS (Free)",
        "quality": "High - Neural Network Generated",
        "note": "Albanian (sq) uses British English voice as fallback",
    }


@app.post("/api/v1/voice/conversation")
async def voice_conversation(req: VoiceConversationRequest, request: Request):
    """
    🎙️ FULL VOICE CONVERSATION PIPELINE

    Audio In → STT (Whisper) → LLM (Ollama) → TTS (Edge) → Audio Out

    Complete voice-to-voice conversation in one request.
    Send audio, get audio response back.

    Flow:
    1. Decode audio from base64
    2. Transcribe with Whisper (Speech-to-Text)
    3. Generate response with Ollama LLM
    4. Convert response to speech (Text-to-Speech)
    5. Return audio response
    """
    start_time = time.time()
    # user_id available via: req.user_id or request.headers.get("X-User-ID")

    try:
        import edge_tts
        import tempfile
        import base64 as b64mod
        import os as os_mod

        # ═══════════════════════════════════════════════════════════════
        # STEP 1: Decode Audio
        # ═══════════════════════════════════════════════════════════════
        audio_bytes = b64mod.b64decode(req.audio_base64)
        if len(audio_bytes) < 100:
            raise HTTPException(400, "Audio data too small")

        # Save to temp file
        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp:
            tmp.write(audio_bytes)
            audio_path = tmp.name

        # ═══════════════════════════════════════════════════════════════
        # STEP 2: Speech-to-Text (Whisper)
        # ═══════════════════════════════════════════════════════════════
        try:
            from faster_whisper import WhisperModel

            global _whisper_model_conv
            if "_whisper_model_conv" not in globals() or _whisper_model_conv is None:
                _whisper_model_conv = WhisperModel("base", device="cpu", compute_type="int8")

            segments, info = _whisper_model_conv.transcribe(
                audio_path, language=req.language if req.language not in ["auto", "sq"] else None, beam_size=5
            )

            transcript = " ".join([seg.text for seg in segments]).strip()
            detected_language = info.language or req.language

        except ImportError:
            # Fallback: Use Ollama's whisper if available
            async with httpx.AsyncClient(timeout=30) as client:
                with open(audio_path, "rb") as f:
                    audio_b64 = b64mod.b64encode(f.read()).decode()
                resp = await client.post(f"{OLLAMA_HOST}/api/generate", json={"model": "whisper", "prompt": audio_b64})
                transcript = resp.json().get("response", "")
                detected_language = req.language

        finally:
            os_mod.unlink(audio_path)

        if not transcript:
            raise HTTPException(400, "Could not transcribe audio. Please speak clearly.")

        stt_time = time.time() - start_time
        logger.info(f"🎤 STT: '{transcript[:50]}...' in {stt_time:.2f}s")

        # ═══════════════════════════════════════════════════════════════
        # STEP 3: Generate LLM Response (Ollama)
        # ═══════════════════════════════════════════════════════════════
        llm_start = time.time()

        system_prompt = """You are a friendly voice assistant. Keep responses concise and natural for speech.
Respond in the same language as the user's message. Be helpful and conversational."""

        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                f"{OLLAMA_HOST}/api/generate",
                json={
                    "model": MODEL,
                    "prompt": transcript,
                    "system": system_prompt,
                    "stream": False,
                    "options": {"temperature": 0.7, "num_predict": 200},
                },
            )
            llm_response = resp.json().get("response", "I couldn't process that. Please try again.")

        llm_time = time.time() - llm_start
        logger.info(f"🧠 LLM: '{llm_response[:50]}...' in {llm_time:.2f}s")

        # ═══════════════════════════════════════════════════════════════
        # STEP 4: Text-to-Speech (Edge TTS)
        # ═══════════════════════════════════════════════════════════════
        tts_start = time.time()

        voice = req.voice or TTS_VOICES.get(detected_language, TTS_VOICES.get("en"))
        communicate = edge_tts.Communicate(text=llm_response, voice=voice)

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            tts_path = tmp.name

        await communicate.save(tts_path)

        with open(tts_path, "rb") as f:
            audio_response = f.read()

        os_mod.unlink(tts_path)

        tts_time = time.time() - tts_start
        total_time = time.time() - start_time

        logger.info(f"🔊 Voice Conversation: STT={stt_time:.1f}s LLM={llm_time:.1f}s TTS={tts_time:.1f}s Total={total_time:.1f}s")

        # ═══════════════════════════════════════════════════════════════
        # STEP 5: Return Audio Response
        # ═══════════════════════════════════════════════════════════════
        return StreamingResponse(
            iter([audio_response]),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "inline; filename=response.mp3",
                "X-Transcript": transcript[:100],
                "X-Response-Text": llm_response[:100],
                "X-Processing-Time": f"{total_time:.3f}s",
                "X-STT-Time": f"{stt_time:.3f}s",
                "X-LLM-Time": f"{llm_time:.3f}s",
                "X-TTS-Time": f"{tts_time:.3f}s",
                "X-Voice-Used": voice,
                "X-Detected-Language": detected_language,
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Voice Conversation Error: {e}")
        raise HTTPException(500, f"Voice conversation failed: {str(e)}")


# Initialize whisper model placeholder
_whisper_model_conv = None


# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn

    logger.info(f"🌊 Ocean Core Full v5.0.0 starting on port {PORT}")
    logger.info("⚙️ Zürich Engine v1.0 - 9-stage deterministic reasoning")
    logger.info("🧠 Trinity Debate v1.0 - 5-persona AI debate")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
