"""
Paradise Stack - Cognitive Memory
Persistent knowledge graph, evolving skills, and local cognitive storage.
Learns from every interaction and grows smarter over time.
"""

import json
import time
import hashlib
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Set, Any
from datetime import datetime
from collections import defaultdict

PROJECT_ROOT = Path(__file__).parent.parent.parent
COGNITIVE_DIR = PROJECT_ROOT / ".cognitive"
COGNITIVE_DIR.mkdir(exist_ok=True)

class KnowledgeGraph:
    """
    Persistent knowledge graph that grows with each use.
    Stores concepts, relationships, and learned patterns.
    """
    
    def __init__(self):
        self.nodes_file = COGNITIVE_DIR / "knowledge_nodes.json"
        self.edges_file = COGNITIVE_DIR / "knowledge_edges.json"
        self.nodes: Dict[str, Dict] = self._load(self.nodes_file, {})
        self.edges: List[Dict] = self._load(self.edges_file, [])
        self.dirty = False
        
    def _load(self, path: Path, default):
        if path.exists():
            try:
                return json.loads(path.read_text())
            except:
                pass
        return default
    
    def _save(self):
        if self.dirty:
            self.nodes_file.write_text(json.dumps(self.nodes, indent=2))
            self.edges_file.write_text(json.dumps(self.edges, indent=2))
            self.dirty = False
    
    def add_concept(self, concept: str, category: str = "general", 
                    properties: Dict = None, confidence: float = 0.5):
        """Add a concept to the knowledge graph."""
        node_id = hashlib.md5(concept.lower().encode()).hexdigest()[:12]
        
        if node_id not in self.nodes:
            self.nodes[node_id] = {
                "id": node_id,
                "concept": concept,
                "category": category,
                "properties": properties or {},
                "confidence": confidence,
                "strength": 1,
                "accessed_at": datetime.now().isoformat(),
                "learned_at": datetime.now().isoformat(),
                "access_count": 0,
                "related_to": [],
            }
            self.dirty = True
        
        return node_id
    
    def connect(self, concept1: str, concept2: str, relationship: str = "related"):
        """Connect two concepts."""
        id1 = self.add_concept(concept1)
        id2 = self.add_concept(concept2)
        
        edge_id = f"{id1}_{id2}"
        
        existing = any(e.get("id") == edge_id for e in self.edges)
        if not existing:
            self.edges.append({
                "id": edge_id,
                "from": id1,
                "to": id2,
                "relationship": relationship,
                "strength": 1,
                "created_at": datetime.now().isoformat(),
            })
            self.dirty = True
            
            self.nodes[id1]["related_to"].append(id2)
            self.nodes[id2]["related_to"].append(id1)
    
    def learn(self, text: str, context: str = ""):
        """Learn from text input - extract concepts and connect them."""
        words = text.lower().split()
        
        important = [w for w in words if len(w) > 4 and w.isalpha()]
        
        for i, word in enumerate(important):
            self.add_concept(word, category="learned")
            
            if i > 0:
                prev = important[i-1]
                self.connect(prev, word, "follows_in_text")
        
        if context:
            for word in important[:5]:
                self.add_concept(context, category="context")
                self.connect(word, context)
        
        self._save()
    
    def recall(self, concept: str) -> Optional[Dict]:
        """Recall a concept from memory."""
        concept_lower = concept.lower()
        
        for node_id, node in self.nodes.items():
            if concept_lower in node["concept"].lower():
                node["access_count"] += 1
                node["accessed_at"] = datetime.now().isoformat()
                node["strength"] = min(10, node["strength"] + 0.1)
                self.dirty = True
                self._save()
                return node
        
        return None
    
    def get_related(self, concept: str, max_results: int = 5) -> List[Dict]:
        """Get concepts related to this one."""
        node = self.recall(concept)
        if not node:
            return []
        
        related = []
        for related_id in node.get("related_to", [])[:max_results]:
            if related_id in self.nodes:
                related.append(self.nodes[related_id])
        
        return related
    
    def strengthen(self, concept: str):
        """Increase strength of a concept."""
        node = self.recall(concept)
        if node:
            node["strength"] = min(10, node["strength"] + 0.5)
            node["confidence"] = min(1.0, node["confidence"] + 0.1)
            self.dirty = True
            self._save()
    
    def get_stats(self) -> Dict:
        """Get knowledge graph statistics."""
        categories = defaultdict(int)
        total_strength = 0
        
        for node in self.nodes.values():
            categories[node.get("category", "unknown")] += 1
            total_strength += node.get("strength", 0)
        
        return {
            "total_concepts": len(self.nodes),
            "total_connections": len(self.edges),
            "categories": dict(categories),
            "avg_strength": total_strength / max(1, len(self.nodes)),
            "most_accessed": sorted(
                [(n["concept"], n["access_count"]) for n in self.nodes.values()],
                key=lambda x: x[1], reverse=True
            )[:5],
        }
    
    def export(self) -> Dict:
        """Export entire knowledge graph."""
        return {
            "nodes": self.nodes,
            "edges": self.edges,
            "stats": self.get_stats(),
            "exported_at": datetime.now().isoformat(),
        }


