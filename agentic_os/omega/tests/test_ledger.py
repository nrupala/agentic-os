# agentic_os/omega/tests/test_ledger.py
# Copyright © 2026 2351485 ALBERTA INC.
# SPDX-License-Identifier: AGPL-3.0-only

import pytest
from pathlib import Path
from agentic_os.omega.core.ledger import SelfCorrectionLedger
from agentic_os.omega.core.rules import ThinkingRules
from agentic_os.omega.core.state import InvariantViolation




def test_signature_stability_and_uniqueness():
    ledger = SelfCorrectionLedger()
    action = "bash"
    payload1 = {"command": "pytest"}
    payload2 = {"command": "pytest -v"}

    sig1_a = ledger._compute_signature(action, payload1)
    sig1_b = ledger._compute_signature(action, payload1)
    sig2 = ledger._compute_signature(action, payload2)

    assert isinstance(sig1_a, str)
    assert len(sig1_a) == 12
    assert sig1_a == sig1_b
    assert sig1_a != sig2


def test_failure_counting():
    ledger = SelfCorrectionLedger()
    sig = ledger.record_failure(
        iteration=1,
        action_name="run_tests",
        payload={"target": "unit"},
        error_msg="AssertError",
        hypothesis="Mock failure hypothesis"
    )

    assert ledger.get_action_failure_count(sig) == 1

    ledger.record_failure(
        iteration=2,
        action_name="run_tests",
        payload={"target": "unit"},
        error_msg="AssertError 2",
        hypothesis="Second failure hypothesis"
    )

    assert ledger.get_action_failure_count(sig) == 2


def test_persistence_across_instances(tmp_path: Path):
    ledger_file = tmp_path / "ledger.json"

    ledger1 = SelfCorrectionLedger(ledger_file=ledger_file)
    sig = ledger1.record_failure(
        iteration=1,
        action_name="compile",
        payload={"target": "main"},
        error_msg="SyntaxError",
        hypothesis="Missing bracket"
    )
    assert ledger1.get_action_failure_count(sig) == 1

    ledger2 = SelfCorrectionLedger(ledger_file=ledger_file)
    assert ledger2.get_action_failure_count(sig) == 1

    ledger2.record_failure(
        iteration=2,
        action_name="compile",
        payload={"target": "main"},
        error_msg="SyntaxError",
        hypothesis="Still missing bracket"
    )
    assert ledger2.get_action_failure_count(sig) == 2


def test_anti_loop_rule_enforcement():
    ledger = SelfCorrectionLedger()
    action = "deploy"
    payload = {"env": "prod"}

    sig = ""
    for i in range(1, 3):
        sig = ledger.record_failure(
            iteration=i,
            action_name=action,
            payload=payload,
            error_msg="Fail",
            hypothesis="Retrying"
        )
        ThinkingRules.enforce_anti_loop_rule(ledger, sig)

    sig = ledger.record_failure(
        iteration=3,
        action_name=action,
        payload=payload,
        error_msg="Fail",
        hypothesis="Retrying 3rd time"
    )

    with pytest.raises(InvariantViolation):
        ThinkingRules.enforce_anti_loop_rule(ledger, sig)
