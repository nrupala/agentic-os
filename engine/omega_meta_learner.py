#!/usr/bin/env python3
"""
OMEGA Recursive Meta-Learning Engine
=====================================
Enhanced recursive feedback loop with meta-learning.
Inspired by:
- SICA: Self-Improving Coding Agent
- STOP: Self-Taught Optimizer
- Darwin Gödel Machine (DGM)

Features:
- Meta-improvement loop that learns to learn better
- Strategy selection based on past performance
- Continuous optimization of reasoning strategies
- Self-tuned hyperparameters
"""

import os
import sys
import json
import sqlite3
import hashlib
import time
from pathlib import Path
from typing import Dict, Optional, List, Any, Tuple
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

PROJECT_ROOT = Path(__file__).parent.parent
ENGINE_DIR = PROJECT_ROOT / "engine"

def _get_encryptor():
    """Lazy-load encryption module."""
    try:
        from omega_phase_encryptor import OmegaPhaseEncryptor
        return OmegaPhaseEncryptor("meta_learner")
    except ImportError:
        return None

_ENCRYPTOR = None

@dataclass
class Strategy:
    strategy_id: str
    name: str
    description: str
    success_rate: float
    usage_count: int
    avg_execution_time: float
    last_used: str
    parameters: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MetaAttempt:
    attempt_id: str
    goal: str
    strategy_id: str
    result: str
    success: bool
    execution_time: float
    timestamp: str

@dataclass
class MetaLearnedRule:
    rule_id: str
    trigger: str
    action: str
    confidence: float
    success_count: int
    failure_count: int
    created_at: str

