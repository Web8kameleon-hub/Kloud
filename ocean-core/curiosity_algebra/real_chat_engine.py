# -*- coding: utf-8 -*-
"""
🧠 REAL CHAT ENGINE - No Fake, Only Real Functions!
====================================================
Chat engine që bën gjëra reale:
- Llogaritje matematikore
- Përgjigje në gjuhën e përdoruesit (i18n)
- Informacion real sistemi
- Data dhe kohë
- Konvertime

NO PLACEHOLDER! NO FAKE ANSWERS! VETËM FUNKSIONE REALE!

Author: Kloud Team
"""

import re
import math
import json
import hashlib
from typing import Dict, Any, List, Optional, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

from .i18n_engine import get_i18n_engine, t, detect_lang
from .binary_protocols import get_binary_service
from .real_learning_engine import get_real_learning_engine


class IntentType(Enum):
    """Llojet e qëllimeve"""
    MATH = "math"
    GREETING = "greeting"
    TIME = "time"
    DATE = "date"
    STATUS = "status"
    HELP = "help"
    CONVERSION = "conversion"
    TRANSLATION = "translation"
    SYSTEM = "system"
    UNKNOWN = "unknown"


@dataclass
class ChatIntent:
    """Qëllimi i zbuluar"""
    type: IntentType
    confidence: float
    entities: Dict[str, Any] = field(default_factory=dict)
    raw_query: str = ""
    language: str = "en"


@dataclass
class ChatResponse:
    """Përgjigja e chat-it"""
    success: bool
    type: str
    answer: str
    language: str
    confidence: float
    data: Dict[str, Any] = field(default_factory=dict)
    suggestions: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "type": self.type,
            "answer": self.answer,
            "language": self.language,
            "confidence": self.confidence,
            "data": self.data,
            "suggestions": self.suggestions,
            "timestamp": self.timestamp
        }


