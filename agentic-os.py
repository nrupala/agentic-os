#!/usr/bin/env python3
"""
agentic-OS: Unified Autonomous Agent System
==========================================
Paradise Stack + OMEGA-CODE Integration

Features:
- 19-phase OMEGA-CODE cognitive architecture
- Hierarchical memory with WAL protocol
- GAN-style self-correction
- RAG-based memory retrieval
- Zero-trust security
- Enterprise observability
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List

PROJECT_ROOT = Path(__file__).parent
PROJECT_NAME = os.getenv("PROJECT_NAME", "default")

sys.path.insert(0, str(PROJECT_ROOT / "engine"))
sys.path.insert(0, str(PROJECT_ROOT / "security"))


class AgenticOS:
    """
    Unified agentic-OS system integrating all 19 phases.
    
    Architecture:
    ┌─────────────────────────────────────────────────────────────┐
    │                    agentic-OS Core                          │
    ├─────────────────────────────────────────────────────────────┤
    │  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐  │
    │  │   Memory    │  │  Cognitive   │  │   Security     │  │
    │  │   System    │  │   Engine     │  │   Layer        │  │
    │  │  (3-tier)  │  │  (Meta+GAN) │  │ (Vault+RBAC)   │  │
    │  └──────┬──────┘  └──────┬───────┘  └───────┬────────┘  │
    │         │                  │                   │           │
    │         └──────────────────┼───────────────────┘           │
    │                            ▼                              │
    │                   ┌────────────────┐                        │
    │                   │   Recursive   │                        │
    │                   │     Forge     │                        │
    │                   │  (RECOLLECT   │                        │
    │                   │  → RECTIFY     │                        │
    │                   │  → VERIFY      │                        │
    │                   │  → PERSIST)    │                        │
    │                   └───────┬────────┘                        │
    │                           ▼                                │
    │                   ┌────────────────┐                        │
    │                   │  Observability │                        │
    │                   │   (Loki/Graf)  │                        │
    │                   └────────────────┘                        │
    └─────────────────────────────────────────────────────────────┘
    """
    
    def __init__(self, project: str = None):
        self.project = project or PROJECT_NAME
        self.project_path = PROJECT_ROOT / "projects" / self.project
        
        self.subsystems = {}
        self._init_all()
    
    def _init_all(self):
        """Initialize all subsystems."""
        print("\n[INIT] agentic-OS: Initializing subsystems...")
        
        self._ensure_dirs()
        self._init_memory()
        self._init_cognitive()
        self._init_security()
        self._init_observability()
        
        active = sum(1 for v in self.subsystems.values() if v)
        print(f"[INIT] {active}/{len(self.subsystems)} subsystems active")
    
    def _ensure_dirs(self):
        """Ensure required directories exist."""
        dirs = ["src", "outputs", "state", "logs", "memory", "self-eval-logs"]
        for d in dirs:
            (self.project_path / d).mkdir(parents=True, exist_ok=True)
    
    def _init_memory(self):
        """Initialize memory subsystem."""
        try:
            from omega_hierarchical_memory import HierarchicalMemory
            self.subsystems["memory"] = HierarchicalMemory(str(self.project_path))
            print("  [OK] Memory System")
        except Exception as e:
            print(f"  [FAIL] Memory: {e}")
            self.subsystems["memory"] = None
    
    def _init_cognitive(self):
        """Initialize cognitive subsystems."""
        try:
            from omega_meta_logic import MetaCognition
            db_path = str(self.project_path / "state" / "omega.db")
            self.subsystems["meta"] = MetaCognition(db_path)
            print("  [OK] Meta-Cognition")
        except Exception as e:
            print(f"  [FAIL] Meta-Cognition: {e}")
            self.subsystems["meta"] = None
        
        try:
            from omega_gan import OmegaGAN
            self.subsystems["gan"] = OmegaGAN(str(self.project_path))
            print("  [OK] GAN Self-Correction")
        except Exception as e:
            print(f"  [FAIL] GAN: {e}")
            self.subsystems["gan"] = None
        
        try:
            from omega_rag import OmegaRAG
            self.subsystems["rag"] = OmegaRAG(str(self.project_path))
            print("  [OK] RAG Retrieval")
        except Exception as e:
            print(f"  [FAIL] RAG: {e}")
            self.subsystems["rag"] = None
    
    def _init_security(self):
        """Initialize security subsystem."""
        try:
            from omega_access import AccessControl
            self.subsystems["access"] = AccessControl(str(PROJECT_ROOT / "system_scripts"))
            print("  [OK] Access Control")
        except Exception as e:
            print(f"  [FAIL] Access Control: {e}")
            self.subsystems["access"] = None
    
    def _init_observability(self):
        """Initialize observability subsystem."""
        try:
            from omega_self_eval import SelfEvaluationReporting
            self.subsystems["evaluator"] = SelfEvaluationReporting(str(self.project_path))
            print("  [OK] Self-Evaluation")
        except Exception as e:
            print(f"  [FAIL] Self-Evaluation: {e}")
            self.subsystems["evaluator"] = None
    
    def think(self, goal: str) -> str:
        """
        Think phase: Use cognitive engine to process goal.
        """
        context = ""
        
        if self.subsystems.get("rag"):
            context = self.subsystems["rag"].retrieve_context(goal)
        
        if self.subsystems.get("meta") and self.subsystems.get("memory"):
            patterns = self.subsystems["meta"].analyze_failure_patterns()
            constraints = self.subsystems["meta"].derive_constraints(patterns)
            
            prompt = self.subsystems["meta"].generate_disciplined_prompt(
                goal=goal,
                constraints=constraints,
                patterns=patterns
            )
            return context + "\n" + prompt if context else prompt
        
        return goal
    
    def generate(self, goal: str) -> tuple:
        """
        Generate phase: Use GAN to generate code.
        Returns (code, evaluation)
        """
        if self.subsystems.get("gan"):
            constraints = ["Error handling", "Type hints", "Documentation"]
            code, evaluation = self.subsystems["gan"].generate_and_refine(goal, constraints)
            return code, evaluation
        
        return "# Fallback code", {"score": 0.5, "passed": False}
    
    def remember(self, key: str, value: str):
        """Store in memory."""
        if self.subsystems.get("memory"):
            self.subsystems["memory"].distill_wisdom([f"{key}: {value}"])
    
    def recall(self, query: str) -> List[str]:
        """Recall from memory."""
        if self.subsystems.get("rag"):
            results = self.subsystems["rag"].retrieve(query)
            return [r["content"] for r in results]
        return []
    
    def evaluate(self, iteration: int, success: bool):
        """Self-evaluate after iteration."""
        if self.subsystems.get("evaluator") and iteration % 10 == 0:
            metrics = {
                "recursion_depth": iteration,
                "max_recursion": 50,
                "total_decisions": iteration,
                "correct_decisions": iteration if success else iteration - 1,
                "violations": 0,
                "auto_corrections": 0,
                "decisions": [],
                "failures": [],
                "next_goal": "Continue"
            }
            self.subsystems["evaluator"].generate_markdown_report(metrics)
    
    def status(self) -> Dict:
        """Get system status."""
        return {
            "project": self.project,
            "subsystems": {k: v is not None for k, v in self.subsystems.items()},
            "memory_files": list((self.project_path / "memory").glob("*"))
        }
    
    def close(self):
        """Cleanup resources."""
        for sub in self.subsystems.values():
            if hasattr(sub, 'close'):
                sub.close()


def run_demo():
    """Run a simple demonstration."""
    print("""
