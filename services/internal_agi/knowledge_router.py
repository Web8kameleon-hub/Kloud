# ============================================================================
# KNOWLEDGE ROUTER - Routes Queries to Appropriate Data Sources
# ============================================================================
# Intelligent routing using internal data sources only
# NO external LLMs - Pure Kloud intelligence
# ============================================================================

import re
import logging
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Any, Tuple, Set
from datetime import datetime
import json
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

logger = logging.getLogger(__name__)


# ============================================================================
# QUERY INTENT CLASSIFICATION
# ============================================================================

class QueryDomain(Enum):
    """High-level query domains"""
    GOVERNMENT = "government"
    EDUCATION = "education"
    HEALTHCARE = "healthcare"
    FINANCE = "finance"
    STATISTICS = "statistics"
    TECHNOLOGY = "technology"
    NEWS = "news"
    CULTURE = "culture"
    SPORTS = "sports"
    ENTERTAINMENT = "entertainment"
    TOURISM = "tourism"
    TRANSPORT = "transport"
    ENERGY = "energy"
    TELECOM = "telecom"
    RESEARCH = "research"
    INDUSTRY = "industry"
    ENVIRONMENT = "environment"
    AGRICULTURE = "agriculture"
    GENERAL = "general"


class QueryIntent(Enum):
    """Specific query intents"""
    SEARCH = "search"           # Looking for information
    COMPARE = "compare"         # Comparing data across sources
    ANALYZE = "analyze"         # Deep analysis required
    AGGREGATE = "aggregate"     # Aggregating from multiple sources
    STREAM = "stream"           # Real-time data stream
    REPORT = "report"           # Generate a report
    PREDICT = "predict"         # Prediction/forecasting
    EXPLAIN = "explain"         # Explanation required
    LIST = "list"               # List items/entities
    LOOKUP = "lookup"           # Direct lookup


@dataclass
class QueryIntent:
    """Parsed query intent with metadata"""
    domain: QueryDomain
    intent_type: QueryIntent
    entities: List[str]
    countries: List[str]
    keywords: List[str]
    confidence: float
    raw_query: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "domain": self.domain.value,
            "intent_type": self.intent_type.value,
            "entities": self.entities,
            "countries": self.countries,
            "keywords": self.keywords,
            "confidence": self.confidence,
            "raw_query": self.raw_query,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class RouteDecision:
    """Decision on where to route a query"""
    primary_sources: List[str]      # Primary data sources to query
    secondary_sources: List[str]    # Fallback sources
    modules: List[str]              # Kloud modules to engage
    strategy: str                   # aggregation, stream, single, parallel
    priority: int                   # 1-10 priority level
    estimated_sources: int          # How many sources will be queried
    reasoning: str                  # Why this decision was made
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "primary_sources": self.primary_sources,
            "secondary_sources": self.secondary_sources,
            "modules": self.modules,
            "strategy": self.strategy,
            "priority": self.priority,
            "estimated_sources": self.estimated_sources,
            "reasoning": self.reasoning
        }


# ============================================================================
# KEYWORD PATTERNS FOR DOMAIN DETECTION
# ============================================================================

