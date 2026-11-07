# agentic_os/omega/core/state.py
"""State models for OMEGA-CODE, extracted verbatim from omega_forge.py (Deliverable 3A).

Extraction by the harness after two Gemini attempts drifted from the contracts
on main; class names, fields, enum values and semantics are identical to the
monolith. Only imports and this docstring were added.
"""
from __future__ import annotations

import enum
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


class StepStatus(str, enum.Enum):
    PENDING = "PENDING"
    THINKING = "THINKING"
    ACTING = "ACTING"
    VERIFYING = "VERIFYING"
    PASS = "PASS"
    FAIL = "FAIL"
    HALTED = "HALTED"


class InvariantViolation(Exception):
    """Raised when an internal OMEGA thinking rule is violated."""
    pass


# ---------------------------------------------------------------------------
# Data Models & Serialization
# ---------------------------------------------------------------------------

@dataclass
class ThoughtRecord:
    thought_id: str
    rationale: str
    proposed_action: str
    verification_criterion: str
    timestamp: float = field(default_factory=time.time)

    def validate_invariants(self) -> None:
        if not self.rationale.strip():
            raise InvariantViolation("Invariant Violation: Rationale cannot be empty.")
        if not self.proposed_action.strip():
            raise InvariantViolation("Invariant Violation: Proposed action cannot be empty.")
        if not self.verification_criterion.strip():
            raise InvariantViolation("Invariant Violation: Verification criterion must be explicitly defined.")


@dataclass
class ActionResult:
    action_name: str
    payload: Dict[str, Any]
    output: str
    error: Optional[str]
    exit_code: int
    duration_ms: float
    timestamp: float = field(default_factory=time.time)


@dataclass
class VerificationRecord:
    passed: bool
    diagnostic_message: str
    observed_state: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)


@dataclass
class CycleStep:
    iteration: int
    status: StepStatus
    thought: Optional[ThoughtRecord] = None
    action: Optional[ActionResult] = None
    verification: Optional[VerificationRecord] = None
    error_recovery_notes: Optional[str] = None


@dataclass
class ForgeState:
    session_id: str
    objective: str
    current_iteration: int
    max_iterations: int
    status: StepStatus
    steps: List[CycleStep] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ForgeState:
        steps_raw = data.pop("steps", [])
        state = cls(**data)
        for s in steps_raw:
            thought = ThoughtRecord(**s["thought"]) if s.get("thought") else None
            action = ActionResult(**s["action"]) if s.get("action") else None
            verification = VerificationRecord(**s["verification"]) if s.get("verification") else None
            step = CycleStep(
                iteration=s["iteration"],
                status=StepStatus(s["status"]),
                thought=thought,
                action=action,
                verification=verification,
                error_recovery_notes=s.get("error_recovery_notes"),
            )
            state.steps.append(step)
        return state
