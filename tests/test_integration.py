"""
Paradise Stack - Integration Test
Tests all systems working together.
"""

import sys
import json
from pathlib import Path

PROJECT_ROOT = Path("C:\\Users\\HomeUser\\Downloads\\agentic-OS")
sys.path.insert(0, str(PROJECT_ROOT))

INTELLIGENCE_DIR = PROJECT_ROOT / "intelligence"

def test_cli_integration():
    """Test CLI module works."""
    try:
        from paradise_cli import ParadiseStackCLI
        cli = ParadiseStackCLI()
        state = cli.engine.get_evolved_state()
        assert "evolution_level" in state
        print("[PASS] CLI Integration")
        return True
    except Exception as e:
        print(f"[FAIL] CLI Integration: {e}")
        return False

def test_web_dashboard_integration():
    """Test web dashboard module works."""
    try:
        from dashboard.web_dashboard import app, get_system_state
        state = get_system_state()
        assert "evolution_level" in state
        print("[PASS] Web Dashboard Integration")
        return True
    except Exception as e:
        print(f"[FAIL] Web Dashboard Integration: {e}")
        return False

def test_intelligence_engine_integration():
    """Test intelligence engine works."""
    try:
        from cognition.continuous_intelligence import initialize_evolution
        
        engine = initialize_evolution()
        state = engine.get_evolved_state()
        
        assert state["evolution_level"] >= 1
        assert state["skills_integrated"] >= 0
        assert state["patterns_mastered"] >= 0
        
        print("[PASS] Intelligence Engine Integration")
        return True
    except Exception as e:
        print(f"[FAIL] Intelligence Engine Integration: {e}")
        return False

def test_skills_loading():
    """Test skills can be loaded."""
    try:
        skills_dir = INTELLIGENCE_DIR / "skills"
        skills = list(skills_dir.glob("*.md"))
        
        assert len(skills) >= 1, f"Expected >=1 skills, got {len(skills)}"
        
        print(f"[PASS] Skills Loading: {len(skills)} skill sources")
        return True
    except Exception as e:
        print(f"[FAIL] Skills Loading: {e}")
        return False

def test_cache_data():
    """Test cached data is accessible."""
    try:
        cache_file = INTELLIGENCE_DIR / "cache" / "intelligence_cache.json"
        
        with open(cache_file, 'r') as f:
            cache = json.load(f)
        
        assert "top_repos" in cache
        assert len(cache["top_repos"]) >= 1
        
        print(f"[PASS] Cache Data: {len(cache['top_repos'])} repos")
        return True
    except Exception as e:
        print(f"[FAIL] Cache Data: {e}")
        return False

def test_planner_integration():
    """Test planner module works."""
    try:
        from planner import CodebaseExplorer, TaskAnalyzer, Planner
        
        explorer = CodebaseExplorer()
        explorer.scan()
        
        analyzer = TaskAnalyzer("add login feature")
        assert analyzer.detected_type is not None
        
        print("[PASS] Planner Integration")
        return True
    except Exception as e:
        print(f"[FAIL] Planner Integration: {e}")
        return False

def test_full_workflow():
    """Test full workflow: scan -> integrate -> use."""
    try:
        from cognition.continuous_intelligence import initialize_evolution
        
        engine = initialize_evolution()
        
        initial_patterns = engine.get_evolved_state()["patterns_mastered"]
        
        engine.evolve_from_interaction({
            "type": "test_workflow",
            "content": "testing async patterns with Python",
            "outcome": "success"
        })
        
        state = engine.get_evolved_state()
        suggestions = engine.suggest_improvements()
        
        assert state["evolution_level"] >= 1
        assert isinstance(suggestions, list)
        
        print(f"[PASS] Full Workflow: patterns={state['patterns_mastered']}, suggestions={len(suggestions)}")
        return True
    except Exception as e:
        print(f"[FAIL] Full Workflow: {e}")
        return False

def main():
    print("=" * 60)
    print("Paradise Stack - Integration Test")
    print("=" * 60)
    print()
    
    tests = [
        ("Skills Loading", test_skills_loading),
        ("Cache Data", test_cache_data),
        ("CLI Integration", test_cli_integration),
        ("Web Dashboard Integration", test_web_dashboard_integration),
        ("Intelligence Engine Integration", test_intelligence_engine_integration),
        ("Planner Integration", test_planner_integration),
        ("Full Workflow", test_full_workflow),
    ]
    
    results = []
    for name, test_fn in tests:
        print(f"\n[{name}]")
        results.append(test_fn())
    
    print()
    print("=" * 60)
    print("INTEGRATION SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    
    if passed == total:
        print("\n[OK] ALL INTEGRATION TESTS PASSED!")
        return True
    else:
        print(f"\n[FAIL] {total - passed} tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