DOMAIN_KEYWORDS = {
    QueryDomain.GOVERNMENT: [
        "government", "ministry", "parliament", "congress", "senate",
        "president", "prime minister", "law", "legislation", "policy",
        "regulation", "public", "federal", "national", "municipal",
        "election", "vote", "democrat", "republican", "political",
        "qeveri", "ligj", "politikë", "kryeministër", "president"
    ],
    QueryDomain.EDUCATION: [
        "university", "college", "school", "education", "student",
        "professor", "academic", "research", "degree", "scholarship",
        "learning", "teaching", "curriculum", "fakultet", "universitet",
        "cambridge", "oxford", "harvard", "mit", "stanford"
    ],
    QueryDomain.HEALTHCARE: [
        "hospital", "health", "medical", "doctor", "patient", "disease",
        "treatment", "medicine", "clinic", "pharmaceutical", "nursing",
        "surgery", "therapy", "diagnosis", "spital", "shëndetësi",
        "covid", "vaccine", "pandemic", "epidemic"
    ],
    QueryDomain.FINANCE: [
        "bank", "finance", "money", "currency", "stock", "market",
        "investment", "loan", "credit", "trading", "economy",
        "inflation", "gdp", "interest rate", "forex", "crypto",
        "bitcoin", "ethereum", "bankë", "para", "financë"
    ],
    QueryDomain.STATISTICS: [
        "statistics", "data", "census", "population", "demographic",
        "survey", "poll", "metric", "indicator", "rate", "percentage",
        "statistikë", "të dhëna", "popullsi"
    ],
    QueryDomain.TECHNOLOGY: [
        "technology", "tech", "software", "hardware", "computer",
        "programming", "developer", "startup", "innovation", "ai",
        "machine learning", "blockchain", "cloud", "teknologji"
    ],
    QueryDomain.NEWS: [
        "news", "breaking", "headline", "reporter", "journalist",
        "article", "press", "media", "broadcast", "lajme"
    ],
    QueryDomain.CULTURE: [
        "culture", "art", "museum", "heritage", "tradition", "festival",
        "music", "theater", "literature", "history", "kulturë"
    ],
    QueryDomain.SPORTS: [
        "sport", "football", "basketball", "tennis", "soccer", "nba",
        "fifa", "uefa", "olympics", "athlete", "team", "match",
        "championship", "league", "futboll", "basketboll"
    ],
    QueryDomain.ENTERTAINMENT: [
        "entertainment", "movie", "film", "tv", "television", "show",
        "celebrity", "music", "concert", "streaming", "netflix",
        "youtube", "gaming", "game", "argëtim"
    ],
    QueryDomain.TOURISM: [
        "tourism", "travel", "hotel", "vacation", "destination",
        "tourist", "flight", "booking", "resort", "beach",
        "turizëm", "udhëtim"
    ],
    QueryDomain.TRANSPORT: [
        "transport", "transportation", "road", "railway", "airport",
        "port", "shipping", "logistics", "traffic", "vehicle",
        "car", "train", "bus", "airplane", "transport"
    ],
    QueryDomain.ENERGY: [
        "energy", "electricity", "power", "renewable", "solar",
        "wind", "nuclear", "oil", "gas", "fuel", "energji"
    ],
    QueryDomain.TELECOM: [
        "telecom", "telecommunication", "mobile", "phone", "internet",
        "5g", "network", "broadband", "wireless", "telekom"
    ],
    QueryDomain.RESEARCH: [
        "research", "study", "paper", "journal", "publication",
        "experiment", "lab", "laboratory", "science", "kërkim"
    ],
    QueryDomain.INDUSTRY: [
        "industry", "manufacturing", "factory", "production", "supply",
        "industrial", "mining", "construction", "industri"
    ],
    QueryDomain.ENVIRONMENT: [
        "environment", "climate", "pollution", "green", "ecology",
        "nature", "wildlife", "conservation", "sustainable", "mjedis"
    ],
    QueryDomain.AGRICULTURE: [
        "agriculture", "farming", "crop", "livestock", "food",
        "agricultural", "harvest", "farm", "bujqësi"
    ]
}

