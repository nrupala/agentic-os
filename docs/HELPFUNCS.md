# OMEGA Codex Function Reference

> Comprehensive function/method documentation for all 10-Step Architecture components

---

## File Index

| Step | Component | File | Status |
|------|----------|------|--------|
| 1-2 | COGNITION/META_COGNITION | omega_meta_logic.py | ACTIVE |
| 3 | PLANNER | omega_forge.py | ACTIVE |
| 4 | OMEGA STACK | omega_codex.py | ACTIVE |
| 5 | REACTIVE | omega_feedback_loop.py | ACTIVE |
| 6 | GUARDIAN | omega_self_eval.py | ACTIVE |
| 7 | EXECUTOR | omega_shell_tools.py | ACTIVE |
| 8 | IMPROVER | omega_gan.py | ACTIVE |
| 9 | KNOWLEDGE | omega_rag.py | ACTIVE |
| 10 | VERIFY | omega_lsp_client.py | ACTIVE |
| TOOLS | REPO MAP | omega_repo_map.py | ACTIVE |
| MEMORY | MEMORY | omega_hierarchical_memory.py | ACTIVE |

---

## Step 1-2: COGNITION / META_COGNITION

### File: `omega_meta_logic.py`

**Purpose**: Pre-frontal cortex for self-aware recursive improvement. Analyzes failure patterns and generates hard constraints.

| Function | Signature | Purpose | Called By | Status |
|----------|-----------|---------|----------|--------|
| MetaCognition.__init__ | `(self, db_path: str = None)` | Initialize meta-cognition with SQLite | omega_codex._init_paradise_stack | OK |
| _connect | `(self) -> sqlite3.Connection` | Connect to state database | MetaCognition.__init__ | OK |
| _load_rules | `(self) -> List[ThinkingRule]` | Load thinking rules from DB | MetaCognition.__init__ | OK |
| analyze_failure_patterns | `(self, limit: int = 10) -> List[FailurePattern]` | Query SQLite for last N failures | omega_codex._phase_think | OK |
| _error_type_to_constraint | `(self, error_type: str) -> str` | Map error to constraint | derive_constraints | OK |
| derive_constraints | `(self, patterns: List[FailurePattern] = None) -> List[str]` | Auto-generate Thinking Rules | omega_codex._phase_think | OK |
| _save_constraints | `(self, constraints: List[str], patterns: List[FailurePattern])` | Save constraints to DB | derive_constraints | OK |
| generate_disciplined_prompt | `(self, goal: str, constraints: List[str], patterns: List[FailurePattern])` | Inject constraints into prompt | omega_codex._phase_think | OK |
| get_active_rules | `(self) -> List[ThinkingRule]` | Get currently active rules | None | UNUSED |
| clear_rules | `(self)` | Clear all thinking rules | None | UNUSED |
| close | `(self)` | Close database connection | None | UNUSED |
| __enter__ | `(self)` | Context manager entry | None | UNUSED |
| __exit__ | `(self, exc_type, exc_val, exc_tb)` | Context manager exit | None | UNUSED |
| parse | `(response: str) -> Tuple[bool, Dict]` | Parse LLM response | None | UNUSED |
| _fuzzy_parse | `(response: str) -> Tuple[bool, Dict]` | Fuzzy parse fallback | None | UNUSED |
| analyze_project | `(project_name: str = None) -> Dict` | Analyze project failures | None | UNUSED |

**Helper Classes**:
- `FailurePattern` - Dataclass for error patterns
- `ThinkingRule` - Dataclass for thinking constraints

---

## Step 3: PLANNER

### File: `omega_forge.py`

**Purpose**: DAG-based implementation planning and code generation orchestration.

| Function | Signature | Purpose | Called By | Status |
|----------|-----------|---------|----------|--------|
| ForgeState | `(self, ...)` | Initialize forge state | None | OK |
| analyze_goal | `(self, goal: str)` | Analyze goal for requirements | None | OK |
| find_dependencies | `(self, goal: str)` | Find code dependencies | None | OK |
| resolve_imports | `(self, file_path: str)` | Resolve imports | None | OK |
| build_file_graph | `(self) -> Dict` | Build file dependency graph | None | OK |
| get_file_order | `(self) -> List[str]` | Get topological file order | omega_codex.execute_full_10step | OK |
| generate_plan | `(self, goal: str)` | Generate implementation plan | None | OK |
| _classify_error | `(self, error: str)` | Classify error type | None | OK |
| _suggest_fix | `(self, error: str)` | Suggest fix | None | OK |
| execute_goal | `(self, goal: str, iterations: int)` | Execute goal | CLI | OK |

