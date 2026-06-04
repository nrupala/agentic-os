#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
# Copyright 2026 agentic-OS Contributors

"""
Paradise Cognitive Orchestrator - Parallel PDCA Loop Coordinator
Disciplined autonomous development with parallel Plan-Do-Check-Act loops
"""

import os
import sys
import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum

PROJECT_ROOT = Path(os.environ.get("HOST_PROJECT_ROOT", "/app"))
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from cognition.knowledge_graph import get_graph, KnowledgeGraph, Entity, Blob
    from cognition.meta_cognition import get_meta_cognition, get_rag, get_gan, get_rnn
    from cognition.self_improvement import get_memory, get_self_improver, get_optimizer
    from cognition.entities import get_registry, create_default_carriers, CognitiveCarrier
    from cognition.verification import VerificationEngine, PDCAVerifier, LoopDetector
except ImportError:
    pass


class LoopState(Enum):
    IDLE = "idle"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    STUCK = "stuck"


@dataclass
class PDCALoop:
    """Single PDCA Loop Instance"""
    name: str
    phase: str
    state: LoopState = LoopState.IDLE
    iteration: int = 0
    max_iterations: int = 10
    issues: list = field(default_factory=list)
    results: list = field(default_factory=list)
    stuck_count: int = 0
    
    def can_continue(self) -> bool:
        return self.iteration < self.max_iterations and self.state not in [LoopState.PASSED, LoopState.STUCK]
    
    def is_stuck(self) -> bool:
        return self.stuck_count >= 3


@dataclass
class CarrierTask:
    """Task assigned to a carrier"""
    carrier_name: str
    task_type: str
    input_data: Any
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    success: bool = False
    output: Any = None
    error: Optional[str] = None


