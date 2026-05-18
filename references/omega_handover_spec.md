# OMEGA-CODE: Project Handover & System Architecture

## 1. Executive Summary
OMEGA-CODE is a fully autonomous, recursive development engine designed for persistent code generation, verification, and self-optimization. It operates on a "Never-Quit" philosophy, utilizing a state-machine architecture that survives LLM outages, system restarts, and logic failures.

## 2. System Architecture (The "Magic" Stack)
The system is built entirely on **FOSS (Free and Open Source Software)** principles:
- **Orchestrator:** Python-based State Machine with SQLite persistence.
- **VCS:** Local Git-driven atomic versioning for every recursive iteration.
- **Sandbox:** Docker-in-Docker (DinD) with network isolation and resource caps.
- **Hardening:** Multi-stage Docker builds using `python-slim`, non-root users, and immutable cores.

## 3. Core Logic Components

### A. The Recursive Forge (`omega_forge.py`)
- **Recollect & Rectify:** Uses SQLite to pull previous logs and failed code.
- **Persistence:** Every attempt is saved to `omega_state.db`.
- **Termination:** Only stops when the sandbox returns a `0` exit code (Base Case).

### B. The Metacognition Engine
- **Self-Evaluation:** A Meta-Agent analyzes failure patterns across the last 5 iterations.
- **Thinking Rules:** Derives hard constraints (e.g., "Use absolute paths") that are injected into the LLM's system prompt to prevent repetitive errors.
- **Discipline Protocol:** Binds the LLM to a strict JSON output format with mandatory `thought_process` and `validation_test` fields.

### C. The Environment Controller (`omega_engine.sh`)
- **Patience Logic:** Implements exponential backoff for LLM API delays or outages.
- **Atomic Commits:** Auto-commits every iteration to Git with status tags (`PASS/FAIL`).
- **Heartbeat:** Periodically checks system health and restarts the forge if it hangs.

## 4. Operational Maintenance

### The Vacuum Protocol (`omega_vacuum.py`)
- **Distillation:** Summarizes raw logs into a permanent `MEMORY.md` (Long-term wisdom).
- **Cleanup:** Prunes temporary files and older logs to prevent disk bloat while maintaining a 10-log rolling window for context.

### Security & Verification Scripts
- `healthcheck.sh`: Monitors service responsiveness and memory pressure.
- `verify_env.py`: Confirms non-root execution and network isolation.
- `check_deps.py`: Validates pinned FOSS library versions (NumPy, Flask).

## 5. Directory & Project Structure
Projects are isolated via Docker Compose using the `${PROJECT_NAME}` variable:
```text
projects/[NAME]/
├── src/            # Live code (Git tracked)
├── outputs/        # Validated production artifacts
├── self-eval-logs/ # Recursive MD reports
├── logs/           # Stdout/Stderr tracebacks
├── state/          # project_state.db
└── MEMORY.md       # Distilled engineering wisdom