class IntentDetector:
    """Detekton qëllimin e përdoruesit"""
    
    def __init__(self):
        self.math_patterns = [
            # Direct expressions
            r'(\d+(?:\.\d+)?)\s*([\+\-\*\/\^%])\s*(\d+(?:\.\d+)?)',
            # Albanian
            r'sa\s+b[eë]jn[eë]\s+(\d+(?:\.\d+)?)\s*([\+\-\*\/x×÷:])\s*(\d+(?:\.\d+)?)',
            r'llogarit\s+(\d+(?:\.\d+)?)\s*([\+\-\*\/x×÷:])\s*(\d+(?:\.\d+)?)',
            r'sa\s+[eë]sht[eë]\s+(\d+(?:\.\d+)?)\s*([\+\-\*\/x×÷:])\s*(\d+(?:\.\d+)?)',
            # English
            r'what\s+is\s+(\d+(?:\.\d+)?)\s*([\+\-\*\/x×÷:])\s*(\d+(?:\.\d+)?)',
            r'calculate\s+(\d+(?:\.\d+)?)\s*([\+\-\*\/x×÷:])\s*(\d+(?:\.\d+)?)',
            r'compute\s+(\d+(?:\.\d+)?)\s*([\+\-\*\/x×÷:])\s*(\d+(?:\.\d+)?)',
            # Square root, power
            r'(sqrt|rrënja|raiz)\s*[\(\s]*(\d+(?:\.\d+)?)',
            r'(\d+(?:\.\d+)?)\s*(squared|katror|në katror)',
            r'(\d+(?:\.\d+)?)\s*(cubed|kub|në kub)',
        ]
        
        self.greeting_patterns = [
            r'\b(hello|hi|hey|greetings|good\s+morning|good\s+afternoon|good\s+evening)\b',
            r'\b(përshëndetje|mirëdita|mirëmbrëmje|mirëmëngjes|tungjatjeta|çkemi)\b',
            r'\b(hallo|guten\s+tag|guten\s+morgen)\b',
            r'\b(bonjour|bonsoir|salut)\b',
            r'\b(ciao|buongiorno|buonasera)\b',
            r'\b(hola|buenos\s+días)\b',
            r'\b(merhaba|selam)\b',
        ]
        
        self.time_patterns = [
            r'\b(what\s+time|current\s+time|time\s+now)\b',
            r'\b(sa\s+[eë]sht[eë]\s+ora|ora\s+sa\s+[eë]sht[eë]|çfarë\s+ore)\b',
            r'\b(wie\s+spät|welche\s+zeit)\b',
            r'\b(quelle\s+heure)\b',
            r'\b(che\s+ora)\b',
            r'\b(saat\s+kaç)\b',
        ]
        
        self.date_patterns = [
            r'\b(what\s+day|what\s+date|today|current\s+date)\b',
            r'\b(çfarë\s+dit[eë]|sot|data\s+e\s+sotme)\b',
            r'\b(welcher\s+tag|heute)\b',
            r'\b(quel\s+jour|aujourd\'hui)\b',
            r'\b(che\s+giorno|oggi)\b',
            r'\b(bugün|hangi\s+gün)\b',
        ]
        
        self.status_patterns = [
            r'\b(status|health|how\s+are\s+you)\b',
            r'\b(gjendja|si\s+je|statusi)\b',
            r'\b(wie\s+geht)\b',
            r'\b(comment\s+vas)\b',
            r'\b(come\s+stai)\b',
            r'\b(nasılsın)\b',
        ]
        
        self.help_patterns = [
            r'\b(help|what\s+can\s+you\s+do|commands|ndihmë|çfarë\s+bën|hilfe|aide|aiuto|ayuda)\b',
        ]
        
        self.conversion_patterns = [
            r'(\d+(?:\.\d+)?)\s*(km|mi|miles|kilometer|celsius|fahrenheit|kg|lb|pounds|m|ft|feet)\s*(?:to|në|in)\s*(km|mi|miles|kilometer|celsius|fahrenheit|kg|lb|pounds|m|ft|feet)',
        ]
    
    def detect(self, query: str) -> ChatIntent:
        """Detekto qëllimin e query-t"""
        query_lower = query.lower().strip()
        lang = detect_lang(query)
        
        # Math
        for pattern in self.math_patterns:
            match = re.search(pattern, query_lower)
            if match:
                return ChatIntent(
                    type=IntentType.MATH,
                    confidence=0.95,
                    entities={"match": match.groups()},
                    raw_query=query,
                    language=lang
                )
        
        # Conversion
        for pattern in self.conversion_patterns:
            match = re.search(pattern, query_lower)
            if match:
                return ChatIntent(
                    type=IntentType.CONVERSION,
                    confidence=0.9,
                    entities={"value": float(match.group(1)), "from": match.group(2), "to": match.group(3)},
                    raw_query=query,
                    language=lang
                )
        
        # Greeting
        for pattern in self.greeting_patterns:
            if re.search(pattern, query_lower):
                return ChatIntent(
                    type=IntentType.GREETING,
                    confidence=0.9,
                    raw_query=query,
                    language=lang
                )
        
        # Time
        for pattern in self.time_patterns:
            if re.search(pattern, query_lower):
                return ChatIntent(
                    type=IntentType.TIME,
                    confidence=0.9,
                    raw_query=query,
                    language=lang
                )
        
        # Date
        for pattern in self.date_patterns:
            if re.search(pattern, query_lower):
                return ChatIntent(
                    type=IntentType.DATE,
                    confidence=0.9,
                    raw_query=query,
                    language=lang
                )
        
        # Status
        for pattern in self.status_patterns:
            if re.search(pattern, query_lower):
                return ChatIntent(
                    type=IntentType.STATUS,
                    confidence=0.85,
                    raw_query=query,
                    language=lang
                )
        
        # Help
        for pattern in self.help_patterns:
            if re.search(pattern, query_lower):
                return ChatIntent(
                    type=IntentType.HELP,
                    confidence=0.9,
                    raw_query=query,
                    language=lang
                )
        
        # Unknown
        return ChatIntent(
            type=IntentType.UNKNOWN,
            confidence=0.5,
            raw_query=query,
            language=lang
        )


