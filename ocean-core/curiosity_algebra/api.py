# -*- coding: utf-8 -*-
"""
🌊 CURIOSITY ALGEBRA API
========================
FastAPI endpoints për Curiosity Ocean Signal Algebra System.

Endpoints:
- /events - Unified Event Bus
- /cells - Cell Registry
- /call - Call Operator
- /curiosity - Curiosity Orchestrator
- /signals - Universal Signal Integrator
- /bin/* - REAL BINARY endpoints (CBOR, MessagePack, Custom)
"""

from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime
import struct
import time

from .event_bus import Event, EventType, get_event_bus
from .signal_algebra import get_signal_algebra
from .cell_registry import Cell, CellRole, CellState, get_cell_registry
from .call_operator import CallScope, create_call_operator
from .curiosity_orchestrator import get_curiosity_orchestrator
from .signal_integrator import get_signal_integrator
from .binary_protocols import get_binary_service, BinaryFormat, BinaryEncoder
from .binary_middleware import BinaryResponse, create_binary_response
from .binary_algebra import get_binary_algebra, BinaryOp, BinaryNumber, BinarySignal, BinaryMatrix
from .cbp_protocol import (
    get_protocol, get_schema_registry, KloudProtocol, Frame, StreamFrame,
    FrameFlags, MessageType, dump_frame, read_clsn_file, write_clsn_file
)
from .real_learning_engine import get_real_learning

# API Version prefix for security - all APIs must be versioned
router = APIRouter(prefix="/api/v1/curiosity", tags=["Curiosity Ocean Algebra v1"])


# ==================== MODELS ====================

class EventModel(BaseModel):
    source: str
    type: str = "signal"
    payload: Dict[str, Any] = {}
    confidence: float = 1.0
    tags: List[str] = []

class CellModel(BaseModel):
    id: str
    name: str = ""
    role: str = "logic"
    capabilities: List[str] = []
    links: List[str] = []
    metadata: Dict[str, Any] = {}

class CallRequest(BaseModel):
    query: str
    scope: str = "all"
    role: Optional[str] = None
    capability: Optional[str] = None
    cell_id: Optional[str] = None
    cascade: bool = False

class SignalRequest(BaseModel):
    source_id: str
    signal_type: str = "metric"
    payload: Dict[str, Any] = {}


# ==================== EVENT BUS ====================

@router.post("/events")
async def publish_event(event: EventModel):
    """Publiko një ngjarje në Unified Event Bus"""
    bus = get_event_bus()
    
    evt = Event(
        source=event.source,
        type=EventType(event.type) if event.type in EventType._value2member_map_ else EventType.SIGNAL,
        payload=event.payload,
        confidence=event.confidence,
        tags=event.tags
    )
    
    await bus.publish_async(evt)
    
    return {
        "status": "published",
        "event_id": evt.id,
        "timestamp": evt.timestamp.isoformat()
    }

@router.get("/events")
async def get_events(count: int = 100, source: str = None, type: str = None):
    """Merr ngjarjet e fundit"""
    bus = get_event_bus()
    
    if source:
        events = bus.get_by_source(source, count)
    elif type:
        events = bus.get_by_type(EventType(type), count)
    else:
        events = bus.get_recent(count)
    
    return {
        "count": len(events),
        "events": [e.to_dict() for e in events]
    }

@router.get("/events/stats")
async def get_event_stats():
    """Statistikat e Event Bus"""
    return get_event_bus().get_stats()


# ==================== CELL REGISTRY ====================

@router.post("/cells")
async def register_cell(cell: CellModel):
    """Regjistro një qelizë të re"""
    registry = get_cell_registry()
    
    c = Cell(
        id=cell.id,
        name=cell.name,
        role=CellRole(cell.role),
        capabilities=cell.capabilities,
        links=cell.links,
        metadata=cell.metadata,
        state=CellState.ACTIVE
    )
    
    registry.register(c)
    
    return {
        "status": "registered",
        "cell_id": c.id,
        "role": c.role.value
    }

@router.get("/cells")
async def list_cells(role: str = None, state: str = None):
    """Lista e qelizave"""
    registry = get_cell_registry()
    
    role_enum = CellRole(role) if role else None
    state_enum = CellState(state) if state else None
    
    cells = registry.query(role=role_enum, state=state_enum)
    
    return {
        "count": len(cells),
        "cells": [c.to_dict() for c in cells]
    }

@router.get("/cells/{cell_id}")
async def get_cell(cell_id: str):
    """Merr një qelizë specifike"""
    registry = get_cell_registry()
    cell = registry.get(cell_id)
    
    if not cell:
        raise HTTPException(status_code=404, detail="Cell not found")
    
    return cell.to_dict()

@router.get("/cells/graph")
async def get_cell_graph():
    """Grafi i qelizave"""
    return get_cell_registry().get_graph()

@router.get("/cells/stats")
async def get_cell_stats():
    """Statistikat e Cell Registry"""
    return get_cell_registry().get_stats()


# ==================== CALL OPERATOR ====================

@router.post("/call")
async def call_cells(request: CallRequest):
    """Thirr qelizat sipas kritereve"""
    registry = get_cell_registry()
    caller = create_call_operator(registry)
    
    role = CellRole(request.role) if request.role else None
    
    responses = caller.call(
        query=request.query,
        scope=CallScope(request.scope),
        role=role,
        capability=request.capability,
        cell_id=request.cell_id,
        cascade=request.cascade
    )
    
    return {
        "query": request.query,
        "scope": request.scope,
        "total_responses": len(responses),
        "successful": len([r for r in responses if r.success]),
        "responses": [r.to_dict() for r in responses]
    }

@router.post("/call/broadcast")
async def broadcast_to_all(query: str):
    """Broadcast: Thirr TË GJITHA qelizat"""
    registry = get_cell_registry()
    caller = create_call_operator(registry)
    
    responses = caller.broadcast(query)
    
    return {
        "query": query,
        "scope": "all",
        "responses": len(responses)
    }


# ==================== CURIOSITY ORCHESTRATOR ====================

@router.get("/status")
async def get_curiosity_status():
    """Statusi i Curiosity Ocean"""
    orchestrator = get_curiosity_orchestrator()
    return orchestrator.get_status()

@router.post("/ask")
async def ask_curiosity(question: str):
    """Bëj një pyetje kurioziteti"""
    orchestrator = get_curiosity_orchestrator()
    return orchestrator.ask(question)

@router.get("/insights")
async def get_insights(limit: int = 20, severity: str = None):
    """Merr zbulimet e kuriozitetit"""
    orchestrator = get_curiosity_orchestrator()
    return {
        "insights": orchestrator.get_insights(limit, severity)
    }

@router.post("/explore")
async def run_exploration():
    """Ekzekuto një eksplorim të plotë të sistemit"""
    orchestrator = get_curiosity_orchestrator()
    return await orchestrator.run_exploration()


# ==================== SIGNAL ALGEBRA ====================

@router.post("/algebra/analyze")
async def analyze_signal(key: str, values: List[float] = None):
    """Analizë e një sinjali"""
    algebra = get_signal_algebra()
    
    if values:
        for v in values:
            algebra.record(key, v)
    
    return algebra.analyze(key)

@router.post("/algebra/correlate")
async def correlate_signals(signal1: List[float], signal2: List[float]):
    """Gjej korelacionin ndërmjet dy sinjaleve"""
    algebra = get_signal_algebra()
    correlation = algebra.correlate(signal1, signal2)
    
    return {
        "correlation": correlation,
        "interpretation": "strong positive" if correlation > 0.7 else 
                         "strong negative" if correlation < -0.7 else
                         "weak" if abs(correlation) < 0.3 else "moderate"
    }

@router.post("/algebra/aggregate")
async def aggregate_signals(signals: List[float], window: int = None):
    """Agregim i sinjaleve"""
    algebra = get_signal_algebra()
    return algebra.aggregate(signals, window)


