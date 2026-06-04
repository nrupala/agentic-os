#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
# Copyright 2026 agentic-OS Contributors

"""
Paradise Cognitive Orchestrator - Main Coordinator
Ties together all cognitive systems: Knowledge Graph, Meta-Cognition, Self-Improvement, RNN, GAN, RAG
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(os.environ.get("HOST_PROJECT_ROOT", "/app"))
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from cognition.knowledge_graph import get_graph, KnowledgeGraph, Entity, Blob
    from cognition.meta_cognition import (
        get_meta_cognition, MetaCognition,
        get_rag, RAGEngine,
        get_gan, GANGenerator,
        get_rnn, RNNProcessor,
    )
    from cognition.self_improvement import (
        get_memory, get_self_improver, get_optimizer, get_loop,
        Memory, SelfImprover, StrategyOptimizer, ImprovementLoop,
    )
    from cognition.entities import (
        get_registry, create_default_carriers,
        EntityRegistry, CognitiveCarrier, Container,
        DataBlob, TaskPlaceholder,
    )
except ImportError:
    pass


class CognitiveOrchestrator:
    """Central coordinator for all cognitive processes"""
    
    def __init__(self):
        self.initialized = False
        self.knowledge_graph = None
        self.meta_cognition = None
        self.rag = None
        self.gan = None
        self.rnn = None
        self.memory = None
        self.self_improver = None
        self.optimizer = None
        self.improvement_loop = None
        self.registry = None
        self.session_id = None
        self.iteration = 0
        self.max_iterations = 10
        self.user_satisfied = False
        
        self.cognitive_log = []
        self.state = {
            "phase": "idle",
            "current_task": None,
            "issues": [],
            "improvements": [],
            "learnings": [],
        }
    
    def initialize(self):
        """Initialize all cognitive subsystems"""
        print("🧠 Initializing Cognitive Systems...")
        
        try:
            self.knowledge_graph = get_graph()
            self.meta_cognition = get_meta_cognition()
            self.rag = get_rag()
            self.gan = get_gan()
            self.rnn = get_rnn()
            self.memory = get_memory()
            self.self_improver = get_self_improver()
            self.optimizer = get_optimizer()
            self.improvement_loop = get_loop()
            self.registry = get_registry()
            
            carriers = create_default_carriers()
            for carrier in carriers:
                self.registry.register_carrier(carrier)
            
            self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.initialized = True
            
            self._log("system", "Cognitive orchestrator initialized")
            print(f"   ✓ Knowledge Graph: {self.knowledge_graph.stats['total_entities']} entities")
            print("   ✓ Meta-Cognition: Active")
            print("   ✓ RAG Engine: Active")
            print("   ✓ GAN Generator: Active")
            print("   ✓ RNN Processor: Active")
            print("   ✓ Self-Improver: Active")
            print(f"   ✓ Entity Registry: {len(carriers)} carriers")
            
            return True
        except Exception as e:
            print(f"   ✗ Initialization error: {e}")
            return False
    
    def _log(self, event_type: str, message: str, data: Optional[dict] = None):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "message": message,
            "data": data or {},
            "iteration": self.iteration,
        }
        self.cognitive_log.append(entry)
    
    def think(self, prompt: str) -> dict:
        """Use meta-cognition to analyze and plan"""
        thought = self.meta_cognition.think(prompt)
        self._log("thought", f"Analyzing prompt: {prompt[:50]}...", thought)
        
        context = self.rag.get_context(prompt)
        if context:
            thought["rag_context"] = context
        
        similar = self.memory.recall_similar(prompt)
        if similar:
            thought["similar_experiences"] = len(similar)
        
        return thought
    
    def plan(self, prompt: str) -> dict:
        """Generate implementation plan using knowledge graph"""
        self.state["phase"] = "planning"
        self._log("plan", "Generating implementation plan")
        
        plan_result = {
            "thought": self.think(prompt),
            "strategy": self.meta_cognition.get_best_strategy(prompt.split()[0]),
            "improvements": self.self_improver.get_improvements(prompt),
            "learnings": self.knowledge_graph.get_recent_learning(5),
        }
        
        return plan_result
    
    def execute_with_cognition(self, task_func, check_func) -> dict:
        """Execute task with full cognitive feedback loop"""
        self.state["phase"] = "executing"
        self.iteration = 0
        results = {
            "iterations": [],
            "success": False,
            "final_outcome": None,
        }
        
        while self.iteration < self.max_iterations and not self.user_satisfied:
            self.iteration += 1
            self._log("iteration", f"Starting iteration {self.iteration}/{self.max_iterations}")
            
            self.state["phase"] = f"iteration_{self.iteration}"
            
            self.rnn.add_step({"type": self.state["phase"], "iteration": self.iteration})
            
            result = task_func(iteration=self.iteration)
            check_result = check_func(result)
            
            iteration_result = {
                "iteration": self.iteration,
                "task_result": result,
                "check_result": check_result,
                "cognitive_state": self.get_state(),
            }
            results["iterations"].append(iteration_result)
            
            if check_result.get("success"):
                if check_result.get("user_satisfied"):
                    self.user_satisfied = True
                    results["success"] = True
                    results["final_outcome"] = check_result.get("outcome")
                    self._log("success", f"Task completed successfully at iteration {self.iteration}")
                    break
            
            issues = check_result.get("issues", [])
            if issues:
                self.state["issues"].extend(issues)
                self._learn_from_issues(issues)
                
                improvements = self.self_improver.get_improvements(str(issues))
                self.state["improvements"].extend(improvements)
            
            loops = self.rnn.detect_loops()
            if loops:
                self._log("warning", f"Loop detected: {loops}")
                if len(loops) > 2:
                    self._log("critical", "Too many loops - breaking cycle")
                    break
            
            suggested = self.rnn.get_next_action()
            if suggested:
                self._log("suggestion", f"RNN suggests: {suggested}")
        
        results["total_iterations"] = self.iteration
        results["cognitive_state"] = self.get_state()
        
        self._save_session(results)
        
        return results
    
    def _learn_from_issues(self, issues: list):
        """Learn from issues encountered"""
        for issue in issues:
            issue_type = issue.get("type", "unknown")
            self.knowledge_graph.learn_from_failure(
                task_type=self.state["current_task"] or "unknown",
                approach=issue_type,
                error=str(issue),
            )
    
    def generate_synthetic_data(self, context: dict, data_type: str = "test_cases") -> str:
        """Use GAN to generate synthetic training/test data"""
        return self.gan.generate(data_type, context)
    
    def add_knowledge(self, concept: str, content: str, category: str = "general"):
        """Add learned knowledge to the graph"""
        blob = self.knowledge_graph.add_learning(concept, content, category)
        self._log("learn", f"Added knowledge: {concept}")
        return blob
    
    def query_knowledge(self, query: str) -> list[dict]:
        """Query the knowledge graph"""
        return self.knowledge_graph.query(query)
    
    def get_state(self) -> dict:
        """Get current cognitive state"""
        return {
            "session_id": self.session_id,
            "iteration": self.iteration,
            "max_iterations": self.max_iterations,
            "user_satisfied": self.user_satisfied,
            "phase": self.state["phase"],
            "current_task": self.state["current_task"],
            "issues_count": len(self.state["issues"]),
            "improvements_count": len(self.state["improvements"]),
            "learnings_count": len(self.state["learnings"]),
            "rnn_analysis": self.rnn.analyze_sequence() if self.rnn else {},
        }
    
    def get_dashboard_data(self) -> dict:
        """Get all data for dashboard visualization"""
        return {
            "cognitive_state": self.get_state(),
            "knowledge_graph": {
                "entities": self.knowledge_graph.stats if self.knowledge_graph else {},
                "recent": self.knowledge_graph.get_recent_learning(10) if self.knowledge_graph else [],
            },
            "meta_cognition": self.meta_cognition.get_self_awareness() if self.meta_cognition else {},
            "memory": {
                "total_episodes": len(self.memory.episodes) if self.memory else 0,
                "patterns": self.memory.get_success_patterns() if self.memory else {},
            },
            "optimizer": {
                "strategies": self.optimizer.get_all_strategies() if self.optimizer else [],
            },
            "entity_registry": self.registry.get_stats() if self.registry else {},
            "cognitive_log": self.cognitive_log[-20:],
        }
    
    def _save_session(self, results: dict):
        """Save session results to memory"""
        session_file = PROJECT_ROOT / ".paradise" / "sessions" / f"{self.session_id}.json"
        session_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(session_file, "w") as f:
            json.dump({
                "session_id": self.session_id,
                "completed_at": datetime.now().isoformat(),
                "results": results,
                "cognitive_state": self.get_state(),
            }, f, indent=2)


_orchestrator = None


def get_orchestrator() -> CognitiveOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = CognitiveOrchestrator()
    return _orchestrator


def initialize_cognition() -> bool:
    """Initialize the cognitive orchestrator"""
    orchestrator = get_orchestrator()
    return orchestrator.initialize()


def main():
    print("🧠 Paradise Cognitive Orchestrator")
    print("=" * 40)
    
    orchestrator = get_orchestrator()
    
    if not orchestrator.initialized:
        success = orchestrator.initialize()
        if not success:
            print("Failed to initialize cognitive systems")
            return
    
    print("\n📊 Current State:")
    state = orchestrator.get_state()
    for key, value in state.items():
        print(f"   {key}: {value}")
    
    print("\n🧪 Testing Cognition:")
    
    thought = orchestrator.think("create a REST API for user authentication")
    print(f"   Strategy: {thought['strategy']['approach']}")
    print(f"   Confidence: {thought['confidence']:.0%}")
    
    print("\n💾 Knowledge Query:")
    orchestrator.add_knowledge("api_design", "REST APIs should use proper HTTP methods", "best_practices")
    results = orchestrator.query_knowledge("api")
    print(f"   Found {len(results)} relevant entries")
    
    print("\n✅ Cognitive Orchestrator Ready!")


if __name__ == "__main__":
    main()
