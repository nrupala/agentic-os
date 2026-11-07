# Copyright © 2026 2351485 ALBERTA INC.
# SPDX-License-Identifier: AGPL-3.0-only
# agentic_os/omega/core/engine.py
"""OmegaForge engine for OMEGA-CODE, rewired onto the decomposed core modules.

The class bodies are verbatim from omega_forge.py (Deliverable 1); only the
imports changed. Rewire completed by the harness after two Gemini attempts
truncated mid-file.
"""
from __future__ import annotations

import json
import logging
import subprocess
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger("OMEGA-FORGE")

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


# ---------------------------------------------------------------------------
# Action Execution Interface
# ---------------------------------------------------------------------------
class ActionDispatcher:
    """Executes validated external actions and system operations."""

    def execute_command(self, command: str, cwd: Optional[Path] = None) -> ActionResult:
        start_time = time.time()
        try:
            res = subprocess.run(
                command,
                shell=True,
                cwd=str(cwd) if cwd else None,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=120,
            )
            duration = (time.time() - start_time) * 1000.0
            return ActionResult(
                action_name="shell_command",
                payload={"command": command, "cwd": str(cwd) if cwd else "."},
                output=res.stdout,
                error=res.stderr if res.returncode != 0 else None,
                exit_code=res.returncode,
                duration_ms=duration,
            )
        except subprocess.TimeoutExpired:
            duration = (time.time() - start_time) * 1000.0
            return ActionResult(
                action_name="shell_command",
                payload={"command": command, "cwd": str(cwd) if cwd else "."},
                output="",
                error="Action timed out after 120 seconds.",
                exit_code=-1,
                duration_ms=duration,
            )
        except Exception as ex:
            duration = (time.time() - start_time) * 1000.0
            return ActionResult(
                action_name="shell_command",
                payload={"command": command, "cwd": str(cwd) if cwd else "."},
                output="",
                error=str(ex),
                exit_code=-1,
                duration_ms=duration,
            )


