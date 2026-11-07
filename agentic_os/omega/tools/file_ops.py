"""
agentic_os.omega.tools.file_ops
Guarded file I/O operations strictly confined to authorized workspace boundaries.
Prevents traversal escapes, enforces size constraints, and provides atomic writes.
"""

from __future__ import annotations

import logging
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, List, Optional

from agentic_os.omega.tools.base import BaseTool, ToolResult

logger = logging.getLogger("agentic_os.omega.tools.file_ops")


class GuardedFileOps(BaseTool):
    """
    Filesystem operations tool confined to an absolute workspace boundary.
    Rejects any relative or absolute path traversal attempting to escape the root.
    """

    MAX_READ_BYTES: int = 10 * 1024 * 1024  # 10MB safety bound

    def __init__(self, workspace_root: Path) -> None:
        super().__init__(
            name="guarded_file_ops",
            description="Safe sandboxed filesystem access for file reads, atomic writes, and listings.",
            version="1.0.0",
        )
        self.workspace_root = workspace_root.resolve()
        if not self.workspace_root.exists():
            self.workspace_root.mkdir(parents=True, exist_ok=True)

    def _resolve_and_verify(self, target_path: str | Path) -> Path:
        """Resolve a path and verify it remains strictly within workspace bounds."""
        target = Path(target_path)
        if not target.is_absolute():
            resolved = (self.workspace_root / target).resolve()
        else:
            resolved = target.resolve()

        try:
            resolved.relative_to(self.workspace_root)
        except ValueError as exc:
            raise PermissionError(
                f"Security violation: path '{target_path}' resolves to '{resolved}', "
                f"which escapes workspace root '{self.workspace_root}'."
            ) from exc

        return resolved

    def read_text(self, file_path: str | Path, encoding: str = "utf-8") -> ToolResult:
        """Safely read text file contents up to MAX_READ_BYTES."""
        try:
            resolved = self._resolve_and_verify(file_path)
            if not resolved.exists():
                return ToolResult.fail(f"File not found: {file_path}", path=str(resolved))
            if not resolved.is_file():
                return ToolResult.fail(f"Path is not a regular file: {file_path}", path=str(resolved))

            size = resolved.stat().st_size
            if size > self.MAX_READ_BYTES:
                return ToolResult.fail(
                    f"File exceeds maximum read limit ({size} bytes > {self.MAX_READ_BYTES} bytes)",
                    size=size,
                )

            content = resolved.read_text(encoding=encoding)
            return ToolResult.ok(data=content, path=str(resolved), size=size)
        except PermissionError as p_err:
            return ToolResult.fail(str(p_err), code="TRAVERSAL_DETECTED")
        except Exception as exc:
            return ToolResult.fail(f"Read error: {exc}", code="READ_ERROR")

    def write_text(
        self,
        file_path: str | Path,
        content: str,
        encoding: str = "utf-8",
        make_dirs: bool = True,
    ) -> ToolResult:
        """
        Atomically write text contents to a destination file.
        Uses a sibling temporary file replaced via atomic move to guarantee no partial writes.
        """
        try:
            resolved = self._resolve_and_verify(file_path)
            parent = resolved.parent

            if not parent.exists():
                if make_dirs:
                    parent.mkdir(parents=True, exist_ok=True)
                else:
                    return ToolResult.fail(f"Parent directory does not exist: {parent}")

            # Atomic write pattern: write to tmp within same dir, then replace
            with tempfile.NamedTemporaryFile(
                mode="w",
                dir=parent,
                delete=False,
                encoding=encoding,
            ) as tmp_file:
                tmp_file.write(content)
                tmp_file.flush()
                os.fsync(tmp_file.fileno())
                temp_path = Path(tmp_file.name)

            temp_path.replace(resolved)
            bytes_written = len(content.encode(encoding))
            return ToolResult.ok(
                data={"path": str(resolved), "bytes_written": bytes_written},
                path=str(resolved),
            )
        except PermissionError as p_err:
            return ToolResult.fail(str(p_err), code="TRAVERSAL_DETECTED")
        except Exception as exc:
            return ToolResult.fail(f"Write error: {exc}", code="WRITE_ERROR")

    def list_dir(self, dir_path: str | Path = ".", recursive: bool = False) -> ToolResult:
        """Enumerate files and directories within an authorized sub-tree."""
        try:
            resolved = self._resolve_and_verify(dir_path)
            if not resolved.exists():
                return ToolResult.fail(f"Directory not found: {dir_path}")
            if not resolved.is_dir():
                return ToolResult.fail(f"Path is not a directory: {dir_path}")

            entries: List[dict] = []
            if recursive:
                for item in resolved.rglob("*"):
                    entries.append({
                        "path": str(item.relative_to(self.workspace_root)),
                        "is_dir": item.is_dir(),
                        "size": item.stat().st_size if item.is_file() else None,
                    })
            else:
                for item in resolved.iterdir():
                    entries.append({
                        "path": str(item.relative_to(self.workspace_root)),
                        "is_dir": item.is_dir(),
                        "size": item.stat().st_size if item.is_file() else None,
                    })

            return ToolResult.ok(data=entries, count=len(entries))
        except PermissionError as p_err:
            return ToolResult.fail(str(p_err), code="TRAVERSAL_DETECTED")
        except Exception as exc:
            return ToolResult.fail(f"Listing error: {exc}", code="LIST_ERROR")

    def execute(self, action: str, **kwargs: Any) -> ToolResult:
        """Dynamic dispatch implementation conforming to BaseTool."""
        if action == "read":
            return self.read_text(
                file_path=kwargs["file_path"],
                encoding=kwargs.get("encoding", "utf-8"),
            )
        elif action == "write":
            return self.write_text(
                file_path=kwargs["file_path"],
                content=kwargs["content"],
                encoding=kwargs.get("encoding", "utf-8"),
                make_dirs=kwargs.get("make_dirs", True),
            )
        elif action == "list":
            return self.list_dir(
                dir_path=kwargs.get("dir_path", "."),
                recursive=kwargs.get("recursive", False),
            )
        return ToolResult.fail(f"Unsupported action: {action}")
