# OMEGA Codex - Complete Function Reference

> ALL functions/methods across ALL Python files in the agentic-OS project

---

## Directory Structure

| Directory | Files | Purpose |
|-----------|-------|---------|
| `/` | ~15 | Entry points, CLI |
| `/cognition/` | ~15 | Cognitive engines |
| `/engine/` | ~40 | Core OMEGA engines (10-step) |
| `/observability/` | ~5 | Health, metrics, tracing |
| `/security/` | ~7 | Vault, access, audit |
| `/tools/` | ~10 | Git, Docker, file ops |
| `/api/` | ~2 | REST API |
| `/dashboard/` | ~2 | Web dashboard |
| `/tests/` | ~15 | Test suites |
| `/references/` | ~15 | Reference implementations |

---

## ROOT DIRECTORY FILES

### `agentic-os.py`

| Function | Signature | Purpose | Status |
|---------|-----------|---------|--------|
| main | `(args)` | Entry point | OK |
| setup_logging | `()` | Setup logging | OK |

### `paradise.py`

| Function | Signature | Purpose | Status |
|---------|-----------|---------|--------|
| ParadiseSystem | `class` | Main paradise system | OK |
| initialize | `(self)` | Initialize | OK |
| run_goal | `(self, goal)` | Execute goal | OK |

### `paradise_cli.py`

| Function | Signature | Purpose | Status |
|---------|-----------|---------|--------|
| main | `()` | CLI entry | OK |
| parse_args | `()` | Parse arguments | OK |

### `paradise_chat.py`

| Function | Signature | Purpose | Status |
|---------|-----------|---------|--------|
| ChatClient | `class` | Chat interface | OK |
| run | `()` | Run chat | OK |

### `omega_cli.py`

| Function | Signature | Purpose | Status |
|---------|-----------|---------|--------|
| main | `()` | CLI entry | OK |
| run_goal | `(goal, opts)` | Execute | OK |

### `run.py`

| Function | Signature | Purpose | Status |
|---------|-----------|---------|--------|
| main | `()` | Run entry | OK |

### `entrypoint.py`

| Function | Signature | Purpose | Status |
|---------|-----------|---------|--------|
| main | `()` | Entry | OK |

### `quickstart.py`

| Function | Signature | Purpose | Status |
|---------|-----------|---------|--------|
| main | `()` | Quick start | OK |

---

## COGNITION DIRECTORY

### `cognition/__init__.py`

Exports: `Agent`, `Team`, `Orchestrator`

### `cognition/orchestrator.py`

| Function | Signature | Purpose | Status |
|---------|-----------|---------|--------|
| Orchestrator | `class` | Main orchestrator | OK |
| run | `(goal)` | Execute | OK |

### `cognition/master_orchestrator.py`

| Function | Signature | Purpose | Status |
|---------|-----------|---------|--------|
| MasterOrchestrator | `class` | Master coordination | OK |
| orchestrate | `(goals)` | Coordinate | OK |

### `cognition/pdc_orchestrator.py`

| Function | Signature | Purpose | Status |
|---------|-----------|---------|--------|
| PDCOrchestrator | `class` | Plan-Do-Check | OK |
| plan | `(goal)` | Plan phase | OK |
| do | `(plan)` | Do phase | OK |
| check | `(result)` | Check phase | OK |

### `cognition/agent_pairing.py`

| Function | Signature | Purpose | Status |
|---------|-----------|---------|--------|
| AgentPairing | `class` | Agent pairing | OK |
| pair | `(agents)` | Pair agents | OK |

### `cognition/agent_personas.py`

| Function | Signature | Purpose | Status |
|---------|-----------|---------|--------|
| AgentPersonas | `class` | Agent personas | OK |
| get_persona | `(name)` | Get persona | OK |

### `cognition/continuous_intelligence.py`

| Function | Signature | Purpose | Status |
|---------|-----------|---------|--------|
| ContinuousIntelligence | `class` | Continuous learning | OK |
| learn | `(experience)` | Learn | OK |

### `cognition/engineering_teams.py`

| Function | Signature | Purpose | Status |
|---------|-----------|---------|--------|
| EngineeringTeam | `class` | Team mgmt | OK |
| assign_task | `(task)` | Assign | OK |

### `cognition/entities.py`

| Function | Signature | Purpose | Status |
|---------|-----------|---------|--------|
| Entity | `class` | Base entity | OK |
| Agent | `class` | Agent entity | OK |
| Team | `class` | Team entity | OK |

### `cognition/knowledge_graph.py`

| Function | Signature | Purpose | Status |
|---------|-----------|---------|--------|
| KnowledgeGraph | `class` | Graph DB | OK |
| add_node | `(node)` | Add node | OK |
| add_edge | `(from, to)` | Add edge | OK |
| query | `(pattern)` | Query | OK |

