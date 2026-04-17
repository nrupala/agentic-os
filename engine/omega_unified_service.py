#!/usr/bin/env python3
"""
OMEGA Unified Service
=====================
Integrates all OMEGA components into a unified recursive persistent service.

Components:
- OMEGA Daemon: Persistent service with resource management
- Gödel Machine: Self-referential code modification
- Reproducible Builds: Build verification and provenance
- Meta-Learner: Recursive meta-learning for strategy optimization
- Omega Forge: Core code generation
- Omega Integrator: System integration hub

This is the main entry point for the enhanced OMEGA engine.
"""

import os
import sys
import json
import time
import threading
import signal
from pathlib import Path
from typing import Dict, Optional, Any, List
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

logging.basicConfig(
    level=logging.INFO,
    format='[OMEGA] %(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent
ENGINE_DIR = PROJECT_ROOT / "engine"

sys.path.insert(0, str(ENGINE_DIR))

try:
    from omega_phase_encryptor import OmegaPhaseEncryptor
    _ENCRYPTOR = OmegaPhaseEncryptor("unified_service")
    HAS_ZK = True
except ImportError:
    _ENCRYPTOR = None
    HAS_ZK = False

@dataclass
class OmegaServiceConfig:
    project: str = "omega"
    port: int = 8765
    daemon_mode: bool = True
    auto_repair: bool = True
    self_modification: bool = True
    reproducible_builds: bool = True
    meta_learning: bool = True
    max_memory_mb: int = 2048
    max_cpu_percent: int = 80
    max_concurrent_tasks: int = 4

@dataclass
class ServiceStatus:
    started_at: str
    status: str
    components: Dict[str, str]
    metrics: Dict[str, Any]
    version: str = "2.0.0"

class OmegaUnifiedService:
    """
    OMEGA Unified Service
    ====================
    Integrates all OMEGA components into a single cohesive service.
    
    Features:
    - Persistent daemon with crash recovery
    - Self-referential code modification (Gödel Machine)
    - Reproducible build verification
    - Meta-learning strategy optimization
    - Resource management and auto-scaling
    """
    
    VERSION = "2.0.0"
    
    def __init__(self, config: OmegaServiceConfig = None):
        self.config = config or OmegaServiceConfig()
        
        self.status = ServiceStatus(
            started_at=datetime.now().isoformat(),
            status="initializing",
            components={},
            metrics={},
            version=self.VERSION
        )
        
        self.running = False
        
        self.daemon = None
        self.godel_machine = None
        self.reproducible_builds = None
        self.meta_learner = None
        self.forge = None
        
        self._init_components()
        
        logger.info(f"OMEGA Unified Service v{self.VERSION} initialized")
    
    def _init_components(self):
        """Initialize all OMEGA components."""
        
        if self.config.daemon_mode:
            try:
                from omega_daemon import OmegaDaemon
                self.daemon = OmegaDaemon(self.config.project, self.config.port)
                self.status.components["daemon"] = "active"
                logger.info("  [OK] Daemon Service")
            except Exception as e:
                self.status.components["daemon"] = f"error: {e}"
                logger.warning(f"  [!] Daemon Service: {e}")
        
        if self.config.self_modification:
            try:
                from omega_godel_machine import GödelMachine
                self.godel_machine = GödelMachine(self.config.project)
                self.status.components["godel_machine"] = "active"
                logger.info("  [OK] Gödel Machine")
            except Exception as e:
                self.status.components["godel_machine"] = f"error: {e}"
                logger.warning(f"  [!] Gödel Machine: {e}")
        
        if self.config.reproducible_builds:
            try:
                from omega_reproducible_builds import ReproducibleBuilds
                self.reproducible_builds = ReproducibleBuilds(self.config.project)
                self.status.components["reproducible_builds"] = "active"
                logger.info("  [OK] Reproducible Builds")
            except Exception as e:
                self.status.components["reproducible_builds"] = f"error: {e}"
                logger.warning(f"  [!] Reproducible Builds: {e}")
        
        if self.config.meta_learning:
            try:
                from omega_meta_learner import RecursiveMetaLearner
                self.meta_learner = RecursiveMetaLearner(self.config.project)
                self.status.components["meta_learner"] = "active"
                logger.info("  [OK] Meta-Learner")
            except Exception as e:
                self.status.components["meta_learner"] = f"error: {e}"
                logger.warning(f"  [!] Meta-Learner: {e}")
        
        try:
            from omega_forge import OmegaForge
            self.forge = OmegaForge(self.config.project)
            self.status.components["forge"] = "active"
            logger.info("  [OK] Omega Forge")
        except Exception as e:
            self.status.components["forge"] = f"error: {e}"
            logger.warning(f"  [!] Omega Forge: {e}")
        
        self.status.status = "ready"
        logger.info("All components initialized")
    
    def start(self):
        """Start the unified service."""
        logger.info(f"Starting OMEGA Unified Service v{self.VERSION}...")
        
        self.running = True
        self.status.status = "running"
        
        signal.signal(signal.SIGINT, self._handle_shutdown)
        signal.signal(signal.SIGTERM, self._handle_shutdown)
        
        if self.reproducible_builds:
            try:
                self.reproducible_builds.create_manifest()
            except Exception as e:
                logger.warning(f"Could not create initial manifest: {e}")
        
        main_thread = threading.Thread(target=self._main_loop, daemon=True)
        main_thread.start()
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            self._shutdown()
    
    def _main_loop(self):
        """Main service loop."""
        loop_count = 0
        
        while self.running:
            try:
                loop_count += 1
                
                if loop_count % 60 == 0:
                    self._periodic_maintenance()
                
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Main loop error: {e}")
                time.sleep(5)
    
    def _periodic_maintenance(self):
        """Periodic maintenance tasks."""
        
        if self.godel_machine:
            changes = self.godel_machine.get_applicable_changes()
            if changes:
                logger.info(f"Found {len(changes)} applicable self-modifications")
        
        if self.reproducible_builds:
            result = self.reproducible_builds.verify_against_manifest()
            self.status.metrics["reproducibility"] = result.get("reproducibility_score", 0)
        
        if self.meta_learner:
            trends = self.meta_learner.analyze_performance_trends()
            self.status.metrics["performance_trend"] = trends.get("trend", "unknown")
        
        self._update_metrics()
        
        logger.info(f"Metrics: {self.status.metrics}")
    
    def _update_metrics(self):
        """Update service metrics."""
        
        self.status.metrics["uptime_seconds"] = (
            datetime.now() - datetime.fromisoformat(self.status.started_at)
        ).total_seconds()
        
        self.status.metrics["component_count"] = len(self.status.components)
        
        active = sum(1 for v in self.status.components.values() if v == "active")
        self.status.metrics["active_components"] = active
    
    def _handle_shutdown(self, signum, frame):
        """Handle graceful shutdown."""
        logger.info("Shutdown signal received")
        self.running = False
    
    def _shutdown(self):
        """Graceful shutdown."""
        logger.info("Shutting down OMEGA Unified Service...")
        self.status.status = "stopped"
        
        if self.reproducible_builds:
            try:
                self.reproducible_builds.create_signed_manifest()
            except Exception as e:
                logger.warning(f"Could not create signed manifest: {e}")
        
        logger.info("OMEGA Unified Service stopped")
    
    def execute_goal(self, goal: str, context: Dict = None) -> Dict:
        """Execute a coding goal using all available components."""
        
        logger.info(f"Executing goal: {goal[:50]}...")
        
        context = context or {}
        start_time = time.time()
        
        if self.meta_learner:
            result = self.meta_learner.execute_with_meta_learning(goal)
            
            if result.get("success"):
                return {
                    "success": True,
                    "result": result,
                    "execution_time": time.time() - start_time,
                    "components_used": ["meta_learner"]
                }
        
        if self.forge:
            result = self.forge.execute_goal(goal)
            
            if result.get("success"):
                return {
                    "success": True,
                    "result": result,
                    "execution_time": time.time() - start_time,
                    "components_used": ["forge"]
                }
        
        return {
            "success": False,
            "error": "All components failed",
            "execution_time": time.time() - start_time
        }
    
    def submit_task(self, goal: str, metadata: Dict = None) -> str:
        """Submit a task to the daemon queue."""
        
        if self.daemon:
            return self.daemon.submit_task(goal, metadata)
        
        task_id = f"task_{int(time.time())}_{hashlib.md5(goal.encode()).hexdigest()[:6]}"
        
        storage_path = Path(f"projects/{self.config.project}/state")
        storage_path.mkdir(parents=True, exist_ok=True)
        
        task_file = storage_path / "task_queue.json"
        tasks = []
        if task_file.exists():
            try:
                data = task_file.read_bytes()
                if HAS_ZK and _ENCRYPTOR and len(data) > 12:
                    tasks = json.loads(_ENCRYPTOR.aesgcm.decrypt(data[:12], data[12:], None).decode())
                else:
                    tasks = json.loads(task_file.read_text())
            except:
                tasks = []
        
        tasks.append({
            "id": task_id,
            "goal": goal,
            "metadata": metadata or {},
            "submitted_at": datetime.now().isoformat()
        })
        
        if HAS_ZK and _ENCRYPTOR:
            try:
                payload = _ENCRYPTOR.encrypt_string(json.dumps(tasks))
                task_file.write_bytes(payload.nonce + payload.ciphertext)
                return task_id
            except Exception:
                pass
        
        task_file.write_text(json.dumps(tasks, indent=2))
        
        return task_id
    
    def self_repair(self, error: str, context: Dict) -> Dict:
        """Attempt self-repair using Gödel Machine."""
        
        if not self.godel_machine:
            return {"success": False, "error": "Gödel Machine not available"}
        
        change = self.godel_machine.analyze_failure_and_propose_fix(error, context)
        
        if change:
            applied = self.godel_machine.apply_change(change.change_id)
            
            if applied:
                self.godel_machine.learn_from_result(change.change_id, True)
                return {
                    "success": True,
                    "change_id": change.change_id,
                    "action": "self_modified"
                }
        
        return {"success": False, "error": "Could not generate repair"}
    
    def verify_build(self) -> Dict:
        """Verify build reproducibility."""
        
        if not self.reproducible_builds:
            return {"verified": False, "error": "Reproducible builds not available"}
        
        return self.reproducible_builds.verify_against_manifest()
    
    def get_status(self) -> Dict:
        """Get service status."""
        
        status_dict = asdict(self.status)
        
        if self.godel_machine:
            status_dict["godel_stats"] = self.godel_machine.get_statistics()
        
        if self.meta_learner:
            status_dict["meta_stats"] = self.meta_learner.get_statistics()
        
        if self.reproducible_builds:
            status_dict["repro_stats"] = self.reproducible_builds.get_statistics()
        
        return status_dict
    
    def get_optimal_strategy(self) -> Dict:
        """Get optimal strategy from meta-learner."""
        
        if self.meta_learner:
            return self.meta_learner.get_optimal_parameters()
        
        return {"error": "Meta-learner not available"}


import hashlib

_service_instance = None

def get_service(config: OmegaServiceConfig = None) -> OmegaUnifiedService:
    """Get or create service instance."""
    global _service_instance
    
    if _service_instance is None:
        _service_instance = OmegaUnifiedService(config)
    
    return _service_instance


def start_service(project: str = "omega", port: int = 8765):
    """Start the unified service."""
    config = OmegaServiceConfig(project=project, port=port)
    service = OmegaUnifiedService(config)
    service.start()


def execute_goal(goal: str, project: str = "omega") -> Dict:
    """Execute a goal through the unified service."""
    config = OmegaServiceConfig(project=project)
    service = OmegaUnifiedService(config)
    return service.execute_goal(goal)


def submit_task(goal: str, project: str = "omega") -> str:
    """Submit task to the unified service."""
    config = OmegaServiceConfig(project=project)
    service = OmegaUnifiedService(config)
    return service.submit_task(goal)


def get_status(project: str = "omega") -> Dict:
    """Get service status."""
    config = OmegaServiceConfig(project=project)
    service = OmegaUnifiedService(config)
    return service.get_status()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="OMEGA Unified Service")
    parser.add_argument("--project", default="omega", help="Project name")
    parser.add_argument("--port", type=int, default=8765, help="Port")
    parser.add_argument("--start", action="store_true", help="Start service")
    parser.add_argument("--execute", type=str, help="Execute goal")
    parser.add_argument("--submit", type=str, help="Submit task")
    parser.add_argument("--status", action="store_true", help="Show status")
    parser.add_argument("--repair", type=str, help="Attempt self-repair")
    parser.add_argument("--verify", action="store_true", help="Verify build")
    parser.add_argument("--strategy", action="store_true", help="Get optimal strategy")
    
    args = parser.parse_args()
    
    config = OmegaServiceConfig(project=args.project, port=args.port)
    service = OmegaUnifiedService(config)
    
    if args.start:
        service.start()
    elif args.execute:
        result = service.execute_goal(args.execute)
        print(json.dumps(result, indent=2))
    elif args.submit:
        task_id = service.submit_task(args.submit)
        print(f"Task ID: {task_id}")
    elif args.status:
        print(json.dumps(service.get_status(), indent=2))
    elif args.repair:
        result = service.self_repair(args.repair, {"file": "engine/omega_forge.py"})
        print(json.dumps(result, indent=2))
    elif args.verify:
        result = service.verify_build()
        print(json.dumps(result, indent=2))
    elif args.strategy:
        result = service.get_optimal_strategy()
        print(json.dumps(result, indent=2))
    else:
        print(f"OMEGA Unified Service v{service.VERSION}")
        print(f"Project: {args.project}")
        print(f"Status: {service.status.status}")
        print(f"Components: {len(service.status.components)}")