# ============================================================================
# KLOUD INTELLIGENCE HUB - Unified Entry Point
# ============================================================================
# Connects Internal AGI, Curiosity Ocean, and Knowledge Index
# ============================================================================

"""
KLOUD INTELLIGENCE ARCHITECTURE v1.0.0

┌─────────────────────────────────────────────────────────────────────────────┐
│                         KLOUD INTELLIGENCE HUB                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌───────────────────────────────────────────────────────────────────┐    │
│   │                      INTERNAL AGI ENGINE                          │    │
│   │  ┌──────────┐ ┌──────────────┐ ┌───────────────┐ ┌─────────────┐  │    │
│   │  │ Module   │ │  Knowledge   │ │   Reasoning   │ │  Context    │  │    │
│   │  │ Registry │ │   Router     │ │    Engine     │ │  Builder    │  │    │
│   │  │ 23 mods  │ │  Query→Src   │ │ Pattern+Rule  │ │ Session+KG  │  │    │
│   │  └──────────┘ └──────────────┘ └───────────────┘ └─────────────┘  │    │
│   └───────────────────────────────────────────────────────────────────┘    │
│                                     ▼                                       │
│   ┌───────────────────────────────────────────────────────────────────┐    │
│   │                       CURIOSITY OCEAN                             │    │
│   │  ┌──────────┐ ┌──────────────┐ ┌───────────────┐ ┌─────────────┐  │    │
│   │  │  Search  │ │   Explore    │ │   Discovery   │ │   Random    │  │    │
│   │  │  Engine  │ │    Topics    │ │   Insights    │ │    Walk     │  │    │
│   │  └──────────┘ └──────────────┘ └───────────────┘ └─────────────┘  │    │
│   └───────────────────────────────────────────────────────────────────┘    │
│                                     ▼                                       │
│   ┌───────────────────────────────────────────────────────────────────┐    │
│   │                      KNOWLEDGE INDEX                              │    │
│   │  ┌──────────┐ ┌──────────────┐ ┌───────────────┐ ┌─────────────┐  │    │
│   │  │  200K+   │ │    Link      │ │    Index      │ │   Search    │  │    │
│   │  │  Links   │ │   Scorer     │ │   Builder     │ │   Engine    │  │    │
│   │  │ 155 ctry │ │  Quality+    │ │  data→JSON    │ │  Fast Find  │  │    │
│   │  └──────────┘ └──────────────┘ └───────────────┘ └─────────────┘  │    │
│   └───────────────────────────────────────────────────────────────────┘    │
│                                     ▼                                       │
│   ┌───────────────────────────────────────────────────────────────────┐    │
│   │                       DATA SOURCES                                │    │
│   │  ┌──────────┐ ┌──────────────┐ ┌───────────────┐ ┌─────────────┐  │    │
│   │  │  Europe  │ │   Americas   │ │  Asia/China   │ │   Global    │  │    │
│   │  │  400+    │ │    400+      │ │    550+       │ │   1500+     │  │    │
│   │  └──────────┘ └──────────────┘ └───────────────┘ └─────────────┘  │    │
│   │  ┌──────────┐ ┌──────────────┐ ┌───────────────┐ ┌─────────────┐  │    │
│   │  │ Africa   │ │   Pacific    │ │  Balkans/EE   │ │ Caribbean   │  │    │
│   │  │  300+    │ │    150+      │ │    200+       │ │   200+      │  │    │
│   │  └──────────┘ └──────────────┘ └───────────────┘ └─────────────┘  │    │
│   └───────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

NO EXTERNAL AI DEPENDENCIES:
✗ No OpenAI
✗ No Groq  
✗ No Claude API
✓ 100% Internal Processing
✓ Pattern Matching
✓ Rule-Based Inference
✓ Statistical Analysis
✓ Semantic Search (local)

API PORTS (NO CONFLICTS):
- HQ Server:        8000 (kloud.com - MAIN API)
- ALBA Service:     5555 (Frame Generation)
- ALBI Service:     6680 (AI Processing)
- JONA Service:     7777 (Orchestration)
- Knowledge Index:  8008 (Link Search - sub-service)
- Curiosity Ocean:  8009 (Knowledge Portal - sub-service)

NOTE: Knowledge Index & Curiosity Ocean are SUB-ROUTES of HQ (8000)
      They can also run standalone on their own ports for testing
"""