class StrategySelector:
    """Selects best strategy based on meta-learning."""
    
    def __init__(self):
        self.strategies: Dict[str, Strategy] = {}
        self.load_strategies()
    
    def load_strategies(self):
        """Load strategies from encrypted storage."""
        global _ENCRYPTOR
        storage_path = PROJECT_ROOT / "projects" / "omega" / "state"
        storage_path.mkdir(parents=True, exist_ok=True)

        strategies_file = storage_path / "meta_strategies.json"
        strategies_file_enc = storage_path / "meta_strategies.enc"

        if _ENCRYPTOR is None:
            _ENCRYPTOR = _get_encryptor()

        if _ENCRYPTOR and strategies_file_enc.exists():
            try:
                decrypted = _ENCRYPTOR.decrypt_string("strategies")
                data = json.loads(decrypted)
                self.strategies = {k: Strategy(**v) for k, v in data.items()}
                return
            except Exception:
                pass

        if strategies_file.exists():
            try:
                data = json.loads(strategies_file.read_text())
                self.strategies = {k: Strategy(**v) for k, v in data.items()}
            except:
                pass
    
    def save_strategies(self):
        """Save strategies to storage with encryption."""
        global _ENCRYPTOR
        storage_path = PROJECT_ROOT / "projects" / "omega" / "state"
        storage_path.mkdir(parents=True, exist_ok=True)
        strategies_file = storage_path / "meta_strategies.json"

        data = json.dumps({k: asdict(v) for k, v in self.strategies.items()}, indent=2)

        if _ENCRYPTOR is None:
            _ENCRYPTOR = _get_encryptor()

        if _ENCRYPTOR:
            try:
                _ENCRYPTOR.encrypt_memory({"strategies": data}, "strategies")
                strategies_file.write_text(data)
                return
            except Exception:
                pass

        strategies_file.write_text(data)
    
    def select_strategy(self, context: Dict) -> Strategy:
        """Select the best strategy based on context and past performance."""
        
        if not self.strategies:
            self._initialize_default_strategies()
        
        goal_type = context.get("goal_type", "general")
        
        candidates = []
        for sid, strategy in self.strategies.items():
            if goal_type in strategy.parameters.get("applicable_to", ["general"]):
                score = self._calculate_strategy_score(strategy, context)
                candidates.append((sid, score))
        
        candidates.sort(key=lambda x: x[1], reverse=True)
        
        selected_id = candidates[0][0] if candidates else "default"
        
        strategy = self.strategies.get(selected_id, self.strategies["default"])
        strategy.usage_count += 1
        strategy.last_used = datetime.now().isoformat()
        self.save_strategies()
        
        return strategy
    
    def _calculate_strategy_score(self, strategy: Strategy, context: Dict) -> float:
        """Calculate strategy score based on performance and context."""
        
        success_weight = 0.5
        speed_weight = 0.2
        recency_weight = 0.2
        confidence_weight = 0.1
        
        success_score = strategy.success_rate
        
        if strategy.avg_execution_time > 0:
            speed_score = min(60.0 / strategy.avg_execution_time, 1.0)
        else:
            speed_score = 0.5
        
        if strategy.last_used:
            try:
                last = datetime.fromisoformat(strategy.last_used)
                hours_ago = (datetime.now() - last).total_seconds() / 3600
                recency_score = max(0, 1 - hours_ago / 168)
            except:
                recency_score = 0.5
        else:
            recency_score = 0.5
        
        confidence_score = strategy.success_rate
        
        score = (
            success_weight * success_score +
            speed_weight * speed_score +
            recency_weight * recency_score +
            confidence_weight * confidence_score
        )
        
        return score
    
    def _initialize_default_strategies(self):
        """Initialize default strategies."""
        self.strategies = {
            "default": Strategy(
                strategy_id="default",
                name="Default Generation",
                description="Standard code generation approach",
                success_rate=0.5,
                usage_count=0,
                avg_execution_time=0,
                last_used="",
                parameters={"applicable_to": ["general"]}
            ),
            "recursive_refine": Strategy(
                strategy_id="recursive_refine",
                name="Recursive Refinement",
                description="Iterative refinement with self-correction",
                success_rate=0.65,
                usage_count=0,
                avg_execution_time=0,
                last_used="",
                parameters={"applicable_to": ["complex", "refactor"], "max_iterations": 5}
            ),
            "test_first": Strategy(
                strategy_id="test_first",
                name="Test-First Development",
                description="Write tests before implementation",
                success_rate=0.7,
                usage_count=0,
                avg_execution_time=0,
                last_used="",
                parameters={"applicable_to": ["bug_fix", "feature"]}
            ),
            "scaffold": Strategy(
                strategy_id="scaffold",
                name="Scaffold and Implement",
                description="Build scaffold then fill in details",
                success_rate=0.6,
                usage_count=0,
                avg_execution_time=0,
                last_used="",
                parameters={"applicable_to": ["api", "web_server"]}
            ),
            "template_match": Strategy(
                strategy_id="template_match",
                name="Template Matching",
                description="Match and adapt from known patterns",
                success_rate=0.75,
                usage_count=0,
                avg_execution_time=0,
                last_used="",
                parameters={"applicable_to": ["boilerplate", "config", "cli"]}
            )
        }
        self.save_strategies()
    
    def update_strategy_performance(self, strategy_id: str, success: bool, execution_time: float):
        """Update strategy performance metrics."""
        
        if strategy_id in self.strategies:
            strategy = self.strategies[strategy_id]
            
            old_count = strategy.usage_count
            old_rate = strategy.success_rate
            
            new_count = old_count + 1
            new_rate = (old_rate * old_count + (1.0 if success else 0.0)) / new_count
            
            strategy.success_rate = new_rate
            strategy.usage_count = new_count
            
            if strategy.avg_execution_time > 0:
                strategy.avg_execution_time = (strategy.avg_execution_time * (new_count - 1) + execution_time) / new_count
            else:
                strategy.avg_execution_time = execution_time
            
            self.save_strategies()


