#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
"""
OMEGA-CODE Main Entrypoint
==========================
Integrated entry point that wires all 19 phases together.
"""

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
PROJECT_NAME = os.getenv("PROJECT_NAME", "default")

sys.path.insert(0, str(PROJECT_ROOT / "engine"))
sys.path.insert(0, str(PROJECT_ROOT / "security"))

def print_banner():
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   ███████╗██╗   ██╗███████╗███████╗██████╗  ██████╗     ║
║   ██╔════╝╚██╗ ██╔╝██╔════╝██╔════╝██╔══██╗██╔═══██╗    ║
║   ███████╗ ╚████╔╝ █████╗  █████╗  ██████╔╝██║   ██║    ║
║   ╚════██║  ╚██╔╝  ██╔══╝  ██╔══╝  ██╔══██╗██║   ██║    ║
║   ███████║   ██║   ███████╗███████╗██║  ██║╚██████╔╝    ║
║   ╚══════╝   ╚═╝   ╚══════╝╚══════╝╚═╝  ╚═╝ ╚═════╝     ║
║                                                           ║
║   OMEGA-CODE v2.0 - Full 19-Phase Integration             ║
║   Recursive Autonomous Agent with Cognitive Abilities      ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """)

def initialize_subsystems():
    """Initialize all OMEGA subsystems."""
    subsystems = {}
    
    print("\n[INIT] Initializing subsystems...")
    
    from omega_meta_logic import MetaCognition
    try:
        db_path = PROJECT_ROOT / "projects" / PROJECT_NAME / "state" / "omega.db"
        subsystems["meta"] = MetaCognition(str(db_path))
        print("  ✅ Meta-Cognition Engine")
    except Exception as e:
        print(f"  ⚠️ Meta-Cognition: {e}")
    
    from omega_self_develop import SelfDevelopingIntelligence
    try:
        subsystems["self_dev"] = SelfDevelopingIntelligence(str(PROJECT_ROOT / "projects" / PROJECT_NAME))
        print("  ✅ Self-Developing Intelligence")
    except Exception as e:
        print(f"  ⚠️ Self-Developing: {e}")
    
    from omega_hierarchical_memory import HierarchicalMemory
    try:
        subsystems["memory"] = HierarchicalMemory(str(PROJECT_ROOT / "projects" / PROJECT_NAME))
        print("  ✅ Hierarchical Memory System")
    except Exception as e:
        print(f"  ⚠️ Memory System: {e}")
    
    from omega_self_eval import SelfEvaluationReporting
    try:
        subsystems["evaluator"] = SelfEvaluationReporting(str(PROJECT_ROOT / "projects" / PROJECT_NAME))
        print("  ✅ Self-Evaluation Reporting")
    except Exception as e:
        print(f"  ⚠️ Self-Evaluator: {e}")
    
    from omega_vacuum import VacuumProtocol
    try:
        subsystems["vacuum"] = VacuumProtocol(str(PROJECT_ROOT / "projects" / PROJECT_NAME))
        print("  ✅ Vacuum Protocol")
    except Exception as e:
        print(f"  ⚠️ Vacuum: {e}")
    
    from omega_vault import SecureVault
    try:
        subsystems["vault"] = SecureVault(str(PROJECT_ROOT / "projects" / PROJECT_NAME))
        print("  ✅ Secure Vault (AES-256-GCM)")
    except Exception as e:
        print(f"  ⚠️ Vault: {e}")
    
    from omega_access import AccessControl
    try:
        subsystems["access"] = AccessControl(str(PROJECT_ROOT / "system_scripts"))
        print("  ✅ RBAC Access Control")
    except Exception as e:
        print(f"  ⚠️ Access Control: {e}")
    
    from omega_audit import AuditTrail
    try:
        subsystems["audit"] = AuditTrail(str(PROJECT_ROOT / "projects" / PROJECT_NAME))
        print("  ✅ Audit Trail")
    except Exception as e:
        print(f"  ⚠️ Audit Trail: {e}")
    
    from omega_mail import OmegaMailAlert
    try:
        subsystems["alerts"] = OmegaMailAlert()
        print("  ✅ Email Alerting")
    except Exception as e:
        print(f"  ⚠️ Email Alerts: {e}")
    
    from omega_rag import OmegaRAG
    try:
        subsystems["rag"] = OmegaRAG(str(PROJECT_ROOT / "projects" / PROJECT_NAME))
        print("  ✅ RAG Memory Retrieval")
    except Exception as e:
        print(f"  ⚠️ RAG: {e}")
    
    from omega_gan import OmegaGAN
    try:
        subsystems["gan"] = OmegaGAN(str(PROJECT_ROOT / "projects" / PROJECT_NAME))
        print("  ✅ GAN Self-Correction")
    except Exception as e:
        print(f"  ⚠️ GAN: {e}")
    
    print(f"\n[INIT] {len(subsystems)}/11 subsystems active")
    return subsystems

def run_recursive_loop(subsystems, goal: str, max_attempts: int = 50):
    """Run the main OMEGA recursive loop."""
    from omega_forge import OmegaForge
    
    print("\n[LOOP] Starting recursive loop")
    print(f"  Goal: {goal}")
    print(f"  Max Attempts: {max_attempts}")
    print(f"  Project: {PROJECT_NAME}")
    
    forge = OmegaForge(PROJECT_NAME)
    
    iteration = 0
    while iteration < max_attempts:
        iteration += 1
        print(f"\n{'='*60}")
        print(f"  ITERATION {iteration}/{max_attempts}")
        print(f"{'='*60}")
        
        if "memory" in subsystems:
            subsystems["memory"].write_session_state({
                "branch": "main",
                "iteration": iteration,
                "last_action": "iteration_start",
                "pending_tasks": [goal],
                "decisions": []
            })
        
        if "self_dev" in subsystems:
            gap_result = subsystems["self_dev"].check_capability_gap()
            if gap_result.get("gap_detected"):
                print(f"[LOOP] Capability gap: {gap_result['gaps']}")
        
        state = forge.recollect(goal)
        
        if iteration == 1:
            state.goal = goal
        
        code, discipline_output = forge.rectify(state)
        state.code = code
        
        print("[LOOP] Verifying in sandbox...")
        success, logs = forge.sandbox_verify(code)
        
        if success:
            state.status = "success"
            forge.persist(state)
            
            print("\n" + "="*60)
            print("  ✅ SUCCESS - BASE CASE REACHED")
            print("="*60)
            
            if "memory" in subsystems:
                subsystems["memory"].append_daily_log(
                    f"SUCCESS: {goal} in {iteration} iterations",
                    category="success"
                )
            
            if "alerts" in subsystems:
                subsystems["alerts"].send_alert(
                    "OMEGA Goal Achieved",
                    f"Goal: {goal}\nIterations: {iteration}",
                    "normal"
                )
            
            break
        
        state.status = "failed"
        state.last_error = logs[:500]
        state.attempts = iteration
        forge.persist(state)
        
        print(f"[LOOP] Verification failed: {logs[:100]}...")
        
        if iteration % 10 == 0 and "evaluator" in subsystems:
            subsystems["evaluator"].generate_markdown_report({
                "recursion_depth": iteration,
                "max_recursion": max_attempts,
                "total_decisions": iteration,
                "correct_decisions": 0,
                "violations": 0,
                "auto_corrections": 0,
                "decisions": [],
                "failures": [{"category": "verification_error", "count": iteration}],
                "next_goal": "Continue recursive refinement"
            })
        
        if iteration >= max_attempts:
            print("\n⚠️ MAX ATTEMPTS REACHED")
            
            if "alerts" in subsystems:
                subsystems["alerts"].alert_recursion_overload(iteration, max_attempts)
    
    forge.close()
    return iteration

def cleanup_subsystems(subsystems):
    """Clean up subsystem connections."""
    print("\n[CLEANUP] Closing subsystem connections...")
    
    for name, subsystem in subsystems.items():
        try:
            if hasattr(subsystem, 'close'):
                subsystem.close()
        except:
            pass
    
    print("[CLEANUP] Done")

def main():
    print_banner()
    
    goal = os.getenv("GOAL", "Build a self-healing microservice with health checks.")
    max_attempts = int(os.getenv("MAX_ATTEMPTS", "50"))
    
    subsystems = initialize_subsystems()
    
    try:
        iterations = run_recursive_loop(subsystems, goal, max_attempts)
        
        print(f"\n{'='*60}")
        print("EXECUTION COMPLETE")
        print(f"{'='*60}")
        print(f"Total Iterations: {iterations}")
        print(f"Status: {'SUCCESS' if iterations < max_attempts else 'MAX_ATTEMPTS'}")
        
        return 0 if iterations < max_attempts else 1
    
    except KeyboardInterrupt:
        print("\n[INTERRUPT] Received shutdown signal")
        return 130
    
    except Exception as e:
        print(f"\n[ERROR] {e}")
        return 1
    
    finally:
        cleanup_subsystems(subsystems)

if __name__ == "__main__":
    sys.exit(main())
