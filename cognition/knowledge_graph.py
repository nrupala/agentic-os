#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
# Copyright 2026 agentic-OS Contributors

"""
Paradise Knowledge Graph - Persistent Learning & Memory System
Graph-based knowledge storage with relationship tracking
"""

import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
from collections import defaultdict
import threading

PROJECT_ROOT = Path(os.environ.get("HOST_PROJECT_ROOT", "/app"))
GRAPH_DIR = PROJECT_ROOT / ".paradise" / "knowledge"
GRAPH_DIR.mkdir(parents=True, exist_ok=True)


class Blob:
    """Atomic knowledge unit - smallest irreducible piece of information"""
    
    def __init__(
        self,
        content: Any,
        blob_type: str = "generic",
        source: str = "system",
        tags: Optional[list] = None,
        confidence: float = 1.0,
        blob_id: Optional[str] = None,
    ):
        self.id = blob_id or str(uuid.uuid4())[:12]
        self.content = content
        self.type = blob_type
        self.source = source
        self.tags = tags or []
        self.confidence = confidence
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
        self.access_count = 0
        self.utility_score = 1.0
    
    def to_dict(self):
        return {
            "id": self.id,
            "content": self.content,
            "type": self.type,
            "source": self.source,
            "tags": self.tags,
            "confidence": self.confidence,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "access_count": self.access_count,
            "utility_score": self.utility_score,
        }
    
    @classmethod
    def from_dict(cls, data):
        blob = cls(
            content=data["content"],
            blob_type=data.get("type", "generic"),
            source=data.get("source", "system"),
            tags=data.get("tags", []),
            confidence=data.get("confidence", 1.0),
            blob_id=data.get("id"),
        )
        blob.created_at = data.get("created_at", blob.created_at)
        blob.updated_at = data.get("updated_at", blob.created_at)
        blob.access_count = data.get("access_count", 0)
        blob.utility_score = data.get("utility_score", 1.0)
        return blob
    
    def access(self):
        self.access_count += 1
        self.updated_at = datetime.now().isoformat()
        return self
    
    def update_utility(self, delta: float):
        self.utility_score = max(0.0, min(1.0, self.utility_score + delta))


class Entity:
    """Core object in the knowledge graph - can be concepts, solutions, patterns, tasks"""
    
    def __init__(
        self,
        name: str,
        entity_type: str,
        description: str = "",
        properties: Optional[dict] = None,
        entity_id: Optional[str] = None,
    ):
        self.id = entity_id or str(uuid.uuid4())[:12]
        self.name = name
        self.type = entity_type
        self.description = description
        self.properties = properties or {}
        self.blobs = []
        self.relationships = []
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
        self.success_count = 0
        self.failure_count = 0
        self.last_used = None
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "description": self.description,
            "properties": self.properties,
            "blobs": [b.to_dict() if isinstance(b, Blob) else b for b in self.blobs],
            "relationships": self.relationships,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "last_used": self.last_used,
        }
    
    @classmethod
    def from_dict(cls, data):
        entity = cls(
            name=data["name"],
            entity_type=data["type"],
            description=data.get("description", ""),
            properties=data.get("properties", {}),
            entity_id=data.get("id"),
        )
        entity.blobs = [Blob.from_dict(b) if isinstance(b, dict) else b for b in data.get("blobs", [])]
        entity.relationships = data.get("relationships", [])
        entity.created_at = data.get("created_at", entity.created_at)
        entity.updated_at = data.get("updated_at", entity.created_at)
        entity.success_count = data.get("success_count", 0)
        entity.failure_count = data.get("failure_count", 0)
        entity.last_used = data.get("last_used")
        return entity
    
    def add_blob(self, blob: Blob):
        self.blobs.append(blob)
        self.updated_at = datetime.now().isoformat()
    
    def add_relationship(self, target_id: str, relationship_type: str, weight: float = 1.0):
        rel = {
            "target": target_id,
            "type": relationship_type,
            "weight": weight,
            "created_at": datetime.now().isoformat(),
        }
        for r in self.relationships:
            if r["target"] == target_id and r["type"] == relationship_type:
                r["weight"] = max(r["weight"], weight)
                return
        self.relationships.append(rel)
        self.updated_at = datetime.now().isoformat()
    
    def record_success(self):
        self.success_count += 1
        self.last_used = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
    
    def record_failure(self):
        self.failure_count += 1
        self.last_used = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
    
    def success_rate(self) -> float:
        total = self.success_count + self.failure_count
        return self.success_count / total if total > 0 else 0.5