---

## Step 4: OMEGA STACK

### File: `omega_codex.py`

**Purpose**: Main 6-phase recursive loop orchestrator (RECOLLECT → THINK → GENERATE → VERIFY → PERSIST → EVALUATE).

| Function | Signature | Purpose | Called By | Status |
|----------|-----------|---------|----------|--------|
| OmegaCodex.__init__ | `(self, project: str = "default")` | Initialize all subsystems | CLI, process_goal | OK |
| _init_paradise_stack | `(self)` | Initialize Paradise Stack components | OmegaCodex.__init__ | OK |
| _init_seamless_tools | `(self)` | Initialize verification tools | OmegaCodex.__init__ | OK |
| _phase_recollect | `(self, goal: str) -> Dict` | Load state from memory | execute | OK |
| _phase_think | `(self, goal: str, state: Dict) -> str` | RAG retrieves + Meta analyzes | execute | OK |
| _phase_generate | `(self, goal: str, prompt: str, constraints: List[str])` | GAN generates + Discriminator evaluates | execute | OK |
| _phase_verify | `(self, code: str) -> Dict` | Run linter + tests | execute | OK |
| _phase_persist | `(self, goal: str, code: str, evaluation: Dict) -> bool` | Save to memory + Git | execute | OK |
| _phase_evaluate | `(self, goal: str, iteration: int, evaluation: Dict) -> Dict` | Self-assessment | execute | OK |
| execute_full_10step | `(self, goal: str, max_iterations: int) -> Dict` | Execute all 10 steps | CLI --full | OK |
| execute | `(self, goal: str, max_iterations: int, planner_context: Dict) -> Dict` | Main 6-phase loop | CLI, process_goal | OK |
| get_status | `(self) -> Dict` | Get system status | CLI --status | OK |
| TenStepArchitecture.get_step_info | `() -> List[Dict]` | Get 10-step info | CLI --steps | OK |

**Class Enums**:
- `LoopPhase` - RECOLLECT, THINK, GENERATE, VERIFY, PERSIST, EVALUATE

---

## Step 5: REACTIVE

### File: `omega_feedback_loop.py`

**Purpose**: DAG-based reactive validation and self-correction.

| Function | Signature | Purpose | Called By | Status |
|----------|-----------|---------|----------|--------|
| FeedbackLoop.__init__ | `(self, ...)` | Initialize feedback loop | None | OK |
| process | `(self, code: str, context: Dict)` | Process code with feedback | None | OK |
| classify_error | `(self, error: str)` | Classify error type | None | OK |
| suggest_fix | `(self, error: str)` | Suggest fix | None | OK |
| apply_fix | `(self, code: str, fix: str)` | Apply fix to code | None | OK |
| run_linter | `(self, file_path: str)` | Run linter | omega_codex._phase_verify | OK |
| run_tests | `(self, test_path: str)` | Run tests | omega_codex._phase_verify | OK |
| check_file_exists | `(self, path: str)` | Check file exists | None | OK |
| get_context | `(self) -> Dict` | Get loop context | None | OK |
| reset | `(self)` | Reset loop | None | UNUSED |
| get_summary | `(self) -> Dict` | Get summary | None | UNUSED |

**Subclass** (Dead code):
- `FileAwareFeedbackLoop` - Never instantiated

---

## Step 6: GUARDIAN

### File: `omega_self_eval.py`

**Purpose**: Self-evaluation reporting and quality metrics.

| Function | Signature | Purpose | Called By | Status |
|----------|-----------|---------|----------|--------|
| SelfEvaluationReporting.__init__ | `(self, project_path: str)` | Initialize evaluator | omega_codex._init_paradise_stack | OK |
| generate_markdown_report | `(self, metrics: Dict)` | Generate markdown report | omega_codex._phase_evaluate | OK |
| get_latest_report | `(self) -> str` | Get latest report | None | UNUSED |

