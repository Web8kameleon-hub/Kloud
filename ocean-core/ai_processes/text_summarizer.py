"""
TEXT SUMMARIZER - AI Process for Intelligent Summarization
==========================================================
Generates concise summaries of long texts using multiple strategies.

Features:
- Extractive summarization (key sentence extraction)
- Abstractive summarization (LLM-powered rewriting)
- Multi-document summarization
- Configurable summary length
- Key point extraction
- TL;DR generation
"""

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import asyncio
from collections import Counter
import math

logger = logging.getLogger(__name__)


class SummaryType(Enum):
    """Types of summarization"""
    EXTRACTIVE = "extractive"    # Extract key sentences
    ABSTRACTIVE = "abstractive"  # Generate new text
    HYBRID = "hybrid"            # Combination of both
    BULLET_POINTS = "bullet_points"  # Key points as bullets
    TLDR = "tldr"                # Very short summary


@dataclass
class SummaryResult:
    """Result of text summarization"""
    original_text: str
    summary: str
    summary_type: SummaryType
    compression_ratio: float  # 0.1 = 10% of original
    key_points: List[str]
    key_sentences: List[str]
    word_count_original: int
    word_count_summary: int
    confidence: float
    language: str
    processing_time_ms: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "summary": self.summary,
            "summary_type": self.summary_type.value,
            "compression_ratio": round(self.compression_ratio, 3),
            "key_points": self.key_points,
            "key_sentences": self.key_sentences[:3],  # Top 3
            "word_count": {
                "original": self.word_count_original,
                "summary": self.word_count_summary
            },
            "confidence": round(self.confidence, 3),
            "language": self.language,
            "processing_time_ms": round(self.processing_time_ms, 2),
            "metadata": self.metadata
        }


