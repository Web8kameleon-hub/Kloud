# ============================================================================
# CONTEXT BUILDER - Builds Context from Internal Sources
# ============================================================================
# Assembles context for reasoning from all Kloud data sources
# NO external APIs - pure internal data aggregation
# ============================================================================

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
import json
import asyncio
import sys
import os

# Add parent directory for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

logger = logging.getLogger(__name__)


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class ContextFrame:
    """
    A frame of context built from internal sources
    
    Contains:
    - Data from relevant sources
    - Metadata about the sources
    - Temporal information
    - Relationship mappings
    """
    frame_id: str
    query: str
    sources: List[str]
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    relationships: Dict[str, List[str]]
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    ttl_seconds: int = 300  # 5 minute default TTL
    
    def __post_init__(self):
        if self.expires_at is None:
            self.expires_at = self.created_at + timedelta(seconds=self.ttl_seconds)
    
    def is_expired(self) -> bool:
        """Check if this context frame has expired"""
        return datetime.now() > self.expires_at
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "frame_id": self.frame_id,
            "query": self.query,
            "sources": self.sources,
            "data": self.data,
            "metadata": self.metadata,
            "relationships": self.relationships,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "is_expired": self.is_expired()
        }
    
    def add_data(self, source: str, data: Any):
        """Add data from a source"""
        self.data[source] = data
        if source not in self.sources:
            self.sources.append(source)
    
    def add_relationship(self, entity: str, related: List[str]):
        """Add entity relationship"""
        if entity not in self.relationships:
            self.relationships[entity] = []
        self.relationships[entity].extend(related)


@dataclass
class SourceInfo:
    """Information about a data source"""
    source_id: str
    name: str
    module: str
    country: Optional[str]
    category: str
    api_available: bool
    last_accessed: Optional[datetime]
    access_count: int = 0
    avg_latency_ms: float = 0.0


# ============================================================================
# CONTEXT BUILDER CLASS
# ============================================================================