class RecursiveMetaLearner:
    """
    Recursive Meta-Learning Engine
    =============================
    Learns to improve its own learning process.
    """
    
    VERSION = "2.0.0"
    
    def __init__(self, project: str = "omega"):
        self.project = project
        self.db_path = f"projects/{project}/state/omega_state.db"
        
        self.strategy_selector = StrategySelector()
        
        self.attempts: List[MetaAttempt] = []
        self.rules: Dict[str, MetaLearnedRule] = {}
        
        self.max_recursion_depth = 10
        self.convergence_threshold = 0.95
        
        self._init_storage()
        self._load_rules()
        
        print(f"[META-LEARN] Recursive Meta-Learner v{self.VERSION} initialized")
    
    def _init_storage(self):
        """Initialize storage."""
        global _ENCRYPTOR
        if _ENCRYPTOR is None:
            _ENCRYPTOR = _get_encryptor()

        storage_path = Path(f"projects/{self.project}/state")
        storage_path.mkdir(parents=True, exist_ok=True)

        attempts_file = storage_path / "meta_attempts.json"
        attempts_file_enc = storage_path / "meta_attempts.enc"

        if _ENCRYPTOR and attempts_file_enc.exists():
            try:
                decrypted = _ENCRYPTOR.decrypt_string("attempts")
                data = json.loads(decrypted)
                self.attempts = [MetaAttempt(**a) for a in data]
                return
            except Exception:
                pass

        if attempts_file.exists():
            try:
                data = json.loads(attempts_file.read_text())
                self.attempts = [MetaAttempt(**a) for a in data]
            except:
                self.attempts = []
    
    def _save_attempts(self):
        """Save attempts to encrypted storage."""
        global _ENCRYPTOR
        storage_path = Path(f"projects/{self.project}/state")
        storage_path.mkdir(parents=True, exist_ok=True)
        attempts_file = storage_path / "meta_attempts.json"
        attempts_file_enc = storage_path / "meta_attempts.enc"

        data = json.dumps([asdict(a) for a in self.attempts], indent=2)

        if _ENCRYPTOR is None:
            _ENCRYPTOR = _get_encryptor()

        if _ENCRYPTOR:
            try:
                _ENCRYPTOR.encrypt_string(data, "attempts")
                return
            except Exception:
                pass

        attempts_file.write_text(data)
    
    def _load_rules(self):
        """Load learned rules from encrypted storage."""
        global _ENCRYPTOR
        storage_path = Path(f"projects/{self.project}/state")
        storage_path.mkdir(parents=True, exist_ok=True)
        rules_file = storage_path / "meta_rules.json"
        rules_file_enc = storage_path / "meta_rules.enc"

        if _ENCRYPTOR is None:
            _ENCRYPTOR = _get_encryptor()

        if _ENCRYPTOR and rules_file_enc.exists():
            try:
                decrypted = _ENCRYPTOR.decrypt_string("rules")
                data = json.loads(decrypted)
                self.rules = {k: MetaLearnedRule(**v) for k, v in data.items()}
                return
            except Exception:
                pass

        if rules_file.exists():
            try:
                data = json.loads(rules_file.read_text())
                self.rules = {k: MetaLearnedRule(**v) for k, v in data.items()}
            except:
                self.rules = {}
    
    def _save_rules(self):
        """Save rules to encrypted storage."""
        global _ENCRYPTOR
        storage_path = Path(f"projects/{self.project}/state")
        storage_path.mkdir(parents=True, exist_ok=True)
        rules_file = storage_path / "meta_rules.json"
        rules_file_enc = storage_path / "meta_rules.enc"

        data = json.dumps({k: asdict(v) for k, v in self.rules.items()}, indent=2)

        if _ENCRYPTOR is None:
            _ENCRYPTOR = _get_encryptor()

        if _ENCRYPTOR:
            try:
                _ENCRYPTOR.encrypt_string(data, "rules")
                return
            except Exception:
                pass

        rules_file.write_text(data)
    
    def determine_goal_type(self, goal: str) -> str:
        """Classify goal type for strategy selection."""
        goal_lower = goal.lower()
        
        if any(x in goal_lower for x in ["fix", "bug", "error", "crash", "issue"]):
            return "bug_fix"
        elif any(x in goal_lower for x in ["refactor", "improve", "optimize", "clean"]):
            return "refactor"
        elif any(x in goal_lower for x in ["create", "new", "build", "implement", "add"]):
            return "feature"
        elif any(x in goal_lower for x in ["api", "endpoint", "rest", "service"]):
            return "api"
        elif any(x in goal_lower for x in ["web", "server", "http"]):
            return "web_server"
        elif any(x in goal_lower for x in ["test", "spec", "verify"]):
            return "test"
        else:
            return "general"
    
    def execute_with_meta_learning(self, goal: str, max_attempts: int = 10) -> Dict:
        """Execute goal with meta-learning guided strategy."""
        
        start_time = time.time()
        
        goal_type = self.determine_goal_type(goal)
        context = {"goal": goal, "goal_type": goal_type}
        
        strategy = self.strategy_selector.select_strategy(context)
        
        print(f"[META-LEARN] Using strategy: {strategy.name}")
        
        attempt_id = f"attempt_{int(start_time)}_{hashlib.md5(goal.encode()).hexdigest()[:6]}"
        
        attempt = MetaAttempt(
            attempt_id=attempt_id,
            goal=goal,
            strategy_id=strategy.strategy_id,
            result="pending",
            success=False,
            execution_time=0,
            timestamp=datetime.now().isoformat()
        )
        
        success = False
        last_error = ""
        
        for iteration in range(max_attempts):
            iteration_start = time.time()
            
            result = self._execute_iteration(goal, strategy, iteration)
            
            iteration_time = time.time() - iteration_start
            
            if result.get("success"):
                success = True
                last_error = ""
                break
            else:
                last_error = result.get("error", "Unknown error")
                
                self._learn_from_failure(goal, last_error, iteration)
        
        execution_time = time.time() - start_time
        
        attempt.result = "success" if success else "failed"
        attempt.success = success
        attempt.execution_time = execution_time
        
        self.attempts.append(attempt)
        if len(self.attempts) > 1000:
            self.attempts = self.attempts[-1000:]
        self._save_attempts()
        
        self.strategy_selector.update_strategy_performance(
            strategy.strategy_id, success, execution_time
        )
        
        if success:
            self._derive_new_rule(goal, strategy.strategy_id)
        
        return {
            "success": success,
            "strategy_used": strategy.name,
            "iterations": iteration + 1,
            "execution_time": execution_time,
            "last_error": last_error,
            "meta_learned": len(self.rules)
        }
    
    def _execute_iteration(self, goal: str, strategy: Strategy, iteration: int) -> Dict:
        """Execute a single iteration based on strategy."""
        
        if strategy.strategy_id == "recursive_refine":
            return self._execute_recursive_refine(goal, iteration)
        elif strategy.strategy_id == "test_first":
            return self._execute_test_first(goal, iteration)
        elif strategy.strategy_id == "scaffold":
            return self._execute_scaffold(goal, iteration)
        elif strategy.strategy_id == "template_match":
            return self._execute_template_match(goal, iteration)
        else:
            return self._execute_default(goal, iteration)
    
    def _execute_default(self, goal: str, iteration: int) -> Dict:
        """Default execution strategy."""
        return self._call_omega_forge(goal)
    
    def _execute_recursive_refine(self, goal: str, iteration: int) -> Dict:
        """Recursive refinement strategy."""
        result = self._call_omega_forge(goal)
        
        if not result.get("success"):
            refined_goal = f"{goal} (refinement attempt {iteration + 1})"
            result = self._call_omega_forge(refined_goal)
        
        return result
    
    def _execute_test_first(self, goal: str, iteration: int) -> Dict:
        """Test-first development strategy."""
        test_goal = f"Write tests for: {goal}"
        test_result = self._call_omega_forge(test_goal)
        
        impl_goal = f"Implement: {goal}"
        return self._call_omega_forge(impl_goal)
    
    def _execute_scaffold(self, goal: str, iteration: int) -> Dict:
        """Scaffold then implement strategy."""
        scaffold_goal = f"Create scaffold for: {goal}"
        scaffold_result = self._call_omega_forge(scaffold_goal)
        
        if scaffold_result.get("success"):
            return self._call_omega_forge(goal)
        
        return scaffold_result
    
    def _execute_template_match(self, goal: str, iteration: int) -> Dict:
        """Template matching strategy."""
        template_goal = f"Use template for: {goal}"
        return self._call_omega_forge(template_goal)
    
    def _call_omega_forge(self, goal: str) -> Dict:
        """Call OMEGA Forge for code generation."""
        try:
            sys.path.insert(0, str(ENGINE_DIR))
            from omega_forge import OmegaForge
            
            forge = OmegaForge(self.project)
            result = forge.execute_goal(goal)
            
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _learn_from_failure(self, goal: str, error: str, iteration: int):
        """Learn from failure to improve future attempts."""
        
        error_type = self._classify_error(error)
        
        rule_key = f"{error_type}_{goal[:20]}"
        
        if rule_key in self.rules:
            rule = self.rules[rule_key]
            rule.failure_count += 1
            rule.confidence = rule.success_count / (rule.success_count + rule.failure_count)
        else:
            self.rules[rule_key] = MetaLearnedRule(
                rule_id=rule_key,
                trigger=error_type,
                action=f"retry_with_{iteration}",
                confidence=0.0,
                success_count=0,
                failure_count=1,
                created_at=datetime.now().isoformat()
            )
        
        self._save_rules()
    
    def _classify_error(self, error: str) -> str:
        """Classify error type using unified ErrorClassifier."""
        try:
            from omega_error_classifier import classify_error
            return classify_error(error)
        except ImportError:
            error_lower = error.lower()
            if "timeout" in error_lower:
                return "timeout"
            elif "syntax" in error_lower:
                return "syntax_error"
            elif "import" in error_lower:
                return "import_error"
            elif "attribute" in error_lower:
                return "attribute_error"
            elif "type" in error_lower:
                return "type_error"
            else:
                return "other"
    
    def _derive_new_rule(self, goal: str, strategy_id: str):
        """Derive new rule from successful execution."""
        
        goal_type = self.determine_goal_type(goal)
        
        rule_key = f"{strategy_id}_{goal_type}"
        
        if rule_key in self.rules:
            rule = self.rules[rule_key]
            rule.success_count += 1
            rule.confidence = rule.success_count / (rule.success_count + rule.failure_count)
        else:
            self.rules[rule_key] = MetaLearnedRule(
                rule_id=rule_key,
                trigger=goal_type,
                action=strategy_id,
                confidence=1.0,
                success_count=1,
                failure_count=0,
                created_at=datetime.now().isoformat()
            )
        
        self._save_rules()
    
    def get_optimal_parameters(self) -> Dict:
        """Get optimized hyperparameters based on meta-learning."""
        
        best_strategies = []
        for sid, strategy in self.strategy_selector.strategies.items():
            if strategy.usage_count > 0:
                best_strategies.append((sid, strategy.success_rate))
        
        best_strategies.sort(key=lambda x: x[1], reverse=True)
        
        return {
            "best_strategy": best_strategies[0][0] if best_strategies else "default",
            "expected_success_rate": best_strategies[0][1] if best_strategies else 0.5,
            "learned_rules": len(self.rules),
            "total_attempts": len(self.attempts),
            "strategies": {
                sid: {
                    "success_rate": s.success_rate,
                    "usage_count": s.usage_count,
                    "avg_time": s.avg_execution_time
                }
                for sid, s in self.strategy_selector.strategies.items()
            }
        }
    
    def analyze_performance_trends(self) -> Dict:
        """Analyze performance trends over time."""
        
        if len(self.attempts) < 10:
            return {"trend": "insufficient_data"}
        
        recent = self.attempts[-50:]
        
        success_count = sum(1 for a in recent if a.success)
        recent_success_rate = success_count / len(recent)
        
        earlier = self.attempts[-100:-50] if len(self.attempts) >= 100 else []
        
        if earlier:
            earlier_success = sum(1 for a in earlier if a.success)
            earlier_success_rate = earlier_success / len(earlier)
            trend = "improving" if recent_success_rate > earlier_success_rate else "declining"
        else:
            trend = "stable"
        
        avg_time = statistics.mean([a.execution_time for a in recent])
        
        return {
            "trend": trend,
            "recent_success_rate": recent_success_rate,
            "avg_execution_time": avg_time,
            "total_attempts": len(self.attempts),
            "improvement_potential": 1.0 - recent_success_rate
        }
    
    def get_statistics(self) -> Dict:
        """Get meta-learning statistics."""
        return {
            "version": self.VERSION,
            "strategies_count": len(self.strategy_selector.strategies),
            "learned_rules": len(self.rules),
            "total_attempts": len(self.attempts),
            "success_rate": sum(1 for a in self.attempts if a.success) / max(len(self.attempts), 1),
            "optimal_params": self.get_optimal_parameters()
        }


