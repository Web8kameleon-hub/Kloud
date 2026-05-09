"""
Prometheus metrics module for Kloud
Provides FastAPI middleware for automatic metrics collection
"""

from prometheus_client import Counter, Histogram, Gauge, REGISTRY, generate_latest
from prometheus_client.core import CollectorRegistry
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time
import logging

logger = logging.getLogger(__name__)

# Create a separate registry for better isolation
metrics_registry = CollectorRegistry()

# Request metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code'],
    registry=metrics_registry
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency in seconds',
    ['method', 'endpoint'],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
    registry=metrics_registry
)

# Request size metrics
http_request_size_bytes = Histogram(
    'http_request_size_bytes',
    'HTTP request size in bytes',
    ['method', 'endpoint'],
    registry=metrics_registry
)

http_response_size_bytes = Histogram(
    'http_response_size_bytes',
    'HTTP response size in bytes',
    ['method', 'endpoint'],
    registry=metrics_registry
)

# Business metrics
api_calls_total = Counter(
    'api_calls_total',
    'Total API calls by endpoint',
    ['endpoint'],
    registry=metrics_registry
)

ai_agent_executions = Counter(
    'ai_agent_executions_total',
    'Total AI agent executions',
    ['agent_type', 'status'],
    registry=metrics_registry
)

processing_time_seconds = Histogram(
    'processing_time_seconds',
    'Processing time in seconds',
    ['operation'],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0),
    registry=metrics_registry
)

# System metrics
active_connections = Gauge(
    'active_connections',
    'Number of active connections',
    registry=metrics_registry
)

cache_hits = Counter(
    'cache_hits_total',
    'Total cache hits',
    ['cache_name'],
    registry=metrics_registry
)

cache_misses = Counter(
    'cache_misses_total',
    'Total cache misses',
    ['cache_name'],
    registry=metrics_registry
)

# AI & Document Generation Metrics
ai_agent_duration_seconds = Histogram(
    'ai_agent_duration_seconds',
    'AI agent execution time in seconds',
    ['agent_type'],  # crewai, langchain, claude
    buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0),
    registry=metrics_registry
)

ai_agent_tokens_used = Counter(
    'ai_agent_tokens_used_total',
    'Total tokens consumed by AI agents',
    ['agent_type', 'token_type'],  # token_type: input, output
    registry=metrics_registry
)

documents_generated_total = Counter(
    'documents_generated_total',
    'Total documents generated',
    ['document_type', 'status'],  # status: success, error
    registry=metrics_registry
)

document_generation_duration_seconds = Histogram(
    'document_generation_duration_seconds',
    'Document generation time in seconds',
    ['document_type'],
    buckets=(0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0),
    registry=metrics_registry
)

document_size_bytes = Histogram(
    'document_size_bytes',
    'Generated document size in bytes',
    ['document_type'],
    buckets=(1024, 5120, 10240, 51200, 102400, 512000, 1048576),
    registry=metrics_registry
)

api_validation_errors_total = Counter(
    'api_validation_errors_total',
    'Total validation errors',
    ['endpoint', 'error_type'],
    registry=metrics_registry
)

# Business/SLA Metrics
api_calls_authenticated = Counter(
    'api_calls_authenticated_total',
    'Authenticated API calls by user tier',
    ['endpoint', 'user_tier'],  # tier: free, pro, enterprise
    registry=metrics_registry
)

subscription_value_usd = Gauge(
    'subscription_value_usd',
    'Current MRR (Monthly Recurring Revenue) in USD',
    ['tier'],  # tier: free, pro, enterprise
    registry=metrics_registry
)

background_jobs_running = Gauge(
    'background_jobs_running',
    'Number of running background jobs',
    ['job_type'],
    registry=metrics_registry
)

queue_depth = Gauge(
    'queue_depth',
    'Number of items in processing queue',
    ['queue_name'],
    registry=metrics_registry
)


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to collect HTTP metrics"""
    
    async def dispatch(self, request: Request, call_next) -> Response:
        method = request.method
        path = request.url.path
        
        # Normalize path to prevent cardinality explosion
        endpoint = self._normalize_path(path)
        
        start_time = time.time()
        
        try:
            # Get request size
            if request.method in ["POST", "PUT"]:
                body = await request.body()
                request_size = len(body)
            else:
                request_size = 0
            
            response = await call_next(request)
            
            # Record metrics
            duration = time.time() - start_time
            status_code = response.status_code
            
            http_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status_code=status_code
            ).inc()
            
            http_request_duration_seconds.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)
            
            if request_size > 0:
                http_request_size_bytes.labels(
                    method=method,
                    endpoint=endpoint
                ).observe(request_size)
            
            # Estimate response size
            if hasattr(response, 'body'):
                response_size = len(response.body)
                http_response_size_bytes.labels(
                    method=method,
                    endpoint=endpoint
                ).observe(response_size)
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            http_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status_code=500
            ).inc()
            http_request_duration_seconds.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)
            logger.error(f"Error in metrics middleware: {e}")
            raise
    
    @staticmethod
    def _normalize_path(path: str) -> str:
        """Normalize path to prevent cardinality explosion"""
        # Convert numeric IDs to {id}
        import re
        
        # Common patterns for IDs
        normalized = re.sub(r'/\d+', '/{id}', path)
        normalized = re.sub(r'/[a-f0-9]{8}(-[a-f0-9]{4}){3}-[a-f0-9]{12}', '/{uuid}', normalized)
        
        return normalized if normalized != path else path


def get_metrics() -> bytes:
    """Get all metrics in Prometheus text format"""
    return generate_latest(metrics_registry)



