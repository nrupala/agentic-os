"""
OpenTelemetry Tracing Module
============================
Distributed tracing for agentic-OS

MIT License
Copyright (c) 2024 Nrupal Akolkar
"""

import os
import logging
from typing import Optional
from functools import wraps

# OpenTelemetry imports
try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    from opentelemetry.sdk.resources import Resource, SERVICE_NAME
    from opentelemetry.trace import Status, StatusCode
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False
    print("[WARNING] OpenTelemetry not installed. Install with: pip install opentelemetry-api opentelemetry-sdk")

logger = logging.getLogger(__name__)


class TracingConfig:
    """Configuration for OpenTelemetry tracing."""
    
    def __init__(self):
        self.service_name = os.getenv("OTEL_SERVICE_NAME", "agentic-os")
        self.exporter_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
        self.export_interval = int(os.getenv("OTEL_EXPORT_INTERVAL_MS", "1000"))
        self.enabled = os.getenv("OTEL_ENABLED", "true").lower() == "true"


class Tracing:
    """OpenTelemetry tracing wrapper for agentic-OS."""
    
    _instance: Optional['Tracing'] = None
    _tracer: Optional[object] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.config = TracingConfig()
        self._tracer = None
        
        if OTEL_AVAILABLE and self.config.enabled:
            self._setup_tracing()
            self._initialized = True
    
    def _setup_tracing(self):
        """Setup OpenTelemetry tracing provider."""
        try:
            # Create resource with service name
            resource = Resource.create({
                SERVICE_NAME: self.config.service_name,
                "service.version": "1.0.0",
                "deployment.environment": os.getenv("OTEL_ENVIRONMENT", "development")
            })
            
            # Create tracer provider
            provider = TracerProvider(resource=resource)
            
            # Add console exporter for development
            if os.getenv("OTEL_CONSOLE_EXPORT", "true").lower() == "true":
                provider.add_span_processor(
                    BatchSpanProcessor(ConsoleSpanExporter())
                )
            
            # Set global tracer provider
            trace.set_tracer_provider(provider)
            
            # Get tracer
            self._tracer = trace.get_tracer(self.config.service_name)
            
            logger.info(f"OpenTelemetry tracing initialized for service: {self.config.service_name}")
            
        except Exception as e:
            logger.warning(f"Failed to initialize OpenTelemetry: {e}")
            self._tracer = None
    
    def get_tracer(self):
        """Get the tracer instance."""
        if self._tracer is None and OTEL_AVAILABLE:
            self._tracer = trace.get_tracer("agentic-os-fallback")
        return self._tracer
    
    def start_span(self, name: str, **attributes):
        """Start a new span."""
        tracer = self.get_tracer()
        if tracer:
            return tracer.start_span(name, attributes=attributes)
        return None
    
    def trace_function(self, func):
        """Decorator to trace a function."""
        if not OTEL_AVAILABLE:
            return func
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            tracer = self.get_tracer()
            if not tracer:
                return func(*args, **kwargs)
            
            with tracer.start_as_current_span(func.__name__) as span:
                try:
                    span.set_attribute("function.name", func.__name__)
                    span.set_attribute("function.module", func.__module__)
                    result = func(*args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    return result
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise
        
        return wrapper
    
    def trace_async(self, func):
        """Decorator to trace an async function."""
        if not OTEL_AVAILABLE:
            return func
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            tracer = self.get_tracer()
            if not tracer:
                return await func(*args, **kwargs)
            
            with tracer.start_as_current_span(func.__name__) as span:
                try:
                    span.set_attribute("function.name", func.__name__)
                    span.set_attribute("function.module", func.__module__)
                    result = await func(*args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    return result
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise
        
        return wrapper


# Global tracing instance
tracing = Tracing()


def get_tracer(name: str = "agentic-os"):
    """Get a tracer by name."""
    if OTEL_AVAILABLE:
        return trace.get_tracer(name)
    return None


def trace_operation(name: str, **attributes):
    """Context manager for tracing operations."""
    tracer = tracing.get_tracer()
    if tracer:
        return tracer.start_as_current_span(name, attributes=attributes)
    
    # Return a no-op context manager
    from contextlib import nullcontext
    return nullcontext()


# Export for use in other modules
__all__ = [
    'Tracing',
    'tracing',
    'get_tracer',
    'trace_operation',
    'trace',
    'StatusCode',
    'OTEL_AVAILABLE'
]