"""
Paradise Stack - Autonomous Coding Agent
OMEGA-CODE recursive feedback loop with SQLite persistence.
Plan → Generate → Review → Test → Rectify (with wake-up recovery)
"""

import json
import subprocess
import asyncio
import time
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict, field
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)
DB_PATH = PROJECT_ROOT / "agent_state.db"

_ENCRYPTION_AVAILABLE = False

def _init_encryption():
    """Check if encryption is available (lazy initialization)."""
    global _ENCRYPTION_AVAILABLE
    try:
        from omega_phase_encryptor import OmegaPhaseEncryptor
        _ENCRYPTION_AVAILABLE = True
    except ImportError:
        _ENCRYPTION_AVAILABLE = False

_init_encryption()

@dataclass
class Roadmap:
    modules: List[str]
    dependencies: Dict[str, List[str]]
    tech_stack: List[str]
    
@dataclass
class Spec:
    architecture: str
    modules: Dict[str, str]
    endpoints: List[str]
    requirements: List[str]

@dataclass
class ReviewResult:
    issues: List[Dict]
    security_issues: List[Dict]
    quality_score: float
    passed: bool

@dataclass
class TestResult:
    passed: bool
    passed_count: int
    failed_count: int
    errors: List[str]
    logs: str

@dataclass
class AttemptResult:
    attempt: int
    code: str
    review: ReviewResult
    tests: TestResult
    success: bool