---

## Step 7: EXECUTOR

### File: `omega_shell_tools.py`

**Purpose**: Shell command execution and test running.

| Function | Signature | Purpose | Called By | Status |
|----------|-----------|---------|----------|--------|
| OmegaShellTools.__init__ | `(self, root_path: str)` | Initialize shell tools | omega_codex._init_seamless_tools | OK |
| is_command_safe | `(self, cmd: str) -> bool` | Check command safety | run | OK |
| run | `(self, cmd: str, timeout: int) -> Tuple[str, str, int]` | Run shell command | Multiple | OK |
| run_linter | `(self, file_path: str)` | Run ruff/pyright | None | UNUSED |
| run_test | `(self, test_path: str)` | Run pytest | None | UNUSED |
| run_typecheck | `(self, file_path: str)` | Run type checker | None | UNUSED |
| create_session | `(self)` | Create session | None | UNUSED |
| get_command_history | `(self) -> List[Dict]` | Get command history | None | UNUSED |
| FeedbackLoop.run_and_fix | `(self, code: str) -> str` | Run and auto-fix | None | UNUSED |

---

## Step 8: IMPROVER

### File: `omega_gan.py`

**Purpose**: GAN-inspired code generation (Generator + Discriminator).

| Function | Signature | Purpose | Called By | Status |
|----------|-----------|---------|----------|--------|
| OmegaGAN.__init__ | `(self, project_path: str)` | Initialize GAN | omega_codex._init_paradise_stack | OK |
| generate_and_refine | `(self, goal: str, constraints: List[str], max_iterations: int)` | Generate + refine code | omega_codex._phase_generate | OK |
| get_temporal_context | `(self) -> dict` | Get RNN-like state | omega_codex._phase_recollect | OK |
| _load_history | `(self) -> List[dict]` | Load history | OmegaGAN.__init__ | OK |
| _load_state | `(self) -> dict` | Load temporal state | OmegaGAN.__init__ | OK |
| _save_history | `(self)` | Save history | generate_and_refine | OK |
| _save_state | `(self)` | Save state | generate_and_refine | OK |
| _calculate_trend | `(self) -> str` | Calculate score trend | get_temporal_context | OK |
| CodeGenerator.__init__ | `(self)` | Initialize generator | OmegaGAN.__init__ | OK |
| CodeGenerator.generate | `(self, goal: str, constraints: List[str])` | Main generation | generate_and_refine | OK |
| CodeGenerator._generate_web_server | ... | Web server template | CodeGenerator.generate | OK |
| CodeGenerator._generate_database | ... | Database template | CodeGenerator.generate | OK |
| CodeGenerator._generate_cli | ... | CLI template | CodeGenerator.generate | OK |
| CodeGenerator._generate_basic | ... | Basic template | CodeGenerator.generate | OK |
| CodeGenerator._generate_websocket_chat | ... | WebSocket template | CodeGenerator.generate | OK |
| CodeGenerator._generate_rest_api | ... | REST API template | CodeGenerator.generate | OK |
| CodeGenerator._generate_rest_api_auth | ... | REST API+Auth template | CodeGenerator.generate | OK |
| CodeDiscriminator.__init__ | `(self)` | Initialize discriminator | OmegaGAN.__init__ | OK |
| CodeDiscriminator.evaluate | `(self, code: str, goal: str) -> dict` | Evaluate code quality | generate_and_refine | OK |

**Template Classes** (Dead code - never instantiated):
- `ZeroKnowledgeCrypto` - Zero-knowledge crypto utilities
- `IdentityManager` - Zero-identifier identity management
- `MessageStore` - Zero-knowledge message storage
- `SecureChatServer` - Secure chat server
- `SecureChatClient` - Secure chat client

---

## Step 9: KNOWLEDGE

### File: `omega_rag.py`

**Purpose**: Retrieval-Augmented Generation for long-term memory.

