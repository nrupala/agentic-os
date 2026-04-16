#!/usr/bin/env python3
"""
agentic-OS State Manager
========================
Checkpoint/resume for long-running executions

MIT License
Copyright (c) 2024 Nrupal Akolkar
"""

import asyncio
import json
import hashlib
import pickle
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Set, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class CheckpointStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class TaskState:
    task_id: str
    name: str
    status: str
    result: Any = None
    error: Optional[str] = None
    progress: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    attempts: int = 0


@dataclass
class Checkpoint:
    checkpoint_id: str
    execution_id: str
    created_at: str
    status: CheckpointStatus
    tasks: Dict[str, TaskState] = field(default_factory=dict)
    memory_state: Dict[str, Any] = field(default_factory=dict)
    engine_state: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "checkpoint_id": self.checkpoint_id,
            "execution_id": self.execution_id,
            "created_at": self.created_at,
            "status": self.status.value,
            "tasks": {k: asdict(v) for k, v in self.tasks.items()},
            "memory_state": self.memory_state,
            "engine_state": self.engine_state,
            "metrics": self.metrics,
            "version": self.version
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Checkpoint":
        tasks = {
            k: TaskState(**v) for k, v in data.get("tasks", {}).items()
        }
        return cls(
            checkpoint_id=data["checkpoint_id"],
            execution_id=data["execution_id"],
            created_at=data["created_at"],
            status=CheckpointStatus(data["status"]),
            tasks=tasks,
            memory_state=data.get("memory_state", {}),
            engine_state=data.get("engine_state", {}),
            metrics=data.get("metrics", {}),
            version=data.get("version", "1.0")
        )


