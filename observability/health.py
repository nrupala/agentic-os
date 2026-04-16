#!/usr/bin/env python3
"""
agentic-OS Health Checks
========================
Comprehensive health monitoring for all system components

Provides:
- /health - Basic health check
- /health/ready - Readiness probe
- /health/live - Liveness probe
- /health/detailed - Detailed component status

MIT License
Copyright (c) 2024 Nrupal Akolkar
"""

import asyncio
import time
import psutil
import platform
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum
from abc import ABC, abstractmethod
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ComponentHealth:
    name: str
    status: HealthStatus
    latency_ms: float = 0.0
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status.value,
            "latency_ms": round(self.latency_ms, 2),
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp
        }


class HealthCheck(ABC):
    def __init__(self, name: str, timeout: float = 5.0):
        self.name = name
        self.timeout = timeout
    
    @abstractmethod
    async def check(self) -> ComponentHealth:
        pass
    
    async def _timed_check(self) -> ComponentHealth:
        start = time.perf_counter()
        try:
            result = await asyncio.wait_for(self.check(), timeout=self.timeout)
            result.latency_ms = (time.perf_counter() - start) * 1000
            return result
        except asyncio.TimeoutError:
            return ComponentHealth(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                latency_ms=(time.perf_counter() - start) * 1000,
                message=f"Health check timed out after {self.timeout}s"
            )
        except Exception as e:
            return ComponentHealth(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                latency_ms=(time.perf_counter() - start) * 1000,
                message=f"Health check failed: {str(e)}"
            )


class SystemHealthCheck(HealthCheck):
    def __init__(self, name: str = "system", timeout: float = 5.0):
        super().__init__(name, timeout)
    
    async def check(self) -> ComponentHealth:
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            load_avg = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else (0, 0, 0)
            
            status = HealthStatus.HEALTHY
            if cpu_percent > 90 or memory.percent > 90:
                status = HealthStatus.DEGRADED
            
            return ComponentHealth(
                name="system",
                status=status,
                message="System resources OK",
                details={
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "memory_available_mb": memory.available / (1024 * 1024),
                    "disk_percent": disk.percent,
                    "disk_free_gb": disk.free / (1024 * 1024 * 1024),
                    "load_average": load_avg,
                    "platform": platform.system(),
                    "platform_release": platform.release()
                }
            )
        except Exception as e:
            return ComponentHealth(
                name="system",
                status=HealthStatus.UNHEALTHY,
                message=f"Failed to check system: {str(e)}"
            )


class ProcessHealthCheck(HealthCheck):
    def __init__(self, name: str = "process", timeout: float = 5.0):
        super().__init__(name, timeout)
    
    async def check(self) -> ComponentHealth:
        try:
            process = psutil.Process()
            threads = process.num_threads()
            fds = process.num_fds() if hasattr(process, 'num_fds') else 0
            memory_info = process.memory_info()
            
            open_files = len(process.open_files()) if hasattr(process, 'open_files') else 0
            
            return ComponentHealth(
                name="process",
                status=HealthStatus.HEALTHY,
                message="Process running normally",
                details={
                    "pid": process.pid,
                    "threads": threads,
                    "open_files": open_files,
                    "memory_rss_mb": memory_info.rss / (1024 * 1024),
                    "memory_vms_mb": memory_info.vms / (1024 * 1024),
                    "cpu_percent": process.cpu_percent(interval=0.1),
                    "status": process.status()
                }
            )
        except Exception as e:
            return ComponentHealth(
                name="process",
                status=HealthStatus.UNHEALTHY,
                message=f"Process check failed: {str(e)}"
            )


