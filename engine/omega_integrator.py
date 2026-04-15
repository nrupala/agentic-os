#!/usr/bin/env python3
"""
OMEGA-CODE Integration Hub
=========================
Wires all 19 phases together into a cohesive system.
"""

import os
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent

class OmegaIntegrator:
    """
    Central integration hub that coordinates all OMEGA subsystems.
    
    Integrates:
    - Meta-Cognition (omega_meta_logic.py)
    - Self-Developing (omega_self_develop.py)
    - Hierarchical Memory (omega_hierarchical_memory.py)
    - Self-Evaluation (omega_self_eval.py)
    - Vacuum Protocol (omega_vacuum.py)
    - Vault Security (omega_vault.py)
    - Access Control (omega_access.py)
    - Audit Trail (omega_audit.py)
    - Mail Alerts (omega_mail.py)
    """
    
    def __init__(self, project: str):
        self.project = project
        self.project_path = PROJECT_ROOT / "projects" / project
        
        self.meta = None
        self.self_dev = None
        self.memory = None
        self.evaluator = None
        self.vault = None
        self.access = None
        self.audit = None
        self.alerts = None
        
        self._init_all_subsystems()
    
    def _init_all_subsystems(self):
        """Initialize all OMEGA subsystems."""
        sys.path.insert(0, str(PROJECT_ROOT / "engine"))
        sys.path.insert(0, str(PROJECT_ROOT / "security"))
        
        try:
            from omega_meta_logic import MetaCognition
            db_path = str(self.project_path / "state" / "omega.db")
            self.meta = MetaCognition(db_path)
            print("[INTEGRATOR] Meta-Cognition: ACTIVE")
        except Exception as e:
            print(f"[INTEGRATOR] Meta-Cognition: INACTIVE ({e})")
        
        try:
            from omega_self_develop import SelfDevelopingIntelligence
            self.self_dev = SelfDevelopingIntelligence(str(self.project_path))
            print("[INTEGRATOR] Self-Developing: ACTIVE")
        except Exception as e:
            print(f"[INTEGRATOR] Self-Developing: INACTIVE ({e})")
        
        try:
            from omega_hierarchical_memory import HierarchicalMemory
            self.memory = HierarchicalMemory(str(self.project_path))
            print("[INTEGRATOR] Hierarchical Memory: ACTIVE")
        except Exception as e:
            print(f"[INTEGRATOR] Hierarchical Memory: INACTIVE ({e})")
        
        try:
            from omega_self_eval import SelfEvaluationReporting
            self.evaluator = SelfEvaluationReporting(str(self.project_path))
            print("[INTEGRATOR] Self-Evaluation: ACTIVE")
        except Exception as e:
            print(f"[INTEGRATOR] Self-Evaluation: INACTIVE ({e})")
        
        try:
            from omega_vault import SecureVault
            self.vault = SecureVault(str(self.project_path))
            print("[INTEGRATOR] Vault Security: ACTIVE")
        except Exception as e:
            print(f"[INTEGRATOR] Vault Security: INACTIVE ({e})")
        
        try:
            from omega_access import AccessControl
            self.access = AccessControl(str(PROJECT_ROOT / "system_scripts"))
            print("[INTEGRATOR] Access Control: ACTIVE")
        except Exception as e:
            print(f"[INTEGRATOR] Access Control: INACTIVE ({e})")
        
        try:
            from omega_audit import AuditTrail
            self.audit = AuditTrail(str(self.project_path))
            print("[INTEGRATOR] Audit Trail: ACTIVE")
        except Exception as e:
            print(f"[INTEGRATOR] Audit Trail: INACTIVE ({e})")
        
        try:
            from omega_mail import OmegaMailAlert
            self.alerts = OmegaMailAlert()
            print("[INTEGRATOR] Email Alerts: ACTIVE")
        except Exception as e:
            print(f"[INTEGRATOR] Email Alerts: INACTIVE ({e})")
    
    def on_iteration_start(self, context: dict):
        """Called at the start of each recursion iteration."""
        if self.memory:
            self.memory.write_session_state({
                "branch": context.get("branch", "unknown"),
                "iteration": context.get("iteration", 0),
                "last_action": "iteration_start",
                "pending_tasks": context.get("pending_tasks", []),
                "decisions": []
            })
        
        if self.self_dev:
            gap_result = self.self_dev.check_capability_gap()
            if gap_result.get("gap_detected"):
                print(f"[INTEGRATOR] Capability gap detected: {gap_result['gaps']}")
        
        self._audit_event("iteration_start", context)
    
    def on_iteration_complete(self, context: dict, result: dict):
        """Called after each iteration completes."""
        if self.memory:
            self.memory.append_daily_log(
                f"Iteration {context.get('iteration')}: {result.get('status')}",
                category="iteration"
            )
        
        if self.evaluator and context.get("iteration", 0) % 10 == 0:
            self._generate_eval_report(context, result)
        
        self._audit_event("iteration_complete", result)
        
        if result.get("status") == "failed":
            self._check_alerts(result)
    
    def on_rectify(self, goal: str, constraints: list, patterns: list):
        """Called during code rectification."""
        if self.meta:
            prompt = self.meta.generate_disciplined_prompt(
                goal=goal,
                constraints=constraints,
                patterns=patterns
            )
            return prompt
        return goal
    
    def on_verify(self, code: str, result: dict):
        """Called after code verification."""
        self._audit_event("verify", {
            "success": result.get("success", False),
            "logs": result.get("logs", "")[:200]
        })
        
        if not result.get("success") and self.meta:
            self.meta.log_failure(result.get("error", "Unknown"))
    
    def on_success(self, state: dict):
        """Called when goal is achieved."""
        if self.memory:
            self.memory.append_daily_log(
                f"SUCCESS: {state.get('goal')}",
                category="success"
            )
        
        if self.evaluator:
            self._generate_eval_report(state, {"status": "success"})
        
        self._audit_event("goal_achieved", state)
        
        if self.alerts:
            self.alerts.send_alert(
                "OMEGA Goal Achieved",
                f"Goal: {state.get('goal')}\nIterations: {state.get('attempts', 0)}",
                "normal"
            )
    
    def on_max_attempts(self, state: dict):
        """Called when max iterations reached."""
        if self.alerts:
            self.alerts.alert_recursion_overload(
                state.get("attempts", 0),
                state.get("max_attempts", 50)
            )
        
        self._audit_event("max_attempts_reached", state)
    
    def _generate_eval_report(self, context: dict, result: dict):
        """Generate self-evaluation report."""
        metrics = {
            "recursion_depth": context.get("iteration", 0),
            "max_recursion": 50,
            "total_decisions": context.get("iteration", 0),
            "correct_decisions": context.get("iteration", 0) if result.get("status") == "success" else 0,
            "violations": 0,
            "auto_corrections": 0,
            "decisions": [],
            "failures": [],
            "next_goal": "Continue autonomous development"
        }
        
        if self.evaluator:
            report = self.evaluator.generate_markdown_report(metrics)
            print(f"[INTEGRATOR] Self-eval report generated")
            return report
        return None
    
    def _audit_event(self, event_type: str, data: dict):
        """Log event to audit trail."""
        if self.audit:
            self.audit.log_event(
                user="omega-system",
                action=event_type,
                status="success",
                metadata=data
            )
    
    def _check_alerts(self, result: dict):
        """Check if alert conditions are met."""
        if self.alerts:
            error = result.get("error", "").lower()
            
            if "unauthorized" in error or "permission" in error:
                self.alerts.alert_unauthorized_access(
                    "omega-agent",
                    "internal",
                    error[:100]
                )
            
            if "memory" in error or "oom" in error:
                self.alerts.alert_memory_pressure(95.0)
    
    def get_system_status(self) -> dict:
        """Get comprehensive system status."""
        return {
            "timestamp": datetime.now().isoformat(),
            "project": self.project,
            "subsystems": {
                "meta_cognition": self.meta is not None,
                "self_developing": self.self_dev is not None,
                "hierarchical_memory": self.memory is not None,
                "self_evaluation": self.evaluator is not None,
                "vault_security": self.vault is not None,
                "access_control": self.access is not None,
                "audit_trail": self.audit is not None,
                "email_alerts": self.alerts is not None
            }
        }
    
    def close(self):
        """Clean up all subsystem connections."""
        if self.meta:
            self.meta.close()


