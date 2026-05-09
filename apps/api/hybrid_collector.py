"""
Hybrid Data Collector - Multi-Source Data Aggregation
Combines internal files, cycles, docs, stats with external open APIs.
Implements priority-based data fetching for self-evolution.
"""

import asyncio
import json
import httpx
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from enum import Enum

from apps.api.internal_client import InternalAPIClient, DataSource


class HybridDataCollector:
    \"\"\"
    Collects data from multiple sources with priority ordering:
    1. Local files (cycles, docs, stats)
    2. Internal APIs (Weaviate cache, processed data)
    3. External Open APIs (OpenAlex, PubMed, etc.)
    
    Supports self-evolution by prioritizing internal data sources.
    \"\"\"
    
    def __init__(
        self,
        project_root: Optional[Path] = None,
        internal_api_url: str = 'http://localhost:8000'
    ):
        self.project_root = project_root or Path.cwd()
        self.internal_client = InternalAPIClient(base_url=internal_api_url)
        
        # Define data source paths
        self.data_paths = {
            'cycles': self.project_root / 'cycles',
            'docs': self.project_root / 'docs',
            'research': self.project_root / 'research',
            'data': self.project_root / 'data'
        }
        
        # External API registry
        self.external_apis = {
            'research': [
                'https://api.openalex.org',
                'https://api.semanticscholar.org',
                'https://eutils.ncbi.nlm.nih.gov/entrez/eutils'
            ],
            'health': [
                'https://clinicaltrials.gov/api/v2',
                'https://api.fda.gov'
            ],
            'weather': [
                'https://api.open-meteo.com/v1'
            ],
            'crypto': [
                'https://api.coingecko.com/api/v3'
            ],
            'genomics': [
                'https://rest.ensembl.org',
                'https://www.ebi.ac.uk/proteins/api'
            ]
        }
        
        self.stats = {
            'local_file_queries': 0,
            'internal_api_queries': 0,
            'external_api_queries': 0,
            'total_queries': 0,
            'data_sources_used': []
        }
    
    async def query_local_files(
        self,
        category: str,
        query: str,
        file_pattern: str = '*.json'
    ) -> List[Dict[str, Any]]:
        \"\"\"Query local files (cycles, docs, data)\"\"\"
        results = []
        
        if category not in self.data_paths:
            return results
        
        path = self.data_paths[category]
        if not path.exists():
            return results
        
        try:
            for file_path in path.rglob(file_pattern):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                        # Simple text search in JSON content
                        content_str = json.dumps(data).lower()
                        if query.lower() in content_str:
                            results.append({
                                'source': 'local_file',
                                'file': str(file_path.relative_to(self.project_root)),
                                'data': data,
                                'timestamp': datetime.now().isoformat()
                            })
                except:
                    continue
            
            self.stats['local_file_queries'] += 1
        except Exception as e:
            pass
        
        return results
    
    async def query_cycles(self, query: str) -> List[Dict[str, Any]]:
        \"\"\"Query cycle JSON files\"\"\"
        return await self.query_local_files('cycles', query, '*.json')
    
    async def query_docs(self, query: str) -> List[Dict[str, Any]]:
        \"\"\"Query documentation files\"\"\"
        md_results = await self.query_local_files('docs', query, '*.md')
        
        # Also search text content in markdown
        docs_path = self.data_paths['docs']
        if docs_path.exists():
            for md_file in docs_path.rglob('*.md'):
                try:
                    content = md_file.read_text(encoding='utf-8')
                    if query.lower() in content.lower():
                        md_results.append({
                            'source': 'local_doc',
                            'file': str(md_file.relative_to(self.project_root)),
                            'content': content[:500],  # First 500 chars
                            'timestamp': datetime.now().isoformat()
                        })
                except:
                    continue
        
        return md_results
    
    async def query_internal_api(
        self,
        endpoint: str,
        params: Optional[Dict] = None
    ) -> Optional[Dict[str, Any]]:
        \"\"\"Query internal Kloud API\"\"\"
        try:
            result = await self.internal_client.get(endpoint, params=params)
            self.stats['internal_api_queries'] += 1
            return result
        except Exception as e:
            return None
    
    async def query_external_api(
        self,
        api_url: str,
        params: Optional[Dict] = None
    ) -> Optional[Dict[str, Any]]:
        \"\"\"Query external open API\"\"\"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(api_url, params=params)
                response.raise_for_status()
                
                self.stats['external_api_queries'] += 1
                return {
                    'source': 'external_api',
                    'api': api_url,
                    'data': response.json(),
                    'timestamp': datetime.now().isoformat()
                }
        except Exception:
            return None
    
    async def hybrid_collect(
        self,
        query: str,
        categories: List[str] = ['cycles', 'docs', 'research'],
        min_results: int = 5,
        use_external: bool = True
    ) -> Dict[str, Any]:
        \"\"\"
        Collect data from multiple sources with hybrid approach.
        
        Priority:
        1. Local files (cycles, docs)
        2. Internal APIs (if endpoint provided)
        3. External APIs (if enabled and needed)
        \"\"\"
        self.stats['total_queries'] += 1
        all_results = []
        sources_used = []
        
        # Phase 1: Local files
        for category in categories:
            if category == 'cycles':
                cycle_results = await self.query_cycles(query)
                all_results.extend(cycle_results)
                if cycle_results:
                    sources_used.append('cycles')
            
            elif category == 'docs':
                doc_results = await self.query_docs(query)
                all_results.extend(doc_results)
                if doc_results:
                    sources_used.append('docs')
            
            elif category == 'research':
                research_files = await self.query_local_files('research', query, '*.py')
                all_results.extend(research_files)
                if research_files:
                    sources_used.append('research_files')
        
        # Phase 2: Internal API (if exists)
        if len(all_results) < min_results:
            # Try internal research API
            internal_result = await self.query_internal_api(
                '/research/query',
                params={'q': query, 'limit': min_results}
            )
            if internal_result and internal_result.get('source') == 'internal':
                all_results.append(internal_result)
                sources_used.append('internal_api')
        
        # Phase 3: External APIs (if still not enough data)
        if use_external and len(all_results) < min_results:
            # Query OpenAlex
            openalex_result = await self.query_external_api(
                'https://api.openalex.org/works',
                params={'search': query, 'per_page': 5}
            )
            if openalex_result:
                all_results.append(openalex_result)
                sources_used.append('openalex')
        
        # Update stats
        self.stats['data_sources_used'] = list(set(self.stats['data_sources_used'] + sources_used))
        
        return {
            'query': query,
            'total_results': len(all_results),
            'sources_used': sources_used,
            'results': all_results,
            'self_consumption_ratio': self._calculate_self_consumption(sources_used),
            'timestamp': datetime.now().isoformat()
        }
    
    async def hybrid_research(
        self,
        topic: str,
        include_external: bool = True
    ) -> Dict[str, Any]:
        \"\"\"Specialized research data collection\"\"\"
        results = []
        
        # 1. Local research files
        research_files = await self.query_local_files('research', topic, '*.py')
        results.extend(research_files)
        
        # 2. Docs
        doc_results = await self.query_docs(topic)
        results.extend(doc_results)
        
        # 3. Internal research API
        internal = await self.query_internal_api('/research/query', {'topic': topic})
        if internal:
            results.append(internal)
        
        # 4. External research APIs
        if include_external and len(results) < 10:
            # OpenAlex
            openalex = await self.query_external_api(
                'https://api.openalex.org/works',
                {'filter': f'title.search:{topic}', 'per_page': 5}
            )
            if openalex:
                results.append(openalex)
            
            # Semantic Scholar
            semantic = await self.query_external_api(
                'https://api.semanticscholar.org/graph/v1/paper/search',
                {'query': topic, 'limit': 5}
            )
            if semantic:
                results.append(semantic)
        
        return {
            'topic': topic,
            'total_results': len(results),
            'results': results
        }
    
    async def hybrid_weather(
        self,
        city: str,
        coords: Optional[tuple[float, float]] = None
    ) -> Dict[str, Any]:
        \"\"\"Weather data with internal cache first\"\"\"
        
        # Try internal API first (cached data)
        internal = await self.query_internal_api(
            '/api/weather',
            {'city': city}
        )
        
        if internal and internal.get('source') == 'internal':
            return internal
        
        # Fallback to external
        if coords:
            lat, lon = coords
            external = await self.query_external_api(
                'https://api.open-meteo.com/v1/forecast',
                {'latitude': lat, 'longitude': lon, 'current_weather': True}
            )
            return external or {'error': 'No data available'}
        
        return {'error': 'No coordinates provided for external query'}
    
    async def hybrid_crypto(
        self,
        coins: List[str] = ['bitcoin', 'ethereum']
    ) -> Dict[str, Any]:
        \"\"\"Crypto prices with internal aggregator first\"\"\"
        
        # Internal API (aggregated/cached)
        internal = await self.query_internal_api(
            '/api/crypto/market',
            {'coins': ','.join(coins)}
        )
        
        if internal and internal.get('source') == 'internal':
            return internal
        
        # External fallback
        external = await self.query_external_api(
            'https://api.coingecko.com/api/v3/simple/price',
            {'ids': ','.join(coins), 'vs_currencies': 'usd'}
        )
        
        return external or {'error': 'No data available'}
    
    def _calculate_self_consumption(self, sources_used: List[str]) -> float:
        \"\"\"Calculate percentage of internal vs external sources\"\"\"
        if not sources_used:
            return 0.0
        
        internal_sources = {'cycles', 'docs', 'research_files', 'internal_api', 'local_file'}
        internal_count = sum(1 for s in sources_used if s in internal_sources)
        
        return (internal_count / len(sources_used)) * 100
    
    def get_stats(self) -> Dict[str, Any]:
        \"\"\"Get collection statistics\"\"\"
        total_queries = (
            self.stats['local_file_queries'] +
            self.stats['internal_api_queries'] +
            self.stats['external_api_queries']
        )
        
        if total_queries == 0:
            self_consumption = 0.0
        else:
            internal_queries = self.stats['local_file_queries'] + self.stats['internal_api_queries']
            self_consumption = (internal_queries / total_queries) * 100
        
        return {
            **self.stats,
            'self_consumption_ratio': self_consumption
        }


