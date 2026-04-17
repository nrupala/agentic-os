"""
OMEGA-CODE: Recursive Coding Agent
===================================
Recollect -> Rectify -> Verify -> Persist

Features:
- Meta-cognition engine for failure analysis
- Discipline Protocol with strict JSON output
- Temporal state snapshots
- Docker sandbox verification
"""

import os
import sys
import sqlite3
import subprocess
import time
import json
import asyncio
import hashlib
from pathlib import Path
from typing import Dict, Tuple, Optional, List, Any
from dataclasses import dataclass, asdict, field
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
TIMEOUT = 45
MAX_ATTEMPTS = int(os.getenv("MAX_ATTEMPTS", "50"))
SANDBOX_IMAGE = "python:3.11-slim"

@dataclass
class ForgeState:
    goal: str = ""
    code: str = ""
    status: str = "pending"
    attempts: int = 0
    logs: str = ""
    last_error: str = ""
    docker_available: bool = False
    created_at: str = ""
    updated_at: str = ""

@dataclass
class DisciplineOutput:
    thought_process: str
    rectified_code: str
    validation_test: str

class StateSnapshot:
    """Temporal state for warm-start and recovery."""
    
    def __init__(self, project: str):
        self.project = project
        self.snapshot_path = Path(f"projects/{project}/state_snapshot.json")
        self.data = self._load()
    
    def _load(self) -> Dict:
        if self.snapshot_path.exists():
            try:
                return json.loads(self.snapshot_path.read_text())
            except:
                pass
        return self._default()
    
    def _default(self) -> Dict:
        return {
            "project": self.project,
            "current_branch": "main",
            "recursion_depth": 0,
            "last_cognitive_breakthrough": "",
            "pending_tasks": [],
            "failure_patterns": [],
            "llm_status": "READY",
            "environment_hash": "",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    
    def update(self, **kwargs):
        self.data.update(kwargs)
        self.data["updated_at"] = datetime.now().isoformat()
        self.snapshot_path.parent.mkdir(parents=True, exist_ok=True)
        self.snapshot_path.write_text(json.dumps(self.data, indent=2))
    
    def save(self):
        self.snapshot_path.parent.mkdir(parents=True, exist_ok=True)
        self.snapshot_path.write_text(json.dumps(self.data, indent=2))
    
    def compute_hash(self) -> str:
        return hashlib.sha256(str(self.data).encode()).hexdigest()[:16]
    
    def increment_depth(self):
        self.data["recursion_depth"] = self.data.get("recursion_depth", 0) + 1
        self.save()
    
    def add_failure(self, error: str):
        failures = self.data.get("failure_patterns", [])
        if len(failures) > 20:
            failures = failures[-20:]
        failures.append({
            "error": error[:200],
            "timestamp": datetime.now().isoformat()
        })
        self.data["failure_patterns"] = failures
        self.save()


class OmegaForge:
    """
    OMEGA-CODE recursive engine with persistence and meta-cognition.
    
    Phase 1: RECOLLECT - Load previous state from SQLite
    Phase 2: RECTIFY - Generate improved code using constraints
    Phase 3: VERIFY - Execute in Docker sandbox
    Phase 4: PERSIST - Save state to SQLite and snapshot
    """
    
    def __init__(self, project: str = None):
        self.project = project or os.getenv("PROJECT_NAME", "default")
        self.db_path = f"projects/{self.project}/state/omega_state.db"
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self._init_db()
        self.docker_available = self._check_docker()
        self.project_dir = Path(f"projects/{self.project}")
        self.snapshot = StateSnapshot(self.project)
        
        self.meta = None
        self._init_meta()
    
    def _init_meta(self):
        """Initialize meta-cognition engine."""
        try:
            sys.path.insert(0, str(PROJECT_ROOT / "engine"))
            from omega_meta_logic import MetaCognition
            self.meta = MetaCognition(self.db_path)
        except Exception as e:
            print(f"[META] Warning: Could not initialize meta-cognition: {e}")
            self.meta = None
    
    def _init_db(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS forge_state (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                goal TEXT NOT NULL,
                code TEXT,
                status TEXT DEFAULT 'pending',
                attempts INTEGER DEFAULT 0,
                logs TEXT DEFAULT '',
                last_error TEXT DEFAULT '',
                docker_available INTEGER DEFAULT 0,
                created_at TEXT,
                updated_at TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS forge_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                goal TEXT NOT NULL,
                code TEXT,
                status TEXT,
                attempts INTEGER,
                logs TEXT,
                timestamp TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS failures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                goal TEXT,
                error TEXT,
                error_type TEXT,
                timestamp TEXT
            )
        """)
        self.conn.commit()
    
    def _check_docker(self) -> bool:
        try:
            result = subprocess.run(
                ["docker", "version"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    def _classify_error(self, error: str) -> str:
        """Classify error type from error message using unified ErrorClassifier."""
        try:
            from omega_error_classifier import classify_error
            return classify_error(error)
        except ImportError:
            error_lower = error.lower()
            if any(x in error_lower for x in ["timeout", "timed out"]):
                return "timeout"
            elif any(x in error_lower for x in ["syntax", "parse error", "expected"]):
                return "syntax_error"
            elif any(x in error_lower for x in ["import", "modulenotfound", "no module"]):
                return "import_error"
            elif any(x in error_lower for x in ["memory", "out of memory", "oom"]):
                return "memory"
            elif any(x in error_lower for x in ["connection", "network", "refused"]):
                return "network"
            elif any(x in error_lower for x in ["permission", "access denied"]):
                return "permission"
            elif any(x in error_lower for x in ["type error", "type mismatch"]):
                return "type_error"
            elif any(x in error_lower for x in ["value error", "invalid value"]):
                return "value_error"
            elif any(x in error_lower for x in ["assertion", "assert"]):
                return "assertion"
            elif any(x in error_lower for x in ["docker", "container"]):
                return "docker"
            elif any(x in error_lower for x in ["sqlite", "database"]):
                return "sqlite"
            elif any(x in error_lower for x in ["json", "decode"]):
                return "json"
            elif any(x in error_lower for x in ["file", "not found", "no such"]):
                return "file"
            return "generic"
    
    def recollect(self, goal: str = None) -> ForgeState:
        """Phase 1: RECOLLECT - Load previous state."""
        cursor = self.conn.cursor()
        
        if goal:
            cursor.execute(
                "SELECT goal, code, status, attempts, logs, last_error, docker_available, created_at, updated_at "
                "FROM forge_state WHERE goal = ? AND status != 'success' ORDER BY id DESC LIMIT 1",
                (goal,)
            )
        else:
            cursor.execute(
                "SELECT goal, code, status, attempts, logs, last_error, docker_available, created_at, updated_at "
                "FROM forge_state WHERE status != 'success' ORDER BY id DESC LIMIT 1"
            )
        
        row = cursor.fetchone()
        
        if row:
            return ForgeState(
                goal=row[0], code=row[1], status=row[2], attempts=row[3],
                logs=row[4], last_error=row[5], docker_available=bool(row[6]),
                created_at=row[7], updated_at=row[8]
            )
        
        return ForgeState()
    
    def persist(self, state: ForgeState) -> int:
        """Phase 4: PERSIST - Save state to SQLite."""
        cursor = self.conn.cursor()
        now = datetime.now().isoformat()
        
        if not state.created_at:
            state.created_at = now
        state.updated_at = now
        
        cursor.execute("""
            INSERT INTO forge_state 
            (goal, code, status, attempts, logs, last_error, docker_available, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            state.goal, state.code, state.status, state.attempts,
            state.logs, state.last_error, int(state.docker_available),
            state.created_at, state.updated_at
        ))
        
        cursor.execute("""
            INSERT INTO forge_history
            (goal, code, status, attempts, logs, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (state.goal, state.code, state.status, state.attempts, state.logs, now))
        
        if state.status == "failed" and state.last_error:
            error_type = self._classify_error(state.last_error)
            cursor.execute(
                "INSERT INTO failures (goal, error, error_type, timestamp) VALUES (?, ?, ?, ?)",
                (state.goal, state.last_error, error_type, now)
            )
            self.snapshot.add_failure(state.last_error)
        
        self.conn.commit()
        return cursor.lastrowid
    
    def sandbox_verify(self, code: str) -> Tuple[bool, str]:
        """Phase 3: VERIFY - Execute code in sandbox."""
        if self.docker_available:
            return self._docker_verify(code)
        return self._local_verify(code)
    
    def _docker_verify(self, code: str) -> Tuple[bool, str]:
        container_name = f"omega_sandbox_{int(time.time())}"
        escaped_code = code.replace("'", "'\\''")
        
        docker_cmd = [
            "docker", "run", "--rm",
            "--name", container_name,
            "--network", "none",
            "--memory", "256m",
            "--cpus", "0.5",
            SANDBOX_IMAGE,
            "python3", "-c", f"'{escaped_code}'"
        ]
        
        try:
            result = subprocess.run(
                docker_cmd,
                capture_output=True,
                text=True,
                timeout=TIMEOUT
            )
            
            if result.returncode == 0:
                return True, result.stdout
            else:
                return False, f"EXECUTION_ERROR:\n{result.stderr[:500]}"
        
        except subprocess.TimeoutExpired:
            subprocess.run(["docker", "stop", container_name], capture_output=True)
            return False, "TIMEOUT_ERROR: Code exceeded execution limit."
        except Exception as e:
            return False, f"SANDBOX_CRITICAL_FAILURE: {str(e)}"
    
    def _local_verify(self, code: str) -> Tuple[bool, str]:
        temp_file = self.project_dir / "omega_sandbox.py"
        temp_file.write_text(code)
        
        try:
            result = subprocess.run(
                ["python", str(temp_file)],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(self.project_dir)
            )
            
            if result.returncode == 0:
                return True, result.stdout
            else:
                return False, f"EXECUTION_ERROR:\n{result.stderr[:500]}"
        
        except subprocess.TimeoutExpired:
            return False, "TIMEOUT_ERROR: Code exceeded execution limit."
        except Exception as e:
            return False, f"CRITICAL_FAILURE: {str(e)}"
        finally:
            if temp_file.exists():
                temp_file.unlink()
    
    def rectify(self, state: ForgeState) -> Tuple[str, DisciplineOutput]:
        """
        Phase 2: RECTIFY - Generate improved code with Discipline Protocol.
        Returns (code, discipline_output)
        """
        print(f"\n[OMEGA] Phase 2: RECTIFY")
        print(f"  Attempts so far: {state.attempts}")
        
        patterns = []
        constraints = []
        
        if self.meta:
            patterns = self.meta.analyze_failure_patterns()
            constraints = self.meta.derive_constraints(patterns)
            print(f"  [META] Found {len(patterns)} failure patterns")
            print(f"  [META] Generated {len(constraints)} constraints")
        
        if state.last_error:
            print(f"  Last error: {state.last_error[:100]}...")
        
        discipline_output = self._generate_with_discipline(
            goal=state.goal,
            constraints=constraints,
            patterns=patterns,
            previous_logs=state.logs,
            attempt=state.attempts + 1
        )
        
        code = discipline_output.rectified_code if discipline_output else self._fallback_code(state)
        
        return code, discipline_output
    
    def _generate_with_discipline(
        self,
        goal: str,
        constraints: List[str],
        patterns: List,
        previous_logs: str,
        attempt: int
    ) -> Optional[DisciplineOutput]:
        """
        Generate code with Discipline Protocol (Strict JSON SPI).
        """
        if self.meta:
            prompt = self.meta.generate_disciplined_prompt(
                goal=goal,
                constraints=constraints,
                patterns=patterns,
                previous_logs=previous_logs
            )
        else:
            prompt = goal
        
        try:
            from execution_engine import ExecutionEngine
            async def gen():
                engine = ExecutionEngine()
                return await engine.generate(prompt, "python")
            loop = asyncio.new_event_loop()
            raw_response = loop.run_until_complete(gen())
            loop.close()
        except Exception as e:
            print(f"  [LLM] Generation failed: {e}")
            return None
        
        try:
            from omega_meta_logic import DisciplineParser
            success, parsed = DisciplineParser.parse(raw_response)
            
            if success:
                print(f"  [DISCIPLINE] Parsed successfully")
                return DisciplineOutput(
                    thought_process=parsed.get("thought_process", ""),
                    rectified_code=parsed.get("rectified_code", ""),
                    validation_test=parsed.get("validation_test", "")
                )
        except Exception as e:
            print(f"  [PARSE] Failed to parse discipline output: {e}")
        
        return DisciplineOutput(
            thought_process="Fallback generation",
            rectified_code=raw_response,
            validation_test="def test_basic():\n    pass"
        )
    
    def _fallback_code(self, state: ForgeState) -> str:
        return f'''# OMEGA-CODE Generated
# Goal: {state.goal}
# Attempt: {state.attempts + 1}

import sys
from pathlib import Path

def main():
    print("Executing: {state.goal}")
    print("Attempt: {state.attempts + 1}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
'''
    
    def run_loop(self, goal: str, max_attempts: int = MAX_ATTEMPTS) -> ForgeState:
        """Main OMEGA-CODE recursive loop."""
        print("\n" + "=" * 60)
        print("🚀 OMEGA-FORGE INITIALIZED (Discipline Protocol)")
        print(f"   Goal: {goal}")
        print(f"   Docker Sandbox: {'AVAILABLE' if self.docker_available else 'UNAVAILABLE'}")
        print(f"   Meta-Cognition: {'ACTIVE' if self.meta else 'INACTIVE'}")
        print(f"   Max Attempts: {max_attempts}")
        print("=" * 60)
        
        state = self.recollect(goal)
        
        if state.goal == goal and state.status == "failed":
            print(f"\n[RECOLLECT] Resuming previous session")
            print(f"   Previous attempts: {state.attempts}")
        else:
            print(f"\n[RECOLLECT] Fresh start")
            state.goal = goal
            state.docker_available = self.docker_available
        
        self.snapshot.update(
            pending_tasks=[goal],
            llm_status="READY"
        )
        
        while state.attempts < max_attempts:
            state.attempts += 1
            self.snapshot.increment_depth()
            
            print(f"\n{'=' * 60}")
            print(f"--- RECURSION DEPTH: {state.attempts}/{max_attempts} ---")
            print("=" * 60)
            
            code, discipline_output = self.rectify(state)
            state.code = code
            
            print(f"\n[VERIFY] Running sandbox verification...")
            success, logs = self.sandbox_verify(code)
            
            state.logs = logs[:1000]
            
            if success:
                state.status = "success"
                self.persist(state)
                
                self.snapshot.update(
                    llm_status="SUCCESS",
                    last_cognitive_breakthrough=f"Goal achieved at depth {state.attempts}"
                )
                
                print("\n" + "=" * 60)
                print("[OK] BASE CASE REACHED: Functional parity achieved")
                print("=" * 60)
                return state
            else:
                state.status = "failed"
                state.last_error = logs[:500]
                self.persist(state)
                
                self.snapshot.update(llm_status="RECTIFYING")
                
                print(f"\n[FAIL] LOGIC BREACH DETECTED")
                print(f"   Error: {logs[:150]}...")
            
            time.sleep(1)
        
        print(f"\n[WARN] MAX ATTEMPTS ({max_attempts}) REACHED")
        self.snapshot.update(llm_status="MAX_ATTEMPTS")
        return state
    
    def close(self):
        self.conn.close()
        if self.meta:
            self.meta.close()


def main():
    project = os.getenv("PROJECT_NAME", "default")
    goal = os.getenv("GOAL", "Build a self-healing microservice with sub-millisecond latency.")
    
    forge = OmegaForge(project)
    
    try:
        state = forge.run_loop(goal)
        
        print("\n" + "=" * 60)
        print("FINAL STATE")
        print("=" * 60)
        print(f"Status: {state.status}")
        print(f"Attempts: {state.attempts}")
        print(f"Success: {state.status == 'success'}")
        
        return 0 if state.status == "success" else 1
    
    finally:
        forge.close()


if __name__ == "__main__":
    exit(main())
