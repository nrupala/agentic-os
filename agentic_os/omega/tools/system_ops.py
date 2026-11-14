# Copyright © 2026 2351485 ALBERTA INC.
# SPDX-License-Identifier: AGPL-3.0-only
"""System and filesystem tools confined to a workspace."""

import glob
import hashlib
import os
from pathlib import Path
import shutil
import tarfile
from typing import Any, Optional
import zipfile

from agentic_os.omega.tools.base import BaseTool, ToolResult


def _confined(root: Path, path: str) -> Optional[Path]:
    """Resolve a target path and verify it does not escape the root workspace."""
    target = (root / path).resolve()
    if target != root and root not in target.parents:
        return None
    return target


class FileHashTool(BaseTool):
    """Calculate the cryptographic hash of a file within the workspace."""

    def __init__(self) -> None:
        super().__init__(
            name="file_hash",
            description="Compute hex digest of a file using sha256, sha1, or md5.",
            version="1.0.0",
        )

    def execute(self, path: str = "", workspace: str = "", algorithm: str = "sha256", **kwargs: Any) -> ToolResult:
        if not workspace:
            return ToolResult.fail("workspace is required")
        if not path:
            return ToolResult.fail("path is required")
        if algorithm not in ("sha256", "sha1", "md5"):
            return ToolResult.fail(f"unsupported algorithm: {algorithm}")

        root = Path(workspace).resolve()
        target = _confined(root, path)
        if target is None:
            return ToolResult.fail("path escapes workspace")
        if not target.exists() or not target.is_file():
            return ToolResult.fail("target does not exist or is not a file")

        try:
            hasher = hashlib.new(algorithm)
            with open(target, "rb") as f:
                while chunk := f.read(65536):
                    hasher.update(chunk)
            return ToolResult.ok(hasher.hexdigest())
        except Exception as exc:
            return ToolResult.fail(str(exc))


class DirTreeTool(BaseTool):
    """List directory tree structure confined to workspace up to a maximum depth."""

    def __init__(self) -> None:
        super().__init__(
            name="dir_tree",
            description="List directory tree structure up to a maximum recursion depth.",
            version="1.0.0",
        )

    def execute(self, workspace: str = "", path: str = ".", max_depth: int = 3, **kwargs: Any) -> ToolResult:
        if not workspace:
            return ToolResult.fail("workspace is required")
        if not isinstance(max_depth, int) or max_depth < 0:
            return ToolResult.fail("max_depth must be a non-negative integer")

        root = Path(workspace).resolve()
        target = _confined(root, path)
        if target is None:
            return ToolResult.fail("path escapes workspace")
        if not target.exists():
            return ToolResult.fail("path does not exist")
        if not target.is_dir():
            return ToolResult.fail("path is not a directory")

        entries: list[str] = []

        def _traverse(current_dir: Path, current_depth: int) -> None:
            if current_depth >= max_depth:
                return
            try:
                children = sorted(current_dir.iterdir(), key=lambda p: p.name)
            except OSError:
                return
            for child in children:
                rel = child.relative_to(root).as_posix()
                if child.is_dir():
                    entries.append(f"{rel}/")
                    _traverse(child, current_depth + 1)
                else:
                    entries.append(rel)

        try:
            _traverse(target, 0)
            entries.sort()
            return ToolResult.ok(entries)
        except Exception as exc:
            return ToolResult.fail(str(exc))


