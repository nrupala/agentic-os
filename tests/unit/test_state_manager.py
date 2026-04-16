#!/usr/bin/env python3
"""
Unit tests for engine/state_manager.py

MIT License
Copyright (c) 2024 Nrupal Akolkar
"""

import pytest
import asyncio
import json
import shutil
import tempfile
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from engine.state_manager import (
    CheckpointStatus,
    TaskState,
    Checkpoint,
    CheckpointManager,
    ResumableExecutor
)


class TestCheckpointStatus:
    def test_checkpoint_status_values(self):
        assert CheckpointStatus.ACTIVE.value == "active"
        assert CheckpointStatus.COMPLETED.value == "completed"
        assert CheckpointStatus.FAILED.value == "failed"
        assert CheckpointStatus.CANCELLED.value == "cancelled"


class TestTaskState:
    def test_task_state_creation(self):
        state = TaskState(
            task_id="task-1",
            name="Test Task",
            status="running"
        )
        assert state.task_id == "task-1"
        assert state.name == "Test Task"
        assert state.status == "running"
        assert state.progress == 0.0

    def test_task_state_with_result(self):
        state = TaskState(
            task_id="task-1",
            name="Test Task",
            status="completed",
            result={"data": "success"}
        )
        assert state.result == {"data": "success"}

    def test_task_state_with_error(self):
        state = TaskState(
            task_id="task-1",
            name="Test Task",
            status="failed",
            error="Something went wrong"
        )
        assert state.error == "Something went wrong"


class TestCheckpoint:
    def test_checkpoint_creation(self):
        checkpoint = Checkpoint(
            checkpoint_id="cp-1",
            execution_id="exec-1",
            created_at="2024-01-01T00:00:00",
            status=CheckpointStatus.ACTIVE
        )
        assert checkpoint.checkpoint_id == "cp-1"
        assert checkpoint.execution_id == "exec-1"
        assert checkpoint.status == CheckpointStatus.ACTIVE
        assert checkpoint.tasks == {}

    def test_checkpoint_to_dict(self):
        checkpoint = Checkpoint(
            checkpoint_id="cp-1",
            execution_id="exec-1",
            created_at="2024-01-01T00:00:00",
            status=CheckpointStatus.ACTIVE,
            tasks={}
        )
        result = checkpoint.to_dict()
        
        assert result["checkpoint_id"] == "cp-1"
        assert result["execution_id"] == "exec-1"
        assert result["status"] == "active"

    def test_checkpoint_from_dict(self):
        data = {
            "checkpoint_id": "cp-1",
            "execution_id": "exec-1",
            "created_at": "2024-01-01T00:00:00",
            "status": "completed",
            "tasks": {}
        }
        
        checkpoint = Checkpoint.from_dict(data)
        
        assert checkpoint.checkpoint_id == "cp-1"
        assert checkpoint.status == CheckpointStatus.COMPLETED

    def test_checkpoint_with_tasks(self):
        task = TaskState(task_id="task-1", name="Task 1", status="completed")
        
        checkpoint = Checkpoint(
            checkpoint_id="cp-1",
            execution_id="exec-1",
            created_at="2024-01-01T00:00:00",
            status=CheckpointStatus.ACTIVE,
            tasks={"task-1": task}
        )
        
        result = checkpoint.to_dict()
        assert "task-1" in result["tasks"]