class TextSummarizer:
    """
    Advanced Text Summarization Engine
    
    Combines:
    - TF-IDF based extractive summarization
    - TextRank-style sentence scoring
    - LLM-powered abstractive summarization
    """
    
    # Common stop words (English + Albanian)
    STOP_WORDS = {
        # English
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "must", "shall", "can", "need", "dare",
        "to", "of", "in", "for", "on", "with", "at", "by", "from", "as",
        "into", "through", "during", "before", "after", "above", "below",
        "this", "that", "these", "those", "it", "its", "itself",
        "i", "me", "my", "myself", "we", "our", "ours", "ourselves",
        "you", "your", "yours", "yourself", "yourselves",
        "he", "him", "his", "himself", "she", "her", "hers", "herself",
        "they", "them", "their", "theirs", "themselves",
        "what", "which", "who", "whom", "when", "where", "why", "how",
        "all", "each", "every", "both", "few", "more", "most", "other",
        "some", "such", "no", "nor", "not", "only", "own", "same", "so",
        "than", "too", "very", "just", "also", "now", "and", "but", "or",
        # Albanian
        "dhe", "ose", "por", "megjithatë", "është", "janë", "ishte", "ishin",
        "ka", "kanë", "kishte", "kishin", "do", "të", "në", "për", "me",
        "nga", "si", "kjo", "ky", "këta", "këto", "ai", "ajo", "ata", "ato",
        "unë", "ti", "ne", "ju", "një", "disa", "shumë", "pak", "çdo"
    }
    
    def __init__(self, ollama_host: Optional[str] = None):
        self.ollama_host = ollama_host or "http://kloud-ollama:11434"
        self._initialized = False
        logger.info("📝 TextSummarizer initialized")
    
    async def initialize(self):
        """Initialize the summarizer"""
        if self._initialized:
            return
        self._initialized = True
        logger.info("✅ TextSummarizer ready")
    
    async def summarize(
        self,
        text: str,
        summary_type: SummaryType = SummaryType.HYBRID,
        target_ratio: float = 0.3,  # Target 30% of original
        max_sentences: int = 5,
        language: str = "auto"
    ) -> SummaryResult:
        """
        Summarize text
        
        Args:
            text: Text to summarize
            summary_type: Type of summarization
            target_ratio: Target compression ratio (0.1-0.5)
            max_sentences: Maximum sentences in summary
            language: Language code or 'auto'
        """
        start_time = datetime.now()
        
        # Preprocess
        sentences = self._split_sentences(text)
        word_count_original = len(text.split())
        
        # Detect language
        if language == "auto":
            language = self._detect_language(text)
        
        # Extract key sentences (extractive)
        scored_sentences = self._score_sentences(sentences, text)
        key_sentences = [s for s, _ in sorted(scored_sentences, key=lambda x: -x[1])[:max_sentences]]
        
        # Extract key points
        key_points = self._extract_key_points(text, sentences)
        
        # Generate summary based on type
        if summary_type == SummaryType.EXTRACTIVE:
            summary = " ".join(key_sentences)
        elif summary_type == SummaryType.BULLET_POINTS:
            summary = "\n".join([f"• {point}" for point in key_points])
        elif summary_type == SummaryType.TLDR:
            summary = await self._generate_tldr(text, language)
        elif summary_type == SummaryType.ABSTRACTIVE:
            summary = await self._abstractive_summarize(text, language, target_ratio)
        else:  # HYBRID
            extractive = " ".join(key_sentences[:3])
            abstractive = await self._abstractive_summarize(text, language, target_ratio)
            summary = abstractive if abstractive else extractive
        
        word_count_summary = len(summary.split())
        compression_ratio = word_count_summary / max(word_count_original, 1)
        
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return SummaryResult(
            original_text=text[:500] + "..." if len(text) > 500 else text,
            summary=summary,
            summary_type=summary_type,
            compression_ratio=compression_ratio,
            key_points=key_points,
            key_sentences=key_sentences,
            word_count_original=word_count_original,
            word_count_summary=word_count_summary,
            confidence=self._calculate_confidence(text, summary),
            language=language,
            processing_time_ms=processing_time,
            metadata={
                "sentence_count": len(sentences),
                "target_ratio": target_ratio,
                "summarizer_version": "1.0.0"
            }
        )
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Handle abbreviations
        text = re.sub(r'(Mr|Mrs|Ms|Dr|Prof|Inc|Ltd|etc)\. ', r'\1@ ', text)
        
        # Split on sentence boundaries
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        # Restore abbreviations
        sentences = [s.replace('@', '.') for s in sentences]
        
        # Filter short/empty
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        
        return sentences
    
    def _score_sentences(
        self,
        sentences: List[str],
        full_text: str
    ) -> List[Tuple[str, float]]:
        """Score sentences for importance using TF-IDF-like approach"""
        if not sentences:
            return []
        
        # Calculate word frequencies
        word_freq = Counter()
        for sentence in sentences:
            words = self._tokenize(sentence)
            word_freq.update(words)
        
        # Score each sentence
        scored = []
        for i, sentence in enumerate(sentences):
            score = 0.0
            words = self._tokenize(sentence)
            
            # Word frequency score
            for word in words:
                if word not in self.STOP_WORDS:
                    # TF-IDF-like scoring
                    tf = word_freq[word] / max(sum(word_freq.values()), 1)
                    score += tf
            
            # Normalize by length
            score = score / max(len(words), 1)
            
            # Position bonus (first/last sentences often important)
            if i == 0:
                score *= 1.5
            elif i == len(sentences) - 1:
                score *= 1.2
            elif i < 3:
                score *= 1.1
            
            # Length penalty (avoid very long or very short)
            if 10 <= len(words) <= 30:
                score *= 1.1
            
            scored.append((sentence, score))
        
        return scored
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into words"""
        words = re.findall(r'\b\w+\b', text.lower())
        return [w for w in words if len(w) > 2]
    
    def _extract_key_points(
        self,
        text: str,
        sentences: List[str]
    ) -> List[str]:
        """Extract key points from text"""
        key_points = []
        
        # Look for bullet points or numbered items
        bullet_patterns = [
            r'[•\-\*]\s*(.+)',
            r'\d+[.)]\s*(.+)',
            r'(?:First|Second|Third|Finally|Moreover|Additionally)[,:]?\s+(.+)',
        ]
        
        for pattern in bullet_patterns:
            matches = re.findall(pattern, text, re.MULTILINE)
            key_points.extend(matches[:5])
        
        # If no structured points, extract from top sentences
        if not key_points:
            scored = self._score_sentences(sentences, text)
            top_sentences = [s for s, _ in sorted(scored, key=lambda x: -x[1])[:4]]
            key_points = [self._shorten_sentence(s) for s in top_sentences]
        
        return key_points[:5]
    
    def _shorten_sentence(self, sentence: str, max_words: int = 15) -> str:
        """Shorten a sentence to key phrase"""
        words = sentence.split()
        if len(words) <= max_words:
            return sentence
        return " ".join(words[:max_words]) + "..."
    
    async def _generate_tldr(self, text: str, language: str) -> str:
        """Generate very short TL;DR summary"""
        # Try LLM first
        llm_summary = await self._llm_summarize(text, language, "one sentence")
        if llm_summary:
            return llm_summary
        
        # Fallback: first sentence + key words
        sentences = self._split_sentences(text)
        if sentences:
            return self._shorten_sentence(sentences[0], max_words=20)
        
        return text[:100] + "..."
    
    async def _abstractive_summarize(
        self,
        text: str,
        language: str,
        target_ratio: float
    ) -> str:
        """Generate abstractive summary using LLM"""
        target_words = int(len(text.split()) * target_ratio)
        
        llm_summary = await self._llm_summarize(
            text,
            language,
            f"approximately {target_words} words"
        )
        
        if llm_summary:
            return llm_summary
        
        # Fallback to extractive
        sentences = self._split_sentences(text)
        scored = self._score_sentences(sentences, text)
        top = [s for s, _ in sorted(scored, key=lambda x: -x[1])[:3]]
        return " ".join(top)
    
    async def _llm_summarize(
        self,
        text: str,
        language: str,
        length_hint: str
    ) -> Optional[str]:
        """Use LLM for summarization"""
        try:
            import httpx
            
            lang_instruction = "in Albanian" if language == "sq" else "in English"
            
            prompt = f"""Summarize this text {lang_instruction}, {length_hint}:

