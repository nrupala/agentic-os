================================================================================
PROJECT SPECIFICATION: OMEGA-CODE ENGINE INTEGRATION
REPOSITORY: nrupala/agentic-os
PHASE: 02 (Core Runtime Engine & Autonomous Execution Pipeline)
STATUS: ACTIVE
================================================================================

1. ARCHITECTURAL OVERVIEW
OMEGA-CODE is the deterministic agentic development kernel executing inside
agentic-os. Phase 2 establishes the core runtime loop (Thought -> Action ->
Verify), state serialization, and recursive self-correction ledger. All execution
operates under fail-closed invariants: no action runs without a prior explicit
verification criterion; no state advances without deterministic verification output.

2. TARGET DIRECTORY MATRIX
agentic_os/
└── omega/
    ├── __init__.py
    ├── core/
    ├── engine.py                  # Orchestration & loop execution
    ├── state.py                   # State models, serialization, transitions
    ├── ledger.py                  # Self-correction ledger & error diffing
    ├── rules.py                   # Thinking rules & invariant enforcers
    └── sandbox.py                 # Isolated subprocess & tool execution runner
    ├── tools/
    │   ├── __init__.py
    │   ├── base.py                # Abstract Base Tool interface
    │   ├── git_ops.py             # Atomic commit & branch management
    │   └── file_ops.py            # Guarded file IO
    └── tests/
        ├── __init__.py
        ├── test_state_machine.py  # Serialization, transitions, resume tests
        ├── test_engine_loop.py    # Thought-Action-Verify mock runs
        └── test_ledger.py         # Regression detection & error accounting

3. MILESTONES & ACCEPTANCE CRITERIA

[M2.1] Core Forge Loop & State Persistence
  - File: agentic_os/omega/core/engine.py, agentic_os/omega/core/state.py
  - Criteria:
    * Complete serialize/deserialize roundtrips preserve execution state to disk.
    * Engine can pause at any step and resume execution without state loss.
    * Cycle transitions strictly follow: IDLE -> THINKING -> ACTION -> VERIFY -> (RESOLVED | RETRY | HALTED).

[M2.2] Self-Correction Ledger & Thinking Rules Invariant
  - File: agentic_os/omega/core/ledger.py, agentic_os/omega/core/rules.py
  - Criteria:
    * Deduplication of failed action signatures (prevents repetitive failure loops).
    * Bounded retry counters trigger hard escalation when threshold is breached.
    * Thought records must declare an explicit verification criterion before tool emission.

[M2.3] Guarded Action Execution & Vault Git Lane
  - File: agentic_os/omega/tools/git_ops.py, agentic_os/omega/core/sandbox.py
  - Criteria:
    * Atomic commit messages follow standard: [ITERATION-n] [PASS|FAIL] <context>.
    * Subprocess execution captures stdout/stderr, execution time, and exit codes.
    * Unhandled errors fail closed and register to the correction ledger.

4. PHASE 2 GATEWAY TEST CRITERIA
  - Test Suite: `pytest agentic_os/omega/tests/ -v --strict-markers`
  - Zero-Tolerance Conditions:
    * 0 unhandled exceptions.
    * 0 dangling subprocesses.
    * 100% deterministic state resume from a serialized checkpoint.
