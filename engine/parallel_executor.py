#!/usr/bin/env python3
"""
agentic-OS Parallel Executor
============================
Concurrent task execution with dependency management

MIT License
Copyright (c) 2024 Nrupal Akolkar
"""

import asyncio
import uuid
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable, Awaitable, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    DEPENDENCY_FAILED = "dependency_failed"


@dataclass
class TaskResult:
    task_id: str
    status: TaskStatus
    result: Any = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Task:
    id: str
    name: str
    func: Callable[..., Awaitable[Any]]
    args: tuple = field(default_factory=tuple)
    kwargs: Dict[str, Any] = field(default_factory=dict)
    dependencies: Set[str] = field(default_factory=set)
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def __hash__(self):
        return hash(self.id)


class DependencyGraph:
    def __init__(self):
        self._tasks: Dict[str, Task] = {}
        self._dependents: Dict[str, Set[str]] = defaultdict(set)
        self._dependencies: Dict[str, Set[str]] = defaultdict(set)
    
    def add_task(self, task: Task):
        self._tasks[task.id] = task
        for dep_id in task.dependencies:
            self._dependents[dep_id].add(task.id)
            self._dependencies[task.id].add(dep_id)
    
    def get_ready_tasks(self) -> List[Task]:
        ready = []
        for task_id, task in self._tasks.items():
            if task.status != TaskStatus.PENDING:
                continue
            
            deps_completed = all(
                self._tasks[dep_id].status == TaskStatus.COMPLETED
                for dep_id in task.dependencies
            )
            
            deps_failed = any(
                self._tasks[dep_id].status in (TaskStatus.FAILED, TaskStatus.DEPENDENCY_FAILED)
                for dep_id in task.dependencies
            )
            
            if deps_failed:
                task.status = TaskStatus.DEPENDENCY_FAILED
                task.error = "One or more dependencies failed"
            elif deps_completed:
                ready.append(task)
        
        return ready
    
    def get_task(self, task_id: str) -> Optional[Task]:
        return self._tasks.get(task_id)
    
    def get_all_tasks(self) -> List[Task]:
        return list(self._tasks.values())
    
    def is_complete(self) -> bool:
        return all(
            t.status in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.DEPENDENCY_FAILED, TaskStatus.CANCELLED)
            for t in self._tasks.values()
        )
    
    def get_execution_order(self) -> List[List[str]]:
        levels = []
        remaining = set(self._tasks.keys())
        completed = set()
        
        while remaining:
            ready = []
            for task_id in remaining:
                deps = self._dependencies[task_id]
                if deps.issubset(completed):
                    ready.append(task_id)
            
            if not ready:
                break
            
            levels.append(ready)
            completed.update(ready)
            remaining.difference_update(ready)
        
        return levels


@dataclass
class ExecutionStats:
    total_tasks: int = 0
    completed: int = 0
    failed: int = 0
    running: int = 0
    pending: int = 0
    total_duration_ms: float = 0.0
    avg_task_duration_ms: float = 0.0
    max_parallelism: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_tasks": self.total_tasks,
            "completed": self.completed,
            "failed": self.failed,
            "running": self.running,
            "pending": self.pending,
            "total_duration_ms": round(self.total_duration_ms, 2),
            "avg_task_duration_ms": round(self.avg_task_duration_ms, 2),
            "max_parallelism": self.max_parallelism
        }


