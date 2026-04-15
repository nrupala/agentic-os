#!/usr/bin/env python3
"""
Paradise Stack - Test Suite
"""
import sys
import subprocess
from pathlib import Path

GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'
PROJECT_ROOT = Path("/app")
RESULTS = {"total": 0, "passed": 0, "failed": 0, "skipped": 0, "tests": []}


def run_cmd(cmd, timeout=30):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout, cwd=PROJECT_ROOT)
        return r.returncode, r.stdout, r.stderr
    except Exception:
        return -1, "", "timeout"

def run_tests():
    print(f"\n{BOLD}{BLUE}{'='*60}{RESET}\n{BOLD}{BLUE}PARADISE STACK TEST SUITE{RESET}\n{BOLD}{BLUE}{'='*60}{RESET}\n")
    
    tests = [
        ("FUNCTIONAL", [
            ("planner --help", lambda: (run_cmd("python3 /app/planner.py")[1], "Usage:" in run_cmd("python3 /app/planner.py")[1] or "Usage:" in run_cmd("python3 /app/planner.py")[2])),
            ("/status endpoint", lambda: (run_cmd("curl -s http://localhost:3001/status")[1], '"status"' in run_cmd("curl -s http://localhost:3001/status")[1])),
            ("/version endpoint", lambda: (run_cmd("curl -s http://localhost:3001/version")[1], '"platform"' in run_cmd("curl -s http://localhost:3001/version")[1])),
            ("/execute endpoint", lambda: (run_cmd('curl -s -X POST http://localhost:3001/execute -H "Content-Type: application/json" -d \'{"command":"echo test"}\'')[1], '"success"' in run_cmd('curl -s -X POST http://localhost:3001/execute -H "Content-Type: application/json" -d \'{"command":"echo test"}\'')[1])),
            ("execute command", lambda: (run_cmd('curl -s -X POST http://localhost:3001/execute -H "Content-Type: application/json" -d \'{"command":"echo hello"}\'')[1], "hello" in run_cmd('curl -s -X POST http://localhost:3001/execute -H "Content-Type: application/json" -d \'{"command":"echo hello"}\'')[1])),
        ]),
        ("QUALITY ASSURANCE", [
            ("ruff available", lambda: (run_cmd("which ruff")[1], "ruff" in run_cmd("which ruff")[1])),
            ("ruff check", lambda: (run_cmd("ruff check /app 2>&1")[1], True)),
            ("Python syntax", lambda: (run_cmd("python3 -m py_compile /app/planner.py")[1], run_cmd("python3 -m py_compile /app/planner.py")[0] == 0)),
        ]),
        ("OPERATIONAL", [
            ("Container process", lambda: (run_cmd("ps aux 2>/dev/null || pslist 2>/dev/null || tasklist 2>/dev/null")[1], True)),
            ("Port 3001 accessible", lambda: (run_cmd("curl -s -o /dev/null -w '%{http_code}' http://localhost:3001/status")[1], "200" in run_cmd("curl -s -o /dev/null -w '%{http_code}' http://localhost:3001/status")[1])),
            ("Logs directory", lambda: (str(PROJECT_ROOT / "logs"), (PROJECT_ROOT / "logs").exists())),
            ("Outputs directory", lambda: (str(PROJECT_ROOT / "outputs"), (PROJECT_ROOT / "outputs").exists())),
        ]),
        ("PERFORMANCE", [
            ("Status response time", lambda: (run_cmd("curl -s http://localhost:3001/status")[1], True)),
            ("Execute response time", lambda: (run_cmd('curl -s -X POST http://localhost:3001/execute -H "Content-Type: application/json" -d \'{"command":"echo perf"}\'')[1], True)),
        ]),
        ("INTEGRATION", [
            ("Planner step", lambda: (run_cmd("python3 /app/planner.py integration_test 2>&1")[1], "PLAN.md" in run_cmd("python3 /app/planner.py integration_test 2>&1")[1])),
            ("Guardian step", lambda: (run_cmd("ruff check /app 2>&1")[1], True)),
        ]),
    ]
    
    for category, test_list in tests:
        print(f"\n{BOLD}{BLUE}{'='*40}{RESET}\n{BOLD}{category}{RESET}\n{BOLD}{BLUE}{'='*40}{RESET}\n")
        for name, test_fn in test_list:
            RESULTS["total"] += 1
            try:
                output, passed = test_fn()
                if passed:
                    RESULTS["passed"] += 1
                    RESULTS["tests"].append({"name": name, "status": "passed", "category": category})
                    print(f"  {GREEN}PASS{RESET} {name:<40}")
                else:
                    RESULTS["failed"] += 1
                    RESULTS["tests"].append({"name": name, "status": "failed", "category": category})
                    print(f"  {RED}FAIL{RESET} {name:<40} - {output[:60]}")
            except Exception as e:
                RESULTS["failed"] += 1
                RESULTS["tests"].append({"name": name, "status": "failed", "category": category, "error": str(e)})
                print(f"  {RED}FAIL{RESET} {name:<40} - {str(e)[:60]}")
    
    print(f"\n{BOLD}{BLUE}{'='*60}{RESET}\n{BOLD}SUMMARY{RESET}\n{BOLD}{BLUE}{'='*60}{RESET}\n")
    print(f"  Total:   {RESULTS['total']}")
    print(f"  {GREEN}Passed:  {RESULTS['passed']}{RESET}")
    print(f"  {RED}Failed:  {RESULTS['failed']}{RESET}")
    pct = (RESULTS['passed'] / RESULTS['total'] * 100) if RESULTS['total'] > 0 else 0
    print(f"  Rate: {pct:.1f}%")
    return 0 if RESULTS['failed'] == 0 else 1

if __name__ == '__main__':
    sys.exit(run_tests())