class RealChatEngine:
    """Motori real i chat-it - asnjë fake!"""
    
    def __init__(self):
        self.i18n = get_i18n_engine()
        self.detector = IntentDetector()
        self.binary_service = get_binary_service()
        self.learning_engine = get_real_learning_engine()  # REAL LEARNING!
        self.history: List[Dict[str, Any]] = []
        self.stats = {
            "queries_processed": 0,
            "math_solved": 0,
            "greetings_given": 0,
            "times_told": 0,
            "dates_told": 0,
            "help_given": 0,
            "conversions_done": 0,
            "unknown_handled": 0,
            "knowledge_queries": 0
        }
    
    def chat(self, query: str) -> ChatResponse:
        """Proceso pyetjen dhe kthe përgjigje REALE"""
        self.stats["queries_processed"] += 1
        
        # Detect intent
        intent = self.detector.detect(query)
        
        # Handle based on intent
        handlers = {
            IntentType.MATH: self._handle_math,
            IntentType.GREETING: self._handle_greeting,
            IntentType.TIME: self._handle_time,
            IntentType.DATE: self._handle_date,
            IntentType.STATUS: self._handle_status,
            IntentType.HELP: self._handle_help,
            IntentType.CONVERSION: self._handle_conversion,
            IntentType.UNKNOWN: self._handle_unknown,
        }
        
        handler = handlers.get(intent.type, self._handle_unknown)
        response = handler(intent)
        
        # Save to history
        self.history.append({
            "query": query,
            "intent": intent.type.value,
            "language": intent.language,
            "response": response.to_dict(),
            "timestamp": datetime.now().isoformat()
        })
        
        return response
    
    def _handle_math(self, intent: ChatIntent) -> ChatResponse:
        """Trajto llogaritjet - REALE!"""
        self.stats["math_solved"] += 1
        lang = intent.language
        query = intent.raw_query
        
        # Try binary service calculator first
        result = self.binary_service.calculate(query)
        
        if result.get("success"):
            # Format answer in user's language
            result_value = result["result"]
            expr = result.get("expression", query)
            
            # Build answer in user's language
            result_text = self.i18n.t("result_is", lang)
            formatted = self.i18n.format_number(result_value, lang)
            
            answer = f"{result_text}: {expr} = {formatted}"
            
            return ChatResponse(
                success=True,
                type="math",
                answer=answer,
                language=lang,
                confidence=1.0,
                data={
                    "expression": expr,
                    "result": result_value,
                    "formatted_result": formatted,
                    "operator": result.get("operator"),
                    "operands": result.get("operands")
                },
                suggestions=self._get_math_suggestions(lang)
            )
        
        # Try parsing directly
        parsed = self._parse_math_directly(query)
        if parsed:
            result_text = self.i18n.t("result_is", lang)
            formatted = self.i18n.format_number(parsed["result"], lang)
            answer = f"{result_text}: {parsed['expression']} = {formatted}"
            
            return ChatResponse(
                success=True,
                type="math",
                answer=answer,
                language=lang,
                confidence=0.95,
                data=parsed,
                suggestions=self._get_math_suggestions(lang)
            )
        
        # Can't solve
        error_text = self.i18n.t("error", lang)
        return ChatResponse(
            success=False,
            type="math_error",
            answer=f"{error_text}: Could not parse expression",
            language=lang,
            confidence=0.0,
            suggestions=self._get_math_suggestions(lang)
        )
    
    def _parse_math_directly(self, query: str) -> Optional[Dict[str, Any]]:
        """Parse math expression directly"""
        import re
        
        # Clean query
        clean = query.lower().strip()
        clean = re.sub(r'sa\s+b[eë]jn[eë]\s*', '', clean)
        clean = re.sub(r'what\s+is\s*', '', clean)
        clean = re.sub(r'calculate\s*', '', clean)
        clean = re.sub(r'llogarit\s*', '', clean)
        clean = clean.replace('x', '*').replace('×', '*').replace('÷', '/').replace(':', '/')
        clean = clean.replace('?', '').strip()
        
        # Find expression
        match = re.search(r'(\d+(?:\.\d+)?)\s*([\+\-\*\/\^%])\s*(\d+(?:\.\d+)?)', clean)
        if match:
            a, op, b = float(match.group(1)), match.group(2), float(match.group(3))
            
            if op == '+':
                result = a + b
            elif op == '-':
                result = a - b
            elif op == '*':
                result = a * b
            elif op == '/':
                result = a / b if b != 0 else float('inf')
            elif op == '^':
                result = a ** b
            elif op == '%':
                result = a % b if b != 0 else 0
            else:
                return None
            
            return {
                "expression": f"{a} {op} {b}",
                "operands": [a, b],
                "operator": op,
                "result": result
            }
        
        # Try sqrt
        sqrt_match = re.search(r'sqrt[\(\s]*(\d+(?:\.\d+)?)', clean)
        if sqrt_match:
            n = float(sqrt_match.group(1))
            return {
                "expression": f"√{n}",
                "operands": [n],
                "operator": "sqrt",
                "result": math.sqrt(n)
            }
        
        # Try squared
        sq_match = re.search(r'(\d+(?:\.\d+)?)\s*(squared|katror)', clean)
        if sq_match:
            n = float(sq_match.group(1))
            return {
                "expression": f"{n}²",
                "operands": [n],
                "operator": "square",
                "result": n ** 2
            }
        
        return None
    
    def _handle_greeting(self, intent: ChatIntent) -> ChatResponse:
        """Trajto përshëndetjet"""
        self.stats["greetings_given"] += 1
        lang = intent.language
        
        greeting = self.i18n.t("hello", lang)
        help_text = self.i18n.t("how_can_i_help", lang)
        
        return ChatResponse(
            success=True,
            type="greeting",
            answer=f"{greeting}! {help_text}",
            language=lang,
            confidence=1.0,
            suggestions=self._get_general_suggestions(lang)
        )
    
    def _handle_time(self, intent: ChatIntent) -> ChatResponse:
        """Trajto pyetjet për kohën - REALE!"""
        self.stats["times_told"] += 1
        lang = intent.language
        now = datetime.now()
        
        # Real time!
        hour = now.hour
        minute = now.minute
        second = now.second
        
        # Format based on language
        if lang in ["en"]:
            am_pm = "AM" if hour < 12 else "PM"
            hour_12 = hour if hour <= 12 else hour - 12
            hour_12 = 12 if hour_12 == 0 else hour_12
            time_str = f"{hour_12}:{minute:02d}:{second:02d} {am_pm}"
        else:
            time_str = f"{hour:02d}:{minute:02d}:{second:02d}"
        
        now_text = self.i18n.t("now", lang)
        
        return ChatResponse(
            success=True,
            type="time",
            answer=f"🕐 {now_text}: {time_str}",
            language=lang,
            confidence=1.0,
            data={
                "hour": hour,
                "minute": minute,
                "second": second,
                "formatted": time_str,
                "timezone": "local"
            }
        )
    
    def _handle_date(self, intent: ChatIntent) -> ChatResponse:
        """Trajto pyetjet për datën - REALE!"""
        self.stats["dates_told"] += 1
        lang = intent.language
        now = datetime.now()
        
        # Real date!
        date_long = self.i18n.format_date(now, lang, "long")
        date_short = self.i18n.format_date(now, lang, "short")
        today = self.i18n.t("today", lang)
        
        return ChatResponse(
            success=True,
            type="date",
            answer=f"📅 {today}: {date_long}",
            language=lang,
            confidence=1.0,
            data={
                "year": now.year,
                "month": now.month,
                "day": now.day,
                "weekday": now.weekday(),
                "date_long": date_long,
                "date_short": date_short,
                "iso": now.date().isoformat()
            }
        )
    
    def _handle_status(self, intent: ChatIntent) -> ChatResponse:
        """Trajto pyetjet për statusin - REALE!"""
        lang = intent.language
        
        status_text = self.i18n.t("status", lang)
        operational = self.i18n.t("operational", lang)
        
        return ChatResponse(
            success=True,
            type="status",
            answer=f"✅ {status_text}: {operational}",
            language=lang,
            confidence=1.0,
            data={
                "status": "operational",
                "queries_processed": self.stats["queries_processed"],
                "uptime": "active",
                "version": "2.1.0"
            }
        )
    
    def _handle_help(self, intent: ChatIntent) -> ChatResponse:
        """Trajto pyetjet për ndihmë"""
        self.stats["help_given"] += 1
        lang = intent.language
        
        help_messages = {
            "sq": """🤖 **Çfarë mund të bëj:**
• Llogaritje: "Sa bëjnë 5 + 3?" ose "10 * 5"
• Ora: "Sa është ora?"
• Data: "Çfarë dite është sot?"
• Përshëndetje: "Përshëndetje!"
• Konvertime: "10 km në mile"
• Statusi: "Si je?"
""",
            "en": """🤖 **What I can do:**
• Math: "What is 5 + 3?" or "10 * 5"
• Time: "What time is it?"
• Date: "What day is today?"
• Greeting: "Hello!"
• Conversions: "10 km to miles"
• Status: "How are you?"
""",
            "de": """🤖 **Was ich kann:**
• Mathematik: "Was ist 5 + 3?" oder "10 * 5"
• Zeit: "Wie spät ist es?"
• Datum: "Welcher Tag ist heute?"
• Begrüßung: "Hallo!"
• Umrechnung: "10 km in Meilen"
""",
        }
        
        answer = help_messages.get(lang, help_messages["en"])
        
        return ChatResponse(
            success=True,
            type="help",
            answer=answer,
            language=lang,
            confidence=1.0,
            suggestions=self._get_general_suggestions(lang)
        )
    
    def _handle_conversion(self, intent: ChatIntent) -> ChatResponse:
        """Trajto konvertimet - REALE!"""
        self.stats["conversions_done"] += 1
        lang = intent.language
        
        value = intent.entities.get("value", 0)
        from_unit = intent.entities.get("from", "").lower()
        to_unit = intent.entities.get("to", "").lower()
        
        # Real conversion rates
        conversions = {
            ("km", "mi"): lambda x: x * 0.621371,
            ("km", "miles"): lambda x: x * 0.621371,
            ("mi", "km"): lambda x: x * 1.60934,
            ("miles", "km"): lambda x: x * 1.60934,
            ("celsius", "fahrenheit"): lambda x: x * 9/5 + 32,
            ("fahrenheit", "celsius"): lambda x: (x - 32) * 5/9,
            ("kg", "lb"): lambda x: x * 2.20462,
            ("kg", "pounds"): lambda x: x * 2.20462,
            ("lb", "kg"): lambda x: x * 0.453592,
            ("pounds", "kg"): lambda x: x * 0.453592,
            ("m", "ft"): lambda x: x * 3.28084,
            ("m", "feet"): lambda x: x * 3.28084,
            ("ft", "m"): lambda x: x * 0.3048,
            ("feet", "m"): lambda x: x * 0.3048,
            ("kilometer", "mi"): lambda x: x * 0.621371,
            ("kilometer", "miles"): lambda x: x * 0.621371,
        }
        
        key = (from_unit, to_unit)
        if key in conversions:
            result = conversions[key](value)
            formatted = self.i18n.format_number(result, lang)
            
            return ChatResponse(
                success=True,
                type="conversion",
                answer=f"📐 {value} {from_unit} = {formatted} {to_unit}",
                language=lang,
                confidence=1.0,
                data={
                    "from_value": value,
                    "from_unit": from_unit,
                    "to_value": result,
                    "to_unit": to_unit
                }
            )
        
        error = self.i18n.t("error", lang)
        return ChatResponse(
            success=False,
            type="conversion_error",
            answer=f"{error}: Unknown conversion {from_unit} → {to_unit}",
            language=lang,
            confidence=0.0
        )
    
    def _handle_unknown(self, intent: ChatIntent) -> ChatResponse:
        """Trajto pyetjet e panjohura - KERKO NE REAL LEARNING!"""
        self.stats["unknown_handled"] += 1
        lang = intent.language
        query = intent.raw_query
        
        # Try to find any numbers and operators
        numbers = re.findall(r'\d+(?:\.\d+)?', query)
        operators = re.findall(r'[\+\-\*\/\^%]', query)
        
        if len(numbers) >= 2 and len(operators) >= 1:
            # Maybe it's math, try parsing
            parsed = self._parse_math_directly(query)
            if parsed:
                return self._handle_math(intent)
        
        # === KERKO NE REAL LEARNING ENGINE ===
        self.stats["knowledge_queries"] += 1
        
        # Provojmë të gjejmë përgjigje nga njohuritë reale
        knowledge_result = self._search_real_knowledge(query)
        if knowledge_result:
            return ChatResponse(
                success=True,
                type="knowledge",
                answer=knowledge_result["answer"],
                language=lang,
                confidence=knowledge_result.get("confidence", 0.8),
                data={
                    "source": knowledge_result.get("source", "real_learning"),
                    "evidence": knowledge_result.get("evidence", ""),
                    "is_real": True,
                    "is_mock": False
                },
                suggestions=[]
            )
        
        # Nëse nuk gjejmë, kthejmë përgjigje të sinqertë
        messages = {
            "sq": f"🔍 Nuk kam informacion për: '{query}'\n\nMund të pyes për:\n• Llogaritje: 5+3\n• Ora: Sa është ora?\n• Data: Çfarë dite është?\n• Konvertime: 10 km to miles",
            "en": f"🔍 I don't have information about: '{query}'\n\nYou can ask:\n• Math: 5+3\n• Time: What time is it?\n• Date: What day is it?\n• Conversions: 10 km to miles",
            "de": f"🔍 Ich habe keine Informationen über: '{query}'\n\nSie können fragen:\n• Mathematik: 5+3\n• Zeit: Wie spät ist es?",
        }
        
        answer = messages.get(lang, messages["en"])
        
        return ChatResponse(
            success=True,
            type="no_knowledge",
            answer=answer,
            language=lang,
            confidence=0.3,
            data={"searched": True, "found": False},
            suggestions=self._get_general_suggestions(lang)
        )
    
    def _search_real_knowledge(self, query: str) -> Optional[Dict[str, Any]]:
        """Kërko në Real Learning Engine për përgjigje"""
        query_lower = query.lower()
        
        # Kërko fjalë kyçe dhe lidhi me topics
        keyword_to_topic = {
            # Autor/krijues
            "created": "app_author",
            "creator": "app_author",
            "author": "app_author",
            "made": "app_author",
            "built": "app_author",
            "krijuar": "app_author",
            "krijoi": "app_author",
            "autori": "app_author",
            "kush": "app_author",
            
            # Version
            "version": "app_version",
            "versioni": "app_version",
            "v2": "app_version",
            "v3": "app_version",
            
            # Files/stats
            "files": "file_counts",
            "lines": "total_lines",
            "skedarë": "file_counts",
            "rreshta": "total_lines",
            
            # Docker
            "docker": "docker_base_Dockerfile",
            "container": "docker_base_Dockerfile",
            "port": "exposed_ports",
            "ports": "exposed_ports",
            
            # Modules
            "module": "main_modules",
            "modules": "main_modules",
            "modul": "main_modules",
        }
        
        # Gjej topic-un e përshtatshëm
        matched_topic = None
        for keyword, topic in keyword_to_topic.items():
            if keyword in query_lower:
                matched_topic = topic
                break
        
        if not matched_topic:
            # Provojmë të gjejmë çdo fjalë në topics
            all_knowledge = self.learning_engine.get_all_knowledge()
            for topic in all_knowledge:
                topic_lower = topic.lower().replace("_", " ")
                for word in query_lower.split():
                    if len(word) > 3 and word in topic_lower:
                        matched_topic = topic
                        break
        
        if matched_topic:
            result = self.learning_engine.query(matched_topic)
            if result.get("success"):
                answer = result.get("answer")
                source = result.get("source", "")
                evidence = result.get("evidence", "")
                
                # Formato përgjigjen
                if isinstance(answer, list):
                    answer_str = ", ".join(str(a) for a in answer)
                elif isinstance(answer, dict):
                    answer_str = json.dumps(answer, indent=2)
                else:
                    answer_str = str(answer)
                
                return {
                    "answer": f"📚 {matched_topic}: {answer_str}\n\n📁 Source: {source}",
                    "source": source,
                    "evidence": evidence,
                    "confidence": result.get("confidence", 0.9)
                }
        
        return None
    
    def _get_math_suggestions(self, lang: str) -> List[str]:
        """Sugjerime për math"""
        suggestions = {
            "sq": ["15 + 27", "100 / 4", "25 * 3", "Sa bëjnë 50 - 18?"],
            "en": ["15 + 27", "100 / 4", "25 * 3", "What is 50 - 18?"],
            "de": ["15 + 27", "100 / 4", "25 * 3", "Was ist 50 - 18?"],
        }
        return suggestions.get(lang, suggestions["en"])
    
    def _get_general_suggestions(self, lang: str) -> List[str]:
        """Sugjerime të përgjithshme"""
        suggestions = {
            "sq": ["5 + 3", "Sa është ora?", "Çfarë dite është sot?", "10 km në mile"],
            "en": ["5 + 3", "What time is it?", "What day is today?", "10 km to miles"],
            "de": ["5 + 3", "Wie spät ist es?", "Welcher Tag ist heute?"],
        }
        return suggestions.get(lang, suggestions["en"])
    
    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Merr historinë"""
        return self.history[-limit:]
    
    def get_stats(self) -> Dict[str, Any]:
        """Merr statistikat"""
        return {
            **self.stats,
            "history_count": len(self.history),
            "supported_languages": len(self.i18n.get_supported_languages())
        }
    
    def clear_history(self):
        """Pastro historinë"""
        self.history = []


# Global instance
_real_chat_engine: Optional[RealChatEngine] = None


def get_real_chat_engine() -> RealChatEngine:
    """Merr instancën globale"""
    global _real_chat_engine
    if _real_chat_engine is None:
        _real_chat_engine = RealChatEngine()
    return _real_chat_engine

