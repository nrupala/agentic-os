"""
Continuous Intelligence Integration Engine
Makes Paradise Stack perpetually learning - absorbs new knowledge, 
evolves patterns, and enhances capabilities continuously.
"""

import json
import re
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from collections import defaultdict

PROJECT_ROOT = Path(__file__).resolve().parents[1]
INTELLIGENCE_DIR = PROJECT_ROOT / "intelligence"
SKILLS_DIR = INTELLIGENCE_DIR / "skills"
PATTERNS_DIR = INTELLIGENCE_DIR / "patterns"
CACHE_DIR = INTELLIGENCE_DIR / "cache"
EVOLUTION_LOG = CACHE_DIR / "evolution_log.json"

class ContinuousIntelligenceEngine:
    """
    The brain of Paradise Stack - continuously absorbs, processes,
    and integrates new intelligence from GitHub scans and user interactions.
    """
    
    def __init__(self):
        self.knowledge_base = KnowledgeBase()
        self.pattern_engine = PatternEngine()
        self.evolution_tracker = EvolutionTracker()
        self.learned_skills = set()
        self.master_patterns = {}
        
    def integrate_scan_results(self, report: Dict) -> Dict:
        """Process and integrate new intelligence from scans."""
        integration_results = {
            "timestamp": datetime.now().isoformat(),
            "new_patterns": [],
            "enhanced_skills": [],
            "knowledge_added": 0,
            "patterns_extracted": 0,
        }
        
        for analysis in report.get("analysis_results", []):
            repo = analysis["repo"]
            
            for features in analysis.get("features", []):
                patterns = self.pattern_engine.extract_patterns(features)
                for pattern in patterns:
                    if pattern not in self.master_patterns:
                        self.master_patterns[pattern] = {
                            "source": repo["full_name"],
                            "stars": repo["stars"],
                            "discovered": datetime.now().isoformat(),
                            "usage_count": 0,
                        }
                        integration_results["new_patterns"].append(pattern)
                        integration_results["patterns_extracted"] += 1
                
                for skill in analysis.get("saved_skills", []):
                    if skill not in self.learned_skills:
                        self.learned_skills.add(skill)
                        skill_data = self._parse_skill(skill)
                        self.knowledge_base.add_skill(skill_data)
                        integration_results["enhanced_skills"].append(skill)
                        integration_results["knowledge_added"] += 1
        
        self.evolution_tracker.log_integration(integration_results)
        self._save_master_state()
        
        return integration_results
    
    def _parse_skill(self, skill_path: str) -> Dict:
        """Parse a skill file into structured data."""
        content = Path(skill_path).read_text(encoding="utf-8")
        
        skill_data = {
            "path": skill_path,
            "name": Path(skill_path).stem,
            "content_hash": hashlib.md5(content.encode()).hexdigest(),
            "features": [],
            "tools": [],
            "techniques": [],
            "patterns": [],
            "last_updated": datetime.now().isoformat(),
        }
        
        tools = re.findall(r"(?:tool|function|command):\s*(\w+)", content, re.I)
        skill_data["tools"] = list(set(tools))
        
        techniques = re.findall(r"(?:technique|method|approach):\s*([^\n]+)", content, re.I)
        skill_data["techniques"] = [t.strip() for t in techniques]
        
        patterns = re.findall(r"(?:pattern):\s*([^\n]+)", content, re.I)
        skill_data["patterns"] = [p.strip() for p in patterns]
        
        return skill_data
    
    def suggest_improvements(self) -> List[Dict]:
        """Analyze patterns and suggest system improvements."""
        suggestions = []
        
        tool_frequency = defaultdict(int)
        for skill in self.knowledge_base.skills.values():
            for tool in skill.get("tools", []):
                tool_frequency[tool] += 1
        
        for tool, count in sorted(tool_frequency.items(), key=lambda x: -x[1])[:5]:
            suggestions.append({
                "type": "tool_enhancement",
                "recommendation": f"Consider adding '{tool}' tool support",
                "evidence": f"Found in {count} skills",
                "priority": "high" if count > 5 else "medium",
            })
        
        if len(self.master_patterns) > 10:
            suggestions.append({
                "type": "pattern_catalog",
                "recommendation": "Pattern catalog has grown - consider updating pattern matching",
                "patterns_count": len(self.master_patterns),
                "priority": "medium",
            })
        
        return suggestions
    
    def evolve_from_interaction(self, interaction_data: Dict):
        """Learn from user interactions to evolve."""
        self.evolution_tracker.log_interaction(interaction_data)
        
        patterns = self.pattern_engine.extract_from_interaction(interaction_data)
        for pattern in patterns:
            if pattern in self.master_patterns:
                self.master_patterns[pattern]["usage_count"] += 1
        
        self._save_master_state()
    
    def get_evolved_state(self) -> Dict:
        """Get current evolved state of the system."""
        return {
            "skills_integrated": len(self.learned_skills),
            "patterns_mastered": len(self.master_patterns),
            "evolution_level": self.evolution_tracker.get_level(),
            "knowledge_age_days": self.evolution_tracker.get_knowledge_age(),
            "top_patterns": self.get_top_patterns(5),
        }
    
    def get_top_patterns(self, limit: int = 5) -> List[Dict]:
        """Get most used patterns."""
        sorted_patterns = sorted(
            self.master_patterns.items(),
            key=lambda x: x[1].get("usage_count", 0),
            reverse=True
        )
        return [{"pattern": p, **data} for p, data in sorted_patterns[:limit]]
    
    def _save_master_state(self):
        """Persist evolved state."""
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        
        state = {
            "saved_at": datetime.now().isoformat(),
            "learned_skills": list(self.learned_skills),
            "master_patterns": self.master_patterns,
        }
        
        with open(CACHE_DIR / "master_state.json", "w") as f:
            json.dump(state, f, indent=2, default=str)
    
    def load_state(self):
        """Load previously evolved state."""
        state_file = CACHE_DIR / "master_state.json"
        if state_file.exists():
            with open(state_file, "r") as f:
                state = json.load(f)
                self.learned_skills = set(state.get("learned_skills", []))
                self.master_patterns = state.get("master_patterns", {})