# ==================== SIGNAL INTEGRATOR ====================

@router.get("/signals/status")
async def get_integrator_status():
    """Statusi i Universal Signal Integrator"""
    return get_signal_integrator().get_status()

@router.post("/signals/emit")
async def emit_signal(request: SignalRequest):
    """Emëto një sinjal nga një burim"""
    integrator = get_signal_integrator()
    
    success = integrator.emit_signal(
        source_id=request.source_id,
        signal_type=request.signal_type,
        payload=request.payload
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Source not found")
    
    return {"status": "emitted", "source": request.source_id}

@router.get("/signals/sources")
async def get_sources(region: str = None, category: str = None, api_only: bool = False):
    """Merr burimet e sinjaleve"""
    integrator = get_signal_integrator()
    
    if region:
        sources = integrator.get_sources_by_region(region)
    elif category:
        sources = integrator.get_sources_by_category(category)
    elif api_only:
        sources = integrator.get_api_sources()
    else:
        sources = integrator.get_active_sources()
    
    return {
        "count": len(sources),
        "sources": [
            {
                "id": s.id,
                "name": s.name,
                "category": s.category,
                "region": s.region,
                "url": s.url,
                "api_available": s.api_available
            }
            for s in sources[:100]  # Limit to 100
        ]
    }

@router.post("/signals/poll")
async def poll_sources():
    """Poll të gjitha burimet për sinjale të reja"""
    integrator = get_signal_integrator()
    return await integrator.poll_all_sources()


# ==================== FULL SYSTEM STATUS ====================

@router.get("/system")
async def get_full_system_status():
    """Statusi i plotë i sistemit Curiosity Ocean"""
    return {
        "service": "Curiosity Ocean Algebra System",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "event_bus": get_event_bus().get_stats(),
            "cell_registry": get_cell_registry().get_stats(),
            "curiosity": get_curiosity_orchestrator().get_status(),
            "signal_integrator": get_signal_integrator().get_status()
        }
    }


# ==================== MEGA SIGNAL COLLECTOR ====================

@router.post("/mega/collect")
async def mega_collect_all_signals():
    """
    Mblidh TË GJITHA sinjalet - Git, Files, Packages, API, Docker, Algebra, Punctuation
    
    Kjo skanon të gjithë workspace-in dhe mbledh:
    - Git: commits, branches, tags, diffs
    - Files: çdo file, funksion, klasë, import, variabël
    - Packages: Python dhe Node.js dependencies
    - API: të gjitha endpoints
    - Docker: containers, images, ports
    - Algebra: operacione matematikore
    - Punctuation: çdo pikë, presje, simbole
    """
    from .mega_signal_collector import get_mega_collector
    import os
    
    workspace = os.environ.get("WORKSPACE_PATH", "/app")
    collector = get_mega_collector(workspace)
    report = await collector.collect_all()
    
    return {
        "status": "collected",
        "timestamp": datetime.now().isoformat(),
        **report
    }

@router.get("/mega/status")
async def get_mega_collector_status():
    """Statusi i Mega Signal Collector"""
    from .mega_signal_collector import get_mega_collector
    
    collector = get_mega_collector()
    return {
        "service": "MegaSignalCollector",
        "total_signals": collector.stats["total_signals"],
        "stats": collector.stats,
        "punctuation_stats": collector.punctuation_stats,
        "algebra_expressions": len(collector.algebra_expressions)
    }

@router.get("/mega/signals")
async def get_mega_signals(
    signal_type: Optional[str] = None,
    source: Optional[str] = None,
    path_pattern: Optional[str] = None,
    limit: int = 100
):
    """Merr sinjalet nga Mega Collector me filtra"""
    from .mega_signal_collector import get_mega_collector, SignalType
    
    collector = get_mega_collector()
    
    # Convert string to SignalType if provided
    st = None
    if signal_type:
        try:
            st = SignalType(signal_type)
        except ValueError:
            pass
    
    signals = collector.query_signals(
        signal_type=st,
        source=source,
        path_pattern=path_pattern
    )
    
    return {
        "count": len(signals),
        "signals": [
            {
                "id": s.id,
                "type": s.type.value,
                "source": s.source,
                "value": str(s.value)[:200],
                "path": s.path,
                "line": s.line,
                "timestamp": s.timestamp.isoformat()
            }
            for s in signals[:limit]
        ]
    }

@router.get("/mega/graph")
async def get_mega_signal_graph():
    """Eksporto grafin e sinjaleve - nodes dhe edges"""
    from .mega_signal_collector import get_mega_collector
    
    collector = get_mega_collector()
    return collector.export_graph()

@router.get("/mega/algebra")
async def get_mega_algebra_expressions():
    """Merr të gjitha shprehjet algjebrike të gjetura"""
    from .mega_signal_collector import get_mega_collector
    
    collector = get_mega_collector()
    return {
        "count": len(collector.algebra_expressions),
        "expressions": [
            {
                "expression": e.expression[:100],
                "variables": e.variables,
                "operators": e.operators,
                "file": e.source_file,
                "line": e.line_number
            }
            for e in collector.algebra_expressions[:100]
        ]
    }

@router.get("/mega/punctuation")
async def get_mega_punctuation_stats():
    """Merr statistikat e pikësimit - çdo presje, çdo pikë"""
    from .mega_signal_collector import get_mega_collector
    
    collector = get_mega_collector()
    total = sum(collector.punctuation_stats.values())
    
    return {
        "total_punctuation": total,
        "stats": collector.punctuation_stats,
        "percentages": {
            k: round(v / total * 100, 2) if total > 0 else 0
            for k, v in collector.punctuation_stats.items()
        }
    }

@router.get("/mega/files")
async def get_mega_file_stats():
    """Merr statistikat e files"""
    from .mega_signal_collector import get_mega_collector
    
    collector = get_mega_collector()
    return {
        "files_scanned": collector.stats["files_scanned"],
        "lines_scanned": collector.stats["lines_scanned"],
        "functions_found": collector.stats["functions_found"],
        "classes_found": collector.stats["classes_found"],
        "imports_found": collector.stats["imports_found"],
        "variables_found": collector.stats["variables_found"],
        "top_files": collector._get_top_files()
    }

@router.get("/mega/git")
async def get_mega_git_stats():
    """Merr statistikat e Git"""
    from .mega_signal_collector import get_mega_collector
    
    collector = get_mega_collector()
    return {
        "commits_found": collector.stats["commits_found"],
        "branches_found": collector.stats["branches_found"],
        "git_signals": collector.stats["git_signals"]
    }

@router.get("/mega/docker")
async def get_mega_docker_stats():
    """Merr statistikat e Docker"""
    from .mega_signal_collector import get_mega_collector
    
    collector = get_mega_collector()
    return {
        "containers_found": collector.stats["containers_found"],
        "docker_signals": collector.stats["docker_signals"]
    }

@router.get("/mega/api")
async def get_mega_api_stats():
    """Merr statistikat e API endpoints"""
    from .mega_signal_collector import get_mega_collector
    
    collector = get_mega_collector()
    return {
        "endpoints_found": collector.stats["endpoints_found"],
        "api_signals": collector.stats["api_signals"]
    }


# ==================== BINARY PROTOCOLS ====================

@router.get("/binary/status")
async def get_binary_status():
    """Status i binary protocol service"""
    from .binary_protocols import get_binary_service
    return get_binary_service().get_status()


