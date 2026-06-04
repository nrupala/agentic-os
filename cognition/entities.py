#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
# Copyright 2026 agentic-OS Contributors

"""
Paradise Cognitive Entities - Carriers, Blobs, Containers, Placeholders
The foundational building blocks of the cognitive system
"""

import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Callable
from enum import Enum

PROJECT_ROOT = Path(os.environ.get("HOST_PROJECT_ROOT", "/app"))


class EntityState(Enum):
    IDLE = "idle"
    RUNNING = "running"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"
    SUSPENDED = "suspended"


class Container:
    """Container for organizing related entities and their state"""
    
    def __init__(self, name: str, container_type: str = "generic"):
        self.id = str(uuid.uuid4())[:12]
        self.name = name
        self.type = container_type
        self.entities = {}
        self.blobs = {}
        self.state = EntityState.IDLE
        self.parent_id = None
        self.children = []
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
        self.metadata = {}
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "state": self.state.value,
            "parent_id": self.parent_id,
            "children": self.children,
            "entities": list(self.entities.keys()),
            "blobs": list(self.blobs.keys()),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Container":
        container = cls(name=data["name"], container_type=data.get("type", "generic"))
        container.id = data.get("id", container.id)
        container.state = EntityState(data.get("state", "idle"))
        container.parent_id = data.get("parent_id")
        container.children = data.get("children", [])
        container.created_at = data.get("created_at", container.created_at)
        container.updated_at = data.get("updated_at", container.created_at)
        container.metadata = data.get("metadata", {})
        return container
    
    def add_entity(self, entity_id: str):
        if entity_id not in self.entities:
            self.entities[entity_id] = entity_id
            self.updated_at = datetime.now().isoformat()
    
    def remove_entity(self, entity_id: str):
        if entity_id in self.entities:
            del self.entities[entity_id]
            self.updated_at = datetime.now().isoformat()
    
    def add_blob(self, blob_id: str):
        if blob_id not in self.blobs:
            self.blobs[blob_id] = blob_id
            self.updated_at = datetime.now().isoformat()
    
    def set_state(self, state: EntityState):
        self.state = state
        self.updated_at = datetime.now().isoformat()
    
    def is_complete(self) -> bool:
        return self.state == EntityState.COMPLETED
    
    def is_failed(self) -> bool:
        return self.state == EntityState.FAILED


class ServiceCarrier:
    """A carrier that provides services to other carriers"""
    
    def __init__(self, name: str, service_type: str):
        self.id = str(uuid.uuid4())[:12]
        self.name = name
        self.type = service_type
        self.endpoints = {}
        self.state = EntityState.IDLE
        self.dependencies = []
        self.provides = []
        self.created_at = datetime.now().isoformat()
        self.last_execution = None
        self.execution_count = 0
        self.error_count = 0
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "state": self.state.value,
            "endpoints": self.endpoints,
            "dependencies": self.dependencies,
            "provides": self.provides,
            "execution_count": self.execution_count,
            "error_count": self.error_count,
            "created_at": self.created_at,
            "last_execution": self.last_execution,
        }
    
    def add_endpoint(self, name: str, handler: Callable):
        self.endpoints[name] = {
            "handler": handler.__name__ if hasattr(handler, "__name__") else "unknown",
            "added_at": datetime.now().isoformat(),
        }
    
    def record_execution(self, success: bool = True):
        self.execution_count += 1
        self.last_execution = datetime.now().isoformat()
        if not success:
            self.error_count += 1
    
    def health_check(self) -> dict:
        return {
            "healthy": self.error_count < self.execution_count * 0.5 if self.execution_count > 0 else True,
            "executions": self.execution_count,
            "errors": self.error_count,
            "error_rate": self.error_count / self.execution_count if self.execution_count > 0 else 0,
        }


