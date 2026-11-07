# Copyright © 2026 2351485 ALBERTA INC.
# SPDX-License-Identifier: AGPL-3.0-only
"""Ledger summary generation and verification telemetry for Omega.

Aggregates execution logs, status transitions, and thought records from
the raw ledger entry dictionaries into human-readable and structured metrics.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional


def summarize_ledger_entries(entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compile structured metrics from a list of raw ledger entry dictionaries.

    Expected entry schema variants:
      - Thought entries: {"event_type": "thought", "data": {...ThoughtRecord fields...}, "timestamp": float}
      - Action/Execution entries: {"event_type": "action", "data": {"action": ..., "status": ...}, "timestamp": float}
      - Verification entries: {"event_type": "verification", "data": {"passed": bool, "details": ...}, "timestamp": float}
      - Generic entries: {"type": ..., "status": ..., "timestamp": ...}
    """
    total_entries = len(entries)
    thoughts: List[Dict[str, Any]] = []
    actions: List[Dict[str, Any]] = []
    verifications: List[Dict[str, Any]] = []

    passed_verifications = 0
    failed_verifications = 0

    earliest_ts: Optional[float] = None
    latest_ts: Optional[float] = None

    for entry in entries:
        ts = entry.get("timestamp")
        if isinstance(ts, (int, float)):
            if earliest_ts is None or ts < earliest_ts:
                earliest_ts = ts
            if latest_ts is None or ts > latest_ts:
                latest_ts = ts

        event_type = entry.get("event_type") or entry.get("type") or ""
        payload = entry.get("data") if isinstance(entry.get("data"), dict) else entry

        if "thought_id" in payload or event_type == "thought":
            thoughts.append(payload)

        if "action" in payload or event_type == "action":
            actions.append(payload)

        if "verification" in event_type or "passed" in payload:
            verifications.append(payload)
            if payload.get("passed") is True or payload.get("status") == "success":
                passed_verifications += 1
            elif payload.get("passed") is False or payload.get("status") == "failed":
                failed_verifications += 1

    duration = 0.0
    if earliest_ts is not None and latest_ts is not None:
        duration = max(0.0, latest_ts - earliest_ts)

    return {
        "total_entries": total_entries,
        "total_thoughts": len(thoughts),
        "total_actions": len(actions),
        "total_verifications": len(verifications),
        "verifications_passed": passed_verifications,
        "verifications_failed": failed_verifications,
        "verification_success_rate": (
            (passed_verifications / len(verifications)) if verifications else 1.0
        ),
        "start_time": earliest_ts,
        "end_time": latest_ts,
        "duration_seconds": duration,
        "latest_thought": thoughts[-1] if thoughts else None,
        "latest_action": actions[-1] if actions else None,
    }


def format_ledger_markdown(summary: Dict[str, Any]) -> str:
    """Format a summary dictionary into a clean markdown report."""
    duration_str = f"{summary.get('duration_seconds', 0.0):.2f}s"
    rate_str = f"{(summary.get('verification_success_rate', 0.0) * 100):.1f}%"

    md = [
        "# Omega Ledger Execution Summary",
        "",
        "## Core Metrics",
        f"- **Total Ledger Entries:** {summary.get('total_entries', 0)}",
        f"- **Thoughts Generated:** {summary.get('total_thoughts', 0)}",
        f"- **Actions Logged:** {summary.get('total_actions', 0)}",
        f"- **Verifications:** {summary.get('total_verifications', 0)} "
        f"({summary.get('verifications_passed', 0)} passed, "
        f"{summary.get('verifications_failed', 0)} failed, Success Rate: {rate_str})",
        f"- **Execution Duration:** {duration_str}",
        "",
    ]

    latest_thought = summary.get("latest_thought")
    if latest_thought:
        md.append("## Latest Thought")
        md.append(f"- **ID:** `{latest_thought.get('thought_id', 'N/A')}`")
        md.append(f"- **Rationale:** {latest_thought.get('rationale', 'N/A')}")
        md.append(f"- **Proposed Action:** `{latest_thought.get('proposed_action', 'N/A')}`")
        md.append(f"- **Criterion:** {latest_thought.get('verification_criterion', 'N/A')}")
        md.append("")

    return "\n".join(md)
