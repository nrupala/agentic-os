# Copyright © 2026 2351485 ALBERTA INC.
# SPDX-License-Identifier: AGPL-3.0-only

"""
agentic_os/omega/core/memory.py

Production-grade 3-tier memory engine for Omega Agentic OS.
Provides:
  1. SemanticMemory: Persistent, JSON-backed, process-durable store with
     atomic writes, multi-tag indexing, and resilient query capabilities.
  2. MemoryContextAssembler: Deterministic, bounded context assembler enforcing
     strict truncation hierarchy (Objective -> Ledger Summary -> Semantic Entries)
     to guarantee prompts remain within explicit model character ceilings.
"""

from __future__ import annotations

import json
import logging
import os
import tempfile
import threading
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Union

logger = logging.getLogger("agentic_os.omega.core.memory")

# Optional dynamic import hook for ledger summary
try:
    from agentic_os.omega.core.ledger_summary import get_ledger_summary  # type: ignore
except ImportError:
    try:
        from agentic_os.omega.core.ledger import ledger_summary as get_ledger_summary  # type: ignore
    except ImportError:
        get_ledger_summary = None


class SemanticMemory:
    """
    JSON-file-backed semantic memory tier.
    
    Guarantees cross-process durability through atomic rename operations
    and in-process thread-safety via reentrant locking.
    """

    def __init__(self, storage_path: Union[str, Path] = "omega_memory.json") -> None:
        self.storage_path = Path(storage_path).resolve()
        self._lock = threading.RLock()
        self._ensure_storage()

    def _ensure_storage(self) -> None:
        with self._lock:
            if not self.storage_path.parent.exists():
                self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            if not self.storage_path.exists():
                self._write_raw({})

    def _read_raw(self) -> Dict[str, Dict[str, Any]]:
        with self._lock:
            if not self.storage_path.exists():
                return {}
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if not content:
                        return {}
                    return json.loads(content)
            except (json.JSONDecodeError, OSError) as e:
                logger.error("Failed to read memory file %s: %s", self.storage_path, e)
                return {}

    def _write_raw(self, data: Dict[str, Dict[str, Any]]) -> None:
        """
        Executes an atomic write using a temporary sibling file and os.replace.
        Ensures process crashes do not leave corrupted or partial memory payloads.
        """
        with self._lock:
            parent = self.storage_path.parent
            parent.mkdir(parents=True, exist_ok=True)

            temp_file = None
            try:
                with tempfile.NamedTemporaryFile(
                    mode="w",
                    dir=parent,
                    delete=False,
                    encoding="utf-8",
                    suffix=".tmp"
                ) as tf:
                    json.dump(data, tf, indent=2, ensure_ascii=False)
                    tf.flush()
                    os.fsync(tf.fileno())
                    temp_file = tf.name

                os.replace(temp_file, self.storage_path)
            except Exception as e:
                if temp_file and os.path.exists(temp_file):
                    try:
                        os.unlink(temp_file)
                    except OSError:
                        pass
                logger.error("Atomic write failed for %s: %s", self.storage_path, e)
                raise

    def put(
        self,
        key: str,
        value: Any,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Stores or overwrites a memory record.
        """
        if not key or not isinstance(key, str):
            raise ValueError("Memory key must be a non-empty string.")

        entry = {
            "key": key,
            "value": value,
            "tags": list(set(tags or [])),
            "metadata": metadata or {},
            "updated_at": time.time(),
        }

        with self._lock:
            data = self._read_raw()
            data[key] = entry
            self._write_raw(data)
            return entry

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a record by key. Returns None if not found.
        """
        with self._lock:
            data = self._read_raw()
            return data.get(key)

    def delete(self, key: str) -> bool:
        """
        Deletes a record by key. Returns True if deleted, False if not present.
        """
        with self._lock:
            data = self._read_raw()
            if key in data:
                del data[key]
                self._write_raw(data)
                return True
            return False

    def search(
        self,
        query: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Performs ranked query and tag-based filtering on stored semantic entries.
        Matches against keys, serialized values, and tag sets.
        """
        with self._lock:
            data = self._read_raw()

        results: List[Dict[str, Any]] = []
        required_tags = set(tags) if tags else set()
        q = query.lower().strip() if query else None

        for item in data.values():
            item_tags = set(item.get("tags", []))
            if required_tags and not required_tags.issubset(item_tags):
                continue

            score = 0
            if q:
                key_match = q in item.get("key", "").lower()
                val_str = json.dumps(item.get("value", ""), ensure_ascii=False).lower()
                val_match = q in val_str
                tag_match = any(q in t.lower() for t in item_tags)

                if not (key_match or val_match or tag_match):
                    continue

                if key_match:
                    score += 5
                if tag_match:
                    score += 3
                if val_match:
                    score += 1
            else:
                score = 1

            enriched_item = dict(item)
            enriched_item["_score"] = score
            results.append(enriched_item)

        results.sort(key=lambda x: (x.get("_score", 0), x.get("updated_at", 0)), reverse=True)

        for item in results:
            item.pop("_score", None)

        if limit is not None and limit > 0:
            return results[:limit]
        return results

    def all(self) -> List[Dict[str, Any]]:
        """
        Returns all records in memory sorted by last update time descending.
        """
        with self._lock:
            data = self._read_raw()
            items = list(data.values())
            items.sort(key=lambda x: x.get("updated_at", 0), reverse=True)
            return items


class MemoryContextAssembler:
    """
    Assembles a deterministic, bounded context payload for model inference.
    
    Truncation hierarchy:
      1. Objective: Immutable priority. NEVER truncated, even if exceeding max_chars.
      2. Ledger Summary: Truncated only if Objective + Ledger Summary exceeds max_chars.
      3. Semantic Entries: Progressively appended only within remaining character headroom.
    """

    def __init__(
        self,
        semantic_memory: Optional[SemanticMemory] = None,
        max_chars: int = 8000,
        ledger_summary_provider: Optional[Callable[[], str]] = None,
    ) -> None:
        self.semantic_memory = semantic_memory or SemanticMemory()
        self.max_chars = max_chars
        self.ledger_summary_provider = ledger_summary_provider or get_ledger_summary

    def _resolve_ledger_summary(self) -> str:
        if self.ledger_summary_provider is None:
            return ""
        try:
            summary = self.ledger_summary_provider()
            return str(summary).strip() if summary else ""
        except Exception as e:
            logger.warning("Error invoking ledger summary provider: %s", e)
            return ""

    def assemble(
        self,
        objective: str,
        query: Optional[str] = None,
        tags: Optional[List[str]] = None,
        max_chars: Optional[int] = None,
        semantic_limit: Optional[int] = 10,
    ) -> str:
        """
        Builds the unified context payload enforcing strict character bounds.
        """
        ceiling = max_chars if max_chars is not None else self.max_chars
        objective_text = (objective or "").strip()

        # Section 1: Objective (Non-negotiable, never truncated)
        obj_header = "### OBJECTIVE\n"
        obj_block = f"{obj_header}{objective_text}\n\n"

        remaining_budget = ceiling - len(obj_block)

        # Section 2: Ledger Summary
        ledger_text = self._resolve_ledger_summary()
        ledger_block = ""
        if ledger_text and remaining_budget > 0:
            ledger_header = "### LEDGER SUMMARY\n"
            full_ledger_block = f"{ledger_header}{ledger_text}\n\n"

            if len(full_ledger_block) <= remaining_budget:
                ledger_block = full_ledger_block
                remaining_budget -= len(ledger_block)
            else:
                prefix = f"{ledger_header}"
                marker = "\n... [LEDGER TRUNCATED]\n\n"
                avail = remaining_budget - len(prefix) - len(marker)
                if avail > 0:
                    ledger_block = f"{prefix}{ledger_text[:avail]}{marker}"
                    remaining_budget = 0
                else:
                    ledger_block = ""
                    remaining_budget = 0

        # Section 3: Relevant Semantic Entries
        semantic_block = ""
        if remaining_budget > 0:
            entries = self.semantic_memory.search(query=query or objective_text, tags=tags, limit=semantic_limit)
            if entries:
                sem_header = "### RELEVANT MEMORY\n"
                accumulated_entries = []
                sem_budget = remaining_budget - len(sem_header) - 1

                for item in entries:
                    val_str = json.dumps(item.get("value"), ensure_ascii=False) if not isinstance(item.get("value"), str) else item.get("value")
                    tag_meta = f" [tags: {','.join(item.get('tags', []))}]" if item.get("tags") else ""
                    entry_str = f"- {item.get('key')}{tag_meta}: {val_str}\n"

                    if len(entry_str) <= sem_budget:
                        accumulated_entries.append(entry_str)
                        sem_budget -= len(entry_str)
                    else:
                        break

                if accumulated_entries:
                    semantic_block = f"{sem_header}{''.join(accumulated_entries)}\n"

        context = f"{obj_block}{ledger_block}{semantic_block}".rstrip() + "\n"
        return context


__all__ = ["SemanticMemory", "MemoryContextAssembler"]
