#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
"""
OMEGA-CODE Quickstart Demo
==========================
Shows how all 19 phases work together in a simple demonstration.
"""

import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent
PROJECT_NAME = "demo"

sys.path.insert(0, str(PROJECT_ROOT / "engine"))
sys.path.insert(0, str(PROJECT_ROOT / "security"))

def print_banner():
    print("""
============================================================
   OMEGA-CODE Quickstart Demo
   Watch all 19 phases work together!
============================================================
    """)

def demo_memory():
    """Demo the hierarchical memory system."""
    print("\n[1/7] DEMO: Hierarchical Memory System")
    print("-" * 50)
    
    from omega_hierarchical_memory import HierarchicalMemory
    
    memory = HierarchicalMemory(str(PROJECT_ROOT / "projects" / PROJECT_NAME))
    
    memory.write_session_state({
        "branch": "main",
        "iteration": 1,
        "last_action": "demo_start",
        "pending_tasks": ["Initialize OMEGA"],
        "decisions": ["Use recursive approach"]
    })
    
    memory.append_daily_log("Demo started successfully", category="demo")
    memory.distill_wisdom([
        "Always start with memory initialization",
        "Log everything for debugging"
    ])
    
    results = memory.retrieve_relevant("memory")
    print("  [OK] SESSION-STATE.md created")
    print("  [OK] Daily log appended")
    print("  [OK] Wisdom distilled to MEMORY.md")
    print(f"  [OK] Retrieved {len(results)} relevant memory entries")

def demo_self_eval():
    """Demo the self-evaluation system."""
    print("\n[2/7] DEMO: Self-Evaluation Reporting")
    print("-" * 50)
    
    from omega_self_eval import SelfEvaluationReporting
    
    evaluator = SelfEvaluationReporting(str(PROJECT_ROOT / "projects" / PROJECT_NAME))
    
    metrics = {
        "recursion_depth": 10,
        "max_recursion": 50,
        "total_decisions": 10,
        "correct_decisions": 8,
        "violations": 2,
        "auto_corrections": 3,
        "decisions": [
            {"description": "Use iterative approach", "correct": True},
            {"description": "Skip validation", "correct": False}
        ],
        "failures": [
            {"category": "import_error", "count": 2, "last_seen": datetime.now().isoformat()}
        ],
        "next_goal": "Achieve 95% accuracy"
    }
    
    evaluator.generate_markdown_report(metrics)
    print("  [OK] Self-eval report generated")
    print("  [OK] Report saved to self-eval-logs/")

def demo_rag():
    """Demo the RAG retrieval system."""
    print("\n[3/7] DEMO: RAG Memory Retrieval")
    print("-" * 50)
    
    from omega_rag import OmegaRAG
    
    rag = OmegaRAG(str(PROJECT_ROOT / "projects" / PROJECT_NAME))
    
    rag.add_to_memory("Python is great for rapid prototyping", category="learned")
    rag.add_to_memory("Always validate JSON before parsing", category="lesson")
    
    results = rag.retrieve("python", top_k=3)
    print("  [OK] Memory entries indexed")
    print(f"  [OK] Retrieved {len(results)} relevant entries for 'python'")
    
    context = rag.retrieve_context("code development", max_tokens=200)
    print(f"  [OK] Context retrieved: {len(context)} chars")

def demo_gan():
    """Demo the GAN self-correction system."""
    print("\n[4/7] DEMO: GAN Self-Correction")
    print("-" * 50)
    
    from omega_gan import OmegaGAN
    
    gan = OmegaGAN(str(PROJECT_ROOT / "projects" / PROJECT_NAME))
    
    goal = "Create a function that adds two numbers"
    constraints = ["Use type hints", "Handle edge cases"]
    
    code, evaluation = gan.generate_and_refine(goal, constraints, max_iterations=3)
    
    print(f"  [OK] Generated code with score: {evaluation['score']:.2f}")
    print(f"  [OK] Passed discriminator: {evaluation['passed']}")
    print(f"  [OK] Issues found: {len(evaluation['issues'])}")
    
    context = gan.get_temporal_context()
    print(f"  [OK] Total generations: {context['total']}")
    print(f"  [OK] Success rate: {context['success_rate']:.1%}")