{text[:2000]}

Summary:"""
            
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(
                    f"{self.ollama_host}/api/generate",
                    json={
                        "model": "llama3.1:8b",
                        "prompt": prompt,
                        "stream": False,
                        "options": {"temperature": 0.5, "num_predict": 200}
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get("response", "").strip()
        except Exception as e:
            logger.debug(f"LLM summarization failed: {e}")
        
        return None
    
    def _calculate_confidence(self, original: str, summary: str) -> float:
        """Calculate confidence in summary quality"""
        confidence = 0.6
        
        # Length check
        orig_words = len(original.split())
        sum_words = len(summary.split())
        
        if orig_words > 50 and sum_words > 10:
            confidence += 0.1
        
        # Compression ratio check
        ratio = sum_words / max(orig_words, 1)
        if 0.1 <= ratio <= 0.4:
            confidence += 0.15
        
        # Content overlap (key words preserved)
        orig_keywords = set(self._tokenize(original)) - self.STOP_WORDS
        sum_keywords = set(self._tokenize(summary)) - self.STOP_WORDS
        
        if orig_keywords:
            overlap = len(orig_keywords & sum_keywords) / len(orig_keywords)
            confidence += overlap * 0.15
        
        return min(1.0, confidence)
    
    def _detect_language(self, text: str) -> str:
        """Simple language detection"""
        albanian_indicators = {"dhe", "është", "për", "nga", "me", "mund", "nuk", "ë", "ç"}
        words = set(text.lower().split())
        
        if len(words & albanian_indicators) >= 2 or "ë" in text.lower():
            return "sq"
        return "en"
    
    async def summarize_documents(
        self,
        documents: List[str],
        **kwargs
    ) -> SummaryResult:
        """Summarize multiple documents together"""
        combined = "\n\n---\n\n".join(documents)
        return await self.summarize(combined, **kwargs)


# Singleton instance
_text_summarizer: Optional[TextSummarizer] = None


def get_text_summarizer() -> TextSummarizer:
    """Get or create text summarizer instance"""
    global _text_summarizer
    if _text_summarizer is None:
        _text_summarizer = TextSummarizer()
    return _text_summarizer

