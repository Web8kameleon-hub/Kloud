"""
TEXT CLASSIFIER - Multi-label Text Classification AI Process
=============================================================
Classifies text into predefined categories using ML and rule-based approaches.

Features:
- Multi-label classification
- Topic detection
- Intent classification
- Custom category support
- Confidence scoring
- Domain detection
"""

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Set
from datetime import datetime

logger = logging.getLogger(__name__)


class TextCategory(Enum):
    """Predefined text categories"""

    TECHNOLOGY = "technology"
    BUSINESS = "business"
    SCIENCE = "science"
    HEALTH = "health"
    POLITICS = "politics"
    SPORTS = "sports"
    ENTERTAINMENT = "entertainment"
    EDUCATION = "education"
    FINANCE = "finance"
    LEGAL = "legal"
    NEWS = "news"
    OPINION = "opinion"
    TUTORIAL = "tutorial"
    QUESTION = "question"
    SUPPORT = "support"
    MARKETING = "marketing"
    PERSONAL = "personal"
    OTHER = "other"


class TextDomain(Enum):
    """Text domains"""

    INDUSTRIAL = "industrial"
    MEDICAL = "medical"
    LEGAL = "legal"
    TECHNICAL = "technical"
    ACADEMIC = "academic"
    CASUAL = "casual"
    FORMAL = "formal"
    CREATIVE = "creative"


@dataclass
class Classification:
    """Single classification result"""

    category: str
    confidence: float
    evidence: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {"category": self.category, "confidence": round(self.confidence, 3), "evidence": self.evidence[:3]}


@dataclass
class ClassificationResult:
    """Result of text classification"""

    text_preview: str
    primary_category: str
    all_categories: List[Classification]
    domain: str
    topics: List[str]
    is_question: bool
    is_formal: bool
    word_count: int
    processing_time_ms: float
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "primary_category": self.primary_category,
            "categories": [c.to_dict() for c in self.all_categories],
            "domain": self.domain,
            "topics": self.topics,
            "is_question": self.is_question,
            "is_formal": self.is_formal,
            "word_count": self.word_count,
            "processing_time_ms": round(self.processing_time_ms, 2),
            "metadata": self.metadata,
        }