@router.post("/binary/encode")
async def encode_to_binary(data: Dict[str, Any], format: str = "cbor2"):
    """Encode data to binary format - CBOR2/MSGPACK ONLY"""
    from .binary_protocols import get_binary_service, BinaryFormat
    import base64
    
    service = get_binary_service()
    
    # BINARY ONLY - no JSON fallback
    format_map = {
        "cbor": BinaryFormat.CBOR2,
        "cbor2": BinaryFormat.CBOR2,
        "msgpack": BinaryFormat.MSGPACK,
        "custom": BinaryFormat.CUSTOM_BINARY,
        "compressed": BinaryFormat.COMPRESSED_CBOR,
        "compressed_cbor": BinaryFormat.COMPRESSED_CBOR
    }
    
    binary_format = format_map.get(format.lower(), BinaryFormat.CUSTOM_BINARY)
    encoded = service.encode_response(data, binary_format)
    
    return {
        "format": binary_format.name,
        "size_bytes": len(encoded),
        "original_size": len(str(data)),
        "compression_ratio": len(str(data)) / len(encoded) if len(encoded) > 0 else 0,
        "data_base64": base64.b64encode(encoded).decode('ascii'),
        "data_hex": encoded.hex()[:200] + "..." if len(encoded) > 100 else encoded.hex()
    }


