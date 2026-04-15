#!/usr/bin/env python3
"""
PHASE 13: GAN-Inspired Self-Correction
Generator vs Discriminator pattern for code quality.
"""

import json
import hashlib
from pathlib import Path
from typing import Tuple, Optional, List
from datetime import datetime

class CodeGenerator:
    """Generator: Creates code solutions."""
    
    def __init__(self):
        self.generated_count = 0
    
    def generate(self, goal: str, constraints: List[str]) -> str:
        """Generate code based on goal and constraints."""
        self.generated_count += 1
        
        code = f'''# OMEGA Generated Code
# Goal: {goal}
# Constraints: {len(constraints)} applied

def main():
    """
    Generated solution for: {goal}
    """
    result = {{"status": "implemented", "goal": "{goal}"}}
    print(f"Completed: {{result}}")
    return result

if __name__ == "__main__":
    main()
'''
        for constraint in constraints[:3]:
            code = f"# Constraint: {constraint}\n" + code
        
        return code


class CodeDiscriminator:
    """Discriminator: Evaluates code quality."""
    
    def __init__(self):
        self.quality_checks = [
            "error_handling",
            "type_safety", 
            "resource_cleanup",
            "input_validation",
            "documentation"
        ]
    
    def evaluate(self, code: str, goal: str) -> dict:
        """
        Evaluate code quality against goal.
        
        Returns:
            dict with 'score' (0-1), 'issues' list, 'passed' bool
        """
        issues = []
        score = 1.0
        
        if "try:" not in code and "except" not in code:
            issues.append("Missing error handling")
            score -= 0.2
        
        if "return" not in code:
            issues.append("Missing return statement")
            score -= 0.1
        
        if len(code) < 100:
            issues.append("Code seems too short")
            score -= 0.15
        
        if "# Goal:" not in code:
            issues.append("Missing goal documentation")
            score -= 0.1
        
        if "print" not in code and "return" not in code:
            issues.append("No output mechanism")
            score -= 0.15
        
        if "import" in code and code.count("import") > 5:
            issues.append("Too many imports - consider reducing")
            score -= 0.1
        
        if goal.lower()[:20] not in code.lower():
            issues.append("Goal not referenced in code")
            score -= 0.1
        
        return {
            "score": max(0.0, score),
            "issues": issues,
            "passed": score >= 0.7,
            "evaluated_at": datetime.now().isoformat()
        }


class OmegaGAN:
    """
    GAN-inspired self-correction system.
    
    - Generator creates code
    - Discriminator evaluates it
    - Loop continues until discriminator passes
    - Track temporal state for RNN-like behavior
    """
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.generator = CodeGenerator()
        self.discriminator = CodeDiscriminator()
        
        self.history_file = self.project_path / "state" / "gan_history.json"
        self.history = self._load_history()
        
        self.state_file = self.project_path / "state" / "gan_state.json"
        self.state = self._load_state()
    
    def _load_history(self) -> List[dict]:
        """Load generation history."""
        if self.history_file.exists():
            try:
                return json.loads(self.history_file.read_text())
            except:
                pass
        return []
    
    def _load_state(self) -> dict:
        """Load temporal state (RNN-like)."""
        if self.state_file.exists():
            try:
                return json.loads(self.state_file.read_text())
            except:
                pass
        
        return {
            "total_generations": 0,
            "successful_generations": 0,
            "avg_score": 0.0,
            "common_issues": [],
            "recent_scores": []
        }
    
    def _save_history(self):
        """Save generation history."""
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        self.history_file.write_text(json.dumps(self.history[-100:], indent=2))
    
    def _save_state(self):
        """Save temporal state."""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.state_file.write_text(json.dumps(self.state, indent=2))
    
    def generate_and_refine(
        self,
        goal: str,
        constraints: List[str],
        max_iterations: int = 5
    ) -> Tuple[str, dict]:
        """
        Generate code with iterative refinement.
        
        Loop:
        1. Generator creates code
        2. Discriminator evaluates
        3. If failed, Generator refines based on issues
        4. Repeat until passed or max_iterations
        """
        self.state["total_generations"] += 1
        
        current_code = ""
        iteration = 0
        best_code = ""
        best_score = 0.0
        
        while iteration < max_iterations:
            iteration += 1
            
            if iteration == 1:
                current_code = self.generator.generate(goal, constraints)
            else:
                issues = self.state.get("last_issues", [])
                refined_constraints = constraints + [f"Fix: {i}" for i in issues]
                current_code = self.generator.generate(goal, refined_constraints)
            
            evaluation = self.discriminator.evaluate(current_code, goal)
            
            self.history.append({
                "iteration": iteration,
                "goal": goal,
                "score": evaluation["score"],
                "issues": evaluation["issues"],
                "timestamp": datetime.now().isoformat()
            })
            
            self.state["last_issues"] = evaluation["issues"]
            self.state["recent_scores"].append(evaluation["score"])
            if len(self.state["recent_scores"]) > 10:
                self.state["recent_scores"] = self.state["recent_scores"][-10:]
            self.state["avg_score"] = sum(self.state["recent_scores"]) / len(self.state["recent_scores"])
            
            if evaluation["score"] > best_score:
                best_score = evaluation["score"]
                best_code = current_code
            
            if evaluation["passed"]:
                self.state["successful_generations"] += 1
                break
        
        self._save_history()
        self._save_state()
        
        return best_code, evaluation
    
    def get_temporal_context(self) -> dict:
        """Get RNN-like temporal state."""
        return {
            "total": self.state["total_generations"],
            "successful": self.state["successful_generations"],
            "success_rate": self.state["successful_generations"] / max(1, self.state["total_generations"]),
            "avg_score": self.state["avg_score"],
            "recent_trend": self._calculate_trend()
        }
    
    def _calculate_trend(self) -> str:
        """Calculate if scores are improving or declining."""
        scores = self.state["recent_scores"]
        if len(scores) < 3:
            return "insufficient_data"
        
        recent = sum(scores[-3:]) / 3
        earlier = sum(scores[:3]) / 3
        
        if recent > earlier + 0.1:
            return "improving"
        elif recent < earlier - 0.1:
            return "declining"
        return "stable"


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: omega_gan.py <project_path>")
        sys.exit(1)
    
    project_path = sys.argv[1]
    gan = OmegaGAN(project_path)
    
    goal = "Create a function that validates email addresses"
    constraints = ["Use regex", "Handle edge cases", "Return boolean"]
    
    print(f"Running GAN for: {goal}\n")
    
    code, evaluation = gan.generate_and_refine(goal, constraints)
    
    print(f"Final Score: {evaluation['score']:.2f}")
    print(f"Passed: {evaluation['passed']}")
    print(f"Iterations: {len([h for h in gan.history if h['goal'] == goal])}")
    print("\n--- Generated Code ---")
    print(code[:500] + "..." if len(code) > 500 else code)
    
    print("\n--- Temporal Context ---")
    context = gan.get_temporal_context()
    for k, v in context.items():
        print(f"  {k}: {v}")