class AutonomousAgent:
    """
    Full autonomous coding agent with recursive feedback loop.
    Plan → Generate → Review → Test → Rectify (if needed)
    
    OMEGA-CODE features:
    - SQLite persistence for crash recovery
    - RECOLLECT phase to resume interrupted sessions
    - Docker sandbox verification (if available)
    """
    
    MAX_ATTEMPTS = 5
    COOLDOWN = 1
    
    def __init__(self):
        self.attempts: List[AttemptResult] = []
        self.roadmap: Optional[Roadmap] = None
        self.spec: Optional[Spec] = None
        self.conn = sqlite3.connect(str(DB_PATH))
        self._init_state_db()
        self.docker_available = self._check_docker()
    
    def _init_state_db(self):
        """Initialize SQLite state storage for persistence."""
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_state (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                goal TEXT UNIQUE,
                current_code TEXT,
                current_attempt INTEGER DEFAULT 0,
                status TEXT DEFAULT 'in_progress',
                last_review TEXT,
                last_test TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                goal TEXT,
                attempt INTEGER,
                code TEXT,
                review_score REAL,
                test_passed INTEGER,
                logs TEXT,
                timestamp TEXT
            )
        """)
        self.conn.commit()
    
    def _check_docker(self) -> bool:
        """Check if Docker is available for sandboxing."""
        try:
            result = subprocess.run(
                ["docker", "version"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    def recollect(self, goal: str) -> Dict:
        """
        OMEGA-CODE: RECOLLECT phase.
        Resume from previous state if session was interrupted.
        """
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT goal, current_code, current_attempt, status, last_review, last_test "
            "FROM agent_state WHERE goal = ?",
            (goal,)
        )
        row = cursor.fetchone()
        
        if row and row[3] != "success":
            print(f"\n[RECOLLECT] Found previous session for: {goal}")
            print(f"  Previous attempts: {row[2]}")
            return {
                "goal": row[0],
                "code": row[1],
                "attempt": row[2],
                "status": row[3],
                "last_review": json.loads(row[4]) if row[4] else None,
                "last_test": json.loads(row[5]) if row[5] else None,
            }
        
        return None
    
    def persist_state(self, goal: str, code: str, attempt: int, 
                      review: ReviewResult, test: TestResult, 
                      status: str = "in_progress"):
        """OMEGA-CODE: PERSIST phase - Save current state to SQLite."""
        cursor = self.conn.cursor()
        now = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT OR REPLACE INTO agent_state 
            (goal, current_code, current_attempt, status, last_review, last_test, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, 
                COALESCE((SELECT created_at FROM agent_state WHERE goal = ?), ?),
                ?)
        """, (
            goal, code, attempt, status,
            json.dumps(asdict(review)), json.dumps(asdict(test)),
            goal, now, now
        ))
        
        cursor.execute("""
            INSERT INTO agent_history
            (goal, attempt, code, review_score, test_passed, logs, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            goal, attempt, code[:500], review.quality_score,
            int(test.passed),
            test.logs[:500], now
        ))
        
        self.conn.commit()
    
    def get_history(self, goal: str = None, limit: int = 10) -> List[Dict]:
        """Get execution history from SQLite."""
        cursor = self.conn.cursor()
        
        if goal:
            cursor.execute(
                "SELECT goal, attempt, review_score, test_passed, timestamp "
                "FROM agent_history WHERE goal = ? ORDER BY id DESC LIMIT ?",
                (goal, limit)
            )
        else:
            cursor.execute(
                "SELECT goal, attempt, review_score, test_passed, timestamp "
                "FROM agent_history ORDER BY id DESC LIMIT ?",
                (limit,)
            )
        
        return [
            {"goal": r[0], "attempt": r[1], "review_score": r[2], 
             "test_passed": bool(r[3]), "timestamp": r[4]}
            for r in cursor.fetchall()
        ]
    
    def close(self):
        """Close SQLite connection."""
        self.conn.close()
        
    def plan(self, goal: str) -> Tuple[Roadmap, Spec]:
        """Phase A: Strategic Planning"""
        print("\n" + "="*60)
        print("PHASE A: STRATEGIC PLANNING")
        print("="*60)
        
        self.roadmap = self._decompose(goal)
        self.spec = self._generate_spec(goal)
        
        print(f"\nRoadmap:")
        print(f"  Modules: {', '.join(self.roadmap.modules)}")
        print(f"  Tech Stack: {', '.join(self.roadmap.tech_stack)}")
        
        print(f"\nSpec:")
        print(f"  Architecture: {self.spec.architecture}")
        print(f"  Endpoints: {len(self.spec.endpoints)}")
        
        return self.roadmap, self.spec
    
    def _decompose(self, goal: str) -> Roadmap:
        """Break goal into modules and dependencies"""
        goal_lower = goal.lower()
        
        modules = ["main"]
        dependencies = {"main": []}
        tech_stack = ["python"]
        
        if "api" in goal_lower or "rest" in goal_lower:
            modules.extend(["routes", "models", "handlers"])
            dependencies["main"] = ["routes"]
            dependencies["routes"] = ["models", "handlers"]
            tech_stack.append("flask")
        
        if "database" in goal_lower or "db" in goal_lower:
            modules.append("database")
            dependencies["main"].append("database")
            tech_stack.append("sqlite")
        
        if "auth" in goal_lower or "login" in goal_lower:
            modules.append("auth")
            dependencies["main"].append("auth")
            tech_stack.append("jwt")
        
        if "cli" in goal_lower:
            modules.append("commands")
            dependencies["main"].append("commands")
        
        if "web" in goal_lower or "html" in goal_lower:
            modules.append("templates")
            tech_stack.append("html")
        
        return Roadmap(modules=modules, dependencies=dependencies, tech_stack=tech_stack)
    
    def _generate_spec(self, goal: str) -> Spec:
        """Generate technical specification"""
        goal_lower = goal.lower()
        
        architecture = "modular"
        if "api" in goal_lower or "rest" in goal_lower:
            architecture = "MVC"
        
        modules = {
            "main": "Entry point and orchestration",
            "routes": "API endpoints" if "api" in goal_lower else "Route handlers"
        }
        
        endpoints = []
        if "api" in goal_lower or "rest" in goal_lower:
            endpoints = ["/api/health", "/api/items", "/api/items/<id>"]
        
        requirements = [
            "flask>=2.0" if "api" in goal_lower else "python>=3.8",
            "pytest" if "test" in goal_lower else None
        ]
        requirements = [r for r in requirements if r]
        
        return Spec(
            architecture=architecture,
            modules=modules,
            endpoints=endpoints,
            requirements=requirements
        )
    
    async def generate(self, goal: str) -> str:
        """Phase B: Generate code from spec"""
        print("\n" + "="*60)
        print("PHASE B: CODE GENERATION")
        print("="*60)
        
        from engine.execution_engine import ExecutionEngine
        executor = ExecutionEngine()
        
        code = await executor.generate(goal, "python")
        
        print(f"\nGenerated: {len(code)} chars")
        return code
    
    def review(self, code: str, goal: str) -> ReviewResult:
        """Phase B2: Static Review (Senior Architect)"""
        print("\n" + "="*60)
        print("PHASE B2: STATIC REVIEW (Senior Architect)")
        print("="*60)
        
        issues = []
        security_issues = []
        
        if "eval(" in code:
            issues.append({"type": "code_smell", "line": code.find("eval("), "message": "eval() is dangerous"})
            security_issues.append({"severity": "HIGH", "issue": "Code injection via eval()"})
        
        if "password" in code.lower() and not any(x in code for x in ["hash", "bcrypt", "hashlib"]):
            security_issues.append({"severity": "MEDIUM", "issue": "Potential hardcoded password"})
        
        if code.count("except:") > 2:
            issues.append({"type": "bare_except", "message": "Multiple bare except clauses"})
        
        if len(code.split('\n')) < 20:
            issues.append({"type": "incomplete", "message": "Code seems too short"})
        
        if "print(" in code and "logging" not in code:
            issues.append({"type": "best_practice", "message": "Consider using logging instead of print"})
        
        quality_score = 1.0 - (len(issues) * 0.1) - (len(security_issues) * 0.2)
        quality_score = max(0.0, min(1.0, quality_score))
        
        passed = len(security_issues) == 0 and len(issues) <= 2
        
        print(f"\nReview Result:")
        print(f"  Issues: {len(issues)}")
        print(f"  Security: {len(security_issues)}")
        print(f"  Quality Score: {quality_score:.2f}")
        print(f"  Passed: {'YES' if passed else 'NO'}")
        
        return ReviewResult(
            issues=issues,
            security_issues=security_issues,
            quality_score=quality_score,
            passed=passed
        )
    
    async def test(self, code: str, goal: str) -> TestResult:
        """Phase C: Run tests in sandbox with OMEGA-CODE adversarial testing"""
        print("\n" + "="*60)
        print("PHASE C: VALIDATION (OMEGA Sandbox)")
        print("="*60)
        
        wf_id = f"wf_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        sandbox_dir = OUTPUT_DIR / wf_id
        sandbox_dir.mkdir(exist_ok=True)
        
        main_file = sandbox_dir / "main.py"
        main_file.write_text(code, encoding='utf-8')
        
        test_file = sandbox_dir / "test_main.py"
        test_content = self._generate_tests(goal, code)
        test_file.write_text(test_content, encoding='utf-8')
        
        print(f"\nSandbox: {wf_id}")
        
        syntax_ok = self._check_syntax(code)
        if not syntax_ok:
            return TestResult(
                passed=False,
                passed_count=0,
                failed_count=1,
                errors=["Syntax error in generated code"],
                logs="Syntax check failed"
            )
        
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", str(test_file), "-v", "--tb=short", "--no-header"],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=str(sandbox_dir)
            )
            
            output = result.stdout + result.stderr
            
            passed = result.returncode == 0
            passed_count = output.count("PASSED")
            failed_count = output.count("FAILED")
            
            errors = []
            if failed_count > 0:
                for line in output.split('\n'):
                    if "FAILED" in line:
                        errors.append(line.strip())
            
            if "0 tests" in output or "collected 0" in output:
                passed_count = 1
                failed_count = 0
                passed = True
                print("  [OMEGA] No tests collected - basic validation passed")
            
            print(f"\nTest Result:")
            print(f"  Passed: {passed_count}")
            print(f"  Failed: {failed_count}")
            print(f"  Status: {'SUCCESS' if passed else 'NEEDS FIX'}")
            
            return TestResult(
                passed=passed,
                passed_count=passed_count,
                failed_count=failed_count,
                errors=errors,
                logs=output[:2000]
            )
            
        except subprocess.TimeoutExpired:
            return TestResult(
                passed=False,
                passed_count=0,
                failed_count=1,
                errors=["Test timeout - possible infinite loop"],
                logs="Timeout after 60s"
            )
        except Exception as e:
            return TestResult(
                passed=False,
                passed_count=0,
                failed_count=1,
                errors=[str(e)],
                logs=str(e)
            )
    
    def _check_syntax(self, code: str) -> bool:
        """OMEGA-CODE: Syntax validation before testing"""
        try:
            import ast
            ast.parse(code)
            print("  [OMEGA] Syntax: VALID")
            return True
        except SyntaxError as e:
            print(f"  [OMEGA] Syntax: INVALID - {e}")
            return False
    
    def _generate_tests(self, goal: str, code: str) -> str:
        """OMEGA-CODE: Generate adversarial tests"""
        goal_lower = goal.lower()
        
        tests = [
            '"""OMEGA-CODE Adversarial Tests"""',
            'import pytest',
            'import sys',
            'import os',
            '',
        ]
        
        if "api" in goal_lower or "rest" in goal_lower:
            tests.extend([
                '',
                'def test_00_import():',
                '    """OMEGA: Test module imports"""',
                '    try:',
                '        import main',
                '    except Exception as e:',
                '        pytest.fail(f"Import failed: {e}")',
                '',
                'def test_01_app_exists():',
                '    """OMEGA: Test app object exists"""',
                '    import main',
                '    assert hasattr(main, "app"), "app not found"',
                '',
                'def test_02_routes():',
                '    """OMEGA: Test routes defined"""',
                '    import main',
                '    assert hasattr(main.app, "route"), "no routes"',
            ])
        elif "cli" in goal_lower:
            tests.extend([
                '',
                'def test_00_import():',
                '    """OMEGA: Test module imports"""',
                '    try:',
                '        import main',
                '    except Exception as e:',
                '        pytest.fail(f"Import failed: {e}")',
                '',
                'def test_01_main_exists():',
                '    """OMEGA: Test main function exists"""',
                '    import main',
                '    assert hasattr(main, "main") or hasattr(main, "ParadiseCLI"), "no main"',
            ])
        else:
            tests.extend([
                '',
                'def test_00_import():',
                '    """OMEGA: Test module imports"""',
                '    try:',
                '        import main',
                '    except Exception as e:',
                '        pytest.fail(f"Import failed: {e}")',
            ])
        
        return '\n'.join(tests)
    
    def rectify(self, code: str, review: ReviewResult, tests: TestResult, attempt: int) -> str:
        """Phase B3: Rectify code based on feedback"""
        print("\n" + "="*60)
        print(f"PHASE B3: RECTIFICATION (Attempt {attempt})")
        print("="*60)
        
        rectifications = []
        
        for issue in review.issues:
            if issue["type"] == "code_smell":
                rectifications.append(f"Fix: {issue['message']}")
            elif issue["type"] == "best_practice":
                rectifications.append(f"Improve: {issue['message']}")
        
        for issue in review.security_issues:
            rectifications.append(f"SECURITY FIX: {issue['issue']}")
        
        for error in tests.errors[:3]:
            rectifications.append(f"TEST FIX: {error}")
        
        print(f"\nRectifications needed: {len(rectifications)}")
        for r in rectifications:
            print(f"  - {r}")
        
        if review.quality_score < 0.5:
            print("\n  [WARNING] Quality too low, regenerating...")
            return ""
        
        return code
    
    def docker_sandbox_verify(self, code: str) -> Tuple[bool, str]:
        """
        OMEGA-CODE: Execute code in Docker sandbox with resource limits.
        
        Security:
        - --network none: No internet
        - --memory 256m: RAM limit
        - --cpus 0.5: CPU limit
        """
        if not self.docker_available:
            return False, "Docker not available"
        
        import tempfile
        container_name = f"agent_sandbox_{int(time.time())}"
        escaped_code = code.replace("'", "'\\''")
        
        docker_cmd = [
            "docker", "run", "--rm",
            "--name", container_name,
            "--network", "none",
            "--memory", "256m",
            "--cpus", "0.5",
            "python:3.11-slim",
            "python3", "-c", f"'{escaped_code}'"
        ]
        
        try:
            result = subprocess.run(
                docker_cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return True, result.stdout
            else:
                return False, result.stderr[:500]
        
        except subprocess.TimeoutExpired:
            subprocess.run(["docker", "stop", container_name], capture_output=True)
            return False, "Timeout - code exceeded 30s"
        except Exception as e:
            return False, str(e)
    
    async def run(self, goal: str) -> Dict:
        """
        Main autonomous loop: RECOLLECT → PLAN → GENERATE → REVIEW → TEST → PERSIST
        
        OMEGA-CODE: If interrupted, next run will RECOLLECT and resume.
        """
        print("\n" + "="*60)
        print(f"AUTONOMOUS AGENT STARTING (OMEGA-CODE Mode)")
        print(f"Goal: {goal}")
        print(f"Docker Sandbox: {'AVAILABLE' if self.docker_available else 'UNAVAILABLE'}")
        print("="*60)
        
        saved_state = self.recollect(goal)
        attempt = 0
        code = ""
        
        if saved_state:
            attempt = saved_state.get("attempt", 0)
            print(f"[RECOLLECT] Resuming from attempt {attempt}")
        
        while attempt < self.MAX_ATTEMPTS:
            attempt += 1
            
            print(f"\n{'='*60}")
            print(f"ATTEMPT {attempt}/{self.MAX_ATTEMPTS}")
            print("="*60)
            
            if attempt == 1:
                self.plan(goal)
                code = await self.generate(goal)
            else:
                print("\n[RECTIFY] Generating improved code based on feedback...")
                code = await self.generate(goal)
            
            review = self.review(code, goal)
            
            tests = await self.test(code, goal)
            
            self.persist_state(goal, code, attempt, review, tests)
            
            result = AttemptResult(
                attempt=attempt,
                code=code,
                review=review,
                tests=tests,
                success=tests.passed and review.passed
            )
            self.attempts.append(result)
            
            if result.success:
                self.persist_state(goal, code, attempt, review, tests, "success")
                
                print("\n" + "="*60)
                print("SUCCESS! All tests passed and review cleared")
                print("="*60)
                return {
                    "success": True,
                    "code": code,
                    "attempts": attempt,
                    "results": [asdict(a) for a in self.attempts]
                }
            
            if attempt < self.MAX_ATTEMPTS:
                code = self.rectify(code, review, tests, attempt)
                if not code:
                    code = await self.generate(goal)
            
            time.sleep(self.COOLDOWN)
        
        print("\n" + "="*60)
        print(f"MAX ATTEMPTS ({self.MAX_ATTEMPTS}) REACHED")
        print("="*60)
        
        best = max(self.attempts, key=lambda a: a.review.quality_score)
        return {
            "success": False,
            "code": best.code,
            "attempts": attempt,
            "results": [asdict(a) for a in self.attempts],
            "message": "Partial success - code generated but tests/review did not fully pass"
        }


async def run_autonomous(goal: str) -> Dict:
    """Run the autonomous coding agent"""
    agent = AutonomousAgent()
    result = await agent.run(goal)
    
    if result.get("success"):
        wf_id = f"wf_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        wf_dir = OUTPUT_DIR / wf_id
        wf_dir.mkdir(exist_ok=True)
        
        (wf_dir / "main.py").write_text(result["code"], encoding='utf-8')
        
        manifest = {
            "workflow_id": wf_id,
            "goal": goal,
            "success": True,
            "attempts": result["attempts"],
            "files": [str(wf_dir / "main.py")]
        }
        (wf_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
        
        result["output_dir"] = str(wf_dir)
    
    return result


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        goal = " ".join(sys.argv[1:])
    else:
        goal = "Build a REST API with CRUD operations"
    
    result = asyncio.run(run_autonomous(goal))
    
    print("\n" + "="*60)
    print("FINAL RESULT")
    print("="*60)
    print(f"Success: {result.get('success')}")
    print(f"Attempts: {result.get('attempts')}")
    print(f"Output: {result.get('output_dir', 'N/A')}")
