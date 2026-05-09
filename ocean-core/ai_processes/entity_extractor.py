"""
ENTITY EXTRACTOR - Named Entity Recognition (NER) AI Process
=============================================================
Extracts named entities from text: people, organizations, locations, dates, etc.

Features:
- Multiple entity types (PERSON, ORG, LOCATION, DATE, etc.)
- Pattern-based extraction
- LLM-enhanced recognition
- Entity linking and deduplication
- Multi-language support (English + Albanian)
"""

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)


class EntityType(Enum):
    """Types of named entities"""
    PERSON = "PERSON"           # People names
    ORGANIZATION = "ORG"        # Companies, institutions
    LOCATION = "LOC"            # Places, cities, countries
    GPE = "GPE"                 # Geo-political entities
    DATE = "DATE"               # Dates and times
    TIME = "TIME"               # Time expressions
    MONEY = "MONEY"             # Monetary values
    PERCENT = "PERCENT"         # Percentages
    EMAIL = "EMAIL"             # Email addresses
    PHONE = "PHONE"             # Phone numbers
    URL = "URL"                 # Web URLs
    PRODUCT = "PRODUCT"         # Product names
    EVENT = "EVENT"             # Events
    LANGUAGE = "LANGUAGE"       # Languages
    TECHNOLOGY = "TECH"         # Tech terms
    MEDICAL = "MEDICAL"         # Medical terms


@dataclass
class Entity:
    """A single extracted entity"""
    text: str
    entity_type: EntityType
    start_pos: int
    end_pos: int
    confidence: float
    normalized_text: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "type": self.entity_type.value,
            "position": {"start": self.start_pos, "end": self.end_pos},
            "confidence": round(self.confidence, 3),
            "normalized": self.normalized_text,
            "metadata": self.metadata
        }


@dataclass
class EntityExtractionResult:
    """Result of entity extraction"""
    original_text: str
    entities: List[Entity]
    entity_counts: Dict[str, int]
    unique_entities: Dict[str, List[str]]
    processing_time_ms: float
    language: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "entities": [e.to_dict() for e in self.entities],
            "entity_counts": self.entity_counts,
            "unique_entities": self.unique_entities,
            "total_entities": len(self.entities),
            "processing_time_ms": round(self.processing_time_ms, 2),
            "language": self.language
        }


