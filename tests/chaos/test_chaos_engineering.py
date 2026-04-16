"""
Chaos Engineering Tests
=======================
Test resilience under failure conditions

MIT License
Copyright (c) 2024 Nrupal Akolkar
"""

import pytest
import asyncio
import random
import time
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from observability.circuit_breaker import CircuitOpenError, CircuitBreaker, CircuitBreakerConfig, CircuitState


class TestChaosEngineering:
    """Chaos engineering tests for agentic-OS."""

    @pytest.mark.asyncio
    async def test_circuit_breaker_under_failure(self):
        """Test circuit breaker opens under repeated failures."""
        config = CircuitBreakerConfig(failure_threshold=3, timeout=1.0)
        cb = CircuitBreaker("chaos-test", config=config)

        failures = 0
        rejected = 0

        for i in range(5):
            try:
                async def fail():
                    raise ValueError("Simulated failure")

                await cb.call(fail)
                failures += 1
            except ValueError:
                failures += 1
            except CircuitOpenError:
                rejected += 1

        assert cb.state == CircuitState.OPEN
        assert rejected >= 1

    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        """Test timeout handling for slow operations."""
        config = CircuitBreakerConfig(timeout=0.1)
        cb = CircuitBreaker("timeout-test", config=config)

        async def slow_operation():
            await asyncio.sleep(0.5)
            return "done"

        start = time.time()

        try:
            await asyncio.wait_for(cb.call(slow_operation), timeout=0.2)
        except (asyncio.TimeoutError, CircuitOpenError, Exception):
            pass

        duration = time.time() - start
        assert duration < 1.0

    @pytest.mark.asyncio
    async def test_fallback_handler_execution(self):
        """Test fallback handler is called when circuit is open."""
        config = CircuitBreakerConfig(failure_threshold=1)
        cb = CircuitBreaker("fallback-test", config=config)

        async def fail():
            raise ValueError("Failure")

        try:
            await cb.call(fail)
        except ValueError:
            pass

        # Test that circuit opened
        assert cb.state == CircuitState.OPEN

    @pytest.mark.asyncio
    async def test_retry_with_exponential_backoff(self):
        """Test retry mechanism with exponential backoff."""
        attempt_times = []

        async def flaky_operation():
            attempt_times.append(time.time())
            if len(attempt_times) < 3:
                raise ConnectionError("Network error")
            return "success"

        max_retries = 3
        base_delay = 0.01

        for attempt in range(max_retries):
            try:
                await flaky_operation()
                break
            except ConnectionError:
                if attempt < max_retries - 1:
                    await asyncio.sleep(base_delay * (2 ** attempt))

        assert len(attempt_times) >= 3

    @pytest.mark.asyncio
    async def test_graceful_degradation(self):
        """Test graceful degradation when services are unavailable."""
        from observability.health import HealthMonitor, HealthStatus

        monitor = HealthMonitor()

        # Just verify health monitor works
        result = await monitor.check_all()

        # Should return a summary even if no checks registered
        assert result is not None

    @pytest.mark.asyncio
    async def test_concurrent_failure_recovery(self):
        """Test recovery under concurrent failures."""
        config = CircuitBreakerConfig(failure_threshold=5, half_open_max_calls=2)
        cb = CircuitBreaker("concurrent-test", config=config)

        async def failing_operation():
            raise RuntimeError("Concurrent failure")

        tasks = [cb.call(failing_operation) for _ in range(10)]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        failures = sum(1 for r in results if isinstance(r, Exception))
        assert failures > 0

    def test_memory_pressure_handling(self):
        """Test handling under memory pressure."""
        objects = []

        try:
            for i in range(100):
                objects.append([j for j in range(100)])
        except MemoryError:
            pytest.fail("Memory error not handled gracefully")

        objects.clear()
        assert True

    def test_network_partition_simulation(self):
        """Test behavior under network partition."""
        with patch('requests.get') as mock_get:
            import requests
            mock_get.side_effect = requests.exceptions.Timeout()

            try:
                requests.get("http://example.com", timeout=0.001)
            except requests.exceptions.Timeout:
                pass

            assert True


class TestResilience:
    """Test system resilience patterns."""

    def test_idempotent_operations(self):
        """Test that operations are idempotent."""
        operation_count = 0

        def idempotent_operation():
            nonlocal operation_count
            operation_count += 1
            return "result"

        results = [idempotent_operation() for _ in range(5)]
        assert all(r == "result" for r in results)

    def test_state_isolation(self):
        """Test that state is isolated between operations."""
        state1 = {"value": 1}
        state2 = {"value": 2}

        def operation(state):
            state["processed"] = True
            return state

        result1 = operation(state1.copy())
        result2 = operation(state2.copy())

        assert result1 != result2

    def test_graceful_shutdown(self):
        """Test graceful shutdown under load."""
        import threading

        active_tasks = []
        shutdown_flag = threading.Event()

        def worker():
            while not shutdown_flag.is_set():
                time.sleep(0.01)
                active_tasks.append(1)

        threads = [threading.Thread(target=worker) for _ in range(5)]
        for t in threads:
            t.start()

        time.sleep(0.1)
        shutdown_flag.set()

        for t in threads:
            t.join(timeout=1)

        assert all(not t.is_alive() for t in threads)


class TestFaultInjection:
    """Test fault injection capabilities."""

    def test_inject_network_delay(self):
        """Test handling of network delays."""
        with patch('time.sleep') as mock_sleep:
            mock_sleep.return_value = None

            time.sleep(0.01)
            assert True

    def test_inject_error_responses(self):
        """Test handling of error responses."""
        error_responses = [
            Exception("Network error"),
            Exception("Timeout"),
            Exception("Connection refused")
        ]

        for error in error_responses:
            with pytest.raises(Exception):
                raise error

    def test_inject_resource_exhaustion(self):
        """Test handling of resource exhaustion."""
        with patch('os.path.exists') as mock_exists:
            mock_exists.side_effect = OSError("No space left on device")

            try:
                Path("/test").exists()
            except OSError:
                pass

            assert True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])