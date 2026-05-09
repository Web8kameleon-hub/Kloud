# ============================================================================
# INDEX BUILDER - Build Knowledge Index from Data Sources
# ============================================================================
# Builds the comprehensive link index from all data_sources modules
# ============================================================================

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import os
import sys
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

logger = logging.getLogger(__name__)


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class BuildResult:
    """Result of index building"""
    success: bool
    total_links: int
    sources_processed: int
    countries: int
    categories: int
    api_links: int
    duration_seconds: float
    errors: List[str]
    output_path: str


@dataclass
class SourceModule:
    """Information about a source module"""
    name: str
    module_path: str
    region: str
    estimated_sources: int


# ============================================================================
# SOURCE MODULES CONFIGURATION
# ============================================================================

SOURCE_MODULES = [
    SourceModule("europe_sources", "data_sources.europe_sources", "Europe", 400),
    SourceModule("asia_china_sources", "data_sources.asia_china_sources", "Asia-China", 300),
    SourceModule("india_south_asia_sources", "data_sources.india_south_asia_sources", "India-South Asia", 250),
    SourceModule("americas_sources", "data_sources.americas_sources", "Americas", 400),
    SourceModule("africa_middle_east_sources", "data_sources.africa_middle_east_sources", "Africa-Middle East", 300),
    SourceModule("asia_oceania_global_sources", "data_sources.asia_oceania_global_sources", "Asia-Oceania", 250),
    SourceModule("caribbean_central_america_sources", "data_sources.caribbean_central_america_sources", "Caribbean", 200),
    SourceModule("pacific_islands_sources", "data_sources.pacific_islands_sources", "Pacific Islands", 150),
    SourceModule("central_asia_caucasus_sources", "data_sources.central_asia_caucasus_sources", "Central Asia", 150),
    SourceModule("eastern_europe_balkans_sources", "data_sources.eastern_europe_balkans_sources", "Eastern Europe", 200),
    SourceModule("global_data_sources", "data_sources.global_data_sources", "Global", 1500),
]


# ============================================================================
# INDEX BUILDER CLASS
# ============================================================================

