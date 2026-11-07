# Copyright © 2026 2351485 ALBERTA INC.
# SPDX-License-Identifier: AGPL-3.0-only
# agentic_os/omega/tests/test_engine_loop.py
"""Engine loop tests for OmegaForgeEngine (Deliverable 3C).

Scenarios are Gemini's from her plan matrix; the harness wrote this file
against the real API on main after her two versions targeted an invented
constructor-injected API. Mock pattern follows her __main__ self-test.
"""
from pathlib import Path

import pytest

from agentic_os.omega.core.engine import OmegaForgeEngine
from agentic_os.omega.core.state import (
    ActionResult,
    InvariantViolation,
    StepStatus,
    ThoughtRecord,
    VerificationRecord,
)


def _thought(action: str, iteration: int) -> ThoughtRecord:
    return ThoughtRecord(
        thought_id=f"T-{iteration}",
        rationale="test rationale",
        proposed_action=action,
        verification_criterion="executor output accepted by verifier",
    )


def _ok_action(thought: ThoughtRecord) -> ActionResult:
    return ActionResult(
        action_name=thought.proposed_action, payload={}, output="done",
        error=None, exit_code=0, duration_ms=0.1,
    )


def _pass_verifier(thought, action):
    return VerificationRecord(passed=True, diagnostic_message="ok",
                              observed_state={"exit_code": action.exit_code})


def _fail_verifier(thought, action):
    return VerificationRecord(passed=False, diagnostic_message="not good enough",
                              observed_state={"exit_code": action.exit_code})


def test_passing_run_completes_in_one_iteration(tmp_path: Path):
    engine = OmegaForgeEngine("s1", "obj", tmp_path, max_iterations=5)
    status = engine.run_until_complete(lambda s, l: _thought("do_it", s.current_iteration), _ok_action, _pass_verifier)
    assert status == StepStatus.PASS
    assert engine.state.current_iteration == 1


def test_failing_verifier_terminates_within_max_iterations(tmp_path: Path):
    engine = OmegaForgeEngine("s2", "obj", tmp_path, max_iterations=3)
    # Vary the action each iteration so the anti-loop rule is not the terminator.
    status = engine.run_until_complete(
        lambda s, l: _thought(f"attempt_{s.current_iteration}", s.current_iteration),
        _ok_action, _fail_verifier)
    assert status == StepStatus.HALTED
    assert engine.state.current_iteration == 3


def test_repeated_identical_failure_trips_anti_loop(tmp_path: Path):
    engine = OmegaForgeEngine("s3", "obj", tmp_path, max_iterations=10)
    with pytest.raises(InvariantViolation):
        engine.run_until_complete(lambda s, l: _thought("same_action", s.current_iteration), _ok_action, _fail_verifier)


def test_self_correction_recovery_fail_then_pass(tmp_path: Path):
    engine = OmegaForgeEngine("s4", "obj", tmp_path, max_iterations=5)

    def thought_fn(state, ledger):
        action = "flaky_action" if state.current_iteration == 0 else "fixed_action"
        return _thought(action, state.current_iteration)

    def verifier(thought, action):
        ok = thought.proposed_action == "fixed_action"
        return VerificationRecord(passed=ok, diagnostic_message="ok" if ok else "still broken",
                                  observed_state={})

    status = engine.run_until_complete(thought_fn, _ok_action, verifier)
    assert status == StepStatus.PASS
    assert engine.state.current_iteration == 2


def test_thought_invariant_violation_halts_run(tmp_path: Path):
    engine = OmegaForgeEngine("s5", "obj", tmp_path, max_iterations=3)

    def bad_thought(state, ledger):
        return ThoughtRecord(thought_id="T", rationale="", proposed_action="x",
                             verification_criterion="y")

    with pytest.raises(InvariantViolation):
        engine.run_until_complete(bad_thought, _ok_action, _pass_verifier)


def test_resuming_engine_from_persisted_state(tmp_path: Path):
    engine = OmegaForgeEngine("s6", "obj", tmp_path, max_iterations=5)
    status = engine.step(lambda s, l: _thought("first", 0), _ok_action, _fail_verifier)
    assert status == StepStatus.FAIL
    assert engine.state.current_iteration == 1

    engine2 = OmegaForgeEngine("s6", "obj", tmp_path, max_iterations=5)
    assert engine2.state.current_iteration == 1
    status = engine2.run_until_complete(lambda s, l: _thought("second", s.current_iteration), _ok_action, _pass_verifier)
    assert status == StepStatus.PASS
    assert engine2.state.current_iteration == 2
