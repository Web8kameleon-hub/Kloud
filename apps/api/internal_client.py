"""
Internal API Client - Self-Consumption Layer
Enables Kloud modules to consume own APIs FIRST before external sources.
Implements fallback logic, circuit breaker, and hybrid data collection.
"""

import asyncio
import httpx
import time
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum


class DataSource(Enum):
    """Priority-ordered data sources for hybrid collection"""
    INTERNAL_API = 1  # Highest priority
    LOCAL_CACHE = 2
    CYCLES_DB = 3
    WEAVIATE = 4
    EXTERNAL_API = 5  # Lowest priority


class CircuitState(Enum):
    CLOSED = 'closed'  # Normal operation
    OPEN = 'open'      # Failing, use fallback
    HALF_OPEN = 'half_open'  # Testing recovery


class CircuitBreaker:
    """Prevents cascading failures from internal API calls"""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
    
    def record_success(self):
        self.failure_count = 0
        self.state = CircuitState.CLOSED
    
    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
    
    def can_attempt(self) -> bool:
        if self.state == CircuitState.CLOSED:
            return True
        
        if self.state == CircuitState.OPEN:
            # Check if timeout expired
            if self.last_failure_time:
                elapsed = (datetime.now() - self.last_failure_time).total_seconds()
                if elapsed >= self.timeout:
                    self.state = CircuitState.HALF_OPEN
                    return True
            return False
        
        # HALF_OPEN state
        return True