class IndexBuilder:
    """
    Builds the knowledge index from all data_sources modules
    
    Features:
    - Processes all regional data_sources
    - Generates unique link IDs
    - Calculates quality scores
    - Creates search-optimized index
    - Outputs JSON index file
    """
    
    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = output_dir or self._default_output_dir()
        self.source_modules = SOURCE_MODULES
        self._link_counter = 0
    
    def _default_output_dir(self) -> str:
        """Get default output directory"""
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        return os.path.join(base, "app", "knowledge")
    
    def _generate_link_id(self, source_name: str) -> str:
        """Generate unique link ID"""
        self._link_counter += 1
        # Use source name prefix + counter
        prefix = source_name[:3].upper() if source_name else "LNK"
        return f"{prefix}_{self._link_counter:06d}"
    
    def build(self, include_modules: List[str] = None) -> BuildResult:
        """
        Build the complete knowledge index
        
        Args:
            include_modules: List of module names to include (None = all)
        
        Returns:
            BuildResult with statistics
        """
        start_time = datetime.now()
        errors = []
        all_links = []
        countries_seen = set()
        categories_seen = set()
        api_count = 0
        sources_processed = 0
        
        # Process each source module
        for module_info in self.source_modules:
            if include_modules and module_info.name not in include_modules:
                continue
            
            logger.info(f"Processing {module_info.name}...")
            
            try:
                links, stats = self._process_module(module_info)
                all_links.extend(links)
                countries_seen.update(stats['countries'])
                categories_seen.update(stats['categories'])
                api_count += stats['api_count']
                sources_processed += 1
                
                logger.info(f"  → {len(links)} links from {module_info.name}")
                
            except Exception as e:
                error_msg = f"Error processing {module_info.name}: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)
        
        # Build the final index
        index_data = {
            "version": "1.0.0",
            "generated_at": datetime.now().isoformat(),
            "generator": "Kloud IndexBuilder",
            "statistics": {
                "total_links": len(all_links),
                "countries": len(countries_seen),
                "categories": len(categories_seen),
                "api_links": api_count
            },
            "countries": sorted(list(countries_seen)),
            "categories": sorted(list(categories_seen)),
            "links": all_links
        }
        
        # Save to file
        output_path = os.path.join(self.output_dir, "links_index.json")
        self._save_index(index_data, output_path)
        
        # Calculate duration
        duration = (datetime.now() - start_time).total_seconds()
        
        return BuildResult(
            success=len(errors) == 0,
            total_links=len(all_links),
            sources_processed=sources_processed,
            countries=len(countries_seen),
            categories=len(categories_seen),
            api_links=api_count,
            duration_seconds=duration,
            errors=errors,
            output_path=output_path
        )
    
    def _process_module(self, module_info: SourceModule) -> tuple:
        """Process a single source module"""
        import importlib
        
        # Import the module
        module = importlib.import_module(module_info.module_path)
        
        # Get sources (different modules have different function names)
        sources = []
        if hasattr(module, 'get_all_sources'):
            sources = module.get_all_sources()
        elif hasattr(module, 'get_sources'):
            sources = module.get_sources()
        elif hasattr(module, 'GlobalDataSources'):
            gds = module.GlobalDataSources()
            sources = gds.get_all_sources()
        
        # Process each source into a link
        links = []
        countries = set()
        categories = set()
        api_count = 0
        
        for source in sources:
            link = self._source_to_link(source, module_info)
            links.append(link)
            
            # Track stats
            if link['country']:
                countries.add(link['country'])
            categories.add(link['category'])
            if link['api_available']:
                api_count += 1
        
        stats = {
            'countries': countries,
            'categories': categories,
            'api_count': api_count
        }
        
        return links, stats
    
    def _source_to_link(self, source: Any, module_info: SourceModule) -> Dict[str, Any]:
        """Convert a source object to a link dictionary"""
        from .link_scorer import LinkScorer
        scorer = LinkScorer()
        
        # Get category
        category = source.category.value if hasattr(source.category, 'value') else str(source.category)
        
        # Extract domain
        domain = self._extract_domain(source.url)
        
        # Generate tags
        tags = self._generate_tags(source, module_info)
        
        # Calculate score
        score = scorer.score(source)
        
        return {
            "id": self._generate_link_id(module_info.name),
            "title": source.name,
            "description": source.description,
            "url": source.url,
            "source": module_info.name,
            "region": module_info.region,
            "domain": domain,
            "country": source.country or "Global",
            "category": category,
            "layer": self._determine_layer(category),
            "tags": tags,
            "score": score,
            "api_available": source.api_available,
            "license": source.license,
            "last_verified": datetime.now().isoformat()
        }
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc or url
        except:
            return url
    
    def _generate_tags(self, source: Any, module_info: SourceModule) -> List[str]:
        """Generate tags for a source"""
        tags = []
        
        # Category tag
        cat = source.category.value if hasattr(source.category, 'value') else str(source.category)
        tags.append(cat.lower())
        
        # Region tag
        tags.append(module_info.region.lower().replace(" ", "-"))
        
        # API tag
        if source.api_available:
            tags.extend(["api", "open-data", "programmatic"])
        
        # Country tag
        if source.country:
            tags.append(source.country.lower())
        
        # Content-based tags
        text = f"{source.name} {source.description}".lower()
        if "open" in text:
            tags.append("open")
        if "data" in text:
            tags.append("data")
        if "statistics" in text or "stat" in text:
            tags.append("statistics")
        if "portal" in text:
            tags.append("portal")
        if "government" in text or "gov" in text:
            tags.append("government")
        
        return list(set(tags))[:15]
    
    def _determine_layer(self, category: str) -> int:
        """Determine which layer the source belongs to"""
        layer_map = {
            "GOVERNMENT": 7,
            "STATISTICS": 6,
            "UNIVERSITY": 7,
            "RESEARCH": 8,
            "TECHNOLOGY": 8,
            "BANK": 7,
            "HOSPITAL": 7,
            "NEWS": 10,
            "ENTERTAINMENT": 10,
            "SPORT": 10,
            "TOURISM": 10,
            "CULTURE": 10,
            "TRANSPORT": 7,
            "ENERGY": 7,
            "TELECOM": 7,
            "INDUSTRY": 7,
            "ENVIRONMENTAL": 7,
            "AGRICULTURE": 7,
            "HOBBY": 10,
            "PLAYFUL": 10,
        }
        return layer_map.get(category.upper(), 6)
    
    def _save_index(self, data: Dict[str, Any], path: str):
        """Save index to JSON file"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Index saved to {path}")
    
    def build_incremental(self, new_sources: List[Any]) -> int:
        """
        Add new sources to existing index
        
        Args:
            new_sources: List of new source objects
        
        Returns:
            Number of links added
        """
        # Load existing index
        index_path = os.path.join(self.output_dir, "links_index.json")
        existing_links = []
        
        if os.path.exists(index_path):
            with open(index_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                existing_links = data.get("links", [])
                self._link_counter = len(existing_links)
        
        # Add new sources
        added = 0
        for source in new_sources:
            module_info = SourceModule("manual", "manual", "Manual", 0)
            link = self._source_to_link(source, module_info)
            existing_links.append(link)
            added += 1
        
        # Save updated index
        index_data = {
            "version": "1.0.0",
            "generated_at": datetime.now().isoformat(),
            "total_links": len(existing_links),
            "links": existing_links
        }
        self._save_index(index_data, index_path)
        
        return added


# ============================================================================
# CLI INTERFACE
# ============================================================================

def main():
    """CLI interface for building the index"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Build Kloud Knowledge Index")
    parser.add_argument("--output", "-o", help="Output directory")
    parser.add_argument("--modules", "-m", nargs="+", help="Specific modules to include")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.basicConfig(level=logging.INFO)
    
    builder = IndexBuilder(output_dir=args.output)
    result = builder.build(include_modules=args.modules)
    
    print(f"\n{'='*60}")
    print("KNOWLEDGE INDEX BUILD COMPLETE")
    print(f"{'='*60}")
    print(f"Success: {result.success}")
    print(f"Total Links: {result.total_links:,}")
    print(f"Countries: {result.countries}")
    print(f"Categories: {result.categories}")
    print(f"API Links: {result.api_links:,}")
    print(f"Duration: {result.duration_seconds:.2f}s")
    print(f"Output: {result.output_path}")
    
    if result.errors:
        print(f"\nErrors ({len(result.errors)}):")
        for error in result.errors:
            print(f"  - {error}")


if __name__ == "__main__":
    main()