class TextClassifier:
    """
    Multi-label Text Classification Engine

    Uses keyword matching, patterns, and LLM for classification
    """

    # Keywords for each category
    CATEGORY_KEYWORDS = {
        TextCategory.TECHNOLOGY: [
            "software",
            "hardware",
            "computer",
            "programming",
            "code",
            "api",
            "algorithm",
            "database",
            "server",
            "cloud",
            "ai",
            "machine learning",
            "neural",
            "app",
            "mobile",
            "web",
            "internet",
            "network",
            "cyber",
            "robot",
            "automation",
            "iot",
            "blockchain",
            "crypto",
            "digital",
        ],
        TextCategory.BUSINESS: [
            "company",
            "market",
            "revenue",
            "profit",
            "sales",
            "customer",
            "strategy",
            "management",
            "ceo",
            "startup",
            "investment",
            "funding",
            "growth",
            "enterprise",
            "b2b",
            "b2c",
            "roi",
            "kpi",
            "quarter",
        ],
        TextCategory.SCIENCE: [
            "research",
            "study",
            "experiment",
            "theory",
            "hypothesis",
            "discovery",
            "scientist",
            "laboratory",
            "physics",
            "chemistry",
            "biology",
            "astronomy",
            "quantum",
            "molecular",
            "particle",
        ],
        TextCategory.HEALTH: [
            "medical",
            "health",
            "disease",
            "treatment",
            "patient",
            "doctor",
            "hospital",
            "medicine",
            "symptom",
            "diagnosis",
            "therapy",
            "vaccine",
            "clinical",
            "wellness",
            "mental health",
            "nutrition",
        ],
        TextCategory.FINANCE: [
            "stock",
            "investment",
            "bank",
            "loan",
            "credit",
            "mortgage",
            "interest rate",
            "forex",
            "trading",
            "portfolio",
            "dividend",
            "inflation",
            "budget",
            "tax",
            "financial",
            "economy",
        ],
        TextCategory.EDUCATION: [
            "learn",
            "study",
            "school",
            "university",
            "course",
            "student",
            "teacher",
            "curriculum",
            "degree",
            "education",
            "training",
            "classroom",
            "lecture",
            "exam",
            "graduate",
        ],
        TextCategory.LEGAL: [
            "law",
            "legal",
            "court",
            "attorney",
            "lawyer",
            "judge",
            "regulation",
            "compliance",
            "contract",
            "lawsuit",
            "litigation",
            "intellectual property",
            "patent",
            "copyright",
        ],
        TextCategory.SUPPORT: [
            "help",
            "problem",
            "issue",
            "error",
            "bug",
            "fix",
            "support",
            "troubleshoot",
            "solution",
            "assistance",
            "technical support",
        ],
        TextCategory.TUTORIAL: [
            "how to",
            "tutorial",
            "guide",
            "step by step",
            "instructions",
            "learn how",
            "walkthrough",
            "example",
            "demonstration",
        ],
        TextCategory.MARKETING: [
            "brand",
            "campaign",
            "advertising",
            "promotion",
            "seo",
            "social media",
            "content",
            "engagement",
            "conversion",
            "leads",
        ],
    }

    # Domain indicators
    DOMAIN_INDICATORS = {
        TextDomain.INDUSTRIAL: [
            "manufacturing",
            "production",
            "factory",
            "assembly",
            "industrial",
            "machinery",
            "automation",
            "scada",
            "plc",
            "process control",
        ],
        TextDomain.MEDICAL: [
            "patient",
            "diagnosis",
            "treatment",
            "clinical",
            "pharmaceutical",
            "surgery",
            "medical device",
            "hospital",
            "healthcare",
        ],
        TextDomain.LEGAL: ["whereas", "hereby", "pursuant", "jurisdiction", "plaintiff", "defendant", "statutory", "contractual"],
        TextDomain.ACADEMIC: [
            "methodology",
            "literature review",
            "hypothesis",
            "findings",
            "abstract",
            "citation",
            "peer review",
            "thesis",
        ],
        TextDomain.TECHNICAL: ["specification", "implementation", "architecture", "module", "interface", "protocol", "configuration"],
    }

    def __init__(self, ollama_host: Optional[str] = None):
        self.ollama_host = ollama_host or "http://kloud-clx:11434"
        self._initialized = False
        logger.info("📊 TextClassifier initialized")

    async def initialize(self):
        """Initialize the classifier"""
        if self._initialized:
            return
        self._initialized = True
        logger.info("✅ TextClassifier ready")

    async def classify(self, text: str, custom_categories: Optional[List[str]] = None, use_llm: bool = True) -> ClassificationResult:
        """
        Classify text into categories

        Args:
            text: Text to classify
            custom_categories: Custom category labels
            use_llm: Use LLM for enhanced classification
        """
        start_time = datetime.now()

        text_lower = text.lower()
        words = text_lower.split()

        # Classify into categories
        classifications = self._classify_categories(text_lower)

        # Detect domain
        domain = self._detect_domain(text_lower)

        # Extract topics
        topics = self._extract_topics(text)

        # Check properties
        is_question = self._is_question(text)
        is_formal = self._is_formal(text)

        # LLM enhancement
        if use_llm and len(classifications) < 2:
            llm_categories = await self._llm_classify(text)
            for cat, conf in llm_categories:
                if not any(c.category == cat for c in classifications):
                    classifications.append(Classification(category=cat, confidence=conf, evidence=["LLM classification"]))

        # Sort by confidence
        classifications.sort(key=lambda c: -c.confidence)

        primary = classifications[0].category if classifications else "other"

        processing_time = (datetime.now() - start_time).total_seconds() * 1000

        return ClassificationResult(
            text_preview=text[:200] + "..." if len(text) > 200 else text,
            primary_category=primary,
            all_categories=classifications[:5],
            domain=domain.value if isinstance(domain, TextDomain) else domain,
            topics=topics,
            is_question=is_question,
            is_formal=is_formal,
            word_count=len(words),
            processing_time_ms=processing_time,
        )

    def _classify_categories(self, text_lower: str) -> List[Classification]:
        """Classify text using keyword matching"""
        classifications = []

        for category, keywords in self.CATEGORY_KEYWORDS.items():
            matches = []
            for keyword in keywords:
                if keyword in text_lower:
                    matches.append(keyword)

            if matches:
                confidence = min(0.95, 0.3 + (len(matches) * 0.1))
                classifications.append(Classification(category=category.value, confidence=confidence, evidence=matches))

        return classifications

    def _detect_domain(self, text_lower: str) -> TextDomain:
        """Detect text domain"""
        max_score = 0
        detected_domain = TextDomain.CASUAL

        for domain, indicators in self.DOMAIN_INDICATORS.items():
            score = sum(1 for ind in indicators if ind in text_lower)
            if score > max_score:
                max_score = score
                detected_domain = domain

        # Check formality
        formal_markers = ["therefore", "furthermore", "consequently", "hereby"]
        if any(m in text_lower for m in formal_markers):
            if detected_domain == TextDomain.CASUAL:
                detected_domain = TextDomain.FORMAL

        return detected_domain

    def _extract_topics(self, text: str) -> List[str]:
        """Extract main topics from text"""
        topics = []

        # Look for capitalized phrases
        phrases = re.findall(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b", text)
        topics.extend(phrases[:3])

        # Look for quoted terms
        quoted = re.findall(r'"([^"]+)"', text)
        topics.extend(quoted[:2])

        return list(set(topics))[:5]

    def _is_question(self, text: str) -> bool:
        """Check if text is a question"""
        question_starters = [
            "what",
            "why",
            "how",
            "when",
            "where",
            "who",
            "which",
            "can",
            "could",
            "would",
            "should",
            "is",
            "are",
            "do",
            "does",
        ]
        first_word = text.split()[0].lower() if text else ""
        return "?" in text or first_word in question_starters

    def _is_formal(self, text: str) -> bool:
        """Check if text is formal"""
        informal_markers = ["lol", "omg", "btw", "idk", "tbh", "gonna", "wanna"]
        formal_markers = ["hereby", "whereas", "pursuant", "therefore", "furthermore"]

        text_lower = text.lower()

        informal_count = sum(1 for m in informal_markers if m in text_lower)
        formal_count = sum(1 for m in formal_markers if m in text_lower)

        return formal_count > informal_count

    async def _llm_classify(self, text: str) -> List[tuple]:
        """Use LLM for classification"""
        try:
            import httpx

            categories = ", ".join([c.value for c in TextCategory])

            prompt = f"""Classify this text into ONE primary category.
Categories: {categories}

Text: {text[:1000]}

Return ONLY the category name:"""

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.ollama_host}/api/generate",
                    json={"model": "llama3.1:8b", "prompt": prompt, "stream": False, "options": {"temperature": 0.1, "num_predict": 20}},
                )

                if response.status_code == 200:
                    result = response.json()
                    category = result.get("response", "").strip().lower()

                    # Validate category
                    valid_categories = [c.value for c in TextCategory]
                    if category in valid_categories:
                        return [(category, 0.8)]
        except Exception as e:
            logger.debug(f"LLM classification failed: {e}")

        return []


# Singleton instance
_text_classifier: Optional[TextClassifier] = None


def get_text_classifier() -> TextClassifier:
    """Get or create text classifier instance"""
    global _text_classifier
    if _text_classifier is None:
        _text_classifier = TextClassifier()
    return _text_classifier