### `cognition/meta_cognition.py`

| Function | Signature | Purpose | Status |
|---------|-----------|---------|--------|
| MetaCognition | `class` | Meta reasoning | OK |
| reflect | `(experience)` | Reflect | OK |

### `cognition/notebook.py`

| Function | Signature | Purpose | Status |
|---------|-----------|---------|--------|
| Notebook | `class` | Code notebook | OK |
| execute_cell | `(code)` | Execute | OK |

### `cognition/reactive_engine.py`

| Function | Signature | Purpose | Status |
|---------|-----------|---------|--------|
| ReactiveEngine | `class` | Reactive processing | OK |
| react | `(stimulus)` | React | OK |

### `cognition/self_improvement.py`

| Function | Signature | Purpose | Status |
|---------|-----------|---------|--------|
| SelfImprovement | `class` | Self-improvement | OK |
| improve | `(feedback)` | Improve | OK |

### `cognition/verification.py`

| Function | Signature | Purpose | Status |
|---------|-----------|---------|--------|
| VerificationEngine | `class` | Code verification | OK |
| verify | `(code)` | Verify | OK |

---

## ENGINE DIRECTORY (Core)

### `engine/omega_codex.py`

| Function | Signature | Purpose | Status |
|---------|-----------|---------|--------|
| OmegaCodex | `class` | Main orchestrator | OK |
| execute | `(goal)` | Execute 6-phase | OK |
| execute_full_10step | `(goal)` | Execute 10-step | OK |

### `engine/omega_forge.py`

| Function | Signature | Purpose | Status |
|---------|-----------|---------|--------|
| ForgeState | `class` | Forge state | OK |
| generate_plan | `(goal)` | Generate plan | OK |
| get_file_order | `()` | DAG order | OK |

### `engine/omega_gan.py`

| Function | Signature | Purpose | Status |
|---------|-----------|---------|--------|
| OmegaGAN | `class` | GAN generator | OK |
| generate_and_refine | `(goal, constraints)` | Generate code | OK |
| CodeGenerator | `class` | Code generator | OK |
| CodeDiscriminator | `class` | Code evaluator | OK |

### `engine/omega_feedback_loop.py`

| Function | Signature | Purpose | Status |
|---------|-----------|---------|--------|
| FeedbackLoop | `class` | Feedback loop | OK |
| process | `(code)` | Process code | OK |
| run_linter | `(path)` | Run linter | OK |

### `engine/omega_meta_logic.py`

| Function | Signature | Purpose | Status |
|---------|-----------|---------|--------|
| MetaCognition | `class` | Meta reasoning | OK |
| analyze_failure_patterns | `()` | Analyze failures | OK |
| derive_constraints | `(patterns)` | Derive constraints | OK |

### `engine/omega_rag.py`

| Function | Signature | Purpose | Status |
|---------|-----------|---------|--------|
| OmegaRAG | `class` | RAG retrieval | OK |
| retrieve | `(query)` | Retrieve | OK |
| index_code | `(code)` | Index code | OK |

### `engine/omega_repo_map.py`

| Function | Signature | Purpose | Status |
|---------|-----------|---------|--------|
| OmegaRepoMap | `class` | Repo mapping | OK |
| build_index | `()` | Build index | OK |
| get_file_order | `()` | Get file order | OK |

### `engine/omega_shell_tools.py`

| Function | Signature | Purpose | Status |
|---------|-----------|---------|--------|
| OmegaShellTools | `class` | Shell execution | OK |
| run | `(cmd)` | Run command | OK |

### `engine/omega_lsp_client.py`

| Function | Signature | Purpose | Status |
|---------|-----------|---------|--------|
| SimpleLSPClient | `class` | LSP client | OK |
| get_diagnostics | `()` | Get diagnostics | OK |
| OmegaLSPClient | `class` | Full LSP (DEAD) | UNUSED |

### `engine/omega_error_classifier.py` (CONSOLIDATED)

| Function | Signature | Purpose | Status |
|---------|-----------|---------|--------|
| ErrorCategory | `Enum` | Error types | OK |
| ErrorClassifier | `class` | Classifier | OK |
| classify | `(error: str)` | Classify error | OK |
| classify_str | `(error: str)` | Return as string | OK |
| classify_error | `(error: str)` | Convenience func | OK |
| error_to_constraint | `(error: str)` | Get fix | OK |
| to_constraint | `(error: str)` | Convenience func | OK |
| suggest_fix | `(error: str)` | Suggest fix | OK |

### `engine/omega_unified_shell.py` (CONSOLIDATED)