class EntityExtractor:
    """
    Named Entity Recognition Engine
    
    Uses pattern matching + LLM for comprehensive entity extraction
    """
    
    # Common title patterns
    TITLES = r'(?:Mr|Mrs|Ms|Miss|Dr|Prof|Sir|Madam|Rev|Hon|Capt|Lt|Col|Gen|Sgt)\.?'
    
    # Patterns for different entity types
    PATTERNS = {
        EntityType.EMAIL: r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        EntityType.URL: r'https?://(?:[-\w.])+(?:\:\d+)?(?:/(?:[\w/_.,]*)?(?:\?\S+)?)?',
        EntityType.PHONE: r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
        EntityType.MONEY: r'[$€£¥]\s?\d+(?:,\d{3})*(?:\.\d{2})?|\d+(?:,\d{3})*(?:\.\d{2})?\s?(?:USD|EUR|GBP|ALL|LEK)',
        EntityType.PERCENT: r'\d+(?:\.\d+)?%',
        EntityType.DATE: r'(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4})|(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4})|(?:\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4})',
        EntityType.TIME: r'\d{1,2}:\d{2}(?::\d{2})?(?:\s*[AP]M)?',
    }
    
    # Known organizations
    KNOWN_ORGS = {
        "Google", "Microsoft", "Apple", "Amazon", "Meta", "Facebook", "Twitter",
        "Tesla", "SpaceX", "NASA", "UN", "EU", "NATO", "WHO", "UNICEF",
        "IBM", "Intel", "NVIDIA", "OpenAI", "Anthropic", "Kloud",
        # Albanian
        "Universiteti i Tiranës", "RTSH", "BKT", "Raiffeisen", "Alpha Bank"
    }
    
    # Country and city patterns
    LOCATIONS = {
        # Countries
        "Albania", "Kosovo", "North Macedonia", "Montenegro", "Serbia",
        "USA", "UK", "Germany", "France", "Italy", "Spain", "China", "Japan",
        # Albanian cities
        "Tiranë", "Tirana", "Durrës", "Vlorë", "Shkodër", "Korçë", "Fier",
        "Elbasan", "Berat", "Lushnjë", "Pogradec", "Sarandë", "Gjirokastër",
        # World cities
        "New York", "London", "Paris", "Berlin", "Tokyo", "Beijing",
        "San Francisco", "Los Angeles", "Chicago", "Washington"
    }
    
    def __init__(self, ollama_host: Optional[str] = None):
        self.ollama_host = ollama_host or "http://kloud-ollama:11434"
        self._initialized = False
        logger.info("🏷️ EntityExtractor initialized")
    
    async def initialize(self):
        """Initialize the extractor"""
        if self._initialized:
            return
        self._initialized = True
        logger.info("✅ EntityExtractor ready")
    
    async def extract(
        self,
        text: str,
        entity_types: Optional[List[EntityType]] = None,
        use_llm: bool = True,
        language: str = "auto"
    ) -> EntityExtractionResult:
        """
        Extract entities from text
        
        Args:
            text: Text to analyze
            entity_types: Specific types to extract (None = all)
            use_llm: Use LLM for enhanced extraction
            language: Language code or 'auto'
        """
        start_time = datetime.now()
        
        # Detect language
        if language == "auto":
            language = self._detect_language(text)
        
        entities: List[Entity] = []
        
        # Pattern-based extraction
        entities.extend(self._extract_patterns(text, entity_types))
        
        # Named entity extraction
        entities.extend(self._extract_names(text))
        entities.extend(self._extract_organizations(text))
        entities.extend(self._extract_locations(text))
        
        # LLM enhancement
        if use_llm:
            llm_entities = await self._llm_extract(text, language)
            entities.extend(llm_entities)
        
        # Deduplicate
        entities = self._deduplicate(entities)
        
        # Sort by position
        entities.sort(key=lambda e: e.start_pos)
        
        # Calculate stats
        entity_counts = self._count_entities(entities)
        unique_entities = self._get_unique_entities(entities)
        
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return EntityExtractionResult(
            original_text=text[:500] + "..." if len(text) > 500 else text,
            entities=entities,
            entity_counts=entity_counts,
            unique_entities=unique_entities,
            processing_time_ms=processing_time,
            language=language
        )
    
    def _extract_patterns(
        self,
        text: str,
        entity_types: Optional[List[EntityType]]
    ) -> List[Entity]:
        """Extract entities using regex patterns"""
        entities = []
        
        for etype, pattern in self.PATTERNS.items():
            if entity_types and etype not in entity_types:
                continue
            
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append(Entity(
                    text=match.group(),
                    entity_type=etype,
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.95  # High confidence for pattern matches
                ))
        
        return entities
    
    def _extract_names(self, text: str) -> List[Entity]:
        """Extract person names"""
        entities = []
        
        # Pattern: Title + Name
        title_pattern = rf'{self.TITLES}\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        for match in re.finditer(title_pattern, text):
            entities.append(Entity(
                text=match.group(),
                entity_type=EntityType.PERSON,
                start_pos=match.start(),
                end_pos=match.end(),
                confidence=0.9
            ))
        
        # Pattern: Two or three capitalized words together (likely names)
        name_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\b'
        for match in re.finditer(name_pattern, text):
            name = match.group(1)
            # Skip if it's a known organization or location
            if name in self.KNOWN_ORGS or name in self.LOCATIONS:
                continue
            # Skip if at start of sentence (might be regular words)
            if match.start() > 0 and text[match.start()-1] not in '.!?\n':
                entities.append(Entity(
                    text=name,
                    entity_type=EntityType.PERSON,
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.7
                ))
        
        return entities
    
    def _extract_organizations(self, text: str) -> List[Entity]:
        """Extract organization names"""
        entities = []
        
        # Known organizations
        for org in self.KNOWN_ORGS:
            for match in re.finditer(rf'\b{re.escape(org)}\b', text, re.IGNORECASE):
                entities.append(Entity(
                    text=match.group(),
                    entity_type=EntityType.ORGANIZATION,
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.95,
                    normalized_text=org
                ))
        
        # Pattern: Words + Corp/Inc/Ltd/LLC
        org_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:Corp|Inc|Ltd|LLC|Co|Company|Group|Foundation)\b'
        for match in re.finditer(org_pattern, text):
            entities.append(Entity(
                text=match.group(),
                entity_type=EntityType.ORGANIZATION,
                start_pos=match.start(),
                end_pos=match.end(),
                confidence=0.9
            ))
        
        return entities
    
    def _extract_locations(self, text: str) -> List[Entity]:
        """Extract location entities"""
        entities = []
        
        # Known locations
        for loc in self.LOCATIONS:
            for match in re.finditer(rf'\b{re.escape(loc)}\b', text, re.IGNORECASE):
                entities.append(Entity(
                    text=match.group(),
                    entity_type=EntityType.LOCATION,
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.95,
                    normalized_text=loc
                ))
        
        return entities
    
    async def _llm_extract(self, text: str, language: str) -> List[Entity]:
        """Use LLM for entity extraction"""
        try:
            import httpx
            
            prompt = f"""Extract named entities from this text. Return JSON array with entities.
Types: PERSON, ORG, LOC, DATE, PRODUCT, EVENT

Text: {text[:1500]}

Return ONLY valid JSON array like:
[{{"text": "entity text", "type": "TYPE"}}]

Entities:"""
            
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(
                    f"{self.ollama_host}/api/generate",
                    json={
                        "model": "llama3.1:8b",
                        "prompt": prompt,
                        "stream": False,
                        "options": {"temperature": 0.2, "num_predict": 300}
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    llm_response = result.get("response", "")
                    return self._parse_llm_entities(llm_response, text)
        except Exception as e:
            logger.debug(f"LLM entity extraction failed: {e}")
        
        return []
    
    def _parse_llm_entities(self, llm_response: str, original_text: str) -> List[Entity]:
        """Parse LLM response into entities"""
        entities = []
        
        try:
            import json
            # Find JSON array in response
            match = re.search(r'\[.*\]', llm_response, re.DOTALL)
            if match:
                data = json.loads(match.group())
                for item in data:
                    if isinstance(item, dict) and "text" in item and "type" in item:
                        # Find position in original text
                        start = original_text.find(item["text"])
                        if start >= 0:
                            etype = self._map_entity_type(item["type"])
                            entities.append(Entity(
                                text=item["text"],
                                entity_type=etype,
                                start_pos=start,
                                end_pos=start + len(item["text"]),
                                confidence=0.75,
                                metadata={"source": "llm"}
                            ))
        except Exception as e:
            logger.debug(f"Failed to parse LLM entities: {e}")
        
        return entities
    
    def _map_entity_type(self, type_str: str) -> EntityType:
        """Map string to EntityType"""
        mapping = {
            "PERSON": EntityType.PERSON,
            "PER": EntityType.PERSON,
            "ORG": EntityType.ORGANIZATION,
            "ORGANIZATION": EntityType.ORGANIZATION,
            "LOC": EntityType.LOCATION,
            "LOCATION": EntityType.LOCATION,
            "GPE": EntityType.GPE,
            "DATE": EntityType.DATE,
            "TIME": EntityType.TIME,
            "MONEY": EntityType.MONEY,
            "PRODUCT": EntityType.PRODUCT,
            "EVENT": EntityType.EVENT,
        }
        return mapping.get(type_str.upper(), EntityType.PERSON)
    
    def _deduplicate(self, entities: List[Entity]) -> List[Entity]:
        """Remove duplicate entities"""
        seen: Set[Tuple[str, str]] = set()
        unique = []
        
        for entity in entities:
            key = (entity.text.lower(), entity.entity_type.value)
            if key not in seen:
                seen.add(key)
                unique.append(entity)
        
        return unique
    
    def _count_entities(self, entities: List[Entity]) -> Dict[str, int]:
        """Count entities by type"""
        counts: Dict[str, int] = {}
        for entity in entities:
            key = entity.entity_type.value
            counts[key] = counts.get(key, 0) + 1
        return counts
    
    def _get_unique_entities(self, entities: List[Entity]) -> Dict[str, List[str]]:
        """Get unique entity texts by type"""
        unique: Dict[str, Set[str]] = {}
        for entity in entities:
            key = entity.entity_type.value
            if key not in unique:
                unique[key] = set()
            unique[key].add(entity.text)
        return {k: list(v) for k, v in unique.items()}
    
    def _detect_language(self, text: str) -> str:
        """Simple language detection"""
        albanian_indicators = {"dhe", "është", "për", "nga", "me", "mund", "nuk"}
        words = set(text.lower().split())
        
        if len(words & albanian_indicators) >= 2:
            return "sq"
        return "en"


# Singleton instance
_entity_extractor: Optional[EntityExtractor] = None


def get_entity_extractor() -> EntityExtractor:
    """Get or create entity extractor instance"""
    global _entity_extractor
    if _entity_extractor is None:
        _entity_extractor = EntityExtractor()
    return _entity_extractor

