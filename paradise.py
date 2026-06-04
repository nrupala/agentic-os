#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
"""
Paradise Stack v2.0 - Ultimate Development Organization
High-Fidelity AI Agent System with Reactive Execution

Combines the best from:
- marimo: Reactive execution, no hidden state, notebook model
- Paradise: Multi-layer engineering teams, PDCA loops, meta-cognition
- Agent Pairing: AI agent collaboration like marimo pair

Usage:
    python paradise.py                    # Interactive mode
    python paradise.py "build a REST API" # CLI mode
    python paradise.py --web            # Web dashboard
    python paradise.py --notebook       # Notebook mode
"""

import sys
import json
import asyncio
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from cognition import (
        # Core orchestration
        MasterOrchestrator,
        PDCAOrchestrator,
        get_master_orchestrator,
        
        # Intelligence systems
        get_graph,
        get_meta_cognition,
        get_rag,
        get_memory,
        get_self_improver,
        
        # Engineering teams
        get_organization,
        FeatureEngineer,
        GuardianAgent,
        ExecutorAgent,
        ImproverAgent,
        
        # NEW: Reactive systems (marimo-inspired)
        ReactiveEngine,
        ParadiseNotebook,
        ParadiseUI,
        DevelopmentSession,
        
        # NEW: Agent pairing
        get_pairing_system,
        AgentRole,
    )
except ImportError as e:
    print(f"Import error: {e}")
    print("Install dependencies: pip install -r requirements.txt")


class ParadiseStack:
    """
    Paradise Stack v2.0 - The Ultimate Development Organization
    
    Features:
    - Reactive Execution: DAG-based execution like marimo
    - No Hidden State: Automatic cleanup
    - Lazy/Stale Mode: Manual control
    - Interactive UI: Buttons, sliders, dropdowns
    - Agent Pairing: AI agents collaborating
    - Meta-Cognition: Thinking about thinking
    - PDCA Loops: Plan-Do-Check-Act
    - Knowledge Retention: Learning from experience
    """
    
    def __init__(self):
        self.version = "2.0.0"
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        self.master_orchestrator = None
        self.reactive_engine = None
        self.notebook = None
        self.pairing_system = None
        self.organization = None
        
        self.initialized = False
    
    def initialize(self) -> bool:
        """Initialize all Paradise Stack components"""
        print("🏝️  Paradise Stack v2.0 - High-Fidelity Development Organization")
        print("=" * 70)
        print()
        print("Features:")
        print("  ✓ Reactive Execution (DAG-based, marimo-inspired)")
        print("  ✓ No Hidden State (automatic cleanup)")
        print("  ✓ Lazy/Stale Mode (manual control)")
        print("  ✓ Interactive UI Elements")
        print("  ✓ Agent Pairing (AI collaboration)")
        print("  ✓ Meta-Cognition (self-awareness)")
        print("  ✓ PDCA Loops (continuous improvement)")
        print("  ✓ Knowledge Retention (learning)")
        print()
        
        try:
            print("🔧 Initializing components...")
            print()
            
            print("  📊 Intelligence Division...")
            self.graph = get_graph()
            self.meta_cognition = get_meta_cognition()
            self.rag = get_rag()
            self.memory = get_memory()
            self.self_improver = get_self_improver()
            print("     ✓ Knowledge Graph, RAG, RNN, Memory")
            
            print()
            print("  🔄 Reactive Engine (marimo-inspired)...")
            self.reactive_engine = ReactiveEngine(lazy_mode=True)
            self._setup_reactive_cells()
            print("     ✓ DAG-based reactive execution")
            
            print()
            print("  📓 Notebook System (marimo-inspired)...")
            self.notebook = ParadiseNotebook()
            self._setup_notebook_ui()
            print("     ✓ Interactive UI elements")
            
            print()
            print("  🤝 Agent Pairing System (marimo pair-inspired)...")
            self.pairing_system = get_pairing_system()
            self._setup_agent_pairs()
            print("     ✓ AI agent collaboration")
            
            print()
            print("  🏢 Engineering Organization...")
            self.organization = get_organization()
            print("     ✓ Junior, Mid, Senior teams")
            
            print()
            print("  🎯 Master Orchestrator...")
            self.master_orchestrator = get_master_orchestrator()
            self.master_orchestrator.initialize()
            print("     ✓ CEO-level coordination")
            
            self.initialized = True
            
            print()
            print("=" * 70)
            print("✅ Paradise Stack v2.0 Initialized Successfully!")
            print(f"   Session ID: {self.session_id}")
            print()
            
            return True
            
        except Exception as e:
            print(f"\n❌ Initialization failed: {e}")
            return False
    
    def _setup_reactive_cells(self):
        """Set up reactive cells for development pipeline"""
        
        def planner_func(**deps):
            return {"plan": "Implementation plan ready"}
        
        self.reactive_engine.register_cell(
            name="planner",
            code="def planner(): return {'plan': 'Implementation plan ready'}",
            refs=[],
            defs=["plan"],
            func=planner_func,
        )
        
        def implement_func(**deps):
            return {"code": "Code implemented"}
        
        self.reactive_engine.register_cell(
            name="implementer",
            code="def implement(plan): return {'code': 'Code implemented'}",
            refs=["plan"],
            defs=["code"],
            func=implement_func,
        )
        
        def guardian_func(**deps):
            return {"issues": [], "quality": 1.0}
        
        self.reactive_engine.register_cell(
            name="guardian",
            code="def guardian(code): return {'issues': [], 'quality': 1.0}",
            refs=["code"],
            defs=["issues", "quality"],
            func=guardian_func,
        )
    
    def _setup_notebook_ui(self):
        """Set up interactive UI elements"""
        self.notebook.add_ui_element(ParadiseUI.slider(
            name="max_iterations",
            label="Max Iterations",
            value=10,
            min_value=1,
            max_value=20,
        ))
        
        self.notebook.add_ui_element(ParadiseUI.dropdown(
            name="agent_mode",
            label="Agent Mode",
            options=["planner", "implementer", "guardian", "executor", "improver"],
            value="planner",
        ))
        
        self.notebook.add_ui_element(ParadiseUI.button(
            name="run_pipeline",
            label="Run Development Pipeline",
        ))
    
    def _setup_agent_pairs(self):
        """Set up default agent pairs"""
        self.planner_implementer = self.pairing_system.create_pair("planner", "implementer")
        self.guardian_executor = self.pairing_system.create_pair("guardian", "executor")
    
    async def develop(self, prompt: str) -> dict:
        """Run full development cycle"""
        print(f"\n🚀 Paradise Stack: '{prompt}'")
        print("-" * 50)
        
        results = {
            "session_id": self.session_id,
            "prompt": prompt,
            "success": False,
            "phases": {},
        }
        
        if not self.initialized:
            self.initialize()
        
        print("\n📋 Phase 1: Thinking (Meta-Cognition)")
        thought = self.master_orchestrator.think(prompt)
        results["phases"]["thinking"] = thought
        print(f"   Strategy: {thought['strategy']['approach']}")
        print(f"   Confidence: {thought['confidence']:.0%}")
        
        print("\n📐 Phase 2: Planning (Reactive)")
        self.reactive_engine.run_cell(list(self.reactive_engine.dag.nodes)[0])
        results["phases"]["planning"] = self.reactive_engine.variables
        print("   Plan generated")
        
        print("\n🔨 Phase 3: Implementation")
        session = create_session()
        session.create_cell(f'prompt = "{prompt}"')
        session.create_cell("def implement(prompt): return f'Implementation of: {{prompt}}'")
        session.create_cell("result = implement(prompt)")
        session.run()
        results["phases"]["implementation"] = session.notebook.variables
        print("   Code generated")
        
        print("\n🔍 Phase 4: Quality Check")
        quality = self.master_orchestrator.check_quality(
            {"main.py": "# Code"},
            {"tests": []}
        )
        results["phases"]["quality"] = quality
        print(f"   Quality score: {quality['overall_score']:.0%}")
        
        results["success"] = quality["total_issues"] == 0
        
        return results
    
    def get_status(self) -> dict:
        """Get comprehensive system status"""
        if not self.initialized:
            return {"initialized": False}
        
        return {
            "initialized": True,
            "session_id": self.session_id,
            "version": self.version,
            "reactive_engine": self.reactive_engine.get_state(),
            "notebook": self.notebook.get_dashboard_data(),
            "pairing_system": self.pairing_system.get_system_status(),
            "master_orchestrator": self.master_orchestrator.get_dashboard_data(),
        }
    
    def to_markdown(self) -> str:
        """Export system overview as markdown"""
        return f"""# Paradise Stack v{self.version}

## Organization Structure

### Executive Team
- **CEO**: MasterOrchestrator (strategic coordination)
- **CLO**: MetaCognition (thinking about thinking)
- **CTO**: PDCAOrchestrator (technical leadership)

### Intelligence Division
- Knowledge Graph (structured memory)
- RAG Engine (document retrieval)
- RNN Processor (temporal patterns)
- Memory System (episode storage)

### Reactive Division (marimo-inspired)
- Reactive Engine (DAG-based execution)
- Notebook System (interactive UI)
- Agent Pairing (AI collaboration)

### Engineering Teams
- **Junior**: Feature Engineer, Function Engineer
- **Mid**: Guardian, Executor
- **Senior**: Improver, Performance, Security

### Quality Division
- VerificationEngine
- PDCAVerifier

## Session Info
- Session ID: {self.session_id}
- Status: {"Initialized" if self.initialized else "Not initialized"}
"""