class FileInfoTool(BaseTool):
    """Retrieve metadata about a file or directory within the workspace."""

    def __init__(self) -> None:
        super().__init__(
            name="file_info",
            description="Get metadata including existence, type, size, and mtime.",
            version="1.0.0",
        )

    def execute(self, path: str = "", workspace: str = "", **kwargs: Any) -> ToolResult:
        if not workspace:
            return ToolResult.fail("workspace is required")
        if not path:
            return ToolResult.fail("path is required")

        root = Path(workspace).resolve()
        target = _confined(root, path)
        if target is None:
            return ToolResult.fail("path escapes workspace")

        try:
            if not target.exists():
                return ToolResult.ok(
                    {
                        "exists": False,
                        "is_dir": False,
                        "is_file": False,
                        "size": None,
                        "modified": None,
                    }
                )

            stat = target.stat()
            is_dir = target.is_dir()
            is_file = target.is_file()
            size = stat.st_size if is_file else None
            modified = float(stat.st_mtime)

            return ToolResult.ok(
                {
                    "exists": True,
                    "is_dir": is_dir,
                    "is_file": is_file,
                    "size": size,
                    "modified": modified,
                }
            )
        except Exception as exc:
            return ToolResult.fail(str(exc))


class FindFilesTool(BaseTool):
    """Find files and directories matching a glob pattern within the workspace."""

    def __init__(self) -> None:
        super().__init__(
            name="find_files",
            description="Find files and directories matching a glob pattern.",
            version="1.0.0",
        )

    def execute(self, pattern: str = "", workspace: str = "", **kwargs: Any) -> ToolResult:
        if not workspace:
            return ToolResult.fail("workspace is required")
        if not pattern:
            return ToolResult.fail("pattern is required")

        root = Path(workspace).resolve()
        if not root.exists() or not root.is_dir():
            return ToolResult.fail("workspace does not exist or is not a directory")

        try:
            matches: list[str] = []
            for matched_path in root.glob(pattern):
                try:
                    rel = matched_path.relative_to(root).as_posix()
                    matches.append(rel)
                except ValueError:
                    continue
            matches.sort()
            return ToolResult.ok(matches)
        except Exception as exc:
            return ToolResult.fail(str(exc))


class DiskUsageTool(BaseTool):
    """Retrieve disk space statistics for a path within the workspace."""

    def __init__(self) -> None:
        super().__init__(
            name="disk_usage",
            description="Get disk usage statistics including total, used, and free bytes.",
            version="1.0.0",
        )

    def execute(self, workspace: str = "", path: str = ".", **kwargs: Any) -> ToolResult:
        if not workspace:
            return ToolResult.fail("workspace is required")

        root = Path(workspace).resolve()
        target = _confined(root, path)
        if target is None:
            return ToolResult.fail("path escapes workspace")
        if not target.exists():
            return ToolResult.fail("path does not exist")

        try:
            usage = shutil.disk_usage(target)
            return ToolResult.ok(
                {
                    "total": usage.total,
                    "used": usage.used,
                    "free": usage.free,
                }
            )
        except Exception as exc:
            return ToolResult.fail(str(exc))


class EnvGetTool(BaseTool):
    """Get the value of an allowlisted environment variable."""

    def __init__(self) -> None:
        super().__init__(
            name="env_get",
            description="Get the value of an allowlisted environment variable.",
            version="1.0.0",
        )

    def execute(self, name: str = "", **kwargs: Any) -> ToolResult:
        if not isinstance(name, str) or not name:
            return ToolResult.fail("environment variable not allowlisted")
        allowed = {"PATH", "HOME", "USER", "LANG", "TZ", "OSTYPE"}
        if name not in allowed and not name.startswith("OMEGA_"):
            return ToolResult.fail("environment variable not allowlisted")
        return ToolResult.ok(os.environ.get(name))


