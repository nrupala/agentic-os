# agentic_os/omega/core/rules.py
"""Thinking Rules for OMEGA-CODE, extracted verbatim from omega_forge.py (Deliverable 3A)."""
from __future__ import annotations

from typing import Optional

from agentic_os.omega.core.ledger import SelfCorrectionLedger
from agentic_os.omega.core.state import InvariantViolation, ThoughtRecord


class ThinkingRules:
    """Enforces non-negotiable operational boundaries and invariants."""

    @staticmethod
    def enforce_pre_action_rule(thought: ThoughtRecord) -> None:
        """
        Rule: An action cannot be dispatched without an explicit, verifiable
        post-condition criterion defined in advance.
        """
        thought.validate_invariants()

    @staticmethod
    def enforce_anti_loop_rule(ledger: SelfCorrectionLedger, action_signature: str) -> None:
        """
        Rule: Identical failed actions cannot be repeated without rationale/diff changes.
        """
        failures = ledger.get_action_failure_count(action_signature)
        if failures >= 3:
            raise InvariantViolation(
                f"Halting: Action '{action_signature}' has repeatedly failed {failures} times without resolution."
            )