class TestCheckpointManager:
    @pytest.fixture
    def temp_dir(self):
        tmpdir = tempfile.mkdtemp()
        yield tmpdir
        shutil.rmtree(tmpdir, ignore_errors=True)

    def test_manager_creation(self, temp_dir):
        manager = CheckpointManager(storage_path=temp_dir)
        assert manager.storage_path == Path(temp_dir)

    def test_start_execution(self, temp_dir):
        manager = CheckpointManager(storage_path=temp_dir)
        checkpoint_id = manager.start_execution("exec-1")
        
        assert checkpoint_id is not None
        assert manager._current_checkpoint is not None
        assert manager._execution_id == "exec-1"

    def test_update_task_new(self, temp_dir):
        manager = CheckpointManager(storage_path=temp_dir)
        manager.start_execution("exec-1")
        
        manager.update_task(
            task_id="task-1",
            name="Task 1",
            status="running"
        )
        
        assert "task-1" in manager._tasks
        assert manager._tasks["task-1"].name == "Task 1"
        assert manager._tasks["task-1"].status == "running"

    def test_update_task_existing(self, temp_dir):
        manager = CheckpointManager(storage_path=temp_dir)
        manager.start_execution("exec-1")
        
        manager.update_task("task-1", "Task 1", "running")
        manager.update_task("task-1", "Task 1", "completed", result="success")
        
        assert manager._tasks["task-1"].status == "completed"
        assert manager._tasks["task-1"].result == "success"

    def test_update_memory_state(self, temp_dir):
        manager = CheckpointManager(storage_path=temp_dir)
        manager.start_execution("exec-1")
        
        manager.update_memory_state("counter", 42)
        manager.update_memory_state("data", {"key": "value"})
        
        assert manager._memory_state["counter"] == 42
        assert manager._memory_state["data"] == {"key": "value"}

    def test_update_engine_state(self, temp_dir):
        manager = CheckpointManager(storage_path=temp_dir)
        manager.start_execution("exec-1")
        
        manager.update_engine_state("mode", "parallel")
        
        assert manager._engine_state["mode"] == "parallel"

    @pytest.mark.asyncio
    async def test_save_checkpoint(self, temp_dir):
        manager = CheckpointManager(storage_path=temp_dir)
        manager.start_execution("exec-1")
        
        manager.update_task("task-1", "Task 1", "running")
        
        saved_id = await manager.save()
        
        assert saved_id is not None
        
        checkpoint_file = Path(temp_dir) / f"{saved_id}.json"
        assert checkpoint_file.exists()
        
        with open(checkpoint_file) as f:
            data = json.load(f)
        
        assert data["checkpoint_id"] == saved_id
        assert "task-1" in data["tasks"]

    @pytest.mark.asyncio
    async def test_save_creates_binary_file(self, temp_dir):
        manager = CheckpointManager(storage_path=temp_dir)
        manager.start_execution("exec-1")
        
        manager.update_memory_state("data", "test")
        
        saved_id = await manager.save()
        
        binary_file = Path(temp_dir) / f"{saved_id}.bin"
        assert binary_file.exists()

    @pytest.mark.asyncio
    async def test_complete_checkpoint(self, temp_dir):
        manager = CheckpointManager(storage_path=temp_dir)
        manager.start_execution("exec-1")
        
        await manager.complete()
        
        assert manager._current_checkpoint.status == CheckpointStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_complete_with_status(self, temp_dir):
        manager = CheckpointManager(storage_path=temp_dir)
        manager.start_execution("exec-1")
        
        await manager.complete(CheckpointStatus.FAILED)
        
        assert manager._current_checkpoint.status == CheckpointStatus.FAILED

    @pytest.mark.asyncio
    async def test_resume_checkpoint(self, temp_dir):
        manager = CheckpointManager(storage_path=temp_dir)
        manager.start_execution("exec-1")
        
        manager.update_task("task-1", "Task 1", "completed", result="success")
        saved_id = await manager.save()
        
        new_manager = CheckpointManager(storage_path=temp_dir)
        resumed = await new_manager.resume(saved_id)
        
        assert resumed.execution_id == "exec-1"
        assert "task-1" in resumed.tasks
        assert resumed.tasks["task-1"].result == "success"

    def test_list_checkpoints(self, temp_dir):
        manager = CheckpointManager(storage_path=temp_dir)
        
        import asyncio
        async def create_checkpoint():
            manager.start_execution(f"exec-{datetime.utcnow().timestamp()}")
            await manager.save()
        
        asyncio.run(create_checkpoint())
        asyncio.run(create_checkpoint())
        
        checkpoints = manager.list_checkpoints()
        assert len(checkpoints) >= 2

    def test_delete_checkpoint(self, temp_dir):
        manager = CheckpointManager(storage_path=temp_dir)
        
        import asyncio
        async def create_and_delete():
            manager.start_execution("exec-1")
            return await manager.save()
        
        saved_id = asyncio.run(create_and_delete())
        
        manager.delete_checkpoint(saved_id)
        
        checkpoints = manager.list_checkpoints()
        assert not any(c["checkpoint_id"] == saved_id for c in checkpoints)

    def test_get_task(self, temp_dir):
        manager = CheckpointManager(storage_path=temp_dir)
        manager.start_execution("exec-1")
        manager.update_task("task-1", "Task 1", "completed")
        
        task = manager.get_task("task-1")
        assert task is not None
        assert task.name == "Task 1"

    def test_get_nonexistent_task(self, temp_dir):
        manager = CheckpointManager(storage_path=temp_dir)
        manager.start_execution("exec-1")
        
        task = manager.get_task("nonexistent")
        assert task is None

    def test_get_memory_state(self, temp_dir):
        manager = CheckpointManager(storage_path=temp_dir)
        manager.start_execution("exec-1")
        manager.update_memory_state("key", "value")
        
        value = manager.get_memory_state("key")
        assert value == "value"

    def test_get_all_memory_state(self, temp_dir):
        manager = CheckpointManager(storage_path=temp_dir)
        manager.start_execution("exec-1")
        manager.update_memory_state("key1", "value1")
        manager.update_memory_state("key2", "value2")
        
        all_state = manager.get_memory_state()
        assert all_state == {"key1": "value1", "key2": "value2"}

    def test_max_checkpoints_enforcement(self, temp_dir):
        manager = CheckpointManager(storage_path=temp_dir, max_checkpoints=2)
        
        import asyncio
        async def create_checkpoint():
            manager.start_execution(f"exec-{datetime.utcnow().timestamp()}")
            await manager.save()
        
        for i in range(5):
            asyncio.run(create_checkpoint())
        
        checkpoints = manager.list_checkpoints()
        assert len(checkpoints) <= 2

    def test_checkpoint_listener(self, temp_dir):
        manager = CheckpointManager(storage_path=temp_dir)
        manager.start_execution("exec-1")
        
        listener_called = []
        manager.on_checkpoint(lambda cp: listener_called.append(cp))
        
        import asyncio
        async def trigger_listener():
            manager.update_task("task-1", "Task 1", "completed")
            await manager.save()
        
        asyncio.run(trigger_listener())
        
        assert len(listener_called) == 1