| Function | Signature | Purpose | Status |
|---------|-----------|---------|--------|
| CommandResult | `NamedTuple` | Result container | OK |
| UnifiedShell | `class` | Shell wrapper | OK |
| run | `(cmd, timeout)` | Run command | OK |
| get_shell | `()` | Singleton | UNUSED |

### `engine/unused_code/` (ARCHIVED)

| File | Origin | Reason |
|------|--------|--------|
| archive_templates.py | omega_gan.py | CODE_TEMPLATES unused |
| broken_py_compile_check.py | omega_codex.py | Missing file arg |
| broken_testpy_ast_check.py | omega_codex.py | test.py missing |

### `engine/omega_hierarchical_memory.py`

| Function | Signature | Purpose | Status |
|---------|-----------|---------|--------|
| HierarchicalMemory | `class` | 3-tier memory | OK |
| retrieve_relevant | `(query)` | Retrieve | OK |
| distill_wisdom | `(items)` | Save wisdom | OK |

### `engine/omega_self_eval.py`

| Function | Signature | Purpose | Status |
|---------|-----------|---------|--------|
| SelfEvaluationReporting | `class` | Self-eval | OK |
| generate_markdown_report | `(metrics)` | Generate | OK |

### `engine/omega_git_tools.py`

| Function | Signature | Purpose | Status |
|---------|-----------|---------|--------|
| OmegaGitTools | `class` | Git operations | OK |
| status | `()` | Get status | OK |
| add | `(files)` | Stage files | OK |
| commit | `(msg)` | Commit | OK |

### Additional Engine Files

| File | Key Functions |
|------|--------------|
| bridge.py | `Bridge` class |
| autonomous_agent.py | `AutonomousAgent` class |
| execution_engine.py | `ExecutionEngine` class |
| local_builder.py | `LocalBuilder` class |
| parallel_executor.py | `ParallelExecutor` class |
| state_manager.py | `StateManager` class |
| cognitive_memory.py | `CognitiveMemory` class |
| intelli_daemon.py | `IntelliDaemon` class |
| task_console.py | `TaskConsole` class |

### ZERO-KNOWLEDGE MODULES (NUCLEAR SAFETY)

> **NUCLEAR GRADE**: Every phase writes to encrypted file. If RAM fails, resume from file.

### `engine/zero_knowledge_handoff.py`

| Function | Signature | Purpose | Status |
|---------|-----------|---------|--------|
| PhaseSignal | `class` | Encrypted signal | OK |
| ZeroKnowledgeHandoff | `class` | Main handoff | OK |
| write_phase | `(proj, phase, data)` | Encrypt to file | OK |
| read_phase | `(proj, phase)` | Decrypt from file | OK |

### `engine/omega_phase_encryptor.py`

| Function | Signature | Purpose | Status |
|---------|-----------|---------|--------|
| EncryptedPayload | `class` | Encrypted data | OK |
| PhaseFile | `class` | File metadata | OK |
| OmegaPhaseEncryptor | `class` | Main encryptor | OK |
| encrypt_string | `(text)` | Encrypt text | OK |
| decrypt_string | `(payload)` | Decrypt text | OK |
| encrypt_code | `(code, name)` | Encrypt code | OK |
| decrypt_code | `(name)` | Decrypt code | OK |
| encrypt_memory | `(data, type)` | Encrypt memory | OK |
| decrypt_memory | `(type)` | Decrypt memory | OK |
| encrypt_for_transit | `(data)` | Network encrypt | OK |
| decrypt_from_transit | `(data)` | Network decrypt | OK |

### `engine/omega_resume.py`

| Function | Signature | Purpose | Status |
|---------|-----------|---------|--------|
| ResumePoint | `class` | Checkpoint data | OK |
| ZeroKnowledgeResume | `class` | Resume manager | OK |
| check_resume | `(proj)` | Check status | OK |
| can_resume | `(proj)` | Can resume? | OK |
| get_resume_data | `(proj, phase)` | Get data | OK |

---

## OBSERVABILITY DIRECTORY

### `observability/__init__.py`

Exports: `Health`, `Metrics`, `Tracing`

### `observability/health.py`

| Function | Signature | Purpose | Status |
|---------|-----------|---------|--------|
| Health | `class` | Health checks | OK |
| check | `()` | Perform check | OK |
| is_healthy | `()` | Get status | OK |

### `observability/metrics.py`

| Function | Signature | Purpose | Status |
|---------|-----------|---------|--------|
| Metrics | `class` | Metrics collection | OK |
| record | `(name, value)` | Record metric | OK |
| get_metrics | `()` | Get all | OK |

### `observability/tracing.py`

| Function | Signature | Purpose | Status |
|---------|-----------|---------|--------|
| Tracing | `class` | Distributed tracing | OK |
| start_span | `(name)` | Start span | OK |
| end_span | `(span)` | End span | OK |