# Global instance
hybrid_collector = HybridDataCollector()


# Example usage
async def demo_hybrid_collection():
    collector = HybridDataCollector()
    
    print('=== Hybrid Data Collection Demo ===\\n')
    
    # 1. Query cycles + docs
    result = await collector.hybrid_collect(
        query='neural',
        categories=['cycles', 'docs'],
        min_results=3
    )
    print(f\"Query: 'neural'\")
    print(f\"  Total results: {result['total_results']}\")
    print(f\"  Sources used: {', '.join(result['sources_used'])}\")
    print(f\"  Self-consumption: {result['self_consumption_ratio']:.1f}%\\n\")
    
    # 2. Research query
    research = await collector.hybrid_research('machine learning')
    print(f\"Research: 'machine learning'\")
    print(f\"  Total results: {research['total_results']}\\n\")
    
    # 3. Statistics
    stats = collector.get_stats()
    print('Statistics:')
    print(f\"  Total queries: {stats['total_queries']}\")
    print(f\"  Local file queries: {stats['local_file_queries']}\")
    print(f\"  Internal API queries: {stats['internal_api_queries']}\")
    print(f\"  External API queries: {stats['external_api_queries']}\")
    print(f\"  Self-consumption ratio: {stats['self_consumption_ratio']:.1f}%\")


if __name__ == '__main__':
    asyncio.run(demo_hybrid_collection())

