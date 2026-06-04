#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
# Copyright 2026 agentic-OS Contributors

"""
Paradise Cognition - Meta-Cognition, Self-Reflection, and Strategy Adjustment
Self-awareness, performance monitoring, and adaptive learning
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Optional
from collections import deque

PROJECT_ROOT = Path(os.environ.get("HOST_PROJECT_ROOT", "/app"))


class MetaCognition:
    """Self-awareness and strategic planning for the agent system"""
    
    def __init__(self):
        self.self_model = {
            "capabilities": [
                "code_generation",
                "bug_fixing",
                "refactoring",
                "testing",
                "documentation",
                "planning",
            ],
            "limitations": [
                "no_internet_access",
                "limited_context_window",
                "no_build_verification",
            ],
            "current_focus": None,
            "confidence": 0.8,
        }
        self.thought_history = deque(maxlen=100)
        self.strategy_effectiveness = {}
        self.iteration_memory = deque(maxlen=50)
    
    def think(self, prompt: str) -> dict:
        thought = {
            "timestamp": datetime.now().isoformat(),
            "prompt": prompt,
            "reflection": self._reflect(prompt),
            "strategy": self._select_strategy(prompt),
            "confidence": self._calculate_confidence(prompt),
        }
        self.thought_history.append(thought)
        return thought
    
    def _reflect(self, prompt: str) -> str:
        prompt_lower = prompt.lower()
        
        reflections = []
        
        if any(kw in prompt_lower for kw in ["add", "new", "create", "implement"]):
            reflections.append("Task requires creation of new code. Need to understand scope.")
        
        if any(kw in prompt_lower for kw in ["fix", "bug", "error", "broken"]):
            reflections.append("Task is corrective. Need to identify root cause first.")
        
        if any(kw in prompt_lower for kw in ["refactor", "improve", "optimize"]):
            reflections.append("Task is optimization. Need to measure current state.")
        
        if any(kw in prompt_lower for kw in ["test", "spec"]):
            reflections.append("Task involves verification. Need clear acceptance criteria.")
        
        if len(prompt) < 50:
            reflections.append("Prompt is brief. May need to ask clarifying questions.")
        
        return "; ".join(reflections) or "General task - applying standard approach."
    
    def _select_strategy(self, prompt: str) -> dict:
        prompt_lower = prompt.lower()
        
        if any(kw in prompt_lower for kw in ["api", "endpoint", "route"]):
            strategy = {
                "approach": "api_first",
                "steps": ["define_schema", "implement_routes", "add_tests", "document"],
                "focus": "contract_first_development",
            }
        elif any(kw in prompt_lower for kw in ["frontend", "ui", "dashboard", "component"]):
            strategy = {
                "approach": "component_driven",
                "steps": ["design_components", "build_structure", "add_interactivity", "style"],
                "focus": "user_interface_development",
            }
        elif any(kw in prompt_lower for kw in ["database", "model", "schema", "sql"]):
            strategy = {
                "approach": "data_first",
                "steps": ["design_schema", "implement_models", "add_migrations", "test_queries"],
                "focus": "data_modeling",
            }
        elif any(kw in prompt_lower for kw in ["fix", "bug", "error"]):
            strategy = {
                "approach": "debug_first",
                "steps": ["reproduce", "identify", "fix", "verify"],
                "focus": "problem_solving",
            }
        else:
            strategy = {
                "approach": "standard",
                "steps": ["understand", "plan", "implement", "test", "review"],
                "focus": "general_development",
            }
        
        return strategy
    
    def _calculate_confidence(self, prompt: str) -> float:
        confidence = 0.8
        
        if len(prompt) > 100:
            confidence += 0.1
        
        if any(kw in prompt.lower() for kw in self.self_model["capabilities"]):
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def record_iteration(self, iteration_data: dict):
        self.iteration_memory.append({
            "timestamp": datetime.now().isoformat(),
            **iteration_data,
        })
        
        approach = iteration_data.get("approach", "unknown")
        success = iteration_data.get("success", False)
        
        if approach not in self.strategy_effectiveness:
            self.strategy_effectiveness[approach] = {"success": 0, "failure": 0}
        
        if success:
            self.strategy_effectiveness[approach]["success"] += 1
        else:
            self.strategy_effectiveness[approach]["failure"] += 1
    
    def get_best_strategy(self, task_type: str) -> Optional[dict]:
        if task_type in self.strategy_effectiveness:
            stats = self.strategy_effectiveness[task_type]
            total = stats["success"] + stats["failure"]
            if total > 0:
                success_rate = stats["success"] / total
                if success_rate > 0.6:
                    return {"approach": task_type, "success_rate": success_rate}
        
        return None
    
    def adjust_strategy(self, current_strategy: dict, feedback: dict) -> dict:
        adjusted = current_strategy.copy()
        
        if feedback.get("type") == "repetitive_failures":
            adjusted["steps"] = ["analyze_root_cause", "simplify_approach"] + adjusted["steps"][:3]
            adjusted["focus"] = "breakthrough_mode"
        
        if feedback.get("type") == "over_complexity":
            adjusted["steps"] = adjusted["steps"][:3]
            adjusted["focus"] = "minimal_viable"
        
        if feedback.get("type") == "low_confidence":
            adjusted["confidence_threshold"] = 0.5
            adjusted["steps"].insert(0, "gather_requirements")
        
        return adjusted
    
    def get_self_awareness(self) -> dict:
        return {
            "self_model": self.self_model,
            "recent_thoughts": list(self.thought_history)[-5:],
            "strategy_effectiveness": self.strategy_effectiveness,
            "total_iterations": len(self.iteration_memory),
        }


class RAGEngine:
    """Retrieval Augmented Generation - Ground responses in documents"""
    
    def __init__(self):
        self.documents = {}
        self.embeddings = {}
        self.index = {}
    
    def add_document(self, doc_id: str, content: str, metadata: Optional[dict] = None):
        self.documents[doc_id] = {
            "content": content,
            "metadata": metadata or {},
            "added_at": datetime.now().isoformat(),
        }
        self._update_index(doc_id, content)
    
    def _update_index(self, doc_id: str, content: str):
        words = content.lower().split()
        for word in words:
            if len(word) > 3:
                if word not in self.index:
                    self.index[word] = []
                if doc_id not in self.index[word]:
                    self.index[word].append(doc_id)
    
    def retrieve(self, query: str, top_k: int = 5) -> list[dict]:
        query_words = query.lower().split()
        scores = {}
        
        for word in query_words:
            if len(word) > 3:
                for doc_id in self.index.get(word, []):
                    scores[doc_id] = scores.get(doc_id, 0) + 1
        
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        results = []
        for doc_id, score in ranked[:top_k]:
            if doc_id in self.documents:
                results.append({
                    "doc_id": doc_id,
                    "content": self.documents[doc_id]["content"][:500],
                    "score": score,
                    "metadata": self.documents[doc_id]["metadata"],
                })
        
        return results
    
    def get_context(self, query: str, max_chars: int = 2000) -> str:
        results = self.retrieve(query, top_k=3)
        context = []
        remaining = max_chars
        
        for result in results:
            if remaining <= 0:
                break
            chunk = result["content"][:remaining]
            context.append(chunk)
            remaining -= len(chunk)
        
        return "\n\n".join(context)


class GANGenerator:
    """Generative Adversarial Network - Generate synthetic training data"""
    
    def __init__(self):
        self.generators = {
            "test_cases": self._generate_test_case,
            "code_snippets": self._generate_code_snippet,
            "documentation": self._generate_docs,
        }
        self.generated_samples = []
    
    def _generate_test_case(self, context: dict) -> str:
        template = '''def test_{name}(self):
    """Test {description}"""
    {setup}
    result = {function_call}
    assert result == {expected}
'''
        return template.format(**context)
    
    def _generate_code_snippet(self, context: dict) -> str:
        template = '''def {name}({params}):
    """{description}"""
    {body}
    return {return_value}
'''
        return template.format(**context)
    
    def _generate_docs(self, context: dict) -> str:
        return f'''# {context.get('name', 'Component')}

## Description
{context.get('description', 'No description provided.')}

## Usage
```python
{context.get('example', '# Add example here')}
```

## Parameters
{context.get('params', 'None')}
'''
    
    def generate(self, sample_type: str, context: dict) -> str:
        if sample_type in self.generators:
            sample = self.generators[sample_type](context)
            self.generated_samples.append({
                "type": sample_type,
                "context": context,
                "generated": sample,
                "timestamp": datetime.now().isoformat(),
            })
            return sample
        return f"# Generated {sample_type} placeholder"


class RNNProcessor:
    """RNN-based sequence processor for temporal patterns and loops"""
    
    def __init__(self):
        self.sequence_buffer = deque(maxlen=1000)
        self.patterns = {}
        self.loop_detector = LoopDetector()
    
    def add_step(self, step_data: dict):
        self.sequence_buffer.append({
            "timestamp": datetime.now().isoformat(),
            **step_data,
        })
        
        step_type = step_data.get("type", "unknown")
        if step_type not in self.patterns:
            self.patterns[step_type] = {"count": 0, "success": 0}
        self.patterns[step_type]["count"] += 1
        
        if step_data.get("success"):
            self.patterns[step_type]["success"] += 1
    
    def detect_loops(self) -> list[dict]:
        loop_candidates = []
        
        for step_type, stats in self.patterns.items():
            if stats["count"] > 5:
                success_rate = stats["success"] / stats["count"]
                if success_rate < 0.3:
                    loop_candidates.append({
                        "type": step_type,
                        "iterations": stats["count"],
                        "success_rate": success_rate,
                        "suggestion": "Consider alternative approach",
                    })
        
        return loop_candidates
    
    def get_next_action(self) -> Optional[str]:
        recent = list(self.sequence_buffer)[-10:]
        
        types = [s.get("type") for s in recent]
        
        if types.count("lint") > 3 and types.count("fix") > 3:
            return "escalate_to_human"
        
        if types.count("test") > types.count("implement"):
            return "focus_on_implementation"
        
        return None
    
    def analyze_sequence(self) -> dict:
        return {
            "total_steps": len(self.sequence_buffer),
            "pattern_stats": self.patterns,
            "loops": self.detect_loops(),
            "suggested_action": self.get_next_action(),
            "recent_sequence": [s.get("type") for s in list(self.sequence_buffer)[-5:]],
        }


class LoopDetector:
    """Detect repetitive patterns that indicate stuck states"""
    
    def __init__(self):
        self.state_history = deque(maxlen=20)
        self.stuck_threshold = 5
    
    def record_state(self, state: str):
        self.state_history.append({
            "state": state,
            "timestamp": datetime.now().isoformat(),
        })
    
    def is_stuck(self) -> bool:
        if len(self.state_history) < self.stuck_threshold:
            return False
        
        recent = [s["state"] for s in list(self.state_history)[-self.stuck_threshold:]]
        return len(set(recent)) == 1
    
    def get_stuck_info(self) -> Optional[dict]:
        if self.is_stuck():
            return {
                "stuck": True,
                "state": self.state_history[-1]["state"],
                "iterations": len(self.state_history),
                "recommendation": "Break the loop - try a different approach",
            }
        return None


_cognition_instance = None
_rag_instance = None
_gan_instance = None
_rnn_instance = None


def get_meta_cognition() -> MetaCognition:
    global _cognition_instance
    if _cognition_instance is None:
        _cognition_instance = MetaCognition()
    return _cognition_instance


def get_rag() -> RAGEngine:
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = RAGEngine()
    return _rag_instance


def get_gan() -> GANGenerator:
    global _gan_instance
    if _gan_instance is None:
        _gan_instance = GANGenerator()
    return _gan_instance


def get_rnn() -> RNNProcessor:
    global _rnn_instance
    if _rnn_instance is None:
        _rnn_instance = RNNProcessor()
    return _rnn_instance


def main():
    print("🧠 Paradise Meta-Cognition")
    print("=" * 40)
    
    meta = get_meta_cognition()
    rag = get_rag()
    get_gan()
    rnn = get_rnn()
    
    print("\n📊 System Capabilities:")
    for cap in meta.self_model["capabilities"]:
        print(f"   ✓ {cap}")
    
    print("\n💭 Sample Thought:")
    thought = meta.think("create a REST API for user management")
    print(f"   Strategy: {thought['strategy']['approach']}")
    print(f"   Confidence: {thought['confidence']:.0%}")
    
    print("\n📚 RAG - Document Retrieval:")
    rag.add_document("api_design", "REST APIs use HTTP methods: GET, POST, PUT, DELETE")
    rag.add_document("auth_patterns", "JWT tokens for stateless authentication")
    results = rag.retrieve("authentication")
    print(f"   Found {len(results)} relevant documents")
    
    print("\n🔄 RNN Sequence Analysis:")
    rnn.add_step({"type": "implement", "success": True})
    rnn.add_step({"type": "test", "success": False})
    rnn.add_step({"type": "fix", "success": False})
    analysis = rnn.analyze_sequence()
    print(f"   Total steps: {analysis['total_steps']}")
    print(f"   Suggested action: {analysis['suggested_action']}")


if __name__ == "__main__":
    main()
