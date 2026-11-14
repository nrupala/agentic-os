# Copyright © 2026 2351485 ALBERTA INC.
# SPDX-License-Identifier: AGPL-3.0-only
"""Dashboard and audit-trail UI for Omegacode.

Provides a read-only view of a workspace, including execution state,
ledger summaries, and semantic memory records.
"""

from __future__ import annotations

import datetime
import html
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from agentic_os.omega.core.ledger_summary import summarize_ledger_entries
from agentic_os.omega.core.memory import SemanticMemory


def _load_json_file(path: Path, default: Any) -> Any:
    """Return parsed JSON from path, or default if missing, unreadable, or invalid."""
    try:
        if not path.is_file():
            return default
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def load_workspace(workspace_dir: str | Path) -> dict[str, Any]:
    """Load and summarize workspace state, ledger, and semantic memory without modifying disk."""
    path = Path(workspace_dir)

    raw_state = _load_json_file(path / ".omega_state.json", None)
    state = raw_state if isinstance(raw_state, dict) else None

    raw_ledger = _load_json_file(path / ".omega_ledger.json", [])
    ledger_entries = raw_ledger if isinstance(raw_ledger, list) else []

    ledger_summary = summarize_ledger_entries(ledger_entries)

    memory_path = path / "semantic_memory.json"
    memory_entries: list[dict[str, Any]] = []
    if memory_path.exists():
        try:
            mem = SemanticMemory(memory_path)
            res = mem.all()
            if isinstance(res, list):
                memory_entries = res
        except Exception:
            memory_entries = []

    return {
        "workspace": str(path),
        "state": state,
        "ledger_entries": ledger_entries,
        "ledger_summary": ledger_summary,
        "memory_entries": memory_entries,
    }


def _esc(value: Any) -> str:
    """HTML-escape a value, converting None to an empty string."""
    if value is None:
        return ""
    return html.escape(str(value), quote=True)


def _fmt_ts(value: Any) -> str:
    """Format a timestamp as UTC ISO-like string if numeric, otherwise HTML-escape."""
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        try:
            dt = datetime.datetime.fromtimestamp(value, tz=datetime.timezone.utc)
            return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
        except Exception:
            return _esc(value)
    return _esc(value)


def _render_session(state) -> str:
    if not state:
        return "<h2>Session</h2><p>No session state found in this workspace.</p>"
    return (
        "<h2>Session</h2>"
        f"<p><strong>Objective:</strong> {_esc(state.get('objective'))}</p>"
        f"<p><strong>Session ID:</strong> {_esc(state.get('session_id'))}</p>"
        f"<p><strong>Status:</strong> {_esc(state.get('status'))}</p>"
        f"<p>Iteration {_esc(state.get('current_iteration'))} of {_esc(state.get('max_iterations'))}</p>"
    )


def _render_summary(summary) -> str:
    s = summary or {}
    rate = s.get("verification_success_rate")
    rate_str = f"{float(rate) * 100:.1f}%" if rate is not None else ""
    return (
        "<h2>Ledger summary</h2>"
        "<table>"
        f"<tr><td>Total entries</td><td>{_esc(s.get('total_entries'))}</td></tr>"
        f"<tr><td>Total verifications</td><td>{_esc(s.get('total_verifications'))}</td></tr>"
        f"<tr><td>Passed</td><td>{_esc(s.get('verifications_passed'))}</td></tr>"
        f"<tr><td>Failed</td><td>{_esc(s.get('verifications_failed'))}</td></tr>"
        f"<tr><td>Success rate</td><td>{_esc(rate_str)}</td></tr>"
        f"<tr><td>Duration seconds</td><td>{_esc(s.get('duration_seconds'))}</td></tr>"
        "</table>"
    )


