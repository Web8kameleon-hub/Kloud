"""
OCEAN CORE 8030
===============
Curiosity Ocean - Universal Knowledge Aggregation Engine
Completely isolated from main.py - runs on port 8030

Modules:
- data_sources.py: Connector layer for internal data
- external_apis.py: Open source integrations (Wikipedia, Arxiv, PubMed, etc.)
- query_processor.py: Intelligence engine for query processing
- knowledge_engine.py: Data aggregation + response formulation
- ocean_api.py: FastAPI app (standalone)

Author: Kloud
Version: 2.0.0
"""

__version__ = "2.0.0"
__all__ = [
    "data_sources",
    "external_apis",
    "query_processor",
    "knowledge_engine",
    "ocean_api",
]