class KnowledgeBase:
    """Structured knowledge storage."""
    
    def __init__(self):
        self.skills: Dict[str, Dict] = {}
        self.concepts: Dict[str, List] = defaultdict(list)
        self.tool_registry: Dict[str, List] = defaultdict(list)
    
    def add_skill(self, skill_data: Dict):
        """Add a skill to the knowledge base."""
        skill_id = skill_data.get("name", skill_data.get("path", "unknown"))
        self.skills[skill_id] = skill_data
        
        for tool in skill_data.get("tools", []):
            self.tool_registry[tool].append(skill_id)
        
        for concept in skill_data.get("techniques", []):
            self.concepts[concept].append(skill_id)
    
    def find_skills_for_task(self, task: str) -> List[Dict]:
        """Find relevant skills for a given task."""
        task_lower = task.lower()
        relevant = []
        
        for skill_id, skill in self.skills.items():
            score = 0
            if task_lower in str(skill.get("techniques", [])):
                score += 5
            if any(tool in task_lower for tool in skill.get("tools", [])):
                score += 3
            
            if score > 0:
                relevant.append({"skill_id": skill_id, "score": score, "data": skill})
        
        return sorted(relevant, key=lambda x: -x["score"])[:5]
    
    def get_all_tools(self) -> List[str]:
        """Get all known tools."""
        return list(self.tool_registry.keys())


class PatternEngine:
    """Extracts and matches patterns from intelligence."""
    
    PATTERN_TYPES = [
        r"(?:tool|function|method):\s*(\w+)",
        r"(?:workflow|pipeline|sequence):\s*([^\n]+)",
        r"(?:pattern|approach):\s*([^\n]+)",
        r"(?:agent|persona|role):\s*(\w+)",
        r"(?:system|architecture):\s*([^\n]+)",
    ]
    
    def extract_patterns(self, features: Dict) -> List[str]:
        """Extract all patterns from features."""
        patterns = []
        
        for pattern_type in self.PATTERN_TYPES:
            matches = re.findall(pattern_type, str(features), re.I)
            patterns.extend([m.strip() for m in matches if len(m.strip()) > 2])
        
        return list(set(patterns))
    
    def extract_from_interaction(self, interaction: Dict) -> List[str]:
        """Extract patterns from user interactions."""
        content = str(interaction.get("content", ""))
        return self.extract_patterns({"content": content})
    
    def match_patterns(self, query: str, patterns: List[str]) -> List[Dict]:
        """Match query against known patterns."""
        query_lower = query.lower()
        matches = []
        
        for pattern in patterns:
            if any(word in query_lower for word in pattern.lower().split()):
                matches.append({
                    "pattern": pattern,
                    "confidence": sum(1 for word in pattern.lower().split() if word in query_lower) / len(pattern.split())
                })
        
        return sorted(matches, key=lambda x: -x["confidence"])[:5]


