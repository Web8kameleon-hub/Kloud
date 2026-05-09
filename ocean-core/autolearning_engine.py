# -*- coding: utf-8 -*-
"""
🧠 KLOUD AUTOLEARNING ENGINE
================================
Sistem i mësimit të vazhdueshëm që:
- Ruan çdo pyetje dhe përgjigje
- Mëson patterns nga përdoruesit
- Përmirëson përgjigjet me kalimin e kohës
- Krijon knowledge base të brendshme
- NUK VARET NGA API TË JASHTME

Author: Kloud Team
Version: 1.0.0
"""

from __future__ import annotations
import os
import hashlib
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from collections import defaultdict
import re
import json  # Needed for legacy file migration and stats output

# Binary storage - CBOR2 primary, JSON fallback
try:
    import cbor2
    HAS_CBOR2 = True
except ImportError:
    HAS_CBOR2 = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =============================================================================
# KNOWLEDGE STORAGE - BINARY (CBOR2)
# =============================================================================

# Binary files - .cbor extension
KNOWLEDGE_FILE = os.path.join(os.path.dirname(__file__), "learned_knowledge.cbor")
PATTERNS_FILE = os.path.join(os.path.dirname(__file__), "learned_patterns.cbor")
FEEDBACK_FILE = os.path.join(os.path.dirname(__file__), "user_feedback.cbor")

# Legacy JSON files for migration
KNOWLEDGE_FILE_JSON = os.path.join(os.path.dirname(__file__), "learned_knowledge.json")
PATTERNS_FILE_JSON = os.path.join(os.path.dirname(__file__), "learned_patterns.json")
FEEDBACK_FILE_JSON = os.path.join(os.path.dirname(__file__), "user_feedback.json")