# Country patterns for detection
COUNTRY_PATTERNS = {
    # Europe
    "albania": ["albania", "shqipëri", "albanian", "shqiptar", "tirana", "tiranë"],
    "germany": ["germany", "german", "deutschland", "gjermani", "berlin", "munich"],
    "france": ["france", "french", "francë", "paris", "lyon"],
    "italy": ["italy", "italian", "itali", "rome", "roma", "milan"],
    "uk": ["uk", "britain", "british", "england", "english", "london", "mbretëri"],
    "spain": ["spain", "spanish", "spanjë", "madrid", "barcelona"],
    "netherlands": ["netherlands", "dutch", "holandë", "amsterdam"],
    "switzerland": ["switzerland", "swiss", "zvicër", "zurich", "geneva"],
    "austria": ["austria", "austrian", "austri", "vienna"],
    "poland": ["poland", "polish", "poloni", "warsaw"],
    
    # Asia
    "china": ["china", "chinese", "kinë", "beijing", "shanghai"],
    "japan": ["japan", "japanese", "japoni", "tokyo", "osaka"],
    "korea": ["korea", "korean", "kore", "seoul", "south korea"],
    "india": ["india", "indian", "indi", "delhi", "mumbai"],
    "pakistan": ["pakistan", "pakistani", "pakistan", "karachi"],
    
    # Americas
    "usa": ["usa", "us", "america", "american", "shba", "amerikë", "washington", "new york"],
    "canada": ["canada", "canadian", "kanada", "toronto", "vancouver"],
    "brazil": ["brazil", "brazilian", "brazil", "sao paulo", "rio"],
    "mexico": ["mexico", "mexican", "meksikë", "mexico city"],
    
    # Middle East
    "turkey": ["turkey", "turkish", "turqi", "ankara", "istanbul"],
    "israel": ["israel", "israeli", "izrael", "tel aviv"],
    "uae": ["uae", "emirates", "emirate", "dubai", "abu dhabi"],
    "saudi": ["saudi", "arabia", "saudi arabia", "arabi saudite", "riyadh"],
    
    # Africa
    "egypt": ["egypt", "egyptian", "egjipt", "cairo"],
    "nigeria": ["nigeria", "nigerian", "nigeri", "lagos"],
    "south africa": ["south africa", "afrika jugore", "johannesburg", "cape town"],
    "kenya": ["kenya", "kenyan", "kenia", "nairobi"],
    
    # Oceania
    "australia": ["australia", "australian", "australi", "sydney", "melbourne"],
    "new zealand": ["new zealand", "zealandi e re", "auckland", "wellington"],
}


# ============================================================================
# KNOWLEDGE ROUTER CLASS
# ============================================================================