@router.post("/binary/decode")
async def decode_from_binary(data_base64: str, format: str = "cbor2"):
    """Decode data from binary format - CBOR2/MSGPACK ONLY"""
    from .binary_protocols import get_binary_service, BinaryFormat
    import base64
    
    service = get_binary_service()
    
    # BINARY ONLY - no JSON fallback
    format_map = {
        "cbor": BinaryFormat.CBOR2,
        "cbor2": BinaryFormat.CBOR2,
        "msgpack": BinaryFormat.MSGPACK,
        "custom": BinaryFormat.CUSTOM_BINARY,
        "compressed": BinaryFormat.COMPRESSED_CBOR,
        "compressed_cbor": BinaryFormat.COMPRESSED_CBOR
    }
    
    binary_format = format_map.get(format.lower(), BinaryFormat.CUSTOM_BINARY)
    
    try:
        binary_data = base64.b64decode(data_base64)
        decoded = service.decode_request(binary_data, binary_format)
        return {
            "success": True,
            "format": binary_format.name,
            "decoded_data": decoded
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# ==================== SMART CALCULATOR ====================

class CalculateRequest(BaseModel):
    expression: str
    format: str = "json"

@router.post("/calculate")
async def calculate_expression(request: CalculateRequest):
    """Llogarit shprehje matematikore - kupton shqip dhe anglisht"""
    from .binary_protocols import get_binary_service, BinaryFormat
    import base64
    
    service = get_binary_service()
    result = service.calculate(request.expression)
    
    if request.format.lower() in ["binary", "cbor", "msgpack", "custom"]:
        format_map = {
            "binary": BinaryFormat.CUSTOM_BINARY,
            "cbor": BinaryFormat.CBOR2,
            "msgpack": BinaryFormat.MSGPACK,
            "custom": BinaryFormat.CUSTOM_BINARY
        }
        binary_format = format_map.get(request.format.lower(), BinaryFormat.CUSTOM_BINARY)
        encoded = service.encode_response(result, binary_format)
        result["binary_response"] = base64.b64encode(encoded).decode('ascii')
        result["binary_size"] = len(encoded)
    
    return result


@router.get("/calculate")
async def calculate_expression_get(expression: str, format: str = "json"):
    """Llogarit shprehje - GET version"""
    from .binary_protocols import get_binary_service
    
    service = get_binary_service()
    return service.calculate(expression)


@router.get("/calculator/history")
async def get_calculator_history():
    """Merr historikun e llogaritjeve"""
    from .binary_protocols import get_binary_service
    
    service = get_binary_service()
    return {
        "count": len(service.calculator.history),
        "history": service.calculator.history[-50:],  # Last 50
        "variables": service.calculator.variables
    }


@router.post("/calculator/variable")
async def set_calculator_variable(name: str, value: float):
    """Vendos një variabël"""
    from .binary_protocols import get_binary_service
    
    service = get_binary_service()
    service.calculator.set_variable(name, value)
    return {
        "success": True,
        "variable": name,
        "value": value,
        "all_variables": service.calculator.variables
    }


# ==================== SMART CHAT WITH CALCULATION ====================

class SmartChatRequest(BaseModel):
    query: str
    format: str = "json"
    include_binary: bool = False

@router.post("/smart-chat")
async def smart_chat(request: SmartChatRequest):
    """Smart chat që kupton llogaritje dhe pyetje"""
    from .binary_protocols import get_binary_service, BinaryFormat
    import base64
    import re
    
    service = get_binary_service()
    query = request.query.strip()
    
    # Try to detect if it's a calculation
    math_patterns = [
        r'\d+\s*[\+\-\*\/\^%]\s*\d+',  # Simple math
        r'sa\s+b[eë]jn[eë]',  # Albanian "sa bëjnë"
        r'what\s+is',  # English
        r'calculate',  # Calculate
        r'llogarit',  # Albanian calculate
        r'compute'  # Compute
    ]
    
    is_math = any(re.search(pattern, query.lower()) for pattern in math_patterns)
    
    if is_math:
        # It's a math question
        calc_result = service.calculate(query)
        
        if calc_result.get("success"):
            response = {
                "type": "calculation",
                "query": query,
                "answer": calc_result["formatted"],
                "result": calc_result["result"],
                "expression": calc_result["expression"],
                "operator": calc_result.get("operator"),
                "operands": calc_result.get("operands"),
                "confidence": 1.0,
                "language": "sq" if re.search(r'sa\s+b[eë]jn[eë]|llogarit', query.lower()) else "en"
            }
            
            if request.include_binary:
                encoded = service.encode_response(response, BinaryFormat.CUSTOM_BINARY)
                response["binary_base64"] = base64.b64encode(encoded).decode('ascii')
                response["binary_size"] = len(encoded)
            
            return response
        else:
            return {
                "type": "calculation_error",
                "query": query,
                "error": calc_result.get("error"),
                "hint": calc_result.get("hint")
            }
    
    # Not a math question - general response
    return {
        "type": "general",
        "query": query,
        "answer": f"I understood your question: '{query}'. For calculations, try '5+3' or 'sa bëjnë 10*5'",
        "confidence": 0.7,
        "suggestions": [
            "Try a calculation: 5 + 3",
            "Provo: sa bëjnë 10 * 5",
            "Calculate: 100 / 4",
            "Llogarit: 25 ^ 2"
        ]
    }


# ==================== BUFFER & STREAMING ====================

@router.get("/buffer/stats")
async def get_buffer_stats():
    """Merr statistikat e buffer-it"""
    from .binary_protocols import get_binary_service
    
    service = get_binary_service()
    return {
        "main_buffer": service.buffer.get_stats(),
        "signal_buffer": service.signal_buffer.get_stats()
    }


@router.post("/buffer/write")
async def write_to_buffer(data: Dict[str, Any]):
    """Shkruaj në buffer"""
    from .binary_protocols import get_binary_service, SignalPacket, DataType
    import time
    
    service = get_binary_service()
    
    packet = SignalPacket(
        signal_id=int(time.time() * 1000) % 1000000,
        signal_type=1,
        source_hash=hash(str(data)) & 0xFFFFFFFF,
        value_type=DataType.MAP,
        value=data,
        timestamp=time.time()
    )
    
    bytes_written = service.signal_buffer.write_packet(packet)
    
    return {
        "success": True,
        "bytes_written": bytes_written,
        "buffer_stats": service.signal_buffer.get_stats()
    }


@router.get("/buffer/read")
async def read_from_buffer():
    """Lexo nga buffer"""
    from .binary_protocols import get_binary_service
    import base64
    
    service = get_binary_service()
    packet_data = service.signal_buffer.read_packet()
    
    if packet_data:
        return {
            "success": True,
            "packet_base64": base64.b64encode(packet_data).decode('ascii'),
            "packet_size": len(packet_data),
            "buffer_stats": service.signal_buffer.get_stats()
        }
    else:
        return {
            "success": False,
            "message": "No packets available",
            "buffer_stats": service.signal_buffer.get_stats()
        }


# ==================== I18N ENGINE ====================

@router.get("/i18n/status")
async def get_i18n_status():
    """Status i i18n engine"""
    from .i18n_engine import get_i18n_engine
    
    engine = get_i18n_engine()
    return {
        "status": "operational",
        "stats": engine.get_stats(),
        "supported_languages": engine.get_supported_languages()
    }


@router.get("/i18n/translate")
async def translate_key(key: str, lang: str = "en"):
    """Përkthe një çelës"""
    from .i18n_engine import get_i18n_engine
    
    engine = get_i18n_engine()
    translation = engine.t(key, lang)
    
    return {
        "key": key,
        "language": lang,
        "translation": translation,
        "found": translation != key
    }


@router.get("/i18n/detect")
async def detect_language(text: str):
    """Detekto gjuhën e tekstit"""
    from .i18n_engine import get_i18n_engine
    
    engine = get_i18n_engine()
    lang, confidence = engine.detector.detect_with_confidence(text)
    
    return {
        "text": text,
        "detected_language": lang,
        "confidence": confidence,
        "language_name": next(
            (l["name"] for l in engine.get_supported_languages() if l["code"] == lang),
            lang
        )
    }


@router.get("/i18n/languages")
async def get_supported_languages():
    """Merr gjuhët e mbështetura"""
    from .i18n_engine import get_i18n_engine
    return get_i18n_engine().get_supported_languages()


@router.post("/i18n/add")
async def add_translation(key: str, lang: str, value: str):
    """Shto përkthim të ri"""
    from .i18n_engine import get_i18n_engine
    
    engine = get_i18n_engine()
    engine.add_translation(key, lang, value)
    
    return {
        "success": True,
        "key": key,
        "language": lang,
        "value": value
    }


# ==================== REAL CHAT - NO FAKE! ====================

class RealChatRequest(BaseModel):
    query: str
    include_data: bool = True

@router.post("/real-chat")
async def real_chat(request: RealChatRequest):
    """Chat REAL - asnjë fake, vetëm funksione reale!"""
    from .real_chat_engine import get_real_chat_engine
    
    engine = get_real_chat_engine()
    response = engine.chat(request.query)
    
    result = response.to_dict()
    
    if not request.include_data:
        result.pop("data", None)
    
    return result


@router.get("/real-chat")
async def real_chat_get(query: str):
    """Chat REAL - GET version"""
    from .real_chat_engine import get_real_chat_engine
    
    engine = get_real_chat_engine()
    response = engine.chat(query)
    return response.to_dict()


@router.get("/real-chat/history")
async def get_real_chat_history(limit: int = 50):
    """Merr historinë e chat-it"""
    from .real_chat_engine import get_real_chat_engine
    
    engine = get_real_chat_engine()
    return {
        "count": len(engine.history),
        "history": engine.get_history(limit)
    }


@router.get("/real-chat/stats")
async def get_real_chat_stats():
    """Statistikat e chat-it real"""
    from .real_chat_engine import get_real_chat_engine
    return get_real_chat_engine().get_stats()


# ==================== AUTOLEARNING ENGINE ====================

class LearnRequest(BaseModel):
    query: str
    response: str
    sources: List[str] = []
    confidence: float = 0.8

class FeedbackRequest(BaseModel):
    knowledge_id: str
    helpful: bool

@router.get("/learn/status")
async def get_learning_status():
    """Status i autolearning engine"""
    import sys
    sys.path.insert(0, '/app')
    from autolearning_engine import get_autolearning_engine
    
    engine = get_autolearning_engine()
    return {
        "status": "operational",
        "stats": engine.get_learning_stats()
    }


@router.post("/learn/query")
async def process_learning_query(query: str):
    """Proceso pyetje me autolearning"""
    import sys
    sys.path.insert(0, '/app')
    from autolearning_engine import get_autolearning_engine
    
    engine = get_autolearning_engine()
    result = engine.process_query(query)
    
    # Add suggested response
    suggested = engine.suggest_response(query)
    result["suggested_response"] = suggested
    
    return result


@router.post("/learn/teach")
async def teach_knowledge(request: LearnRequest):
    """Mëso dije të re"""
    import sys
    sys.path.insert(0, '/app')
    from autolearning_engine import get_autolearning_engine
    
    engine = get_autolearning_engine()
    knowledge_id = engine.learn_from_response(
        query=request.query,
        response=request.response,
        sources=request.sources,
        confidence=request.confidence
    )
    
    return {
        "success": True,
        "knowledge_id": knowledge_id,
        "query": request.query,
        "response": request.response,
        "confidence": request.confidence
    }


@router.post("/learn/feedback")
async def record_feedback(request: FeedbackRequest):
    """Regjistro feedback për dije"""
    import sys
    sys.path.insert(0, '/app')
    from autolearning_engine import get_autolearning_engine
    
    engine = get_autolearning_engine()
    engine.record_feedback(request.knowledge_id, request.helpful)
    
    return {
        "success": True,
        "knowledge_id": request.knowledge_id,
        "helpful": request.helpful
    }


@router.get("/learn/suggest")
async def suggest_response(query: str):
    """Sugjero përgjigje nga dijet e mësuara"""
    import sys
    sys.path.insert(0, '/app')
    from autolearning_engine import get_autolearning_engine
    
    engine = get_autolearning_engine()
    suggested = engine.suggest_response(query)
    
    return {
        "query": query,
        "suggested_response": suggested,
        "found": suggested is not None
    }


@router.get("/learn/knowledge")
async def get_knowledge_base():
    """Merr të gjithë dijet e mësuara"""
    import sys
    sys.path.insert(0, '/app')
    from autolearning_engine import get_autolearning_engine
    
    engine = get_autolearning_engine()
    kb = engine.knowledge_accumulator.knowledge_base
    
    return {
        "total": len(kb),
        "knowledge": [
            {
                "id": k.knowledge_id,
                "query": k.query,
                "response": k.response[:100] + "..." if len(k.response) > 100 else k.response,
                "confidence": k.confidence,
                "times_used": k.times_used,
                "helpfulness": k.helpfulness_score
            }
            for k in kb.values()
        ]
    }


@router.get("/learn/patterns")
async def get_patterns():
    """Merr patterns e mësuara"""
    import sys
    sys.path.insert(0, '/app')
    from autolearning_engine import get_autolearning_engine
    
    engine = get_autolearning_engine()
    
    base_patterns = list(engine.pattern_detector.BASE_PATTERNS.keys())
    custom_patterns = [
        {
            "id": p.pattern_id,
            "type": p.pattern_type,
            "keywords": p.keywords,
            "times_matched": p.times_matched
        }
        for p in engine.pattern_detector.custom_patterns.values()
    ]
    
    return {
        "base_patterns": base_patterns,
        "base_count": len(base_patterns),
        "custom_patterns": custom_patterns,
        "custom_count": len(custom_patterns)
    }


# ==================== REAL BINARY ENDPOINTS - NO JSON! ====================

@router.get("/bin/chat")
async def binary_chat(query: str, format: str = "clsn"):
    """
    🔥 REAL BINARY CHAT - Jo JSON!
    Kthen përgjigje në format binar (CBOR, MessagePack, ose CLSN)
    """
    from .real_chat_engine import get_real_chat_engine
    
    engine = get_real_chat_engine()
    response = engine.chat(query)
    data = response.to_dict()
    
    return create_binary_response(data, format)


@router.get("/bin/calculate")
async def binary_calculate(expression: str, format: str = "clsn"):
    """
    🔥 REAL BINARY CALCULATION - Jo JSON!
    """
    service = get_binary_service()
    result = service.calculate(expression)
    
    return create_binary_response(result, format)


@router.get("/bin/time")
async def binary_time(format: str = "clsn"):
    """
    🔥 REAL BINARY TIME - Jo JSON!
    """
    from datetime import datetime
    now = datetime.now()
    
    data = {
        "hour": now.hour,
        "minute": now.minute,
        "second": now.second,
        "microsecond": now.microsecond,
        "timestamp": now.timestamp(),
        "iso": now.isoformat(),
        "date": {
            "year": now.year,
            "month": now.month,
            "day": now.day,
            "weekday": now.weekday()
        }
    }
    
    return create_binary_response(data, format)


@router.get("/bin/status")
async def binary_status(format: str = "clsn"):
    """
    🔥 REAL BINARY STATUS - Jo JSON!
    """
    from .real_chat_engine import get_real_chat_engine
    from .mega_signal_collector import get_mega_collector
    
    data = {
        "status": "operational",
        "version": "2.2.0",
        "binary_formats": ["cbor", "msgpack", "clsn"],
        "chat_stats": get_real_chat_engine().get_stats(),
        "signals": get_mega_collector().stats.get("total_signals", 0),
        "timestamp": datetime.now().timestamp()
    }
    
    return create_binary_response(data, format)


@router.get("/bin/signals")
async def binary_signals(limit: int = 100, format: str = "clsn"):
    """
    🔥 REAL BINARY SIGNALS - Jo JSON!
    """
    from .mega_signal_collector import get_mega_collector
    
    collector = get_mega_collector()
    signals = []
    
    for signal in list(collector.signals.values())[:limit]:
        signals.append({
            "id": signal.id,
            "type": signal.type.value,
            "source": signal.source,
            "value": str(signal.value)[:100],
            "path": signal.path or "",
            "line": signal.line or 0
        })
    
    data = {
        "total": len(collector.signals),
        "returned": len(signals),
        "signals": signals
    }
    
    return create_binary_response(data, format)


@router.post("/bin/stream")
async def binary_stream_write(request: Request, format: str = "clsn"):
    """
    🔥 REAL BINARY STREAM WRITE
    Shkruaj direkt në buffer
    """
    body = await request.body()
    service = get_binary_service()
    
    # Write raw bytes to buffer
    bytes_written = service.buffer.write(body)
    
    data = {
        "success": True,
        "bytes_written": bytes_written,
        "buffer_position": service.buffer.write_position,
        "buffer_available": service.buffer.available()
    }
    
    return create_binary_response(data, format)


@router.get("/bin/stream")
async def binary_stream_read(size: int = 1024, format: str = "clsn"):
    """
    🔥 REAL BINARY STREAM READ
    Lexo direkt nga buffer
    """
    service = get_binary_service()
    
    # Read raw bytes
    data_bytes = service.buffer.read(min(size, service.buffer.available()))
    
    # Return raw binary
    if format == "raw":
        return Response(
            content=data_bytes,
            media_type="application/octet-stream",
            headers={
                "X-Bytes-Read": str(len(data_bytes)),
                "X-Buffer-Remaining": str(service.buffer.available())
            }
        )
    
    data = {
        "bytes_read": len(data_bytes),
        "data_hex": data_bytes.hex() if data_bytes else "",
        "buffer_remaining": service.buffer.available()
    }
    
    return create_binary_response(data, format)


@router.get("/bin/learn")
async def binary_learn_status(format: str = "clsn"):
    """
    🔥 REAL BINARY LEARNING STATUS
    """
    import sys
    sys.path.insert(0, '/app')
    from autolearning_engine import get_autolearning_engine
    
    engine = get_autolearning_engine()
    data = {
        "status": "operational",
        "stats": engine.get_learning_stats()
    }
    
    return create_binary_response(data, format)


@router.get("/bin/i18n")
async def binary_i18n(key: str, lang: str = "en", format: str = "clsn"):
    """
    🔥 REAL BINARY I18N
    """
    from .i18n_engine import get_i18n_engine
    
    engine = get_i18n_engine()
    translation = engine.t(key, lang)
    
    data = {
        "key": key,
        "language": lang,
        "translation": translation,
        "found": translation != key
    }
    
    return create_binary_response(data, format)


@router.get("/bin/raw")
async def get_raw_binary(data_type: str = "timestamp"):
    """
    🔥 ABSOLUTE RAW BINARY - Asnjë wrapper!
    Returns: Pure bytes
    """
    import struct
    import time
    
    if data_type == "timestamp":
        # 8 bytes: double timestamp
        raw = struct.pack('>d', time.time())
    elif data_type == "counter":
        # 4 bytes: counter
        service = get_binary_service()
        raw = struct.pack('>I', service.stats.get("encoded_count", 0))
    elif data_type == "magic":
        # 4 bytes: CLSN magic
        raw = b'CLSN'
    elif data_type == "status":
        # 1 byte: status code (1 = ok)
        raw = struct.pack('B', 1)
    else:
        # 16 bytes: header
        raw = struct.pack('>4sIQ', b'CLSN', 1, int(time.time() * 1000000))
    
    return Response(
        content=raw,
        media_type="application/octet-stream",
        headers={
            "X-Data-Type": data_type,
            "X-Bytes": str(len(raw)),
            "X-Format": "raw-binary"
        }
    )


@router.post("/bin/decode")
async def decode_binary(request: Request):
    """
    🔥 DECODE BINARY TO JSON
    Merr binary, kthen JSON (për debugging)
    """
    body = await request.body()
    content_type = request.headers.get("Content-Type", "application/octet-stream")
    
    format_map = {
        "application/cbor": BinaryFormat.CBOR2,
        "application/msgpack": BinaryFormat.MSGPACK,
        "application/octet-stream": BinaryFormat.CUSTOM_BINARY,
        "application/x-kloud": BinaryFormat.CUSTOM_BINARY,
    }
    
    binary_format = format_map.get(content_type, BinaryFormat.CUSTOM_BINARY)
    encoder = BinaryEncoder(binary_format)
    
    try:
        decoded = encoder.decode(body, binary_format)
        return {
            "success": True,
            "format": binary_format.name,
            "bytes_decoded": len(body),
            "decoded_data": decoded
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "bytes_received": len(body),
            "hex_preview": body[:50].hex() if body else ""
        }


# ==================== BINARY ALGEBRA ENDPOINTS ====================

@router.get("/algebra/op")
async def binary_operation(a: int, op: str, b: int = 0, bits: int = 64):
    """
    🔢 ALGJEBËR BINARE - Operacion
    
    Operacionet: and, or, xor, not, nand, nor, xnor, shl, shr, rol, ror, add, sub, mul, div, mod
    
    Returns: RAW BINARY BYTES
    """
    algebra = get_binary_algebra()
    result_bytes = algebra.operate_raw(a, op, b, bits)
    
    return Response(
        content=result_bytes,
        media_type="application/octet-stream",
        headers={
            "X-Operation": op,
            "X-Operand-A": str(a),
            "X-Operand-B": str(b),
            "X-Bits": str(bits),
            "X-Result-Decimal": str(int.from_bytes(result_bytes, 'big')),
            "X-Result-Binary": format(int.from_bytes(result_bytes, 'big'), f'0{bits}b'),
            "X-Result-Hex": result_bytes.hex()
        }
    )


@router.get("/algebra/op/json")
async def binary_operation_json(a: int, op: str, b: int = 0, bits: int = 64):
    """
    🔢 ALGJEBËR BINARE - Operacion (JSON për debug)
    """
    algebra = get_binary_algebra()
    
    op_map = {
        "and": BinaryOp.AND, "&": BinaryOp.AND,
        "or": BinaryOp.OR, "|": BinaryOp.OR,
        "xor": BinaryOp.XOR, "^": BinaryOp.XOR,
        "not": BinaryOp.NOT, "~": BinaryOp.NOT,
        "nand": BinaryOp.NAND, "nor": BinaryOp.NOR, "xnor": BinaryOp.XNOR,
        "shl": BinaryOp.SHL, "<<": BinaryOp.SHL,
        "shr": BinaryOp.SHR, ">>": BinaryOp.SHR,
        "rol": BinaryOp.ROL, "ror": BinaryOp.ROR,
        "add": BinaryOp.ADD, "+": BinaryOp.ADD,
        "sub": BinaryOp.SUB, "-": BinaryOp.SUB,
        "mul": BinaryOp.MUL, "*": BinaryOp.MUL,
        "div": BinaryOp.DIV, "/": BinaryOp.DIV,
        "mod": BinaryOp.MOD, "%": BinaryOp.MOD,
    }
    
    binary_op = op_map.get(op.lower(), BinaryOp.AND)
    result = algebra.operate(a, binary_op, b, bits)
    
    return {
        "operation": op,
        "a": {"value": a, "binary": format(a & ((1 << bits) - 1), f'0{bits}b')},
        "b": {"value": b, "binary": format(b & ((1 << bits) - 1), f'0{bits}b')},
        "result": result.to_dict(),
        "stats": algebra.get_stats()
    }


@router.get("/algebra/signal")
async def create_binary_signal(pattern: str = "10101010", sample_rate: int = 1000, name: str = "sig"):
    """
    🔊 SINJAL BINAR
    
    Pattern: string i 0 dhe 1 (p.sh. "10101010" për clock)
    
    Returns: BYTES (8 bits = 1 byte)
    """
    samples = [int(c) for c in pattern if c in '01']
    signal = BinarySignal(samples, sample_rate, name)
    
    # Kthen bytes
    raw = signal.to_bytes()
    
    return Response(
        content=raw,
        media_type="application/octet-stream",
        headers={
            "X-Signal-Name": name,
            "X-Signal-Length": str(len(samples)),
            "X-Sample-Rate": str(sample_rate),
            "X-Energy": str(signal.energy),
            "X-Duty-Cycle": f"{signal.duty_cycle:.4f}",
            "X-Pattern": pattern[:32]
        }
    )


@router.post("/algebra/signal/op")
async def signal_operation(request: Request, op: str = "and"):
    """
    🔊 OPERACION MIDIS DY SINJALEVE
    
    Body: dy patterns të ndara me newline
    """
    body = await request.body()
    lines = body.decode('utf-8').strip().split('\n')
    
    if len(lines) < 2:
        raise HTTPException(400, "Nevojiten 2 patterns")
    
    s1 = BinarySignal([int(c) for c in lines[0] if c in '01'], 1000, "s1")
    s2 = BinarySignal([int(c) for c in lines[1] if c in '01'], 1000, "s2")
    
    if op.lower() in ["and", "&"]:
        result = s1 & s2
    elif op.lower() in ["or", "|"]:
        result = s1 | s2
    elif op.lower() in ["xor", "^"]:
        result = s1 ^ s2
    else:
        result = s1 & s2
    
    raw = result.to_bytes()
    
    return Response(
        content=raw,
        media_type="application/octet-stream",
        headers={
            "X-Operation": op,
            "X-Result-Name": result.name,
            "X-Result-Length": str(len(result)),
            "X-Result-Binary": ''.join(str(s) for s in result.samples[:64])
        }
    )


@router.get("/algebra/signal/clock")
async def generate_clock(length: int = 64, period: int = 2):
    """
    ⏰ GJENERO CLOCK SIGNAL
    """
    signal = BinarySignal.clock(length, period)
    raw = signal.to_bytes()
    
    return Response(
        content=raw,
        media_type="application/octet-stream",
        headers={
            "X-Signal-Type": "clock",
            "X-Length": str(length),
            "X-Period": str(period),
            "X-Frequency-Hz": f"{signal.frequency():.2f}",
            "X-Pattern": ''.join(str(s) for s in signal.samples[:32])
        }
    )


@router.get("/algebra/signal/pulse")
async def generate_pulse(length: int = 64, start: int = 16, width: int = 8):
    """
    ⚡ GJENERO PULSE SIGNAL
    """
    signal = BinarySignal.pulse(length, start, width)
    raw = signal.to_bytes()
    
    return Response(
        content=raw,
        media_type="application/octet-stream",
        headers={
            "X-Signal-Type": "pulse",
            "X-Length": str(length),
            "X-Start": str(start),
            "X-Width": str(width),
            "X-Pattern": ''.join(str(s) for s in signal.samples[:32])
        }
    )


@router.get("/algebra/signal/correlate")
async def correlate_signals(pattern1: str = "10101010", pattern2: str = "1010"):
    """
    📊 KORELACION MIDIS SINJALEVE
    """
    s1 = BinarySignal([int(c) for c in pattern1 if c in '01'], 1000, "s1")
    s2 = BinarySignal([int(c) for c in pattern2 if c in '01'], 1000, "s2")
    
    correlation = s1.correlate(s2)
    max_corr = max(correlation) if correlation else 0
    max_idx = correlation.index(max_corr) if correlation else 0
    
    # Pack correlations as int16
    raw = struct.pack(f'>{len(correlation)}h', *correlation)
    
    return Response(
        content=raw,
        media_type="application/octet-stream",
        headers={
            "X-Signal-1-Length": str(len(s1)),
            "X-Signal-2-Length": str(len(s2)),
            "X-Correlation-Length": str(len(correlation)),
            "X-Max-Correlation": str(max_corr),
            "X-Max-Lag": str(max_idx - len(s2) + 1),
            "X-Values": ','.join(str(c) for c in correlation[:20])
        }
    )


@router.get("/algebra/matrix")
async def create_binary_matrix(rows: int = 4, cols: int = 4, pattern: str = "identity"):
    """
    📐 MATRICË BINARE
    
    pattern: "identity", "ones", "zeros", "random", ose CSV (p.sh. "1,0,1,0;0,1,0,1")
    """
    if pattern == "identity":
        matrix = BinaryMatrix.identity(max(rows, cols))
    elif pattern == "ones":
        matrix = BinaryMatrix(rows, cols, [[1]*cols for _ in range(rows)])
    elif pattern == "zeros":
        matrix = BinaryMatrix(rows, cols)
    elif pattern == "random":
        import random
        data = [[random.randint(0, 1) for _ in range(cols)] for _ in range(rows)]
        matrix = BinaryMatrix(rows, cols, data)
    else:
        # Parse CSV: "1,0,1;0,1,0"
        try:
            row_strs = pattern.split(';')
            data = [[int(c) for c in row.split(',')] for row in row_strs]
            matrix = BinaryMatrix(len(data), len(data[0]) if data else 0, data)
        except:
            matrix = BinaryMatrix.identity(rows)
    
    raw = matrix.to_bytes()
    
    return Response(
        content=raw,
        media_type="application/octet-stream",
        headers={
            "X-Matrix-Rows": str(matrix.rows),
            "X-Matrix-Cols": str(matrix.cols),
            "X-Matrix-Rank": str(matrix.rank_gf2()),
            "X-Matrix-Ones": str(sum(sum(row) for row in matrix.data)),
            "X-Density": f"{matrix.to_dict()['density']:.4f}"
        }
    )


@router.post("/algebra/matrix/multiply")
async def multiply_matrices_gf2(request: Request):
    """
    📐 SHUMËZIM MATRICASH NË GF(2)
    
    Body: dy matrica binare (bytes)
    """
    body = await request.body()
    
    # Assume both matrices back-to-back
    # First 4 bytes = rows1, cols1
    m1 = BinaryMatrix.from_bytes(body)
    
    # Find where m2 starts
    m1_bytes = m1.to_bytes()
    m2_start = len(m1_bytes)
    
    if m2_start < len(body):
        m2 = BinaryMatrix.from_bytes(body[m2_start:])
    else:
        m2 = m1  # Square with self
    
    try:
        result = m1.multiply_gf2(m2)
        raw = result.to_bytes()
        
        return Response(
            content=raw,
            media_type="application/octet-stream",
            headers={
                "X-Result-Rows": str(result.rows),
                "X-Result-Cols": str(result.cols),
                "X-Result-Rank": str(result.rank_gf2())
            }
        )
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("/algebra/packet")
async def create_algebra_packet(expression: str = "5 xor 3", result_bits: int = 32):
    """
    📦 PAKETO REZULTATIN NË FORMAT BINAR BALG
    """
    algebra = get_binary_algebra()
    
    # Parse expression
    parts = expression.lower().split()
    if len(parts) >= 3:
        a = int(parts[0])
        op = parts[1]
        b = int(parts[2])
    elif len(parts) >= 2:
        a = int(parts[1])
        op = parts[0]
        b = 0
    else:
        a, op, b = 5, "xor", 3
    
    result_bytes = algebra.operate_raw(a, op, b, result_bits)
    result_value = int.from_bytes(result_bytes, 'big')
    
    packet = algebra.create_packet({
        "expression": expression,
        "operand_a": a,
        "operand_b": b,
        "operation": op,
        "result": result_value,
        "result_binary": format(result_value, f'0{result_bits}b'),
        "bits": result_bits
    })
    
    return Response(
        content=packet,
        media_type="application/x-balg",
        headers={
            "X-Magic": "BALG",
            "X-Expression": expression,
            "X-Result": str(result_value),
            "X-Result-Binary": format(result_value, f'0{result_bits}b'),
            "X-Packet-Size": str(len(packet))
        }
    )


@router.post("/algebra/packet/decode")
async def decode_algebra_packet(request: Request):
    """
    📦 DECODE BALG PACKET
    """
    body = await request.body()
    algebra = get_binary_algebra()
    
    try:
        decoded = algebra.parse_packet(body)
        return decoded
    except Exception as e:
        raise HTTPException(400, f"Decode error: {e}")


@router.get("/algebra/bits")
async def bit_manipulation(value: int, operation: str = "info", position: int = 0):
    """
    🔧 BIT MANIPULATION
    
    operations: info, get, set, clear, toggle, count
    """
    num = BinaryNumber(value, 64)
    
    if operation == "info":
        raw = struct.pack(
            '>Q I I',  # value, ones, zeros
            num.value,
            num.count_ones(),
            num.count_zeros()
        )
    elif operation == "get":
        raw = struct.pack('>B', num.bit(position))
    elif operation == "set":
        result = num.set_bit(position, 1)
        raw = result.bytes
    elif operation == "clear":
        result = num.set_bit(position, 0)
        raw = result.bytes
    elif operation == "toggle":
        result = num.toggle_bit(position)
        raw = result.bytes
    elif operation == "count":
        raw = struct.pack('>II', num.count_ones(), num.count_zeros())
    else:
        raw = num.bytes
    
    return Response(
        content=raw,
        media_type="application/octet-stream",
        headers={
            "X-Original": str(value),
            "X-Original-Binary": num.binary,
            "X-Operation": operation,
            "X-Position": str(position) if position else "",
            "X-Result-Hex": raw.hex()
        }
    )


@router.get("/algebra/cascade")
async def cascade_operations(ops: str = "5:xor:3|:and:7|:shl:2"):
    """
    ⛓️ KASKADË OPERACIONESH
    
    Format: value:op:operand|:op:operand|...
    Shembull: 5:xor:3|:and:7|:shl:2
    """
    algebra = get_binary_algebra()
    
    steps = ops.split('|')
    results = []
    current = 0
    
    for i, step in enumerate(steps):
        parts = step.strip(':').split(':')
        
        if i == 0 and len(parts) >= 3:
            a = int(parts[0])
            op = parts[1]
            b = int(parts[2])
        elif len(parts) >= 2:
            a = current
            op = parts[0]
            b = int(parts[1])
        else:
            continue
        
        result_bytes = algebra.operate_raw(a, op, b, 64)
        current = int.from_bytes(result_bytes, 'big')
        results.append({
            "step": i + 1,
            "a": a,
            "op": op,
            "b": b,
            "result": current
        })
    
    # Pack all results
    raw = struct.pack(f'>{len(results)}Q', *[r["result"] for r in results])
    
    return Response(
        content=raw,
        media_type="application/octet-stream",
        headers={
            "X-Steps": str(len(results)),
            "X-Final-Result": str(current),
            "X-Final-Binary": format(current, '064b'),
            "X-Final-Hex": format(current, '016x'),
            "X-Operations": '->'.join(s['op'] for s in results)
        }
    )


@router.get("/algebra/truth-table")
async def truth_table(op: str = "and", bits: int = 2):
    """
    📋 TRUTH TABLE NË BINARY
    
    Kthen tabelën e vërtetësisë si bytes
    """
    max_val = 1 << bits
    results = []
    
    for a in range(max_val):
        for b in range(max_val):
            if op.lower() in ["and", "&"]:
                r = a & b
            elif op.lower() in ["or", "|"]:
                r = a | b
            elif op.lower() in ["xor", "^"]:
                r = a ^ b
            elif op.lower() in ["nand"]:
                r = ~(a & b) & (max_val - 1)
            elif op.lower() in ["nor"]:
                r = ~(a | b) & (max_val - 1)
            elif op.lower() in ["xnor"]:
                r = ~(a ^ b) & (max_val - 1)
            else:
                r = a & b
            
            results.append((a, b, r))
    
    # Pack: each entry is 3 bytes (a, b, result)
    raw = bytearray()
    for a, b, r in results:
        raw.extend(struct.pack('>BBB', a, b, r))
    
    return Response(
        content=bytes(raw),
        media_type="application/octet-stream",
        headers={
            "X-Operation": op,
            "X-Bits": str(bits),
            "X-Entries": str(len(results)),
            "X-Format": "A:B:Result (1 byte each)"
        }
    )


@router.get("/algebra/stats")
async def algebra_stats():
    """📊 Statistikat e motorit të algjebës"""
    algebra = get_binary_algebra()
    return algebra.get_stats()


# ==================== KLOUD BINARY PROTOCOL (CBP) ====================

@router.post("/cbp/encode")
async def cbp_encode(request: Request):
    """
    📦 CBP ENCODE - JSON → Binary
    
    Merr JSON, kthen binary frame me CLSN header
    """
    try:
        data = await request.json()
    except:
        data = {}
    
    msg_type_str = request.headers.get("X-Message-Type", "unknown").upper()
    msg_type = getattr(MessageType, msg_type_str, MessageType.UNKNOWN)
    
    compress = request.headers.get("X-Compress", "false").lower() == "true"
    
    protocol = get_protocol()
    binary = protocol.encode_message(data, msg_type, compress=compress)
    
    return Response(
        content=binary,
        media_type="application/x-kloud",
        headers={
            "X-Magic": "CLSN",
            "X-Version": "1",
            "X-Message-Type": msg_type.name,
            "X-Compressed": str(compress),
            "X-Size": str(len(binary))
        }
    )


@router.post("/cbp/decode")
async def cbp_decode(request: Request):
    """
    📦 CBP DECODE - Binary → JSON
    
    Merr binary frame, kthen JSON
    """
    body = await request.body()
    
    if not body:
        raise HTTPException(400, "Empty body")
    
    try:
        protocol = get_protocol()
        msg_type, data = protocol.decode_message(body)
        
        return {
            "success": True,
            "message_type": msg_type.name,
            "frame_size": len(body),
            "data": data
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "frame_size": len(body),
            "hex_preview": body[:50].hex()
        }


@router.post("/cbp/frame/dump")
async def cbp_frame_dump(request: Request):
    """
    🔍 CBP FRAME DUMP - Struktura e frame-it
    """
    body = await request.body()
    return dump_frame(body)


@router.get("/cbp/schemas")
async def cbp_list_schemas():
    """
    📋 Lista e schema-ve të regjistruara
    """
    registry = get_schema_registry()
    
    schemas = []
    for name, schema in registry.schemas.items():
        schemas.append({
            "name": schema.name,
            "version": schema.version,
            "type_id": hex(schema.type_id),
            "fields": len(schema.fields),
            "field_names": [f.name for f in schema.fields]
        })
    
    return {
        "count": len(schemas),
        "schemas": schemas
    }


@router.get("/cbp/schema/{name}")
async def cbp_get_schema(name: str):
    """
    📄 Merr detajet e një schema
    """
    registry = get_schema_registry()
    schema = registry.get(name)
    
    if not schema:
        raise HTTPException(404, f"Schema not found: {name}")
    
    return {
        "name": schema.name,
        "version": schema.version,
        "type_id": hex(schema.type_id),
        "fields": [
            {
                "name": f.name,
                "type": f.dtype.name,
                "offset": f.offset,
                "length_field": f.length_field,
                "description": f.description
            }
            for f in schema.fields
        ]
    }


@router.post("/cbp/request")
async def cbp_binary_request(request: Request):
    """
    🔄 BINARY REQUEST/RESPONSE
    
    Merr binary request, kthen binary response.
    Komunikim 100% binar!
    """
    body = await request.body()
    
    if not body:
        raise HTTPException(400, "Empty binary request")
    
    protocol = get_protocol()
    
    try:
        msg_type, data = protocol.decode_message(body)
        
        # Process based on message type
        if msg_type == MessageType.CALCULATE:
            # Calculate
            expr = data.get("expression", "0")
            try:
                result = eval(expr)
            except:
                result = 0
            
            response_data = {
                "expression": expr,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
            response_type = MessageType.CALCULATE
            
        elif msg_type == MessageType.CHAT:
            # Chat
            query = data.get("query", "")
            response_data = {
                "query": query,
                "response": f"Echo: {query}",
                "timestamp": datetime.now().isoformat()
            }
            response_type = MessageType.CHAT
            
        elif msg_type == MessageType.TIME:
            # Time
            now = datetime.now()
            response_data = {
                "timestamp": now.timestamp(),
                "iso": now.isoformat(),
                "hour": now.hour,
                "minute": now.minute,
                "second": now.second
            }
            response_type = MessageType.TIME
            
        else:
            # Echo
            response_data = {
                "received_type": msg_type.name,
                "data": data,
                "echo": True
            }
            response_type = msg_type
        
        # Encode response
        response_binary = protocol.encode_message(response_data, response_type)
        
        return Response(
            content=response_binary,
            media_type="application/x-kloud",
            headers={
                "X-Magic": "CLSN",
                "X-Request-Type": msg_type.name,
                "X-Response-Type": response_type.name,
                "X-Size": str(len(response_binary))
            }
        )
        
    except Exception as e:
        error_binary = protocol.create_error_frame(500, str(e))
        return Response(
            content=error_binary,
            media_type="application/x-kloud",
            status_code=400,
            headers={"X-Error": str(e)}
        )


# ==================== STREAMING ====================

@router.get("/cbp/stream/start")
async def cbp_stream_start(stream_id: int = 1, chunk_size: int = 256):
    """
    🌊 START STREAM
    
    Kthen info për stream të ri
    """
    protocol = get_protocol()
    stream = protocol.create_stream(stream_id, chunk_size)
    
    return {
        "stream_id": stream_id,
        "chunk_size": chunk_size,
        "status": "created"
    }


@router.post("/cbp/stream/write")
async def cbp_stream_write(request: Request, stream_id: int = 1):
    """
    🌊 WRITE TO STREAM
    
    Shkruan data dhe kthen frames
    """
    body = await request.body()
    protocol = get_protocol()
    
    if stream_id not in protocol.streams:
        protocol.create_stream(stream_id)
    
    stream = protocol.streams[stream_id]
    frames = stream.write(body)
    
    # Combine all frame bytes
    output = bytearray()
    for frame in frames:
        output.extend(frame.to_bytes())
    
    # Flush remaining
    last_frame = stream.flush()
    if last_frame:
        output.extend(last_frame.to_bytes())
        frames.append(last_frame)
    
    return Response(
        content=bytes(output),
        media_type="application/x-kloud-stream",
        headers={
            "X-Stream-Id": str(stream_id),
            "X-Frames": str(len(frames)),
            "X-Total-Size": str(len(output))
        }
    )


@router.get("/cbp/stream/sample")
async def cbp_stream_sample(count: int = 10, interval_ms: int = 100):
    """
    📊 SAMPLE STREAM
    
    Gjeneron stream të samples (sensor simulation)
    """
    import random
    
    protocol = get_protocol()
    stream = protocol.create_stream(1, 64)
    
    frames = []
    for i in range(count):
        sample = {
            "seq": i,
            "value": random.random() * 100,
            "timestamp": datetime.now().timestamp()
        }
        
        sample_bytes = protocol.encoder.encode(sample)
        chunk_frames = stream.write(sample_bytes)
        frames.extend(chunk_frames)
    
    # Flush
    last = stream.flush()
    if last:
        frames.append(last)
    
    # Combine
    output = bytearray()
    for frame in frames:
        output.extend(frame.to_bytes())
    
    return Response(
        content=bytes(output),
        media_type="application/x-kloud-stream",
        headers={
            "X-Sample-Count": str(count),
            "X-Frames": str(len(frames)),
            "X-Size": str(len(output))
        }
    )


@router.get("/cbp/version")
async def cbp_version():
    """ℹ️ CBP Protocol version info"""
    return {
        "name": "Kloud Binary Protocol",
        "version": 1,
        "magic": "CLSN",
        "header_size": 8,
        "features": [
            "compression",
            "checksum",
            "streaming",
            "schema_registry"
        ],
        "message_types": [t.name for t in MessageType],
        "flags": [f.name for f in FrameFlags if f != FrameFlags.NONE]
    }


# ==================== REAL LEARNING (NOT MOCK!) ====================

@router.get("/real-learn/query")
async def real_learning_query(q: str):
    """
    🧠 REAL LEARNING QUERY
    
    Përgjigjet vijnë nga burime REALE:
    - Git history
    - File contents
    - Package info
    - Docstrings
    - NOT from teach/mock!
    """
    engine = get_real_learning()
    result = engine.query(q)
    return result


@router.get("/real-learn/knowledge")
async def real_learning_all():
    """
    📚 ALL REAL KNOWLEDGE
    
    Gjithë dijet e nxjerra nga burime reale
    """
    engine = get_real_learning()
    return engine.get_all_knowledge()


@router.post("/real-learn/refresh")
async def real_learning_refresh():
    """
    🔄 REFRESH - Rimëso nga burimet
    """
    engine = get_real_learning()
    engine.refresh()
    return {
        "success": True,
        "message": "Knowledge refreshed from real sources",
        "total_knowledge": len(engine.knowledge)
    }


@router.get("/real-learn/authors")
async def real_learning_authors():
    """
    👤 WHO MADE THIS? (REAL)
    """
    engine = get_real_learning()
    
    authors = {}
    for key in ['primary_author', 'package_authors', 'npm_author', 'project_authors']:
        if key in engine.knowledge:
            k = engine.knowledge[key]
            authors[key] = {
                "value": k.value,
                "source": k.source,
                "confidence": k.confidence,
                "evidence": k.evidence
            }
    
    return {
        "authors": authors,
        "is_mock": False,
        "is_real": True
    }


@router.get("/real-learn/stats")
async def real_learning_stats():
    """
    📊 PROJECT STATS (REAL)
    """
    engine = get_real_learning()
    
    stats = {}
    for key in ['total_commits', 'total_lines', 'file_counts', 'main_modules', 'project_started', 'current_branch']:
        if key in engine.knowledge:
            k = engine.knowledge[key]
            stats[key] = {
                "value": k.value,
                "source": k.source
            }
    
    return {
        "stats": stats,
        "is_mock": False,
        "is_real": True
    }

