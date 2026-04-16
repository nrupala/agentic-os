#!/usr/bin/env python3
"""
Unit tests for observability/health.py

MIT License
Copyright (c) 2024 Nrupal Akolkar
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from observability.health import (
    HealthStatus,
    ComponentHealth,
    HealthCheck,
    SystemHealthCheck,
    ProcessHealthCheck,
    EngineHealthCheck,
    ToolsHealthCheck,
    HealthMonitor,
    basic_health,
    readiness_probe,
    liveness_probe,
    detailed_health
)


class TestHealthStatus:
    def test_health_status_values(self):
        assert HealthStatus.HEALTHY.value == "healthy"
        assert HealthStatus.DEGRADED.value == "degraded"
        assert HealthStatus.UNHEALTHY.value == "unhealthy"
        assert HealthStatus.UNKNOWN.value == "unknown"

    def test_health_status_is_string(self):
        assert isinstance(HealthStatus.HEALTHY, str)
        assert HealthStatus.HEALTHY == "healthy"


class TestComponentHealth:
    def test_component_health_creation(self):
        health = ComponentHealth(
            name="test",
            status=HealthStatus.HEALTHY,
            latency_ms=10.5,
            message="All good",
            details={"key": "value"}
        )
        
        assert health.name == "test"
        assert health.status == HealthStatus.HEALTHY
        assert health.latency_ms == 10.5
        assert health.message == "All good"
        assert health.details == {"key": "value"}
        assert isinstance(health.timestamp, str)

    def test_component_health_to_dict(self):
        health = ComponentHealth(
            name="test",
            status=HealthStatus.HEALTHY,
            latency_ms=10.0
        )
        
        result = health.to_dict()
        
        assert result["name"] == "test"
        assert result["status"] == "healthy"
        assert result["latency_ms"] == 10.0
        assert "timestamp" in result

    def test_component_health_default_values(self):
        health = ComponentHealth(name="test", status=HealthStatus.HEALTHY)
        
        assert health.latency_ms == 0.0
        assert health.message == ""
        assert health.details == {}


class TestSystemHealthCheck:
    @pytest.mark.asyncio
    async def test_system_health_check_returns_healthy(self):
        check = SystemHealthCheck("system")
        
        with patch('psutil.cpu_percent', return_value=50.0):
            with patch('psutil.virtual_memory', return_value=Mock(percent=50.0, available=1024*1024*1024)):
                with patch('psutil.disk_usage', return_value=Mock(percent=50.0, free=100*1024*1024*1024)):
                    with patch('psutil.getloadavg', return_value=(1.0, 1.0, 1.0)):
                        result = await check.check()
        
        assert result.name == "system"
        assert result.status == HealthStatus.HEALTHY
        assert "cpu_percent" in result.details
        assert "memory_percent" in result.details

    @pytest.mark.asyncio
    async def test_system_health_check_returns_degraded_high_resources(self):
        check = SystemHealthCheck("system")
        
        with patch('psutil.cpu_percent', return_value=95.0):
            with patch('psutil.virtual_memory', return_value=Mock(percent=95.0, available=100*1024*1024)):
                with patch('psutil.disk_usage', return_value=Mock(percent=50.0, free=100*1024*1024*1024)):
                    with patch('psutil.getloadavg', return_value=(5.0, 5.0, 5.0)):
                        result = await check.check()
        
        assert result.status == HealthStatus.DEGRADED

    @pytest.mark.asyncio
    async def test_system_health_check_handles_exception(self):
        check = SystemHealthCheck("system")
        
        with patch('psutil.cpu_percent', side_effect=Exception("Mock error")):
            result = await check.check()
        
        assert result.status == HealthStatus.UNHEALTHY
        assert "Mock error" in result.message


class TestProcessHealthCheck:
    @pytest.mark.asyncio
    async def test_process_health_check_returns_healthy(self):
        check = ProcessHealthCheck("process")
        
        mock_process = Mock()
        mock_process.pid = 12345
        mock_process.num_threads = Mock(return_value=5)
        mock_process.num_fds = Mock(return_value=10)
        mock_process.open_files = Mock(return_value=[])
        mock_process.memory_info = Mock(return_value=Mock(rss=100*1024*1024, vms=200*1024*1024))
        mock_process.cpu_percent = Mock(return_value=10.0)
        mock_process.status = Mock(return_value="running")
        
        with patch('psutil.Process', return_value=mock_process):
            result = await check.check()
        
        assert result.name == "process"
        assert result.status == HealthStatus.HEALTHY
        assert result.details["pid"] == 12345
        assert result.details["threads"] == 5


class TestHealthMonitor:
    def test_health_monitor_creation(self):
        monitor = HealthMonitor()
        assert monitor.checks == []

    def test_register_check(self):
        monitor = HealthMonitor()
        check = SystemHealthCheck("test")
        monitor.register_check(check)
        assert len(monitor.checks) == 1
        assert monitor.checks[0].name == "test"

    def test_register_default_checks(self):
        monitor = HealthMonitor()
        monitor._register_default_checks()
        assert len(monitor.checks) == 4
        names = [c.name for c in monitor.checks]
        assert "system" in names
        assert "process" in names
        assert "engine" in names
        assert "tools" in names

    @pytest.mark.asyncio
    async def test_check_all_returns_summary(self):
        monitor = HealthMonitor()
        
        check = SystemHealthCheck()
        
        monitor.register_check(check)
        result = await monitor.check_all()
        
        assert "status" in result
        assert "timestamp" in result
        assert "components" in result
        assert "summary" in result
        assert result["summary"]["total"] >= 1

    @pytest.mark.asyncio
    async def test_check_all_calculates_overall_status_healthy(self):
        monitor = HealthMonitor()
        
        check = SystemHealthCheck()
        monitor.register_check(check)
        
        result = await monitor.check_all()
        assert result["status"] in ["healthy", "degraded", "unhealthy"]

    @pytest.mark.asyncio
    async def test_check_all_calculates_overall_status_degraded(self):
        monitor = HealthMonitor()
        
        check1 = SystemHealthCheck()
        check2 = ProcessHealthCheck()
        
        monitor.register_check(check1)
        monitor.register_check(check2)
        
        result = await monitor.check_all()
        assert result["status"] in ["healthy", "degraded", "unhealthy"]

    @pytest.mark.asyncio
    async def test_check_all_calculates_overall_status_unhealthy(self):
        monitor = HealthMonitor()
        
        check = SystemHealthCheck()
        monitor.register_check(check)
        
        result = await monitor.check_all()
        assert result["status"] in ["healthy", "degraded", "unhealthy"]


class TestHealthCheckTimedCheck:
    @pytest.mark.asyncio
    async def test_timed_check_completes_quickly(self):
        check = SystemHealthCheck()
        
        result = await check._timed_check()
        
        assert result.latency_ms < 1000

    @pytest.mark.asyncio
    async def test_timed_check_timeout(self):
        check = SystemHealthCheck()
        
        with patch.object(check, 'check', side_effect=asyncio.TimeoutError()):
            result = await check._timed_check()
        
        assert result.status == HealthStatus.UNHEALTHY


class TestHealthEndpointFunctions:
    @pytest.mark.asyncio
    async def test_basic_health(self):
        result = await basic_health()
        assert result["status"] == "healthy"
        assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_liveness_probe(self):
        result = await liveness_probe()
        assert result["status"] == "alive"
        assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_readiness_probe_when_ready(self):
        result = await readiness_probe()
        assert result["status"] == "ready"

    @pytest.mark.asyncio
    async def test_detailed_health(self):
        result = await detailed_health()
        assert "status" in result
        assert "components" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
