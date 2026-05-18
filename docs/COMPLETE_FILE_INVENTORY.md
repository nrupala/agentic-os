# OMEGA Codex - COMPLETE FILE INVENTORY

> ALL files in agentic-OS project (150+ Python, 1000+ Total)

---

## File Type Summary

| Extension | Count | Description |
|-----------|-------|-------------|
| `.py` | ~150 | Python source |
| `.js` | ~2000 | JavaScript (node_modules) |
| `.json` | ~100 | Config/data |
| `.md` | ~50 | Documentation |
| `.yml`/.yaml` | ~20 | CI/CD configs |
| `.html` | ~10 | Web pages |
| `.sh` | ~5 | Shell scripts |
| `.txt` | ~10 | Logs/outputs |
| `.docx` | ~2 | Word docs |

Total: **~2300+ files**

---

## PART 1: PYTHON SOURCE FILES (.py)

### Root Level (~15 files)

| File | Purpose | Key Functions |
|------|---------|---------------|
| agentic-os.py | Main entry point | main, setup_logging |
| paradise.py | Paradise system | ParadiseSystem class |
| paradise_cli.py | CLI interface | main, parse_args |
| paradise_chat.py | Chat interface | ChatClient |
| paradise_unified.py | Unified interface | UnifiedParadise |
| omega_cli.py | OMEGA CLI | main, run_goal |
| omega_stress_test.py | Stress testing | stress_test |
| run.py | Alt entry (pre-Omega) | ParadiseRunner.run, _plan, _build, _verify |
| entrypoint.py | Entrypoint | main |
| quickstart.py | Quick start | main |
| planner.py | Planning | Planner class |
| integration_test.py | Integration tests | test_* functions |

### Cognition Directory (~18 files)

| File | Purpose | Key Functions |
|------|---------|---------------|
| cognition/__init__.py | Package init | exports |
| cognition/orchestrator.py | Main orchestration | Orchestrator.run |
| cognition/master_orchestrator.py | Master coordination | orchestrate |
| cognition/pdc_orchestrator.py | PDCA loop | plan/do/check |
| cognition/agent_pairing.py | Agent pairing | pair_agents |
| cognition/agent_personas.py | Personas | get_persona |
| cognition/continuous_intelligence.py | Learning | learn |
| cognition/engineering_teams.py | Team mgmt | assign_task |
| cognition/entities.py | Entity classes | Entity, Agent, Team |
| cognition/knowledge_graph.py | Graph DB | add_node, query |
| cognition/meta_cognition.py | Meta reasoning | reflect |
| cognition/notebook.py | Code notebook | execute_cell |
| cognition/reactive_engine.py | Reactive | react |
| cognition/self_improvement.py | Self-improve | improve |
| cognition/verification.py | Verification | verify |

### Engine Directory (~40 files)

**Core 10-Step Files:**
| File | Step | Key Functions |
|------|------|---------------|
| omega_codex.py | 4 (OMEGA STACK) | execute, execute_full_10step |
| omega_forge.py | 3 (PLANNER) | generate_plan, get_file_order |
| omega_gan.py | 8 (IMPROVER) | generate_and_refine |
| omega_feedback_loop.py | 5 (REACTIVE) | process, run_linter |
| omega_meta_logic.py | 1-2 (COGNITION) | analyze_failure_patterns |
| omega_rag.py | 9 (KNOWLEDGE) | retrieve, add_to_memory |
| omega_repo_map.py | TOOL | build_index, get_file_order |
| omega_shell_tools.py | 7 (EXECUTOR) | run |
| omega_lsp_client.py | 10 (VERIFY) | get_diagnostics |
| omega_self_eval.py | 6 (GUARDIAN) | generate_markdown_report |
| omega_hierarchical_memory.py | MEMORY | retrieve_relevant |
| omega_git_tools.py | TOOL | status, add, commit |

**Consolidated Modules (Cleanup 2024):**
| File | Purpose | Used By |
|------|--------|-------|
| omega_error_classifier.py | Unified error classification | omega_forge, omega_godel_machine, omega_meta_learner |
| omega_unified_shell.py | Unified shell execution | omega_codex, omega_seamless_service |

**Archived (Dead Code):**
| File | Origin | Reason |
|------|--------|-------|
| unused_code/archive_templates.py | omega_gan.py | CODE_TEMPLATES unused |
| unused_code/broken_py_compile_check.py | omega_codex.py | py_compile missing arg |
| unused_code/broken_testpy_ast_check.py | omega_codex.py | test.py missing |

**Additional Engine Files:**
| File | Purpose |
|------|---------|
| bridge.py | Bridge to external |
| autonomous_agent.py | Autonomous agent |
| execution_engine.py | Execution |
| local_builder.py | Local builds |
| parallel_executor.py | Parallel execution |
| state_manager.py | State management |
| cognitive_memory.py | Cognitive memory |
| intelli_daemon.py | Intelli daemon |
| task_console.py | Task console |
| agent_loop.py | Agent loop |
| autocoder.py | Auto-coder |
| meta_coder.py | Meta coder |
| omega_daemon.py | OMEGA daemon |
| omega_godel_machine.py | Godel machine |
| omega_infrastructure.py | Infrastructure |
| omega_integrator.py | Integrator |
| omega_mcp_server.py | MCP server |
| omega_meta_learner.py | Meta learning |
| omega_semantic_search.py | Semantic search |
| omega_seamless_service.py | Seamless service |
| omega_unified_service.py | Unified service |
| omega_reproducible_builds.py | Reproducible builds |
| omega_self_develop.py | Self-development |
| omega_vacuum.py | Vacuum |
| provenance.py | Provenance |
| self_correcting_memory.py | Self-correcting memory |

### Observability Directory (~5 files)

| File | Purpose | Key Functions |
|------|---------|---------------|
| observability/__init__.py | Package init | exports |
| observability/health.py | Health checks | Health.check |
| observability/metrics.py | Metrics | Metrics.record |
| observability/tracing.py | Tracing | start_span |
| observability/circuit_breaker.py | Circuit breaker | call |

### Security Directory (~7 files)

| File | Purpose | Key Functions |
|------|---------|---------------|
| security/omega_vault.py | Secrets | get_secret, set_secret |
| security/omega_access.py | RBAC | authorize |
| security/omega_audit.py | Audit | log |
| security/omega_mail.py | Email | send |
| security/omega_rotate.py | Rotation | rotate |
| security/omega_seed_gen.py | Seed gen | generate |
| security/secrets.py | Secrets util | generate_secret |

### Tools Directory (~10 files)

| File | Purpose | Key Functions |
|------|---------|---------------|
| tools/git_ops.py | Git ops | clone, pull |
| tools/docker_ops.py | Docker ops | build, run |
| tools/file_ops.py | File ops | read, write |
| tools/security_scanner.py | Security scan | scan |
| tools/test_generator.py | Test gen | generate |
| tools/github_intelligence_scanner.py | GitHub scan | scan |
| tools/github_scanner_scheduler.py | Scheduler | schedule |
| tools/quick_skill_fetch.py | Skill fetch | fetch |
| tools/status_check.py | Status check | check |

### API Directory (~2 files)

| File | Purpose | Key Functions |
|------|---------|---------------|
| api/server.py | FastAPI server | create_app, start_server |
| api/test_client.py | Test client | get, post |

### Dashboard Directory (~2 files)

| File | Purpose | Key Functions |
|------|---------|---------------|
| dashboard/app.py | Dashboard app | create_dashboard |
| dashboard/web_dashboard.py | Web UI | serve |

### Tests Directory (~15 files)

| Directory | Files |
|-----------|-------|
| tests/ | test_integration.py, test_suite.py, test_paradise_stack.py |
| tests/unit/ | test_*.py (7 files) |
| tests/integration/ | test_*.py (3 files) |
| tests/chaos/ | test_chaos_engineering.py |

### Docker Directory (~3 files)

| File | Purpose |
|------|---------|
| docker/check_deps.py | Check dependencies |
| docker/verify_env.py | Verify environment |

---

## PART 2: JAVASCRIPT FILES (.js)

### Dashboard node_modules (~1900 files)

Located in: `dashboard/node_modules/`

Key packages:
- express/ - Web framework
- body-parser/ - HTTP body parsing
- cors/ - CORS headers
- debug/ - Debug utilities
- cookie/ - Cookie handling
- etag/ - ETag headers
- http-errors/ - HTTP errors
- iconv-lite/ - Encoding
- And 50+ more...

---

## PART 3: CONFIG FILES

### YAML Files (~20)

| File | Purpose |
|------|---------|
| .github/workflows/*.yml | CI/CD workflows |
| .continue/agents/*.yaml | Agent configs |
| .continue/mcpServers/*.yaml | MCP servers |
| .aider.conf.yml | Aider config |

### JSON Files (~100)

| File | Purpose |
|------|---------|
| package.json | Node dependencies |
| docs/HELPFUNCS.md | Function reference |
| .paradise/entities.json | Entity storage |
| .omega/cache/*.json | Cache files |

---

## PART 4: DOCUMENTATION (.md)

### Core Docs (~30)

| File | Purpose |
|------|---------|
| ARCHITECTURE.md | System architecture |
| ARCHITECTURE_TEXT.md | Architecture details |
| COMPONENT_HANDSHAKES.md | Component handshakes |
| CHANGELOG.md | Version history |
| CONTRIBUTING.md | Contribution guide |
| README.md | Main readme |
| 10K_METER_ANALYSIS.md | Analysis |

### Agent Docs (in /agent/)

| File | Purpose |
|------|---------|
| agent/BEHhavior.md | Agent behavior |
| agent/CAPABILITIES.md | Capabilities |
| agent/IDENTITY.md | Identity |
| agent/LEARNING.md | Learning |
| agent/ORGANIZATION.md | Organization |
| agent/PHILOSOPHY.md | Philosophy |
| agent/POLICY.md | Policy |

---

## PART 5: WEB FILES

### HTML (~5)

| File | Purpose |
|------|---------|
| dashboard/index.html | Dashboard UI |

---

## PART 6: SHELL SCRIPTS (.sh)

| File | Purpose |
|------|---------|
| (none in project root) | - |

---

## PART 7: OUTPUT FILES

### Generated Outputs (~15)

Located in: `outputs/` and `projects/*/outputs/`

| File Pattern | Purpose |
|--------------|---------|
| outputs/wf_*/main.py | Workflow outputs |
| outputs/src/*.py | Generated code |
| projects/*/outputs/*.py | Project outputs |

---

## ENTRY POINTS

| Command | File | Description |
|---------|------|-------------|
| `python omega_codex.py --goal "..."` | omega_codex.py | Main 10-step |
| `python omega_codex.py --goal "..." --full` | omega_codex.py | Full 10-step |
| `python paradise.py` | paradise.py | Paradise system |
| `python omega_cli.py run "..."` | omega_cli.py | CLI |
| `python -m api.server` | api/server.py | REST API |
| `python agentic-os.py` | agentic-os.py | Entrypoint |
| `python run.py` | run.py | Alt entry |

---

## KEY FUNCTION REFERENCES

### Most Used Functions

| Function | File | Usage |
|----------|------|-------|
| OmegaCodex.execute | omega_codex.py | ~50 calls |
| OmegaRepoMap.build_index | omega_repo_map.py | ~30 calls |
| OmegaShellTools.run | omega_shell_tools.py | ~25 calls |
| MetaCognition.analyze_failure_patterns | omega_meta_logic.py | ~20 calls |
| OmegaGAN.generate_and_refine | omega_gan.py | ~15 calls |

### Dead Code Functions

| Function | File | Issue |
|----------|------|-------|
| OmegaLSPClient (20+ methods) | omega_lsp_client.py | Never instantiated |
| CODE_TEMPLATES (~300 lines) | omega_gan.py | Never used |
| FileAwareFeedbackLoop | omega_feedback_loop.py | Never instantiated |

---

## STATISTICS

| Category | Count |
|----------|-------|
| Python files | ~150 |
| JavaScript files | ~2000 |
| Config files (YAML/JSON) | ~120 |
| Documentation files | ~50 |
| HTML files | ~5 |
| Test files | ~15 |
| **Total** | **~2340** |

---

## Last Updated: 2026-04-16