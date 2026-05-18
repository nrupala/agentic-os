#!/usr/bin/env python3
"""
Paradise Self-Improvement Engine - Learning from Experience
Analyzes outcomes, adapts strategies, accumulates knowledge
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional
from collections import defaultdict

PROJECT_ROOT = Path(os.environ.get("HOST_PROJECT_ROOT", "/app"))
MEMORY_DIR = PROJECT_ROOT / ".paradise" / "memory"
MEMORY_DIR.mkdir(parents=True, exist_ok=True)


class Memory:
    """Persistent memory with semantic indexing"""
    
    def __init__(self):
        self.episodes = []
        self.episode_file = MEMORY_DIR / "episodes.json"
        self.embeddings = defaultdict(list)
        self._load()
    
    def _load(self):
        if self.episode_file.exists():
            try:
                with open(self.episode_file, "r") as f:
                    data = json.load(f)
                    self.episodes = data.get("episodes", [])
            except json.JSONDecodeError:
                pass
    
    def _save(self):
        with open(self.episode_file, "w") as f:
            json.dump({"episodes": self.episodes[-100:]}, f, indent=2)
    
    def store_episode(
        self,
        prompt: str,
        actions: list[dict],
        outcome: str,
        success: bool,
        metadata: Optional[dict] = None,
    ):
        episode = {
            "id": len(self.episodes),
            "prompt": prompt,
            "actions": actions,
            "outcome": outcome,
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {},
        }
        self.episodes.append(episode)
        self._save()
        
        for action in actions:
            action_type = action.get("type", "unknown")
            self.embeddings[action_type].append(episode["id"])
        
        return episode
    
    def recall_similar(self, prompt: str, limit: int = 5) -> list[dict]:
        prompt_words = set(prompt.lower().split())
        
        scored = []
        for episode in self.episodes[-50:]:
            episode_words = set(episode["prompt"].lower().split())
            overlap = len(prompt_words & episode_words)
            if overlap > 0:
                scored.append((episode, overlap))
        
        scored.sort(key=lambda x: x[1], reverse=True)
        return [e[0] for e in scored[:limit]]
    
    def get_success_patterns(self) -> dict:
        patterns = defaultdict(lambda: {"success": 0, "failure": 0, "total": 0})
        
        for episode in self.episodes:
            outcome = "success" if episode["success"] else "failure"
            for action in episode.get("actions", []):
                action_type = action.get("type", "unknown")
                patterns[action_type][outcome] += 1
                patterns[action_type]["total"] += 1
        
        return dict(patterns)


class SelfImprover:
    """Analyzes outcomes and improves system behavior"""
    
    def __init__(self):
        self.memory = Memory()
        self.learned_rules = []
        self.rules_file = MEMORY_DIR / "rules.json"
        self.feedback_history = []
        self._load_rules()
    
    def _load_rules(self):
        if self.rules_file.exists():
            try:
                with open(self.rules_file, "r") as f:
                    self.learned_rules = json.load(f)
            except json.JSONDecodeError:
                pass
    
    def _save_rules(self):
        with open(self.rules_file, "w") as f:
            json.dump(self.learned_rules, f, indent=2)
    
    def analyze_outcome(
        self,
        prompt: str,
        actions: list[dict],
        outcome: str,
        success: bool,
    ) -> dict:
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "prompt": prompt,
            "success": success,
            "issues": [],
            "learnings": [],
            "improvements": [],
        }
        
        if not success:
            analysis["issues"].append("Task did not achieve desired outcome")
            
            if len(actions) > 10:
                analysis["issues"].append("Too many iterations - approach may be wrong")
                analysis["improvements"].append("Consider simpler approach")
            
            for action in actions[-3:]:
                if action.get("type") == "fix" and not action.get("success"):
                    analysis["issues"].append("Same fix attempted multiple times")
                    analysis["improvements"].append("Try different strategy")
        
        if success and len(actions) < 5:
            analysis["learnings"].append("Efficient solution found")
            self._add_rule("efficiency", "Quick success indicates good strategy")
        
        self.memory.store_episode(prompt, actions, outcome, success, analysis)
        
        return analysis
    
    def _add_rule(self, rule_type: str, content: str):
        rule = {
            "type": rule_type,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "confidence": 0.5,
        }
        
        for existing in self.learned_rules:
            if existing["content"] == content:
                existing["confidence"] = min(1.0, existing["confidence"] + 0.1)
                self._save_rules()
                return
        
        self.learned_rules.append(rule)
        self._save_rules()
    
    def get_improvements(self, prompt: str) -> list[str]:
        improvements = []
        
        similar = self.memory.recall_similar(prompt)
        for episode in similar:
            if episode["success"]:
                improvements.append(f"Similar task succeeded with: {episode['outcome']}")
        
        patterns = self.memory.get_success_patterns()
        for action_type, stats in patterns.items():
            if stats["success"] / stats["total"] > 0.8:
                improvements.append(f"Action '{action_type}' has {stats['success']/stats['total']:.0%} success rate")
        
        return improvements[:5]
    
    def adapt_strategy(self, current_strategy: dict, feedback: dict) -> dict:
        adapted = current_strategy.copy()
        
        if feedback.get("repetitive_failures"):
            adapted["approach"] = "breakthrough"
            adapted["max_iterations"] = 2
            adapted["fallback"] = "ask_human"
        
        if feedback.get("low_success_rate"):
            adapted["confidence_threshold"] = 0.8
            adapted["steps"].insert(0, "verify_requirements")
        
        return adapted
    
    def get_learning_summary(self) -> dict:
        patterns = self.memory.get_success_patterns()
        return {
            "total_episodes": len(self.memory.episodes),
            "successful_tasks": sum(1 for e in self.memory.episodes if e["success"]),
            "learned_rules": len(self.learned_rules),
            "pattern_success_rates": {
                k: v["success"] / v["total"] if v["total"] > 0 else 0
                for k, v in patterns.items()
            },
        }


class StrategyOptimizer:
    """Optimizes strategies based on historical performance"""
    
    def __init__(self):
        self.strategy_scores = defaultdict(lambda: {"wins": 0, "losses": 0})
        self.strategy_file = MEMORY_DIR / "strategies.json"
        self._load()
    
    def _load(self):
        if self.strategy_file.exists():
            try:
                with open(self.strategy_file, "r") as f:
                    self.strategy_scores = defaultdict(
                        lambda: {"wins": 0, "losses": 0},
                        json.load(f),
                    )
            except json.JSONDecodeError:
                pass
    
    def _save(self):
        with open(self.strategy_file, "w") as f:
            json.dump(dict(self.strategy_scores), f, indent=2)
    
    def record_outcome(self, strategy: str, success: bool):
        if success:
            self.strategy_scores[strategy]["wins"] += 1
        else:
            self.strategy_scores[strategy]["losses"] += 1
        self._save()
    
    def get_best_strategy(self, context: str = "default") -> Optional[str]:
        best = None
        best_score = -1
        
        for strategy, scores in self.strategy_scores.items():
            total = scores["wins"] + scores["losses"]
            if total >= 3:
                win_rate = scores["wins"] / total
                if win_rate > best_score:
                    best_score = win_rate
                    best = strategy
        
        return best
    
    def get_all_strategies(self) -> list[dict]:
        results = []
        for strategy, scores in self.strategy_scores.items():
            total = scores["wins"] + scores["losses"]
            results.append({
                "strategy": strategy,
                "wins": scores["wins"],
                "losses": scores["losses"],
                "total": total,
                "win_rate": scores["wins"] / total if total > 0 else 0,
            })
        
        results.sort(key=lambda x: x["win_rate"], reverse=True)
        return results


class ImprovementLoop:
    """The core self-improvement feedback loop"""
    
    def __init__(self):
        self.memory = Memory()
        self.improver = SelfImprover()
        self.optimizer = StrategyOptimizer()
        self.iteration_count = 0
        self.max_iterations = 10
    
    def run(
        self,
        prompt: str,
        executor_func,
        check_func,
    ) -> dict:
        results = {
            "prompt": prompt,
            "iterations": [],
            "final_outcome": None,
            "success": False,
        }
        
        actions = []
        user_satisfied = False
        
        while self.iteration_count < self.max_iterations and not user_satisfied:
            self.iteration_count += 1
            
            action = executor_func(prompt, iteration=self.iteration_count)
            actions.append(action)
            
            check_result = check_func(action)
            
            analysis = self.improver.analyze_outcome(
                prompt=prompt,
                actions=actions,
                outcome=str(check_result.get("outcome", "unknown")),
                success=check_result.get("success", False),
            )
            
            results["iterations"].append({
                "iteration": self.iteration_count,
                "action": action,
                "check": check_result,
                "analysis": analysis,
            })
            
            self.optimizer.record_outcome(
                f"iteration_{self.iteration_count}",
                check_result.get("success", False),
            )
            
            if check_result.get("success") and check_result.get("user_satisfied"):
                user_satisfied = True
                results["success"] = True
                results["final_outcome"] = check_result.get("outcome")
            
            if check_result.get("give_up"):
                break
        
        results["total_iterations"] = self.iteration_count
        return results
    
    def should_continue(self, iteration: int, issues: list) -> bool:
        if iteration >= self.max_iterations:
            return False
        
        if not issues:
            return True
        
        if self._is_stuck_in_loop(issues):
            return False
        
        return True
    
    def _is_stuck_in_loop(self, issues: list) -> bool:
        if len(issues) < 3:
            return False
        
        recent = issues[-3:]
        if all(i.get("type") == recent[0].get("type") for i in recent):
            return True
        
        return False


_instance = None


def get_memory() -> Memory:
    global _instance
    if _instance is None:
        _instance = Memory()
    return _instance


def get_self_improver() -> SelfImprover:
    return SelfImprover()


def get_optimizer() -> StrategyOptimizer:
    return StrategyOptimizer()


def get_loop() -> ImprovementLoop:
    return ImprovementLoop()


def main():
    print("🔧 Paradise Self-Improvement Engine")
    print("=" * 40)
    
    memory = get_memory()
    improver = get_self_improver()
    optimizer = get_optimizer()
    
    print("\n📊 Learning Summary:")
    summary = improver.get_learning_summary()
    print(f"   Total Episodes: {summary['total_episodes']}")
    print(f"   Successful Tasks: {summary['successful_tasks']}")
    print(f"   Learned Rules: {summary['learned_rules']}")
    
    print("\n📈 Strategy Performance:")
    for strategy in optimizer.get_all_strategies()[:5]:
        print(f"   {strategy['strategy']}: {strategy['win_rate']:.0%} ({strategy['wins']}W/{strategy['losses']}L)")
    
    print("\n💡 Recent Improvements:")
    improvements = improver.get_improvements("create api")
    for imp in improvements:
        print(f"   • {imp}")


if __name__ == "__main__":
    main()