class SkillEvolution:
    """
    Skills that evolve based on usage patterns.
    Learns which approaches work best for which tasks.
    """
    
    def __init__(self):
        self.skills_file = COGNITIVE_DIR / "skills_evolution.json"
        self.skills: Dict[str, Dict] = self._load()
        self.usage_file = COGNITIVE_DIR / "skill_usage.json"
        self.usage: Dict[str, List[Dict]] = self._load_usage()
        
    def _load(self) -> Dict:
        if self.skills_file.exists():
            try:
                return json.loads(self.skills_file.read_text())
            except:
                pass
        return self._default_skills()
    
    def _load_usage(self) -> Dict:
        if self.usage_file.exists():
            try:
                return json.loads(self.usage_file.read_text())
            except:
                pass
        return {}
    
    def _default_skills(self) -> Dict:
        return {
            "code_generation": {
                "name": "Code Generation",
                "level": 1,
                "xp": 0,
                "approaches": [
                    {"name": "template", "success_rate": 0.6, "uses": 10},
                    {"name": "llm_generate", "success_rate": 0.8, "uses": 5},
                ],
                "best_for": [],
            },
            "bug_fixing": {
                "name": "Bug Fixing", 
                "level": 1,
                "xp": 0,
                "approaches": [
                    {"name": "analyze_error", "success_rate": 0.7, "uses": 8},
                    {"name": "auto_fix", "success_rate": 0.5, "uses": 3},
                ],
                "best_for": [],
            },
            "refactoring": {
                "name": "Refactoring",
                "level": 1,
                "xp": 0,
                "approaches": [
                    {"name": "incremental", "success_rate": 0.9, "uses": 6},
                    {"name": "full_rewrite", "success_rate": 0.4, "uses": 2},
                ],
                "best_for": [],
            },
            "planning": {
                "name": "Planning",
                "level": 1,
                "xp": 0,
                "approaches": [
                    {"name": "step_by_step", "success_rate": 0.85, "uses": 12},
                ],
                "best_for": [],
            },
        }
    
    def record_use(self, skill: str, approach: str, success: bool, context: str = ""):
        """Record skill usage and outcome."""
        if skill not in self.skills:
            self.skills[skill] = self._default_skills().get(skill, {
                "name": skill, "level": 1, "xp": 0, "approaches": [], "best_for": []
            })
        
        skill_data = self.skills[skill]
        
        found = False
        for app in skill_data["approaches"]:
            if app["name"] == approach:
                app["uses"] += 1
                if success:
                    app["success_rate"] = (app["success_rate"] * (app["uses"] - 1) + 1) / app["uses"]
                else:
                    app["success_rate"] = (app["success_rate"] * (app["uses"] - 1)) / app["uses"]
                found = True
                break
        
        if not found:
            skill_data["approaches"].append({
                "name": approach,
                "success_rate": 1.0 if success else 0.0,
                "uses": 1,
            })
        
        if success:
            skill_data["xp"] += 10
            if skill_data["xp"] >= skill_data["level"] * 100:
                skill_data["level"] += 1
                skill_data["xp"] = 0
        
        if context and success:
            for kw in context.lower().split()[:3]:
                if kw not in skill_data["best_for"]:
                    skill_data["best_for"].append(kw)
        
        self.skills_file.write_text(json.dumps(self.skills, indent=2))
        
        if skill not in self.usage:
            self.usage[skill] = []
        self.usage[skill].append({
            "approach": approach,
            "success": success,
            "context": context[:50],
            "timestamp": datetime.now().isoformat(),
        })
        self.usage[skill] = self.usage[skill][-100:]
        self.usage_file.write_text(json.dumps(self.usage, indent=2))
    
    def get_best_approach(self, skill: str, context: str = "") -> str:
        """Get the best approach for a skill based on history."""
        if skill not in self.skills:
            return "template"
        
        skill_data = self.skills[skill]
        
        if context:
            for app in skill_data["approaches"]:
                if any(kw in context.lower() for kw in skill_data.get("best_for", [])):
                    return app["name"]
        
        return max(skill_data["approaches"], key=lambda x: x["success_rate"])["name"]
    
    def get_skill_level(self, skill: str) -> int:
        """Get skill level."""
        return self.skills.get(skill, {}).get("level", 1)
    
    def get_stats(self) -> Dict:
        """Get skill evolution statistics."""
        total_xp = sum(s["xp"] for s in self.skills.values())
        avg_level = sum(s["level"] for s in self.skills.values()) / max(1, len(self.skills))
        
        return {
            "skills_count": len(self.skills),
            "total_xp": total_xp,
            "avg_level": round(avg_level, 1),
            "skills": {
                name: {"level": s["level"], "xp": s["xp"], "best": s["approaches"][0]["name"] if s["approaches"] else None}
                for name, s in self.skills.items()
            },
        }


