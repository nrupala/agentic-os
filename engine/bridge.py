#!/usr/bin/env python3
"""
agentic-OS: Plan → Omega Bridge
================================
The critical connection between Paradise Planning Layer and OMEGA Execution Layer.

This bridge:
1. Receives parsed plans from Paradise Stack
2. Transforms them into Omega execution context
3. Wires up all required subsystems
4. Hands off to OmegaForge for recursive execution

Flow:
    User Request → Planner → Analyzer → Bridge → OmegaForge → User Validation
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "engine"))
sys.path.insert(0, str(PROJECT_ROOT / "security"))
sys.path.insert(0, str(PROJECT_ROOT / "cognition"))


class RequestType(Enum):
    FEATURE_ADD = "feature_add"
    BUG_FIX = "bug_fix"
    REFACTOR = "refactor"
    API = "api"
    FRONTEND = "frontend"
    DATABASE = "database"
    AUTH = "auth"
    TEST = "test"
    DEPLOY = "deploy"
    ML = "ml"
    GENERAL = "general"


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PLANNING = "in_planning"
    IN_EXECUTION = "in_execution"
    VALIDATING = "validating"
    SUCCESS = "success"
    REJECTED = "rejected"
    FAILED = "failed"
    MAX_ITERATIONS = "max_iterations"


@dataclass
class PlanContext:
    """Context from Paradise Planning Layer."""
    goal: str
    request_type: RequestType
    steps: List[str]
    files_to_create: List[str]
    files_to_modify: List[str]
    detected_patterns: List[str] = field(default_factory=list)
    constraints: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            "goal": self.goal,
            "request_type": self.request_type.value,
            "steps": self.steps,
            "files_to_create": self.files_to_create,
            "files_to_modify": self.files_to_modify,
            "detected_patterns": self.detected_patterns,
            "constraints": self.constraints,
            "metadata": self.metadata,
        }


@dataclass
class OmegaContext:
    """Context transformed for OMEGA Execution Layer."""
    goal: str
    max_iterations: int = 50
    patterns: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    strategy: str = "standard"
    files_to_create: List[str] = field(default_factory=list)
    files_to_modify: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    plan_context: Optional[PlanContext] = None
    
    def to_dict(self) -> dict:
        return {
            "goal": self.goal,
            "max_iterations": self.max_iterations,
            "patterns": self.patterns,
            "constraints": self.constraints,
            "strategy": self.strategy,
            "files_to_create": self.files_to_create,
            "files_to_modify": self.files_to_modify,
            "metadata": self.metadata,
        }


@dataclass
class ExecutionState:
    """State maintained during execution."""
    state_id: str
    plan_context: PlanContext
    omega_context: OmegaContext
    status: TaskStatus
    iteration: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    user_validation: Optional[str] = None
    output_files: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "state_id": self.state_id,
            "plan_context": self.plan_context.to_dict(),
            "omega_context": self.omega_context.to_dict(),
            "status": self.status.value,
            "iteration": self.iteration,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "user_validation": self.user_validation,
            "output_files": self.output_files,
            "errors": self.errors,
        }


class PlanToOmegaBridge:
    """
    THE BRIDGE - Converts Paradise Plan to OMEGA Execution Context.
    
    Handshake Protocol:
    
    PLANNING LAYER                    BRIDGE                          OMEGA LAYER
    ─────────────                    ──────                          ───────────
    
    [Plan Generated] ──────────────► [Parse Plan]
                                    [Extract Context]
                                    [Transform to Omega]
                                    [Wire Subsystems]
                                                       ──────────────► [StateSnapshot Created]
                                                       ◄────────────── [Ready to Execute]
    """
    
    def __init__(self, project_name: str = None):
        self.project_name = project_name or os.getenv("PROJECT_NAME", "default")
        self.project_path = PROJECT_ROOT / "projects" / self.project_name
        self.state_file = self.project_path / "state" / "bridge_state.json"
        
        self.subsystems = {}
        self.current_state: Optional[ExecutionState] = None
        
        self._ensure_dirs()
        self._init_subsystems()
    
    def _ensure_dirs(self):
        """Ensure required directories exist."""
        dirs = ["state", "memory", "logs", "outputs"]
        for d in dirs:
            (self.project_path / d).mkdir(parents=True, exist_ok=True)
    
    def _init_subsystems(self):
        """Initialize bridge subsystems."""
        print("[BRIDGE] Initializing subsystems...")
        
        # Initialize cognitive subsystems
        try:
            from omega_meta_logic import MetaCognition
            db_path = str(self.project_path / "state" / "omega.db")
            self.subsystems["meta"] = MetaCognition(db_path)
            print("  [OK] Meta-Cognition")
        except Exception as e:
            print(f"  [FAIL] Meta-Cognition: {e}")
            self.subsystems["meta"] = None
        
        try:
            from omega_hierarchical_memory import HierarchicalMemory
            self.subsystems["memory"] = HierarchicalMemory(str(self.project_path))
            print("  [OK] Hierarchical Memory")
        except Exception as e:
            print(f"  [FAIL] Memory: {e}")
            self.subsystems["memory"] = None
        
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
        
        # Initialize security subsystems
        try:
            from omega_access import AccessControl
            self.subsystems["access"] = AccessControl(str(PROJECT_ROOT / "system_scripts"))
            print("  [OK] Access Control")
        except Exception as e:
            print(f"  [FAIL] Access Control: {e}")
            self.subsystems["access"] = None
        
        try:
            from omega_audit import AuditTrail
            self.subsystems["audit"] = AuditTrail(str(self.project_path))
            print("  [OK] Audit Trail")
        except Exception as e:
            print(f"  [FAIL] Audit Trail: {e}")
            self.subsystems["audit"] = None
        
        # Initialize Paradise Stack components
        try:
            from cognition.knowledge_graph import get_graph
            self.subsystems["knowledge_graph"] = get_graph()
            print("  [OK] Knowledge Graph")
        except Exception as e:
            print(f"  [FAIL] Knowledge Graph: {e}")
            self.subsystems["knowledge_graph"] = None
        
        try:
            from cognition.master_orchestrator import get_master_orchestrator
            self.subsystems["orchestrator"] = get_master_orchestrator()
            print("  [OK] Master Orchestrator")
        except Exception as e:
            print(f"  [FAIL] Master Orchestrator: {e}")
            self.subsystems["orchestrator"] = None
        
        print(f"[BRIDGE] {len([s for s in self.subsystems.values() if s])}/{len(self.subsystems)} subsystems active")
    
    def parse_plan(self, plan_json: Dict) -> PlanContext:
        """Parse plan from Paradise Planner."""
        print(f"\n[BRIDGE] Parsing plan for: {plan_json.get('goal', 'unknown')[:50]}...")
        
        request_type = RequestType(plan_json.get("request_type", "general"))
        
        plan_context = PlanContext(
            goal=plan_json.get("goal", ""),
            request_type=request_type,
            steps=plan_json.get("steps", []),
            files_to_create=plan_json.get("files_to_create", []),
            files_to_modify=plan_json.get("files_to_modify", []),
            detected_patterns=plan_json.get("detected_patterns", []),
            constraints=plan_json.get("constraints", {}),
            metadata=plan_json.get("metadata", {}),
        )
        
        print(f"  [OK] Request Type: {request_type.value}")
        print(f"  [OK] Steps: {len(plan_context.steps)}")
        print(f"  [OK] Files to Create: {len(plan_context.files_to_create)}")
        print(f"  [OK] Files to Modify: {len(plan_context.files_to_modify)}")
        
        return plan_context
    
    def transform_to_omega(self, plan_context: PlanContext) -> OmegaContext:
        """Transform PlanContext to OmegaContext."""
        print("\n[BRIDGE] Transforming plan to Omega context...")
        
        # Extract constraints from plan
        constraints = self._extract_constraints(plan_context)
        
        # Select execution strategy
        strategy = self._select_strategy(plan_context)
        
        # Transform patterns
        patterns = self._transform_patterns(plan_context)
        
        omega_context = OmegaContext(
            goal=plan_context.goal,
            max_iterations=50,
            patterns=patterns,
            constraints=constraints,
            strategy=strategy,
            files_to_create=plan_context.files_to_create,
            files_to_modify=plan_context.files_to_modify,
            metadata={
                "request_type": plan_context.request_type.value,
                "source": "paradise_planner",
                "bridge_version": "1.0",
            },
            plan_context=plan_context,
        )
        
        print(f"  [OK] Strategy: {strategy}")
        print(f"  [OK] Constraints: {len(constraints)}")
        print(f"  [OK] Patterns: {len(patterns)}")
        
        return omega_context
    
    def _extract_constraints(self, plan_context: PlanContext) -> List[str]:
        """Extract constraints from plan context."""
        constraints = []
        
        # Add default constraints
        constraints.extend([
            "Error handling required",
            "Type hints required",
            "Documentation required",
        ])
        
        # Add type-specific constraints
        if plan_context.request_type == RequestType.API:
            constraints.extend([
                "RESTful conventions",
                "Input validation",
                "Error responses",
            ])
        elif plan_context.request_type == RequestType.AUTH:
            constraints.extend([
                "Password hashing required",
                "JWT validation",
                "SQL injection prevention",
            ])
        elif plan_context.request_type == RequestType.FRONTEND:
            constraints.extend([
                "Responsive design",
                "Accessibility compliance",
                "Performance optimization",
            ])
        
        # Add detected patterns as constraints
        for pattern in plan_context.detected_patterns:
            constraints.append(f"Pattern: {pattern}")
        
        return constraints
    
    def _select_strategy(self, plan_context: PlanContext) -> str:
        """Select execution strategy based on request type."""
        strategies = {
            RequestType.FEATURE_ADD: "incremental",
            RequestType.BUG_FIX: "diagnostic",
            RequestType.REFACTOR: "conservative",
            RequestType.API: "contract_first",
            RequestType.FRONTEND: "component_driven",
            RequestType.DATABASE: "schema_first",
            RequestType.AUTH: "security_first",
            RequestType.TEST: "test_driven",
            RequestType.DEPLOY: "infrastructure_first",
            RequestType.ML: "experiment_tracking",
            RequestType.GENERAL: "standard",
        }
        return strategies.get(plan_context.request_type, "standard")
    
    def _transform_patterns(self, plan_context: PlanContext) -> List[str]:
        """Transform detected patterns for Omega execution."""
        patterns = []
        
        # Add request type pattern
        patterns.append(f"type:{plan_context.request_type.value}")
        
        # Add detected patterns
        patterns.extend(plan_context.detected_patterns)
        
        # Add knowledge graph patterns if available
        if self.subsystems.get("knowledge_graph"):
            best_pattern = self.subsystems["knowledge_graph"].get_best_pattern(
                plan_context.request_type.value
            )
            if best_pattern:
                patterns.append(f"learned:{best_pattern.name}")
        
        return patterns
    
    def create_execution_state(self, omega_context: OmegaContext) -> ExecutionState:
        """Create execution state for tracking."""
        state_id = f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        state = ExecutionState(
            state_id=state_id,
            plan_context=omega_context.plan_context,
            omega_context=omega_context,
            status=TaskStatus.PENDING,
        )
        
        self.current_state = state
        self._save_state(state)
        
        print(f"\n[BRIDGE] Execution state created: {state_id}")
        return state
    
    def wire_omega_forge(self, omega_context: OmegaContext) -> 'OmegaForge':
        """Wire up OmegaForge with all required context."""
        print("\n[BRIDGE] Wiring OmegaForge...")
        
        from omega_forge import OmegaForge
        
        # Create OmegaForge instance
        forge = OmegaForge(self.project_name)
        
        # Wire meta-cognition
        if self.subsystems.get("meta"):
            forge.meta = self.subsystems["meta"]
            print("  [OK] Meta-Cognition wired")
        
        # Wire GAN
        if self.subsystems.get("gan"):
            forge.gan = self.subsystems["gan"]
            print("  [OK] GAN wired")
        
        # Wire RAG
        if self.subsystems.get("rag"):
            forge.rag = self.subsystems["rag"]
            print("  [OK] RAG wired")
        
        # Wire memory
        if self.subsystems.get("memory"):
            forge.memory = self.subsystems["memory"]
            print("  [OK] Memory wired")
        
        # Wire knowledge graph
        if self.subsystems.get("knowledge_graph"):
            forge.knowledge_graph = self.subsystems["knowledge_graph"]
            print("  [OK] Knowledge Graph wired")
        
        # Set execution strategy
        forge.strategy = omega_context.strategy
        
        print("  [OK] OmegaForge ready")
        
        return forge
    
    def execute(
        self,
        plan_json: Dict,
        max_iterations: int = 50,
        interactive: bool = True,
    ) -> ExecutionState:
        """
        Execute plan through the full Pipeline: Plan → Bridge → Omega → User Validation.
        
        Args:
            plan_json: Parsed plan from Paradise Planner
            max_iterations: Maximum iterations for Omega loop
            interactive: Whether to prompt for user validation
        
        Returns:
            ExecutionState with results
        """
        print("\n" + "=" * 70)
        print("BRIDGE: PLAN -> OMEGA EXECUTION PIPELINE")
        print("=" * 70)
        
        # Phase 1: Parse Plan
        print("\n[PHASE 1/4] PARSING PLAN FROM PARADISE")
        plan_context = self.parse_plan(plan_json)
        
        # Phase 2: Transform to Omega Context
        print("\n[PHASE 2/4] TRANSFORMING TO OMEGA CONTEXT")
        omega_context = self.transform_to_omega(plan_context)
        omega_context.max_iterations = max_iterations
        
        # Phase 3: Create Execution State
        print("\n[PHASE 3/4] CREATING EXECUTION STATE")
        state = self.create_execution_state(omega_context)
        state.status = TaskStatus.IN_EXECUTION
        
        # Phase 4: Execute with OmegaForge
        print("\n[PHASE 4/4] EXECUTING WITH OMEGA FORGE")
        forge = self.wire_omega_forge(omega_context)
        
        iteration = 0
        success = False
        output_code = None
        
        while iteration < max_iterations:
            iteration += 1
            state.iteration = iteration
            self._save_state(state)
            
            print(f"\n{'-' * 60}")
            print(f"  ITERATION {iteration}/{max_iterations}")
            print(f"{'-' * 60}")
            
            # Recursive loop: RECOLLECT -> THINK -> GENERATE -> VERIFY -> PERSIST
            try:
                # RECOLLECT: Load context
                state_snapshot = forge.recollect(plan_context.goal)
                
                # THINK: Meta-cognition analysis
                if self.subsystems.get("meta"):
                    patterns = self.subsystems["meta"].analyze_failure_patterns()
                    constraints = self.subsystems["meta"].derive_constraints(patterns)
                else:
                    constraints = omega_context.constraints
                
                # GENERATE: Use GAN to generate/refine code
                if self.subsystems.get("gan"):
                    code, evaluation = self.subsystems["gan"].generate_and_refine(
                        plan_context.goal,
                        constraints
                    )
                else:
                    code = f"# Generated code for: {plan_context.goal}"
                    evaluation = {"score": 0.5, "passed": False}
                
                output_code = code
                
                # VERIFY: Check if generation passed
                if evaluation.get("passed", False) or evaluation.get("score", 0) >= 0.7:
                    success = True
                    print(f"\n[SUCCESS] Code generated with score: {evaluation.get('score', 0):.2f}")
                    
                    # PERSIST: Save outputs
                    forge.persist(state_snapshot)
                    state.output_files = self._save_outputs(code, plan_context)
                    
                    break
                
                print(f"[RETRY] Score: {evaluation.get('score', 0):.2f} < 0.7")
                
                # Store pattern for learning
                if self.subsystems.get("knowledge_graph"):
                    self.subsystems["knowledge_graph"].learn_from_failure(
                        task_type=plan_context.request_type.value,
                        approach=omega_context.strategy,
                        error=f"Score: {evaluation.get('score', 0):.2f}",
                    )
                
            except Exception as e:
                print(f"[ERROR] Iteration {iteration}: {e}")
                state.errors.append(str(e))
                self._save_state(state)
        
        # Update final state
        if success:
            state.status = TaskStatus.SUCCESS
            if self.subsystems.get("knowledge_graph"):
                self.subsystems["knowledge_graph"].learn_from_success(
                    task_type=plan_context.request_type.value,
                    approach=omega_context.strategy,
                    outcome={"iterations": iteration},
                )
        elif iteration >= max_iterations:
            state.status = TaskStatus.MAX_ITERATIONS
        else:
            state.status = TaskStatus.FAILED
        
        state.updated_at = datetime.now().isoformat()
        self._save_state(state)
        
        # User Validation Gate
        if interactive and success:
            state = self._prompt_user_validation(state, output_code)
        
        # Cleanup
        forge.close()
        
        print("\n" + "=" * 70)
        print(f"EXECUTION COMPLETE")
        print(f"  Status: {state.status.value}")
        print(f"  Iterations: {state.iteration}")
        print(f"  Output Files: {len(state.output_files)}")
        print(f"  User Validation: {state.user_validation or 'N/A'}")
        print("=" * 70)
        
        return state
    
    def _save_outputs(self, code: str, plan_context: PlanContext) -> List[str]:
        """Save generated code to output files."""
        output_files = []
        output_dir = self.project_path / "outputs"
        output_dir.mkdir(exist_ok=True)
        
        # Save main code file
        for file_path in plan_context.files_to_create:
            if file_path.endswith(('.py', '.js', '.ts', '.tsx', '.jsx')):
                full_path = output_dir / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(code, encoding='utf-8')
                output_files.append(str(full_path))
                break
        
        # If no specific file, save as main code
        if not output_files:
            main_file = output_dir / "generated_code.py"
            main_file.write_text(code, encoding='utf-8')
            output_files.append(str(main_file))
        
        return output_files
    
    def _prompt_user_validation(self, state: ExecutionState, code: str) -> ExecutionState:
        """Prompt user for validation of generated output."""
        print("\n" + "=" * 70)
        print("USER VALIDATION GATE")
        print("=" * 70)
        
        print(f"\nGenerated Code Preview (first 500 chars):")
        print("-" * 50)
        print(code[:500] + "..." if len(code) > 500 else code)
        print("-" * 50)
        
        print("\nOptions:")
        print("  [ACCEPT] - Accept output and finalize")
        print("  [REFINE] - Request refinement (continues loop)")
        print("  [REJECT] - Reject and abort")
        
        try:
            choice = input("\nYour choice (accept/refine/reject): ").strip().lower()
        except EOFError:
            choice = "accept"
        
        if choice.startswith("a") or choice == "accept":
            state.user_validation = "ACCEPT"
            state.status = TaskStatus.SUCCESS
            print("[ACCEPTED] Output accepted and finalized")
        elif choice.startswith("r") or choice == "refine":
            state.user_validation = "REFINE"
            print("[REFINE] Continuing iteration...")
        else:
            state.user_validation = "REJECT"
            state.status = TaskStatus.REJECTED
            print("[REJECTED] Output rejected")
        
        self._save_state(state)
        return state
    
    def _save_state(self, state: ExecutionState):
        """Save state to disk."""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, 'w') as f:
            json.dump(state.to_dict(), f, indent=2)
    
    def load_state(self) -> Optional[ExecutionState]:
        """Load previous state if exists."""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                data = json.load(f)
                return ExecutionState(
                    state_id=data["state_id"],
                    plan_context=PlanContext(**data["plan_context"]),
                    omega_context=OmegaContext(**data["omega_context"]),
                    status=TaskStatus(data["status"]),
                    iteration=data.get("iteration", 0),
                    created_at=data.get("created_at", ""),
                    updated_at=data.get("updated_at", ""),
                    user_validation=data.get("user_validation"),
                    output_files=data.get("output_files", []),
                    errors=data.get("errors", []),
                )
        return None
    
    def get_status(self) -> Dict:
        """Get current bridge status."""
        state = self.load_state()
        
        return {
            "project": self.project_name,
            "subsystems": {k: v is not None for k, v in self.subsystems.items()},
            "active_state": state.to_dict() if state else None,
            "state_file": str(self.state_file),
        }
    
    def close(self):
        """Cleanup resources."""
        for sub in self.subsystems.values():
            if hasattr(sub, 'close'):
                sub.close()


def run_from_planner(goal: str, max_iterations: int = 50) -> ExecutionState:
    """
    Run the complete pipeline from a goal string.
    
    This is the main entry point that users should call:
    
    ```python
    from engine.bridge import run_from_planner
    
    result = run_from_planner("Build a REST API for user authentication")
    print(result.status)
    ```
    """
    bridge = PlanToOmegaBridge()
    
    # Create plan JSON from goal (simplified - normally would go through Paradise Planner)
    plan_json = {
        "goal": goal,
        "request_type": "feature_add",
        "steps": ["analyze", "implement", "test"],
        "files_to_create": ["src/main.py", "src/api.py"],
        "files_to_modify": [],
        "detected_patterns": [],
        "constraints": {},
        "metadata": {"source": "direct_goal"},
    }
    
    result = bridge.execute(plan_json, max_iterations=max_iterations)
    
    bridge.close()
    
    return result


# CLI Entry Point
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Plan → Omega Bridge")
    parser.add_argument("--goal", "-g", help="Goal to execute")
    parser.add_argument("--plan", "-p", help="Path to plan JSON file")
    parser.add_argument("--max", "-m", type=int, default=50, help="Max iterations")
    parser.add_argument("--status", "-s", action="store_true", help="Show bridge status")
    
    args = parser.parse_args()
    
    bridge = PlanToOmegaBridge()
    
    if args.status:
        import json
        print(json.dumps(bridge.get_status(), indent=2))
    elif args.goal:
        result = run_from_planner(args.goal, args.max)
        print(f"\nFinal Status: {result.status.value}")
    elif args.plan:
        with open(args.plan, 'r') as f:
            plan_json = json.load(f)
        result = bridge.execute(plan_json, max_iterations=args.max)
        print(f"\nFinal Status: {result.status.value}")
    else:
        print("Usage: bridge.py --goal 'Build a REST API'")
        print("       bridge.py --plan plan.json")
        print("       bridge.py --status")
    
    bridge.close()


if __name__ == "__main__":
    main()