class EngineHealthCheck(HealthCheck):
    def __init__(self, name: str = "engine", timeout: float = 5.0):
        super().__init__(name, timeout)
    
    async def check(self) -> ComponentHealth:
        try:
            from engine.bridge import PlanToOmegaBridge
            bridge = PlanToOmegaBridge()
            
            return ComponentHealth(
                name="engine",
                status=HealthStatus.HEALTHY,
                message="OMEGA engine ready",
                details={
                    "engine_version": "1.0.0",
                    "components": ["planner", "omega_stack", "executor", "guardian"],
                    "features": {
                        "parallel_execution": False,
                        "checkpointing": False,
                        "circuit_breaker": False
                    }
                }
            )
        except ImportError as e:
            return ComponentHealth(
                name="engine",
                status=HealthStatus.DEGRADED,
                message=f"Engine partially available: {str(e)}"
            )
        except Exception as e:
            return ComponentHealth(
                name="engine",
                status=HealthStatus.UNHEALTHY,
                message=f"Engine check failed: {str(e)}"
            )


class MemoryHealthCheck(HealthCheck):
    def __init__(self, name: str = "memory", timeout: float = 5.0):
        super().__init__(name, timeout)
    
    async def check(self) -> ComponentHealth:
        try:
            from engine.cognitive_memory import CognitiveMemory
            
            mem = CognitiveMemory()
            stats = mem.get_stats()
            
            return ComponentHealth(
                name="memory",
                status=HealthStatus.HEALTHY,
                message="Memory subsystem operational",
                details={
                    "working_memory_items": stats.get("working_memory_size", 0),
                    "long_term_memory_items": stats.get("long_term_memory_size", 0),
                    "knowledge_graph_nodes": stats.get("knowledge_graph_size", 0)
                }
            )
        except ImportError:
            return ComponentHealth(
                name="memory",
                status=HealthStatus.DEGRADED,
                message="Memory subsystem not available (using fallback)"
            )
        except Exception as e:
            return ComponentHealth(
                name="memory",
                status=HealthStatus.UNHEALTHY,
                message=f"Memory check failed: {str(e)}"
            )


class ToolsHealthCheck(HealthCheck):
    def __init__(self, name: str = "tools", timeout: float = 5.0):
        super().__init__(name, timeout)
    
    async def check(self) -> ComponentHealth:
        try:
            tools_status = {}
            available_tools = 0
            total_tools = 0
            
            tool_modules = [
                ("file_ops", "tools.file_ops"),
                ("git_ops", "tools.git_ops"),
                ("docker_ops", "tools.docker_ops"),
                ("security_scanner", "tools.security_scanner"),
                ("test_generator", "tools.test_generator")
            ]
            
            for tool_name, module_path in tool_modules:
                total_tools += 1
                try:
                    __import__(module_path)
                    tools_status[tool_name] = "available"
                    available_tools += 1
                except ImportError:
                    tools_status[tool_name] = "unavailable"
            
            status = HealthStatus.HEALTHY
            if available_tools < total_tools / 2:
                status = HealthStatus.DEGRADED
            
            return ComponentHealth(
                name="tools",
                status=status,
                message=f"{available_tools}/{total_tools} tools available",
                details={
                    "available": available_tools,
                    "total": total_tools,
                    "tools": tools_status
                }
            )
        except Exception as e:
            return ComponentHealth(
                name="tools",
                status=HealthStatus.UNHEALTHY,
                message=f"Tools check failed: {str(e)}"
            )


