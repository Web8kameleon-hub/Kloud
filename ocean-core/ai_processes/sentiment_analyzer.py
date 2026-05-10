"""
SENTIMENT ANALYZER - AI Process for Emotional Analysis
=======================================================
Analyzes text for emotional content, sentiment polarity, and mood detection.

Features:
- Multi-language sentiment detection
- Emotion classification (joy, anger, sadness, fear, surprise, disgust)
- Intensity scoring
- Aspect-based sentiment for specific topics
- Social media sentiment analysis
"""

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)


class SentimentPolarity(Enum):
    """Sentiment polarity classification"""

    VERY_POSITIVE = "very_positive"  # 0.8 to 1.0
    POSITIVE = "positive"  # 0.4 to 0.8
    NEUTRAL = "neutral"  # -0.2 to 0.4
    NEGATIVE = "negative"  # -0.6 to -0.2
    VERY_NEGATIVE = "very_negative"  # -1.0 to -0.6


class EmotionType(Enum):
    """Primary emotion classification (Ekman's 6 basic emotions + extras)"""

    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    TRUST = "trust"
    ANTICIPATION = "anticipation"
    NEUTRAL = "neutral"


@dataclass
class SentimentResult:
    """Result of sentiment analysis"""

    text: str
    polarity: SentimentPolarity
    polarity_score: float  # -1.0 to 1.0
    emotions: Dict[EmotionType, float]  # Emotion probabilities
    dominant_emotion: EmotionType
    intensity: float  # 0.0 to 1.0
    confidence: float
    aspects: Dict[str, float]  # Aspect-based sentiments
    language: str
    processing_time_ms: float
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text[:200] + "..." if len(self.text) > 200 else self.text,
            "polarity": self.polarity.value,
            "polarity_score": round(self.polarity_score, 3),
            "emotions": {e.value: round(v, 3) for e, v in self.emotions.items()},
            "dominant_emotion": self.dominant_emotion.value,
            "intensity": round(self.intensity, 3),
            "confidence": round(self.confidence, 3),
            "aspects": self.aspects,
            "language": self.language,
            "processing_time_ms": round(self.processing_time_ms, 2),
            "metadata": self.metadata,
        }