class PDCAOrchestrator:
    """
    Parallel PDCA Loop Orchestrator
    
    Runs multiple PDCA cycles simultaneously:
    - Planner Loop: Refines implementation plan
    - Implementer Loop: Writes code recursively
    - Guardian Loop: Runs linting/verification
    - Executor Loop: Runs tests
    - Improver Loop: Fixes issues
    """
    
    def __init__(self):
        self.loops = {
            "planner": PDCALoop(name="Planner", phase="PLAN", max_iterations=10),
            "implementer": PDCALoop(name="Implementer", phase="DO", max_iterations=10),
            "guardian": PDCALoop(name="Guardian", phase="CHECK", max_iterations=10),
            "executor": PDCALoop(name="Executor", phase="CHECK", max_iterations=10),
            "improver": PDCALoop(name="Improver", phase="ACT", max_iterations=10),
        }
        
        self.verifier = VerificationEngine()
        self.pdca_verifier = PDCAVerifier()
        self.loop_detector = LoopDetector()
        
        self.task_queue = []
        self.carrier_tasks = []
        self.executor = ThreadPoolExecutor(max_workers=5)
        
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.user_satisfied = False
        self.user_feedback = None
        
        self.knowledge_graph = None
        self.meta_cognition = None
        self.rag = None
        self.gan = None
        self.rnn = None
        self.memory = None
        self.self_improver = None
        self.optimizer = None
        self.registry = None
        
        self.initialized = False
    
    def initialize(self) -> bool:
        """Initialize all cognitive subsystems"""
        print("🧠 Initializing Parallel PDCA Orchestrator...")
        
        try:
            self.knowledge_graph = get_graph()
            self.meta_cognition = get_meta_cognition()
            self.rag = get_rag()
            self.gan = get_gan()
            self.rnn = get_rnn()
            self.memory = get_memory()
            self.self_improver = get_self_improver()
            self.optimizer = get_optimizer()
            self.registry = get_registry()
            
            for carrier in create_default_carriers():
                self.registry.register_carrier(carrier)
            
            self.initialized = True
            self._log("system", "PDCA Orchestrator initialized with 5 parallel loops")
            return True
        except Exception as e:
            print(f"   ✗ Initialization error: {e}")
            return False
    
    def _log(self, event_type: str, message: str, data: Optional[dict] = None):
        """Log cognitive event"""
        print(f"  [{event_type.upper()}] {message}")
    
    def think(self, prompt: str) -> dict:
        """Use meta-cognition to analyze the request"""
        thought = self.meta_cognition.think(prompt)
        
        verification = self.verifier.verify_response(prompt)
        thought["verification"] = {
            "assumptions_stated": verification.details["checks"]["assumptions"]["valid"],
            "verification_mentioned": verification.details["checks"]["verification"]["valid"],
            "failure_modes_considered": verification.details["checks"]["failure_modes"]["valid"],
        }
        
        thought["rag_context"] = self.rag.get_context(prompt)
        thought["similar_experiences"] = len(self.memory.recall_similar(prompt))
        
        return thought
    
    async def run_parallel_pdc(
        self,
        prompt: str,
        plan_func: Callable,
        implement_func: Callable,
        lint_func: Callable,
        test_func: Callable,
        fix_func: Callable,
    ) -> dict:
        """
        Run parallel PDCA loops for autonomous development
        
        Each loop runs independently but shares state through the orchestrator
        """
        results = {
            "session_id": self.session_id,
            "prompt": prompt,
            "loops": {},
            "iterations": [],
            "final_outcome": None,
            "success": False,
        }
        
        self._log("orchestrator", f"Starting parallel PDCA loops for: {prompt[:50]}...")
        
        plan_loop = self.loops["planner"]
        implement_loop = self.loops["implementer"]
        guardian_loop = self.loops["guardian"]
        executor_loop = self.loops["executor"]
        improver_loop = self.loops["improver"]
        
        current_plan = ""
        current_code = {}
        lint_issues = []
        test_failures = []
        
        max_total_iterations = 10
        total_iteration = 0
        
        while total_iteration < max_total_iterations and not self.user_satisfied:
            total_iteration += 1
            iteration_result = {
                "iteration": total_iteration,
                "loop_states": {},
                "actions": [],
            }
            
            self._log("iteration", f"\n{'='*50}")
            self._log("iteration", f"PARALLEL PDCA ITERATION {total_iteration}/{max_total_iterations}")
            self._log("iteration", f"{'='*50}")
            
            async with asyncio.TaskGroup() as tg:
                plan_task = tg.create_task(self._run_plan_loop(
                    plan_loop, prompt, plan_func, current_plan
                ))
                implement_task = tg.create_task(self._run_implement_loop(
                    implement_loop, implement_func, current_plan
                ))
            
            current_plan = plan_task.result()
            current_code = implement_task.result()
            
            lint_result = await self._run_guardian_loop(guardian_loop, lint_func, current_code)
            test_result = await self._run_executor_loop(executor_loop, test_func, current_code)
            
            lint_issues = lint_result.get("issues", [])
            test_failures = test_result.get("failures", [])
            
            iteration_result["loop_states"] = {
                "planner": plan_loop.state.value,
                "implementer": implement_loop.state.value,
                "guardian": guardian_loop.state.value,
                "executor": executor_loop.state.value,
            }
            
            all_checks_passed = len(lint_issues) == 0 and len(test_failures) == 0
            
            if all_checks_passed:
                self._log("success", "All PDCA checks passed!")
                improver_loop.state = LoopState.PASSED
                iteration_result["success"] = True
                results["success"] = True
                results["final_outcome"] = {
                    "plan": current_plan,
                    "code": current_code,
                }
                break
            
            if lint_issues or test_failures:
                self._log("check", f"Found {len(lint_issues)} lint issues, {len(test_failures)} test failures")
                
                fix_result = await self._run_improver_loop(
                    improver_loop, fix_func,
                    {"lint": lint_issues, "tests": test_failures}
                )
                
                current_code = fix_result.get("code", current_code)
                iteration_result["actions"].append({
                    "type": "fix",
                    "result": fix_result,
                })
                
                self._record_learning(
                    prompt=prompt,
                    action="fix_attempt",
                    success=len(lint_issues) == 0 and len(test_failures) == 0,
                    issues={"lint": lint_issues, "tests": test_failures}
                )
            
            self.loop_detector.record(
                f"iteration_{total_iteration}",
                "passed" if all_checks_passed else "failed"
            )
            
            if self.loop_detector.is_stuck():
                self._log("warning", "Loop detection: System appears stuck - breaking")
                results["stuck"] = True
                break
            
            results["iterations"].append(iteration_result)
        
        results["total_iterations"] = total_iteration
        results["final_loop_states"] = {k: v.state.value for k, v in self.loops.items()}
        
        return results
    
    async def _run_plan_loop(
        self,
        loop: PDCALoop,
        prompt: str,
        plan_func: Callable,
        current_plan: str,
    ) -> str:
        """Run the Planner PDCA loop"""
        loop.iteration += 1
        loop.state = LoopState.RUNNING
        
        self._log("planner", f"PLAN loop iteration {loop.iteration}")
        
        plan = await plan_func(prompt, current_plan)
        
        plan_verification = self.verifier.verify_plan(plan)
        if plan_verification.valid:
            loop.state = LoopState.PASSED
            self._log("planner", "PLAN verified - complete")
        else:
            loop.state = LoopState.RUNNING
            self._log("planner", f"PLAN needs improvement: {plan_verification.message}")
        
        return plan
    
    async def _run_implement_loop(
        self,
        loop: PDCALoop,
        implement_func: Callable,
        plan: str,
    ) -> dict:
        """Run the Implementer PDCA loop"""
        loop.iteration += 1
        loop.state = LoopState.RUNNING
        
        self._log("implementer", f"DO loop iteration {loop.iteration}")
        
        code = await implement_func(plan)
        
        loop.results.append(code)
        if code:
            loop.state = LoopState.PASSED
            self._log("implementer", f"DO complete - {len(code)} files created")
        
        return code
    
    async def _run_guardian_loop(
        self,
        loop: PDCALoop,
        lint_func: Callable,
        code: dict,
    ) -> dict:
        """Run the Guardian PDCA loop"""
        loop.iteration += 1
        loop.state = LoopState.RUNNING
        
        self._log("guardian", f"CHECK (Guardian) iteration {loop.iteration}")
        
        result = await lint_func(code)
        issues = result.get("issues", [])
        
        loop.issues = issues
        if len(issues) == 0:
            loop.state = LoopState.PASSED
            self._log("guardian", "Guardian check PASSED")
        else:
            loop.state = LoopState.RUNNING
            self._log("guardian", f"Guardian found {len(issues)} issues")
        
        return result
    
    async def _run_executor_loop(
        self,
        loop: PDCALoop,
        test_func: Callable,
        code: dict,
    ) -> dict:
        """Run the Executor PDCA loop"""
        loop.iteration += 1
        loop.state = LoopState.RUNNING
        
        self._log("executor", f"CHECK (Executor) iteration {loop.iteration}")
        
        result = await test_func(code)
        failures = result.get("failures", [])
        
        loop.issues = failures
        if len(failures) == 0:
            loop.state = LoopState.PASSED
            self._log("executor", "Executor check PASSED")
        else:
            loop.state = LoopState.RUNNING
            self._log("executor", f"Executor found {len(failures)} test failures")
        
        return result
    
    async def _run_improver_loop(
        self,
        loop: PDCALoop,
        fix_func: Callable,
        issues: dict,
    ) -> dict:
        """Run the Improver PDCA loop"""
        loop.iteration += 1
        loop.state = LoopState.RUNNING
        
        self._log("improver", f"ACT (Improver) iteration {loop.iteration}")
        
        result = await fix_func(issues)
        
        if result.get("success"):
            loop.state = LoopState.PASSED
            self._log("improver", "ACT complete - fixes applied")
        else:
            loop.stuck_count += 1
            if loop.is_stuck():
                loop.state = LoopState.STUCK
                self._log("improver", "ACT STUCK - too many failures")
        
        return result
    
    def _record_learning(
        self,
        prompt: str,
        action: str,
        success: bool,
        issues: Optional[dict] = None,
    ):
        """Record learning from the iteration"""
        try:
            if success:
                self.knowledge_graph.learn_from_success(
                    task_type=prompt.split()[0],
                    approach=action,
                    outcome={"success": True},
                )
                self.self_improver.memory.store_episode(
                    prompt=prompt,
                    actions=[{"type": action}],
                    outcome="success",
                    success=True,
                )
                self.optimizer.record_outcome(action, True)
            else:
                self.knowledge_graph.learn_from_failure(
                    task_type=prompt.split()[0],
                    approach=action,
                    error=str(issues),
                )
                self.optimizer.record_outcome(action, False)
        except Exception as e:
            self._log("error", f"Learning recording failed: {e}")
    
    def get_status(self) -> dict:
        """Get current orchestrator status"""
        return {
            "session_id": self.session_id,
            "initialized": self.initialized,
            "user_satisfied": self.user_satisfied,
            "loops": {
                name: {
                    "state": loop.state.value,
                    "iteration": loop.iteration,
                    "issues": len(loop.issues),
                    "stuck": loop.is_stuck(),
                }
                for name, loop in self.loops.items()
            },
            "loop_detector": self.loop_detector.get_status(),
        }
    
    def get_dashboard_data(self) -> dict:
        """Get data for dashboard visualization"""
        return {
            "status": self.get_status(),
            "cognitive": {
                "knowledge_graph": {
                    "entities": self.knowledge_graph.stats if self.knowledge_graph else {},
                    "recent": self.knowledge_graph.get_recent_learning(10) if self.knowledge_graph else [],
                },
                "memory": {
                    "episodes": len(self.memory.episodes) if self.memory else 0,
                    "patterns": self.memory.get_success_patterns() if self.memory else {},
                },
                "optimizer": {
                    "strategies": self.optimizer.get_all_strategies() if self.optimizer else [],
                },
            },
            "pdc_loops": {
                name: {
                    "name": loop.name,
                    "phase": loop.phase,
                    "state": loop.state.value,
                    "iteration": loop.iteration,
                    "max_iterations": loop.max_iterations,
                    "can_continue": loop.can_continue(),
                }
                for name, loop in self.loops.items()
            },
        }