def create_meta_learner(project: str = "omega") -> RecursiveMetaLearner:
    """Create a Recursive Meta-Learner instance."""
    return RecursiveMetaLearner(project)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="OMEGA Recursive Meta-Learner")
    parser.add_argument("--project", default="omega", help="Project name")
    parser.add_argument("--execute", type=str, help="Execute goal with meta-learning")
    parser.add_argument("--params", action="store_true", help="Show optimal parameters")
    parser.add_argument("--trends", action="store_true", help="Show performance trends")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    parser.add_argument("--rules", action="store_true", help="Show learned rules")
    
    args = parser.parse_args()
    
    meta = create_meta_learner(args.project)
    
    if args.execute:
        result = meta.execute_with_meta_learning(args.execute)
        print(json.dumps(result, indent=2))
    elif args.params:
        print(json.dumps(meta.get_optimal_parameters(), indent=2))
    elif args.trends:
        print(json.dumps(meta.analyze_performance_trends(), indent=2))
    elif args.stats:
        print(json.dumps(meta.get_statistics(), indent=2))
    elif args.rules:
        for rule in meta.rules.values():
            print(f"{rule.rule_id}: {rule.confidence:.2%} ({rule.success_count} success, {rule.failure_count} fail)")
    else:
        print(f"Recursive Meta-Learner v{meta.VERSION} ready")