### `observability/circuit_breaker.py`

| Function | Signature | Purpose | Status |
|---------|-----------|---------|--------|
| CircuitBreaker | `class` | Circuit breaker | OK |
| call | `(func)` | Execute with CB | OK |
| is_open | `()` | Check state | OK |

---

## SECURITY DIRECTORY

### `security/omega_vault.py`

| Function | Signature | Purpose | Status |
|---------|-----------|---------|--------|
| VaultManager | `class` | Secret management | OK |
| get_secret | `(key)` | Get secret | OK |
| set_secret | `(key, value)` | Set secret | OK |

### `security/omega_access.py`

| Function | Signature | Purpose | Status |
|---------|-----------|---------|--------|
| AccessControl | `class` | RBAC | OK |
| authorize | `(user, action)` | Authorize | OK |

### `security/omega_audit.py`

| Function | Signature | Purpose | Status |
|---------|-----------|---------|--------|
| AuditLogger | `class` | Audit logging | OK |
| log | `(event)` | Log event | OK |

### `security/omega_mail.py`

| Function | Signature | Purpose | Status |
|---------|-----------|---------|--------|
| Mailer | `class` | Email notifications | OK |
| send | `(to, subject, body)` | Send email | OK |

### `security/secrets.py`

| Function | Signature | Purpose | Status |
|---------|-----------|---------|--------|
| generate_secret | `()` | Gen secret | OK |
| hash_secret | `(secret)` | Hash | OK |

---

## TOOLS DIRECTORY

### `tools/git_ops.py`

| Function | Signature | Purpose | Status |
|---------|-----------|---------|--------|
| GitOps | `class` | Git operations | OK |
| clone | `(repo)` | Clone repo | OK |
| pull | `()` | Pull changes | OK |

### `tools/docker_ops.py`

| Function | Signature | Purpose | Status |
|---------|-----------|---------|--------|
| DockerOps | `class` | Docker ops | OK |
| build | `(image)` | Build image | OK |
| run | `(container)` | Run container | OK |

### `tools/file_ops.py`

| Function | Signature | Purpose | Status |
|---------|-----------|---------|--------|
| FileOps | `class` | File operations | OK |
| read | `(path)` | Read file | OK |
| write | `(path, content)` | Write file | OK |

### `tools/security_scanner.py`

| Function | Signature | Purpose | Status |
|---------|-----------|---------|--------|
| SecurityScanner | `class` | Security scan | OK |
| scan | `(path)` | Scan files | OK |

### `tools/test_generator.py`

| Function | Signature | Purpose | Status |
|---------|-----------|---------|--------|
| TestGenerator | `class` | Test generation | OK |
| generate | `(code)` | Generate tests | OK |

---

## API DIRECTORY

### `api/server.py`

| Function | Signature | Purpose | Status |
|---------|-----------|---------|--------|
| create_app | `()` | Create FastAPI app | OK |
| start_server | `()` | Start server | OK |

### `api/test_client.py`

| Function | Signature | Purpose | Status |
|---------|-----------|---------|--------|
| APITestClient | `class` | Test client | OK |
| get | `(url)` | GET request | OK |
| post | `(url, data)` | POST request | OK |

---

## DASHBOARD DIRECTORY

### `dashboard/app.py`

| Function | Signature | Purpose | Status |
|---------|-----------|---------|--------|
| create_dashboard | `()` | Create dashboard | OK |
| run | `()` | Run dashboard | OK |

---

## TESTS DIRECTORY

### `tests/test_integration.py`

Key: `test_full_flow()`, `test_code_generation()`

### `tests/unit/test_file_ops.py`

Key: `test_read()`, `test_write()`

---

## SUMMARY

| Category | Files | Functions |
|-----------|-------|-----------|
| Root | ~15 | ~30 |
| Cognition | ~15 | ~60 |
| Engine | ~40 | ~200 |
| Observability | ~5 | ~25 |
| Security | ~7 | ~35 |
| Tools | ~10 | ~50 |
| API | ~2 | ~10 |
| Dashboard | ~2 | ~10 |
| Tests | ~15 | ~100 |
| **TOTAL** | **~111** | **~520** |

### Usage Statistics

| Status | Count | Percentage |
|--------|-------|-----------|
| OK (Active) | ~120 | ~23% |
| UNUSED | ~400 | ~77% |
| DEAD CODE | ~50 | ~10% |

---

## Entry Points

| Command | File |
|--------|------|
| `python omega_codex.py --goal "..."` | omega_codex.py |
| `python paradise.py --goal "..."` | paradise.py |
| `python omega_cli.py run "..."` | omega_cli.py |
| `python -m api.server` | api/server.py |
| `python agentic-os.py` | agentic-os.py |