class Carrier:
    """Agent/process that transports information and executes tasks"""
    
    def __init__(
        self,
        name: str,
        carrier_type: str = "generic",
        capabilities: Optional[list] = None,
        state: Optional[dict] = None,
    ):
        self.id = str(uuid.uuid4())[:12]
        self.name = name
        self.type = carrier_type
        self.capabilities = capabilities or []
        self.state = state or {}
        self.history = []
        self.created_at = datetime.now().isoformat()
        self.performance_score = 0.5
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "capabilities": self.capabilities,
            "state": self.state,
            "history": self.history,
            "created_at": self.created_at,
            "performance_score": self.performance_score,
        }
    
    @classmethod
    def from_dict(cls, data):
        carrier = cls(
            name=data["name"],
            carrier_type=data.get("type", "generic"),
            capabilities=data.get("capabilities", []),
            state=data.get("state", {}),
        )
        carrier.id = data.get("id", carrier.id)
        carrier.history = data.get("history", [])
        carrier.created_at = data.get("created_at", carrier.created_at)
        carrier.performance_score = data.get("performance_score", 0.5)
        return carrier
    
    def execute(self, task: dict) -> dict:
        result = {
            "carrier_id": self.id,
            "task": task,
            "started_at": datetime.now().isoformat(),
            "completed_at": None,
            "success": False,
            "output": None,
            "errors": [],
        }
        
        self.history.append({"task": task.get("type", "unknown"), "timestamp": result["started_at"]})
        self.state["last_execution"] = result["started_at"]
        
        return result
    
    def update_performance(self, score: float):
        alpha = 0.1
        self.performance_score = alpha * score + (1 - alpha) * self.performance_score


class Placeholder:
    """Reserved slot for future content - allows incomplete structures to be defined"""
    
    def __init__(
        self,
        name: str,
        placeholder_type: str,
        expected_type: str = "unknown",
        constraints: Optional[dict] = None,
        filled: bool = False,
    ):
        self.id = str(uuid.uuid4())[:12]
        self.name = name
        self.type = placeholder_type
        self.expected_type = expected_type
        self.constraints = constraints or {}
        self.filled = filled
        self.filled_by = None
        self.filled_at = None
        self.created_at = datetime.now().isoformat()
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "expected_type": self.expected_type,
            "constraints": self.constraints,
            "filled": self.filled,
            "filled_by": self.filled_by,
            "filled_at": self.filled_at,
            "created_at": self.created_at,
        }
    
    @classmethod
    def from_dict(cls, data):
        ph = cls(
            name=data["name"],
            placeholder_type=data.get("type", "generic"),
            expected_type=data.get("expected_type", "unknown"),
            constraints=data.get("constraints", {}),
            filled=data.get("filled", False),
        )
        ph.id = data.get("id", ph.id)
        ph.filled_by = data.get("filled_by")
        ph.filled_at = data.get("filled_at")
        ph.created_at = data.get("created_at", ph.created_at)
        return ph
    
    def fill(self, content: Any, source_id: str):
        self.filled = True
        self.filled_by = source_id
        self.filled_at = datetime.now().isoformat()
        self.constraints["actual_content"] = str(content)[:500]
    
    def is_valid(self) -> bool:
        if not self.filled:
            return True
        return self.constraints.get("actual_content") is not None