============================================================
   agentic-OS v2.0
   Unified OMEGA-CODE + Paradise Stack
============================================================
    """)
    
    agent = AgenticOS("demo")
    
    print("\n[MEMORY] Testing memory...")
    agent.remember("first_run", datetime.now().isoformat())
    memories = agent.recall("run")
    print(f"  Recalled {len(memories)} memories")
    
    print("\n[COGNITIVE] Testing cognitive engine...")
    goal = "Create a REST API endpoint"
    thought = agent.think(goal)
    print(f"  Thought processed: {len(thought)} chars")
    
    print("\n[GENERATE] Testing code generation...")
    code, eval_result = agent.generate(goal)
    print(f"  Generated: {len(code)} chars")
    print(f"  Score: {eval_result.get('score', 0):.2f}")
    print(f"  Passed: {eval_result.get('passed', False)}")
    
    print("\n[STATUS]")
    status = agent.status()
    print(f"  Project: {status['project']}")
    print(f"  Active subsystems: {sum(status['subsystems'].values())}/{len(status['subsystems'])}")
    
    agent.close()
    
    print("\n[DONE] Demo complete!")


def run_agent(goal: str = None, max_attempts: int = 50):
    """Run the full autonomous agent loop."""
    goal = goal or os.getenv("GOAL", "Build a self-healing microservice")
    
    print(f"""
============================================================
   agentic-OS: Autonomous Agent
   Goal: {goal}
============================================================
     """)
    
    agent = AgenticOS()
    
    iteration = 0
    
    while iteration < max_attempts:
        iteration += 1
        print(f"\n--- Iteration {iteration}/{max_attempts} ---")
        
        agent.think(goal)
        code, eval_result = agent.generate(goal)
        
        if eval_result.get("passed"):
            print(f"\n[SUCCESS] Goal achieved in {iteration} iterations!")
            agent.remember("success", f"Goal: {goal} completed")
            
            # Save generated code to file
            output_dir = PROJECT_ROOT / "outputs"
            output_dir.mkdir(exist_ok=True)
            
            # Determine file extension and name based on goal
            if "chat" in goal.lower() or "server" in goal.lower():
                filename = "secure_chat_server.py"
            elif "web" in goal.lower() or "api" in goal.lower():
                filename = "web_server.py"
            else:
                filename = "generated_code.py"
            
            output_path = output_dir / filename
            output_path.write_text(code)
            print(f"\n[SAVED] Code saved to: {output_path}")
            
            break
        
        agent.evaluate(iteration, False)
        
        if iteration >= max_attempts:
            print("\n[MAX] Reached max attempts")
    
    agent.close()
    return iteration < max_attempts


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="agentic-OS")
    parser.add_argument("--goal", "-g", help="Goal to achieve")
    parser.add_argument("--max", "-m", type=int, default=50, help="Max iterations")
    parser.add_argument("--demo", "-d", action="store_true", help="Run demo")
    
    args = parser.parse_args()
    
    if args.demo:
        run_demo()
    elif args.goal:
        run_agent(args.goal, args.max)
    else:
        print("Usage: python agentic-os.py --goal 'Build a REST API'")
        print("       python agentic-os.py --demo")
