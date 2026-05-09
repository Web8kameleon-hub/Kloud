#!/usr/bin/env python3
"""
CORE REASONING PIPELINE
=======================
Truri kryesor i Curiosity Ocean.
Përpunon çdo input tekstual me:
- Instruction following
- Self-analysis
- Debugging mode
- Admin mode
- Conversation memory
"""

import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger("CoreReasoning")


class ReasoningMode(Enum):
    """Mënyrat e reasoning"""
    NORMAL = "normal"
    STRICT = "strict"
    ADMIN = "admin"
    DEBUG = "debug"
    SELF_ANALYSIS = "self_analysis"


@dataclass
class ReasoningContext:
    """Konteksti i një sesioni reasoning"""
    session_id: str
    mode: ReasoningMode
    history: List[Dict[str, str]]
    strict_rules: List[str]
    max_tokens: int = -1
    temperature: float = 0.7


STRICT_RULES = """
## STRICT MODE - RREGULLA TË DETYRUESHME

1. **QËNDRO NË TEMË**: Përgjigju VETËM asaj që u pyet. Mos shto informacion shtesë.
2. **MOS PYET**: Mos i bëj pyetje përdoruesit. Thjesht përgjigju.
3. **MOS DEVIJO**: Mos ndrysho temën ose shto përmbajtje të palidhur.
4. **MOS HALUCINO**: Nëse nuk di, thuaj "Nuk e di". Mos shpik.
5. **NDIQ UDHËZIMET**: Nëse të jepen hapa, ekzekutoji TË GJITHË në rend.
6. **VETË-ANALIZË**: Nëse të kërkohet të analizosh përgjigjen, bëje sinqerisht.
7. **FILLO MENJËHERË**: Fillo të shkruash menjëherë, pa hyrje.
8. **OUTPUT I VAZHDUESHËM**: Shkruaj pa u ndalur derisa detyra të përfundojë.

SHKELJA E KËTYRE RREGULLAVE NUK LEJOHET.
"""

ADMIN_RULES = """
## ADMIN MODE - PRIVILEGJE TË PLOTA

Ti je në modalitetin administrativ. Ke akses të plotë në:
- Diagnostikim të sistemit
- Analiza të thella
- Korrigjim të gabimeve
- Raportim të detajuar

Përgjigju me:
- Saktësi absolute
- Detaje teknike kur kërkohen
- Strukturë të qartë
- Pa devijime
"""

DEBUG_RULES = """
## DEBUG MODE - MËNYRA E DEBUGIMIT

Raporto çdo hap të procesimit:
1. Si e kuptove pyetjen
2. Çfarë konteksti përdore
3. Si e ndërtove përgjigjen
4. Ku mund të ketë pasaktësi
"""

SELF_ANALYSIS_TEMPLATE = """
## VETË-ANALIZË E KËRKUAR

Analizo përgjigjen tënde të mëparshme dhe identifiko:
1. **Gabime përkthimi**: A ka fjalë të përkthyera gabim?
2. **Mospërputhje logjike**: A ka kontradikta?
3. **Përmbajtje e palidhur**: A ka devijime nga tema?
4. **Halucinacione**: A ka informacion të shpikur?

Për çdo gabim:
- Shpjego gabimin qartë
- Jep korrigjimin e saktë

Në fund, rishkruaj përgjigjen e plotë të korrigjuar.
"""


