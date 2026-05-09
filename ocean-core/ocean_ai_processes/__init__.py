"""
🧠 OCEAN AI PROCESSES - Professional NLP & ML Suite
====================================================

Advanced AI processing capabilities for Ocean Core:
- Sentiment Analysis (multi-language)
- Text Summarization (extractive & abstractive)
- Named Entity Recognition (NER)
- Text Classification (multi-label)
- Code Analysis & Metrics
- Language Detection (100+ languages)
- Intent Classification (context-aware)
- Topic Modeling (keyword & LDA)

Version: 1.0.0
Author: Kloud Team
Updated: 2026-02-23
"""

from typing import Optional

# Lazy imports for performance
_sentiment_analyzer = None
_text_summarizer = None
_entity_extractor = None
_text_classifier = None
_code_analyzer = None
_language_detector = None
_intent_classifier = None
_topic_modeler = None


def get_sentiment_analyzer(language: str = "en", use_deep_learning: bool = False):
    """Get or create sentiment analyzer instance"""
    global _sentiment_analyzer
    if _sentiment_analyzer is None:
        from .sentiment_analyzer import SentimentAnalyzer
        _sentiment_analyzer = SentimentAnalyzer(language, use_deep_learning)
    return _sentiment_analyzer


def get_text_summarizer(use_transformers: bool = False):
    """Get or create text summarizer instance"""
    global _text_summarizer
    if _text_summarizer is None:
        from .text_summarizer import TextSummarizer
        _text_summarizer = TextSummarizer(use_transformers)
    return _text_summarizer


def get_entity_extractor(language: str = "en", use_spacy: bool = False):
    """Get or create entity extractor instance"""
    global _entity_extractor
    if _entity_extractor is None:
        from .entity_extractor import EntityExtractor
        _entity_extractor = EntityExtractor(language, use_spacy)
    return _entity_extractor


def get_text_classifier(scheme: str = "topic", use_ml: bool = False):
    """Get or create text classifier instance"""
    global _text_classifier
    if _text_classifier is None:
        from .text_classifier import TextClassifier
        _text_classifier = TextClassifier(scheme, use_ml)
    return _text_classifier


def get_code_analyzer():
    """Get or create code analyzer instance"""
    global _code_analyzer
    if _code_analyzer is None:
        from .code_analyzer import CodeAnalyzer
        _code_analyzer = CodeAnalyzer()
    return _code_analyzer


def get_language_detector(use_deep_learning: bool = False):
    """Get or create language detector instance"""
    global _language_detector
    if _language_detector is None:
        from .language_detector import LanguageDetector
        _language_detector = LanguageDetector(use_deep_learning)
    return _language_detector


def get_intent_classifier(use_ml: bool = False):
    """Get or create intent classifier instance"""
    global _intent_classifier
    if _intent_classifier is None:
        from .intent_classifier import IntentClassifier
        _intent_classifier = IntentClassifier(use_ml)
    return _intent_classifier


def get_topic_modeler(method: str = "keyword", num_topics: int = 5):
    """Get or create topic modeler instance"""
    global _topic_modeler
    if _topic_modeler is None:
        from .topic_modeler import TopicModeler
        _topic_modeler = TopicModeler(method, num_topics)
    return _topic_modeler


# Export result classes for type hints
from .code_analyzer import CodeMetrics
from .entity_extractor import Entity, ExtractionResult
from .intent_classifier import IntentResult
from .language_detector import LanguageDetectionResult
from .sentiment_analyzer import SentimentResult
from .text_classifier import ClassificationResult
from .text_summarizer import SummaryResult
from .topic_modeler import TopicModelResult

__all__ = [
    # Factory functions
    "get_sentiment_analyzer",
    "get_text_summarizer",
    "get_entity_extractor",
    "get_text_classifier",
    "get_code_analyzer",
    "get_language_detector",
    "get_intent_classifier",
    "get_topic_modeler",
    # Result classes
    "SentimentResult",
    "SummaryResult",
    "Entity",
    "ExtractionResult",
    "ClassificationResult",
    "CodeMetrics",
    "LanguageDetectionResult",
    "IntentResult",
    "TopicModelResult",
]

__version__ = "1.0.0"