class KnowledgeRouter:
    """
    Routes queries to appropriate data sources and modules
    
    Uses keyword matching, entity extraction, and rule-based logic
    to determine the best sources for answering a query.
    NO external LLMs - pure pattern matching and heuristics.
    """
    
    def __init__(self):
        self.domain_keywords = DOMAIN_KEYWORDS
        self.country_patterns = COUNTRY_PATTERNS
        self._query_cache: Dict[str, RouteDecision] = {}
        self._cache_size = 1000
        
        # Source to region mapping
        self.region_sources = {
            "europe": "europe_sources",
            "asia_china": "asia_china_sources",
            "india_south_asia": "india_south_asia_sources",
            "americas": "americas_sources",
            "africa_middle_east": "africa_middle_east_sources",
            "asia_oceania": "asia_oceania_global_sources",
            "caribbean_central_america": "caribbean_central_america_sources",
            "pacific_islands": "pacific_islands_sources",
            "central_asia_caucasus": "central_asia_caucasus_sources",
            "eastern_europe_balkans": "eastern_europe_balkans_sources",
            "global": "global_data_sources"
        }
        
        # Country to region mapping
        self.country_region = {
            # Europe
            "albania": "eastern_europe_balkans", "germany": "europe", "france": "europe",
            "italy": "europe", "uk": "europe", "spain": "europe", "netherlands": "europe",
            "switzerland": "europe", "austria": "europe", "poland": "europe",
            
            # Asia
            "china": "asia_china", "japan": "asia_china", "korea": "asia_china",
            "india": "india_south_asia", "pakistan": "india_south_asia",
            
            # Americas
            "usa": "americas", "canada": "americas", "brazil": "americas", "mexico": "americas",
            
            # Middle East
            "turkey": "africa_middle_east", "israel": "africa_middle_east",
            "uae": "africa_middle_east", "saudi": "africa_middle_east",
            
            # Africa
            "egypt": "africa_middle_east", "nigeria": "africa_middle_east",
            "south africa": "africa_middle_east", "kenya": "africa_middle_east",
            
            # Oceania
            "australia": "asia_oceania", "new zealand": "asia_oceania",
        }
    
    def parse_query(self, query: str) -> QueryIntent:
        """
        Parse a natural language query to extract intent and entities
        """
        query_lower = query.lower()
        
        # Detect domain
        domain = self._detect_domain(query_lower)
        
        # Detect countries
        countries = self._detect_countries(query_lower)
        
        # Extract keywords (simple tokenization)
        keywords = self._extract_keywords(query_lower)
        
        # Determine intent type
        intent_type = self._detect_intent_type(query_lower)
        
        # Extract named entities (simple pattern matching)
        entities = self._extract_entities(query_lower)
        
        # Calculate confidence
        confidence = self._calculate_confidence(domain, countries, keywords)
        
        return QueryIntent(
            domain=domain,
            intent_type=intent_type,
            entities=entities,
            countries=countries,
            keywords=keywords,
            confidence=confidence,
            raw_query=query
        )
    
    def route(self, query: str) -> RouteDecision:
        """
        Route a query to appropriate sources and modules
        """
        # Check cache
        cache_key = query.lower().strip()
        if cache_key in self._query_cache:
            return self._query_cache[cache_key]
        
        # Parse the query
        intent = self.parse_query(query)
        
        # Determine primary sources based on countries
        primary_sources = []
        if intent.countries:
            for country in intent.countries:
                region = self.country_region.get(country, "global")
                source = self.region_sources.get(region)
                if source and source not in primary_sources:
                    primary_sources.append(source)
        
        # If no country specified, use domain to determine sources
        if not primary_sources:
            primary_sources = self._get_sources_for_domain(intent.domain)
        
        # Secondary sources (always include global)
        secondary_sources = ["global_data_sources"]
        if intent.domain in [QueryDomain.STATISTICS, QueryDomain.RESEARCH]:
            secondary_sources.extend(["europe_sources", "americas_sources"])
        
        # Determine which modules to engage
        modules = self._get_modules_for_intent(intent)
        
        # Determine strategy
        strategy = self._determine_strategy(intent)
        
        # Create decision
        decision = RouteDecision(
            primary_sources=primary_sources,
            secondary_sources=secondary_sources,
            modules=modules,
            strategy=strategy,
            priority=self._calculate_priority(intent),
            estimated_sources=len(primary_sources) + len(secondary_sources),
            reasoning=f"Domain: {intent.domain.value}, Countries: {intent.countries}, Strategy: {strategy}"
        )
        
        # Cache the decision
        if len(self._query_cache) > self._cache_size:
            # Simple LRU: remove first item
            self._query_cache.pop(next(iter(self._query_cache)))
        self._query_cache[cache_key] = decision
        
        return decision
    
    def _detect_domain(self, query: str) -> QueryDomain:
        """Detect the primary domain of a query"""
        scores = {domain: 0 for domain in QueryDomain}
        
        for domain, keywords in self.domain_keywords.items():
            for keyword in keywords:
                if keyword in query:
                    scores[domain] += 1
        
        # Return domain with highest score
        best_domain = max(scores, key=scores.get)
        if scores[best_domain] > 0:
            return best_domain
        return QueryDomain.GENERAL
    
    def _detect_countries(self, query: str) -> List[str]:
        """Detect mentioned countries"""
        countries = []
        for country, patterns in self.country_patterns.items():
            for pattern in patterns:
                if pattern in query:
                    if country not in countries:
                        countries.append(country)
                    break
        return countries
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract meaningful keywords from query"""
        # Remove common stop words
        stop_words = {
            "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
            "have", "has", "had", "do", "does", "did", "will", "would", "could",
            "should", "may", "might", "must", "shall", "can", "need", "dare",
            "for", "of", "to", "in", "on", "at", "by", "with", "about", "from",
            "and", "or", "not", "but", "if", "then", "else", "when", "where",
            "why", "how", "what", "which", "who", "whom", "whose", "this", "that",
            "these", "those", "i", "you", "he", "she", "it", "we", "they", "me",
            "him", "her", "us", "them", "my", "your", "his", "its", "our", "their"
        }
        
        # Simple tokenization
        tokens = re.findall(r'\b\w+\b', query)
        keywords = [t for t in tokens if t not in stop_words and len(t) > 2]
        
        return keywords[:10]  # Limit to 10 keywords
    
    def _detect_intent_type(self, query: str) -> QueryIntent:
        """Detect the type of query intent"""
        if any(word in query for word in ["compare", "versus", "vs", "difference"]):
            return QueryIntent.COMPARE
        if any(word in query for word in ["analyze", "analysis", "examine", "evaluate"]):
            return QueryIntent.ANALYZE
        if any(word in query for word in ["list", "all", "show me", "what are"]):
            return QueryIntent.LIST
        if any(word in query for word in ["aggregate", "total", "sum", "combine"]):
            return QueryIntent.AGGREGATE
        if any(word in query for word in ["stream", "real-time", "live", "current"]):
            return QueryIntent.STREAM
        if any(word in query for word in ["report", "generate", "create"]):
            return QueryIntent.REPORT
        if any(word in query for word in ["predict", "forecast", "future", "will"]):
            return QueryIntent.PREDICT
        if any(word in query for word in ["explain", "why", "how does", "what is"]):
            return QueryIntent.EXPLAIN
        if any(word in query for word in ["find", "lookup", "get", "retrieve"]):
            return QueryIntent.LOOKUP
        
        return QueryIntent.SEARCH
    
    def _extract_entities(self, query: str) -> List[str]:
        """Extract named entities (organizations, etc.)"""
        entities = []
        
        # Common organization patterns
        org_patterns = [
            r'\b(?:World Bank|IMF|UN|UNESCO|WHO|NATO|EU|OECD|FIFA|UEFA)\b',
            r'\b[A-Z][a-z]+ (?:University|Institute|Corporation|Company|Organization)\b',
            r'\b[A-Z]{2,5}\b',  # Acronyms
        ]
        
        for pattern in org_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            entities.extend(matches)
        
        return list(set(entities))[:5]  # Dedupe and limit
    
    def _calculate_confidence(self, domain: QueryDomain, countries: List[str], keywords: List[str]) -> float:
        """Calculate confidence score for the parse"""
        confidence = 0.5  # Base confidence
        
        if domain != QueryDomain.GENERAL:
            confidence += 0.2
        if countries:
            confidence += 0.15
        if len(keywords) >= 3:
            confidence += 0.1
        if len(keywords) >= 5:
            confidence += 0.05
        
        return min(confidence, 1.0)
    
    def _get_sources_for_domain(self, domain: QueryDomain) -> List[str]:
        """Get appropriate sources for a domain"""
        # For global domains, use multiple sources
        if domain in [QueryDomain.STATISTICS, QueryDomain.FINANCE]:
            return ["global_data_sources", "europe_sources", "americas_sources"]
        if domain in [QueryDomain.TECHNOLOGY, QueryDomain.RESEARCH]:
            return ["americas_sources", "europe_sources", "asia_china_sources"]
        if domain == QueryDomain.SPORTS:
            return ["global_data_sources"]  # FIFA, UEFA, etc.
        
        # Default to global
        return ["global_data_sources"]
    
    def _get_modules_for_intent(self, intent: QueryIntent) -> List[str]:
        """Determine which Kloud modules to engage"""
        modules = ["jona"]  # JONA always supervises
        
        if intent.intent_type in [QueryIntent.STREAM]:
            modules.append("alba")
        if intent.intent_type in [QueryIntent.ANALYZE, QueryIntent.AGGREGATE]:
            modules.append("albi")
        if intent.intent_type in [QueryIntent.PREDICT]:
            modules.extend(["cycle_engine", "asi"])
        if intent.intent_type == QueryIntent.REPORT:
            modules.append("blerina")
        
        return modules
    
    def _determine_strategy(self, intent: QueryIntent) -> str:
        """Determine the query execution strategy"""
        if intent.intent_type == QueryIntent.STREAM:
            return "stream"
        if intent.intent_type in [QueryIntent.AGGREGATE, QueryIntent.COMPARE]:
            return "parallel"
        if len(intent.countries) > 1:
            return "parallel"
        if len(intent.countries) == 0 and intent.domain == QueryDomain.GENERAL:
            return "aggregation"
        
        return "single"
    
    def _calculate_priority(self, intent: QueryIntent) -> int:
        """Calculate query priority (1-10)"""
        priority = 5  # Base priority
        
        if intent.intent_type == QueryIntent.STREAM:
            priority = 9  # Real-time is high priority
        elif intent.intent_type == QueryIntent.LOOKUP:
            priority = 7  # Quick lookups are prioritized
        elif intent.intent_type == QueryIntent.ANALYZE:
            priority = 4  # Analysis can take time
        
        return priority


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================

_router_instance: Optional[KnowledgeRouter] = None

def get_router() -> KnowledgeRouter:
    """Get the global knowledge router singleton"""
    global _router_instance
    if _router_instance is None:
        _router_instance = KnowledgeRouter()
    return _router_instance

