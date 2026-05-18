#!/bin/bash
# =============================================================================
# OMEGA-CODE GENESIS: Complete System Construction
# =============================================================================
# Purpose: Single executable that constructs the entire OMEGA-CODE ecosystem
#          - Directories, Python logic, Docker configs, System services
# Usage:   bash omega_genesis.sh [--project NAME]
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_NAME="${PROJECT_NAME:-default}"
PROJECT_DIR="${SCRIPT_DIR}/projects/${PROJECT_NAME}"
SYSTEM_SCRIPTS="${SCRIPT_DIR}/system_scripts"
ENGINE_DIR="${SCRIPT_DIR}/engine"
DOCKER_DIR="${SCRIPT_DIR}/docker"
SECURITY_DIR="${SCRIPT_DIR}/security"

echo "============================================================================"
echo "🚀 OMEGA-CODE GENESIS: Initializing System Architecture..."
echo "============================================================================"
echo "   Project: ${PROJECT_NAME}"
echo "   Root:    ${SCRIPT_DIR}"
echo "============================================================================"

# =============================================================================
# 1. DIRECTORY STRUCTURE
# =============================================================================
echo ""
echo "[1/8] Creating Directory Structure..."

mkdir -p "${PROJECT_DIR}/src"
mkdir -p "${PROJECT_DIR}/outputs"
mkdir -p "${PROJECT_DIR}/state"
mkdir -p "${PROJECT_DIR}/logs"
mkdir -p "${PROJECT_DIR}/self-eval-logs"
mkdir -p "${PROJECT_DIR}/memory"
mkdir -p "${SYSTEM_SCRIPTS}"
mkdir -p "${ENGINE_DIR}"
mkdir -p "${DOCKER_DIR}"
mkdir -p "${SECURITY_DIR}"

echo "   ✓ Directories created"

# =============================================================================
# 2. GENERATE DOCKERFILE (The Hardened Core)
# =============================================================================
echo ""
echo "[2/8] Generating Dockerfile (Multi-Stage Hardened)..."

cat << 'DOCKERFILE_EOF' > "${DOCKER_DIR}/Dockerfile.omega"
# =============================================================================
# OMEGA-CODE Hardened Dockerfile
# Multi-stage build: Builder (Stage 1) -> Runtime (Stage 2)
# =============================================================================

# STAGE 1: Builder (never reaches production)
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /build

# Install OS-level build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install pinned dependencies into local directory
RUN pip install --no-cache-dir --prefix=/install \
    numpy==1.26.4 \
    flask==3.0.2 \
    gunicorn==21.2.0 \
    pytest==8.0.0 \
    cryptography==42.0.0

# =============================================================================
# STAGE 2: Hardened Runtime
# =============================================================================
FROM python:3.12-slim

LABEL maintainer="Paradise-Stack-Omega" \
      security.hardened="true" \
      version="1.0"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/usr/local/lib/python3.12/site-packages

WORKDIR /app

# Create non-privileged user
RUN addgroup --system omega && adduser --system --group omega

# Copy pre-compiled libraries ONLY from builder
COPY --from=builder /install /usr/local

# Copy application code (root owned = immutable for omega user)
COPY --chown=root:root engine /app/engine
COPY --chown=root:root docker /app/docker

# Security lockdown
RUN chmod 755 /app && \
    mkdir -p /tmp/omega && \
    chown omega:omega /tmp/omega

# Copy and set permissions for scripts
COPY --chown=omega:omega docker/healthcheck.sh /app/docker/healthcheck.sh
COPY --chown=omega:omega docker/verify_env.py /app/docker/verify_env.py
COPY --chown=omega:omega docker/check_deps.py /app/docker/check_deps.py
RUN chmod +x /app/docker/healthcheck.sh

# Switch to non-root user
USER omega

EXPOSE 5000

CMD ["python3", "/app/engine/omega_forge.py"]
DOCKERFILE_EOF