| Function | Signature | Purpose | Called By | Status |
|----------|-----------|---------|----------|--------|
| OmegaRAG.__init__ | `(self, project_path: str)` | Initialize RAG | omega_codex._init_paradise_stack | OK |
| retrieve | `(self, query: str, top_k: int = 3) -> List[Dict]` | Retrieve relevant chunks | _build_index | OK |
| retrieve_context | `(self, query: str, max_tokens: int = 500) -> str` | Get context string | omega_codex._phase_think | OK |
| index_code | `(self, code: str, goal: str)` | Index new code | omega_codex.execute_full_10step | OK |
| _ensure_memory | `(self)` | Ensure memory file | OmegaRAG.__init__ | OK |
| _build_index | `(self)` | Build search index | OmegaRAG.__init__ | OK |
| _reindex | `(self)` | Reindex all memory | None | OK |
| _save_index | `(self)` | Save index to disk | _reindex | OK |

---

## Step 10: VERIFY

### File: `omega_lsp_client.py`

**Purpose**: Language Server Protocol for code verification.

| Function | Signature | Purpose | Called By | Status |
|----------|-----------|---------|----------|--------|
| SimpleLSPClient.__init__ | `(self, root_path: str)` | Initialize LSP client | omega_codex._init_seamless_tools | OK |
| get_diagnostics | `(self) -> List[Dict]` | Get code diagnostics | omega_codex.execute_full_10step | OK |
| format_diagnostics | `(self, diagnostics: List[Dict])` | Format diagnostics | None | OK |

**Full Implementation** (Dead code - never used):
- `OmegaLSPClient` (20+ methods) - Full LSP implementation
  - `start_servers` - Start LSP servers
  - `stop_servers` - Stop LSP servers
  - `get_completions` - Get completions
  - `get_definitions` - Go to definition
  - `get_references` - Find references
  - `get_hover` - Get hover info
  - `get_code_actions` - Get code actions
  - `format_document` - Format document
  - And 15+ more...

---

## TOOL: REPO MAP

### File: `omega_repo_map.py`

**Purpose**: AST-based code indexing and repository mapping.

| Function | Signature | Purpose | Called By | Status |
|----------|-----------|---------|----------|--------|
| OmegaRepoMap.__init__ | `(self, root_path: Optional[str] = None)` | Initialize repo map | omega_codex._init_seamless_tools | OK |
| is_ignored | `(self, path: Path) -> bool` | Check ignore patterns | scan_files | OK |
| scan_files | `(self) -> List[Path]` | Scan for source files | build_index | OK |
| compute_file_hash | `(self, path: Path) -> str` | Compute file hash | build_index | OK |
| parse_python_symbols | `(self, path: Path) -> List[Symbol]` | Parse Python symbols | build_index | OK |
| parse_imports | `(self, path: Path) -> List[str]` | Extract imports | build_index | OK |
| build_index | `(self, force: bool = False) -> RepoIndex` | Build complete index | omega_codex._init_seamless_tools | OK |
| get_file_tree | `(self, max_depth: int = 4) -> Dict` | Get file tree | None | OK |
| get_file_order | `(self) -> List[str]` | Get DAG topological order | omega_codex.execute_full_10step | OK |
| get_file_symbols | `(self, file_path: str) -> List[Symbol]` | Get file symbols | None | UNUSED |
| find_symbol | `(self, name: str) -> List[Symbol]` | Find symbol | None | UNUSED |
| get_callers | `(self, symbol_name: str) -> List[str]` | Find callers | None | UNUSED |
| get_context_for_file | `(self, file_path: str) -> Dict` | Get file context | None | OK |
| get_relevant_context | `(self, query: str, max_tokens: int = 15000)` | Get relevant context | None | OK |
| to_dict | `(self) -> Dict` | Export index | None | OK |

**Helper Dataclasses**:
- `Symbol` - Code symbol (function, class, method)
- `FileNode` - File in repository tree
- `RepoIndex` - Complete repository index

---

## TOOL: MEMORY

### File: `omega_hierarchical_memory.py`

**Purpose**: Three-tier memory architecture (Session, Daily, Long-term).

| Function | Signature | Purpose | Called By | Status |
|----------|-----------|---------|----------|--------|
| HierarchicalMemory.__init__ | `(self, project_path: str)` | Initialize memory | omega_codex._init_paradise_stack | OK |
| write_session_state | `(self, context: dict)` | WAL Protocol write | None | OK |
| retrieve_relevant | `(self, query: str, limit: int = 5) -> list` | Retrieve memories | omega_codex._phase_recollect | OK |
| distill_wisdom | `(self, items: List[str])` | Save to long-term | omega_codex._phase_persist | OK |
| read_session_state | `(self) -> str` | Read session state | None | OK |
| read_long_term | `(self) -> str` | Read long-term memory | None | OK |

