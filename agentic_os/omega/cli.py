# Copyright © 2026 2351485 ALBERTA INC.
# SPDX-License-Identifier: AGPL-3.0-only
"""Command line interface for Omegacode."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from agentic_os.omega.core.engine import OmegaForgeEngine
from agentic_os.omega.core.state import StepStatus
from agentic_os.omega.core.ledger import SelfCorrectionLedger
from agentic_os.omega.core.ledger_summary import summarize_ledger_entries, format_ledger_markdown
from agentic_os.omega.core.memory import SemanticMemory
from agentic_os.omega.core.llm_provider import create_thought_provider
from agentic_os.omega.core.llm_verifier import create_verifier_provider


def _resolve_workspace(args) -> Path:
    return Path(getattr(args, "workspace", ".") or ".").expanduser().resolve()


def _format_entry(entry) -> str:
    formatted = f"{entry['key']} = {entry['value']}"
    if entry.get("tags"):
        formatted += f" [{', '.join(entry['tags'])}]"
    return formatted


def cmd_run(args) -> int:
    if not os.environ.get("GEMINI_API_KEY"):
        print(
            "Error: GEMINI_API_KEY is not set. Set the GEMINI_API_KEY environment variable to run the engine.",
            file=sys.stderr,
        )
        return 2

    workspace = _resolve_workspace(args)
    if args.model:
        thought_provider = create_thought_provider(model=args.model)
        verifier = create_verifier_provider(model=args.model)
    else:
        thought_provider = create_thought_provider()
        verifier = create_verifier_provider()

    engine = OmegaForgeEngine(
        session_id="cli-run",
        objective=args.objective,
        workspace_dir=workspace,
        max_iterations=args.max_iterations,
    )

    def _executor(thought):
        return engine.dispatcher.execute_command(thought.proposed_action, cwd=workspace)

    status = engine.run_until_complete(thought_provider, _executor, verifier)
    print(f"Status: {status.value}")
    print(f"Iterations: {engine.state.current_iteration}")
    return 0 if status == StepStatus.PASS else 1


def cmd_ledger(args) -> int:
    workspace = _resolve_workspace(args)
    ledger = SelfCorrectionLedger(ledger_file=workspace / ".omega_ledger.json")
    print(format_ledger_markdown(summarize_ledger_entries(ledger.entries)))
    return 0


def cmd_memory_list(args) -> int:
    mem = SemanticMemory(_resolve_workspace(args) / "semantic_memory.json")
    entries = mem.all()
    if not entries:
        print("No entries.")
    else:
        for entry in entries:
            print(_format_entry(entry))
    return 0


def cmd_memory_get(args) -> int:
    mem = SemanticMemory(_resolve_workspace(args) / "semantic_memory.json")
    entry = mem.get(args.key)
    if entry is None:
        print("not found")
        return 1
    print(_format_entry(entry))
    return 0


def cmd_memory_put(args) -> int:
    mem = SemanticMemory(_resolve_workspace(args) / "semantic_memory.json")
    tags = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else None
    mem.put(args.key, args.value, tags=tags)
    print(f"Stored: {args.key}")
    return 0


def cmd_memory_search(args) -> int:
    mem = SemanticMemory(_resolve_workspace(args) / "semantic_memory.json")
    results = mem.search(args.query)
    if not results:
        print("No results.")
    else:
        for entry in results:
            print(_format_entry(entry))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="omega",
        description="Omegacode command line interface",
    )
    parser.add_argument("--workspace", default=".")
    sub = parser.add_subparsers(dest="command", required=True)

    run_parser = sub.add_parser("run")
    run_parser.add_argument("--objective", required=True)
    run_parser.add_argument("--workspace", default=argparse.SUPPRESS)
    run_parser.add_argument("--max-iterations", type=int, default=10)
    run_parser.add_argument("--model", default=None)
    run_parser.set_defaults(func=cmd_run)

    ledger_parser = sub.add_parser("ledger")
    ledger_parser.add_argument("--workspace", default=argparse.SUPPRESS)
    ledger_parser.set_defaults(func=cmd_ledger)

    memory_parser = sub.add_parser("memory")
    memory_parser.add_argument("--workspace", default=argparse.SUPPRESS)
    mem_sub = memory_parser.add_subparsers(dest="memory_command", required=True)

    list_parser = mem_sub.add_parser("list")
    list_parser.add_argument("--workspace", default=argparse.SUPPRESS)
    list_parser.set_defaults(func=cmd_memory_list)

    get_parser = mem_sub.add_parser("get")
    get_parser.add_argument("key")
    get_parser.add_argument("--workspace", default=argparse.SUPPRESS)
    get_parser.set_defaults(func=cmd_memory_get)

    put_parser = mem_sub.add_parser("put")
    put_parser.add_argument("key")
    put_parser.add_argument("value")
    put_parser.add_argument("--tags", default=None)
    put_parser.add_argument("--workspace", default=argparse.SUPPRESS)
    put_parser.set_defaults(func=cmd_memory_put)

    search_parser = mem_sub.add_parser("search")
    search_parser.add_argument("query")
    search_parser.add_argument("--workspace", default=argparse.SUPPRESS)
    search_parser.set_defaults(func=cmd_memory_search)

    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
