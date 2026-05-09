# -*- coding: utf-8 -*-
"""
🌊 CURIOSITY OCEAN - SIGNAL ALGEBRA SYSTEM
==========================================
Sistemi algjebrik që lidh çdo qelizë të brendshme dhe të jashtme të projektit.

Manifesti Filozofik:
- Çdo modul është qelizë
- Çdo sinjal është puls
- Çdo puls është pyetje
- Deti i kuriozitetit kurrë nuk pushon së kërkuari

Components:
- EventBus: Deti ku derdhen të gjitha sinjalet
- SignalAlgebra: Motori matematikor (superpozim, filtrim, devijim, korelacion)
- CellRegistry: Anatomia e organizmës (graf qelizash)
- CallOperator: Thirrja e qelizave
- CuriosityOrchestrator: Vetëdija e sistemit
- MegaSignalCollector: Skanimi i TË GJITHA sinjaleve
- BinaryProtocols: CBOR2, MessagePack, Custom Binary
- BinaryAlgebra: ALGJEBËR BINARE - AND, OR, XOR, NOT, SHIFT, Matrica GF(2)
- CBP Protocol: Kloud Binary Protocol - streaming, compression, schemas
- I18nEngine: 11 gjuhë
- RealChatEngine: Chat real

Author: Kloud Team
Version: 2.4.0 - CBP Protocol Edition
"""

from .event_bus import EventBus, Event
from .signal_algebra import SignalAlgebra
from .cell_registry import CellRegistry, Cell
from .call_operator import CallOperator
from .curiosity_orchestrator import CuriosityOrchestrator
from .signal_integrator import UniversalSignalIntegrator
from .mega_signal_collector import MegaSignalCollector, MegaSignal, SignalType, get_mega_collector
from .binary_protocols import (
    BinaryEncoder, BinaryBuffer, BinaryMessage, BinaryFormat, BinaryProtocolService,
    SignalPacket, AlgebraPacket, SmartCalculator, DataType,
    get_binary_service
)
from .i18n_engine import (
    I18nEngine, LanguageDetector, Language, TranslationEntry,
    get_i18n_engine, t, detect_lang
)
from .real_chat_engine import (
    RealChatEngine, IntentDetector, IntentType, ChatIntent, ChatResponse,
    get_real_chat_engine
)
from .binary_algebra import (
    BinaryAlgebraEngine, BinaryNumber, BinarySignal, BinaryMatrix, BinaryOp,
    get_binary_algebra
)
from .cbp_protocol import (
    KloudProtocol, Frame, StreamFrame, FrameFlags, MessageType,
    SchemaRegistry, Schema, SchemaField, BinaryStream,
    get_protocol, get_schema_registry, dump_frame,
    read_clsn_file, write_clsn_file
)

__all__ = [
    # Core Components
    'EventBus',
    'Event', 
    'SignalAlgebra',
    'CellRegistry',
    'Cell',
    'CallOperator',
    'CuriosityOrchestrator',
    'UniversalSignalIntegrator',
    # Mega Collector
    'MegaSignalCollector',
    'MegaSignal',
    'SignalType',
    'get_mega_collector',
    # Binary Protocols
    'BinaryEncoder',
    'BinaryBuffer',
    'BinaryMessage',
    'BinaryFormat',
    'BinaryProtocolService',
    'SignalPacket',
    'AlgebraPacket',
    'SmartCalculator',
    'DataType',
    'get_binary_service',
    # I18n Engine
    'I18nEngine',
    'LanguageDetector',
    'Language',
    'TranslationEntry',
    'get_i18n_engine',
    't',
    'detect_lang',
    # Real Chat Engine
    'RealChatEngine',
    'IntentDetector',
    'IntentType',
    'ChatIntent',
    'ChatResponse',
    'get_real_chat_engine',
    # Binary Algebra Engine
    'BinaryAlgebraEngine',
    'BinaryNumber',
    'BinarySignal',
    'BinaryMatrix',
    'BinaryOp',
    'get_binary_algebra',
    # CBP Protocol
    'KloudProtocol',
    'Frame',
    'StreamFrame',
    'FrameFlags',
    'MessageType',
    'SchemaRegistry',
    'Schema',
    'SchemaField',
    'BinaryStream',
    'get_protocol',
    'get_schema_registry',
    'dump_frame',
    'read_clsn_file',
    'write_clsn_file'
]

__version__ = "2.4.0"

