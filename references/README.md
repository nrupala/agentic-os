# Agentic-OS Reference Materials

This directory contains the foundational reference materials used to build the agentic-OS system, combining Paradise Stack and OMEGA-CODE architectures.

---

## Document Index

### Architecture & Design

| # | Document | Description |
|---|----------|-------------|
| 01 | [RESEARCH_REFERENCES.md](01_RESEARCH_REFERENCES.md) | **PRIMARY** - Source repositories (284K+ stars), extracted features, integration map |
| 02 | [OMEGA_BUILD_PLAN.md](02_OMEGA_BUILD_PLAN.md) | **PRIMARY** - 19-phase build plan with detailed specifications |
| 07 | [ARCHITECTURE.md](07_ARCHITECTURE.md) | 9 Mermaid diagrams of system architecture |
| 06 | [SYSTEM_FLOWS.md](06_SYSTEM_FLOWS.md) | Complete flow charts, handshakes, component interactions |
| 08 | [REQUEST_FLOW.md](08_REQUEST_FLOW.md) | User request lifecycle with validation gates |

### Status & Tracking

| # | Document | Description |
|---|----------|-------------|
| 03 | [STATUS.md](03_STATUS.md) | Current system state, test results, known issues |
| 04 | [CHANGELOG.md](04_CHANGELOG.md) | Version history and feature changes |
| 05 | [README.md](05_README.md) | Main documentation |

### Reference Catalogs

| # | Document | Description |
|---|----------|-------------|
| 10 | [LLM_MODELS.md](10_LLM_MODELS.md) | 40+ LLM models catalog (commercial use) |
| 11 | [TOOLS_CATALOG.md](11_TOOLS_CATALOG.md) | Agentic tool integrations |
| 12 | [SKILLS_CATALOG.md](12_SKILLS_CATALOG.md) | Skill system specifications |
| 13 | [REFERENCE_URLS.md](13_REFERENCE_URLS.md) | **Complete URL index of all sources** |

### Templates & Examples

| # | Document | Description |
|---|----------|-------------|
| 09 | [PLAN_TEMPLATE.md](09_PLAN_TEMPLATE.md) | Implementation plan template |

---

## Key Sources Referenced

### Paradise Stack (Original Foundation)
- **Repository Sources**: 8 repositories analyzed
- **Total Stars**: 284K+
- **Extracted Features**: 50+
- **Agent Personas**: 100+
- **Skills**: 156+

### OMEGA-CODE Architecture
- **19 Phases**: Complete recursive autonomous agent
- **Meta-Cognition**: Self-aware reasoning
- **GAN Self-Correction**: Generator vs Discriminator loop
- **RAG Retrieval**: Vector-based memory
- **Zero-Trust Security**: AES-256-GCM + RBAC

---

## Reading Order (Recommended)

1. **Start Here**: `01_RESEARCH_REFERENCES.md` - Understand the source materials
2. **Architecture**: `07_ARCHITECTURE.md` + `06_SYSTEM_FLOWS.md` - Visual system design
3. **Implementation**: `02_OMEGA_BUILD_PLAN.md` - How it was built
4. **Current State**: `03_STATUS.md` - What's working
5. **User Flow**: `08_REQUEST_FLOW.md` - How requests flow through the system

---

## Component Source Mapping

| Component | Source Repository | Key Feature |
|-----------|------------------|-------------|
| Knowledge Graph | collection-claude-code | 7-layer memory |
| Meta-Cognition | everything-claude-code | Continuous learning |
| Self-Improvement | everything-claude-code | Instinct patterns |
| Engineering Teams | agency-agents | Persona structure |
| Verification | everything-claude-code | Verification loops |
| Tool System | collection-claude-code | 40+ tools |
| System Patterns | awesome-system-design | Circuit breaker |
| LLM Catalog | open-llms | 40+ models |

---

## Implemented Tools

| Tool | File | Description |
|------|------|-------------|
| **Test Generator** | `tools/test_generator.py` | Auto-generate pytest from Python source |
| **Security Scanner** | `tools/security_scanner.py` | SAST vulnerability detection |
| **Git Provider** | `tools/git_ops.py` | Full git version control |
| **File Operations** | `tools/file_ops.py` | Read/write/edit/grep files |
| **Web Dashboard** | `dashboard/app.py` + `dashboard/index.html` | Real-time execution UI |
| **Docker Runtime** | `tools/docker_ops.py` | Container build/run/execute |

---

## Maintenance

- **Last Updated**: 2026-04-15
- **Update Trigger**: When new features are extracted from sources
- **Source Sync**: Monthly GitHub scanner runs

---

*These documents represent the intellectual foundation of agentic-OS. Review them to understand the "why" behind architectural decisions.*
