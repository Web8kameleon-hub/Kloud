"""OpenTelemetry Tracing Configuration for Kloud Cloud.

This module provides distributed tracing setup for all microservices,
enabling enterprise-level observability through Grafana Tempo.

Each microservice uses this module to:
1. Create a TracerProvider with proper Resource attributes
2. Export spans to Tempo via OTLP HTTP
3. Integrate with FastAPI and HTTP client libraries

Usage:
    from tracing import setup_tracing
    tracer = setup_tracing("alba")

    @app.get("/health")
    async def health():
        with tracer.start_as_current_span("health_check"):
            return {"status": "ok"}
"""

import os
import socket
from urllib.parse import urlparse
from typing import Optional

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.instrumentation.fastapi import (
    FastAPIInstrumentor,
)  # type: ignore
from opentelemetry.instrumentation.requests import (
    RequestsInstrumentor,
)  # type: ignore
from opentelemetry.instrumentation.aiohttp_client import (
    AioHttpClientInstrumentor,
)  # type: ignore
from opentelemetry.instrumentation.logging import (
    LoggingInstrumentor,
)  # type: ignore
from opentelemetry.trace import Status, StatusCode


def setup_tracing(
    service_name: str,
    environment: str = "production",
    tempo_endpoint: Optional[str] = None,
) -> trace.Tracer:
    """
    Initialize OpenTelemetry tracing for a microservice.

    Args:
        service_name: Name of the service (alba, albi, jona, api, etc.)
        environment: Deployment environment (production, staging, development)
        tempo_endpoint: Tempo OTLP HTTP endpoint.
            Defaults to http://tempo:4318/v1/traces (optional)

    Returns:
        OpenTelemetry Tracer instance for the service

    Note:
        Tempo tracing is optional. If Tempo endpoint is not available,
        tracing will still work with a no-op exporter.
    """
    if tempo_endpoint is None:
        # Respect standard OTEL variables first, then project-specific fallback.
        traces_endpoint = os.getenv("OTEL_EXPORTER_OTLP_TRACES_ENDPOINT")
        otlp_base = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
        if traces_endpoint:
            tempo_endpoint = traces_endpoint
        elif otlp_base:
            tempo_endpoint = otlp_base.rstrip("/") + "/v1/traces"
        else:
            tempo_endpoint = os.getenv("TEMPO_ENDPOINT", "http://tempo:4318/v1/traces")

    def _endpoint_resolvable(endpoint: str) -> bool:
        try:
            parsed = urlparse(endpoint)
            host = parsed.hostname
            if not host:
                return False
            socket.getaddrinfo(host, parsed.port or 80)
            return True
        except Exception:
            return False

    # Create Resource with service identification
    resource = Resource.create(
        {
            "service.name": service_name,
            "service.version": "1.2.3",
            "environment": environment,
            "host.name": os.getenv("HOSTNAME", "unknown"),
        }
    )

    # Create TracerProvider with Resource
    tracer_provider = TracerProvider(resource=resource)

    # Try to connect to Tempo, but don't fail if unavailable
    try:
        # On local Windows runs, "tempo" is typically a Docker-internal DNS name.
        if not _endpoint_resolvable(tempo_endpoint):
            print(
                f"⚠️  Tracing exporter disabled for {service_name} "
                f"(unresolvable OTLP endpoint: {tempo_endpoint})"
            )
            trace.set_tracer_provider(tracer_provider)
            return trace.get_tracer(service_name)

        otlp_exporter = OTLPSpanExporter(
            endpoint=tempo_endpoint,
            timeout=10,
            headers={"User-Agent": f"kloud/{service_name}"},
        )
        batch_processor = BatchSpanProcessor(
            otlp_exporter,
            max_queue_size=2048,
            max_export_batch_size=512,
        )
        tracer_provider.add_span_processor(batch_processor)
        print(f"✓ Tracing enabled for {service_name} → {tempo_endpoint}")
    except Exception as e:
        print(f"⚠️  Tracing disabled for {service_name} (Tempo unavailable: {e})")
        # Tracing will still work with no-op exporter

    # Set global tracer provider
    trace.set_tracer_provider(tracer_provider)

    return trace.get_tracer(service_name)


def instrument_fastapi_app(app, service_name: str) -> None:
    """
    Instrument a FastAPI application for automatic tracing.

    Args:
        app: FastAPI application instance
        service_name: Name of the service for trace identification
    """
    FastAPIInstrumentor.instrument_app(app)


def instrument_http_clients() -> None:
    """
    Instrument HTTP client libraries for automatic tracing:
    - requests library
    - aiohttp client
    """
    RequestsInstrumentor().instrument()
    AioHttpClientInstrumentor().instrument()


def instrument_logging() -> None:
    """
    Instrument logging to include trace context in logs.
    """
    LoggingInstrumentor().instrument()


def get_tracer_for_service(service_name: str) -> trace.Tracer:
    """
    Get or create a tracer for a service.

    Args:
        service_name: Name of the service

    Returns:
        OpenTelemetry Tracer instance
    """
    return trace.get_tracer(service_name)


def create_span_with_error_handling(
    tracer: trace.Tracer,
    span_name: str,
    attributes: Optional[dict] = None,
):
    """
    Context manager that creates a span and handles errors.

    Usage:
        with create_span_with_error_handling(
            tracer, "process_packet", {"packet_size": 256}
        ):
            # span automatically created and errors tracked
            do_processing()
    """

    class SpanContextManager:
        def __init__(self, tracer, name, attrs):
            self.tracer = tracer
            self.name = name
            self.attrs = attrs or {}
            self.span = None

        def __enter__(self):
            self.span = self.tracer.start_as_current_span(self.name)
            self.span.__enter__()
            for key, value in self.attrs.items():
                self.span.set_attribute(key, value)
            return self.span

        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_type is not None:
                self.span.set_attribute("error", True)
                self.span.set_attribute("error.type", exc_type.__name__)
                self.span.set_attribute("error.message", str(exc_val))
                self.span.set_status(Status(StatusCode.ERROR))
            return self.span.__exit__(exc_type, exc_val, exc_tb)

    return SpanContextManager(tracer, span_name, attributes)


# Context propagation helper for inter-service calls
def get_trace_context_headers() -> dict:
    """
    Extract current trace context as HTTP headers for propagation.

    Returns:
        Dictionary of headers containing trace context
    """
    from opentelemetry.propagators.jaeger.jaeger import (
        Jaeger,
    )  # type: ignore

    propagator = Jaeger()
    return propagator.inject({})


__all__ = [
    "setup_tracing",
    "instrument_fastapi_app",
    "instrument_http_clients",
    "instrument_logging",
    "get_tracer_for_service",
    "create_span_with_error_handling",
    "get_trace_context_headers",
]