class ZipCreateTool(BaseTool):
    """Create a ZIP archive of confined workspace files."""

    def __init__(self) -> None:
        super().__init__(
            name="zip_create",
            description="Create a ZIP archive of confined workspace files.",
            version="1.0.0",
        )

    def execute(
        self, archive: str = "", files: list[str] | None = None, workspace: str = "", **kwargs: Any
    ) -> ToolResult:
        if not isinstance(archive, str) or not isinstance(workspace, str) or not isinstance(files, list):
            return ToolResult.fail("invalid argument types")
        try:
            root = Path(workspace).resolve()
            if not root.is_dir():
                return ToolResult.fail("workspace directory does not exist")
            target_archive = _confined(root, archive)
            if target_archive is None:
                return ToolResult.fail("archive path escapes workspace")

            file_pairs: list[tuple[Path, str]] = []
            entries: list[str] = []
            for f in files:
                if not isinstance(f, str):
                    return ToolResult.fail("file entries must be strings")
                cf = _confined(root, f)
                if cf is None:
                    return ToolResult.fail(f"file escapes workspace: {f}")
                if not cf.is_file():
                    return ToolResult.fail(f"file not found: {f}")
                arcname = str(cf.relative_to(root))
                file_pairs.append((cf, arcname))
                entries.append(arcname)

            target_archive.parent.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(target_archive, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
                for cf, arcname in file_pairs:
                    zf.write(cf, arcname=arcname)

            rel_archive = str(target_archive.relative_to(root))
            return ToolResult.ok({"archive": rel_archive, "entries": entries})
        except Exception as e:
            if "target_archive" in locals() and target_archive is not None and target_archive.exists():
                try:
                    target_archive.unlink()
                except Exception:
                    pass
            return ToolResult.fail(str(e))


class ZipListTool(BaseTool):
    """List entries stored in a ZIP archive."""

    def __init__(self) -> None:
        super().__init__(
            name="zip_list",
            description="List entries stored in a ZIP archive.",
            version="1.0.0",
        )

    def execute(self, archive: str = "", workspace: str = "", **kwargs: Any) -> ToolResult:
        if not isinstance(archive, str) or not isinstance(workspace, str):
            return ToolResult.fail("invalid argument types")
        try:
            root = Path(workspace).resolve()
            if not root.is_dir():
                return ToolResult.fail("workspace directory does not exist")
            target = _confined(root, archive)
            if target is None:
                return ToolResult.fail("archive path escapes workspace")
            if not target.is_file() or not zipfile.is_zipfile(target):
                return ToolResult.fail("archive missing or not a valid zip file")
            with zipfile.ZipFile(target, mode="r") as zf:
                return ToolResult.ok(zf.namelist())
        except Exception as e:
            return ToolResult.fail(str(e))


class TarCreateTool(BaseTool):
    """Create an uncompressed TAR archive of confined workspace files."""

    def __init__(self) -> None:
        super().__init__(
            name="tar_create",
            description="Create an uncompressed TAR archive of confined workspace files.",
            version="1.0.0",
        )

    def execute(
        self, archive: str = "", files: list[str] | None = None, workspace: str = "", **kwargs: Any
    ) -> ToolResult:
        if not isinstance(archive, str) or not isinstance(workspace, str) or not isinstance(files, list):
            return ToolResult.fail("invalid argument types")
        try:
            root = Path(workspace).resolve()
            if not root.is_dir():
                return ToolResult.fail("workspace directory does not exist")
            target_archive = _confined(root, archive)
            if target_archive is None:
                return ToolResult.fail("archive path escapes workspace")

            file_pairs: list[tuple[Path, str]] = []
            entries: list[str] = []
            for f in files:
                if not isinstance(f, str):
                    return ToolResult.fail("file entries must be strings")
                cf = _confined(root, f)
                if cf is None:
                    return ToolResult.fail(f"file escapes workspace: {f}")
                if not cf.is_file():
                    return ToolResult.fail(f"file not found: {f}")
                arcname = str(cf.relative_to(root))
                file_pairs.append((cf, arcname))
                entries.append(arcname)

            target_archive.parent.mkdir(parents=True, exist_ok=True)
            with tarfile.open(target_archive, mode="w") as tf:
                for cf, arcname in file_pairs:
                    tf.add(cf, arcname=arcname)

            rel_archive = str(target_archive.relative_to(root))
            return ToolResult.ok({"archive": rel_archive, "entries": entries})
        except Exception as e:
            if "target_archive" in locals() and target_archive is not None and target_archive.exists():
                try:
                    target_archive.unlink()
                except Exception:
                    pass
            return ToolResult.fail(str(e))