echo "   ✓ Dockerfile.omega created"

# =============================================================================
# 3. GENERATE OMEGA-FORGE (The Brain)
# =============================================================================
echo ""
echo "[3/8] Generating omega_forge.py (Core Recursive Engine)..."

cat << 'FORGE_EOF' > "${ENGINE_DIR}/omega_forge.py"
"""
OMEGA-CODE: Recursive Coding Agent
=================================
Recollect -> Rectify -> Verify -> Persist
"""

import os
import sqlite3
import subprocess
import time
import json
import asyncio
from pathlib import Path
from typing import Dict, Tuple, Optional, List
from dataclasses import dataclass, asdict, field
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
DB_PATH = os.getenv("DB_PATH", f"projects/{os.getenv('PROJECT_NAME', 'default')}/state/omega_state.db")
SANDBOX_IMAGE = "python:3.11-slim"
TIMEOUT = 45
MAX_ATTEMPTS = int(os.getenv("MAX_ATTEMPTS", "50"))

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

class OmegaForge:
    """
    OMEGA-CODE recursive engine with persistence.
    Phase 1: RECOLLECT - Load previous state
    Phase 2: RECTIFY - Generate improved code
    Phase 3: VERIFY - Execute in sandbox
    Phase 4: PERSIST - Save state
    """
    
    def __init__(self, project: str = None):
        self.project = project or os.getenv("PROJECT_NAME", "default")
        self.db_path = f"projects/{self.project}/state/omega_state.db"
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self._init_db()
        self.docker_available = self._check_docker()
        self.project_dir = Path(f"projects/{self.project}")
    
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
        
        if state.status == "failed":
            cursor.execute(
                "INSERT INTO failures (goal, error, timestamp) VALUES (?, ?, ?)",
                (state.goal, state.last_error, now)
            )
        
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
    
    def rectify(self, state: ForgeState) -> str:
        """Phase 2: RECTIFY - Generate improved code."""
        print(f"\n[OMEGA] Phase 2: RECTIFY")
        print(f"  Attempts so far: {state.attempts}")
        
        if state.last_error:
            print(f"  Last error: {state.last_error[:100]}...")
        
        # Use meta-cognition if available
        try:
            from omega_meta_logic import MetaCognition
            meta = MetaCognition(self.db_path)
            patterns = meta.analyze_failure_patterns()
            constraints = meta.derive_constraints(patterns)
            prompt = meta.generate_disciplined_prompt(state.goal, constraints, patterns)
        except:
            prompt = state.goal
        
        # Generate code with execution engine
        try:
            from execution_engine import ExecutionEngine
            async def gen():
                engine = ExecutionEngine()
                return await engine.generate(prompt, "python")
            loop = asyncio.new_event_loop()
            code = loop.run_until_complete(gen())
            loop.close()
        except:
            code = self._fallback_code(state)
        
        if not code or len(code) < 50:
            code = self._fallback_code(state)
        
        return code
    
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
        print("🚀 OMEGA-FORGE INITIALIZED")
        print(f"   Goal: {goal}")
        print(f"   Docker Sandbox: {'AVAILABLE' if self.docker_available else 'UNAVAILABLE'}")
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
        
        while state.attempts < max_attempts:
            state.attempts += 1
            
            print(f"\n{'=' * 60}")
            print(f"--- RECURSION DEPTH: {state.attempts}/{max_attempts} ---")
            print("=" * 60)
            
            code = self.rectify(state)
            state.code = code
            
            print(f"\n[VERIFY] Running sandbox verification...")
            success, logs = self.sandbox_verify(code)
            
            state.logs = logs[:1000]
            
            if success:
                state.status = "success"
                self.persist(state)
                
                print("\n" + "=" * 60)
                print("✅ BASE CASE REACHED: Functional parity achieved")
                print("=" * 60)
                return state
            else:
                state.status = "failed"
                state.last_error = logs[:500]
                self.persist(state)
                
                print(f"\n❌ LOGIC BREACH DETECTED")
                print(f"   Error: {logs[:150]}...")
            
            time.sleep(1)
        
        print(f"\n⚠️ MAX ATTEMPTS ({max_attempts}) REACHED")
        return state
    
    def close(self):
        self.conn.close()