class CognitiveMemory:
    """
    Persistent cognitive memory that stores experiences.
    """
    
    def __init__(self):
        self.memory_file = COGNITIVE_DIR / "cognitive_memory.json"
        self.episodes: List[Dict] = self._load()
        self.patterns_file = COGNITIVE_DIR / "patterns.json"
        self.patterns: Dict[str, Dict] = self._load_patterns()
        
    def _load(self) -> List:
        if self.memory_file.exists():
            try:
                return json.loads(self.memory_file.read_text())
            except:
                pass
        return []
    
    def _load_patterns(self) -> Dict:
        if self.patterns_file.exists():
            try:
                return json.loads(self.patterns_file.read_text())
            except:
                pass
        return {"success_patterns": [], "failure_patterns": []}
    
    def store_episode(self, task: str, result: str, success: bool, 
                      context: Dict = None, files_created: List[str] = None):
        """Store a cognitive episode."""
        episode = {
            "id": len(self.episodes) + 1,
            "task": task,
            "result": result[:500] if result else "",
            "success": success,
            "context": context or {},
            "files_created": files_created or [],
            "timestamp": datetime.now().isoformat(),
            "task_type": self._classify_task(task),
        }
        
        self.episodes.append(episode)
        self.episodes = self.episodes[-1000:]
        
        self.memory_file.write_text(json.dumps(self.episodes, indent=2))
        
        self._update_patterns(episode)
        
        return episode["id"]
    
    def _classify_task(self, task: str) -> str:
        """Classify the task type."""
        task_lower = task.lower()
        
        if any(k in task_lower for k in ["build", "create", "make", "generate"]):
            return "code_generation"
        if any(k in task_lower for k in ["fix", "bug", "error", "issue"]):
            return "bug_fixing"
        if any(k in task_lower for k in ["refactor", "improve", "clean"]):
            return "refactoring"
        if any(k in task_lower for k in ["test", "verify"]):
            return "testing"
        if any(k in task_lower for k in ["explain", "what", "how"]):
            return "explanation"
        if any(k in task_lower for k in ["plan", "design", "architecture"]):
            return "planning"
        
        return "general"
    
    def _update_patterns(self, episode: Dict):
        """Update learned patterns."""
        task_type = episode["task_type"]
        success = episode["success"]
        
        pattern = {
            "task_type": task_type,
            "keywords": episode["task"].lower().split()[:5],
            "files_created": len(episode.get("files_created", [])),
            "timestamp": episode["timestamp"],
        }
        
        if success:
            self.patterns["success_patterns"].append(pattern)
            self.patterns["success_patterns"] = self.patterns["success_patterns"][-100:]
        else:
            self.patterns["failure_patterns"].append(pattern)
            self.patterns["failure_patterns"] = self.patterns["failure_patterns"][-50:]
        
        self.patterns_file.write_text(json.dumps(self.patterns, indent=2))
    
    def recall_similar(self, task: str, limit: int = 5) -> List[Dict]:
        """Recall similar past experiences."""
        task_words = set(task.lower().split())
        similarities = []
        
        for ep in reversed(self.episodes[-100:]):
            ep_words = set(ep["task"].lower().split())
            overlap = len(task_words & ep_words)
            if overlap > 0:
                similarities.append((overlap, ep))
        
        similarities.sort(key=lambda x: x[0], reverse=True)
        return [ep for _, ep in similarities[:limit]]
    
    def get_success_rate(self, task_type: str) -> float:
        """Get success rate for task type."""
        relevant = [e for e in self.episodes if e["task_type"] == task_type]
        if not relevant:
            return 0.5
        
        successes = sum(1 for e in relevant if e["success"])
        return successes / len(relevant)
    
    def get_stats(self) -> Dict:
        """Get memory statistics."""
        return {
            "total_episodes": len(self.episodes),
            "successes": sum(1 for e in self.episodes if e["success"]),
            "failures": sum(1 for e in self.episodes if not e["success"]),
            "success_rate": sum(1 for e in self.episodes if e["success"]) / max(1, len(self.episodes)),
            "task_types": {
                t: sum(1 for e in self.episodes if e["task_type"] == t)
                for t in set(e["task_type"] for e in self.episodes)
            },
            "patterns_learned": len(self.patterns.get("success_patterns", [])),
        }


