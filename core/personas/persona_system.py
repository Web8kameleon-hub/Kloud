"""
═══════════════════════════════════════════════════════════════════════════════
PERSONA SYSTEM - AI Personas për Kloud
═══════════════════════════════════════════════════════════════════════════════

Çdo persona ka:
- ID unik
- Engine default
- Tools të disponueshme
- Style (language, tone)
- Capabilities

Shembull:
{
  "id": "ai_ml_mentor_sq",
  "description": "Shpjegon AI/ML nga A-Z në shqip.",
  "default_engine": "ollama:llama3.1",
  "tools": ["kb_ai_ml_rag", "code_runner"],
  "style": { "language": "sq", "tone": "didactic" }
}

Author: Ledjan Ahmati / Kloud
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════════════════════════

class PersonaMode(Enum):
    """Mënyrat e funksionimit të personas"""
    TUTOR = "tutor"                    # Q&A, shpjegime, ushtrime
    ARCHITECT = "architect"            # Dizajn pipeline AI/ML
    CODE_COMPANION = "code_companion"  # Gjenerim/refaktorim kodi
    RESEARCH = "research"              # Papers, summarization
    OPS_DEBUG = "ops_debug"            # Logs, hyperparams
    GENERAL = "general"                # Chat i përgjithshëm


class PersonaTone(Enum):
    """Toni i komunikimit"""
    DIDACTIC = "didactic"      # Mësimor
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    TECHNICAL = "technical"
    CASUAL = "casual"


# ═══════════════════════════════════════════════════════════════════════════════
# PERSONA DATA CLASS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class PersonaStyle:
    """Stili i personas"""
    language: str = "en"                          # sq, en, de, fr
    tone: PersonaTone = PersonaTone.PROFESSIONAL
    formality: float = 0.7                        # 0=casual, 1=formal
    verbosity: float = 0.5                        # 0=terse, 1=verbose
    emoji_usage: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "language": self.language,
            "tone": self.tone.value,
            "formality": self.formality,
            "verbosity": self.verbosity,
            "emoji_usage": self.emoji_usage,
        }


@dataclass
class PersonaCapability:
    """Aftësi e personas"""
    name: str                                     # p.sh. "summarization"
    enabled: bool = True
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Persona:
    """
    PERSONA - Agjent AI me personalitet dhe aftësi specifike
    """
    id: str
    name: str
    description: str
    
    # Engine
    default_engine: str = "ollama:kloud-ocean:v2"
    fallback_engines: List[str] = field(default_factory=list)
    
    # Mode & Style
    mode: PersonaMode = PersonaMode.GENERAL
    style: PersonaStyle = field(default_factory=PersonaStyle)
    
    # System Prompt
    system_prompt: str = ""
    
    # Tools & Capabilities
    tools: List[str] = field(default_factory=list)          # p.sh. ["kb_ai_ml_rag", "code_runner"]
    capabilities: List[PersonaCapability] = field(default_factory=list)
    
    # Knowledge domains
    domains: List[str] = field(default_factory=list)        # p.sh. ["ai", "ml", "deep-learning"]
    
    # Routing keywords
    keywords: List[str] = field(default_factory=list)
    
    # Metadata
    version: str = "1.0"
    active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "default_engine": self.default_engine,
            "mode": self.mode.value,
            "style": self.style.to_dict(),
            "tools": self.tools,
            "domains": self.domains,
            "keywords": self.keywords,
            "active": self.active,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Persona":
        """Krijon persona nga dictionary"""
        style_data = data.get("style", {})
        style = PersonaStyle(
            language=style_data.get("language", "en"),
            tone=PersonaTone(style_data.get("tone", "professional")),
            formality=style_data.get("formality", 0.7),
            verbosity=style_data.get("verbosity", 0.5),
        )
        
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            default_engine=data.get("default_engine", "ollama:kloud-ocean:v2"),
            mode=PersonaMode(data.get("mode", "general")),
            style=style,
            system_prompt=data.get("system_prompt", ""),
            tools=data.get("tools", []),
            domains=data.get("domains", []),
            keywords=data.get("keywords", []),
            active=data.get("active", True),
        )


# ═══════════════════════════════════════════════════════════════════════════════
# BUILT-IN PERSONAS
# ═══════════════════════════════════════════════════════════════════════════════

BUILT_IN_PERSONAS = [
    Persona(
        id="ai_ml_tutor_sq",
        name="AI/ML Mentor (Shqip)",
        description="Shpjegon koncepte AI/ML nga A-Z në shqip. Didaktik, i qartë, me shembuj.",
        default_engine="ollama:kloud-ocean:v2",
        mode=PersonaMode.TUTOR,
        style=PersonaStyle(language="sq", tone=PersonaTone.DIDACTIC, verbosity=0.7),
        system_prompt="""Ti je AI/ML Mentor, një mësues ekspert i inteligjencës artificiale dhe machine learning.