__version__ = "1.0.0"

# ============================================================================
# IMPORTS
# ============================================================================

from services.internal_agi import (
    InternalAGI,
    ModuleRegistry,
    KnowledgeRouter,
    ReasoningEngine,
    ContextBuilder,
    Fallbacks
)

from services.curiosity_ocean import (
    CuriosityOcean,
    OceanSearch,
    TopicExplorer,
    DiscoveryEngine
)

from services.knowledge_index import (
    LinkSearchEngine,
    IndexBuilder,
    LinkScorer
)

# ============================================================================
# UNIFIED INTELLIGENCE CLASS
# ============================================================================

class KloudIntelligence:
    """
    Unified intelligence hub connecting all modules
    
    Features:
    - Internal AGI for reasoning (no external LLMs)
    - Curiosity Ocean for knowledge exploration
    - Knowledge Index for 200k+ link search
    - Data Sources for 155 countries
    """
    
    def __init__(self):
        # Initialize Internal AGI
        self.agi = InternalAGI()
        
        # Initialize Curiosity Ocean
        self.ocean = CuriosityOcean()
        
        # Initialize Knowledge Index
        self.knowledge = LinkSearchEngine()
        
        # Statistics
        self.total_sources = 4053
        self.countries = 155
        self.modules = 23
    
    async def ask(self, query: str, context: dict = None) -> dict:
        """
        Unified ask interface
        
        Routes query through:
        1. Internal AGI for reasoning
        2. Curiosity Ocean for exploration
        3. Knowledge Index for sources
        """
        # Get AGI reasoning
        reasoning = await self.agi.reason(query, context)
        
        # Get ocean exploration
        exploration = await self.ocean.explore(query)
        
        # Get knowledge links
        links = self.knowledge.search(query, limit=10)
        
        return {
            "query": query,
            "reasoning": reasoning,
            "exploration": exploration,
            "sources": links,
            "meta": {
                "engine": "Kloud Internal AGI",
                "version": __version__,
                "external_ai": False
            }
        }
    
    async def search(self, query: str, **filters) -> dict:
        """Search across all knowledge sources"""
        return self.knowledge.search(query, **filters)
    
    async def explore(self, topic: str) -> dict:
        """Explore a topic through Curiosity Ocean"""
        return await self.ocean.explore(topic)
    
    async def discover(self) -> dict:
        """Serendipitous discovery"""
        return await self.ocean.discover()
    
    def get_stats(self) -> dict:
        """Get system statistics"""
        return {
            "total_sources": self.total_sources,
            "countries": self.countries,
            "modules": self.modules,
            "services": {
                "internal_agi": "active",
                "curiosity_ocean": "active",
                "knowledge_index": "active"
            },
            "external_dependencies": {
                "openai": False,
                "groq": False,
                "claude": False
            }
        }


# ============================================================================
# SINGLETON
# ============================================================================

_intelligence: KloudIntelligence = None

def get_intelligence() -> KloudIntelligence:
    """Get the global intelligence instance"""
    global _intelligence
    if _intelligence is None:
        _intelligence = KloudIntelligence()
    return _intelligence


# ============================================================================
# MODULE EXPORTS
# ============================================================================

__all__ = [
    # Main
    "KloudIntelligence",
    "get_intelligence",
    
    # AGI
    "InternalAGI",
    "ModuleRegistry", 
    "KnowledgeRouter",
    "ReasoningEngine",
    "ContextBuilder",
    "Fallbacks",
    
    # Ocean
    "CuriosityOcean",
    "OceanSearch",
    "TopicExplorer",
    "DiscoveryEngine",
    
    # Knowledge
    "LinkSearchEngine",
    "IndexBuilder",
    "LinkScorer",
]

