# ============================================================================
# CURIOSITY OCEAN - Global Knowledge Portal API
# ============================================================================
# Version: 1.0.0
# Purpose: Portal to planetary knowledge with 200,000+ free-score links
# Integration: Internal AGI Engine, Data Sources, Knowledge Index
# ============================================================================

"""
CURIOSITY OCEAN API - The Knowledge Portal

Endpoints:
- /ask           → Ask anything, get intelligent answers
- /search-links  → Search across 4053+ data sources
- /open-data     → Access open data from 155+ countries
- /explore       → Explore categories and regions
- /discover      → Serendipitous discovery
- /stream        → Real-time knowledge streaming

Features:
- 4053+ curated data sources
- 988 API endpoints
- 155+ countries covered
- All categories: Government, Education, Health, Finance, Sports, Entertainment, Tourism
- Powered by Internal AGI Engine (NO external LLMs)

Portal: https://kloud.com/modules/curiosity-ocean
"""

__version__ = "1.0.0"
__author__ = "Kloud"
__description__ = "Curiosity Ocean - Global Knowledge Portal"

from .api import CuriosityOceanAPI, create_app
from .search import KnowledgeSearch, SearchResult
from .explore import Explorer, ExploreResult
from .discovery import DiscoveryEngine, DiscoveryItem

__all__ = [
    "CuriosityOceanAPI",
    "create_app",
    "KnowledgeSearch",
    "SearchResult",
    "Explorer",
    "ExploreResult",
    "DiscoveryEngine",
    "DiscoveryItem",
    "__version__",
]