class DataBlob:
    """Immutable data container that can be passed between carriers"""
    
    def __init__(
        self,
        content: Any,
        blob_type: str = "data",
        schema: Optional[dict] = None,
    ):
        self.id = str(uuid.uuid4())[:12]
        self.content = content
        self.type = blob_type
        self.schema = schema or {}
        self.version = 1
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
        self.hash = self._compute_hash()
        self.tags = []
    
    def _compute_hash(self) -> str:
        content_str = str(self.content)
        return str(abs(hash(content_str)))[:16]
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.type,
            "schema": self.schema,
            "version": self.version,
            "hash": self.hash,
            "tags": self.tags,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
    
    def update(self, new_content: Any) -> "DataBlob":
        self.content = new_content
        self.version += 1
        self.updated_at = datetime.now().isoformat()
        self.hash = self._compute_hash()
        return self
    
    def add_tag(self, tag: str):
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.now().isoformat()


class TaskPlaceholder:
    """Placeholder for tasks that will be filled in later"""
    
    def __init__(
        self,
        name: str,
        expected_type: str,
        constraints: Optional[dict] = None,
    ):
        self.id = str(uuid.uuid4())[:12]
        self.name = name
        self.expected_type = expected_type
        self.constraints = constraints or {}
        self.filled = False
        self.filled_with = None
        self.filled_at = None
        self.created_at = datetime.now().isoformat()
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "expected_type": self.expected_type,
            "constraints": self.constraints,
            "filled": self.filled,
            "filled_with": self.filled_with,
            "filled_at": self.filled_at,
            "created_at": self.created_at,
        }
    
    def fill(self, content: Any):
        self.filled = True
        self.filled_with = content
        self.filled_at = datetime.now().isoformat()
    
    def is_valid(self) -> bool:
        if not self.filled:
            return True
        
        if "type_constraint" in self.constraints:
            expected = self.constraints["type_constraint"]
            if not isinstance(self.filled_with, expected):
                return False
        
        return True


class CognitiveCarrier:
    """Carrier specialized for cognitive tasks"""
    
    CARRIER_TYPES = [
        "planner",
        "implementer",
        "guardian",
        "executor",
        "improver",
        "analyzer",
        "learner",
        "orchestrator",
    ]
    
    def __init__(self, name: str, carrier_type: str):
        if carrier_type not in self.CARRIER_TYPES:
            raise ValueError(f"Invalid carrier type: {carrier_type}")
        
        self.id = str(uuid.uuid4())[:12]
        self.name = name
        self.type = carrier_type
        self.state = EntityState.IDLE
        self.capabilities = []
        self.history = []
        self.performance = {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "total_duration": 0,
        }
        self.created_at = datetime.now().isoformat()
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "state": self.state.value,
            "capabilities": self.capabilities,
            "performance": self.performance,
            "history": self.history[-10:],
            "created_at": self.created_at,
        }
    
    def execute(self, task: dict) -> dict:
        self.state = EntityState.RUNNING
        result = {
            "carrier_id": self.id,
            "task": task,
            "started_at": datetime.now().isoformat(),
            "completed_at": None,
            "success": False,
            "output": None,
        }
        
        self.history.append({
            "task_type": task.get("type"),
            "timestamp": result["started_at"],
        })
        
        return result
    
    def complete(self, result: dict, success: bool):
        result["completed_at"] = datetime.now().isoformat()
        result["success"] = success
        self.state = EntityState.COMPLETED if success else EntityState.FAILED
        
        self.performance["tasks_completed" if success else "tasks_failed"] += 1
    
    def get_efficiency(self) -> float:
        total = self.performance["tasks_completed"] + self.performance["tasks_failed"]
        if total == 0:
            return 0.5
        return self.performance["tasks_completed"] / total