class CheckpointManager:
    def __init__(
        self,
        storage_path: str = ".checkpoints",
        max_checkpoints: int = 10,
        auto_save_interval: float = 30.0
    ):
        self.storage_path = Path(storage_path)
        self.max_checkpoints = max_checkpoints
        self.auto_save_interval = auto_save_interval
        
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self._current_checkpoint: Optional[Checkpoint] = None
        self._execution_id: Optional[str] = None
        self._tasks: Dict[str, TaskState] = {}
        self._memory_state: Dict[str, Any] = {}
        self._engine_state: Dict[str, Any] = {}
        self._dirty = False
        self._auto_save_task: Optional[asyncio.Task] = None
        self._listeners: List[Callable[[Checkpoint], None]] = []
    
    def start_execution(self, execution_id: str) -> str:
        checkpoint_id = hashlib.sha256(
            f"{execution_id}_{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()[:16]
        
        self._execution_id = execution_id
        self._current_checkpoint = Checkpoint(
            checkpoint_id=checkpoint_id,
            execution_id=execution_id,
            created_at=datetime.utcnow().isoformat(),
            status=CheckpointStatus.ACTIVE
        )
        self._tasks = {}
        self._memory_state = {}
        self._engine_state = {}
        self._dirty = True
        
        self._start_auto_save()
        
        logger.info(f"Started execution {execution_id} with checkpoint {checkpoint_id}")
        return checkpoint_id
    
    def update_task(
        self,
        task_id: str,
        name: str,
        status: str,
        result: Any = None,
        error: Optional[str] = None,
        progress: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None
    ):
        if task_id in self._tasks:
            task = self._tasks[task_id]
            task.status = status
            task.result = result
            task.error = error
            task.progress = progress
            if metadata:
                task.metadata.update(metadata)
            
            if status in ("completed", "failed", "cancelled"):
                task.completed_at = datetime.utcnow().isoformat()
        else:
            self._tasks[task_id] = TaskState(
                task_id=task_id,
                name=name,
                status=status,
                result=result,
                error=error,
                progress=progress,
                metadata=metadata or {},
                started_at=datetime.utcnow().isoformat()
            )
        
        self._dirty = True
    
    def update_memory_state(self, key: str, value: Any):
        self._memory_state[key] = value
        self._dirty = True
    
    def update_engine_state(self, key: str, value: Any):
        self._engine_state[key] = value
        self._dirty = True
    
    def set_metrics(self, metrics: Dict[str, Any]):
        if self._current_checkpoint:
            self._current_checkpoint.metrics = metrics
            self._dirty = True
    
    async def save(self, force: bool = False) -> Optional[str]:
        if not self._current_checkpoint or not self._dirty and not force:
            return None
        
        self._current_checkpoint.tasks = self._tasks.copy()
        self._current_checkpoint.memory_state = self._memory_state.copy()
        self._current_checkpoint.engine_state = self._engine_state.copy()
        
        checkpoint_path = self.storage_path / f"{self._current_checkpoint.checkpoint_id}.json"
        
        with open(checkpoint_path, "w") as f:
            json.dump(self._current_checkpoint.to_dict(), f, indent=2, default=str)
        
        await self._save_binaries()
        
        self._dirty = False
        self._enforce_max_checkpoints()
        
        for listener in self._listeners:
            try:
                listener(self._current_checkpoint)
            except Exception as e:
                logger.error(f"Checkpoint listener error: {e}")
        
        logger.info(f"Saved checkpoint {self._current_checkpoint.checkpoint_id}")
        return self._current_checkpoint.checkpoint_id
    
    async def _save_binaries(self):
        if self._memory_state or self._engine_state:
            binary_path = self.storage_path / f"{self._current_checkpoint.checkpoint_id}.bin"
            with open(binary_path, "wb") as f:
                pickle.dump({
                    "memory_state": self._memory_state,
                    "engine_state": self._engine_state
                }, f)
    
    def _enforce_max_checkpoints(self):
        checkpoints = sorted(
            self.storage_path.glob("*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        for old_checkpoint in checkpoints[self.max_checkpoints:]:
            checkpoint_id = old_checkpoint.stem
            binary_path = self.storage_path / f"{checkpoint_id}.bin"
            
            old_checkpoint.unlink(missing_ok=True)
            binary_path.unlink(missing_ok=True)
            
            logger.info(f"Removed old checkpoint {checkpoint_id}")
    
    def _start_auto_save(self):
        if self._auto_save_task:
            self._auto_save_task.cancel()
        
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return
        
        async def auto_save_loop():
            while True:
                await asyncio.sleep(self.auto_save_interval)
                if self._dirty:
                    await self.save()
        
        self._auto_save_task = asyncio.create_task(auto_save_loop())
    
    def stop_auto_save(self):
        if self._auto_save_task:
            self._auto_save_task.cancel()
            self._auto_save_task = None
    
    async def complete(self, status: CheckpointStatus = CheckpointStatus.COMPLETED):
        if self._current_checkpoint:
            self._current_checkpoint.status = status
            await self.save(force=True)
            self.stop_auto_save()
    
    async def resume(self, checkpoint_id: str) -> Checkpoint:
        checkpoint_path = self.storage_path / f"{checkpoint_id}.json"
        
        if not checkpoint_path.exists():
            raise FileNotFoundError(f"Checkpoint {checkpoint_id} not found")
        
        with open(checkpoint_path) as f:
            data = json.load(f)
        
        self._current_checkpoint = Checkpoint.from_dict(data)
        self._execution_id = self._current_checkpoint.execution_id
        self._tasks = self._current_checkpoint.tasks.copy()
        self._memory_state = self._current_checkpoint.memory_state.copy()
        self._engine_state = self._current_checkpoint.engine_state.copy()
        
        binary_path = self.storage_path / f"{checkpoint_id}.bin"
        if binary_path.exists():
            with open(binary_path, "rb") as f:
                data = pickle.load(f)
                self._memory_state = data.get("memory_state", {})
                self._engine_state = data.get("engine_state", {})
        
        self._dirty = False
        logger.info(f"Resumed execution from checkpoint {checkpoint_id}")
        
        return self._current_checkpoint
    
    def list_checkpoints(self) -> List[Dict[str, Any]]:
        checkpoints = []
        for path in self.storage_path.glob("*.json"):
            try:
                with open(path) as f:
                    data = json.load(f)
                checkpoints.append({
                    "checkpoint_id": data["checkpoint_id"],
                    "execution_id": data["execution_id"],
                    "created_at": data["created_at"],
                    "status": data["status"],
                    "task_count": len(data.get("tasks", {}))
                })
            except Exception as e:
                logger.error(f"Error reading checkpoint {path}: {e}")
        
        return sorted(checkpoints, key=lambda x: x["created_at"], reverse=True)
    
    def delete_checkpoint(self, checkpoint_id: str):
        checkpoint_path = self.storage_path / f"{checkpoint_id}.json"
        binary_path = self.storage_path / f"{checkpoint_id}.bin"
        
        checkpoint_path.unlink(missing_ok=True)
        binary_path.unlink(missing_ok=True)
        
        logger.info(f"Deleted checkpoint {checkpoint_id}")
    
    def on_checkpoint(self, listener: Callable[[Checkpoint], None]):
        self._listeners.append(listener)
    
    def get_current_checkpoint(self) -> Optional[Checkpoint]:
        return self._current_checkpoint
    
    def get_task(self, task_id: str) -> Optional[TaskState]:
        return self._tasks.get(task_id)
    
    def get_all_tasks(self) -> Dict[str, TaskState]:
        return self._tasks.copy()
    
    def get_memory_state(self, key: Optional[str] = None) -> Any:
        if key:
            return self._memory_state.get(key)
        return self._memory_state.copy()
    
    def get_engine_state(self, key: Optional[str] = None) -> Any:
        if key:
            return self._engine_state.get(key)
        return self._engine_state.copy()


class ResumableExecutor:
    def __init__(
        self,
        checkpoint_manager: Optional[CheckpointManager] = None,
        auto_checkpoint: bool = True,
        checkpoint_interval: float = 30.0
    ):
        self.checkpoint_manager = checkpoint_manager or CheckpointManager(
            auto_save_interval=checkpoint_interval
        )
        self.auto_checkpoint = auto_checkpoint
        self._execution_id: Optional[str] = None
        self._checkpoint_id: Optional[str] = None
        self._completed_tasks: Set[str] = set()
        self._task_results: Dict[str, Any] = {}
    
    async def execute(
        self,
        execution_id: str,
        tasks: List[Dict[str, Any]],
        executor_func: Callable
    ) -> Dict[str, Any]:
        self._execution_id = execution_id
        
        self._checkpoint_id = self.checkpoint_manager.start_execution(execution_id)
        
        if self.auto_checkpoint:
            self.checkpoint_manager.on_checkpoint(self._on_checkpoint)
        
        for task_data in tasks:
            task_id = task_data["id"]
            
            if task_id in self._completed_tasks:
                logger.info(f"Skipping completed task {task_id}")
                continue
            
            self.checkpoint_manager.update_task(
                task_id=task_id,
                name=task_data.get("name", task_id),
                status="running"
            )
            
            try:
                result = await executor_func(task_data)
                
                self._task_results[task_id] = result
                self._completed_tasks.add(task_id)
                
                self.checkpoint_manager.update_task(
                    task_id=task_id,
                    name=task_data.get("name", task_id),
                    status="completed",
                    result=result
                )
                
                await self.checkpoint_manager.save()
                
            except Exception as e:
                self.checkpoint_manager.update_task(
                    task_id=task_id,
                    name=task_data.get("name", task_id),
                    status="failed",
                    error=str(e)
                )
                await self.checkpoint_manager.save()
                raise
        
        await self.checkpoint_manager.complete()
        return self._task_results
    
    def _on_checkpoint(self, checkpoint: Checkpoint):
        logger.info(f"Checkpoint saved: {checkpoint.checkpoint_id}")
    
    async def resume(self, checkpoint_id: str, executor_func: Callable) -> Dict[str, Any]:
        checkpoint = await self.checkpoint_manager.resume(checkpoint_id)
        
        self._execution_id = checkpoint.execution_id
        self._checkpoint_id = checkpoint_id
        
        for task_id, task_state in checkpoint.tasks.items():
            if task_state.status == "completed":
                self._completed_tasks.add(task_id)
                self._task_results[task_id] = task_state.result
        
        logger.info(f"Resuming execution with {len(self._completed_tasks)} completed tasks")
        
        pending_tasks = [
            {"id": tid, "name": ts.name}
            for tid, ts in checkpoint.tasks.items()
            if ts.status not in ("completed", "failed", "cancelled")
        ]
        
        if pending_tasks:
            try:
                await self.execute(
                    self._execution_id,
                    pending_tasks,
                    executor_func
                )
            except Exception as e:
                logger.error(f"Error during resume: {e}")
                await self.checkpoint_manager.complete(CheckpointStatus.FAILED)
                raise
        
        return self._task_results


if __name__ == "__main__":
    import asyncio
    
    async def main():
        print("=" * 60)
        print("agentic-OS State Manager Demo")
        print("=" * 60)
        
        manager = CheckpointManager(storage_path=".test_checkpoints")
        
        exec_id = "demo-execution-001"
        checkpoint_id = manager.start_execution(exec_id)
        print(f"\nStarted execution {exec_id}")
        print(f"Checkpoint ID: {checkpoint_id}")
        
        manager.update_task(
            task_id="task-1",
            name="Fetch Data",
            status="running",
            progress=0.5
        )
        
        await asyncio.sleep(0.5)
        
        manager.update_task(
            task_id="task-1",
            name="Fetch Data",
            status="completed",
            result={"data": "sample data"},
            progress=1.0
        )
        
        manager.update_task(
            task_id="task-2",
            name="Process Data",
            status="completed",
            result={"processed": True}
        )
        
        manager.update_memory_state("working_memory", {"counter": 42})
        manager.update_engine_state("engine_mode", "parallel")
        
        saved_id = await manager.save()
        print(f"\nSaved checkpoint: {saved_id}")
        
        checkpoint = manager.get_current_checkpoint()
        print(f"\nCheckpoint status: {checkpoint.status.value}")
        print(f"Tasks: {len(checkpoint.tasks)}")
        for tid, task in checkpoint.tasks.items():
            print(f"  - {task.name}: {task.status}")
        
        checkpoints = manager.list_checkpoints()
        print(f"\nAll checkpoints: {len(checkpoints)}")
        
        shutil.rmtree(".test_checkpoints", ignore_errors=True)
        print("\n" + "=" * 60)
    
    asyncio.run(main())
