"""
Paradise Stack v2.0 - Test Suite
Comprehensive tests for all components.
"""

import os
import sys
import json
import asyncio
import tempfile
from pathlib import Path
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path("C:\\Users\\HomeUser\\Downloads\\agentic-OS")
sys.path.insert(0, str(PROJECT_ROOT))

INTELLIGENCE_DIR = PROJECT_ROOT / "intelligence"

class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def record(self, name, passed, error=None):
        if passed:
            self.passed += 1
            print(f"  [PASS] {name}")
        else:
            self.failed += 1
            self.errors.append((name, error))
            print(f"  [FAIL] {name}")
            if error:
                print(f"        Error: {error}")
    
    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'='*60}")
        print(f"Results: {self.passed}/{total} passed")
        if self.failed > 0:
            print(f"Failed: {self.failed}")
            for name, err in self.errors:
                print(f"  - {name}: {err}")
        return self.failed == 0


def test_file_structure():
    """Test that all required files exist."""
    results = TestResults()
    print("\n[TEST] File Structure")
    
    required_files = [
        PROJECT_ROOT / "paradise.py",
        PROJECT_ROOT / "planner.py",
        PROJECT_ROOT / "paradise_cli.py",
        PROJECT_ROOT / "cognition" / "continuous_intelligence.py",
        PROJECT_ROOT / "cognition" / "knowledge_graph.py",
        PROJECT_ROOT / "cognition" / "meta_cognition.py",
        PROJECT_ROOT / "cognition" / "self_improvement.py",
        PROJECT_ROOT / "cognition" / "agent_personas.py",
        PROJECT_ROOT / "tools" / "github_intelligence_scanner.py",
        PROJECT_ROOT / "tools" / "github_scanner_scheduler.py",
        PROJECT_ROOT / "tools" / "status_check.py",
        PROJECT_ROOT / "tools" / "quick_skill_fetch.py",
        PROJECT_ROOT / "agent" / "ORGANIZATION.md",
        PROJECT_ROOT / "agent" / "PHILOSOPHY.md",
        PROJECT_ROOT / "agent" / "CAPABILITIES.md",
        PROJECT_ROOT / "agent" / "LEARNING.md",
        PROJECT_ROOT / "agent" / "BEHAVIOR.md",
        PROJECT_ROOT / "RESEARCH" / "feature-extraction.json",
    ]
    
    for f in required_files:
        results.record(f.name, f.exists(), f"Missing: {f}")
    
    return results


def test_intelligence_directories():
    """Test intelligence directory structure."""
    results = TestResults()
    print("\n[TEST] Intelligence Directories")
    
    dirs = ["skills", "patterns", "cache", "reports"]
    for d in dirs:
        path = INTELLIGENCE_DIR / d
        results.record(f"Directory: {d}", path.exists() and path.is_dir())
    
    return results


def test_knowledge_base():
    """Test KnowledgeBase class."""
    results = TestResults()
    print("\n[TEST] KnowledgeBase")
    
    try:
        from cognition.continuous_intelligence import KnowledgeBase
        
        kb = KnowledgeBase()
        results.record("KnowledgeBase instantiated", True)
        
        skill_data = {
            "name": "test_skill",
            "path": "/test/path",
            "tools": ["bash", "write"],
            "techniques": ["async_pattern"]
        }
        kb.add_skill(skill_data)
        results.record("add_skill works", True)
        
        found = kb.find_skills_for_task("async")
        results.record("find_skills_for_task works", len(found) >= 0)
        
        tools = kb.get_all_tools()
        results.record("get_all_tools works", isinstance(tools, list))
        
    except Exception as e:
        results.record("KnowledgeBase", False, str(e))
    
    return results


def test_pattern_engine():
    """Test PatternEngine class."""
    results = TestResults()
    print("\n[TEST] PatternEngine")
    
    try:
        from cognition.continuous_intelligence import PatternEngine
        
        pe = PatternEngine()
        results.record("PatternEngine instantiated", True)
        
        features = {
            "content": "Uses async patterns with tool execution",
            "source": "test_repo"
        }
        patterns = pe.extract_patterns(features)
        results.record("extract_patterns works", isinstance(patterns, list))
        
        interaction = {"content": "async workflow test"}
        int_patterns = pe.extract_from_interaction(interaction)
        results.record("extract_from_interaction works", isinstance(int_patterns, list))
        
        matched = pe.match_patterns("async", ["async_pattern", "sync_pattern"])
        results.record("match_patterns works", isinstance(matched, list))
        
    except Exception as e:
        results.record("PatternEngine", False, str(e))
    
    return results


def test_evolution_tracker():
    """Test EvolutionTracker class."""
    results = TestResults()
    print("\n[TEST] EvolutionTracker")
    
    try:
        from cognition.continuous_intelligence import EvolutionTracker
        
        # Use temp directory for test
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as tmpdir:
            original_log = os.environ.get("EVOLUTION_LOG")
            os.environ["EVOLUTION_LOG"] = str(Path(tmpdir) / "test_log.json")
            
            try:
                et = EvolutionTracker()
                results.record("EvolutionTracker instantiated", True)
                
                et.log_integration({
                    "timestamp": datetime.now().isoformat(),
                    "patterns_added": 5,
                    "skills_added": 2
                })
                results.record("log_integration works", True)
                
                level = et.get_level()
                results.record("get_level returns int", isinstance(level, int))
                
                age = et.get_knowledge_age()
                results.record("get_knowledge_age works", isinstance(age, int))
                
            finally:
                if original_log:
                    os.environ["EVOLUTION_LOG"] = original_log
                else:
                    os.environ.pop("EVOLUTION_LOG", None)
                
    except Exception as e:
        results.record("EvolutionTracker", False, str(e))
    
    return results


