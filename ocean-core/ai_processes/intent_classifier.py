"""
INTENT CLASSIFIER - User Intent Classification AI Process
==========================================================
Classifies user messages to understand their intent.

Features:
- Intent detection for conversational AI
- Action extraction
- Entity slot filling
- Confidence scoring
- Multi-intent support
"""

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class UserIntent(Enum):
    """Common user intents"""
    # Information
    QUERY = "query"              # Asking for information
    SEARCH = "search"            # Searching for something
    EXPLAIN = "explain"          # Asking for explanation
    DEFINE = "define"            # Asking for definition
    COMPARE = "compare"          # Comparing things
    
    # Actions
    CREATE = "create"            # Create something new
    UPDATE = "update"            # Update/modify something
    DELETE = "delete"            # Delete/remove something
    EXECUTE = "execute"          # Run/execute something
    CONFIGURE = "configure"      # Configure/setup
    
    # Communication
    GREETING = "greeting"        # Hello, hi, etc.
    FAREWELL = "farewell"        # Goodbye, bye
    THANKS = "thanks"            # Thank you
    HELP = "help"                # Asking for help
    FEEDBACK = "feedback"        # Providing feedback
    
    # Navigation
    NAVIGATE = "navigate"        # Go to somewhere
    LIST = "list"                # List items
    SHOW = "show"                # Show/display something
    
    # Transactions
    ORDER = "order"              # Place an order
    CANCEL = "cancel"            # Cancel something
    SUBSCRIBE = "subscribe"      # Subscribe to service
    PAY = "pay"                  # Make payment
    
    # Support
    REPORT_ISSUE = "report_issue"  # Report a problem
    REQUEST_SUPPORT = "support"    # Request support
    
    # Other
    UNKNOWN = "unknown"          # Unknown intent
    CHITCHAT = "chitchat"        # Small talk


@dataclass
class ExtractedSlot:
    """Extracted slot/entity from user message"""
    name: str
    value: str
    type: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "value": self.value,
            "type": self.type
        }


@dataclass
class IntentResult:
    """Single intent classification result"""
    intent: UserIntent
    confidence: float
    keywords: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "intent": self.intent.value,
            "confidence": round(self.confidence, 3),
            "keywords": self.keywords
        }


@dataclass
class IntentClassificationResult:
    """Result of intent classification"""
    message: str
    primary_intent: str
    confidence: float
    all_intents: List[IntentResult]
    extracted_slots: List[ExtractedSlot]
    action_required: bool
    suggested_response_type: str
    processing_time_ms: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "message": self.message[:200],
            "primary_intent": self.primary_intent,
            "confidence": round(self.confidence, 3),
            "all_intents": [i.to_dict() for i in self.all_intents[:3]],
            "extracted_slots": [s.to_dict() for s in self.extracted_slots],
            "action_required": self.action_required,
            "suggested_response_type": self.suggested_response_type,
            "processing_time_ms": round(self.processing_time_ms, 2)
        }