class CognitiveCore:
    """
    Unified cognitive system combining knowledge graph, skills, and memory.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.knowledge = KnowledgeGraph()
        self.skills = SkillEvolution()
        self.memory = CognitiveMemory()
        self._initialized = True
        self.started_at = datetime.now().isoformat()
    
    def learn(self, task: str, result: str, success: bool, 
              context: Dict = None, files_created: List[str] = None):
        """Learn from an interaction."""
        self.knowledge.learn(task, context=context.get("language", "") if context else "")
        
        task_type = self.memory._classify_task(task)
        approach = context.get("approach", "default") if context else "default"
        
        self.skills.record_use(task_type, approach, success, task)
        
        self.memory.store_episode(task, result, success, context, files_created)
        
        if success:
            for word in task.split()[:3]:
                self.knowledge.strengthen(word)
    
    def think(self, task: str) -> Dict:
        """Think about a task - recall relevant knowledge."""
        similar = self.memory.recall_similar(task)
        related = self.knowledge.get_related(task)
        
        task_type = self.memory._classify_task(task)
        best_approach = self.skills.get_best_approach(task_type, task)
        skill_level = self.skills.get_skill_level(task_type)
        success_rate = self.memory.get_success_rate(task_type)
        
        return {
            "task_type": task_type,
            "best_approach": best_approach,
            "skill_level": skill_level,
            "confidence": success_rate,
            "similar_past": [
                {"task": e["task"], "success": e["success"]}
                for e in similar[:3]
            ],
            "related_knowledge": [
                {"concept": n["concept"], "strength": n["strength"]}
                for n in related[:5]
            ],
            "learned_from": len(similar),
        }
    
    def get_full_status(self) -> Dict:
        """Get complete cognitive status."""
        return {
            "initialized": True,
            "uptime": datetime.now().isoformat(),
            "knowledge_graph": self.knowledge.get_stats(),
            "skills": self.skills.get_stats(),
            "memory": self.memory.get_stats(),
        }
    
    def export_all(self) -> Dict:
        """Export all cognitive data."""
        return {
            "knowledge_graph": self.knowledge.export(),
            "skills": self.skills.skills,
            "memory": {
                "episodes": self.memory.episodes[-100:],
                "patterns": self.memory.patterns,
            },
            "exported_at": datetime.now().isoformat(),
        }
    
    def reset(self):
        """Reset all cognitive data (use with caution)."""
        self.knowledge.nodes = {}
        self.knowledge.edges = []
        self.knowledge._save()
        self.skills.skills = self.skills._default_skills()
        self.skills.skills_file.write_text(json.dumps(self.skills.skills, indent=2))
        self.memory.episodes = []
        self.memory.memory_file.write_text("[]")
        self.memory.patterns = {"success_patterns": [], "failure_patterns": []}
        self.memory.patterns_file.write_text(json.dumps(self.memory.patterns, indent=2))


def get_cognitive_core() -> CognitiveCore:
    """Get the singleton cognitive core."""
    return CognitiveCore()


async def demo():
    """Demo the cognitive system."""
    print("Paradise Cognitive Memory")
    print("=" * 40)
    
    core = get_cognitive_core()
    
    print("\n[1] Learning from tasks...")
    core.learn("Build a REST API", "Created api.py", True, 
               {"language": "python"}, ["api.py"])
    core.learn("Fix the login bug", "Fixed auth error", True,
               {"language": "python"}, [])
    core.learn("Create HTML page", "Created index.html", True,
               {"language": "html"}, ["index.html"])
    
    print("\n[2] Thinking about a new task...")
    thought = core.think("Build a user authentication system")
    print(f"    Task type: {thought['task_type']}")
    print(f"    Best approach: {thought['best_approach']}")
    print(f"    Skill level: {thought['skill_level']}")
    print(f"    Confidence: {thought['confidence']:.0%}")
    print(f"    Learned from similar: {thought['learned_from']} tasks")
    
    print("\n[3] Status...")
    status = core.get_full_status()
    print(f"    Concepts learned: {status['knowledge_graph']['total_concepts']}")
    print(f"    Skills evolved: {status['skills']['skills_count']}")
    print(f"    Memories stored: {status['memory']['total_episodes']}")
    print(f"    Overall success rate: {status['memory']['success_rate']:.0%}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(demo())
