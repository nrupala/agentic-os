#!/usr/bin/env python3
"""
agentic-OS Circuit Breaker
==========================
Fail-fast resilience pattern for dependency failures

MIT License
Copyright (c) 2024 Nrupal Akolkar
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Callable, Optional, TypeVar, Awaitable
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps
import threading
import logging

T = TypeVar('T')

logger = logging.getLogger(__name__)


class CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreakerError(Exception):
    pass


class CircuitOpenError(CircuitBreakerError):
    pass


@dataclass
class CircuitMetrics:
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    rejected_calls: int = 0
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    state_changed_at: datetime = field(default_factory=datetime.utcnow)
    total_time_in_open: timedelta = field(default_factory=lambda: timedelta(0))


@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 5
    success_threshold: int = 2
    timeout: float = 60.0
    half_open_max_calls: int = 3
    excluded_exceptions: tuple = ()
    
    def __post_init__(self):
        if self.timeout <= 0:
            raise ValueError("timeout must be positive")


@dataclass
class CircuitInfo:
    name: str
    state: CircuitState
    metrics: CircuitMetrics
    config: CircuitBreakerConfig
    failure_rate: float = 0.0
    latency_p50_ms: float = 0.0
    latency_p95_ms: float = 0.0
    latency_p99_ms: float = 0.0


class CircuitBreaker:
    def __init__(
        self,
        name: str,
        config: Optional[CircuitBreakerConfig] = None,
        on_state_change: Optional[Callable[[str, CircuitState, CircuitState], None]] = None
    ):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self._state = CircuitState.CLOSED
        self._metrics = CircuitMetrics()
        self._lock = threading.RLock()
        self._on_state_change = on_state_change
        self._half_open_calls = 0
        self._call_latencies: list = []
        self._state_change_callbacks: list = []
        
        if on_state_change:
            self._state_change_callbacks.append(on_state_change)
    
    @property
    def state(self) -> CircuitState:
        with self._lock:
            self._check_timeout()
            return self._state
    
    @property
    def metrics(self) -> CircuitMetrics:
        with self._lock:
            return CircuitMetrics(
                total_calls=self._metrics.total_calls,
                successful_calls=self._metrics.successful_calls,
                failed_calls=self._metrics.failed_calls,
                rejected_calls=self._metrics.rejected_calls,
                consecutive_failures=self._metrics.consecutive_failures,
                consecutive_successes=self._metrics.consecutive_successes,
                last_failure_time=self._metrics.last_failure_time,
                last_success_time=self._metrics.last_success_time,
                state_changed_at=self._metrics.state_changed_at
            )
    
    def _check_timeout(self):
        if self._state == CircuitState.OPEN:
            if self._metrics.last_failure_time:
                elapsed = (datetime.utcnow() - self._metrics.last_failure_time).total_seconds()
                if elapsed >= self.config.timeout:
                    self._transition_to(CircuitState.HALF_OPEN)
                    self._half_open_calls = 0
    
    def _transition_to(self, new_state: CircuitState):
        old_state = self._state
        self._state = new_state
        self._metrics.state_changed_at = datetime.utcnow()
        
        if new_state == CircuitState.HALF_OPEN:
            self._metrics.consecutive_successes = 0
            self._half_open_calls = 0
        
        for callback in self._state_change_callbacks:
            try:
                callback(self.name, old_state, new_state)
            except Exception:
                pass
        
        logger.info(f"Circuit '{self.name}' transitioned from {old_state.value} to {new_state.value}")
    
    def _record_success(self, latency_ms: float):
        self._metrics.successful_calls += 1
        self._metrics.consecutive_successes += 1
        self._metrics.consecutive_failures = 0
        self._metrics.last_success_time = datetime.utcnow()
        self._call_latencies.append(latency_ms)
        
        if self._state == CircuitState.HALF_OPEN:
            if self._metrics.consecutive_successes >= self.config.success_threshold:
                self._transition_to(CircuitState.CLOSED)
    
    def _record_failure(self, exception: Optional[Exception] = None):
        self._metrics.failed_calls += 1
        self._metrics.consecutive_failures += 1
        self._metrics.consecutive_successes = 0
        self._metrics.last_failure_time = datetime.utcnow()
        
        if self._state == CircuitState.HALF_OPEN:
            self._transition_to(CircuitState.OPEN)
        elif self._state == CircuitState.CLOSED:
            if self._metrics.consecutive_failures >= self.config.failure_threshold:
                self._transition_to(CircuitState.OPEN)
    
    def _should_allow_request(self) -> bool:
        self._check_timeout()
        
        if self._state == CircuitState.CLOSED:
            return True
        
        if self._state == CircuitState.OPEN:
            return False
        
        if self._state == CircuitState.HALF_OPEN:
            if self._half_open_calls < self.config.half_open_max_calls:
                self._half_open_calls += 1
                return True
            return False
        
        return False
    
    async def call(self, func: Callable[..., Awaitable[T]], *args, **kwargs) -> T:
        if not self._should_allow_request():
            self._metrics.rejected_calls += 1
            raise CircuitOpenError(
                f"Circuit '{self.name}' is OPEN. Call rejected. "
                f"Retry after {(self.config.timeout - (datetime.utcnow() - self._metrics.last_failure_time).total_seconds()) if self._metrics.last_failure_time else self.config.timeout:.0f}s"
            )
        
        self._metrics.total_calls += 1
        start_time = time.perf_counter()
        
        try:
            result = await func(*args, **kwargs)
            latency_ms = (time.perf_counter() - start_time) * 1000
            self._record_success(latency_ms)
            return result
        except self.config.excluded_exceptions:
            latency_ms = (time.perf_counter() - start_time) * 1000
            self._record_success(latency_ms)
            raise
        except Exception as e:
            latency_ms = (time.perf_counter() - start_time) * 1000
            self._record_failure(e)
            raise
    
    def call_sync(self, func: Callable[..., T], *args, **kwargs) -> T:
        if not self._should_allow_request():
            self._metrics.rejected_calls += 1
            raise CircuitOpenError(
                f"Circuit '{self.name}' is OPEN. Call rejected."
            )
        
        self._metrics.total_calls += 1
        start_time = time.perf_counter()
        
        try:
            result = func(*args, **kwargs)
            latency_ms = (time.perf_counter() - start_time) * 1000
            self._record_success(latency_ms)
            return result
        except self.config.excluded_exceptions:
            latency_ms = (time.perf_counter() - start_time) * 1000
            self._record_success(latency_ms)
            raise
        except Exception as e:
            self._record_failure(e)
            raise
    
    def reset(self):
        with self._lock:
            self._state = CircuitState.CLOSED
            self._metrics = CircuitMetrics()
            self._half_open_calls = 0
            self._call_latencies = []
            logger.info(f"Circuit '{self.name}' has been reset")
    
    def get_info(self) -> CircuitInfo:
        with self._lock:
            self._check_timeout()
            
            latencies = sorted(self._call_latencies) if self._call_latencies else [0]
            p50 = latencies[int(len(latencies) * 0.5)] if latencies else 0
            p95 = latencies[int(len(latencies) * 0.95)] if latencies else 0
            p99 = latencies[int(len(latencies) * 0.99)] if latencies else 0
            
            failure_rate = 0.0
            if self._metrics.total_calls > 0:
                failure_rate = self._metrics.failed_calls / self._metrics.total_calls * 100
            
            return CircuitInfo(
                name=self.name,
                state=self._state,
                metrics=self._metrics,
                config=self.config,
                failure_rate=failure_rate,
                latency_p50_ms=p50,
                latency_p95_ms=p95,
                latency_p99_ms=p99
            )
    
    def on_state_change(self, callback: Callable[[str, CircuitState, CircuitState], None]):
        self._state_change_callbacks.append(callback)


class CircuitBreakerRegistry:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._circuits = {}
                    cls._instance._lock = threading.RLock()
        return cls._instance
    
    def register(
        self,
        name: str,
        config: Optional[CircuitBreakerConfig] = None
    ) -> CircuitBreaker:
        with self._lock:
            if name not in self._circuits:
                self._circuits[name] = CircuitBreaker(name, config)
            return self._circuits[name]
    
    def get(self, name: str) -> Optional[CircuitBreaker]:
        with self._lock:
            return self._circuits.get(name)
    
    def get_all(self) -> Dict[str, CircuitInfo]:
        with self._lock:
            return {name: cb.get_info() for name, cb in self._circuits.items()}
    
    def reset_all(self):
        with self._lock:
            for cb in self._circuits.values():
                cb.reset()


def circuit_breaker(
    name: str,
    config: Optional[CircuitBreakerConfig] = None
):
    registry = CircuitBreakerRegistry()
    cb = registry.register(name, config)
    
    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            return await cb.call(func, *args, **kwargs)
        return wrapper
    return decorator


def circuit_breaker_sync(
    name: str,
    config: Optional[CircuitBreakerConfig] = None
):
    registry = CircuitBreakerRegistry()
    cb = registry.register(name, config)
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            return cb.call_sync(func, *args, **kwargs)
        return wrapper
    return decorator


class FallbackHandler:
    def __init__(self):
        self._fallbacks: Dict[str, Callable] = {}
    
    def register(self, circuit_name: str, fallback: Callable):
        self._fallbacks[circuit_name] = fallback
    
    def get_fallback(self, circuit_name: str) -> Optional[Callable]:
        return self._fallbacks.get(circuit_name)
    
    async def execute_with_fallback(
        self,
        circuit_name: str,
        primary: Callable[..., Awaitable[T]],
        *args,
        **kwargs
    ) -> Optional[T]:
        fallback = self.get_fallback(circuit_name)
        
        try:
            registry = CircuitBreakerRegistry()
            cb = registry.get(circuit_name)
            if cb:
                return await cb.call(primary, *args, **kwargs)
            return await primary(*args, **kwargs)
        except CircuitOpenError:
            if fallback:
                logger.info(f"Executing fallback for '{circuit_name}'")
                return fallback(*args, **kwargs)
            return None
        except Exception as e:
            if fallback:
                logger.warning(f"Primary failed, executing fallback: {e}")
                return fallback(*args, **kwargs)
            raise


fallback_handler = FallbackHandler()


if __name__ == "__main__":
    import asyncio
    
    async def main():
        print("=" * 60)
        print("agentic-OS Circuit Breaker Demo")
        print("=" * 60)
        
        registry = CircuitBreakerRegistry()
        
        api_cb = registry.register("api", CircuitBreakerConfig(
            failure_threshold=3,
            success_threshold=2,
            timeout=5.0
        ))
        
        async def failing_service():
            import random
            if random.random() < 0.7:
                raise Exception("Service unavailable")
            return "Success!"
        
        print("\nTesting circuit breaker with random failures...\n")
        
        for i in range(10):
            try:
                result = await api_cb.call(failing_service)
                print(f"Call {i+1}: {result}")
            except CircuitOpenError as e:
                print(f"Call {i+1}: CIRCUIT OPEN - {e}")
            except Exception as e:
                print(f"Call {i+1}: Failed - {e}")
            
            await asyncio.sleep(0.5)
        
        info = api_cb.get_info()
        print(f"\nCircuit Info:")
        print(f"  State: {info.state.value}")
        print(f"  Total calls: {info.metrics.total_calls}")
        print(f"  Failed: {info.metrics.failed_calls}")
        print(f"  Rejected: {info.metrics.rejected_calls}")
        print(f"  Failure rate: {info.failure_rate:.1f}%")
        print("=" * 60)
    
    asyncio.run(main())