class IntentClassifier:
    """
    User Intent Classification Engine
    
    Classifies user messages to understand their intentions
    """
    
    # Intent keywords
    INTENT_PATTERNS = {
        UserIntent.GREETING: {
            "keywords": ["hello", "hi", "hey", "good morning", "good afternoon", 
                        "good evening", "howdy", "greetings", "përshëndetje", 
                        "mirëdita", "tungjatjeta"],
            "patterns": [r'^(hi|hello|hey)\b', r'^good\s+(morning|afternoon|evening)']
        },
        UserIntent.FAREWELL: {
            "keywords": ["bye", "goodbye", "see you", "take care", "farewell",
                        "mirupafshim", "lamtumirë", "ditën e mirë"],
            "patterns": [r'\b(bye|goodbye|see\s+you)\b']
        },
        UserIntent.THANKS: {
            "keywords": ["thank", "thanks", "appreciate", "grateful", "faleminderit"],
            "patterns": [r'\b(thank|thanks)\b', r'appreciate\s+it']
        },
        UserIntent.HELP: {
            "keywords": ["help", "assist", "support", "guidance", "how do i",
                        "can you help", "ndihmë", "si mund"],
            "patterns": [r'\b(help|assist)\s+me', r'can\s+you\s+help', r'how\s+do\s+i']
        },
        UserIntent.QUERY: {
            "keywords": ["what", "who", "when", "where", "which", "çfarë", "kush",
                        "kur", "ku", "cili"],
            "patterns": [r'^(what|who|when|where|which)\b', r'\?$']
        },
        UserIntent.EXPLAIN: {
            "keywords": ["explain", "why", "how", "describe", "elaborate", 
                        "shpjego", "pse", "si"],
            "patterns": [r'^(explain|why|how)\b', r'can\s+you\s+explain']
        },
        UserIntent.DEFINE: {
            "keywords": ["define", "definition", "meaning", "what is", "what's",
                        "përcakto", "çfarë është"],
            "patterns": [r'what\s+(is|are)\s+', r'\bdefine\b', r'meaning\s+of']
        },
        UserIntent.CREATE: {
            "keywords": ["create", "make", "build", "generate", "new", "add",
                        "krijo", "bëj", "shto"],
            "patterns": [r'^(create|make|build|add)\b', r'i\s+want\s+to\s+(create|make)']
        },
        UserIntent.UPDATE: {
            "keywords": ["update", "modify", "change", "edit", "fix", "correct",
                        "përditëso", "ndrysho"],
            "patterns": [r'^(update|modify|change|edit)\b']
        },
        UserIntent.DELETE: {
            "keywords": ["delete", "remove", "clear", "cancel", "fshi", "hiq"],
            "patterns": [r'^(delete|remove|clear)\b']
        },
        UserIntent.SEARCH: {
            "keywords": ["search", "find", "look for", "locate", "kërko", "gjej"],
            "patterns": [r'^(search|find)\b', r'look(ing)?\s+for', r'where\s+can\s+i\s+find']
        },
        UserIntent.LIST: {
            "keywords": ["list", "show all", "display all", "enumerate", "listo", "trego"],
            "patterns": [r'^(list|show)\s+(all|me)', r'give\s+me\s+a\s+list']
        },
        UserIntent.SHOW: {
            "keywords": ["show", "display", "view", "see", "open", "trego", "shfaq"],
            "patterns": [r'^(show|display|view|open)\b', r'let\s+me\s+see']
        },
        UserIntent.CONFIGURE: {
            "keywords": ["configure", "setup", "set up", "settings", "config",
                        "konfiguro", "rregullime"],
            "patterns": [r'^(configure|setup|set\s+up)\b']
        },
        UserIntent.EXECUTE: {
            "keywords": ["run", "execute", "start", "launch", "trigger",
                        "ekzekuto", "fillo"],
            "patterns": [r'^(run|execute|start|launch)\b']
        },
        UserIntent.ORDER: {
            "keywords": ["order", "buy", "purchase", "get", "porosit", "bli"],
            "patterns": [r'i\s+(want|would\s+like)\s+to\s+(order|buy)']
        },
        UserIntent.CANCEL: {
            "keywords": ["cancel", "abort", "stop", "undo", "anulo", "ndalo"],
            "patterns": [r'^(cancel|abort|stop)\b']
        },
        UserIntent.SUBSCRIBE: {
            "keywords": ["subscribe", "sign up", "register", "join", "abonohu", "regjistrohu"],
            "patterns": [r'\b(subscribe|sign\s+up|register)\b']
        },
        UserIntent.PAY: {
            "keywords": ["pay", "payment", "checkout", "purchase", "paguaj", "pagesë"],
            "patterns": [r'\b(pay|payment|checkout)\b']
        },
        UserIntent.REPORT_ISSUE: {
            "keywords": ["bug", "issue", "problem", "error", "broken", "not working",
                        "gabim", "problem"],
            "patterns": [r'\b(bug|issue|problem|error)\b', r'(not|isn\'t)\s+working']
        },
        UserIntent.COMPARE: {
            "keywords": ["compare", "versus", "vs", "difference", "better",
                        "krahaso", "ndryshimi"],
            "patterns": [r'\bcompare\b', r'\bvs\.?\b', r'difference\s+between']
        },
        UserIntent.FEEDBACK: {
            "keywords": ["feedback", "suggestion", "review", "opinion", "mendim"],
            "patterns": [r'\b(feedback|suggestion)\b', r'i\s+think']
        }
    }
    
    # Slot patterns
    SLOT_PATTERNS = {
        "email": r'\b[\w.-]+@[\w.-]+\.\w+\b',
        "phone": r'\b\+?[\d\s-]{10,}\b',
        "number": r'\b\d+\b',
        "date": r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
        "time": r'\b\d{1,2}:\d{2}(?:\s*[AP]M)?\b',
        "url": r'https?://\S+',
        "name": r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b',
        "currency": r'[$€£]\d+(?:\.\d{2})?|\d+\s*(?:USD|EUR|GBP|ALL)'
    }
    
    # Response type mapping
    RESPONSE_TYPES = {
        UserIntent.GREETING: "greeting",
        UserIntent.FAREWELL: "farewell",
        UserIntent.THANKS: "acknowledgment",
        UserIntent.HELP: "assistance",
        UserIntent.QUERY: "informational",
        UserIntent.EXPLAIN: "explanation",
        UserIntent.DEFINE: "definition",
        UserIntent.CREATE: "action_confirmation",
        UserIntent.UPDATE: "action_confirmation",
        UserIntent.DELETE: "action_confirmation",
        UserIntent.SEARCH: "search_results",
        UserIntent.LIST: "list_display",
        UserIntent.SHOW: "content_display",
        UserIntent.REPORT_ISSUE: "support_ticket",
        UserIntent.COMPARE: "comparison",
        UserIntent.CHITCHAT: "conversational"
    }
    
    def __init__(self, ollama_host: Optional[str] = None):
        self.ollama_host = ollama_host or "http://kloud-ollama:11434"
        self._initialized = False
        logger.info("🎯 IntentClassifier initialized")
    
    async def initialize(self):
        """Initialize the classifier"""
        if self._initialized:
            return
        self._initialized = True
        logger.info("✅ IntentClassifier ready")
    
    async def classify(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        use_llm: bool = True
    ) -> IntentClassificationResult:
        """
        Classify user message intent
        
        Args:
            message: User message to classify
            context: Optional conversation context
            use_llm: Use LLM for enhanced classification
        """
        start_time = datetime.now()
        
        message_lower = message.lower().strip()
        
        # Classify intents
        intents = self._classify_intents(message_lower)
        
        # Extract slots
        slots = self._extract_slots(message)
        
        # LLM enhancement for low confidence
        if use_llm and (not intents or intents[0].confidence < 0.6):
            llm_intent = await self._llm_classify(message)
            if llm_intent:
                # Add or boost LLM result
                existing = next((i for i in intents if i.intent == llm_intent), None)
                if existing:
                    existing.confidence = min(0.95, existing.confidence + 0.2)
                else:
                    intents.insert(0, IntentResult(
                        intent=llm_intent,
                        confidence=0.75,
                        keywords=["llm_detected"]
                    ))
        
        # Sort by confidence
        intents.sort(key=lambda x: -x.confidence)
        
        # Default to unknown
        if not intents:
            intents.append(IntentResult(
                intent=UserIntent.UNKNOWN,
                confidence=0.5,
                keywords=[]
            ))
        
        primary = intents[0]
        
        # Determine if action required
        action_intents = {UserIntent.CREATE, UserIntent.UPDATE, UserIntent.DELETE,
                        UserIntent.EXECUTE, UserIntent.ORDER, UserIntent.CANCEL,
                        UserIntent.SUBSCRIBE, UserIntent.PAY}
        action_required = primary.intent in action_intents
        
        # Suggested response type
        response_type = self.RESPONSE_TYPES.get(primary.intent, "general")
        
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return IntentClassificationResult(
            message=message,
            primary_intent=primary.intent.value,
            confidence=primary.confidence,
            all_intents=intents,
            extracted_slots=slots,
            action_required=action_required,
            suggested_response_type=response_type,
            processing_time_ms=processing_time
        )
    
    def _classify_intents(self, message: str) -> List[IntentResult]:
        """Classify message into intents"""
        results = []
        
        for intent, config in self.INTENT_PATTERNS.items():
            score = 0.0
            matched_keywords = []
            
            # Keyword matching
            keywords = config.get("keywords", [])
            for keyword in keywords:
                if keyword in message:
                    score += 0.2
                    matched_keywords.append(keyword)
            
            # Pattern matching
            patterns = config.get("patterns", [])
            for pattern in patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    score += 0.3
            
            if score > 0:
                results.append(IntentResult(
                    intent=intent,
                    confidence=min(0.95, score),
                    keywords=matched_keywords
                ))
        
        return results
    
    def _extract_slots(self, message: str) -> List[ExtractedSlot]:
        """Extract slots/entities from message"""
        slots = []
        
        for slot_type, pattern in self.SLOT_PATTERNS.items():
            matches = re.findall(pattern, message, re.IGNORECASE)
            for match in matches:
                slots.append(ExtractedSlot(
                    name=slot_type,
                    value=match,
                    type=slot_type
                ))
        
        return slots
    
    async def _llm_classify(self, message: str) -> Optional[UserIntent]:
        """Use LLM for intent classification"""
        try:
            import httpx
            
            intent_names = ", ".join([i.value for i in UserIntent])
            
            prompt = f"""Classify the user's intent. Choose ONE from: {intent_names}

Message: "{message}"

Intent:"""
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.ollama_host}/api/generate",
                    json={
                        "model": "llama3.1:8b",
                        "prompt": prompt,
                        "stream": False,
                        "options": {"temperature": 0.1, "num_predict": 20}
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    intent_str = result.get("response", "").strip().lower()
                    
                    # Match to enum
                    for intent in UserIntent:
                        if intent.value in intent_str or intent_str in intent.value:
                            return intent
        except Exception as e:
            logger.debug(f"LLM intent classification failed: {e}")
        
        return None


# Singleton instance
_intent_classifier: Optional[IntentClassifier] = None


def get_intent_classifier() -> IntentClassifier:
    """Get or create intent classifier instance"""
    global _intent_classifier
    if _intent_classifier is None:
        _intent_classifier = IntentClassifier()
    return _intent_classifier