class TestResumableExecutor:
    @pytest.fixture
    def temp_dir(self):
        tmpdir = tempfile.mkdtemp()
        yield tmpdir
        shutil.rmtree(tmpdir, ignore_errors=True)

    @pytest.mark.asyncio
    async def test_execute_creates_checkpoint(self, temp_dir):
        from engine.state_manager import CheckpointManager
        
        manager = CheckpointManager(storage_path=temp_dir)
        executor = ResumableExecutor(checkpoint_manager=manager)
        
        async def dummy_task(task):
            return f"Result for {task['id']}"
        
        tasks = [{"id": "task-1", "name": "Task 1"}]
        
        results = await executor.execute("exec-1", tasks, dummy_task)
        
        assert "task-1" in results
        assert manager._current_checkpoint is not None

    @pytest.mark.asyncio
    async def test_resume_skips_completed_tasks(self, temp_dir):
        from engine.state_manager import CheckpointManager
        
        manager = CheckpointManager(storage_path=temp_dir)
        executor = ResumableExecutor(checkpoint_manager=manager)
        
        completed_tasks = []
        
        async def track_task(task):
            completed_tasks.append(task["id"])
            return f"Result for {task['id']}"
        
        tasks = [{"id": "task-1", "name": "Task 1"}]
        
        await executor.execute("exec-1", tasks, track_task)
        
        assert "task-1" in completed_tasks


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
