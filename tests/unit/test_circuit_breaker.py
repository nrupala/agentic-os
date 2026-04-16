#!/usr/bin/env python3
"""
Unit tests for observability/circuit_breaker.py

MIT License
Copyright (c) 2024 Nrupal Akolkar
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from observability.circuit_breaker import (
    CircuitState,
    CircuitBreakerError,
    CircuitOpenError,
    CircuitMetrics,
    CircuitBreakerConfig,
    CircuitInfo,
    CircuitBreaker,
    CircuitBreakerRegistry,
    FallbackHandler,
    circuit_breaker,
    circuit_breaker_sync
)


class TestCircuitState:
    def test_circuit_state_values(self):
        assert CircuitState.CLOSED.value == "closed"
        assert CircuitState.OPEN.value == "open"
        assert CircuitState.HALF_OPEN.value == "half_open"

    def test_circuit_state_is_string_enum(self):
        assert isinstance(CircuitState.CLOSED, str)


class TestCircuitBreakerError:
    def test_circuit_breaker_error_inheritance(self):
        assert issubclass(CircuitBreakerError, Exception)

    def test_circuit_open_error_inheritance(self):
        assert issubclass(CircuitOpenError, CircuitBreakerError)


class TestCircuitBreakerConfig:
    def test_default_config(self):
        config = CircuitBreakerConfig()
        assert config.failure_threshold == 5
        assert config.success_threshold == 2
        assert config.timeout == 60.0
        assert config.half_open_max_calls == 3

    def test_custom_config(self):
        config = CircuitBreakerConfig(
            failure_threshold=10,
            success_threshold=3,
            timeout=30.0
        )
        assert config.failure_threshold == 10
        assert config.success_threshold == 3
        assert config.timeout == 30.0

    def test_invalid_timeout_raises(self):
        with pytest.raises(ValueError):
            CircuitBreakerConfig(timeout=0)

    def test_negative_timeout_raises(self):
        with pytest.raises(ValueError):
            CircuitBreakerConfig(timeout=-1)

    def test_excluded_exceptions_default(self):
        config = CircuitBreakerConfig()
        assert config.excluded_exceptions == ()


class TestCircuitBreaker:
    def test_circuit_breaker_initialization(self):
        cb = CircuitBreaker("test")
        assert cb.name == "test"
        assert cb.state == CircuitState.CLOSED

    def test_circuit_breaker_initialization_with_config(self):
        config = CircuitBreakerConfig(failure_threshold=10)
        cb = CircuitBreaker("test", config=config)
        assert cb.config.failure_threshold == 10

    def test_circuit_breaker_initial_state(self):
        cb = CircuitBreaker("test")
        metrics = cb.metrics
        assert metrics.total_calls == 0
        assert metrics.successful_calls == 0
        assert metrics.failed_calls == 0

    @pytest.mark.asyncio
    async def test_successful_call(self):
        cb = CircuitBreaker("test")
        
        async def success_func():
            return "success"
        
        result = await cb.call(success_func)
        assert result == "success"
        assert cb.metrics.successful_calls == 1
        assert cb.metrics.consecutive_successes == 1

    @pytest.mark.asyncio
    async def test_failed_call(self):
        cb = CircuitBreaker("test")
        
        async def fail_func():
            raise ValueError("test error")
        
        with pytest.raises(ValueError):
            await cb.call(fail_func)
        
        assert cb.metrics.failed_calls == 1
        assert cb.metrics.consecutive_failures == 1

    @pytest.mark.asyncio
    async def test_circuit_opens_after_threshold(self):
        config = CircuitBreakerConfig(failure_threshold=3)
        cb = CircuitBreaker("test", config=config)
        
        async def fail_func():
            raise ValueError("test error")
        
        for _ in range(3):
            try:
                await cb.call(fail_func)
            except ValueError:
                pass
        
        assert cb.state == CircuitState.OPEN
        assert cb.metrics.consecutive_failures == 3

    @pytest.mark.asyncio
    async def test_rejected_call_when_open(self):
        config = CircuitBreakerConfig(failure_threshold=1, timeout=60.0)
        cb = CircuitBreaker("test", config=config)
        
        async def fail_func():
            raise ValueError("test error")
        
        try:
            await cb.call(fail_func)
        except ValueError:
            pass
        
        assert cb.state == CircuitState.OPEN
        
        async def success_func():
            return "success"
        
        with pytest.raises(CircuitOpenError):
            await cb.call(success_func)
        
        assert cb.metrics.rejected_calls == 1

    @pytest.mark.asyncio
    async def test_circuit_half_open_after_timeout(self):
        config = CircuitBreakerConfig(failure_threshold=1, timeout=0.1)
        cb = CircuitBreaker("test", config=config)
        
        async def fail_func():
            raise ValueError("test error")
        
        try:
            await cb.call(fail_func)
        except ValueError:
            pass
        
        assert cb.state == CircuitState.OPEN
        
        await asyncio.sleep(0.2)
        assert cb.state == CircuitState.HALF_OPEN

    @pytest.mark.asyncio
    async def test_circuit_closes_after_success_threshold(self):
        config = CircuitBreakerConfig(failure_threshold=1, success_threshold=2, timeout=0.1)
        cb = CircuitBreaker("test", config=config)
        
        async def fail_func():
            raise ValueError("test error")
        
        try:
            await cb.call(fail_func)
        except ValueError:
            pass
        
        await asyncio.sleep(0.2)
        assert cb.state == CircuitState.HALF_OPEN
        
        async def success_func():
            return "success"
        
        await cb.call(success_func)
        assert cb.state == CircuitState.HALF_OPEN
        
        await cb.call(success_func)
        assert cb.state == CircuitState.CLOSED

    @pytest.mark.asyncio
    async def test_circuit_reopens_on_half_open_failure(self):
        config = CircuitBreakerConfig(failure_threshold=1, timeout=0.1)
        cb = CircuitBreaker("test", config=config)
        
        async def fail_func():
            raise ValueError("test error")
        
        try:
            await cb.call(fail_func)
        except ValueError:
            pass
        
        await asyncio.sleep(0.2)
        assert cb.state == CircuitState.HALF_OPEN
        
        try:
            await cb.call(fail_func)
        except ValueError:
            pass
        
        assert cb.state == CircuitState.OPEN

    def test_reset_circuit(self):
        cb = CircuitBreaker("test")
        cb._metrics.total_calls = 100
        cb._state = CircuitState.OPEN
        
        cb.reset()
        
        assert cb.state == CircuitState.CLOSED
        assert cb.metrics.total_calls == 0

    def test_get_info(self):
        cb = CircuitBreaker("test")
        info = cb.get_info()
        
        assert info.name == "test"
        assert info.state == CircuitState.CLOSED
        assert isinstance(info, CircuitInfo)

    @pytest.mark.asyncio
    async def test_call_measures_latency(self):
        cb = CircuitBreaker("test")
        
        async def slow_func():
            await asyncio.sleep(0.05)
            return "done"
        
        await cb.call(slow_func)
        
        metrics = cb.metrics
        assert metrics.total_calls == 1

    def test_on_state_change_callback(self):
        callback_called = []
        
        def on_change(name, old, new):
            callback_called.append((name, old, new))
        
        cb = CircuitBreaker("test", on_state_change=on_change)
        cb._transition_to(CircuitState.HALF_OPEN)
        
        assert len(callback_called) == 1
        assert callback_called[0] == ("test", CircuitState.CLOSED, CircuitState.HALF_OPEN)

    @pytest.mark.asyncio
    async def test_excluded_exceptions_do_not_count(self):
        config = CircuitBreakerConfig(failure_threshold=3, excluded_exceptions=(ValueError,))
        cb = CircuitBreaker("test", config=config)
        
        async def excluded_error():
            raise ValueError("excluded")
        
        for _ in range(5):
            try:
                await cb.call(excluded_error)
            except ValueError:
                pass
        
        assert cb.state == CircuitState.CLOSED


class TestCircuitBreakerRegistry:
    def test_registry_is_singleton(self):
        reg1 = CircuitBreakerRegistry()
        reg2 = CircuitBreakerRegistry()
        assert reg1 is reg2

    def test_register_circuit(self):
        reg = CircuitBreakerRegistry()
        cb = reg.register("test")
        assert cb.name == "test"

    def test_register_with_config(self):
        reg = CircuitBreakerRegistry()
        config = CircuitBreakerConfig(failure_threshold=10)
        cb = reg.register("test_with_config", config=config)
        assert cb.config.failure_threshold == 10

    def test_get_registered_circuit(self):
        reg = CircuitBreakerRegistry()
        reg.register("test")
        cb = reg.get("test")
        assert cb is not None
        assert cb.name == "test"

    def test_get_unregistered_circuit(self):
        reg = CircuitBreakerRegistry()
        cb = reg.get("nonexistent")
        assert cb is None

    def test_get_all_circuits(self):
        reg = CircuitBreakerRegistry()
        reg.register("test1")
        reg.register("test2")
        
        all_circuits = reg.get_all()
        assert len(all_circuits) >= 2
        assert "test1" in all_circuits
        assert "test2" in all_circuits

    def test_reset_all_circuits(self):
        reg = CircuitBreakerRegistry()
        cb1 = reg.register("test1")
        cb2 = reg.register("test2")
        
        cb1._state = CircuitState.OPEN
        cb2._state = CircuitState.OPEN
        
        reg.reset_all()
        
        assert cb1.state == CircuitState.CLOSED
        assert cb2.state == CircuitState.CLOSED


class TestFallbackHandler:
    def test_fallback_handler_creation(self):
        handler = FallbackHandler()
        assert handler._fallbacks == {}

    def test_register_fallback(self):
        handler = FallbackHandler()
        fallback = Mock(return_value="fallback_result")
        handler.register("test", fallback)
        assert handler.get_fallback("test") == fallback

    def test_get_unregistered_fallback(self):
        handler = FallbackHandler()
        assert handler.get_fallback("nonexistent") is None


class TestCircuitInfo:
    def test_circuit_info_creation(self):
        info = CircuitInfo(
            name="test",
            state=CircuitState.CLOSED,
            metrics=CircuitMetrics(),
            config=CircuitBreakerConfig()
        )
        assert info.name == "test"
        assert info.state == CircuitState.CLOSED


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
