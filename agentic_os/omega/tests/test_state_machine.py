# test_state_machine.py
import pytest
import time
from agentic_os.omega.core.ledger import SelfCorrectionLedger
from agentic_os.omega.core.rules import ThinkingRules
from agentic_os.omega.core.state import (
    ActionResult,
    ForgeState,
    InvariantViolation,
    StepStatus,
    ThoughtRecord,
    VerificationRecord,
)
from agentic_os.omega.core.engine import OmegaForgeEngine


def test_forge_state_round_trip():
    status = next(iter(StepStatus))
    state = ForgeState(
        session_id="session-alpha-123",
        objective="Verify system invariants and execute tasks",
        current_iteration=2,
        max_iterations=10,
        status=status,
        steps=[],
    )

    state_dict = state.to_dict()
    restored = ForgeState.from_dict(state_dict)

    assert restored.session_id == state.session_id
    assert restored.objective == state.objective
    assert restored.current_iteration == state.current_iteration
    assert restored.max_iterations == state.max_iterations
    assert restored.status == state.status
    assert restored.steps == state.steps


def test_thought_record_invariant_violations():
    # Empty or whitespace rationale
    tr_empty_rationale = ThoughtRecord(
        thought_id="t-1",
        rationale="",
        proposed_action="run_test_command",
        verification_criterion="exit code 0",
    )
    with pytest.raises(InvariantViolation):
        tr_empty_rationale.validate_invariants()

    tr_whitespace_rationale = ThoughtRecord(
        thought_id="t-2",
        rationale="   ",
        proposed_action="run_test_command",
        verification_criterion="exit code 0",
    )
    with pytest.raises(InvariantViolation):
        tr_whitespace_rationale.validate_invariants()

    # Empty or whitespace proposed_action
    tr_empty_action = ThoughtRecord(
        thought_id="t-3",
        rationale="Valid rationale",
        proposed_action="",
        verification_criterion="exit code 0",
    )
    with pytest.raises(InvariantViolation):
        tr_empty_action.validate_invariants()

    tr_whitespace_action = ThoughtRecord(
        thought_id="t-4",
        rationale="Valid rationale",
        proposed_action="   \t  ",
        verification_criterion="exit code 0",
    )
    with pytest.raises(InvariantViolation):
        tr_whitespace_action.validate_invariants()

    # Empty or whitespace verification_criterion
    tr_empty_criterion = ThoughtRecord(
        thought_id="t-5",
        rationale="Valid rationale",
        proposed_action="run_test_command",
        verification_criterion="",
    )
    with pytest.raises(InvariantViolation):
        tr_empty_criterion.validate_invariants()

    tr_whitespace_criterion = ThoughtRecord(
        thought_id="t-6",
        rationale="Valid rationale",
        proposed_action="run_test_command",
        verification_criterion="   \n  ",
    )
    with pytest.raises(InvariantViolation):
        tr_whitespace_criterion.validate_invariants()


def test_thought_record_valid():
    record = ThoughtRecord(
        thought_id="t-valid",
        rationale="Inspect directory structure",
        proposed_action="ls -la",
        verification_criterion="output contains files",
    )
    # Valid record must not raise
    record.validate_invariants()
    assert record.thought_id == "t-valid"
    assert record.proposed_action == "ls -la"
    assert isinstance(record.timestamp, float)