def _save_cbor(filepath: str, data: Any):
    """Save data to CBOR binary file"""
    if HAS_CBOR2:
        with open(filepath, 'wb') as f:
            cbor2.dump(data, f)
    else:
        # Fallback to JSON
        json_path = filepath.replace('.cbor', '.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


def _load_cbor(filepath: str) -> Any:
    """Load data from CBOR binary file"""
    if HAS_CBOR2 and os.path.exists(filepath):
        with open(filepath, 'rb') as f:
            return cbor2.load(f)
    
    # Try legacy JSON
    json_path = filepath.replace('.cbor', '.json')
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    return None


@dataclass
class LearnedKnowledge:
    """Një njësi e dijes së mësuar"""
    knowledge_id: str
    query: str
    query_hash: str
    response: str
    sources: List[str]
    confidence: float
    times_used: int = 0
    times_helpful: int = 0
    times_not_helpful: int = 0
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    @property
    def helpfulness_score(self) -> float:
        """Llogarit sa e dobishme është kjo dije"""
        total = self.times_helpful + self.times_not_helpful
        if total == 0:
            return 0.5  # Neutral
        return self.times_helpful / total
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class QueryPattern:
    """Pattern i identifikuar në pyetje"""
    pattern_id: str
    pattern_type: str  # greeting, question, command, feedback
    keywords: List[str]
    regex: str
    response_template: str
    times_matched: int = 0
    success_rate: float = 0.5
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    def to_dict(self) -> Dict:
        return asdict(self)


# =============================================================================
# PATTERN DETECTOR
# =============================================================================

class PatternDetector:
    """Detekton patterns në pyetje të përdoruesve - MULTILINGUAL"""
    
    # ═══════════════════════════════════════════════════════════════════════════
    # MULTILINGUAL LANGUAGE DETECTION (Latin Script Support)
    # ═══════════════════════════════════════════════════════════════════════════
    
    # Languages with Latin script (romanized versions included)
    LANGUAGE_MARKERS = {
        # Greek (Latin/Romanized - "Greeklish")
        "el": {
            "greetings": ["kalimera", "kalispera", "yassou", "yassas", "geia", "geia sou", "geia sas", "herete"],
            "words": ["efharisto", "parakalo", "nai", "ohi", "ti", "pos", "pou", "pote", "giati", "poso", 
                     "thelo", "echo", "ime", "ise", "einai", "den", "tora", "simera", "avrio", "hthes",
                     "kala", "poli", "ligo", "megalo", "mikro", "neo", "palio", "omorfo", "kalo", "kako"],
            "phrases": ["ti kaneis", "ti kanis", "ola kala", "den katalaveno", "milate", "ellenika",
                       "signomi", "me lene", "pos se lene", "apo pou eisai"],
            "response": "Γεια σας! Πώς μπορώ να σας βοηθήσω;"  # Greek script response
        },
        # Finnish
        "fi": {
            "greetings": ["moi", "hei", "terve", "huomenta", "paivaa", "iltaa", "moikka", "morjens"],
            "words": ["kiitos", "ole hyva", "kylla", "ei", "mita", "miten", "miksi", "koska", "missa",
                     "haluan", "olen", "olet", "on", "olemme", "hyva", "huono", "iso", "pieni",
                     "telia", "etsi", "olla", "kala", "vesi", "talo", "auto", "koira", "kissa"],
            "phrases": ["mita kuuluu", "kaikki hyvin", "en ymmarra", "puhutko", "suomea", "nimeni on"],
            "response": "Hei! Miten voin auttaa sinua?"
        },
        # German (already in system, but add more Latin markers)
        "de": {
            "greetings": ["hallo", "guten morgen", "guten tag", "guten abend", "gruss gott", "servus", "moin"],
            "words": ["danke", "bitte", "ja", "nein", "was", "wie", "warum", "wann", "wo", "wer",
                     "ich", "du", "er", "sie", "wir", "ihr", "haben", "sein", "werden", "konnen",
                     "gut", "schlecht", "gross", "klein", "neu", "alt", "schon", "schnell"],
            "phrases": ["wie geht", "alles klar", "verstehe nicht", "sprechen sie", "deutsch"],
            "response": "Hallo! Wie kann ich Ihnen helfen?"
        },
        # Italian
        "it": {
            "greetings": ["ciao", "buongiorno", "buonasera", "buonanotte", "salve", "salute"],
            "words": ["grazie", "prego", "si", "no", "cosa", "come", "perche", "quando", "dove", "chi",
                     "io", "tu", "lui", "lei", "noi", "voi", "loro", "avere", "essere", "fare",
                     "bene", "male", "grande", "piccolo", "nuovo", "vecchio", "bello", "brutto"],
            "phrases": ["come stai", "tutto bene", "non capisco", "parli", "italiano"],
            "response": "Ciao! Come posso aiutarti?"
        },
        # Spanish
        "es": {
            "greetings": ["hola", "buenos dias", "buenas tardes", "buenas noches", "saludos"],
            "words": ["gracias", "por favor", "si", "no", "que", "como", "porque", "cuando", "donde", "quien",
                     "yo", "tu", "el", "ella", "nosotros", "ustedes", "ellos", "tener", "ser", "estar",
                     "bien", "mal", "grande", "pequeno", "nuevo", "viejo", "bonito", "feo"],
            "phrases": ["como estas", "todo bien", "no entiendo", "hablas", "espanol"],
            "response": "¡Hola! ¿Cómo puedo ayudarte?"
        },
        # French
        "fr": {
            "greetings": ["bonjour", "bonsoir", "bonne nuit", "salut", "coucou"],
            "words": ["merci", "sil vous plait", "oui", "non", "quoi", "comment", "pourquoi", "quand", "ou", "qui",
                     "je", "tu", "il", "elle", "nous", "vous", "ils", "avoir", "etre", "faire",
                     "bien", "mal", "grand", "petit", "nouveau", "vieux", "beau", "laid"],
            "phrases": ["comment allez", "ca va", "tout va bien", "je ne comprends pas", "parlez", "francais"],
            "response": "Bonjour! Comment puis-je vous aider?"
        },
        # Portuguese
        "pt": {
            "greetings": ["ola", "bom dia", "boa tarde", "boa noite", "oi", "tchau"],
            "words": ["obrigado", "obrigada", "por favor", "sim", "nao", "que", "como", "porque", "quando", "onde",
                     "eu", "tu", "ele", "ela", "nos", "voces", "eles", "ter", "ser", "estar",
                     "bem", "mal", "grande", "pequeno", "novo", "velho", "bonito", "feio"],
            "phrases": ["como vai", "tudo bem", "nao entendo", "fala", "portugues"],
            "response": "Olá! Como posso ajudar?"
        },
        # Turkish
        "tr": {
            "greetings": ["merhaba", "selam", "gunaydin", "iyi aksamlar", "iyi geceler"],
            "words": ["tesekkurler", "lutfen", "evet", "hayir", "ne", "nasil", "neden", "ne zaman", "nerede", "kim",
                     "ben", "sen", "o", "biz", "siz", "onlar", "var", "yok", "iyi", "kotu",
                     "buyuk", "kucuk", "yeni", "eski", "guzel", "cirkin"],
            "phrases": ["nasilsin", "iyiyim", "anlamiyorum", "turkce", "konusur musun"],
            "response": "Merhaba! Size nasıl yardımcı olabilirim?"
        },
        # Russian (Romanized/Translit)
        "ru": {
            "greetings": ["privet", "zdravstvuyte", "dobroe utro", "dobriy den", "dobriy vecher"],
            "words": ["spasibo", "pozhaluysta", "da", "net", "chto", "kak", "pochemu", "kogda", "gde", "kto",
                     "ya", "ty", "on", "ona", "my", "vy", "oni", "est", "horosho", "ploho",
                     "bolshoy", "malenkiy", "noviy", "stariy", "krasiviy"],
            "phrases": ["kak dela", "vse horosho", "ya ne ponimayu", "govorite", "po russki"],
            "response": "Привет! Как я могу вам помочь?"
        },
        # Arabic (Romanized/Arabizi)
        "ar": {
            "greetings": ["marhaba", "ahlan", "salam", "sabah el kheir", "masa el kheir"],
            "words": ["shukran", "afwan", "aiwa", "la", "shu", "kif", "lesh", "wein", "meen", "mata",
                     "ana", "enta", "hiya", "huwa", "nahnu", "antum", "hum", "fi", "mafi"],
            "phrases": ["kifak", "keefak", "kif halak", "ma fahimt", "btahki", "arabi"],
            "response": "مرحبا! كيف يمكنني مساعدتك؟"
        },
        # Japanese (Romanized/Romaji)
        "ja": {
            "greetings": ["konnichiwa", "ohayo", "konbanwa", "oyasumi", "moshi moshi"],
            "words": ["arigato", "sumimasen", "hai", "iie", "nani", "dou", "naze", "itsu", "doko", "dare",
                     "watashi", "anata", "kare", "kanojo", "ii", "warui", "ookii", "chiisai"],
            "phrases": ["genki desu ka", "daijoubu", "wakarimasen", "nihongo", "hanasemasu ka"],
            "response": "こんにちは！何かお手伝いできますか？"
        },
        # Chinese (Romanized/Pinyin)
        "zh": {
            "greetings": ["nihao", "ni hao", "zaoshang hao", "wanshang hao", "zaijian"],
            "words": ["xiexie", "bu keqi", "shi", "bu shi", "shenme", "zenme", "weishenme", "nali", "shui",
                     "wo", "ni", "ta", "women", "nimen", "tamen", "hao", "bu hao", "da", "xiao"],
            "phrases": ["ni hao ma", "hen hao", "bu dong", "zhongwen", "hui shuo ma"],
            "response": "你好！我能帮你什么？"
        },
        # Korean (Romanized)
        "ko": {
            "greetings": ["annyeonghaseyo", "annyeong", "anyong", "jal ga"],
            "words": ["gamsahamnida", "ne", "aniyo", "mwo", "eotteoke", "wae", "eonje", "eodi", "nugu",
                     "na", "neo", "geu", "geunyeo", "uri", "joah", "silheo", "keun", "jageun"],
            "phrases": ["jal jinaeyo", "gwenchanayo", "moreugesseyo", "hangugeo", "hal jul arayo"],
            "response": "안녕하세요! 어떻게 도와드릴까요?"
        },
        # Albanian (already primary, but ensure completeness)
        "sq": {
            "greetings": ["përshëndetje", "tungjatjeta", "mirëdita", "mirëmbrëma", "mirëmëngjes", "ckemi", "cpo ben"],
            "words": ["faleminderit", "ju lutem", "po", "jo", "çfarë", "si", "pse", "kur", "ku", "kush",
                     "unë", "ti", "ai", "ajo", "ne", "ju", "ata", "kam", "jam", "bëj",
                     "mirë", "keq", "i madh", "i vogël", "i ri", "i vjetër", "bukur"],
            "phrases": ["si jeni", "çkemi", "çpo bën", "nuk kuptoj", "shqip", "flas", "shqiptar"],
            "response": "Përshëndetje! Si mund t'ju ndihmoj?"
        },
        # English (default)
        "en": {
            "greetings": ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"],
            "words": ["thanks", "please", "yes", "no", "what", "how", "why", "when", "where", "who",
                     "i", "you", "he", "she", "we", "they", "have", "be", "do",
                     "good", "bad", "big", "small", "new", "old", "beautiful", "ugly"],
            "phrases": ["how are you", "all good", "i dont understand", "do you speak", "english"],
            "response": "Hello! How can I help you?"
        }
    }
    
    # Base patterns - Albanian + English
    BASE_PATTERNS = {
        "greeting": {
            "keywords": ["hello", "hi", "hey", "përshëndetje", "mirëdita", "tungjatjeta", "ç'kemi", "si jeni"],
            "regex": r"^(hello|hi|hey|përshëndetje|mirëdita|tungjatjeta|ç'kemi|si jeni)[\s\?!]*$",
            "response": "Përshëndetje! Si mund t'ju ndihmoj sot?"
        },
        "farewell": {
            "keywords": ["bye", "goodbye", "mirupafshim", "shihemi", "faleminderit"],
            "regex": r"^(bye|goodbye|mirupafshim|shihemi|faleminderit)[\s\?!]*$",
            "response": "Mirupafshim! Ishte kënaqësi të bisedoja me ju."
        },
        "thanks": {
            "keywords": ["thanks", "thank you", "faleminderit", "rrofsh"],
            "regex": r"(thanks|thank you|faleminderit|rrofsh)",
            "response": "Ju lutem! Është kënaqësi t'ju ndihmoj."
        },
        "what_is": {
            "keywords": ["what is", "what's", "çfarë është", "ç'është"],
            "regex": r"(what is|what's|çfarë është|ç'është)\s+(.+)",
            "response": None  # Needs dynamic response
        },
        "how_to": {
            "keywords": ["how to", "how do", "si të", "si mund"],
            "regex": r"(how to|how do|si të|si mund)\s+(.+)",
            "response": None
        },
        "price_query": {
            "keywords": ["price", "cost", "çmim", "sa kushton"],
            "regex": r"(price|cost|çmim|sa kushton|how much)",
            "response": None
        },
        "weather_query": {
            "keywords": ["weather", "mot", "temperatura", "shi"],
            "regex": r"(weather|mot|temperatura|shi|rain|sun)",
            "response": None
        },
        "status_query": {
            "keywords": ["status", "gjendje", "how many", "sa", "count"],
            "regex": r"(status|gjendje|how many|sa|count|active|aktive)",
            "response": None
        },
        "location_query": {
            "keywords": ["where", "ku", "location", "vendndodhje"],
            "regex": r"(where|ku|location|vendndodhje)",
            "response": None
        },
        "identity_query": {
            "keywords": ["who are you", "kush je", "what are you", "çfarë je"],
            "regex": r"(who are you|kush je|what are you|çfarë je)",
            "response": "Jam Curiosity Ocean - sistemi i inteligjencës artificiale i Kloud. Kam 14 persona ekspertësh, 23 laboratorë dhe 61 shtresa alfabetike për të analizuar pyetjet tuaja."
        }
    }
    
    def __init__(self):
        self.custom_patterns: Dict[str, QueryPattern] = {}
        self._load_patterns()
    
    def detect_language(self, text: str) -> Tuple[str, float]:
        """
        Detect language from text - supports Latin script variants.
        Returns: (language_code, confidence_score)
        """
        text_lower = text.lower().strip()
        words = text_lower.split()
        
        scores = {}
        
        for lang_code, config in self.LANGUAGE_MARKERS.items():
            score = 0
            
            # Check greetings (highest weight)
            for greeting in config.get("greetings", []):
                if greeting in text_lower:
                    score += 3
            
            # Check words
            for word in config.get("words", []):
                if word in words or word in text_lower:
                    score += 1
            
            # Check phrases (high weight)
            for phrase in config.get("phrases", []):
                if phrase in text_lower:
                    score += 2
            
            if score > 0:
                scores[lang_code] = score
        
        if scores:
            best_lang = max(scores, key=scores.get)
            max_score = scores[best_lang]
            confidence = min(max_score / 5.0, 1.0)  # Normalize to 0-1
            return (best_lang, confidence)
        
        return ("en", 0.3)  # Default to English with low confidence
    
    def get_language_greeting(self, lang_code: str) -> str:
        """Get native greeting for detected language."""
        if lang_code in self.LANGUAGE_MARKERS:
            return self.LANGUAGE_MARKERS[lang_code].get("response", "Hello!")
        return "Hello! How can I help you?"
    
    def _load_patterns(self):
        """Ngarko patterns e mësuara - CBOR binary"""
        try:
            data = _load_cbor(PATTERNS_FILE)
            if data:
                for p in data.get("patterns", []):
                    pattern = QueryPattern(**p)
                    self.custom_patterns[pattern.pattern_id] = pattern
                logger.info(f"📚 Loaded {len(self.custom_patterns)} custom patterns (CBOR binary)")
        except Exception as e:
            logger.warning(f"Could not load patterns: {e}")
    
    def _save_patterns(self):
        """Ruaj patterns - CBOR binary"""
        try:
            data = {
                "patterns": [p.to_dict() for p in self.custom_patterns.values()],
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "format": "cbor2"
            }
            _save_cbor(PATTERNS_FILE, data)
            logger.debug(f"💾 Saved {len(self.custom_patterns)} patterns (CBOR binary)")
        except Exception as e:
            logger.error(f"Could not save patterns: {e}")
    
    def detect(self, query: str) -> Tuple[Optional[str], Optional[str], Dict]:
        """
        Detekto pattern në pyetje - MULTILINGUAL
        Returns: (pattern_type, response_template, metadata)
        """
        q_lower = query.lower().strip()
        
        # ═══════════════════════════════════════════════════════════════════════
        # STEP 1: Detect language first (supports Latin script variants)
        # ═══════════════════════════════════════════════════════════════════════
        detected_lang, confidence = self.detect_language(query)
        
        # If it's a simple greeting in any language, respond in that language
        if len(q_lower.split()) <= 3:  # Short message, likely greeting
            for lang_code, config in self.LANGUAGE_MARKERS.items():
                for greeting in config.get("greetings", []):
                    if greeting in q_lower or q_lower.startswith(greeting):
                        logger.info(f"🌍 Detected {lang_code} greeting: {greeting}")
                        return ("multilingual_greeting", config["response"], {
                            "language": lang_code,
                            "confidence": confidence,
                            "detected_greeting": greeting
                        })
        
        # ═══════════════════════════════════════════════════════════════════════
        # STEP 2: Check base patterns (Albanian + English)
        # ═══════════════════════════════════════════════════════════════════════
        for pattern_type, config in self.BASE_PATTERNS.items():
            # Check keywords
            if any(kw in q_lower for kw in config["keywords"]):
                # Try regex match
                match = re.search(config["regex"], q_lower, re.IGNORECASE)
                if match:
                    return (pattern_type, config["response"], {
                        "match": match.groups(),
                        "language": detected_lang,
                        "confidence": confidence
                    })
        
        # ═══════════════════════════════════════════════════════════════════════
        # STEP 3: Check custom patterns
        # ═══════════════════════════════════════════════════════════════════════
        for pattern in self.custom_patterns.values():
            if any(kw in q_lower for kw in pattern.keywords):
                pattern.times_matched += 1
                self._save_patterns()
                return (pattern.pattern_type, pattern.response_template, {
                    "language": detected_lang,
                    "confidence": confidence
                })
        
        # Return detected language even if no pattern matched
        return (None, None, {"language": detected_lang, "confidence": confidence})
    
    def learn_pattern(self, query: str, response: str, pattern_type: str) -> QueryPattern:
        """Mëso pattern të ri"""
        # Extract keywords
        words = query.lower().split()
        keywords = [w for w in words if len(w) > 3][:5]
        
        pattern_id = f"custom_{hashlib.md5(query.encode()).hexdigest()[:8]}"
        
        pattern = QueryPattern(
            pattern_id=pattern_id,
            pattern_type=pattern_type,
            keywords=keywords,
            regex=re.escape(query.lower()),
            response_template=response,
            times_matched=1
        )
        
        self.custom_patterns[pattern_id] = pattern
        self._save_patterns()
        
        logger.info(f"📝 Learned new pattern: {pattern_type}")
        return pattern


# =============================================================================
# KNOWLEDGE ACCUMULATOR
# =============================================================================

class KnowledgeAccumulator:
    """Akumulon dhe organizon dijet e mësuara"""
    
    def __init__(self):
        self.knowledge_base: Dict[str, LearnedKnowledge] = {}
        self.query_cache: Dict[str, str] = {}  # query_hash -> knowledge_id
        self._load_knowledge()
    
    def _load_knowledge(self):
        """Ngarko dijet e mësuara - CBOR binary"""
        try:
            data = _load_cbor(KNOWLEDGE_FILE)
            if data:
                for k in data.get("knowledge", []):
                    knowledge = LearnedKnowledge(**k)
                    self.knowledge_base[knowledge.knowledge_id] = knowledge
                    self.query_cache[knowledge.query_hash] = knowledge.knowledge_id
                logger.info(f"📚 Loaded {len(self.knowledge_base)} knowledge entries (CBOR binary)")
        except Exception as e:
            logger.warning(f"Could not load knowledge: {e}")
    
    def _save_knowledge(self):
        """Ruaj dijet - CBOR binary"""
        try:
            data = {
                "knowledge": [k.to_dict() for k in self.knowledge_base.values()],
                "total_entries": len(self.knowledge_base),
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "format": "cbor2"
            }
            _save_cbor(KNOWLEDGE_FILE, data)
            logger.debug(f"💾 Saved {len(self.knowledge_base)} knowledge entries (CBOR binary)")
        except Exception as e:
            logger.error(f"Could not save knowledge: {e}")
    
    def _hash_query(self, query: str) -> str:
        """Krijo hash për pyetje"""
        normalized = query.lower().strip()
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def find_similar(self, query: str) -> Optional[LearnedKnowledge]:
        """Gjej dije të ngjashme"""
        query_hash = self._hash_query(query)
        
        # Exact match
        if query_hash in self.query_cache:
            knowledge_id = self.query_cache[query_hash]
            knowledge = self.knowledge_base.get(knowledge_id)
            if knowledge:
                knowledge.times_used += 1
                self._save_knowledge()
                return knowledge
        
        # Fuzzy match - check if keywords match
        q_words = set(query.lower().split())
        best_match = None
        best_score = 0
        
        for knowledge in self.knowledge_base.values():
            k_words = set(knowledge.query.lower().split())
            overlap = len(q_words & k_words)
            score = overlap / max(len(q_words), len(k_words))
            
            if score > 0.7 and score > best_score:
                best_score = score
                best_match = knowledge
        
        if best_match:
            best_match.times_used += 1
            self._save_knowledge()
            
        return best_match
    
    def learn(self, query: str, response: str, sources: List[str], confidence: float) -> LearnedKnowledge:
        """Mëso nga një pyetje/përgjigje"""
        query_hash = self._hash_query(query)
        
        # Check if already exists
        if query_hash in self.query_cache:
            knowledge_id = self.query_cache[query_hash]
            knowledge = self.knowledge_base.get(knowledge_id)
            if knowledge:
                # Update existing
                knowledge.times_used += 1
                knowledge.updated_at = datetime.now(timezone.utc).isoformat()
                self._save_knowledge()
                return knowledge
        
        # Create new
        knowledge_id = f"know_{hashlib.md5(f'{query}{datetime.now()}'.encode()).hexdigest()[:12]}"
        
        knowledge = LearnedKnowledge(
            knowledge_id=knowledge_id,
            query=query,
            query_hash=query_hash,
            response=response,
            sources=sources,
            confidence=confidence,
            times_used=1
        )
        
        self.knowledge_base[knowledge_id] = knowledge
        self.query_cache[query_hash] = knowledge_id
        self._save_knowledge()
        
        logger.info(f"🧠 Learned new knowledge: {query[:50]}...")
        return knowledge
    
    def feedback(self, knowledge_id: str, helpful: bool):
        """Regjistro feedback për dije"""
        if knowledge_id in self.knowledge_base:
            knowledge = self.knowledge_base[knowledge_id]
            if helpful:
                knowledge.times_helpful += 1
            else:
                knowledge.times_not_helpful += 1
            knowledge.updated_at = datetime.now(timezone.utc).isoformat()
            self._save_knowledge()
    
    def get_stats(self) -> Dict:
        """Merr statistikat"""
        total = len(self.knowledge_base)
        total_uses = sum(k.times_used for k in self.knowledge_base.values())
        avg_helpfulness = sum(k.helpfulness_score for k in self.knowledge_base.values()) / max(total, 1)
        
        return {
            "total_knowledge_entries": total,
            "total_times_used": total_uses,
            "average_helpfulness": round(avg_helpfulness, 2),
            "top_queries": sorted(
                [(k.query, k.times_used) for k in self.knowledge_base.values()],
                key=lambda x: x[1],
                reverse=True
            )[:10]
        }


# =============================================================================
# AUTOLEARNING ENGINE
# =============================================================================

class AutolearningEngine:
    """
    🧠 MOTORI KRYESOR I MËSIMIT TË VAZHDUESHËM
    
    Funksionet:
    - Detekton patterns në pyetje
    - Ruan çdo pyetje/përgjigje
    - Rikuperon përgjigje nga knowledge base
    - Përmirëson me kalimin e kohës
    """
    
    def __init__(self):
        self.pattern_detector = PatternDetector()
        self.knowledge_accumulator = KnowledgeAccumulator()
        self.session_queries: List[Dict] = []
        
        logger.info("🧠 AutolearningEngine initialized")
        logger.info(f"   📚 Knowledge base: {len(self.knowledge_accumulator.knowledge_base)} entries")
        logger.info(f"   🔍 Custom patterns: {len(self.pattern_detector.custom_patterns)}")
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Proceso pyetje me autolearning
        Returns dict with: pattern_detected, cached_response, should_learn
        """
        result = {
            "query": query,
            "pattern_type": None,
            "pattern_response": None,
            "cached_knowledge": None,
            "should_learn": True,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # 1. Check patterns first (for greetings, etc)
        pattern_type, pattern_response, metadata = self.pattern_detector.detect(query)
        if pattern_type:
            result["pattern_type"] = pattern_type
            result["pattern_response"] = pattern_response
            if pattern_response:  # Static response available
                result["should_learn"] = False
        
        # 2. Check knowledge base
        cached = self.knowledge_accumulator.find_similar(query)
        if cached:
            result["cached_knowledge"] = {
                "knowledge_id": cached.knowledge_id,
                "response": cached.response,
                "confidence": cached.confidence,
                "times_used": cached.times_used,
                "helpfulness": cached.helpfulness_score
            }
            # Use cached if high confidence and helpful
            if cached.confidence > 0.8 and cached.helpfulness_score > 0.6:
                result["should_learn"] = False
        
        # Track session
        self.session_queries.append(result)
        
        return result
    
    def learn_from_response(self, query: str, response: str, sources: List[str], confidence: float) -> str:
        """
        Mëso nga përgjigja e dhënë
        Returns knowledge_id
        """
        knowledge = self.knowledge_accumulator.learn(query, response, sources, confidence)
        return knowledge.knowledge_id
    
    def record_feedback(self, knowledge_id: str, helpful: bool):
        """Regjistro feedback"""
        self.knowledge_accumulator.feedback(knowledge_id, helpful)
    
    def get_learning_stats(self) -> Dict:
        """Merr statistikat e mësimit"""
        kb_stats = self.knowledge_accumulator.get_stats()
        
        return {
            "knowledge_base": kb_stats,
            "patterns": {
                "base_patterns": len(self.pattern_detector.BASE_PATTERNS),
                "custom_patterns": len(self.pattern_detector.custom_patterns)
            },
            "session": {
                "queries_this_session": len(self.session_queries),
                "learned_this_session": sum(1 for q in self.session_queries if q.get("should_learn", False))
            }
        }
    
    def suggest_response(self, query: str) -> Optional[str]:
        """
        Sugjero përgjigje bazuar në dijet e mësuara
        """
        # Check pattern first
        pattern_type, pattern_response, _ = self.pattern_detector.detect(query)
        if pattern_response:
            return pattern_response
        
        # Check knowledge base
        cached = self.knowledge_accumulator.find_similar(query)
        if cached and cached.helpfulness_score > 0.6:
            return cached.response
        
        return None


# =============================================================================
# SINGLETON & API
# =============================================================================

_engine: Optional[AutolearningEngine] = None

def get_autolearning_engine() -> AutolearningEngine:
    """Get or create the autolearning engine"""
    global _engine
    if _engine is None:
        _engine = AutolearningEngine()
    return _engine


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    engine = get_autolearning_engine()
    
    print("\n" + "="*60)
    print("🧠 AUTOLEARNING ENGINE TEST")
    print("="*60)
    
    # Test queries
    test_queries = [
        "Hello!",
        "What is consciousness?",
        "How many data sources do we have?",
        "What's the weather in Tirana?",
        "Who are you?",
        "Faleminderit për ndihmën!"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: {query}")
        result = engine.process_query(query)
        print(f"   Pattern: {result['pattern_type']}")
        print(f"   Cached: {result['cached_knowledge'] is not None}")
        print(f"   Should learn: {result['should_learn']}")
        
        if result['pattern_response']:
            print(f"   Response: {result['pattern_response']}")
        
        # Simulate learning
        if result['should_learn']:
            knowledge_id = engine.learn_from_response(
                query, 
                f"Response to: {query}", 
                ["test"], 
                0.85
            )
            print(f"   Learned as: {knowledge_id}")
    
    # Show stats
    print("\n" + "="*60)
    print("📊 LEARNING STATS")
    print("="*60)
    stats = engine.get_learning_stats()
    print(json.dumps(stats, indent=2, ensure_ascii=False))

