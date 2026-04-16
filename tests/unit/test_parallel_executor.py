#!/usr/bin/env python3
"""
Unit tests for engine/parallel_executor.py

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

from engine.parallel_executor import (
    TaskStatus,
    TaskResult,
    Task,
    DependencyGraph,
    ExecutionStats,
    ParallelExecutor
)


class TestTaskStatus:
    def test_task_status_values(self):
        assert TaskStatus.PENDING.value == "pending"
        assert TaskStatus.RUNNING.value == "running"
        assert TaskStatus.COMPLETED.value == "completed"
        assert TaskStatus.FAILED.value == "failed"
        assert TaskStatus.CANCELLED.value == "cancelled"
        assert TaskStatus.DEPENDENCY_FAILED.value == "dependency_failed"


class TestTaskResult:
    def test_task_result_creation(self):
        result = TaskResult(
            task_id="test-1",
            status=TaskStatus.COMPLETED,
            result="success",
            duration_ms=100.5
        )
        assert result.task_id == "test-1"
        assert result.status == TaskStatus.COMPLETED
        assert result.result == "success"
        assert result.duration_ms == 100.5

    def test_task_result_with_error(self):
        result = TaskResult(
            task_id="test-1",
            status=TaskStatus.FAILED,
            error="Something went wrong"
        )
        assert result.error == "Something went wrong"


class TestTask:
    def test_task_creation(self):
        async def dummy_func():
            return "result"
        
        task = Task(
            id="task-1",
            name="Test Task",
            func=dummy_func
        )
        assert task.id == "task-1"
        assert task.name == "Test Task"
        assert task.status == TaskStatus.PENDING
        assert task.dependencies == set()

    def test_task_with_dependencies(self):
        async def dummy_func():
            return "result"
        
        task = Task(
            id="task-2",
            name="Dependent Task",
            func=dummy_func,
            dependencies={"task-1", "task-0"}
        )
        assert "task-1" in task.dependencies
        assert "task-0" in task.dependencies

    def test_task_hashable(self):
        async def dummy_func():
            return "result"
        
        task1 = Task(id="task-1", name="Task 1", func=dummy_func)
        task2 = Task(id="task-2", name="Task 2", func=dummy_func)
        
        task_set = {task1, task2}
        assert len(task_set) == 2


class TestDependencyGraph:
    def test_graph_creation(self):
        graph = DependencyGraph()
        assert graph._tasks == {}

    def test_add_task(self):
        graph = DependencyGraph()
        
        async def dummy_func():
            return "result"
        
        task = Task(id="task-1", name="Task 1", func=dummy_func)
        graph.add_task(task)
        
        assert "task-1" in graph._tasks
        assert graph.get_task("task-1") == task

    def test_get_ready_tasks_no_dependencies(self):
        graph = DependencyGraph()
        
        async def dummy_func():
            return "result"
        
        task = Task(id="task-1", name="Task 1", func=dummy_func)
        graph.add_task(task)
        
        ready = graph.get_ready_tasks()
        assert len(ready) == 1
        assert ready[0].id == "task-1"

    def test_get_ready_tasks_with_dependencies_not_met(self):
        graph = DependencyGraph()
        
        async def dummy_func():
            return "result"
        
        task1 = Task(id="task-1", name="Task 1", func=dummy_func)
        task2 = Task(id="task-2", name="Task 2", func=dummy_func, dependencies={"task-1"})
        
        graph.add_task(task1)
        graph.add_task(task2)
        
        ready = graph.get_ready_tasks()
        assert len(ready) == 1
        assert ready[0].id == "task-1"

    def test_get_ready_tasks_with_dependencies_met(self):
        graph = DependencyGraph()
        
        async def dummy_func():
            return "result"
        
        task1 = Task(id="task-1", name="Task 1", func=dummy_func)
        task2 = Task(id="task-2", name="Task 2", func=dummy_func, dependencies={"task-1"})
        
        graph.add_task(task1)
        graph.add_task(task2)
        
        task1.status = TaskStatus.COMPLETED
        ready = graph.get_ready_tasks()
        
        assert len(ready) == 1
        assert ready[0].id == "task-2"

    def test_is_complete_all_completed(self):
        graph = DependencyGraph()
        
        async def dummy_func():
            return "result"
        
        task1 = Task(id="task-1", name="Task 1", func=dummy_func)
        task2 = Task(id="task-2", name="Task 2", func=dummy_func)
        
        graph.add_task(task1)
        graph.add_task(task2)
        
        task1.status = TaskStatus.COMPLETED
        task2.status = TaskStatus.COMPLETED
        
        assert graph.is_complete() is True

    def test_is_complete_pending_tasks(self):
        graph = DependencyGraph()
        
        async def dummy_func():
            return "result"
        
        task1 = Task(id="task-1", name="Task 1", func=dummy_func)
        task2 = Task(id="task-2", name="Task 2", func=dummy_func)
        
        graph.add_task(task1)
        graph.add_task(task2)
        
        task1.status = TaskStatus.COMPLETED
        
        assert graph.is_complete() is False

    def test_get_execution_order(self):
        graph = DependencyGraph()
        
        async def dummy_func():
            return "result"
        
        task1 = Task(id="task-1", name="Task 1", func=dummy_func)
        task2 = Task(id="task-2", name="Task 2", func=dummy_func, dependencies={"task-1"})
        task3 = Task(id="task-3", name="Task 3", func=dummy_func, dependencies={"task-1"})
        task4 = Task(id="task-4", name="Task 4", func=dummy_func, dependencies={"task-2", "task-3"})
        
        graph.add_task(task1)
        graph.add_task(task2)
        graph.add_task(task3)
        graph.add_task(task4)
        
        levels = graph.get_execution_order()
        
        assert len(levels) == 3
        assert levels[0] == ["task-1"]
        assert set(levels[1]) == {"task-2", "task-3"}
        assert levels[2] == ["task-4"]


class TestExecutionStats:
    def test_execution_stats_creation(self):
        stats = ExecutionStats(
            total_tasks=10,
            completed=8,
            failed=1,
            running=1
        )
        assert stats.total_tasks == 10
        assert stats.completed == 8
        assert stats.failed == 1

    def test_execution_stats_to_dict(self):
        stats = ExecutionStats(total_tasks=5, completed=5)
        result = stats.to_dict()
        
        assert result["total_tasks"] == 5
        assert result["completed"] == 5


class TestParallelExecutor:
    def test_executor_creation(self):
        executor = ParallelExecutor(max_workers=4)
        assert executor.max_workers == 4
        assert executor._running_tasks == {}

    def test_add_task(self):
        executor = ParallelExecutor()
        
        async def dummy_func():
            return "result"
        
        task_id = executor.add_task("Test Task", dummy_func)
        assert task_id is not None
        assert executor._graph.get_task(task_id) is not None

    def test_add_task_with_dependencies(self):
        executor = ParallelExecutor()
        
        async def dummy_func():
            return "result"
        
        id1 = executor.add_task("Task 1", dummy_func)
        id2 = executor.add_task("Task 2", dummy_func, dependencies=[id1])
        
        task2 = executor._graph.get_task(id2)
        assert id1 in task2.dependencies

    @pytest.mark.asyncio
    async def test_execute_single_task(self):
        executor = ParallelExecutor(max_workers=1)
        
        async def simple_task():
            await asyncio.sleep(0.01)
            return "success"
        
        executor.add_task("Simple Task", simple_task)
        
        results = await executor.execute()
        
        assert len(results) == 1
        result = list(results.values())[0]
        assert result.status == TaskStatus.COMPLETED
        assert result.result == "success"

    @pytest.mark.asyncio
    async def test_execute_multiple_independent_tasks(self):
        executor = ParallelExecutor(max_workers=3)
        
        async def task1():
            await asyncio.sleep(0.05)
            return "task1"
        
        async def task2():
            await asyncio.sleep(0.05)
            return "task2"
        
        async def task3():
            await asyncio.sleep(0.05)
            return "task3"
        
        executor.add_task("Task 1", task1)
        executor.add_task("Task 2", task2)
        executor.add_task("Task 3", task3)
        
        results = await executor.execute()
        
        assert len(results) == 3
        completed = [r for r in results.values() if r.status == TaskStatus.COMPLETED]
        assert len(completed) == 3

    @pytest.mark.asyncio
    async def test_execute_dependent_tasks(self):
        executor = ParallelExecutor(max_workers=2)
        
        results_store = {}
        
        async def task1():
            await asyncio.sleep(0.05)
            results_store["task1"] = "done"
            return "task1_done"
        
        async def task2():
            await asyncio.sleep(0.05)
            return "task2_done"
        
        id1 = executor.add_task("Task 1", task1)
        executor.add_task("Task 2", task2, dependencies=[id1])
        
        results = await executor.execute()
        
        task1_result = results.get(id1)
        task2_result = next((r for r_id, r in results.items() if r_id != id1), None)
        
        assert task1_result is not None
        assert task1_result.status == TaskStatus.COMPLETED
        assert task1_result.result == "task1_done"
        assert task2_result is not None
        assert task2_result.status == TaskStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_execute_handles_task_failure(self):
        executor = ParallelExecutor(max_workers=1, continue_on_failure=True)
        
        async def failing_task():
            raise ValueError("Task failed")
        
        executor.add_task("Failing Task", failing_task)
        
        results = await executor.execute()
        
        result = list(results.values())[0]
        assert result.status == TaskStatus.FAILED
        assert "Task failed" in result.error

    @pytest.mark.asyncio
    async def test_get_stats(self):
        executor = ParallelExecutor(max_workers=1)
        
        async def simple_task():
            await asyncio.sleep(0.01)
            return "success"
        
        executor.add_task("Task 1", simple_task)
        executor.add_task("Task 2", simple_task)
        
        await executor.execute()
        
        stats = executor.get_stats()
        
        assert stats.total_tasks == 2
        assert stats.completed == 2

    @pytest.mark.asyncio
    async def test_parallelism_limit(self):
        executor = ParallelExecutor(max_workers=2)
        
        start_time = asyncio.get_event_loop().time()
        
        async def long_task():
            await asyncio.sleep(0.2)
            return "done"
        
        executor.add_task("Task 1", long_task)
        executor.add_task("Task 2", long_task)
        executor.add_task("Task 3", long_task)
        
        await executor.execute()
        
        elapsed = asyncio.get_event_loop().time() - start_time
        
        assert executor.get_stats().max_parallelism <= 2

    @pytest.mark.asyncio
    async def test_cancel_all(self):
        executor = ParallelExecutor(max_workers=2)
        
        async def long_task():
            await asyncio.sleep(10)
            return "done"
        
        executor.add_task("Task 1", long_task)
        executor.add_task("Task 2", long_task)
        
        async def run_and_cancel():
            task = asyncio.create_task(executor.execute())
            await asyncio.sleep(0.1)
            executor.cancel_all()
            await task
        
        await run_and_cancel()

    @pytest.mark.asyncio
    async def test_task_callback(self):
        executor = ParallelExecutor(max_workers=1)
        callback_results = []
        
        async def simple_task():
            await asyncio.sleep(0.01)
            return "success"
        
        task_id = executor.add_task("Task", simple_task)
        executor.on_task_complete(task_id, lambda r: callback_results.append(r))
        
        await executor.execute()
        
        assert len(callback_results) == 1
        assert callback_results[0].result == "success"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