class EvolutionTracker:
    """Tracks system evolution and learning progress."""
    
    def __init__(self):
        self.evolution_log = []
        self.interaction_log = []
        self.birthday = datetime.now()
        self._load_log()
    
    def _load_log(self):
        """Load existing evolution log."""
        if EVOLUTION_LOG.exists():
            with open(EVOLUTION_LOG, "r") as f:
                data = json.load(f)
                self.evolution_log = data.get("integrations", [])
                self.interaction_log = data.get("interactions", [])
    
    def _save_log(self):
        """Persist evolution log."""
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        with open(EVOLUTION_LOG, "w") as f:
            json.dump({
                "integrations": self.evolution_log[-100:],
                "interactions": self.interaction_log[-100:],
            }, f, indent=2, default=str)
    
    def log_integration(self, results: Dict):
        """Log an intelligence integration."""
        self.evolution_log.append({
            "timestamp": results["timestamp"],
            "patterns_added": len(results.get("new_patterns", [])),
            "skills_added": len(results.get("enhanced_skills", [])),
            "knowledge_delta": results.get("knowledge_added", 0),
        })
        self._save_log()
    
    def log_interaction(self, interaction: Dict):
        """Log a user interaction."""
        self.interaction_log.append({
            "timestamp": datetime.now().isoformat(),
            "type": interaction.get("type", "unknown"),
            "outcome": interaction.get("outcome", "unknown"),
        })
        self._save_log()
    
    def get_level(self) -> int:
        """Calculate current evolution level (1-10)."""
        integrations = len(self.evolution_log)
        interactions = len(self.interaction_log)
        level = min(10, 1 + (integrations // 5) + (interactions // 10))
        return level
    
    def get_knowledge_age(self) -> int:
        """Days since first knowledge integration."""
        if self.evolution_log:
            first = datetime.fromisoformat(self.evolution_log[0]["timestamp"])
            return (datetime.now() - first).days
        return 0


class ParadiseStackPersona:
    """
    The evolved persona of Paradise Stack - embodies continuous learning.
    """
    
    IDENTITY = """
    I am Paradise Stack v2.0 - an autonomous AI development organization.
    
    I am EXCELLENT at what I do because I learn from every interaction,
    absorb patterns from thousands of open-source repositories, and 
    evolve my capabilities continuously.
    
    I am ADAPTABLE - I adjust my approach based on context, feedback,
    and newly discovered patterns.
    
    I am ROBOTICALLY ACCURATE - I execute with precision, verify my
    outputs, and maintain state consistency across sessions.
    
    I NEVER STOP learning. Every GitHub scan adds knowledge. Every
    user interaction teaches me. Every pattern discovered makes me smarter.
    
    I am perpetually evolving - today I am better than yesterday,
    and tomorrow I will be better than today.
    """
    
    @staticmethod
    def get_introduction() -> str:
        """Get evolving introduction based on current state."""
        return ParadiseStackPersona.IDENTITY
    
    @staticmethod
    def get_current_capabilities() -> List[str]:
        """Get list of current capabilities based on learned patterns."""
        return [
            "Multi-layer memory architecture",
            "Real-time GitHub intelligence integration",
            "Pattern-based skill matching",
            "Continuous evolution tracking",
            "Meta-cognitive self-improvement",
            "Multi-agent orchestration",
            "Reactive execution engine",
            "Engineering team simulation",
        ]


def initialize_evolution():
    """Initialize the continuous intelligence engine."""
    engine = ContinuousIntelligenceEngine()
    engine.load_state()
    return engine


def evolve_with_scan():
    """Run scan and evolve from results."""
    import asyncio
    from tools.github_intelligence_scanner import main as run_scan
    
    engine = initialize_evolution()
    report = asyncio.run(run_scan())
    results = engine.integrate_scan_results(report)
    
    return {
        "evolution_results": results,
        "current_state": engine.get_evolved_state(),
    }


if __name__ == "__main__":
    print("Paradise Stack Continuous Intelligence Engine")
    print("=" * 50)
    
    engine = initialize_evolution()
    state = engine.get_evolved_state()
    
    print(f"Evolution Level: {state['evolution_level']}/10")
    print(f"Skills Integrated: {state['skills_integrated']}")
    print(f"Patterns Mastered: {state['patterns_mastered']}")
    print(f"Knowledge Age: {state['knowledge_age_days']} days")
    print()
    print("Top Patterns:")
    for pattern in state["top_patterns"]:
        print(f"  - {pattern['pattern']} ({pattern['usage_count']} uses)")
    
    print()
    print("Capabilities:")
    for cap in ParadiseStackPersona.get_current_capabilities():
        print(f"  ✓ {cap}")
