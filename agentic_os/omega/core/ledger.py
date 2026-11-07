# Copyright © 2026 2351485 ALBERTA INC.
# SPDX-License-Identifier: AGPL-3.0-only
# agentic_os/omega/core/ledger.py
"""Self-correction ledger for OMEGA-CODE, extracted verbatim from omega_forge.py (Deliverable 3A)."""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional


class SelfCorrectionLedger:
    def __init__(self, ledger_file: Optional[Path] = None):
        self.ledger_file = ledger_file
        self.entries: List[Dict[str, Any]] = []
        if self.ledger_file and self.ledger_file.exists():
            self._load()

    def record_failure(
        self,
        iteration: int,
        action_name: str,
        payload: Dict[str, Any],
        error_msg: str,
        hypothesis: str,
    ) -> str:
        signature = self._compute_signature(action_name, payload)
        entry = {
            "iteration": iteration,
            "signature": signature,
            "action_name": action_name,
            "payload": payload,
            "error_msg": error_msg,
            "hypothesis": hypothesis,
            "timestamp": time.time(),
        }
        self.entries.append(entry)
        self._flush()
        return signature

    def get_action_failure_count(self, signature: str) -> int:
        return sum(1 for e in self.entries if e["signature"] == signature)

    def _compute_signature(self, action_name: str, payload: Dict[str, Any]) -> str:
        serialized = json.dumps({"action": action_name, "payload": payload}, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:12]

    def _flush(self) -> None:
        if self.ledger_file:
            self.ledger_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.ledger_file, "w", encoding="utf-8") as f:
                json.dump(self.entries, f, indent=2)

    def _load(self) -> None:
        if self.ledger_file and self.ledger_file.exists():
            with open(self.ledger_file, "r", encoding="utf-8") as f:
                self.entries = json.load(f)
