# agentic-OS: Unified Autonomous Agent System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![GitHub stars](https://img.shields.io/github/stars/nrupala/agentic-OS)](https://github.com/nrupala/agentic-OS/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/nrupala/agentic-OS)](https://github.com/nrupala/agentic-OS/network)
[![GitHub issues](https://img.shields.io/github/issues/nrupala/agentic-OS)](https://github.com/nrupala/agentic-OS/issues)
[![GitHub pull requests](https://img.shields.io/github/issues-pr/nrupala/agentic-OS)](https://github.com/nrupala/agentic-OS/pulls)
[![CI](https://github.com/nrupala/agentic-OS/actions/workflows/ci.yml/badge.svg)](https://github.com/nrupala/agentic-OS/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/nrupala/agentic-OS/branch/main/graph/badge.svg)](https://codecov.io/gh/nrupala/agentic-OS)

**Version:** 2.0
**Date:** 2026-04-15

Paradise Stack + OMEGA-CODE = agentic-OS

**OMEGA-CODE: Autonomous Codebase Evolution System**

A production-ready, fully autonomous coding agent with cognitive abilities, self-correcting memory, and enterprise-grade security. The OMEGA-Executor is the primary entry point for all operations.

## OMEGA-CODE Manifest

See [OMEGA_CODE_MANIFEST.md](OMEGA_CODE_MANIFEST.md) for the full specification.

---

## Quick Start

```bash
# Run demo
python agentic-os.py --demo

# Run with custom goal
python agentic-os.py --goal "Build a REST API with authentication"

# Run full agent
python agentic-os.py
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      agentic-OS Core                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐    │
│  │   Memory    │  │  Cognitive   │  │   Security     │    │
│  │   System    │  │   Engine     │  │   Layer        │    │
│  │  (3-tier)  │  │  (Meta+GAN)  │  │ (Vault+RBAC)  │    │
│  │             │  │              │  │                │    │
│  │ • SESSION   │  │ • Meta      │  │ • AES-256    │    │
│  │ • DAILY     │  │ • RAG       │  │ • RBAC       │    │
│  │ • LONG-TERM │  │ • GAN       │  │ • Audit      │    │
│  └─────────────┘  └──────────────┘  └────────────────┘    │
│                                                              │
│         ┌──────────────────────────────────────┐            │
│         │         Recursive Forge Loop          │            │
│         │                                       │            │
│         │   1. RECOLLECT (Load state)          │            │
│         │   2. THINK (Cognitive processing)     │            │
│         │   3. GENERATE (GAN code gen)         │            │
│         │   4. VERIFY (Sandbox check)          │            │
│         │   5. PERSIST (Save + remember)        │            │
│         │   6. EVALUATE (Self-assessment)      │            │
│         └──────────────────────────────────────┘            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 19-Phase OMEGA-CODE Integration

| Phase | Component | File | Status |
|-------|-----------|------|--------|
| 1 | Genesis & Foundation | omega_genesis.sh | OK |
| 2 | Meta-Cognition Engine | omega_meta_logic.py | OK |
| 3 | Discipline Protocol | omega_forge.py | OK |
| 4 | Never-Quit Orchestrator | omega_engine.sh | OK |
| 5 | Temporal State Engine | StateSnapshot | OK |
| 6 | Self-Developing Intelligence | omega_self_develop.py | OK |
| 7 | Hierarchical Memory | omega_hierarchical_memory.py | OK |
| 8 | Vacuum Protocol | omega_vacuum.py | OK |
| 9 | Systemd Guardian | omega-guardian.service | OK |
| 10 | Docker Hardening | Dockerfile.omega | OK |
| 11 | Docker Compose | docker-compose.yml | OK |
| 12 | Self-Evaluation | omega_self_eval.py | OK |
| 13 | RAG + GAN | omega_rag.py, omega_gan.py | OK |
| 14 | Zero-Trust Security | omega_vault.py | OK |
| 15 | RBAC Access | omega_access.py | OK |
| 16 | Audit Trail | omega_audit.py | OK |
| 17 | Observability | Loki + Grafana | OK |
| 18 | Alerting | omega_mail.py | OK |
| 19 | System Recovery | omega_iso_gen.sh | OK |

---

## Subsystems

### Memory System (3-Tier)
```
┌─────────────────────────────────────────┐
│  LONG-TERM (MEMORY.md)                  │
│  Distilled wisdom, persists forever      │
├─────────────────────────────────────────┤
│  MEDIUM-TERM (Daily logs)               │
│  Episodic memory, 7-day retention        │
├─────────────────────────────────────────┤
│  SHORT-TERM (SESSION-STATE.md)          │
│  Active context, wiped on session end   │
└─────────────────────────────────────────┘
```

### Cognitive Engine
- **Meta-Cognition**: Failure pattern analysis, constraint derivation
- **RAG**: Semantic retrieval from long-term memory
- **GAN**: Generator creates code, Discriminator evaluates quality

### Security Layer
- **AES-256-GCM**: At-rest encryption
- **RBAC**: Role-based access (ADMIN, DEVELOPER, AUDITOR)
- **Audit Trail**: Tamper-evident JSONL logging

### Observability
- **Loki**: Log aggregation
- **Grafana**: Visualization dashboards
- **Self-Evaluation**: Periodic cognitive reports

---

## Usage

### Python API

```python
from agentic_os import AgenticOS

agent = AgenticOS("myproject")

# Think
thought = agent.think("Build a REST API")

# Generate
code, result = agent.generate("Build a REST API")

# Remember
agent.remember("lesson", "Always validate input")

# Recall
memories = agent.recall("validation")

# Status
status = agent.status()

agent.close()
```

### CLI

```bash
# Demo mode
python agentic-os.py --demo

# Custom goal
python agentic-os.py --goal "Create a user authentication system"

# With max iterations
python agentic-os.py --goal "Build a chatbot" --max 100
```

### Docker

```bash
# Full stack
docker-compose -f docker/docker-compose.yml up --build

# Access services
# Grafana: http://localhost:3000 (omega/omega-secure-123)
# Loki: http://localhost:3100
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| PROJECT_NAME | default | Project identifier |
| GOAL | - | Task goal |
| MAX_ATTEMPTS | 50 | Max iterations |
| LLM_PROVIDER | lmstudio | LLM provider |
| LLM_API_KEY | - | API key |

---

## File Structure

```
agentic-OS/
├── agentic-os.py              # Unified entry point
├── quickstart.py             # Demo script
├── entrypoint.py             # Full OMEGA loop
│
├── engine/
│   ├── omega_forge.py        # Core recursive engine
│   ├── omega_meta_logic.py   # Meta-cognition
│   ├── omega_gan.py          # GAN self-correction
│   ├── omega_rag.py          # RAG retrieval
│   ├── omega_hierarchical_memory.py  # 3-tier memory
│   ├── omega_self_eval.py    # Self-evaluation
│   ├── omega_vacuum.py       # Log cleanup
│   └── omega_integrator.py   # Integration hub
│
├── docker/
│   ├── Dockerfile.omega       # Hardened container
│   ├── docker-compose.yml    # Full stack
│   └── omega_engine.sh       # Never-quit loop
│
├── security/
│   ├── omega_vault.py       # AES-256-GCM
│   ├── omega_access.py       # RBAC
│   ├── omega_audit.py        # Audit trail
│   └── omega_mail.py         # Email alerts
│
└── observability/
    ├── loki-config.yaml       # Loki config
    └── grafana/              # Dashboards
```

---

## How It Works

### Recursive Loop

```
1. RECOLLECT
   └── Load previous state from SQLite
   └── Check memory for context

2. THINK
   └── RAG retrieves relevant memories
   └── Meta-cognition analyzes patterns
   └── Generate disciplined prompt

3. GENERATE
   └── GAN generates code solution
   └── Discriminator evaluates quality
   └── Loop until passed or max iterations

4. VERIFY
   └── Execute in sandbox (Docker)
   └── Check for errors
   └── Return to THINK if failed

5. PERSIST
   └── Save state to SQLite
   └── Update memory (WAL protocol)
   └── Commit to Git

6. EVALUATE
   └── Self-assessment report
   └── Distill lessons
   └── Send alerts if needed
```

### Self-Correction

```
┌─────────────┐     Generate      ┌─────────────┐
│  Generator  │ ─────────────────>│ Discriminator│
│             │                  │             │
│ Creates     │                  │ Evaluates    │
│ code        │                  │ quality      │
└─────────────┘                  └──────┬──────┘
       ▲                               │
       │       Refine                   │ Score
       └───────────────────────────────┘
              < 0.7?
```

---

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Quick Start

```bash
# Fork and clone
git clone https://github.com/YOUR_USERNAME/agentic-OS.git
cd agentic-OS

# Create feature branch
git checkout -b feature/amazing-feature

# Make changes and test
python -m pytest tests/

# Commit and push
git commit -m "feat: add amazing feature"
git push origin feature/amazing-feature

# Open PR
gh pr create --fill
```

---

## GitHub Resources

| Resource | Link |
|----------|------|
| Repository | https://github.com/nrupala/agentic-OS |
| Issues | https://github.com/nrupala/agentic-OS/issues |
| Discussions | https://github.com/nrupala/agentic-OS/discussions |
| Actions | https://github.com/nrupala/agentic-OS/actions |
| Security | https://github.com/nrupala/agentic-OS/security |

---

## Referenced Projects

This project is built upon the following open-source research:

| Project | Stars | Description |
|--------|-------|-------------|
| [opencode](https://github.com/opencode-ai/opencode) | 142K | Open source coding agent |
| [AutoGPT](https://github.com/Significant-Gravitas/AutoGPT) | 183K | Autonomous agent platform |
| [Paradise Stack](https://github.com/mustbeperfect/definitive-opensource) | 3.2K | Agent development framework |
| [OMEGA-CODE](https://github.com/sh栖息桧/omega-code) | - | Recursive autonomous agent |

---

## Status

**ALL 19 PHASES: COMPLETE**

Run `python integration_test.py` to verify all subsystems.

---

## License

MIT License - Copyright (c) 2026 [Nrupal Akolkar](https://github.com/nrupala)

---

*Last Updated: 2026-04-15*