class SentimentAnalyzer:
    """
    Advanced Sentiment Analysis Engine

    Uses a combination of:
    - Lexicon-based analysis (AFINN, SentiWordNet style)
    - Pattern matching for context
    - Ollama LLM for complex analysis
    """

    # Sentiment lexicons (partial - extendable)
    POSITIVE_WORDS = {
        # English
        "good",
        "great",
        "excellent",
        "amazing",
        "wonderful",
        "fantastic",
        "awesome",
        "love",
        "happy",
        "joy",
        "beautiful",
        "perfect",
        "best",
        "brilliant",
        "outstanding",
        "superb",
        "magnificent",
        "delightful",
        "pleasant",
        "positive",
        "success",
        "win",
        "winner",
        "celebrate",
        # Albanian
        "mirë",
        "shkëlqyeshëm",
        "mrekullueshëm",
        "fantastik",
        "dashuri",
        "lumtur",
        "gëzim",
        "bukur",
        "perfekt",
        "më i mirë",
        "sukses",
        # Intensifiers
        "very",
        "extremely",
        "incredibly",
        "absolutely",
        "totally",
        "shumë",
        "jashtëzakonisht",
        "krejtësisht",
    }

    NEGATIVE_WORDS = {
        # English
        "bad",
        "terrible",
        "awful",
        "horrible",
        "hate",
        "angry",
        "sad",
        "disappointed",
        "frustrated",
        "annoying",
        "worst",
        "fail",
        "failure",
        "ugly",
        "disgusting",
        "pathetic",
        "useless",
        "boring",
        "stupid",
        "problem",
        "issue",
        "error",
        "bug",
        "crash",
        "broken",
        # Albanian
        "keq",
        "tmerrshëm",
        "i neveritshëm",
        "urrej",
        "i zemëruar",
        "i trishtuar",
        "zhgënjyer",
        "i mërzitur",
        "dështim",
        "gabim",
        # Negations
        "not",
        "no",
        "never",
        "nothing",
        "nuk",
        "jo",
        "asnjëherë",
    }

    EMOTION_PATTERNS = {
        EmotionType.JOY: [
            r"\b(happy|joy|excited|thrilled|delighted|glad|pleased)\b",
            r"\b(lumtur|gëzuar|i kënaqur|i gëzuar)\b",
            r"[😀😃😄😁😆🥹😊😍🥰😘🤩]",
        ],
        EmotionType.SADNESS: [
            r"\b(sad|unhappy|depressed|miserable|heartbroken|crying|tears)\b",
            r"\b(i trishtuar|i mërzitur|dëshpëruar)\b",
            r"[😢😭😿💔🥺😞😔😥]",
        ],
        EmotionType.ANGER: [
            r"\b(angry|furious|outraged|mad|annoyed|irritated|hate)\b",
            r"\b(i zemëruar|i tërbuar|urrej)\b",
            r"[😠😡🤬👿💢]",
        ],
        EmotionType.FEAR: [
            r"\b(scared|afraid|terrified|anxious|worried|nervous|panic)\b",
            r"\b(i frikësuar|i shqetësuar|i ankthshëm)\b",
            r"[😨😰😱🫣😬]",
        ],
        EmotionType.SURPRISE: [
            r"\b(surprised|amazed|shocked|astonished|stunned|wow)\b",
            r"\b(i habitur|i çuditur|i befasuar)\b",
            r"[😮😯😲🤯😳]",
        ],
        EmotionType.DISGUST: [r"\b(disgusted|gross|yuck|revolting|sick|nasty)\b", r"\b(i neveritshëm|i pakëndshëm)\b", r"[🤢🤮😷🤧]"],
    }

    def __init__(self, ollama_host: Optional[str] = None):
        self.ollama_host = ollama_host or "http://kloud-clx:11434"
        self._initialized = False
        logger.info("🎭 SentimentAnalyzer initialized")

    async def initialize(self):
        """Initialize the analyzer (load models, etc.)"""
        if self._initialized:
            return
        self._initialized = True
        logger.info("✅ SentimentAnalyzer ready")

    async def analyze(self, text: str, language: str = "auto", use_llm: bool = True, extract_aspects: bool = False) -> SentimentResult:
        """
        Analyze sentiment of text

        Args:
            text: Text to analyze
            language: Language code or 'auto' for detection
            use_llm: Whether to use LLM for deeper analysis
            extract_aspects: Extract aspect-based sentiments
        """
        start_time = datetime.now()

        # Detect language if auto
        if language == "auto":
            language = self._detect_language(text)

        # Lexicon-based analysis
        polarity_score = self._lexicon_analysis(text)

        # Emotion detection
        emotions = self._detect_emotions(text)

        # Get dominant emotion
        dominant_emotion = max(emotions, key=emotions.get)

        # Calculate intensity
        intensity = self._calculate_intensity(text, polarity_score)

        # Aspect-based analysis
        aspects = {}
        if extract_aspects:
            aspects = self._extract_aspect_sentiments(text)

        # LLM enhancement (if enabled and complex text)
        if use_llm and len(text) > 50:
            llm_result = await self._llm_enhance(text, language)
            if llm_result:
                # Blend results
                polarity_score = (polarity_score + llm_result.get("polarity", polarity_score)) / 2
                if llm_result.get("emotions"):
                    for emotion, score in llm_result["emotions"].items():
                        if emotion in emotions:
                            emotions[emotion] = (emotions[emotion] + score) / 2

        # Determine polarity category
        polarity = self._score_to_polarity(polarity_score)

        # Calculate confidence
        confidence = self._calculate_confidence(text, emotions, polarity_score)

        processing_time = (datetime.now() - start_time).total_seconds() * 1000

        return SentimentResult(
            text=text,
            polarity=polarity,
            polarity_score=polarity_score,
            emotions=emotions,
            dominant_emotion=dominant_emotion,
            intensity=intensity,
            confidence=confidence,
            aspects=aspects,
            language=language,
            processing_time_ms=processing_time,
            metadata={"word_count": len(text.split()), "used_llm": use_llm, "analyzer_version": "1.0.0"},
        )

    def _lexicon_analysis(self, text: str) -> float:
        """Basic lexicon-based sentiment analysis"""
        text_lower = text.lower()
        words = set(re.findall(r"\b\w+\b", text_lower))

        positive_count = len(words & self.POSITIVE_WORDS)
        negative_count = len(words & self.NEGATIVE_WORDS)

        total = positive_count + negative_count
        if total == 0:
            return 0.0

        # Score from -1 to 1
        score = (positive_count - negative_count) / max(total, 1)

        # Adjust for negations
        negation_patterns = [r"\bnot\s+\w+", r"\bno\s+\w+", r"\bnuk\s+\w+"]
        for pattern in negation_patterns:
            if re.search(pattern, text_lower):
                score *= 0.5  # Reduce certainty when negations present

        return max(-1.0, min(1.0, score))

    def _detect_emotions(self, text: str) -> Dict[EmotionType, float]:
        """Detect emotions in text using pattern matching"""
        emotions = {e: 0.0 for e in EmotionType}
        text_lower = text.lower()

        for emotion, patterns in self.EMOTION_PATTERNS.items():
            for pattern in patterns:
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                if matches:
                    emotions[emotion] += 0.2 * len(matches)

        # Normalize
        total = sum(emotions.values())
        if total > 0:
            emotions = {e: v / total for e, v in emotions.items()}
        else:
            emotions[EmotionType.NEUTRAL] = 1.0

        return emotions

    def _calculate_intensity(self, text: str, polarity: float) -> float:
        """Calculate emotional intensity"""
        # Factors: caps, exclamation marks, intensifiers, emoji
        intensity = abs(polarity)

        # Caps boost
        caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        if caps_ratio > 0.3:
            intensity += 0.2

        # Exclamation/question marks
        if "!" in text:
            intensity += 0.1 * text.count("!")

        # Multiple punctuation
        if re.search(r"[!?]{2,}", text):
            intensity += 0.15

        return min(1.0, intensity)

    def _score_to_polarity(self, score: float) -> SentimentPolarity:
        """Convert numeric score to polarity enum"""
        if score >= 0.6:
            return SentimentPolarity.VERY_POSITIVE
        elif score >= 0.2:
            return SentimentPolarity.POSITIVE
        elif score >= -0.2:
            return SentimentPolarity.NEUTRAL
        elif score >= -0.6:
            return SentimentPolarity.NEGATIVE
        else:
            return SentimentPolarity.VERY_NEGATIVE

    def _calculate_confidence(self, text: str, emotions: Dict[EmotionType, float], polarity: float) -> float:
        """Calculate confidence in the analysis"""
        # Factors: text length, clarity of signals
        confidence = 0.5

        # Longer text = more confidence
        word_count = len(text.split())
        if word_count > 10:
            confidence += 0.1
        if word_count > 50:
            confidence += 0.1

        # Strong polarity = more confidence
        if abs(polarity) > 0.5:
            confidence += 0.15

        # Clear dominant emotion = more confidence
        if emotions:
            max_emotion = max(emotions.values())
            if max_emotion > 0.5:
                confidence += 0.15

        return min(1.0, confidence)

    def _detect_language(self, text: str) -> str:
        """Simple language detection"""
        albanian_chars = set("ëçÇË")
        albanian_words = {"dhe", "është", "për", "nga", "me", "si", "në", "mund", "nuk"}

        text_words = set(text.lower().split())

        if any(c in text for c in albanian_chars):
            return "sq"
        if len(text_words & albanian_words) >= 2:
            return "sq"

        return "en"

    def _extract_aspect_sentiments(self, text: str) -> Dict[str, float]:
        """Extract aspect-based sentiments"""
        # Simple keyword-based extraction
        aspects = {}

        aspect_keywords = {
            "quality": ["quality", "cilësi", "good", "bad", "mirë", "keq"],
            "price": ["price", "çmim", "expensive", "cheap", "shtrenjtë", "lirë"],
            "service": ["service", "shërbim", "support", "help", "ndihmë"],
            "speed": ["fast", "slow", "quick", "shpejtë", "ngadalë"],
        }

        text_lower = text.lower()
        for aspect, keywords in aspect_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    # Simple context window sentiment
                    idx = text_lower.find(keyword)
                    context = text_lower[max(0, idx - 30) : idx + 30]
                    aspects[aspect] = self._lexicon_analysis(context)
                    break

        return aspects

    async def _llm_enhance(self, text: str, language: str) -> Optional[Dict[str, Any]]:
        """Use LLM for deeper sentiment analysis"""
        try:
            import httpx

            prompt = f"""Analyze the sentiment of this text. Return JSON only.
Text: "{text[:500]}"

Return format:
{{"polarity": 0.5, "emotions": {{"joy": 0.3, "sadness": 0.1}}, "summary": "brief summary"}}

Polarity: -1 (very negative) to 1 (very positive)
Emotions: joy, sadness, anger, fear, surprise, disgust (values 0-1)"""

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.ollama_host}/api/generate",
                    json={"model": "llama3.1:8b", "prompt": prompt, "stream": False, "options": {"temperature": 0.3}},
                )

                if response.status_code == 200:
                    result = response.json()
                    # Parse JSON from response
                    import json

                    try:
                        return json.loads(result.get("response", "{}"))
                    except:
                        return None
        except Exception as e:
            logger.debug(f"LLM enhancement failed: {e}")

        return None

    async def batch_analyze(self, texts: List[str], **kwargs) -> List[SentimentResult]:
        """Analyze multiple texts in parallel"""
        tasks = [self.analyze(text, **kwargs) for text in texts]
        return await asyncio.gather(*tasks)


# Singleton instance
_sentiment_analyzer: Optional[SentimentAnalyzer] = None


def get_sentiment_analyzer() -> SentimentAnalyzer:
    """Get or create sentiment analyzer instance"""
    global _sentiment_analyzer
    if _sentiment_analyzer is None:
        _sentiment_analyzer = SentimentAnalyzer()
    return _sentiment_analyzer