_orchestrator = None


def get_orchestrator() -> PDCAOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = PDCAOrchestrator()
    return _orchestrator


def initialize() -> bool:
    """Initialize the orchestrator"""
    orch = get_orchestrator()
    return orch.initialize()


async def run_development(prompt: str) -> dict:
    """Run full development cycle with parallel PDCA"""
    orchestrator = get_orchestrator()
    
    if not orchestrator.initialized:
        orchestrator.initialize()
    
    async def dummy_plan(p, current):
        await asyncio.sleep(0.1)
        return f"# Plan for: {p}\n\n## Steps\n1. Design\n2. Implement\n3. Test"
    
    async def dummy_implement(plan):
        await asyncio.sleep(0.1)
        return {"main.py": "# Implementation"}
    
    async def dummy_lint(code):
        await asyncio.sleep(0.1)
        return {"issues": []}
    
    async def dummy_test(code):
        await asyncio.sleep(0.1)
        return {"failures": []}
    
    async def dummy_fix(issues):
        await asyncio.sleep(0.1)
        return {"success": True, "code": {}}
    
    return await orchestrator.run_parallel_pdc(
        prompt=prompt,
        plan_func=dummy_plan,
        implement_func=dummy_implement,
        lint_func=dummy_lint,
        test_func=dummy_test,
        fix_func=dummy_fix,
    )


def main():
    print("🧠 Paradise PDCA Orchestrator")
    print("=" * 50)
    
    orchestrator = get_orchestrator()
    
    if orchestrator.initialize():
        print("\n📊 System Status:")
        status = orchestrator.get_status()
        for key, value in status.items():
            if key != "loops":
                print(f"   {key}: {value}")
        
        print("\n🔄 PDCA Loops:")
        for name, loop in orchestrator.loops.items():
            print(f"   {loop.name}: {loop.phase} phase, {loop.state.value}")


if __name__ == "__main__":
    main()
