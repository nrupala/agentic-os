"""
Prometheus Metrics Module
==========================
Prometheus metrics for monitoring agentic-OS

MIT License
Copyright (c) 2024 Nrupal Akolkar
"""

import os
import logging
from typing import Optional, Dict, Any
from functools import wraps

# Prometheus imports
try:
    from prometheus_client import Counter, Histogram, Gauge, Summary, generate_latest, REGISTRY
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    print("[WARNING] prometheus-client not installed. Install with: pip install prometheus-client")

logger = logging.getLogger(__name__)


class MetricsConfig:
    """Configuration for Prometheus metrics."""
    
    def __init__(self):
        self.enabled = os.getenv("METRICS_ENABLED", "true").lower() == "true"
        self.port = int(os.getenv("METRICS_PORT", "9090"))
        self.namespace = os.getenv("METRICS_NAMESPACE", "agenticos")
        self.subsystem = os.getenv("METRICS_SUBSYSTEM", "")


class Metrics:
    """Prometheus metrics wrapper for agentic-OS."""
    
    _instance: Optional['Metrics'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.config = MetricsConfig()
        self._metrics: Dict[str, Any] = {}
        
        if PROMETHEUS_AVAILABLE and self.config.enabled:
            self._setup_metrics()
            self._initialized = True
    
    def _setup_metrics(self):
        """Setup Prometheus metrics."""
        ns = self.config.namespace
        
        # API metrics
        self._metrics['api_requests_total'] = Counter(
            'api_requests_total',
            'Total API requests',
            ['method', 'endpoint', 'status'],
            namespace=ns
        )
        
        self._metrics['api_request_duration_seconds'] = Histogram(
            'api_request_duration_seconds',
            'API request duration in seconds',
            ['method', 'endpoint'],
            namespace=ns
        )
        
        # Execution metrics
        self._metrics['executions_total'] = Counter(
            'executions_total',
            'Total execution attempts',
            ['status', 'request_type'],
            namespace=ns
        )
        
        self._metrics['execution_duration_seconds'] = Histogram(
            'execution_duration_seconds',
            'Execution duration in seconds',
            ['request_type'],
            namespace=ns
        )
        
        self._metrics['active_executions'] = Gauge(
            'active_executions',
            'Number of active executions',
            namespace=ns
        )
        
        # Tool metrics
        self._metrics['tool_invocations_total'] = Counter(
            'tool_invocations_total',
            'Total tool invocations',
            ['tool_name', 'status'],
            namespace=ns
        )
        
        self._metrics['tool_duration_seconds'] = Histogram(
            'tool_duration_seconds',
            'Tool invocation duration',
            ['tool_name'],
            namespace=ns
        )
        
        # Circuit breaker metrics
        self._metrics['circuit_breaker_state'] = Gauge(
            'circuit_breaker_state',
            'Circuit breaker state (0=closed, 1=open, 2=half-open)',
            ['name'],
            namespace=ns
        )
        
        self._metrics['circuit_breaker_failures_total'] = Counter(
            'circuit_breaker_failures_total',
            'Total circuit breaker failures',
            ['name'],
            namespace=ns
        )
        
        # Health metrics
        self._metrics['health_status'] = Gauge(
            'health_status',
            'Health status (1=healthy, 0=unhealthy)',
            ['component'],
            namespace=ns
        )
        
        logger.info("Prometheus metrics initialized")
    
    def record_api_request(self, method: str, endpoint: str, status: int, duration: float):
        """Record an API request."""
        if 'api_requests_total' in self._metrics:
            self._metrics['api_requests_total'].labels(
                method=method, endpoint=endpoint, status=status
            ).inc()
            self._metrics['api_request_duration_seconds'].labels(
                method=method, endpoint=endpoint
            ).observe(duration)
    
    def record_execution(self, status: str, request_type: str, duration: float = 0):
        """Record an execution."""
        if 'executions_total' in self._metrics:
            self._metrics['executions_total'].labels(
                status=status, request_type=request_type
            ).inc()
            if duration > 0:
                self._metrics['execution_duration_seconds'].labels(
                    request_type=request_type
                ).observe(duration)
    
    def set_active_executions(self, count: int):
        """Set the number of active executions."""
        if 'active_executions' in self._metrics:
            self._metrics['active_executions'].set(count)
    
    def record_tool_invocation(self, tool_name: str, status: str, duration: float):
        """Record a tool invocation."""
        if 'tool_invocations_total' in self._metrics:
            self._metrics['tool_invocations_total'].labels(
                tool_name=tool_name, status=status
            ).inc()
            self._metrics['tool_duration_seconds'].labels(
                tool_name=tool_name
            ).observe(duration)
    
    def set_circuit_breaker_state(self, name: str, state: int):
        """Set circuit breaker state."""
        if 'circuit_breaker_state' in self._metrics:
            self._metrics['circuit_breaker_state'].labels(name=name).set(state)
    
    def record_circuit_breaker_failure(self, name: str):
        """Record circuit breaker failure."""
        if 'circuit_breaker_failures_total' in self._metrics:
            self._metrics['circuit_breaker_failures_total'].labels(name=name).inc()
    
    def set_health_status(self, component: str, healthy: bool):
        """Set health status for a component."""
        if 'health_status' in self._metrics:
            self._metrics['health_status'].labels(component=component).set(1 if healthy else 0)
    
    def get_metrics(self) -> str:
        """Get all metrics in Prometheus format."""
        if PROMETHEUS_AVAILABLE:
            return generate_latest(REGISTRY)
        return ""


# Metrics decorator
def track_duration(metric_name: str):
    """Decorator to track function duration."""
    def decorator(func):
        if not PROMETHEUS_AVAILABLE:
            return func
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            import time
            start = time.time()
            try:
                return func(*args, **kwargs)
            finally:
                duration = time.time() - start
                metrics = Metrics()
                if hasattr(metrics, '_metrics') and f'{metric_name}_duration_seconds' in metrics._metrics:
                    metrics._metrics[f'{metric_name}_duration_seconds'].observe(duration)
        
        return wrapper
    return decorator


# Global metrics instance
metrics = Metrics()


__all__ = [
    'Metrics',
    'metrics',
    'MetricsConfig',
    'track_duration',
    'PROMETHEUS_AVAILABLE',
    'Counter',
    'Histogram',
    'Gauge',
    'Summary'
]