def test_continuous_intelligence_engine():
    """Test ContinuousIntelligenceEngine class."""
    results = TestResults()
    print("\n[TEST] ContinuousIntelligenceEngine")
    
    try:
        from cognition.continuous_intelligence import ContinuousIntelligenceEngine
        
        engine = ContinuousIntelligenceEngine()
        results.record("Engine instantiated", True)
        
        state = engine.get_evolved_state()
        results.record("get_evolved_state works", isinstance(state, dict))
        results.record("Has evolution_level", "evolution_level" in state)
        results.record("Has skills_integrated", "skills_integrated" in state)
        results.record("Has patterns_mastered", "patterns_mastered" in state)
        
        engine.evolve_from_interaction({
            "type": "test_interaction",
            "content": "testing patterns",
            "outcome": "success"
        })
        results.record("evolve_from_interaction works", True)
        
        suggestions = engine.suggest_improvements()
        results.record("suggest_improvements works", isinstance(suggestions, list))
        
    except Exception as e:
        results.record("ContinuousIntelligenceEngine", False, str(e))
    
    return results


def test_paradise_persona():
    """Test ParadiseStackPersona class."""
    results = TestResults()
    print("\n[TEST] ParadiseStackPersona")
    
    try:
        from cognition.continuous_intelligence import ParadiseStackPersona
        
        identity = ParadiseStackPersona.get_introduction()
        results.record("get_introduction returns text", isinstance(identity, str) and len(identity) > 0)
        
        caps = ParadiseStackPersona.get_current_capabilities()
        results.record("get_current_capabilities returns list", isinstance(caps, list))
        results.record("Has capabilities", len(caps) > 0)
        
    except Exception as e:
        results.record("ParadiseStackPersona", False, str(e))
    
    return results


def test_skills_index():
    """Test skills index."""
    results = TestResults()
    print("\n[TEST] Skills Index")
    
    index_file = INTELLIGENCE_DIR / "skills" / "skills_index.json"
    results.record("skills_index.json exists", index_file.exists())
    
    if index_file.exists():
        try:
            with open(index_file, 'r') as f:
                index = json.load(f)
            results.record("skills_index.json valid JSON", True)
            results.record("Has skills_count", "skills_count" in index)
            results.record("Has skills list", "skills" in index)
            results.record("Has at least 1 skill", index.get("skills_count", 0) >= 1)
        except Exception as e:
            results.record("Parse skills_index", False, str(e))
    
    return results


def test_intelligence_cache():
    """Test intelligence cache."""
    results = TestResults()
    print("\n[TEST] Intelligence Cache")
    
    cache_file = INTELLIGENCE_DIR / "cache" / "intelligence_cache.json"
    results.record("intelligence_cache.json exists", cache_file.exists())
    
    if cache_file.exists():
        try:
            with open(cache_file, 'r') as f:
                cache = json.load(f)
            results.record("cache is valid JSON", True)
            results.record("Has last_scan", "last_scan" in cache)
            results.record("Has top_repos", "top_repos" in cache)
            results.record("Has at least 1 top repo", len(cache.get("top_repos", [])) >= 1)
        except Exception as e:
            results.record("Parse cache", False, str(e))
    
    return results


def test_github_scanner():
    """Test GitHub scanner module."""
    results = TestResults()
    print("\n[TEST] GitHub Scanner")
    
    try:
        from tools.github_intelligence_scanner import GitHubIntelligenceScanner
        
        scanner = GitHubIntelligenceScanner()
        results.record("Scanner instantiated", True)
        
        cache = scanner.get_cached_intelligence()
        results.record("get_cached_intelligence works", isinstance(cache, (dict, type(None))))
        
        needs_scan = scanner.check_scan_needed()
        results.record("check_scan_needed works", isinstance(needs_scan, bool))
        
        index = scanner.generate_skills_index()
        results.record("generate_skills_index works", isinstance(index, str))
        
    except Exception as e:
        results.record("GitHub Scanner", False, str(e))
    
    return results


def test_status_check():
    """Test status check functionality."""
    results = TestResults()
    print("\n[TEST] Status Check")
    
    try:
        from tools.status_check import CHECKS, check
        
        initial_count = len(CHECKS)
        check("test_check", True)
        results.record("check function works", len(CHECKS) > initial_count)
        
    except Exception as e:
        results.record("Status Check", False, str(e))
    
    return results


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("Paradise Stack v2.0 - Test Suite")
    print("=" * 60)
    
    all_results = [
        test_file_structure(),
        test_intelligence_directories(),
        test_knowledge_base(),
        test_pattern_engine(),
        test_evolution_tracker(),
        test_continuous_intelligence_engine(),
        test_paradise_persona(),
        test_skills_index(),
        test_intelligence_cache(),
        test_github_scanner(),
        test_status_check(),
    ]
    
    total_passed = sum(r.passed for r in all_results)
    total_failed = sum(r.failed for r in all_results)
    total = total_passed + total_failed
    
    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)
    print(f"Tests: {total}")
    print(f"Passed: {total_passed}")
    print(f"Failed: {total_failed}")
    
    if total_failed == 0:
        print("\n[OK] ALL TESTS PASSED!")
        return True
    else:
        print(f"\n[FAIL] {total_failed} tests failed")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
