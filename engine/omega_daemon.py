#!/usr/bin/env python3
"""
OMEGA Persistent Daemon Service
===============================
Recursive persistent service that manages its own resources.
Features:
- Daemon mode with graceful shutdown
- Self-managed CPU/memory limits
- Resource monitoring and auto-scaling
- Crash recovery with state restoration
- Heartbeat health checks
"""

import os
import sys
import signal
import time
import json
import hashlib
import threading
import subprocess
import psutil
from pathlib import Path
from typing import Dict, Optional, Any, List
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from enum import Enum
import logging

logging.basicConfig(
    level=logging.INFO,
    format='[OMEGA-DAEMON] %(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent
ENGINE_DIR = PROJECT_ROOT / "engine"

@dataclass
class ResourceLimits:
    max_memory_mb: int = 2048
    max_cpu_percent: int = 80
    max_concurrent_tasks: int = 4
    max_retries: int = 3
    task_timeout_seconds: int = 300

@dataclass
class DaemonState:
    status: str = "starting"
    started_at: str = ""
    last_heartbeat: str = ""
    tasks_completed: int = 0
    tasks_failed: int = 0
    uptime_seconds: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_percent: float = 0.0

class ResourceManager:
    """Self-managed resource controller."""
    
    def __init__(self, limits: ResourceLimits = None):
        self.limits = limits or ResourceLimits()
        self.process = psutil.Process()
        self._task_semaphore = threading.Semaphore(self.limits.max_concurrent_tasks)
    
    def check_resources(self) -> Dict[str, Any]:
        """Check current resource usage."""
        mem_info = self.process.memory_info()
        cpu_percent = self.process.cpu_percent(interval=0.1)
        
        return {
            "memory_mb": mem_info.rss / 1024 / 1024,
            "memory_percent": (mem_info.rss / 1024 / 1024) / self.limits.max_memory_mb * 100,
            "cpu_percent": cpu_percent,
            "available_slots": self.limits.max_concurrent_tasks - self._task_semaphore._value,
            "within_limits": (
                mem_info.rss / 1024 / 1024 < self.limits.max_memory_mb and
                cpu_percent < self.limits.max_cpu_percent
            )
        }
    
    def acquire_task_slot(self, timeout: float = 30.0) -> bool:
        """Acquire a task slot (non-blocking with timeout)."""
        return self._task_semaphore.acquire(timeout=timeout)
    
    def release_task_slot(self):
        """Release a task slot."""
        try:
            self._task_semaphore.release()
        except ValueError:
            pass
    
    def can_accept_task(self) -> bool:
        """Check if daemon can accept new task."""
        resources = self.check_resources()
        return resources["within_limits"] and resources["available_slots"] > 0
    
    def enforce_limits(self):
        """Enforce resource limits via psutil (cross-platform)."""
        try:
            process = psutil.Process()
            max_memory_bytes = self.limits.max_memory_mb * 1024 * 1024
            process.set_memory_limit(max_memory_bytes)
        except AttributeError:
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32 if sys.platform == 'win32' else None
                if kernel32:
                    logger.debug("Windows detected, skipping rlimit")
            except Exception as e:
                logger.debug(f"Could not set memory limit: {e}")
        except Exception as e:
            logger.debug(f"Could not set memory limit: {e}")

class OmegaDaemon:
    """
    OMEGA Persistent Daemon Service
    ==============================
    Runs as background service managing its own resources.
    """
    
    VERSION = "2.0.0"
    HEARTBEAT_INTERVAL = 30
    
    def __init__(self, project: str = "omega", port: int = 8765):
        self.project = project
        self.port = port
        self.state = DaemonState()
        self.running = False
        self.resources = ResourceManager()
        
        self.state_path = Path(f"projects/{project}/state")
        self.state_path.mkdir(parents=True, exist_ok=True)
        
        self._load_checkpoint()
        self._init_signal_handlers()
        
        logger.info(f"OMEGA Daemon v{self.VERSION} initialized for project: {project}")
    
    def _load_checkpoint(self):
        """Load previous state for crash recovery."""
        checkpoint_file = self.state_path / "daemon_checkpoint.json"
        if checkpoint_file.exists():
            try:
                data = json.loads(checkpoint_file.read_text())
                self.state = DaemonState(**data)
                logger.info(f"Recovered from checkpoint: {self.state.status}")
            except Exception as e:
                logger.warning(f"Could not load checkpoint: {e}")
    
    def _save_checkpoint(self):
        """Save current state for crash recovery with optional encryption."""
        checkpoint_file = self.state_path / "daemon_checkpoint.json"
        try:
            from omega_phase_encryptor import OmegaPhaseEncryptor
            enc = OmegaPhaseEncryptor("daemon")
            payload = enc.encrypt_string(json.dumps(asdict(self.state)))
            checkpoint_file.write_bytes(payload.nonce + payload.ciphertext)
            return
        except:
            pass
        checkpoint_file.write_text(json.dumps(asdict(self.state), indent=2))
    
    def _init_signal_handlers(self):
        """Initialize graceful shutdown handlers."""
        signal.signal(signal.SIGINT, self._handle_shutdown)
        signal.signal(signal.SIGTERM, self._handle_shutdown)
    
    def _handle_shutdown(self, signum, frame):
        """Graceful shutdown handler."""
        logger.info("Received shutdown signal, stopping gracefully...")
        self.running = False
    
    def start(self):
        """Start the daemon service."""
        logger.info(f"Starting OMEGA Daemon on port {self.port}...")
        
        self.state.status = "running"
        self.state.started_at = datetime.now().isoformat()
        self.running = True
        
        self.resources.enforce_limits()
        
        main_thread = threading.Thread(target=self._main_loop, daemon=True)
        main_thread.start()
        
        heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        heartbeat_thread.start()
        
        logger.info(f"OMEGA Daemon started successfully")
        logger.info(f"  PID: {os.getpid()}")
        logger.info(f"  Resource limits: {self.resources.limits.max_memory_mb}MB, {self.resources.limits.max_cpu_percent}% CPU")
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            self._shutdown()
    
    def _main_loop(self):
        """Main daemon loop - processes tasks."""
        while self.running:
            try:
                if not self.resources.can_accept_task():
                    time.sleep(5)
                    continue
                
                task = self._fetch_next_task()
                if task:
                    self._execute_task(task)
                
                time.sleep(2)
            except Exception as e:
                logger.error(f"Main loop error: {e}")
                time.sleep(5)
    
    def _heartbeat_loop(self):
        """Heartbeat for health monitoring."""
        while self.running:
            try:
                self.state.last_heartbeat = datetime.now().isoformat()
                
                if self.state.started_at:
                    start = datetime.fromisoformat(self.state.started_at)
                    self.state.uptime_seconds = (datetime.now() - start).total_seconds()
                
                resources = self.resources.check_resources()
                self.state.memory_usage_mb = resources["memory_mb"]
                self.state.cpu_percent = resources["cpu_percent"]
                
                self._save_checkpoint()
                
            except Exception as e:
                logger.error(f"Heartbeat error: {e}")
            
            time.sleep(self.HEARTBEAT_INTERVAL)
    
    def _fetch_next_task(self) -> Optional[Dict]:
        """Fetch next pending task from queue."""
        task_queue = self.state_path / "task_queue.json"
        if not task_queue.exists():
            return None
        
        try:
            tasks = json.loads(task_queue.read_text())
            if tasks:
                task = tasks[0]
                tasks = tasks[1:]
                task_queue.write_text(json.dumps(tasks, indent=2))
                return task
        except Exception as e:
            logger.error(f"Error fetching task: {e}")
        return None
    
    def _execute_task(self, task: Dict):
        """Execute a task with resource management."""
        if not self.resources.acquire_task_slot():
            logger.warning("Could not acquire task slot")
            return
        
        task_id = task.get("id", "unknown")
        logger.info(f"Executing task: {task_id}")
        
        try:
            sys.path.insert(0, str(ENGINE_DIR))
            
            from omega_forge import OmegaForge
            from omega_meta_logic import MetaCognition
            
            forge = OmegaForge(self.project)
            result = forge.execute_goal(task.get("goal", ""))
            
            if result.get("success"):
                self.state.tasks_completed += 1
                logger.info(f"Task {task_id} completed successfully")
            else:
                self.state.tasks_failed += 1
                logger.warning(f"Task {task_id} failed: {result.get('error')}")
            
            self._save_checkpoint()
            
        except Exception as e:
            self.state.tasks_failed += 1
            logger.error(f"Task {task_id} error: {e}")
        
        finally:
            self.resources.release_task_slot()
    
    def _shutdown(self):
        """Graceful shutdown."""
        logger.info("Shutting down OMEGA Daemon...")
        self.state.status = "stopped"
        self._save_checkpoint()
        logger.info("OMEGA Daemon stopped")
    
    def submit_task(self, goal: str, metadata: Dict = None) -> str:
        """Submit a task to the daemon queue."""
        task_queue = self.state_path / "task_queue.json"
        
        tasks = []
        if task_queue.exists():
            try:
                tasks = json.loads(task_queue.read_text())
            except:
                tasks = []
        
        task_id = hashlib.md5(f"{goal}{time.time()}".encode()).hexdigest()[:12]
        
        task = {
            "id": task_id,
            "goal": goal,
            "metadata": metadata or {},
            "submitted_at": datetime.now().isoformat()
        }
        
        tasks.append(task)
        task_queue.write_text(json.dumps(tasks, indent=2))
        
        logger.info(f"Task {task_id} submitted: {goal[:50]}...")
        return task_id
    
    def get_status(self) -> Dict:
        """Get daemon status."""
        return {
            "version": self.VERSION,
            "state": asdict(self.state),
            "resources": self.resources.check_resources(),
            "project": self.project,
            "port": self.port
        }


def start_daemon(project: str = "omega", port: int = 8765):
    """Start OMEGA daemon service."""
    daemon = OmegaDaemon(project, port)
    daemon.start()


def submit_task(goal: str, project: str = "omega") -> str:
    """Submit task to running daemon."""
    daemon = OmegaDaemon(project)
    return daemon.submit_task(goal)


def get_status(project: str = "omega") -> Dict:
    """Get daemon status."""
    daemon = OmegaDaemon(project)
    return daemon.get_status()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="OMEGA Persistent Daemon")
    parser.add_argument("--project", default="omega", help="Project name")
    parser.add_argument("--port", type=int, default=8765, help="Port")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon")
    parser.add_argument("--submit", type=str, help="Submit task and exit")
    parser.add_argument("--status", action="store_true", help="Show status")
    
    args = parser.parse_args()
    
    if args.status:
        print(json.dumps(get_status(args.project), indent=2))
    elif args.submit:
        print(f"Task ID: {submit_task(args.submit, args.project)}")
    else:
        start_daemon(args.project, args.port)