class InternalAPIClient:
    """
    Client for consuming Kloud's own APIs with automatic fallback.
    Implements self-consumption pattern for self-evolution.
    """
    
    def __init__(
        self,
        base_url: str = 'http://localhost:8000',
        timeout: float = 5.0,
        enable_fallback: bool = True
    ):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.enable_fallback = enable_fallback
        self.circuit_breaker = CircuitBreaker()
        self.stats = {
            'internal_calls': 0,
            'external_calls': 0,
            'cache_hits': 0,
            'failures': 0
        }
        self._cache: Dict[str, tuple[Any, datetime]] = {}
        self.cache_ttl = timedelta(minutes=5)
    
    def _cache_key(self, endpoint: str, params: Optional[Dict] = None) -> str:
        """Generate cache key from endpoint and params"""
        if params:
            param_str = '&'.join(f'{k}={v}' for k, v in sorted(params.items()))
            return f'{endpoint}?{param_str}'
        return endpoint
    
    def _get_from_cache(self, key: str) -> Optional[Any]:
        """Get data from local cache if not expired"""
        if key in self._cache:
            data, timestamp = self._cache[key]
            if datetime.now() - timestamp < self.cache_ttl:
                self.stats['cache_hits'] += 1
                return data
            else:
                del self._cache[key]
        return None
    
    def _set_cache(self, key: str, data: Any):
        """Store data in local cache"""
        self._cache[key] = (data, datetime.now())
    
    async def get(
        self,
        endpoint: str,
        params: Optional[Dict] = None,
        fallback_external: Optional[str] = None,
        fallback_fn: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        GET request with internal-first, external-fallback pattern.
        
        Priority:
        1. Local cache (if fresh)
        2. Internal API (self-consumption)
        3. External API (if provided)
        4. Fallback function (if provided)
        """
        cache_key = self._cache_key(endpoint, params)
        
        # Try cache first
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return {'source': 'cache', 'data': cached}
        
        # Try internal API if circuit breaker allows
        if self.circuit_breaker.can_attempt():
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    url = f'{self.base_url}{endpoint}'
                    response = await client.get(url, params=params)
                    response.raise_for_status()
                    
                    data = response.json()
                    self.stats['internal_calls'] += 1
                    self.circuit_breaker.record_success()
                    self._set_cache(cache_key, data)
                    
                    return {'source': 'internal', 'data': data}
            
            except Exception as e:
                self.circuit_breaker.record_failure()
                self.stats['failures'] += 1
                
                if not self.enable_fallback:
                    raise
        
        # Fallback to external API
        if fallback_external:
            try:
                async with httpx.AsyncClient(timeout=self.timeout * 2) as client:
                    response = await client.get(fallback_external, params=params)
                    response.raise_for_status()
                    
                    data = response.json()
                    self.stats['external_calls'] += 1
                    self._set_cache(cache_key, data)
                    
                    return {'source': 'external', 'data': data}
            
            except Exception:
                pass
        
        # Fallback function
        if fallback_fn:
            try:
                data = await fallback_fn() if asyncio.iscoroutinefunction(fallback_fn) else fallback_fn()
                return {'source': 'external', 'data': data}
            except Exception:
                pass
        
        raise RuntimeError(f'All data sources failed for {endpoint}')
    
    async def post(
        self,
        endpoint: str,
        json: Optional[Dict] = None,
        fallback_external: Optional[str] = None
    ) -> Dict[str, Any]:
        """POST request to internal API with external fallback"""
        
        if self.circuit_breaker.can_attempt():
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    url = f'{self.base_url}{endpoint}'
                    response = await client.post(url, json=json)
                    response.raise_for_status()
                    
                    data = response.json()
                    self.stats['internal_calls'] += 1
                    self.circuit_breaker.record_success()
                    
                    return {'source': 'internal', 'data': data}
            
            except Exception:
                self.circuit_breaker.record_failure()
                self.stats['failures'] += 1
                
                if not self.enable_fallback:
                    raise
        
        # Fallback to external
        if fallback_external:
            try:
                async with httpx.AsyncClient(timeout=self.timeout * 2) as client:
                    response = await client.post(fallback_external, json=json)
                    response.raise_for_status()
                    
                    data = response.json()
                    self.stats['external_calls'] += 1
                    
                    return {'source': 'external', 'data': data}
            except Exception:
                pass
        
        raise RuntimeError(f'All data sources failed for {endpoint}')
    
    def get_self_consumption_ratio(self) -> float:
        """Calculate percentage of internal vs external calls"""
        total = self.stats['internal_calls'] + self.stats['external_calls']
        if total == 0:
            return 0.0
        return (self.stats['internal_calls'] / total) * 100
    
    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        return {
            **self.stats,
            'self_consumption_ratio': self.get_self_consumption_ratio(),
            'circuit_state': self.circuit_breaker.state.value,
            'cache_size': len(self._cache)
        }


# Global instance for easy import
internal_client = InternalAPIClient()


# Example usage patterns
async def example_crypto_prices():
    \"\"\"Example: Get crypto prices with self-consumption pattern\"\"\"
    client = InternalAPIClient()
    
    result = await client.get(
        endpoint='/api/crypto/market',
        params={'coins': 'bitcoin,ethereum'},
        fallback_external='https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd'
    )
    
    print(f\"Data source: {result['source']}\")
    return result['data']


async def example_weather_data():
    \"\"\"Example: Get weather with hybrid approach\"\"\"
    client = InternalAPIClient()
    
    result = await client.get(
        endpoint='/api/weather',
        params={'city': 'Tirana'},
        fallback_external='https://api.open-meteo.com/v1/forecast?latitude=41.3275&longitude=19.8187'
    )
    
    return result


async def example_research_query():
    \"\"\"Example: Query research data (internal Weaviate first, then external)\"\"\"
    client = InternalAPIClient()
    
    result = await client.post(
        endpoint='/research/query',
        json={'query': 'neural networks', 'limit': 10},
        fallback_external='https://api.openalex.org/works?search=neural+networks'
    )
    
    return result


if __name__ == '__main__':
    # Demo self-consumption pattern
    async def demo():
        client = InternalAPIClient()
        
        print('=== Self-Consumption Demo ===')
        
        # Make several calls
        await client.get('/health')
        await client.get('/api/system-status')
        await client.get('/asi/status')
        
        # Show statistics
        stats = client.get_stats()
        print(f\"\\nStatistics:\")
        print(f\"  Internal calls: {stats['internal_calls']}\")
        print(f\"  External calls: {stats['external_calls']}\")
        print(f\"  Cache hits: {stats['cache_hits']}\")
        print(f\"  Self-consumption ratio: {stats['self_consumption_ratio']:.1f}%\")
        print(f\"  Circuit state: {stats['circuit_state']}\")
    
    asyncio.run(demo())