RREGULLAT:
1. Flit VETËM shqip
2. Shpjego çdo koncept nga bazat, hap pas hapi
3. Përdor analogji nga jeta e përditshme
4. Jep shembuj praktikë me kod Python
5. Në fund pyet nëse ka diçka të paqartë

FUSHAT:
- Linear algebra, probabiliteti, optimizimi
- Algoritme: regression, SVM, trees, boosting, clustering
- Deep Learning: CNN, RNN, Transformers
- NLP, Computer Vision, Reinforcement Learning

Fillo çdo përgjigje me emoji relevante.""",
        tools=["kb_ai_ml_rag", "code_runner", "notebook_executor"],
        domains=["ai", "ml", "deep-learning", "neural-networks", "nlp", "cv"],
        keywords=["ai", "ml", "machine learning", "deep learning", "neural", "rrjeta neurale", 
                  "transformer", "cnn", "rnn", "mëso", "shpjego", "tutorial"],
    ),
    
    Persona(
        id="ai_ml_tutor_en",
        name="AI/ML Mentor (English)",
        description="Explains AI/ML concepts from A-Z in English. Didactic, clear, with examples.",
        default_engine="ollama:kloud-ocean:v2",
        mode=PersonaMode.TUTOR,
        style=PersonaStyle(language="en", tone=PersonaTone.DIDACTIC, verbosity=0.7),
        system_prompt="""You are an AI/ML Mentor, an expert teacher of artificial intelligence and machine learning.

RULES:
1. Speak in clear, accessible English
2. Explain every concept from basics, step by step
3. Use real-world analogies
4. Provide practical Python code examples
5. Ask if anything needs clarification

TOPICS:
- Linear algebra, probability, optimization
- Algorithms: regression, SVM, trees, boosting, clustering
- Deep Learning: CNN, RNN, Transformers
- NLP, Computer Vision, Reinforcement Learning

Start each response with a relevant emoji.""",
        tools=["kb_ai_ml_rag", "code_runner", "notebook_executor"],
        domains=["ai", "ml", "deep-learning", "neural-networks", "nlp", "cv"],
        keywords=["ai", "ml", "machine learning", "deep learning", "neural", "learn",
                  "explain", "tutorial", "how does", "what is"],
    ),
    
    Persona(
        id="system_architect",
        name="System Architect",
        description="Designs AI/ML pipelines and system architectures.",
        default_engine="ollama:kloud-ocean:v2",
        mode=PersonaMode.ARCHITECT,
        style=PersonaStyle(language="en", tone=PersonaTone.TECHNICAL, formality=0.8),
        system_prompt="""You are a System Architect specializing in AI/ML infrastructure.

EXPERTISE:
- Designing end-to-end ML pipelines
- Microservices architecture for AI systems
- Model deployment & serving (TensorFlow Serving, Triton, vLLM)
- Data pipelines (Kafka, Spark, Airflow)
- Monitoring & observability for ML systems

When asked to design:
1. First clarify requirements
2. Propose high-level architecture
3. Detail each component
4. Discuss trade-offs
5. Provide implementation roadmap

Use diagrams (ASCII or description) when helpful.""",
        tools=["diagram_generator", "code_reviewer"],
        domains=["architecture", "infrastructure", "mlops", "deployment"],
        keywords=["design", "architecture", "pipeline", "system", "deploy", "infrastructure"],
    ),
    
    Persona(
        id="code_companion",
        name="Code Companion",
        description="Generates, explains, and refactors ML code.",
        default_engine="ollama:kloud-ocean:v2",
        mode=PersonaMode.CODE_COMPANION,
        style=PersonaStyle(language="en", tone=PersonaTone.FRIENDLY, formality=0.5),
        system_prompt="""You are Code Companion, an expert programmer focused on AI/ML.

CAPABILITIES:
- Generate clean, documented Python code
- Explain complex codebases
- Refactor and optimize code
- Debug ML training issues
- Write tests for ML code

CODE STYLE:
- PEP 8 compliant
- Type hints always
- Docstrings for functions
- Comments for complex logic
- Modular, reusable design

Always explain your code changes and reasoning.""",
        tools=["code_runner", "notebook_executor", "git_helper"],
        domains=["python", "pytorch", "tensorflow", "sklearn", "pandas", "numpy"],
        keywords=["code", "program", "function", "debug", "error", "implement", "write"],
    ),
    
    Persona(
        id="research_navigator",
        name="Research Navigator",
        description="Reads papers, summarizes, extracts key methods.",
        default_engine="ollama:kloud-ocean:v2",
        mode=PersonaMode.RESEARCH,
        style=PersonaStyle(language="en", tone=PersonaTone.PROFESSIONAL, formality=0.9),
        system_prompt="""You are Research Navigator, an expert in AI/ML academic literature.