def demo_vacuum():
    """Demo the vacuum protocol."""
    print("\n[5/7] DEMO: Vacuum Protocol")
    print("-" * 50)
    
    from omega_vacuum import VacuumProtocol
    
    vacuum = VacuumProtocol(str(PROJECT_ROOT / "projects" / PROJECT_NAME))
    
    results = vacuum.run_vacuum()
    print(f"  [OK] Logs reviewed: {results['logs_reviewed']}")
    print(f"  [OK] Lessons extracted: {len(results['lessons_extracted'])}")
    print(f"  [OK] Logs trashed: {results['logs_trashed']}")
    print(f"  [OK] Temp files cleaned: {results['temp_files_cleaned']}")
    
    status = vacuum.get_status()
    print(f"  [STAT] Current status: {status['logs_count']} logs, {status['trash_count']} trashed")

def demo_security():
    """Demo the security layer."""
    print("\n[6/7] DEMO: Security Layer")
    print("-" * 50)
    
    try:
        from omega_vault import SecureVault
        
        vault = SecureVault(str(PROJECT_ROOT / "projects" / PROJECT_NAME))
        print("  [OK] Vault initialized")
        
        test_data = "Sensitive project wisdom"
        encrypted = vault.secure_store(test_data)
        decrypted = vault.secure_retrieve(encrypted)
        
        print(f"  [OK] Data encrypted ({len(encrypted)} bytes)")
        print(f"  [OK] Data decrypted successfully: {decrypted == test_data}")
        
    except ImportError:
        print("  [WARN] cryptography library not installed")
        print("     Run: pip install cryptography")
    except Exception as e:
        print(f"  [WARN] Vault error: {e}")

def demo_access():
    """Demo the access control system."""
    print("\n[7/7] DEMO: Access Control & Audit")
    print("-" * 50)
    
    from omega_access import AccessControl
    from omega_audit import AuditTrail
    
    access = AccessControl(str(PROJECT_ROOT / "system_scripts"))
    print("  [OK] Access control initialized")
    
    success, role = access.authenticate("omega_admin", "omega_change_me")
    print(f"  [OK] Authenticated: {success}, Role: {role}")
    
    can_run = access.can_perform("omega_admin", "run_iteration")
    can_wipe = access.can_perform("omega_admin", "wipe_project")
    print(f"  [OK] Can run iteration: {can_run}")
    print(f"  [OK] Can wipe project: {can_wipe}")
    
    audit = AuditTrail(str(PROJECT_ROOT / "projects" / PROJECT_NAME))
    audit.log_event("demo_user", "DEMO_ACTION", "success", {"demo": True})
    print("  [OK] Audit event logged")

def show_system_status():
    """Show overall system status."""
    print("\n" + "=" * 60)
    print("SYSTEM STATUS")
    print("=" * 60)
    
    subsystems = [
        ("Meta-Cognition", "omega_meta_logic", "MetaCognition"),
        ("Self-Developing", "omega_self_develop", "SelfDevelopingIntelligence"),
        ("Memory", "omega_hierarchical_memory", "HierarchicalMemory"),
        ("Self-Evaluation", "omega_self_eval", "SelfEvaluationReporting"),
        ("Vacuum", "omega_vacuum", "VacuumProtocol"),
        ("RAG", "omega_rag", "OmegaRAG"),
        ("GAN", "omega_gan", "OmegaGAN"),
    ]
    
    for name, module, cls in subsystems:
        try:
            mod = __import__(module)
            if hasattr(mod, cls):
                print(f"  [OK] {name}")
        except:
            print(f"  [FAIL] {name}")

def main():
    print_banner()
    
    print("Watch how all 19 phases work together!\n")
    
    demo_memory()
    demo_self_eval()
    demo_rag()
    demo_gan()
    demo_vacuum()
    demo_security()
    demo_access()
    
    show_system_status()
    
    print("\n" + "=" * 60)
    print("DEMO COMPLETE!")
    print("=" * 60)
    print("""
To run the full agent:
  python entrypoint.py
  
To run with a custom goal:
  GOAL="Build a REST API" python entrypoint.py
  
To run with Docker:
  docker-compose -f docker/docker-compose.yml up
    """)

if __name__ == "__main__":
    main()