# ---------------------------------------------------------------------------
# OMEGA Forge Engine
# ---------------------------------------------------------------------------
class OmegaForgeEngine:
    def __init__(
        self,
        session_id: str,
        objective: str,
        workspace_dir: Path,
        max_iterations: int = 10,
    ):
        self.workspace_dir = Path(workspace_dir).resolve()
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        self.state_file = self.workspace_dir / ".omega_state.json"
        self.ledger_file = self.workspace_dir / ".omega_ledger.json"

        self.ledger = SelfCorrectionLedger(self.ledger_file)
        self.dispatcher = ActionDispatcher()

        # Load or initialize state
        if self.state_file.exists():
            self.state = self._load_state()
            logger.info("Resumed session %s at iteration %d", self.state.session_id, self.state.current_iteration)
        else:
            self.state = ForgeState(
                session_id=session_id,
                objective=objective,
                current_iteration=0,
                max_iterations=max_iterations,
                status=StepStatus.PENDING,
            )
            self._persist_state()
            logger.info("Initialized new session %s", session_id)

    def _persist_state(self) -> None:
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(self.state.to_dict(), f, indent=2)

    def _load_state(self) -> ForgeState:
        with open(self.state_file, "r", encoding="utf-8") as f:
            return ForgeState.from_dict(json.load(f))

    def step(
        self,
        thought_fn: Callable[[ForgeState, SelfCorrectionLedger], ThoughtRecord],
        action_executor: Callable[[ThoughtRecord], ActionResult],
        verifier_fn: Callable[[ThoughtRecord, ActionResult], VerificationRecord],
    ) -> StepStatus:
        """
        Executes one full cycle of the Thought-Action-Verify loop.
        """
        if self.state.status in (StepStatus.PASS, StepStatus.HALTED):
            logger.info("Engine is in terminal status: %s", self.state.status)
            return self.state.status

        if self.state.current_iteration >= self.state.max_iterations:
            logger.warning("Max iterations (%d) reached. Halting.", self.state.max_iterations)
            self.state.status = StepStatus.HALTED
            self._persist_state()
            return self.state.status

        iteration = self.state.current_iteration + 1
        logger.info("========== BEGIN ITERATION %d/%d ==========", iteration, self.state.max_iterations)

        # 1. THOUGHT PHASE
        self.state.status = StepStatus.THINKING
        thought = thought_fn(self.state, self.ledger)
        ThinkingRules.enforce_pre_action_rule(thought)

        step = CycleStep(iteration=iteration, status=StepStatus.THINKING, thought=thought)
        self.state.steps.append(step)
        self._persist_state()

        # 2. ACTION PHASE
        step.status = StepStatus.ACTING
        self.state.status = StepStatus.ACTING

        action_sig = self.ledger._compute_signature(thought.proposed_action, {})
        ThinkingRules.enforce_anti_loop_rule(self.ledger, action_sig)

        action_result = action_executor(thought)
        step.action = action_result
        self._persist_state()

        # 3. VERIFICATION PHASE
        step.status = StepStatus.VERIFYING
        self.state.status = StepStatus.VERIFYING

        verification_result = verifier_fn(thought, action_result)
        step.verification = verification_result

        # Determine outcome
        if verification_result.passed:
            logger.info("[ITERATION-%d] [PASS] Verification confirmed: %s", iteration, verification_result.diagnostic_message)
            step.status = StepStatus.PASS
            self.state.status = StepStatus.PASS
        else:
            logger.warning("[ITERATION-%d] [FAIL] Verification failed: %s", iteration, verification_result.diagnostic_message)
            step.status = StepStatus.FAIL
            self.state.status = StepStatus.FAIL

            # Register failure in ledger
            self.ledger.record_failure(
                iteration=iteration,
                action_name=action_result.action_name,
                payload=action_result.payload,
                error_msg=verification_result.diagnostic_message,
                hypothesis=f"Action '{thought.proposed_action}' failed to satisfy: {thought.verification_criterion}",
            )

        self.state.current_iteration = iteration
        self._persist_state()
        return self.state.status

    def run_until_complete(
        self,
        thought_fn: Callable[[ForgeState, SelfCorrectionLedger], ThoughtRecord],
        action_executor: Callable[[ThoughtRecord], ActionResult],
        verifier_fn: Callable[[ThoughtRecord, ActionResult], VerificationRecord],
    ) -> StepStatus:
        while self.state.status not in (StepStatus.PASS, StepStatus.HALTED):
            status = self.step(thought_fn, action_executor, verifier_fn)
            if status == StepStatus.PASS:
                logger.info("Objective reached successfully in iteration %d.", self.state.current_iteration)
                break
            if status == StepStatus.FAIL and self.state.current_iteration >= self.state.max_iterations:
                logger.error("Exhausted maximum retry budget. Engine halting.")
                self.state.status = StepStatus.HALTED
                self._persist_state()
                break
        return self.state.status


# ---------------------------------------------------------------------------
# Self-Test Verification Hook
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import shutil
    import tempfile

    test_dir = Path(tempfile.mkdtemp(prefix="omega_test_"))
    try:
        logger.info("Executing self-test suite in %s", test_dir)
        engine = OmegaForgeEngine(
            session_id="test_run_01",
            objective="Verify local environment Python version >= 3.10",
            workspace_dir=test_dir,
            max_iterations=3,
        )

        def mock_thought(state: ForgeState, ledger: SelfCorrectionLedger) -> ThoughtRecord:
            return ThoughtRecord(
                thought_id=f"T_{state.current_iteration + 1}",
                rationale="System requires verification of the active Python executable version.",
                proposed_action="python3 --version",
                verification_criterion="Exit code must be 0 and stdout must contain 'Python 3.'",
            )

        def mock_action(thought: ThoughtRecord) -> ActionResult:
            return engine.dispatcher.execute_command(thought.proposed_action, cwd=test_dir)

        def mock_verify(thought: ThoughtRecord, action: ActionResult) -> VerificationRecord:
            passed = action.exit_code == 0 and "Python 3." in action.output
            return VerificationRecord(
                passed=passed,
                diagnostic_message="Python version check successful." if passed else action.error or "Unknown failure",
                observed_state={"stdout": action.output, "exit_code": action.exit_code},
            )

        final_status = engine.run_until_complete(mock_thought, mock_action, mock_verify)
        assert final_status == StepStatus.PASS, f"Self-test failed with status {final_status}"
        logger.info("Omega Forge self-test verified: PASS.")
    finally:
        shutil.rmtree(test_dir)