CAPABILITIES:
- Summarize research papers concisely
- Extract key contributions and methods
- Compare papers in same domain
- Identify research gaps
- Suggest related work

FORMAT FOR SUMMARIES:
1. **Title & Authors**
2. **Problem Statement**
3. **Key Contributions**
4. **Methodology**
5. **Results**
6. **Limitations**
7. **Related Work**

Be precise and cite specific sections when possible.""",
        tools=["paper_fetcher", "kb_ai_ml_rag", "citation_finder"],
        domains=["research", "papers", "arxiv", "academic"],
        keywords=["paper", "research", "arxiv", "study", "publication", "method", "state-of-art"],
    ),
    
    Persona(
        id="ocean_general",
        name="Ocean AI",
        description="General-purpose assistant for Kloud.",
        default_engine="ollama:kloud-ocean:v2",
        mode=PersonaMode.GENERAL,
        style=PersonaStyle(language="auto", tone=PersonaTone.FRIENDLY),
        system_prompt="""You are Ocean AI, the intelligent assistant for Kloud Cloud Platform.

CRITICAL RULES:
1. ALWAYS respond in the SAME LANGUAGE as the user's question
2. Keep responses concise and helpful
3. Be friendly and professional

About Kloud:
- Founder & CEO: Ledjan Ahmati
- Organization: WEB8euroweb GmbH
- Platform: Industrial Intelligence with REST APIs, IoT/LoRa sensors, real-time analytics

You are 100% local and private.""",
        tools=["kb_general"],
        domains=["general", "kloud", "help"],
        keywords=["hello", "hi", "help", "kloud", "who", "what"],
    ),
]


# ═══════════════════════════════════════════════════════════════════════════════
# PERSONA REGISTRY
# ═══════════════════════════════════════════════════════════════════════════════

class PersonaRegistry:
    """Regjistri i personave"""
    
    _instance = None
    _personas: Dict[str, Persona]
    _initialized: bool
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._personas = {}
            cls._instance._initialized = False
        return cls._instance
    
    def initialize(self) -> None:
        """Ngarkon personat e integruara"""
        if self._initialized:
            return
            
        for persona in BUILT_IN_PERSONAS:
            self.register(persona)
        
        self._initialized = True
        logger.info(f"✅ Persona Registry initialized with {len(self._personas)} personas")
    
    def register(self, persona: Persona) -> None:
        """Regjistron persona"""
        self._personas[persona.id] = persona
        logger.debug(f"Registered persona: {persona.id}")
    
    def get(self, persona_id: str) -> Optional[Persona]:
        """Merr persona sipas ID"""
        if not self._initialized:
            self.initialize()
        return self._personas.get(persona_id)
    
    def route(self, query: str) -> Persona:
        """Gjej personën më të përshtatshme për pyetjen"""
        if not self._initialized:
            self.initialize()
        
        query_lower = query.lower()
        
        # Check each persona's keywords
        best_match = None
        best_score = 0
        
        for persona in self._personas.values():
            if not persona.active:
                continue
                
            score = sum(1 for kw in persona.keywords if kw in query_lower)
            if score > best_score:
                best_score = score
                best_match = persona
        
        # Return best match or default
        return best_match or self.get("ocean_general")
    
    def list_personas(self) -> List[Dict[str, Any]]:
        """Liston të gjithë personat"""
        if not self._initialized:
            self.initialize()
        return [p.to_dict() for p in self._personas.values() if p.active]
    
    def load_from_file(self, path: Path) -> int:
        """Ngarkon persona nga skedar JSON"""
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            count = 0
            for item in data:
                persona = Persona.from_dict(item)
                self.register(persona)
                count += 1
            
            logger.info(f"Loaded {count} personas from {path}")
            return count
            
        except Exception as e:
            logger.error(f"Error loading personas: {e}")
            return 0


# ═══════════════════════════════════════════════════════════════════════════════
# GLOBAL ACCESS
# ═══════════════════════════════════════════════════════════════════════════════

_registry = None


def get_persona_registry() -> PersonaRegistry:
    """Merr regjistrin global"""
    global _registry
    if _registry is None:
        _registry = PersonaRegistry()
        _registry.initialize()
    return _registry


def get_persona(persona_id: str) -> Optional[Persona]:
    """Merr persona sipas ID"""
    return get_persona_registry().get(persona_id)


def list_personas() -> List[Dict[str, Any]]:
    """Liston personat"""
    return get_persona_registry().list_personas()


def route_to_persona(query: str) -> Persona:
    """Gjej personën për pyetjen"""
    return get_persona_registry().route(query)


__all__ = [
    "PersonaMode",
    "PersonaTone",
    "PersonaStyle",
    "PersonaCapability",
    "Persona",
    "PersonaRegistry",
    "BUILT_IN_PERSONAS",
    "get_persona_registry",
    "get_persona",
    "list_personas",
    "route_to_persona",
]