def create_integrated_forge():
    """Create an OmegaForge with all integrations."""
    from engine.omega_forge import OmegaForge
    
    class IntegratedOmegaForge(OmegaForge):
        def __init__(self, project: str = None):
            super().__init__(project)
            
            sys.path.insert(0, str(PROJECT_ROOT / "engine"))
            sys.path.insert(0, str(PROJECT_ROOT / "security"))
            
            self.integrator = OmegaIntegrator(project)
            
            try:
                from omega_hierarchical_memory import HierarchicalMemory
                self.memory = HierarchicalMemory(str(self.project_dir))
            except:
                self.memory = None
        
        def run_loop(self, goal: str, max_attempts: int = 50):
            self.integrator.on_iteration_start({
                "branch": self.snapshot.data.get("current_branch", "main"),
                "iteration": 0,
                "pending_tasks": [goal]
            })
            
            result = super().run_loop(goal, max_attempts)
            
            if result.status == "success":
                self.integrator.on_success({
                    "goal": goal,
                    "attempts": result.attempts,
                    "max_attempts": max_attempts
                })
            elif result.attempts >= max_attempts:
                self.integrator.on_max_attempts({
                    "goal": goal,
                    "attempts": result.attempts,
                    "max_attempts": max_attempts
                })
            
            return result
        
        def close(self):
            super().close()
            self.integrator.close()
    
    return IntegratedOmegaForge


if __name__ == "__main__":
    project = os.getenv("PROJECT_NAME", "default")
    integrator = OmegaIntegrator(project)
    
    print("\n" + "=" * 60)
    print("OMEGA-CODE System Status")
    print("=" * 60)
    
    status = integrator.get_system_status()
    print(f"\nProject: {status['project']}")
    print(f"Timestamp: {status['timestamp']}")
    print("\nSubsystems:")
    
    for subsystem, active in status["subsystems"].items():
        status_icon = "[OK]" if active else "[FAIL]"
        print(f"  {status_icon} {subsystem}")
    
    print("\n" + "=" * 60)
    integrator.close()
