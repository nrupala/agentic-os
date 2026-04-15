"""
Paradise Stack Status Checker
Quick validation - fails fast to show what's working and what's not.
"""

import os
import json
from pathlib import Path
from datetime import datetime

INTELLIGENCE_DIR = Path("C:\\Users\\HomeUser\\Downloads\\agentic-OS\\intelligence")
PROJECT_ROOT = Path("C:\\Users\\HomeUser\\Downloads\\agentic-OS")

CHECKS = []

def check(name, condition, details=""):
    """Record a check result."""
    CHECKS.append({
        "name": name,
        "passed": condition,
        "details": details,
    })
    symbol = "[OK]" if condition else "[FAIL]"
    print(f"  {symbol} {name}")
    if details and not condition:
        print(f"     -> {details}")
    return condition

def main():
    print("=" * 60)
    print("Paradise Stack v2.0 - Status Check")
    print("=" * 60)
    print()
    
    print("Core Files:")
    check("paradise.py exists", (PROJECT_ROOT / "paradise.py").exists())
    check("planner.py exists", (PROJECT_ROOT / "planner.py").exists())
    check("cognition/ exists", (PROJECT_ROOT / "cognition").exists())
    check("tools/ exists", (PROJECT_ROOT / "tools").exists())
    
    print()
    print("Intelligence System:")
    check("intelligence/ dir exists", INTELLIGENCE_DIR.exists())
    check("skills/ dir exists", (INTELLIGENCE_DIR / "skills").exists())
    check("patterns/ dir exists", (INTELLIGENCE_DIR / "patterns").exists())
    check("cache/ dir exists", (INTELLIGENCE_DIR / "cache").exists())
    check("reports/ dir exists", (INTELLIGENCE_DIR / "reports").exists())
    
    print()
    print("GitHub Scanner:")
    check("scanner.py exists", (PROJECT_ROOT / "tools" / "github_intelligence_scanner.py").exists())
    check("scheduler.py exists", (PROJECT_ROOT / "tools" / "github_scanner_scheduler.py").exists())
    
    print()
    print("Intelligence Engine:")
    check("continuous_intelligence.py exists", (PROJECT_ROOT / "cognition" / "continuous_intelligence.py").exists())
    check("paradise_cli.py exists", (PROJECT_ROOT / "paradise_cli.py").exists())
    
    print()
    print("Research Documentation:")
    check("RESEARCH/ exists", (PROJECT_ROOT / "RESEARCH").exists())
    check("feature-extraction.json exists", (PROJECT_ROOT / "RESEARCH" / "feature-extraction.json").exists())
    
    cache_file = INTELLIGENCE_DIR / "cache" / "intelligence_cache.json"
    print()
    print("Cached Intelligence:")
    if cache_file.exists():
        with open(cache_file, 'r') as f:
            cache = json.load(f)
        check("Has scan data", bool(cache.get('last_scan')), f"Last: {cache.get('last_scan', 'Never')}")
        check("Top repos saved", len(cache.get('top_repos', [])) > 0, f"Count: {len(cache.get('top_repos', []))}")
    else:
        check("Has scan data", False, "No cache - need to run scanner")
    
    skills_index = INTELLIGENCE_DIR / "skills" / "skills_index.json"
    if skills_index.exists():
        with open(skills_index, 'r') as f:
            index = json.load(f)
        check("Skills indexed", index.get('skills_count', 0) > 0, f"Count: {index.get('skills_count', 0)}")
    else:
        check("Skills indexed", False, "No skills yet")
    
    print()
    print("-" * 60)
    passed = sum(1 for c in CHECKS if c["passed"])
    total = len(CHECKS)
    print(f"Result: {passed}/{total} checks passed")
    
    if passed == total:
        print("[OK] All systems operational!")
        print()
        print("Next steps:")
        print("  1. Set GITHUB_TOKEN and run: python tools/github_intelligence_scanner.py")
        print("  2. Run CLI: python paradise_cli.py")
    elif passed >= total * 0.7:
        print("[WARN] Mostly operational - some manual setup needed")
    else:
        print("[ERROR] Multiple issues - review failed checks above")
    
    print()
    return passed == total

if __name__ == "__main__":
    main()
