"""
RESPONSE ORCHESTRATOR V5 - PRODUCTION BRAIN
============================================
Minimal, i shpejtë, 100% lokal, pa API të jashtme me pagesë.

Features:
- Fast-path conversational (RealAnswerEngine direkt)
- Multilingual hooks (pa Google/DeepL - 100% lokal)
- Timeout për ekspertët
- Përdor persona/labs/modules vetëm kur ka kuptim
- Zero external paid APIs
- MEGA LAYER ENGINE: ~2.8 MILIARD KOMBINIME
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

# Import Mega Layer Engine
try:
    from mega_layer_engine import LayerActivation, get_mega_layer_engine
    from mega_layer_engine import MegaLayerEngine as MegaLayerEngineClass

    MEGA_LAYERS_AVAILABLE = True
except ImportError:
    MEGA_LAYERS_AVAILABLE = False
    MegaLayerEngineClass = None
    LayerActivation = None

# Import Knowledge Seeds
try:
    from knowledge_seeds.core_knowledge import KnowledgeSeed, find_matching_seed, seed_stats

    KNOWLEDGE_SEEDS_AVAILABLE = True
except ImportError:
    KNOWLEDGE_SEEDS_AVAILABLE = False
    find_matching_seed = None
    seed_stats = None
    KnowledgeSeed = None

# Import Ollama FAST Engine (LINJA OPTIKE - zero overhead)
try:
    from ollama_fast_engine import OllamaFastEngine, get_fast_engine

    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    OllamaFastEngine = None
    get_fast_engine = None

# Import Albanian Dictionary
try:
    from albanian_dictionary import ALL_ALBANIAN_WORDS, KLOUD_TERMS, SENTENCE_PATTERNS, detect_albanian, get_albanian_response

    ALBANIAN_DICT_AVAILABLE = True
except ImportError:
    ALBANIAN_DICT_AVAILABLE = False
    get_albanian_response = None
    detect_albanian = None
    ALL_ALBANIAN_WORDS = {}

# SmartAPIRouter removed - Orchestrator handles all routing

logger = logging.getLogger("orchestrator_v5")


# ─────────────────────────────────────────────────────────
#  ENUMS & DATA CLASSES
# ─────────────────────────────────────────────────────────


class QueryCategory(str, Enum):
    FINANCIAL = "financial"
    PHILOSOPHICAL = "philosophical"
    TECHNICAL = "technical"
    OPERATIONAL = "operational"
    SCIENTIFIC = "scientific"
    NARRATIVE = "narrative"
    PERSONAL = "personal"
    ANALYTICAL = "analytical"
    EXPLORATORY = "exploratory"
    BINARY = "binary"
    CONVERSATIONAL = "conversational"  # Për chat normal


@dataclass
class ExpertConsultation:
    expert_type: str
    expert_name: str
    expert_id: str
    query_sent: str
    response: str
    confidence: float
    relevance_score: float
    processing_time_ms: float
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class OrchestratedResponse:
    query: str
    query_category: QueryCategory
    understanding: Dict[str, Any]
    consulted_experts: List[ExpertConsultation]
    fused_answer: str
    sources_cited: List[str]
    confidence: float
    narrative_quality: float
    learning_record: Dict[str, Any]
    language: str = "sq"
    mega_layers: Optional[Dict[str, Any]] = None  # Mega Layer results
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ─────────────────────────────────────────────────────────
#  LANGUAGE LAYER - 100% LOKAL (PA API TË JASHTME)
# ─────────────────────────────────────────────────────────


class LocalLanguageLayer:
    """
    Multilingual Layer - 100% lokal, pa pagesë, pa cloud.

    Përdor langdetect për detektim dhe përgjigje lokale për çdo gjuhë.
    NUK përdor Google Translate, DeepL, apo çdo API të jashtme.
    """

    def __init__(self):
        self._langdetect_available = False
        try:
            from langdetect import detect as _detect

            self._detect = _detect
            self._langdetect_available = True
        except ImportError:
            self._detect = None

    def detect_language(self, text: str) -> str:
        """Detekto gjuhën - 100% lokal."""
        if not text or len(text.strip()) < 3:
            return "sq"  # Default: Shqip

        # Provo langdetect (lokal, pa pagesë)
        if self._langdetect_available and self._detect:
            try:
                return self._detect(text)
            except Exception:
                pass

        # Fallback: pattern matching lokal
        text_lower = text.lower()

        # Shqip
        sq_markers = [
            "ë",
            "ç",
            "sh",
            "zh",
            "gj",
            "nj",
            "xh",
            "rr",
            "th",
            "dh",
            "është",
            "jam",
            "je",
            "jemi",
            "janë",
            "kam",
            "kemi",
            "kanë",
            "përshëndetje",
            "mirëdita",
            "çfarë",
            "pse",
            "kush",
            "ku",
            "kur",
        ]
        if any(m in text_lower for m in sq_markers):
            return "sq"

        # Gjermanisht
        de_markers = [
            "ü",
            "ö",
            "ä",
            "ß",
            "ich",
            "du",
            "ist",
            "sind",
            "haben",
            "werden",
            "nicht",
            "und",
            "oder",
            "aber",
            "können",
            "möchten",
            "bitte",
        ]
        if any(m in text_lower for m in de_markers):
            return "de"

        # Frëngjisht
        fr_markers = [
            "é",
            "è",
            "ê",
            "ç",
            "je",
            "tu",
            "vous",
            "nous",
            "est",
            "sont",
            "avoir",
            "être",
            "pourquoi",
            "comment",
            "bonjour",
            "merci",
        ]
        if any(m in text_lower for m in fr_markers):
            return "fr"

        # Spanjisht
        es_markers = ["ñ", "¿", "¡", "soy", "eres", "es", "somos", "están", "hola", "gracias", "por qué", "cómo", "cuándo", "dónde", "qué"]
        if any(m in text_lower for m in es_markers):
            return "es"

        # Italisht
        it_markers = [
            "sono",
            "sei",
            "siamo",
            "sono",
            "ciao",
            "grazie",
            "perché",
            "come",
            "quando",
            "dove",
            "cosa",
            "buongiorno",
            "buonasera",
        ]
        if any(m in text_lower for m in it_markers):
            return "it"

        # Greek / Greeklish (Greek written in Latin script)
        el_markers = [
            "kalimera",
            "kalispera",
            "yassou",
            "yassas",
            "geia",
            "geia sou",
            "geia sas",
            "efharisto",
            "parakalo",
            "nai",
            "ohi",
            "pos",
            "pou",
            "pote",
            "giati",
            "poso",
            "thelo",
            "echo",
            "ime",
            "ise",
            "einai",
            "den",
            "tora",
            "simera",
            "avrio",
            "ti kaneis",
            "ti kanis",
            "ola kala",
            "signomi",
            "milate",
            "ellenika",
            "mporo",
            "mazi",
            "matho",
            "mou",
            "sou",
            "mas",
            "sas",
            "kalo",
            "kala",
            "ti",
            "na",
            "me",
            "kai",
            "sto",
            "sta",
            "tous",
            "tis",
            "tha",
            "oxi",
        ]
        if any(m in text_lower for m in el_markers):
            return "el"

        # Turkish
        tr_markers = ["merhaba", "selam", "teşekkürler", "evet", "hayır", "nasıl", "neden", "nerede", "günaydın", "iyi akşamlar", "lutfen"]
        if any(m in text_lower for m in tr_markers):
            return "tr"

        # Default: Anglisht
        return "en"

    async def to_internal(self, text: str, lang: str) -> str:
        """
        Konverto në gjuhën interne - NUK përkthejmë!

        Thjesht e ruajmë query-n origjinale dhe e procesojmë direkt.
        Sistemi ynë kupton shumë gjuhë pa përkthim.
        """
        return text  # Proceso direkt - pa përkthim!

    async def from_internal(self, text: str, lang: str) -> str:
        """
        Konverto nga gjuha interne - NUK përkthejmë!

        Përgjigjet gjenerohen direkt në gjuhën e kërkuar.
        """
        return text  # Kthu direkt - pa përkthim!

    def get_greeting(self, lang: str) -> str:
        """Përshëndetje në gjuhë të ndryshme."""
        greetings = {
            "sq": "Përshëndetje! Jam Curiosity Ocean. Si mund të të ndihmoj?",
            "en": "Hello! I'm Curiosity Ocean. How can I help you?",
            "de": "Hallo! Ich bin Curiosity Ocean. Wie kann ich Ihnen helfen?",
            "fr": "Bonjour! Je suis Curiosity Ocean. Comment puis-je vous aider?",
            "es": "¡Hola! Soy Curiosity Ocean. ¿Cómo puedo ayudarte?",
            "it": "Ciao! Sono Curiosity Ocean. Come posso aiutarti?",
            "el": "Γεια σας! Είμαι το Curiosity Ocean. Πώς μπορώ να σας βοηθήσω;",
            "tr": "Merhaba! Ben Curiosity Ocean. Size nasıl yardımcı olabilirim?",
            "ru": "Привет! Я Curiosity Ocean. Чем могу помочь?",
        }
        return greetings.get(lang, greetings["en"])

    def get_fallback(self, lang: str, query: str) -> str:
        """Mesazh fallback në gjuhë të ndryshme."""
        fallbacks = {
            "sq": f'Faleminderit për pyetjen! Po e analizoj: "{query}"',
            "en": f'Thanks for your question! I\'m analyzing: "{query}"',
            "de": f'Danke für Ihre Frage! Ich analysiere: "{query}"',
            "fr": f'Merci pour votre question! J\'analyse: "{query}"',
            "es": f'¡Gracias por tu pregunta! Estoy analizando: "{query}"',
            "it": f'Grazie per la tua domanda! Sto analizzando: "{query}"',
            "el": f'Ευχαριστώ για την ερώτηση! Αναλύω: "{query}"',
            "tr": f'Soru için teşekkürler! Analiz ediyorum: "{query}"',
            "ru": f'Спасибо за вопрос! Анализирую: "{query}"',
        }
        return fallbacks.get(lang, fallbacks["en"])


# ═══════════════════════════════════════════════════════════════════════════════
#  LANGUAGE REQUEST DETECTOR - Detects explicit language commands
# ═══════════════════════════════════════════════════════════════════════════════

# Language request patterns - maps phrases to ISO language codes
LANGUAGE_REQUEST_PATTERNS = {
    # Albanian requests
    "në gjermanisht": "de",
    "në anglisht": "en",
    "në italisht": "it",
    "në frëngjisht": "fr",
    "në spanjisht": "es",
    "në greqisht": "el",
    "në turqisht": "tr",
    "në rusisht": "ru",
    "në shqip": "sq",
    "përgjigju në gjermanisht": "de",
    "përgjigju në anglisht": "en",
    "përgjigju në italisht": "it",
    "përgjigju në frëngjisht": "fr",
    "përgjigju në greqisht": "el",
    "përgjigju në shqip": "sq",
    # English requests
    "in german": "de",
    "in english": "en",
    "in italian": "it",
    "in french": "fr",
    "in spanish": "es",
    "in greek": "el",
    "in turkish": "tr",
    "in russian": "ru",
    "in albanian": "sq",
    "respond in german": "de",
    "respond in english": "en",
    "reply in german": "de",
    "answer in german": "de",
    # German requests
    "auf deutsch": "de",
    "auf englisch": "en",
    "auf italienisch": "it",
    "auf französisch": "fr",
    "auf spanisch": "es",
    "antworte auf deutsch": "de",
    "antworte auf englisch": "en",
    # Italian requests
    "in italiano": "it",
    "in inglese": "en",
    "in tedesco": "de",
    "rispondi in italiano": "it",
    "rispondi in inglese": "en",
    # French requests
    "en français": "fr",
    "en anglais": "en",
    "en allemand": "de",
    "réponds en français": "fr",
    "réponds en anglais": "en",
    # Greek requests (romanized)
    "sta ellinika": "el",
    "sta agglika": "en",
    "sta germanika": "de",
    "apantise sta ellinika": "el",
    "apantise sta agglika": "en",
    "in greek please": "el",
    "se ellinika": "el",
}


# ─────────────────────────────────────────────────────────
#  EXPERT REGISTRY - MINIMAL, PRODUCTION-FRIENDLY
# ─────────────────────────────────────────────────────────


class ExpertRegistryV5:
    """
    Regjistri minimal i ekspertëve.
    Vetëm 1 persona + 1 lab + 1 modul për kategori.
    """

    def __init__(self):
        self.personas = {
            "smart_human": {"id": "ps_009", "domain": "personal"},
            "systems_architect": {"id": "ps_004", "domain": "technical"},
            "business_analyst": {"id": "ps_008", "domain": "financial"},
            "agi_analyst": {"id": "ps_007", "domain": "philosophical"},
            "scientist": {"id": "ps_010", "domain": "scientific"},
        }
        self.labs = {
            "Budapest_Data": {"id": "lab_data", "domain": "analytical"},
            "Vienna_Neuroscience": {"id": "lab_neuro", "domain": "scientific"},
            "Pristina_Finance": {"id": "lab_fin", "domain": "financial"},
            "Tirana_Tech": {"id": "lab_tech", "domain": "technical"},
        }
        self.modules = {
            "Albi": {"id": "mod_albi", "domain": "financial"},
            "Jona": {"id": "mod_jona", "domain": "philosophical"},
            "Alba": {"id": "mod_alba", "domain": "technical"},
        }

    def pick_minimal_experts(self, category: QueryCategory) -> Dict[str, List[Dict[str, Any]]]:
        """Zgjidh maksimum 1 persona, 1 lab, 1 modul për kategorinë."""
        res = {"personas": [], "labs": [], "modules": []}

        category_value = category.value if hasattr(category, "value") else str(category)

        # Zgjidh 1 persona
        for name, meta in self.personas.items():
            if meta["domain"] == category_value:
                res["personas"].append({"name": name, **meta})
                break

        # Zgjidh 1 lab
        for name, meta in self.labs.items():
            if meta["domain"] == category_value:
                res["labs"].append({"name": name, **meta})
                break

        # Zgjidh 1 modul
        for name, meta in self.modules.items():
            if meta["domain"] == category_value:
                res["modules"].append({"name": name, **meta})
                break

        return res


# ─────────────────────────────────────────────────────────
#  QUERY UNDERSTANDING - LIGHTWEIGHT
# ─────────────────────────────────────────────────────────


class QueryUnderstandingV5:
    """Kuptimi i shpejtë i query-ve."""

    @staticmethod
    def categorize(query: str) -> QueryCategory:
        """Kategorizim i shpejtë bazuar në fjalë kyçe."""
        q = query.lower()

        # Përshëndetje/Chat normal
        greetings = ["hello", "hi", "hey", "përshëndetje", "mirëdita", "çkemi", "tungjatjeta", "si je", "ciao", "hola", "bonjour", "hallo"]
        if any(g in q for g in greetings):
            return QueryCategory.CONVERSATIONAL

        # Financiare
        if any(w in q for w in ["invest", "money", "profit", "revenue", "market", "stock", "biznes", "para", "fitim", "treg"]):
            return QueryCategory.FINANCIAL

        # Filozofike
        if any(w in q for w in ["agi", "conscious", "mind", "meaning", "philosophy", "ndërgjegje", "vetëdije", "kuptim", "filozofi"]):
            return QueryCategory.PHILOSOPHICAL

        # Teknike
        if any(w in q for w in ["api", "deploy", "server", "database", "kubernetes", "infrastrukturë", "kod", "code", "program"]):
            return QueryCategory.TECHNICAL

        # Operacionale
        if any(w in q for w in ["process", "workflow", "operacion", "prodhim", "cycle"]):
            return QueryCategory.OPERATIONAL

        # Shkencore
        if any(w in q for w in ["research", "experiment", "data", "study", "teori", "shkencë", "science"]):
            return QueryCategory.SCIENTIFIC

        # Narrative
        if any(w in q for w in ["story", "tregim", "explain", "shpjego", "histori"]):
            return QueryCategory.NARRATIVE

        # Personale
        if any(w in q for w in ["help", "ndihmë", "ndihme", "mendim", "këshillë", "advice"]):
            return QueryCategory.PERSONAL

        # Analitike
        if any(w in q for w in ["analyze", "analizo", "statistikë", "trend", "pattern"]):
            return QueryCategory.ANALYTICAL

        # Binare
        if any(w in q for w in ["xor", "and", "or", "binary", "bits", "binar"]):
            return QueryCategory.BINARY

        return QueryCategory.EXPLORATORY

    @staticmethod
    def understand(query: str, context: Optional[List[str]] = None) -> Dict[str, Any]:
        """Kuptimi i plotë i query-t."""
        return {
            "query": query,
            "category": QueryUnderstandingV5.categorize(query),
            "context_len": len(context or []),
            "word_count": len(query.split()),
            "complexity": "simple" if len(query.split()) < 15 else "medium",
        }

    @staticmethod
    def needs_experts(category: QueryCategory) -> bool:
        """A duhen ekspertë për këtë kategori?"""
        # Për chat normal dhe eksplorues, NUK duhen ekspertë
        if category in {QueryCategory.CONVERSATIONAL, QueryCategory.EXPLORATORY}:
            return False

        # Për pyetje komplekse, mund të duhen
        return category in {QueryCategory.FINANCIAL, QueryCategory.TECHNICAL, QueryCategory.SCIENTIFIC, QueryCategory.ANALYTICAL}


# ─────────────────────────────────────────────────────────
#  RESPONSE FUSION - MINIMAL
# ─────────────────────────────────────────────────────────


class FusionEngineV5:
    """Bashko përgjigjet nga burime të ndryshme."""

    def fuse(self, base_answer: str, expert_responses: List[ExpertConsultation]) -> Tuple[str, float]:
        """Bashko përgjigjen bazë me inputet e ekspertëve."""
        if not expert_responses:
            return base_answer, 0.9

        # Filtro vetëm përgjigjet me konfidencë të lartë
        valid_extras = []
        for c in expert_responses:
            if c.confidence > 0.6 and c.relevance_score > 0.5:
                valid_extras.append(c.response)

        if not valid_extras:
            return base_answer, 0.9

        # Bashko (maksimum 2 shtesa)
        fused = base_answer + "\n\n📊 **Shtesë nga sisteme të tjera:**\n"
        for e in valid_extras[:2]:
            fused += f"• {e.strip()}\n"

        quality = min(1.0, 0.8 + 0.1 * min(len(valid_extras), 2))
        return fused, quality


# ─────────────────────────────────────────────────────────
#  MAIN ORCHESTRATOR V5
# ─────────────────────────────────────────────────────────


class ResponseOrchestratorV5:
    """
    Curiosity Ocean v5 – Production Brain

    100% LOKAL - PA API TË JASHTME ME PAGESË

    Features:
    - Fast conversational path (RealAnswerEngine)
    - Minimal experts (1 persona, 1 lab, 1 module) - vetëm kur duhen
    - Multilingual hooks (pa Google/DeepL)
    - Timeouts për ekspertët
    - Zero external paid APIs
    - MEGA LAYER ENGINE: ~2.8 MILIARD KOMBINIME UNIKE
    """

    def __init__(
        self,
        real_answer_engine=None,
        language_layer: LocalLanguageLayer = None,
        expert_registry: ExpertRegistryV5 = None,
        fusion_engine: FusionEngineV5 = None,
        expert_timeout_ms: int = 500,
    ):
        self.real_answer_engine = None  # DISABLED - CLX only
        self.language_layer = language_layer or LocalLanguageLayer()
        self.registry = None  # DISABLED - no experts
        self.fusion = None  # DISABLED - no fusion
        self.expert_timeout_ms = expert_timeout_ms
        self.learning_history: List[Dict[str, Any]] = []

        # DISABLED - Mega Layer Engine creates chaos
        self.mega_layer_engine = None

        # Initialize CLX FAST Engine - LINJA OPTIKE!
        self.ollama_engine: Optional[Any] = None
        if OLLAMA_AVAILABLE:
            try:
                self.ollama_engine = get_fast_engine()
                logger.info("⚡ CLXFastEngine initialized - LINJA OPTIKE ACTIVE")
            except Exception as e:
                logger.error(f"❌ ClxIEngine FAILED: {e}")

    def _detect_language_request(self, query: str) -> Optional[str]:
        """
        Detect explicit language request in query.

        Examples:
          - "Përgjigju në gjermanisht: ..." → returns "de"
          - "Respond in French: ..." → returns "fr"
          - "Antworte auf Englisch: ..." → returns "en"

        Returns:
            ISO language code if explicit request found, None otherwise.
        """
        q_lower = query.lower()

        # Check all patterns (longest match first for accuracy)
        sorted_patterns = sorted(LANGUAGE_REQUEST_PATTERNS.keys(), key=len, reverse=True)

        for pattern in sorted_patterns:
            if pattern in q_lower:
                lang_code = LANGUAGE_REQUEST_PATTERNS[pattern]
                logger.info(f"🌍 Language request detected: '{pattern}' → {lang_code}")
                return lang_code

        return None

    async def orchestrate(
        self,
        query: str,
        conversation_context: Optional[List[str]] = None,
        mode: str = "conversational",
    ) -> OrchestratedResponse:
        """
        Orkestro përgjigjen.

        mode:
          - "conversational": fast path - RealAnswerEngine direkt (DEFAULT)
          - "deep": përdor edhe ekspertë aktivikisht
        """
        conversation_context = conversation_context or []

        # ═══════════════════════════════════════════════════════════════════════
        # 0) LANGUAGE REQUEST DETECTION - HIGHEST PRIORITY
        # Detect if user explicitly requests a specific response language
        # ═══════════════════════════════════════════════════════════════════════
        requested_language = self._detect_language_request(query)

        # 1) Language detection (100% lokal)
        detected_lang = self.language_layer.detect_language(query)

        # Use requested language if specified, otherwise use detected
        lang = requested_language if requested_language else detected_lang

        # 2) Query understanding
        understanding = QueryUnderstandingV5.understand(query, conversation_context)
        category: QueryCategory = understanding["category"]

        # 3) CLX përgjigjet - kaq
        base_text = ""
        sources = []
        base_confidence = 0.9
        used_ollama = False
        used_albanian_dict = False

        # ═══════════════════════════════════════════════════════════════════════
        # ALBANIAN DICTIONARY - FAST LOCAL RESPONSES (para CLX)
        # ═══════════════════════════════════════════════════════════════════════
        if lang == "sq" and ALBANIAN_DICT_AVAILABLE and get_albanian_response is not None:
            try:
                albanian_response = get_albanian_response(query)
                if albanian_response:
                    base_text = albanian_response
                    sources = ["albanian_dictionary:local"]
                    base_confidence = 0.95  # High confidence for local dictionary
                    used_albanian_dict = True
                    logger.info(f"🇦🇱 Albanian Dictionary responded locally (no CLX needed)")
            except Exception as e:
                logger.warning(f"Albanian dictionary error: {e}")

        # ═══════════════════════════════════════════════════════════════════════
        # LANGUAGE OVERRIDE for CLX - inject language instruction
        # ═══════════════════════════════════════════════════════════════════════
        language_override_prompt = None
        lang_names = {
            "de": "German (Deutsch)",
            "en": "English",
            "it": "Italian (Italiano)",
            "fr": "French (Français)",
            "es": "Spanish (Español)",
            "el": "Greek (Ελληνικά)",
            "tr": "Turkish (Türkçe)",
            "ru": "Russian (Русский)",
            "sq": "Albanian (Shqip)",
            "pt": "Portuguese",
            "nl": "Dutch",
            "pl": "Polish",
            "ja": "Japanese",
            "zh": "Chinese",
        }

        # Apply language instruction for both explicit requests AND auto-detected non-English
        if requested_language:
            lang_name = lang_names.get(requested_language, requested_language.upper())
            language_override_prompt = f"CRITICAL: Respond ONLY in {lang_name}. Do not use any other language."
            logger.info(f"🌍 Language override active: {lang_name}")
        elif lang != "en":
            # Auto-detected non-English language - guide CLX to respond in detected language
            lang_name = lang_names.get(lang, lang.upper())
            language_override_prompt = f"The user is writing in {lang_name}. Respond naturally in {lang_name}. If you cannot respond in that language, respond in English."
            logger.info(f"🌍 Auto-detected language: {lang_name}")

        # OLLAMA FAST - Linja Optike (zero overhead)
        # Skip if Albanian dictionary already provided a response
        if self.ollama_engine and not used_albanian_dict:
            try:
                # Build enhanced query with language instruction
                enhanced_query = query
                if language_override_prompt:
                    enhanced_query = f"[{language_override_prompt}]\n\n{query}"

                ollama_response = await self.ollama_engine.generate(enhanced_query)
                if ollama_response.success and ollama_response.content:
                    base_text = ollama_response.content
                    sources = [f"clx:{ollama_response.model}"]
                    base_confidence = 0.90
                    used_ollama = True
                    logger.info(f"⚡ CLX FAST [{ollama_response.model}] ({ollama_response.duration_ms:.0f}ms)")
            except Exception as e:
                logger.error(f"CLX error: {e}")
                base_text = f"CLX nuk u përgjigj: {e}"
                sources = ["clx:error"]

        # DISABLED - Ekspertë, Fusion, MegaLayers - vetëm CLX!
        consulted: List[ExpertConsultation] = []
        fused_answer = base_text  # Direct from CLX
        quality = 0.9

        # 6) Ndërto përgjigjen finale
        response = OrchestratedResponse(
            query=query,
            query_category=category,
            understanding=understanding,
            consulted_experts=[],
            fused_answer=fused_answer,
            sources_cited=sources,
            confidence=base_confidence,
            narrative_quality=quality,
            language=lang,
            mega_layers=None,
            learning_record={
                "mode": mode,
                "lang": lang,
                "experts_used": 0,
                "mega_layers_active": False,
                "combinations_used": 0,
                "albanian_dict_used": used_albanian_dict,
            },
        )

        # 7) Learning history
        self.learning_history.append(
            {
                "query": query,
                "category": category.value,
                "mode": mode,
                "lang": lang,
                "albanian_dict_used": used_albanian_dict,
                "timestamp": response.timestamp,
            }
        )

        return response

    async def _consult_experts_parallel(
        self,
        query: str,
        experts: Dict[str, List[Dict[str, Any]]],
    ) -> List[ExpertConsultation]:
        """Konsulto ekspertët në paralel me timeout."""
        tasks = []

        for p in experts.get("personas", []):
            tasks.append(self._call_expert("persona", p["name"], p["id"], query))

        for l in experts.get("labs", []):
            tasks.append(self._call_expert("lab", l["name"], l["id"], query))

        for m in experts.get("modules", []):
            tasks.append(self._call_expert("module", m["name"], m["id"], query))

        if not tasks:
            return []

        # Timeout
        timeout = self.expert_timeout_ms / 1000.0
        try:
            done, pending = await asyncio.wait(tasks, timeout=timeout)

            # Anulo tasks që nuk përfunduan
            for p in pending:
                p.cancel()

            # Mblidh rezultatet
            results: List[ExpertConsultation] = []
            for d in done:
                try:
                    c = d.result()
                    if c is not None:
                        results.append(c)
                except Exception as e:
                    logger.warning(f"Expert call failed: {e}")

            return results
        except Exception as e:
            logger.error(f"Expert consultation error: {e}")
            return []

    async def _call_expert(
        self,
        expert_type: str,
        name: str,
        expert_id: str,
        query: str,
    ) -> Optional[ExpertConsultation]:
        """
        Thirr një ekspert.

        TODO: Lidhe me persona/lab/module të vërtetë.
        Për tani: stub bazë.
        """
        start = datetime.now(timezone.utc)
        try:
            # Simulim i shkurtër (do të zëvendësohet me lidhje reale)
            await asyncio.sleep(0.02)

            # Stub response - zëvendëso me logjikë reale
            response = f"[{expert_type}:{name}] Në zhvillim - struktura gati për lidhje."
            confidence = 0.5
            relevance = 0.4

            elapsed_ms = (datetime.now(timezone.utc) - start).total_seconds() * 1000.0

            return ExpertConsultation(
                expert_type=expert_type,
                expert_name=name,
                expert_id=expert_id,
                query_sent=query,
                response=response,
                confidence=confidence,
                relevance_score=relevance,
                processing_time_ms=elapsed_ms,
            )
        except Exception as e:
            logger.warning(f"Error calling expert {expert_type}:{name}: {e}")
            return None

    async def quick_answer(self, query: str) -> str:
        """
        Përgjigje e shpejtë - pa ekspertë, pa overhead.
        Ideal për chat normal.
        """
        if self.real_answer_engine:
            try:
                result = await self.real_answer_engine.answer(query)
                return result.answer
            except Exception as e:
                logger.error(f"Quick answer error: {e}")

        lang = self.language_layer.detect_language(query)
        return self.language_layer.get_fallback(lang, query)

    def get_stats(self) -> Dict[str, Any]:
        """Statistika të orchestrator-it."""
        return {
            "engine_active": self.real_answer_engine is not None,
            "learning_history_count": len(self.learning_history),
            "expert_timeout_ms": self.expert_timeout_ms,
            "version": "v5_production",
        }

    # ═══════════════════════════════════════════════════════════════════════════
    # ALIAS for backwards compatibility with ocean_api.py
    # ═══════════════════════════════════════════════════════════════════════════
    async def process_query_async(self, query: str, conversation_context: Optional[List[str]] = None) -> OrchestratedResponse:
        """Alias for orchestrate() - backwards compatibility."""
        return await self.orchestrate(query, conversation_context, mode="conversational")


# ─────────────────────────────────────────────────────────
#  SINGLETON & FACTORY
# ─────────────────────────────────────────────────────────

_orchestrator: Optional[ResponseOrchestratorV5] = None


def get_orchestrator_v5() -> ResponseOrchestratorV5:
    """Merr instancën singleton të Orchestrator v5."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = ResponseOrchestratorV5()
    return _orchestrator


# ─────────────────────────────────────────────────────────
#  TEST
# ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO)

    async def test():
        print("\n" + "=" * 60)
        print("🧪 ORCHESTRATOR V5 TEST - PRODUCTION BRAIN")
        print("=" * 60)

        orch = get_orchestrator_v5()

        tests = [
            "Përshëndetje!",
            "Hello, how are you?",
            "Sa bëjnë 15 + 27?",
            "What is the date today?",
            "Çfarë është Curiosity Ocean?",
            "Hola, ¿cómo estás?",
            "Bonjour, comment ça va?",
        ]

        for query in tests:
            print(f"\n📝 Query: {query}")
            response = await orch.orchestrate(query)
            print(f"🌐 Language: {response.language}")
            print(f"📊 Category: {response.query_category.value}")
            print(f"📄 Answer: {response.fused_answer[:200]}...")
            print(f"📈 Confidence: {response.confidence:.0%}")

        print("\n" + "=" * 60)
        print("📊 Stats:", orch.get_stats())

    asyncio.run(test())