class EntityRegistry:
    """Central registry for all cognitive entities"""
    
    def __init__(self):
        self.containers = {}
        self.carriers = {}
        self.blobs = {}
        self.placeholders = {}
        self.registry_file = PROJECT_ROOT / ".paradise" / "entities.json"
        self._load()
    
    def _load(self):
        if self.registry_file.exists():
            try:
                with open(self.registry_file, "r") as f:
                    data = json.load(f)
                    self.containers = {k: Container.from_dict(v) for k, v in data.get("containers", {}).items()}
                    self.carriers = {k: CognitiveCarrier.__new__(CognitiveCarrier) for k in data.get("carriers", {}).keys()}
                    self.blobs = {k: DataBlob(content="") for k in data.get("blobs", {}).keys()}
                    self.placeholders = {k: TaskPlaceholder(name="", expected_type="") for k in data.get("placeholders", {}).keys()}
            except (json.JSONDecodeError, KeyError):
                pass
    
    def _save(self):
        data = {
            "containers": {k: v.to_dict() for k, v in self.containers.items()},
            "carriers": {k: v.to_dict() for k, v in self.carriers.items()},
            "blobs": {k: v.to_dict() for k, v in self.blobs.items()},
            "placeholders": {k: v.to_dict() for k, v in self.placeholders.items()},
            "saved_at": datetime.now().isoformat(),
        }
        with open(self.registry_file, "w") as f:
            json.dump(data, f, indent=2)
    
    def register_container(self, container: Container) -> Container:
        self.containers[container.id] = container
        self._save()
        return container
    
    def register_carrier(self, carrier: CognitiveCarrier) -> CognitiveCarrier:
        self.carriers[carrier.id] = carrier
        self._save()
        return carrier
    
    def register_blob(self, blob: DataBlob) -> DataBlob:
        self.blobs[blob.id] = blob
        self._save()
        return blob
    
    def register_placeholder(self, placeholder: TaskPlaceholder) -> TaskPlaceholder:
        self.placeholders[placeholder.id] = placeholder
        self._save()
        return placeholder
    
    def get_container(self, container_id: str) -> Optional[Container]:
        return self.containers.get(container_id)
    
    def get_carrier(self, carrier_id: str) -> Optional[CognitiveCarrier]:
        return self.carriers.get(carrier_id)
    
    def get_carriers_by_type(self, carrier_type: str) -> list[CognitiveCarrier]:
        return [c for c in self.carriers.values() if c.type == carrier_type]
    
    def get_stats(self) -> dict:
        return {
            "containers": len(self.containers),
            "carriers": len(self.carriers),
            "blobs": len(self.blobs),
            "placeholders": len(self.placeholders),
            "filled_placeholders": sum(1 for p in self.placeholders.values() if p.filled),
        }


_registry = None


def get_registry() -> EntityRegistry:
    global _registry
    if _registry is None:
        _registry = EntityRegistry()
    return _registry


def create_default_carriers() -> list[CognitiveCarrier]:
    carriers = []
    
    carrier_defs = [
        ("planner", "planner", ["planning", "analysis", "architecture"]),
        ("aider", "implementer", ["code_generation", "refactoring", "recursion"]),
        ("guardian", "guardian", ["linting", "security", "quality"]),
        ("executor", "executor", ["testing", "execution", "verification"]),
        ("improver", "improver", ["fixing", "optimization", "learning"]),
        ("orchestrator", "orchestrator", ["coordination", "flow", "monitoring"]),
    ]
    
    for name, ctype, caps in carrier_defs:
        carrier = CognitiveCarrier(name=name, carrier_type=ctype)
        carrier.capabilities = caps
        carriers.append(carrier)
    
    return carriers


def main():
    print("🏗️  Paradise Cognitive Entities")
    print("=" * 40)
    
    registry = get_registry()
    
    print("\n📊 Entity Registry Stats:")
    stats = registry.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\n🚀 Creating Default Carriers...")
    for carrier in create_default_carriers():
        registry.register_carrier(carrier)
        print(f"   ✓ {carrier.name} ({carrier.type})")
    
    print("\n📦 Sample Container:")
    container = Container(name="dev-session", container_type="development")
    container.add_entity("planner")
    container.add_entity("aider")
    registry.register_container(container)
    print(f"   Created: {container.name} with {len(container.entities)} entities")


if __name__ == "__main__":
    main()