---

## Summary Statistics

| Metric | Count |
|-------|-------|
| Total Functions | ~120 |
| Active (OK) | ~45 |
| Unused (UNUSED) | ~50+ |
| Dead Code | ~25 |

---

## Usage Notes

1. **Entry Points**:
   - CLI: `python omega_codex.py --goal "your goal"`
   - API: `from omega_codex import process_goal; process_goal("goal")`
   - Full: `python omega_codex.py --goal "goal" --full`

2. **Flow**: 
   ```
   User Input → PLAN (omega_forge) → EXECUTE (omega_codex) → VERIFY → LEARN
   ```

3. **Subsystems**:
   - Paradise Stack: Memory, Meta, RAG, GAN, Evaluator
   - Seamless Tools: RepoMap, Shell, Git, LSP

---

## Consolidated Modules (Added During Cleanup)

### File: `omega_error_classifier.py`

**Purpose**: Unified error classification - replaces duplicate logic in omega_forge.py, omega_godel_machine.py, omega_meta_learner.py

| Function | Signature | Purpose | Called By | Status |
|----------|-----------|---------|----------|--------|
| ErrorCategory | `Enum` | Error type enum (TIMEOUT, SYNTAX_ERROR, etc.) | - | OK |
| ErrorClassifier | `class` | Core classifier with pattern matching | - | OK |
| classify | `(cls, error: str) -> ErrorCategory` | Classify error into category | - | OK |
| classify_str | `(error: str) -> str` | Return category as string | omega_codex | OK |
| error_to_constraint | `(error: str) -> str` | Map error to fix suggestion | omega_codex | OK |
| suggest_fix | `(error: str) -> str` | Get fix for error type | None | UNUSED |
| classify_error | `(error: str) -> str` | Convenience wrapper | omega_forge, omega_godel_machine, omega_meta_learner | OK |
| to_constraint | `(error: str) -> str` | Convenience wrapper | omega_codex | OK |
| suggest_fix | `(error: str) -> str` | Convenience wrapper | None | UNUSED |

**Usage**:
```python
from omega_error_classifier import classify_error, error_to_constraint

error_type = classify_error("TimeoutError: connection timed out")
# -> "timeout"

fix = error_to_constraint("SyntaxError: invalid syntax")
# -> "Check syntax and fix parse errors"
```

---

### File: `omega_unified_shell.py`

**Purpose**: Unified shell execution - centralizes subprocess.run calls

| Function | Signature | Purpose | Called By | Status |
|----------|-----------|---------|----------|--------|
| CommandResult | `class` | NamedTuple(return_code, stdout, stderr, timeout) | - | OK |
| UnifiedShell | `class` | Shell execution wrapper | - | OK |
| run | `(self, cmd: str, timeout: int = 30) -> CommandResult` | Run command | omega_codex, omega_seamless_service | OK |
| run_safe | `(self, cmd: str, timeout: int = 30) -> CommandResult` | Run with shell=False | None | UNUSED |
| get_shell | `(root_path: str = None) -> UnifiedShell` | Get singleton instance | None | UNUSED |

**Usage**:
```python
from omega_unified_shell import UnifiedShell

shell = UnifiedShell()
result = shell.run("ruff check .", timeout=30)
if result.return_code == 0:
    print("Passed")
```

---

### File: `unused_code/`

**Purpose**: Archived dead code - moved from active files during cleanup

| File | Origin | Reason |
|------|--------|-------|
| archive_templates.py | omega_gan.py | CODE_TEMPLATES (~300 lines) never used |
| broken_py_compile_check.py | omega_codex.py | py_compile called without file arg |
| broken_testpy_ast_check.py | omega_codex.py | test.py doesn't exist |

---

### Updated Files (Now Use Unified Modules)

| File | Change |
|------|-------|
| omega_forge.py | _classify_error now imports ErrorClassifier |
| omega_godel_machine.py | _classify_error now imports ErrorClassifier |
| omega_meta_learner.py | _classify_error now imports ErrorClassifier |