def _render_steps(state) -> str:
    steps = state.get("steps") if state else None
    if not steps:
        return "<h2>Steps</h2><p>No steps recorded.</p>"

    rows = []
    for step in steps:
        iteration = step.get("iteration")
        iteration = "" if iteration is None else iteration
        status = step.get("status")
        status = "" if status is None else status

        thought = step.get("thought") or {}
        action = step.get("action") or {}
        act = thought.get("proposed_action") or action.get("action_name") or ""

        verification = step.get("verification") or {}
        if verification.get("passed") is True:
            res = "Passed"
        elif verification.get("passed") is False:
            res = "Failed"
        else:
            res = ""

        notes = verification.get("diagnostic_message") or step.get("error_recovery_notes") or ""

        rows.append(
            f"<tr><td>{_esc(iteration)}</td><td>{_esc(status)}</td><td>{_esc(act)}</td><td>{_esc(res)}</td><td>{_esc(notes)}</td></tr>"
        )

    return (
        "<h2>Steps</h2>"
        "<table>"
        "<tr><th>Iteration</th><th>Status</th><th>Action</th><th>Result</th><th>Notes</th></tr>"
        + "".join(rows)
        + "</table>"
    )


def _render_ledger(entries) -> str:
    if not entries:
        return "<h2>Self-correction ledger</h2><p>No ledger entries.</p>"
    header = "<tr><th>Iteration</th><th>Action</th><th>Signature</th><th>Error</th><th>Hypothesis</th><th>Time</th></tr>"
    rows = []
    for entry in entries:
        cells = (
            f"<td>{_esc(entry.get('iteration'))}</td>"
            f"<td>{_esc(entry.get('action_name'))}</td>"
            f"<td>{_esc(entry.get('signature'))}</td>"
            f"<td>{_esc(entry.get('error_msg'))}</td>"
            f"<td>{_esc(entry.get('hypothesis'))}</td>"
            f"<td>{_fmt_ts(entry.get('timestamp'))}</td>"
        )
        rows.append(f"<tr>{cells}</tr>")
    return "<h2>Self-correction ledger</h2><table>" + header + "".join(rows) + "</table>"

def _render_memory(entries) -> str:
    if not entries:
        return "<h2>Semantic memory</h2><p>No memory entries.</p>"
    header = "<tr><th>Key</th><th>Value</th><th>Tags</th><th>Updated</th></tr>"
    rows = []
    for entry in entries:
        val = entry.get('value')
        val_str = val if isinstance(val, str) else json.dumps(val)
        tags = entry.get('tags')
        tags_str = ", ".join(tags) if isinstance(tags, list) else ""
        cells = (
            f"<td>{_esc(entry.get('key'))}</td>"
            f"<td>{_esc(val_str)}</td>"
            f"<td>{_esc(tags_str)}</td>"
            f"<td>{_fmt_ts(entry.get('updated_at'))}</td>"
        )
        rows.append(f"<tr>{cells}</tr>")
    return "<h2>Semantic memory</h2><table>" + header + "".join(rows) + "</table>"


def render_dashboard(data: dict) -> str:
    parts = [
        "<!DOCTYPE html><html><head>"
        '<meta charset="utf-8">'
        "<title>Omegacode Dashboard</title>"
        "<style>body { font-family: sans-serif; margin: 24px; color: #222; } table { border-collapse: collapse; margin: 12px 0; } th, td { border: 1px solid #bbb; padding: 6px 10px; text-align: left; vertical-align: top; } th { background: #eee; }</style>"
        "</head><body>",
        "<h1>Omegacode Dashboard</h1>",
        f"<p>Workspace: {_esc(data.get('workspace', ''))}</p>",
        _render_session(data.get("state")),
        _render_summary(data.get("ledger_summary")),
        _render_steps(data.get("state")),
        _render_ledger(data.get("ledger_entries") or []),
        _render_memory(data.get("memory_entries") or []),
        "</body></html>",
    ]
    return "".join(parts)


import argparse
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


def serve(workspace_dir, host="127.0.0.1", port=8765):
    workspace = Path(workspace_dir)

    class DashboardHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            parsed_path = urllib.parse.urlparse(self.path).path
            if parsed_path == "/":
                body = render_dashboard(load_workspace(workspace)).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            elif parsed_path == "/api/summary":
                payload = load_workspace(workspace)["ledger_summary"]
                body = json.dumps(payload).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            else:
                self.send_response(404)
                self.end_headers()

        def log_message(self, format, *args):
            return

    server = ThreadingHTTPServer((host, port), DashboardHandler)
    print(f"Serving workspace at http://{host}:{port}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return server


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    serve(args.workspace, port=args.port)
