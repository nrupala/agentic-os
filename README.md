# agentic-OS: Ecosystem Integrator

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![GitHub stars](https://img.shields.io/github/stars/nrupala/agentic-OS)](https://github.com/nrupala/agentic-OS/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/nrupala/agentic-OS)](https://github.com/nrupala/agentic-OS/network)
[![GitHub issues](https://img.shields.io/github/issues/nrupala/agentic-OS)](https://github.com/nrupala/agentic-OS/issues)
[![GitHub pull requests](https://img.shields.io/github/issues-pr/nrupala/agentic-OS)](https://github.com/nrupala/agentic-OS/pulls)
[![CI](https://github.com/nrupala/agentic-OS/actions/workflows/ci.yml/badge.svg)](https://github.com/nrupala/agentic-OS/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/nrupala/agentic-OS/branch/main/graph/badge.svg)](https://codecov.io/gh/nrupala/agentic-OS)

**Version:** 3.0
**Date:** 2026-06-03

agentic-OS is the **integrator** of a 47-repo autonomous ecosystem — the glue that weaves Guardian Mesh, Omega Code, Argent, AxiomCode, Aetheris, Nexus, LocalForge, LLMVM, Zerok, PAE, and 37+ other projects into a single self-sustaining fabric.

This is not a monolith. This is the **operating system** for a never-dying fleet of agents.

---

## Core Repos

| Repo | Language | Role |
|------|----------|------|
| [Guardian Mesh](https://github.com/nrupala/guardian-mesh) | Rust | 5-enclave security fabric, post-quantum crypto |
| [Omega Code](https://github.com/nrupala/omega-code) | Python | Self-building verification pipeline |
| [Argent](https://github.com/nrupala/argent) | Rust | ZK autonomous coding agent with WASM sandbox |
| [AxiomCode](https://github.com/nrupala/axiomcode) | Python | Natural language → Lean 4 formal proofs |
| [Aetheris](https://github.com/nrupala/aetheris) | Rust | Production AI cloud gateway (OCI) |
| [Nexus](https://github.com/nrupala/nexus) | Python | 55+ provider search aggregation |
| [LocalForge](https://github.com/nrupala/localforge) | TypeScript | Multi-agent workflow engine |
| [LLMVM](https://github.com/nrupala/llmvm) | Python | Agent orchestrator |
| [Zerok](https://github.com/nrupala/zerok) | Rust+Go | Portable zero-knowledge vault CLI |
| [PAE](https://github.com/nrupala/pae) | Python | Personal analytics engine |
| And 37+ more... | | |

---

## Three-Layer Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     GUARDIAN MESH (Rust)                      │
│  5-enclave security fabric · post-quantum crypto · enclave    │
│  attestation · hardware-backed sealing · sealed logging      │
├──────────────────────────────────────────────────────────────┤
│                     OMEGA CODE (Python)                       │
│  Self-building verification pipeline · recursive forge loop   │
│  meta-cognition · GAN self-correction · 3-tier memory        │
├──────────────────────────────────────────────────────────────┤
│                     ECOSYSTEM (47 repos)                      │
│  Argent · AxiomCode · Aetheris · Nexus · LocalForge · LLMVM  │
│  Zerok · PAE · and 37+ more                                   │
└──────────────────────────────────────────────────────────────┘
```

**Guardian Mesh** runs at the bottom — hardware-enforced trust. **Omega Code** runs in the middle — self-verifying intelligence. The **Ecosystem** runs on top — every specialized agent serving a purpose.

---

## Quick Start

```bash
# Clone with all submodules
git clone --recursive https://github.com/nrupala/agentic-OS.git
cd agentic-OS

# Build Guardian Mesh (requires Rust)
cd guardian-mesh && cargo build --release && cd ..

# Run Omega Code pipeline
python omega-code/omega_forge.py

# Launch ecosystem
python integrator.py --discover  # scans 47 repos
python integrator.py --status     # reports health of all
python integrator.py --deploy     # deploys missing services
```

---

## Vision

A **self-sustaining ecosystem** that never dies. If a node fails, another replaces it. If a repo drifts, the integrator corrects it. The system evolves itself — discovering new tools, rewriting components, and hardening security — without human intervention.

The integrator (`integrator.py`) is the central nervous system:
- Discovers every repo and its capabilities
- Routes tasks to the right agent
- Monitors health across the fleet
- Recovers failures autonomously
- Grows the ecosystem organically

---

## License

MIT License — Copyright (c) 2026 [Nrupal Akolkar](https://github.com/nrupala)

---

*Last Updated: 2026-06-03*