class ParallelExecutor:
    def __init__(
        self,
        max_workers: int = 4,
        stop_on_first_failure: bool = False,
        continue_on_failure: bool = True
    ):
        self.max_workers = max_workers
        self.stop_on_first_failure = stop_on_first_failure
        self.continue_on_failure = continue_on_failure
        self._graph = DependencyGraph()
        self._running_tasks: Dict[str, asyncio.Task] = {}
        self._results: Dict[str, TaskResult] = {}
        self._lock = asyncio.Lock()
        self._callbacks: Dict[str, List[Callable]] = defaultdict(list)
        self._start_time: Optional[float] = None
        self._peak_parallelism = 0
    
    def add_task(
        self,
        name: str,
        func: Callable[..., Awaitable[Any]],
        *args,
        dependencies: Optional[List[str]] = None,
        task_id: Optional[str] = None,
        **kwargs
    ) -> str:
        task_id = task_id or str(uuid.uuid4())
        
        task = Task(
            id=task_id,
            name=name,
            func=func,
            args=args,
            kwargs=kwargs,
            dependencies=set(dependencies or [])
        )
        
        self._graph.add_task(task)
        return task_id
    
    def on_task_complete(self, task_id: str, callback: Callable[[TaskResult], None]):
        self._callbacks[task_id].append(callback)
    
    async def _execute_task(self, task: Task) -> TaskResult:
        started_at = datetime.utcnow()
        
        try:
            result = await task.func(*task.args, **task.kwargs)
            completed_at = datetime.utcnow()
            duration_ms = (completed_at - started_at).total_seconds() * 1000
            
            task.status = TaskStatus.COMPLETED
            task.result = result
            
            return TaskResult(
                task_id=task.id,
                status=TaskStatus.COMPLETED,
                result=result,
                started_at=started_at,
                completed_at=completed_at,
                duration_ms=duration_ms
            )
        except asyncio.CancelledError:
            task.status = TaskStatus.CANCELLED
            return TaskResult(
                task_id=task.id,
                status=TaskStatus.CANCELLED,
                error="Task was cancelled",
                started_at=started_at,
                completed_at=datetime.utcnow(),
                duration_ms=(datetime.utcnow() - started_at).total_seconds() * 1000
            )
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            
            for dep_task in self._graph.get_all_tasks():
                if task.id in dep_task.dependencies:
                    dep_task.status = TaskStatus.DEPENDENCY_FAILED
                    dep_task.error = f"Dependency '{task.name}' failed"
            
            return TaskResult(
                task_id=task.id,
                status=TaskStatus.FAILED,
                error=str(e),
                started_at=started_at,
                completed_at=datetime.utcnow(),
                duration_ms=(datetime.utcnow() - started_at).total_seconds() * 1000
            )
    
    async def execute(self) -> Dict[str, TaskResult]:
        self._start_time = time.perf_counter()
        self._results = {}
        
        logger.info(f"Starting parallel execution with max_workers={self.max_workers}")
        
        try:
            while not self._graph.is_complete():
                ready_tasks = self._graph.get_ready_tasks()
                
                if not ready_tasks:
                    if not self._running_tasks:
                        break
                    await asyncio.sleep(0.01)
                    continue
                
                while ready_tasks and len(self._running_tasks) < self.max_workers:
                    task = ready_tasks.pop(0)
                    task.status = TaskStatus.RUNNING
                    
                    asyncio_task = asyncio.create_task(self._execute_task(task))
                    self._running_tasks[task.id] = asyncio_task
                    
                    self._peak_parallelism = max(self._peak_parallelism, len(self._running_tasks))
                
                if self._running_tasks:
                    done, pending = await asyncio.wait(
                        self._running_tasks.values(),
                        timeout=0.1,
                        return_when=asyncio.FIRST_COMPLETED
                    )
                    
                    for completed_task in done:
                        task_id = None
                        for tid, t in self._running_tasks.items():
                            if t == completed_task:
                                task_id = tid
                                break
                        
                        if task_id:
                            result = await completed_task
                            self._results[task_id] = result
                            
                            for callback in self._callbacks.get(task_id, []):
                                try:
                                    callback(result)
                                except Exception as e:
                                    logger.error(f"Callback error: {e}")
                            
                            del self._running_tasks[task_id]
                            
                            logger.info(f"Task {task_id} completed with status {result.status.value}")
                            
                            if result.status == TaskStatus.FAILED and self.stop_on_first_failure:
                                for running_id, running_task in list(self._running_tasks.items()):
                                    running_task.cancel()
                                return self._results
                    
                    ready_tasks = self._graph.get_ready_tasks()
                
                if not self._running_tasks and not ready_tasks:
                    break
            
            for remaining_id, remaining_task in list(self._running_tasks.items()):
                try:
                    result = await remaining_task
                    self._results[remaining_id] = result
                except Exception as e:
                    self._results[remaining_id] = TaskResult(
                        task_id=remaining_id,
                        status=TaskStatus.FAILED,
                        error=str(e)
                    )
            
        except Exception as e:
            logger.error(f"Execution error: {e}")
            for running_task in self._running_tasks.values():
                running_task.cancel()
        
        return self._results
    
    def get_stats(self) -> ExecutionStats:
        all_tasks = self._graph.get_all_tasks()
        completed_tasks = [t for t in all_tasks if t.status == TaskStatus.COMPLETED]
        failed_tasks = [t for t in all_tasks if t.status == TaskStatus.FAILED]
        running_tasks = [t for t in all_tasks if t.status == TaskStatus.RUNNING]
        pending_tasks = [t for t in all_tasks if t.status == TaskStatus.PENDING]
        
        total_duration = 0.0
        for result in self._results.values():
            total_duration += result.duration_ms
        
        avg_duration = total_duration / len(completed_tasks) if completed_tasks else 0.0
        
        return ExecutionStats(
            total_tasks=len(all_tasks),
            completed=len(completed_tasks),
            failed=len(failed_tasks),
            running=len(running_tasks),
            pending=len(pending_tasks),
            total_duration_ms=time.perf_counter() - self._start_time if self._start_time else 0.0,
            avg_task_duration_ms=avg_duration,
            max_parallelism=self._peak_parallelism
        )
    
    def get_results(self) -> Dict[str, TaskResult]:
        return self._results
    
    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        task = self._graph.get_task(task_id)
        return task.status if task else None
    
    def cancel_all(self):
        for task in self._running_tasks.values():
            task.cancel()