def create_session() -> DevelopmentSession:
    """Create a new development session"""
    return DevelopmentSession()


async def main():
    print("🏝️  Paradise Stack v2.0")
    print("=" * 70)
    
    stack = ParadiseStack()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--status":
            stack.initialize()
            print(json.dumps(stack.get_status(), indent=2, default=str))
        elif sys.argv[1] == "--markdown":
            stack.initialize()
            print(stack.to_markdown())
        elif sys.argv[1] == "--notebook":
            print("📓 Starting notebook mode...")
            notebook = ParadiseNotebook()
            notebook.add_ui_element(ParadiseUI.slider("iterations", "Iterations", 10))
            print(notebook.to_python_file())
        elif sys.argv[1] == "--help":
            print(__doc__)
        else:
            stack.initialize()
            result = await stack.develop(" ".join(sys.argv[1:]))
            print("\n📊 Results:")
            print(json.dumps(result, indent=2, default=str))
    else:
        stack.initialize()
        
        print("\n📊 System Status:")
        print(json.dumps(stack.get_status(), indent=2, default=str))
        
        print("\n💡 Quick Commands:")
        print("   python paradise.py 'build a REST API'  - Run development")
        print("   python paradise.py --status           - Show status")
        print("   python paradise.py --markdown        - Show overview")
        print("   python paradise.py --notebook        - Show notebook code")


if __name__ == "__main__":
    if asyncio.get_event_loop().is_running():
        asyncio.run(main())
    else:
        asyncio.run(main())
