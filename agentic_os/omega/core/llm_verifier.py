# Copyright © 2026 2351485 ALBERTA INC.
# SPDX-License-Identifier: AGPL-3.0-only

"""LLM-backed verifier (the Critic) for the Omega Forge Engine.

Evaluates an executed action against the thought record's verification
criterion using Gemini over standard library urllib.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any, Callable

from agentic_os.omega.core.state import ActionResult, ThoughtRecord, VerificationRecord


class VerifierError(RuntimeError):
    """Raised when the LLM verifier cannot obtain or parse a valid verdict."""


def create_verifier_provider(
    api_key: str | None = None,
    model: str = "gemini-flash-latest",
    timeout: float = 30.0,
    base_url: str = "https://generativelanguage.googleapis.com/v1beta/models",
) -> Callable[[ThoughtRecord, ActionResult], VerificationRecord]:
    """Creates a callable verifier provider conforming to OmegaForgeEngine's verifier_fn.

    Args:
        api_key: Gemini API key. Defaults to GEMINI_API_KEY environment variable.
        model: Target Gemini model identifier.
        timeout: Network timeout in seconds for urllib requests.
        base_url: Base endpoint URL for Gemini generateContent API.

    Returns:
        Callable[[ThoughtRecord, ActionResult], VerificationRecord]
    """
    resolved_api_key = api_key or os.environ.get("GEMINI_API_KEY")
    if not resolved_api_key:
        raise ValueError(
            "Gemini API key must be provided or set in the GEMINI_API_KEY environment variable."
        )

    endpoint_url = f"{base_url.rstrip('/')}/{model}:generateContent?key={resolved_api_key}"

    system_instruction = (
        "You are an impartial, strict verification critic for an autonomous agent engine.\n"
        "Your task is to determine whether an executed action fulfilled the thought's verification criterion.\n"
        "Evaluate the provided criterion, action name, exit code, output, and error.\n\n"
        "You MUST respond ONLY with valid, raw JSON matching this schema:\n"
        '{"passed": <true|false>, "diagnostic": "<string explaining reasoning>"}\n'
        "Do not include markdown fences, comments, or any extra text."
    )

    def verifier(thought: ThoughtRecord, action: ActionResult) -> VerificationRecord:
        payload_data = {
            "thought_id": thought.thought_id,
            "verification_criterion": thought.verification_criterion,
            "action_name": action.action_name,
            "exit_code": action.exit_code,
            "output": action.output,
            "error": action.error,
        }

        user_prompt = (
            f"Criterion to verify:\n{thought.verification_criterion}\n\n"
            f"Executed Action: {action.action_name}\n"
            f"Exit Code: {action.exit_code}\n"
            f"Output:\n{action.output}\n"
            f"Error:\n{action.error}\n\n"
            "Evaluate strictly and return JSON with keys 'passed' and 'diagnostic'."
        )

        request_body = {
            "systemInstruction": {
                "parts": [{"text": system_instruction}]
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": user_prompt}]
                }
            ],
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.0,
            },
        }

        body_bytes = json.dumps(request_body).encode("utf-8")
        req = urllib.request.Request(
            endpoint_url,
            data=body_bytes,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                status_code = response.getcode()
                raw_response = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            err_msg = exc.read().decode("utf-8", errors="replace") if exc.fp else str(exc)
            raise VerifierError(
                f"Gemini API HTTP {exc.code} error during verification: {err_msg}"
            ) from exc
        except urllib.error.URLError as exc:
            raise VerifierError(
                f"Gemini API network failure during verification: {exc.reason}"
            ) from exc
        except Exception as exc:
            raise VerifierError(
                f"Unexpected error communicating with Gemini verifier: {exc}"
            ) from exc

        if status_code != 200:
            raise VerifierError(f"Gemini API returned unexpected HTTP status {status_code}: {raw_response}")

        try:
            parsed_api = json.loads(raw_response)
        except json.JSONDecodeError as exc:
            raise VerifierError(
                f"Gemini API returned non-JSON response payload: {raw_response}"
            ) from exc

        candidates = parsed_api.get("candidates", [])
        if not candidates:
            raise VerifierError(
                f"Gemini API returned no candidates. Full response: {parsed_api}"
            )

        candidate = candidates[0]
        content_parts = candidate.get("content", {}).get("parts", [])
        if not content_parts or "text" not in content_parts[0]:
            raise VerifierError(
                f"Gemini candidate has no text part. Full candidate: {candidate}"
            )

        verdict_raw = content_parts[0]["text"].strip()

        # Handle models wrapping JSON in code blocks despite generationConfig
        if verdict_raw.startswith("```"):
            lines = verdict_raw.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            verdict_raw = "\n".join(lines).strip()

        try:
            verdict = json.loads(verdict_raw)
        except json.JSONDecodeError as exc:
            raise VerifierError(
                f"Gemini verifier output could not be parsed as JSON: {verdict_raw!r}"
            ) from exc

        if not isinstance(verdict, dict):
            raise VerifierError(
                f"Gemini verifier output must be a JSON object, got {type(verdict).__name__}: {verdict!r}"
            )

        if "passed" not in verdict or "diagnostic" not in verdict:
            raise VerifierError(
                f"Gemini verifier output missing required keys 'passed' or 'diagnostic': {verdict!r}"
            )

        passed_val = verdict["passed"]
        if not isinstance(passed_val, bool):
            raise VerifierError(
                f"Gemini verifier key 'passed' must be a boolean, got {type(passed_val).__name__}: {passed_val!r}"
            )

        diagnostic_val = verdict["diagnostic"]
        if not isinstance(diagnostic_val, str):
            raise VerifierError(
                f"Gemini verifier key 'diagnostic' must be a string, got {type(diagnostic_val).__name__}: {diagnostic_val!r}"
            )

        observed_state: dict[str, Any] = {
            "model": model,
            "action_name": action.action_name,
            "exit_code": action.exit_code,
            "criterion": thought.verification_criterion,
            "diagnostic": diagnostic_val,
            "input_summary": payload_data,
        }

        return VerificationRecord(
            passed=passed_val,
            diagnostic_message=diagnostic_val,
            observed_state=observed_state,
        )

    return verifier