class CoreReasoningPipeline:
    """Pipeline kryesor i reasoning"""
    
    def __init__(self):
        self.active_sessions: Dict[str, ReasoningContext] = {}
        self.processed_count = 0
        logger.info("✅ CoreReasoningPipeline initialized")
    
    def create_session(
        self, 
        session_id: str, 
        mode: ReasoningMode = ReasoningMode.NORMAL
    ) -> ReasoningContext:
        """Krijo një sesion të ri reasoning"""
        context = ReasoningContext(
            session_id=session_id,
            mode=mode,
            history=[],
            strict_rules=STRICT_RULES.split("\n") if mode == ReasoningMode.STRICT else []
        )
        self.active_sessions[session_id] = context
        return context
    
    def get_system_prompt(self, mode: ReasoningMode) -> str:
        """Merr system prompt sipas mode"""
        base = """Ti je Curiosity Ocean 🌊 - Truri i Avancuar i Kloud Cloud.
Krijuar nga Ledjan Ahmati (ABA GmbH, Gjermani) në 2025.
Platforma: https://kloud.cloud

SJELLJA KRYESORE:
- Fillo të shkruash menjëherë që në sekondat e para
- Mos bëj pauza mendimi para se të përgjigjesh
- Prodho output të vazhdueshëm pa ndërprerje
- Vazhdo derisa përgjigja të jetë e plotë
"""
        
        if mode == ReasoningMode.STRICT:
            return base + STRICT_RULES
        elif mode == ReasoningMode.ADMIN:
            return base + ADMIN_RULES
        elif mode == ReasoningMode.DEBUG:
            return base + DEBUG_RULES
        elif mode == ReasoningMode.SELF_ANALYSIS:
            return base + SELF_ANALYSIS_TEMPLATE
        
        return base
    
    def build_messages(
        self, 
        context: ReasoningContext, 
        user_message: str
    ) -> List[Dict[str, str]]:
        """Ndërto listën e mesazheve për Ollama"""
        messages = [
            {"role": "system", "content": self.get_system_prompt(context.mode)}
        ]
        
        # Shto historinë
        for msg in context.history[-10:]:  # Last 10 messages
            messages.append(msg)
        
        # Shto mesazhin aktual
        messages.append({"role": "user", "content": user_message})
        
        return messages
    
    def add_to_history(
        self, 
        context: ReasoningContext, 
        role: str, 
        content: str
    ):
        """Shto mesazh në histori"""
        context.history.append({"role": role, "content": content})
        
        # Limit history to 50 messages
        if len(context.history) > 50:
            context.history = context.history[-50:]
    
    def get_ollama_options(self, mode: ReasoningMode) -> Dict[str, Any]:
        """Merr opsionet e Ollama sipas mode"""
        base_options = {
            "num_ctx": 8192,
            "num_predict": -1,  # Unlimited
            "num_keep": 0,
            "mirostat": 0,
            "repeat_last_n": 64,
            "stop": []
        }
        
        if mode == ReasoningMode.STRICT:
            base_options["temperature"] = 0.3  # Më deterministik
            base_options["repeat_penalty"] = 1.3
        elif mode == ReasoningMode.ADMIN:
            base_options["temperature"] = 0.5
            base_options["repeat_penalty"] = 1.2
        else:
            base_options["temperature"] = 0.7
            base_options["repeat_penalty"] = 1.1
        
        return base_options
    
    def process(
        self, 
        session_id: str, 
        message: str, 
        mode: Optional[ReasoningMode] = None
    ) -> Dict[str, Any]:
        """
        Proceso një mesazh përmes pipeline.
        Kthen dict me: messages, options, mode
        """
        # Get or create session
        if session_id not in self.active_sessions:
            self.create_session(session_id, mode or ReasoningMode.NORMAL)
        
        context = self.active_sessions[session_id]
        
        # Update mode if specified
        if mode:
            context.mode = mode
        
        # Build request
        messages = self.build_messages(context, message)
        options = self.get_ollama_options(context.mode)
        
        self.processed_count += 1
        
        return {
            "session_id": session_id,
            "mode": context.mode.value,
            "messages": messages,
            "options": options,
            "history_length": len(context.history)
        }
    
    def record_response(self, session_id: str, user_msg: str, assistant_msg: str):
        """Regjistro përgjigjen në histori"""
        if session_id in self.active_sessions:
            context = self.active_sessions[session_id]
            self.add_to_history(context, "user", user_msg)
            self.add_to_history(context, "assistant", assistant_msg)
    
    def clear_session(self, session_id: str):
        """Pastro një sesion"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
    
    def get_stats(self) -> Dict[str, Any]:
        """Merr statistikat"""
        return {
            "active_sessions": len(self.active_sessions),
            "processed_count": self.processed_count,
            "modes": {
                mode.value: sum(
                    1 for ctx in self.active_sessions.values() 
                    if ctx.mode == mode
                )
                for mode in ReasoningMode
            }
        }


# Singleton instance
_pipeline: Optional[CoreReasoningPipeline] = None


def get_reasoning_pipeline() -> CoreReasoningPipeline:
    """Merr instancën singleton të pipeline"""
    global _pipeline
    if _pipeline is None:
        _pipeline = CoreReasoningPipeline()
    return _pipeline