class HealthMonitor:
    def __init__(self):
        self.checks: List[HealthCheck] = []
        self._last_check: Optional[Dict[str, ComponentHealth]] = None
        self._last_check_time: Optional[float] = None
        
    def register_check(self, check: HealthCheck):
        self.checks.append(check)
    
    async def check_all(self, detailed: bool = False) -> Dict[str, Any]:
        if not self.checks:
            self._register_default_checks()
        
        results = {}
        for check in self.checks:
            result = await check._timed_check()
            results[check.name] = result.to_dict()
        
        self._last_check = {k: ComponentHealth(**v) for k, v in results.items()}
        self._last_check_time = time.time()
        
        overall_status = self._calculate_overall_status(results)
        
        response = {
            "status": overall_status.value,
            "timestamp": datetime.utcnow().isoformat(),
            "components": results,
            "summary": {
                "total": len(results),
                "healthy": sum(1 for r in results.values() if r["status"] == HealthStatus.HEALTHY.value),
                "degraded": sum(1 for r in results.values() if r["status"] == HealthStatus.DEGRADED.value),
                "unhealthy": sum(1 for r in results.values() if r["status"] == HealthStatus.UNHEALTHY.value)
            }
        }
        
        return response
    
    def _register_default_checks(self):
        self.register_check(SystemHealthCheck("system"))
        self.register_check(ProcessHealthCheck("process"))
        self.register_check(EngineHealthCheck("engine"))
        self.register_check(ToolsHealthCheck("tools"))
    
    def _calculate_overall_status(self, results: Dict[str, Dict[str, Any]]) -> HealthStatus:
        statuses = [r["status"] for r in results.values()]
        
        if any(s == HealthStatus.UNHEALTHY.value for s in statuses):
            return HealthStatus.UNHEALTHY
        if any(s == HealthStatus.DEGRADED.value for s in statuses):
            return HealthStatus.DEGRADED
        if any(s == HealthStatus.UNKNOWN.value for s in statuses):
            return HealthStatus.UNKNOWN
        return HealthStatus.HEALTHY


health_monitor = HealthMonitor()


async def basic_health() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


async def readiness_probe() -> Dict[str, Any]:
    result = await health_monitor.check_all(detailed=False)
    
    critical_checks = ["system", "process", "engine"]
    for check in critical_checks:
        if check in result["components"]:
            if result["components"][check]["status"] == HealthStatus.UNHEALTHY.value:
                return {
                    "status": "not_ready",
                    "reason": f"Critical check '{check}' is unhealthy",
                    "timestamp": result["timestamp"]
                }
    
    return {
        "status": "ready",
        "timestamp": result["timestamp"]
    }


async def liveness_probe() -> Dict[str, Any]:
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat()
    }


async def detailed_health() -> Dict[str, Any]:
    return await health_monitor.check_all(detailed=True)


def create_health_routes(app):
    from fastapi import APIRouter
    
    router = APIRouter(prefix="/health", tags=["health"])
    
    @router.get("")
    async def health():
        return await basic_health()
    
    @router.get("/ready")
    async def ready():
        return await readiness_probe()
    
    @router.get("/live")
    async def live():
        return await liveness_probe()
    
    @router.get("/detailed")
    async def detailed():
        return await detailed_health()
    
    app.include_router(router)
    return router


if __name__ == "__main__":
    import asyncio
    
    async def main():
        print("=" * 60)
        print("agentic-OS Health Check System")
        print("=" * 60)
        
        monitor = HealthMonitor()
        monitor.register_check(SystemHealthCheck("system"))
        monitor.register_check(ProcessHealthCheck("process"))
        monitor.register_check(EngineHealthCheck("engine"))
        monitor.register_check(MemoryHealthCheck("memory"))
        monitor.register_check(ToolsHealthCheck("tools"))
        
        print("\nRunning health checks...\n")
        result = await monitor.check_all(detailed=True)
        
        print(f"Overall Status: {result['status'].upper()}")
        print(f"Timestamp: {result['timestamp']}")
        print(f"\nSummary: {result['summary']['healthy']} healthy, "
              f"{result['summary']['degraded']} degraded, "
              f"{result['summary']['unhealthy']} unhealthy\n")
        
        print("Component Details:")
        print("-" * 60)
        for name, health in result["components"].items():
            status_icon = {
                "healthy": "✓",
                "degraded": "⚠",
                "unhealthy": "✗",
                "unknown": "?"
            }.get(health["status"], "?")
            
            print(f"{status_icon} {name.upper():15} {health['status']:10} "
                  f"({health['latency_ms']:.1f}ms) - {health['message']}")
        
        print("=" * 60)
    
    asyncio.run(main())