class KnowledgeGraph:
    """Persistent knowledge graph with entities, relationships, and learned patterns"""
    
    def __init__(self):
        self.lock = threading.RLock()
        self.entities = {}
        self.blobs = {}
        self.carriers = {}
        self.placeholders = {}
        self.graph_file = GRAPH_DIR / "knowledge_graph.json"
        self.stats = {
            "total_entities": 0,
            "total_blobs": 0,
            "total_queries": 0,
            "successful_tasks": 0,
            "failed_tasks": 0,
            "learned_patterns": 0,
        }
        self._load()
    
    def _load(self):
        if self.graph_file.exists():
            try:
                with open(self.graph_file, "r") as f:
                    data = json.load(f)
                    self.entities = {k: Entity.from_dict(v) for k, v in data.get("entities", {}).items()}
                    self.blobs = {k: Blob.from_dict(v) for k, v in data.get("blobs", {}).items()}
                    self.carriers = {k: Carrier.from_dict(v) for k, v in data.get("carriers", {}).items()}
                    self.placeholders = {k: Placeholder.from_dict(v) for k, v in data.get("placeholders", {}).items()}
                    self.stats = data.get("stats", self.stats)
            except (json.JSONDecodeError, KeyError):
                pass
    
    def _save(self):
        with self.lock:
            data = {
                "entities": {k: v.to_dict() for k, v in self.entities.items()},
                "blobs": {k: v.to_dict() for k, v in self.blobs.items()},
                "carriers": {k: v.to_dict() for k, v in self.carriers.items()},
                "placeholders": {k: v.to_dict() for k, v in self.placeholders.items()},
                "stats": self.stats,
                "saved_at": datetime.now().isoformat(),
            }
            with open(self.graph_file, "w") as f:
                json.dump(data, f, indent=2)
    
    def add_entity(self, entity: Entity) -> Entity:
        with self.lock:
            self.entities[entity.id] = entity
            self.stats["total_entities"] = len(self.entities)
            self._save()
        return entity
    
    def add_blob(self, blob: Blob) -> Blob:
        with self.lock:
            self.blobs[blob.id] = blob
            self.stats["total_blobs"] = len(self.blobs)
            self._save()
        return blob
    
    def add_carrier(self, carrier: Carrier) -> Carrier:
        with self.lock:
            self.carriers[carrier.id] = carrier
            self._save()
        return carrier
    
    def add_placeholder(self, placeholder: Placeholder) -> Placeholder:
        with self.lock:
            self.placeholders[placeholder.id] = placeholder
            self._save()
        return placeholder
    
    def get_entity(self, entity_id: str) -> Optional[Entity]:
        with self.lock:
            return self.entities.get(entity_id)
    
    def get_entity_by_name(self, name: str, entity_type: Optional[str] = None) -> Optional[Entity]:
        with self.lock:
            for entity in self.entities.values():
                if entity.name.lower() == name.lower():
                    if entity_type is None or entity.type == entity_type:
                        return entity
        return None
    
    def find_related(self, entity_id: str, relationship_type: Optional[str] = None) -> list[Entity]:
        with self.lock:
            entity = self.entities.get(entity_id)
            if not entity:
                return []
            
            related = []
            for rel in entity.relationships:
                if relationship_type is None or rel["type"] == relationship_type:
                    target = self.entities.get(rel["target"])
                    if target:
                        related.append(target)
            return related
    
    def learn_from_success(
        self,
        task_type: str,
        approach: str,
        outcome: dict,
        details: Optional[dict] = None,
    ):
        entity = self.get_entity_by_name(approach, "pattern")
        if entity:
            entity.record_success()
        else:
            entity = Entity(
                name=approach,
                entity_type="pattern",
                description=f"Successful approach for {task_type}",
                properties={
                    "task_type": task_type,
                    "approach": approach,
                    "outcome": outcome,
                    "details": details or {},
                },
            )
            entity.record_success()
            self.add_entity(entity)
        
        self.stats["successful_tasks"] += 1
        self.stats["learned_patterns"] = len(
            [e for e in self.entities.values() if e.type == "pattern"]
        )
        self._save()
    
    def learn_from_failure(
        self,
        task_type: str,
        approach: str,
        error: str,
        details: Optional[dict] = None,
    ):
        entity = self.get_entity_by_name(approach, "pattern")
        if entity:
            entity.record_failure()
        else:
            entity = Entity(
                name=approach,
                entity_type="pattern",
                description=f"Failed approach for {task_type}",
                properties={
                    "task_type": task_type,
                    "approach": approach,
                    "error": error,
                    "details": details or {},
                },
            )
            entity.record_failure()
            self.add_entity(entity)
        
        self.stats["failed_tasks"] += 1
        self._save()
    
    def get_best_pattern(self, task_type: str) -> Optional[Entity]:
        with self.lock:
            candidates = []
            for entity in self.entities.values():
                if entity.type == "pattern" and entity.properties.get("task_type") == task_type:
                    candidates.append(entity)
            
            if not candidates:
                return None
            
            candidates.sort(key=lambda e: e.success_rate(), reverse=True)
            return candidates[0]
    
    def get_recent_learning(self, limit: int = 10) -> list[dict]:
        with self.lock:
            entities = sorted(
                self.entities.values(),
                key=lambda e: e.updated_at,
                reverse=True,
            )
            return [
                {
                    "name": e.name,
                    "type": e.type,
                    "success_rate": e.success_rate(),
                    "last_used": e.last_used,
                }
                for e in entities[:limit]
            ]
    
    def get_stats(self) -> dict:
        with self.lock:
            return {
                **self.stats,
                "entity_types": defaultdict(int),
                "pattern_success_rate": 0.0,
            }
    
    def query(self, query_text: str) -> list[dict]:
        with self.lock:
            self.stats["total_queries"] += 1
            query_lower = query_text.lower()
            
            results = []
            for entity in self.entities.values():
                score = 0
                if query_lower in entity.name.lower():
                    score += 10
                if query_lower in entity.description.lower():
                    score += 5
                if any(query_lower in str(b.content).lower() for b in entity.blobs):
                    score += 3
                
                if score > 0:
                    results.append({"entity": entity, "score": score})
            
            results.sort(key=lambda x: x["score"], reverse=True)
            self._save()
            return results[:10]
    
    def create_solution_entity(
        self,
        name: str,
        solution_type: str,
        files: list[str],
        plan: str,
        success: bool,
    ) -> Entity:
        entity = Entity(
            name=name,
            entity_type="solution",
            description=f"{solution_type} solution",
            properties={
                "solution_type": solution_type,
                "files": files,
                "plan": plan[:1000] if plan else "",
                "success": success,
            },
        )
        
        blob = Blob(
            content=plan,
            blob_type="plan",
            source="planner",
            tags=[solution_type, "plan"],
        )
        entity.add_blob(blob)
        
        if success:
            entity.record_success()
        
        return self.add_entity(entity)
    
    def add_learning(
        self,
        concept: str,
        content: str,
        category: str = "general",
        metadata: Optional[dict] = None,
    ) -> Blob:
        blob = Blob(
            content=content,
            blob_type=category,
            source="learning",
            tags=[category, concept],
        )
        
        entity = self.get_entity_by_name(concept)
        if entity:
            entity.add_blob(blob)
        else:
            entity = Entity(
                name=concept,
                entity_type="concept",
                description=f"Learned {category}: {concept}",
                properties=metadata or {},
            )
            entity.add_blob(blob)
            self.add_entity(entity)
        
        return blob


_graph_instance = None


def get_graph() -> KnowledgeGraph:
    global _graph_instance
    if _graph_instance is None:
        _graph_instance = KnowledgeGraph()
    return _graph_instance


def main():
    print("🧠 Paradise Knowledge Graph")
    print("=" * 40)
    
    graph = get_graph()
    
    print("\n📊 Stats:")
    print(f"   Entities: {graph.stats['total_entities']}")
    print(f"   Blobs: {graph.stats['total_blobs']}")
    print(f"   Successful tasks: {graph.stats['successful_tasks']}")
    print(f"   Failed tasks: {graph.stats['failed_tasks']}")
    
    print("\n📚 Recent Learning:")
    for learning in graph.get_recent_learning(5):
        print(f"   - {learning['name']} ({learning['type']})")
        print(f"     Success rate: {learning['success_rate']:.1%}")


if __name__ == "__main__":
    main()