class ContextBuilder:
    """
    Builds context frames from internal Kloud data sources
    
    Responsibilities:
    - Load and cache data source information
    - Query relevant sources for context
    - Build relationship graphs between entities
    - Manage context frame lifecycle
    
    Works with:
    - data_sources/ modules (4053+ sources)
    - Module registry
    - Knowledge router decisions
    """
    
    def __init__(self):
        self._frame_cache: Dict[str, ContextFrame] = {}
        self._source_cache: Dict[str, SourceInfo] = {}
        self._max_cache_size = 100
        self._frame_counter = 0
        
        # Initialize source information
        self._init_sources()
    
    def _init_sources(self):
        """Initialize source information from data_sources modules"""
        try:
            # Import data_sources dynamically
            from data_sources import GlobalDataSources
            
            gds = GlobalDataSources()
            
            # Load regional sources
            regions = [
                "europe", "asia_china", "india_south_asia", "americas",
                "africa_middle_east", "asia_oceania", "caribbean_central_america",
                "pacific_islands", "central_asia_caucasus", "eastern_europe_balkans"
            ]
            
            for region in regions:
                sources = gds.get_sources_by_region(region)
                for source in sources:
                    source_id = f"{region}:{source.name}".replace(" ", "_").lower()
                    self._source_cache[source_id] = SourceInfo(
                        source_id=source_id,
                        name=source.name,
                        module=f"{region}_sources",
                        country=source.country,
                        category=source.category.value if hasattr(source.category, 'value') else str(source.category),
                        api_available=source.api_available,
                        last_accessed=None
                    )
            
            logger.info(f"Initialized {len(self._source_cache)} sources from data_sources")
            
        except ImportError as e:
            logger.warning(f"Could not import data_sources: {e}")
            # Continue without pre-loaded sources
    
    def _generate_frame_id(self) -> str:
        """Generate unique frame ID"""
        self._frame_counter += 1
        return f"ctx_{datetime.now().strftime('%Y%m%d%H%M%S')}_{self._frame_counter:05d}"
    
    async def build_context(
        self,
        query: str,
        sources: List[str],
        route_decision: Any = None,
        max_sources: int = 10
    ) -> ContextFrame:
        """
        Build a context frame for a query
        
        Args:
            query: The user's query
            sources: List of source modules to query
            route_decision: Optional RouteDecision from knowledge router
            max_sources: Maximum number of sources to include
        
        Returns:
            ContextFrame with aggregated data
        """
        frame_id = self._generate_frame_id()
        
        # Initialize frame
        frame = ContextFrame(
            frame_id=frame_id,
            query=query,
            sources=[],
            data={},
            metadata={
                "query_length": len(query),
                "requested_sources": sources,
                "max_sources": max_sources,
                "route_decision": route_decision.to_dict() if hasattr(route_decision, 'to_dict') else None
            },
            relationships={}
        )
        
        # Gather data from sources
        for source_module in sources[:max_sources]:
            source_data = await self._query_source(source_module, query)
            if source_data:
                frame.add_data(source_module, source_data)
        
        # Build relationships based on data
        self._build_relationships(frame)
        
        # Cache the frame
        self._cache_frame(frame)
        
        return frame
    
    async def _query_source(self, source_module: str, query: str) -> Optional[Dict[str, Any]]:
        """
        Query a specific source module for data
        
        This is where we would normally fetch from APIs,
        but we're keeping it internal by using cached source info.
        """
        try:
            # Get sources from cache that match this module
            matching_sources = [
                s for s in self._source_cache.values()
                if source_module in s.source_id or s.module == source_module
            ]
            
            if not matching_sources:
                # Try to load the module directly
                module_data = await self._load_module_sources(source_module)
                if module_data:
                    return module_data
                return None
            
            # Extract keywords from query for filtering
            keywords = query.lower().split()
            
            # Filter sources relevant to query
            relevant = []
            for source in matching_sources:
                source_text = f"{source.name} {source.category}".lower()
                if any(keyword in source_text for keyword in keywords):
                    relevant.append({
                        "id": source.source_id,
                        "name": source.name,
                        "category": source.category,
                        "country": source.country,
                        "api_available": source.api_available
                    })
            
            if not relevant:
                # Return first few sources as default
                relevant = [
                    {
                        "id": s.source_id,
                        "name": s.name,
                        "category": s.category,
                        "country": s.country,
                        "api_available": s.api_available
                    }
                    for s in matching_sources[:5]
                ]
            
            return {
                "module": source_module,
                "total_sources": len(matching_sources),
                "relevant_sources": relevant[:10],
                "query_match": len(relevant)
            }
            
        except Exception as e:
            logger.error(f"Error querying source {source_module}: {e}")
            return None
    
    async def _load_module_sources(self, module_name: str) -> Optional[Dict[str, Any]]:
        """Load sources directly from a module file"""
        try:
            # Map module name to actual module
            module_map = {
                "europe_sources": "data_sources.europe_sources",
                "asia_china_sources": "data_sources.asia_china_sources",
                "india_south_asia_sources": "data_sources.india_south_asia_sources",
                "americas_sources": "data_sources.americas_sources",
                "africa_middle_east_sources": "data_sources.africa_middle_east_sources",
                "asia_oceania_global_sources": "data_sources.asia_oceania_global_sources",
                "caribbean_central_america_sources": "data_sources.caribbean_central_america_sources",
                "pacific_islands_sources": "data_sources.pacific_islands_sources",
                "central_asia_caucasus_sources": "data_sources.central_asia_caucasus_sources",
                "eastern_europe_balkans_sources": "data_sources.eastern_europe_balkans_sources",
                "global_data_sources": "data_sources.global_data_sources",
            }
            
            if module_name not in module_map:
                return None
            
            # Import the module
            import importlib
            module = importlib.import_module(module_map[module_name])
            
            # Get sources (different modules have different function names)
            sources = []
            if hasattr(module, 'get_all_sources'):
                sources = module.get_all_sources()
            elif hasattr(module, 'get_sources'):
                sources = module.get_sources()
            
            return {
                "module": module_name,
                "total_sources": len(sources),
                "sample_sources": [
                    {
                        "name": s.name if hasattr(s, 'name') else str(s),
                        "country": s.country if hasattr(s, 'country') else "Unknown",
                        "category": s.category.value if hasattr(s, 'category') and hasattr(s.category, 'value') else str(getattr(s, 'category', 'Unknown'))
                    }
                    for s in sources[:10]
                ]
            }
            
        except Exception as e:
            logger.error(f"Error loading module {module_name}: {e}")
            return None
    
    def _build_relationships(self, frame: ContextFrame):
        """Build entity relationships from frame data"""
        # Extract entities from data
        entities: Set[str] = set()
        
        for source, data in frame.data.items():
            if isinstance(data, dict):
                # Extract countries
                if 'relevant_sources' in data:
                    for src in data['relevant_sources']:
                        if 'country' in src and src['country']:
                            entities.add(src['country'])
                
                # Extract categories
                if 'sample_sources' in data:
                    for src in data['sample_sources']:
                        if 'category' in src:
                            entities.add(src['category'])
        
        # Build simple relationships
        entities_list = list(entities)
        for i, entity in enumerate(entities_list):
            # Each entity is related to adjacent entities in our data
            related = entities_list[max(0, i-2):i] + entities_list[i+1:min(len(entities_list), i+3)]
            if related:
                frame.add_relationship(entity, related)
    
    def _cache_frame(self, frame: ContextFrame):
        """Cache a context frame"""
        # Clean expired frames
        self._clean_cache()
        
        # Add new frame
        self._frame_cache[frame.frame_id] = frame
        
        # Evict if over limit
        if len(self._frame_cache) > self._max_cache_size:
            oldest_id = min(self._frame_cache.keys(), key=lambda k: self._frame_cache[k].created_at)
            del self._frame_cache[oldest_id]
    
    def _clean_cache(self):
        """Remove expired frames from cache"""
        expired = [fid for fid, frame in self._frame_cache.items() if frame.is_expired()]
        for fid in expired:
            del self._frame_cache[fid]
    
    def get_frame(self, frame_id: str) -> Optional[ContextFrame]:
        """Get a cached context frame by ID"""
        frame = self._frame_cache.get(frame_id)
        if frame and not frame.is_expired():
            return frame
        return None
    
    def get_source_info(self, source_id: str) -> Optional[SourceInfo]:
        """Get information about a specific source"""
        return self._source_cache.get(source_id)
    
    def get_sources_by_country(self, country: str) -> List[SourceInfo]:
        """Get all sources for a specific country"""
        return [s for s in self._source_cache.values() if s.country and s.country.lower() == country.lower()]
    
    def get_sources_by_category(self, category: str) -> List[SourceInfo]:
        """Get all sources in a specific category"""
        return [s for s in self._source_cache.values() if s.category.lower() == category.lower()]
    
    def get_api_sources(self) -> List[SourceInfo]:
        """Get all sources that have API available"""
        return [s for s in self._source_cache.values() if s.api_available]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get context builder statistics"""
        return {
            "total_sources_cached": len(self._source_cache),
            "active_frames": len(self._frame_cache),
            "frames_created": self._frame_counter,
            "sources_with_api": len(self.get_api_sources()),
            "unique_countries": len(set(s.country for s in self._source_cache.values() if s.country)),
            "unique_categories": len(set(s.category for s in self._source_cache.values()))
        }
    
    async def enrich_context(self, frame: ContextFrame, additional_sources: List[str]) -> ContextFrame:
        """
        Enrich an existing context frame with additional sources
        """
        for source in additional_sources:
            if source not in frame.sources:
                data = await self._query_source(source, frame.query)
                if data:
                    frame.add_data(source, data)
        
        # Rebuild relationships
        self._build_relationships(frame)
        
        return frame


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================

_builder_instance: Optional[ContextBuilder] = None

def get_builder() -> ContextBuilder:
    """Get the global context builder singleton"""
    global _builder_instance
    if _builder_instance is None:
        _builder_instance = ContextBuilder()
    return _builder_instance