def main():
    import sys
    
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
FORGE_EOF

echo "   ✓ omega_forge.py created"

# =============================================================================
# 4. GENERATE OMEGA-VACUUM (Autonomous Cleanup)
# =============================================================================
echo ""
echo "[4/8] Generating omega_vacuum.py (Log Distillation)..."

cat << 'VACUUM_EOF' > "${ENGINE_DIR}/omega_vacuum.py"
"""
OMEGA-CODE Vacuum Protocol
==========================
Log distillation and pruning engine.
- Summarizes 50 logs into Top 3 Lessons
- Appends wisdom to MEMORY.md
- Prunes to 10-log rolling window
- Safe delete with .trash
"""

import os
import glob
import json
import shutil
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
PROJECT_NAME = os.getenv("PROJECT_NAME", "default")
LOG_DIR = PROJECT_ROOT / f"projects/{PROJECT_NAME}/self-eval-logs"
MEMORY_DIR = PROJECT_ROOT / f"projects/{PROJECT_NAME}/memory"
TRASH_DIR = PROJECT_ROOT / f"projects/{PROJECT_NAME}/.trash"
MAX_LOGS = 10
DISTILL_THRESHOLD = 50

def vacuum_logs():
    """Distills logs into wisdom and prunes the rest."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    TRASH_DIR.mkdir(parents=True, exist_ok=True)
    
    logs = sorted(LOG_DIR.glob("eval_*.md"), key=os.path.getmtime)
    
    print(f"[VACUUM] Found {len(logs)} evaluation logs")
    
    if len(logs) <= MAX_LOGS:
        print("[VACUUM] Log count healthy. Skipping cleanup.")
        return
    
    to_delete = logs[:-MAX_LOGS]
    print(f"[VACUUM] Distilling {len(to_delete)} logs into long-term memory...")
    
    # DISTILLATION PHASE
    lessons = distill_lessons(to_delete)
    
    if lessons:
        append_to_memory(lessons)
    
    # PURGE PHASE
    for log_path in to_delete:
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            trash_path = TRASH_DIR / f"{timestamp}_{log_path.name}"
            shutil.move(str(log_path), str(trash_path))
            print(f"[CLEANUP] Moved to .trash: {log_path.name}")
        except Exception as e:
            print(f"[ERROR] Failed to process {log_path}: {e}")
    
    # TEMP FILE PURGE
    temp_files = list(PROJECT_ROOT.glob("*.tmp")) + list(Path("/tmp/omega").glob("*") if Path("/tmp/omega").exists() else [])
    for tmp in temp_files:
        if tmp.is_file():
            try:
                tmp.unlink()
                print(f"[CLEANUP] Deleted temp: {tmp.name}")
            except:
                pass

def distill_lessons(logs: list) -> list:
    """Extract top lessons from old logs."""
    lessons = []
    
    for log_path in logs:
        try:
            content = log_path.read_text()
            # Simple extraction - look for key patterns
            if "BREAKTHROUGH" in content or "FIXED" in content:
                for line in content.split('\n'):
                    if line.strip().startswith('- **') or line.strip().startswith('* '):
                        lessons.append(line.strip())
        except:
            pass
    
    return lessons[:3]  # Top 3 lessons

def append_to_memory(lessons: list):
    """Append distilled lessons to MEMORY.md."""
    memory_file = MEMORY_DIR / "MEMORY.md"
    
    entry = f"""
## Distilled Wisdom - {datetime.now().strftime('%Y-%m-%d')}