async def create_task_dag() -> ParallelExecutor:
    executor = ParallelExecutor(max_workers=4)
    
    async def fetch_data(name: str, delay: float):
        await asyncio.sleep(delay)
        return f"data from {name}"
    
    async def process_data(name: str, data: Any):
        await asyncio.sleep(0.5)
        return f"processed {data}"
    
    executor.add_task("fetch_users", fetch_data, "users", 1.0)
    executor.add_task("fetch_products", fetch_data, "products", 0.8)
    
    results = executor.get_results()
    user_data_id = list(executor._graph.get_all_tasks())[0].id
    product_data_id = list(executor._graph.get_all_tasks())[1].id
    
    executor.add_task(
        "process_users",
        process_data,
        "users",
        None,
        dependencies=[user_data_id]
    )
    
    executor.add_task(
        "process_products",
        process_data,
        "products",
        None,
        dependencies=[product_data_id]
    )
    
    return executor


if __name__ == "__main__":
    async def main():
        print("=" * 60)
        print("agentic-OS Parallel Executor Demo")
        print("=" * 60)
        
        executor = ParallelExecutor(max_workers=3)
        
        async def task1():
            await asyncio.sleep(1.0)
            return "Task 1 result"
        
        async def task2(data: str):
            await asyncio.sleep(0.5)
            return f"Task 2 result with {data}"
        
        async def task3(data: str):
            await asyncio.sleep(0.3)
            return f"Task 3 result with {data}"
        
        async def dependent_task(data1: str, data2: str):
            await asyncio.sleep(0.5)
            return f"Dependent task: {data1} + {data2}"
        
        id1 = executor.add_task("Independent Task 1", task1)
        id2 = executor.add_task("Independent Task 2", task2, "input_data")
        
        executor.add_task(
            "Dependent Task",
            dependent_task,
            None,
            None,
            dependencies=[id1, id2]
        )
        
        print(f"\nExecuting {len(executor._graph.get_all_tasks())} tasks with max 3 workers...\n")
        
        results = await executor.execute()
        stats = executor.get_stats()
        
        print("Results:")
        for task_id, result in results.items():
            task = executor._graph.get_task(task_id)
            status_icon = {
                TaskStatus.COMPLETED: "✓",
                TaskStatus.FAILED: "✗",
                TaskStatus.RUNNING: "⟳",
                TaskStatus.PENDING: "○"
            }.get(result.status, "?")
            
            print(f"  {status_icon} {task.name}: {result.status.value}")
            if result.result:
                print(f"      → {result.result}")
            if result.error:
                print(f"      → Error: {result.error}")
        
        print(f"\nStats:")
        print(f"  Total tasks: {stats.total_tasks}")
        print(f"  Completed: {stats.completed}")
        print(f"  Failed: {stats.failed}")
        print(f"  Total duration: {stats.total_duration_ms:.1f}ms")
        print(f"  Peak parallelism: {stats.max_parallelism}")
        print("=" * 60)
    
    asyncio.run(main())
