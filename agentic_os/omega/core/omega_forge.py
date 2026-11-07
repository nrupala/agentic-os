# Copyright © 2026 2351485 ALBERTA INC.
# SPDX-License-Identifier: AGPL-3.0-only
# agentic_os/omega/core/omega_forge.py
"""Compatibility shim: re-exports the decomposed OMEGA-CODE core modules.

The monolith was decomposed in Deliverable 3 (state.py, ledger.py, rules.py,
engine.py). Existing imports from this module keep working unchanged.
"""
from __future__ import annotations

from agentic_os.omega.core.engine import ActionDispatcher, OmegaForgeEngine
from agentic_os.omega.core.ledger import SelfCorrectionLedger
from agentic_os.omega.core.rules import ThinkingRules
from agentic_os.omega.core.state import (
    ActionResult,
    CycleStep,
    ForgeState,
    InvariantViolation,
    StepStatus,
    ThoughtRecord,
    VerificationRecord,
)

__all__ = [
    "ActionDispatcher",
    "ActionResult",
    "CycleStep",
    "ForgeState",
    "InvariantViolation",
    "OmegaForgeEngine",
    "SelfCorrectionLedger",
    "StepStatus",
    "ThinkingRules",
    "ThoughtRecord",
    "VerificationRecord",
]