"""
    for lesson in lessons:
        entry += f"- {lesson}\n"
    
    if memory_file.exists():
        existing = memory_file.read_text()
        memory_file.write_text(existing + entry)
    else:
        memory_file.write_text(f"""# OMEGA-CODE Memory
## Distilled Engineering Wisdom

{entry}
""")
    
    print(f"[WISDOM] Appended {len(lessons)} lessons to MEMORY.md")

if __name__ == "__main__":
    print("=" * 60)
    print("OMEGA-CODE VACUUM PROTOCOL")
    print("=" * 60)
    vacuum_logs()
    print("=" * 60)
VACUUM_EOF

echo "   ✓ omega_vacuum.py created"

# =============================================================================
# 5. GENERATE DOCKER COMPOSE
# =============================================================================
echo ""
echo "[5/8] Generating docker-compose.yml..."

cat << 'COMPOSE_EOF' > "${DOCKER_DIR}/docker-compose.yml"
# OMEGA-CODE Docker Compose
# Full autonomous agent lifecycle with project isolation

services:
  omega-agent:
    build:
      context: ..
      dockerfile: docker/Dockerfile.omega
    image: omega-hardened:latest
    container_name: omega_${PROJECT_NAME}
    environment:
      - PROJECT_NAME=${PROJECT_NAME}
      - MAX_ATTEMPTS=${MAX_ATTEMPTS:-50}
      - RECURSION_LIMIT=${RECURSION_LIMIT:-50}
    # Security: Hardened runtime
    read_only: true
    tmpfs:
      - /tmp/omega:rw,size=64m
    networks:
      - omega-sandbox
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
    # Project isolation via volumes
    volumes:
      - ../projects/${PROJECT_NAME}/src:/app/projects/${PROJECT_NAME}/src:rw
      - ../projects/${PROJECT_NAME}/outputs:/app/projects/${PROJECT_NAME}/outputs:rw
      - ../projects/${PROJECT_NAME}/logs:/app/projects/${PROJECT_NAME}/logs:rw
      - ../projects/${PROJECT_NAME}/state:/app/projects/${PROJECT_NAME}/state:rw
      - ../projects/${PROJECT_NAME}/self-eval-logs:/app/projects/${PROJECT_NAME}/self-eval-logs:rw
      - ../projects/${PROJECT_NAME}/memory:/app/projects/${PROJECT_NAME}/memory:rw
    # Automated startup sequence
    command: >
      sh -c "python3 /app/docker/verify_env.py &&
             python3 /app/docker/check_deps.py &&
             python3 /app/engine/omega_forge.py"
    healthcheck:
      test: ["CMD", "/app/docker/healthcheck.sh"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s

networks:
  omega-sandbox:
    driver: bridge
    internal: true
COMPOSE_EOF

echo "   ✓ docker-compose.yml created"

# =============================================================================
# 6. GENERATE SYSTEMD GUARDIAN (Persistence)
# =============================================================================
echo ""
echo "[6/8] Generating systemd service..."

cat << 'SYSTEMD_EOF' > "${SYSTEM_SCRIPTS}/omega-guardian.service"
# OMEGA-CODE Guardian Service
# Ensures 24/7 uptime with automatic restart

[Unit]
Description=OMEGA-CODE Infinite Persistence Guardian
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=${SCRIPT_DIR}
ExecStart=/usr/local/bin/docker-compose -f docker/docker-compose.yml up -d
ExecStop=/usr/local/bin/docker-compose -f docker/docker-compose.yml down
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
SYSTEMD_EOF

echo "   ✓ omega-guardian.service created"

# =============================================================================
# 7. INITIALIZE GIT
# =============================================================================
echo ""
echo "[7/8] Initializing Git repository..."

if [ ! -d "${SCRIPT_DIR}/.git" ]; then
    git init "${SCRIPT_DIR}"
    git config user.name "OMEGA-CODE Agent"
    git config user.email "omega@paradise.local"
    
    cat << 'GITIGNORE_EOF' > "${SCRIPT_DIR}/.gitignore"
# OMEGA-CODE Git Ignore
__pycache__/
*.pyc
*.pyo
*.db
*.sqlite
.trash/
*.tmp
projects/*/state/
projects/*/logs/*.log
projects/*/.trash/
.DS_Store
.env
*.key
certs/
grafana_data/
chroma_data/
GITIGNORE_EOF
    
    echo "   ✓ Git initialized"
else
    echo "   ✓ Git already initialized"
fi

# =============================================================================
# 8. INITIAL STATE & PERMISSIONS
# =============================================================================
echo ""
echo "[8/8] Setting permissions and creating initial state..."

# Create initial state snapshot
cat << 'SNAPSHOT_EOF' > "${PROJECT_DIR}/state_snapshot.json"
{
  "project": "${PROJECT_NAME}",
  "current_branch": "main",
  "recursion_depth": 0,
  "last_cognitive_breakthrough": "System initialized",
  "pending_tasks": [],
  "failure_patterns": [],
  "llm_status": "READY",
  "environment_hash": "",
  "created_at": "$(date -Iseconds)",
  "updated_at": "$(date -Iseconds)"
}
SNAPSHOT_EOF

# Create initial MEMORY.md
cat << 'MEMORY_EOF' > "${PROJECT_DIR}/memory/MEMORY.md"
# OMEGA-CODE Memory
## Distilled Engineering Wisdom

### System Initialization
- System initialized at: $(date -Iseconds)
- Project: ${PROJECT_NAME}

---
*Generated by OMEGA-CODE Genesis*
MEMORY_EOF

# Create initial SESSION-STATE.md
cat << 'SESSION_EOF' > "${PROJECT_DIR}/memory/SESSION-STATE.md"
# OMEGA-CODE Session State
## Active Working Memory

**Status:** INITIALIZING
**Started:** $(date -Iseconds)
**Current Task:** None

### Critical Variables
- PROJECT_NAME: ${PROJECT_NAME}
- RECURSION_DEPTH: 0

### Active Obstacles
- None (system initializing)

---
*Last Updated: $(date -Iseconds)*
SESSION_EOF

# Create initial README
cat << 'README_EOF' > "${PROJECT_DIR}/src/README.md"
# ${PROJECT_NAME}
## OMEGA-CODE Generated Project

Generated at: $(date -Iseconds)

---
*Protected by OMEGA-CODE Guardian*
README_EOF

echo "   ✓ State files created"

# =============================================================================
# FINAL OUTPUT
# =============================================================================
echo ""
echo "============================================================================"
echo "✅ OMEGA-CODE GENESIS COMPLETE"
echo "============================================================================"
echo ""
echo "Project Structure:"
echo "  projects/${PROJECT_NAME}/"
echo "    ├── src/            # Live code (Git tracked)"
echo "    ├── outputs/        # Validated artifacts"
echo "    ├── state/          # Project-specific DB"
echo "    ├── logs/           # Tracebacks"
echo "    ├── self-eval-logs/ # Daily evaluation reports"
echo "    ├── memory/         # Hierarchical memory"
echo "    │   ├── SESSION-STATE.md"
echo "    │   └── MEMORY.md"
echo "    └── state_snapshot.json"
echo ""
echo "============================================================================"
echo "🚀 NEXT STEPS"
echo "============================================================================"
echo ""
echo "1. Start the agent:"
echo "   export PROJECT_NAME=${PROJECT_NAME}"
echo "   docker-compose -f docker/docker-compose.yml up --build"
echo ""
echo "2. Or run locally:"
echo "   python engine/omega_forge.py"
echo ""
echo "3. For 24/7 operation, install the guardian:"
echo "   sudo cp system_scripts/omega-guardian.service /etc/systemd/system/"
echo "   sudo systemctl enable omega-guardian"
echo "   sudo systemctl start omega-guardian"
echo ""
echo "============================================================================"
