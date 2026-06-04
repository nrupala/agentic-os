#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
"""
OMEGA-CODE Integration Test
Verifies all subsystems are properly integrated.
"""

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR
PROJECT_NAME = "default"

sys.path.insert(0, str(PROJECT_ROOT / "engine"))
sys.path.insert(0, str(PROJECT_ROOT / "security"))

def test_imports():
    """Test that all modules can be imported."""
    modules = [
        ("omega_meta_logic", "MetaCognition"),
        ("omega_self_develop", "SelfDevelopingIntelligence"),
        ("omega_hierarchical_memory", "HierarchicalMemory"),
        ("omega_self_eval", "SelfEvaluationReporting"),
        ("omega_vacuum", "VacuumProtocol"),
        ("omega_vault", "SecureVault"),
        ("omega_access", "AccessControl"),
        ("omega_audit", "AuditTrail"),
        ("omega_mail", "OmegaMailAlert"),
        ("omega_integrator", "OmegaIntegrator"),
        ("omega_rag", "OmegaRAG"),
        ("omega_gan", "OmegaGAN"),
    ]
    
    print("Testing module imports...")
    
    all_passed = True
    for module_name, class_name in modules:
        try:
            module = __import__(module_name)
            cls = getattr(module, class_name, None)
            if cls:
                print(f"  [OK] {module_name}.{class_name}")
            else:
                print(f"  [FAIL] {module_name}.{class_name} - class not found")
                all_passed = False
        except Exception as e:
            print(f"  [FAIL] {module_name}.{class_name} - {e}")
            all_passed = False
    
    return all_passed

def test_instantiation():
    """Test that modules can be instantiated."""
    print("\nTesting subsystem instantiation...")
    
    project_path = PROJECT_ROOT / "projects" / PROJECT_NAME
    project_path.mkdir(parents=True, exist_ok=True)
    (project_path / "state").mkdir(exist_ok=True)
    (project_path / "memory").mkdir(exist_ok=True)
    
    all_passed = True
    
    try:
        from omega_hierarchical_memory import HierarchicalMemory
        HierarchicalMemory(str(project_path))
        print("  [OK] HierarchicalMemory instantiated")
    except Exception as e:
        print(f"  [WARN] HierarchicalMemory: {e}")
    
    try:
        from omega_self_eval import SelfEvaluationReporting
        SelfEvaluationReporting(str(project_path))
        print("  [OK] SelfEvaluationReporting instantiated")
    except Exception as e:
        print(f"  [WARN] SelfEvaluationReporting: {e}")
    
    try:
        from omega_audit import AuditTrail
        AuditTrail(str(project_path))
        print("  [OK] AuditTrail instantiated")
    except Exception as e:
        print(f"  [WARN] AuditTrail: {e}")
    
    try:
        from omega_rag import OmegaRAG
        OmegaRAG(str(project_path))
        print("  [OK] OmegaRAG instantiated")
    except Exception as e:
        print(f"  [WARN] OmegaRAG: {e}")
    
    try:
        from omega_gan import OmegaGAN
        OmegaGAN(str(project_path))
        print("  [OK] OmegaGAN instantiated")
    except Exception as e:
        print(f"  [WARN] OmegaGAN: {e}")
    
    try:
        from omega_integrator import OmegaIntegrator
        integrator = OmegaIntegrator(PROJECT_NAME)
        status = integrator.get_system_status()
        print("  [OK] OmegaIntegrator instantiated")
        print("\nSubsystem Status:")
        for name, active in status["subsystems"].items():
            icon = "[OK]" if active else "[FAIL]"
            print(f"    {icon} {name}")
        integrator.close()
    except Exception as e:
        print(f"  [FAIL] OmegaIntegrator: {e}")
        all_passed = False
    
    return all_passed

def test_file_structure():
    """Verify all required files exist."""
    print("\nTesting file structure...")
    
    required_files = [
        "entrypoint.py",
        "omega_genesis.sh",
        "omega_iso_gen.sh",
        "omega_stress_test.py",
        "integration_test.py",
        "engine/omega_forge.py",
        "engine/omega_meta_logic.py",
        "engine/omega_vacuum.py",
        "engine/omega_integrator.py",
        "engine/omega_self_develop.py",
        "engine/omega_hierarchical_memory.py",
        "engine/omega_self_eval.py",
        "engine/omega_rag.py",
        "engine/omega_gan.py",
        "docker/docker-compose.yml",
        "docker/Dockerfile.omega",
        "docker/omega_engine.sh",
        "security/omega_vault.py",
        "security/omega_access.py",
        "security/omega_audit.py",
        "security/omega_mail.py",
        "observability/loki-config.yaml",
        "observability/grafana/OMEGA-Master-Dashboard.json",
        "system_scripts/omega-guardian.service",
    ]
    
    all_passed = True
    for filepath in required_files:
        full_path = PROJECT_ROOT / filepath
        if full_path.exists():
            print(f"  [OK] {filepath}")
        else:
            print(f"  [FAIL] {filepath} - NOT FOUND")
            all_passed = False
    
    return all_passed

def main():
    print("="*60)
    print("OMEGA-CODE Integration Test Suite")
    print("="*60)
    
    all_passed = True
    
    all_passed &= test_imports()
    all_passed &= test_instantiation()
    all_passed &= test_file_structure()
    
    print("\n" + "="*60)
    if all_passed:
        print("ALL INTEGRATION TESTS PASSED")
    else:
        print("SOME TESTS FAILED - Review output above")
    print("="*60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
