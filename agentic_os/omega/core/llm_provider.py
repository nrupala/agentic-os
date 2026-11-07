# Copyright © 2026 2351485 ALBERTA INC.
# SPDX-License-Identifier: AGPL-3.0-only
"""LLM Thought Provider for OmegaForgeEngine.

Implements the Thought-Action-Verification (TAV) loop provider using the
Gemini REST API via standard library urllib, consuming state and ledger context
and returning structured ThoughtRecord instances.
"""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from typing import Any, Callable, Dict, Optional

from agentic_os.omega.core.ledger import SelfCorrectionLedger
from agentic_os.omega.core.state import ForgeState, ThoughtRecord


SYSTEM_INSTRUCTION = """You are the core cognitive engine of the Omega Agentic OS.
You operate strictly in a Thought-Action-Verification (TAV) cycle.

For every iteration, analyze the overall goal, the current state, and the ledger of past attempts/failures.
Formulate the next step and output strictly valid JSON conforming to this schema:
{
  "thought": "<Detailed rationale analyzing current state, previous failures, and next step>",
  "action": {
    "type": "<Action category or tool name>",
    "content": "<The concrete proposed action command or payload as a string>"
  },
  "verification_plan": "<Explicit falsifiable criterion to verify whether this action succeeded>"
}

Rules:
1. Return ONLY the JSON object. Do not enclose in markdown code fences or add commentary.
2. The 'thought', 'action', and 'verification_plan' keys are required.
3. 'action' must contain a 'content' string describing the proposed action.
"""


def _clean_json_response(raw_text: str) -> str:
    """Strip markdown code fence blocks if present."""
    text = raw_text.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if match:
        return match.group(1).strip()
    return text


def parse_tav_json(raw_text: str, iteration: int) -> ThoughtRecord:
    """Parse TAV JSON response into a ThoughtRecord.

    Maps:
      - thought -> rationale
      - action.content -> proposed_action (string)
      - verification_plan -> verification_criterion

    Raises ValueError on malformed or missing fields.
    """
    cleaned = _clean_json_response(raw_text)
    try:
        data = json.loads(cleaned)
    except Exception as exc:
        raise ValueError(
            f"Malformed TAV response: unable to decode JSON: {exc}\nRaw content:\n{raw_text}"
        ) from exc

    if not isinstance(data, dict):
        raise ValueError(
            f"Malformed TAV response: expected top-level JSON object, got {type(data).__name__}"
        )

    if "thought" not in data or not isinstance(data["thought"], str):
        raise ValueError("Malformed TAV response: missing or non-string 'thought' field")

    if "action" not in data:
        raise ValueError("Malformed TAV response: missing 'action' field")

    raw_action = data["action"]
    if isinstance(raw_action, dict):
        if "content" not in raw_action:
            raise ValueError(
                "Malformed TAV response: 'action' object must contain a 'content' field"
            )
        proposed_action = str(raw_action["content"])
    elif isinstance(raw_action, str):
        proposed_action = raw_action
    else:
        raise ValueError(
            f"Malformed TAV response: invalid 'action' format: {type(raw_action).__name__}"
        )

    if "verification_plan" not in data or not isinstance(data["verification_plan"], str):
        raise ValueError(
            "Malformed TAV response: missing or non-string 'verification_plan' field"
        )

    return ThoughtRecord(
        thought_id=f"T-{iteration + 1}",
        rationale=data["thought"].strip(),
        proposed_action=proposed_action.strip(),
        verification_criterion=data["verification_plan"].strip(),
    )


def _build_prompt(state: ForgeState, ledger: SelfCorrectionLedger) -> str:
    """Construct prompt context from current state and self-correction ledger."""
    prompt_lines = [
        f"Goal: {getattr(state, 'goal', 'Execute assigned objective')}",
        f"Current Iteration: {getattr(state, 'iteration', 0)}",
        f"State Status: {getattr(state, 'status', 'UNKNOWN')}",
    ]

    context = getattr(state, "context", None)
    if context:
        prompt_lines.append(f"State Context: {json.dumps(context, default=str)}")

    # Incorporate ledger history if available
    entries = getattr(ledger, "entries", None)
    if entries:
        prompt_lines.append(f"\nLedger History ({len(entries)} records):")
        for idx, entry in enumerate(entries[-5:], 1):  # Include up to last 5 entries
            prompt_lines.append(f"[{idx}] {entry}")
    else:
        summary_method = getattr(ledger, "to_summary", None)
        if callable(summary_method):
            prompt_lines.append(f"\nLedger Summary:\n{summary_method()}")

    prompt_lines.append("\nGenerate the next TAV cycle step in valid JSON format.")
    return "\n".join(prompt_lines)


def create_thought_provider(
    api_key: Optional[str] = None,
    model: str = "gemini-1.5-flash",
    timeout: float = 30.0,
    base_url: str = "https://generativelanguage.googleapis.com/v1beta",
) -> Callable[[ForgeState, SelfCorrectionLedger], ThoughtRecord]:
    """Factory returning a thought provider callable compatible with OmegaForgeEngine.

    The callable signature is:
        (state: ForgeState, ledger: SelfCorrectionLedger) -> ThoughtRecord
    """
    resolved_api_key = api_key or os.environ.get("GEMINI_API_KEY")
    if not resolved_api_key:
        raise ValueError(
            "GEMINI_API_KEY is not set. Provide api_key argument or set the environment variable."
        )

    url = f"{base_url}/models/{model}:generateContent?key={resolved_api_key}"

    def thought_provider(state: ForgeState, ledger: SelfCorrectionLedger) -> ThoughtRecord:
        user_prompt = _build_prompt(state, ledger)

        payload: Dict[str, Any] = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": user_prompt}],
                }
            ],
            "systemInstruction": {
                "parts": [{"text": SYSTEM_INSTRUCTION}],
            },
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.2,
            },
        }

        req_data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            url=url,
            data=req_data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                status_code = response.getcode()
                raw_body = response.read().decode("utf-8")
                if status_code != 200:
                    raise ValueError(
                        f"Gemini API returned unexpected status {status_code}: {raw_body}"
                    )
        except urllib.error.HTTPError as http_err:
            err_body = http_err.read().decode("utf-8", errors="replace")
            raise ValueError(
                f"Gemini API HTTP {http_err.code} error: {err_body}"
            ) from http_err
        except urllib.error.URLError as url_err:
            raise ConnectionError(
                f"Failed to connect to Gemini API: {url_err.reason}"
            ) from url_err

        try:
            parsed_response = json.loads(raw_body)
            candidates = parsed_response.get("candidates", [])
            if not candidates:
                raise ValueError(
                    f"Gemini API response contained no candidates: {raw_body}"
                )
            first_candidate = candidates[0]
            parts = first_candidate.get("content", {}).get("parts", [])
            if not parts or "text" not in parts[0]:
                raise ValueError(
                    f"Gemini API response missing content parts: {raw_body}"
                )
            generated_text = parts[0]["text"]
        except (KeyError, IndexError, json.JSONDecodeError) as parse_err:
            raise ValueError(
                f"Failed to extract candidate content from Gemini response: {parse_err}\nBody: {raw_body}"
            ) from parse_err

        current_iteration = getattr(state, "iteration", 0)
        return parse_tav_json(generated_text, iteration=current_iteration)

    return thought_provider
