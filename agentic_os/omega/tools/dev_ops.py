# Copyright © 2026 2351485 ALBERTA INC.
# SPDX-License-Identifier: AGPL-3.0-only

"""Developer utilities."""

import ast
import configparser
import difflib
import io
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from agentic_os.omega.tools.base import BaseTool, ToolResult

_SEMVER_REGEX = re.compile(
    r"^(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z.-]+))?(?:\+([0-9A-Za-z.-]+))?$"
)


def _parse_semver(version: str) -> Optional[Dict[str, Any]]:
    """Parse a semantic version string into structured components."""
    if not isinstance(version, str):
        return None
    match = _SEMVER_REGEX.match(version.strip())
    if not match:
        return None
    return {
        "major": int(match.group(1)),
        "minor": int(match.group(2)),
        "patch": int(match.group(3)),
        "prerelease": match.group(4),
        "build": match.group(5),
    }


def _compare_semver(a: Dict[str, Any], b: Dict[str, Any]) -> int:
    """Compare two parsed semantic versions and return -1, 0, or 1."""
    for key in ("major", "minor", "patch"):
        if a[key] < b[key]:
            return -1
        if a[key] > b[key]:
            return 1

    pre_a = a["prerelease"]
    pre_b = b["prerelease"]

    if pre_a is None and pre_b is None:
        return 0
    if pre_a is None and pre_b is not None:
        return 1
    if pre_a is not None and pre_b is None:
        return -1

    parts_a = pre_a.split(".")
    parts_b = pre_b.split(".")

    for part_a, part_b in zip(parts_a, parts_b):
        num_a = part_a.isdigit()
        num_b = part_b.isdigit()

        if num_a and num_b:
            ia, ib = int(part_a), int(part_b)
            if ia < ib:
                return -1
            if ia > ib:
                return 1
        elif num_a and not num_b:
            return -1
        elif not num_a and num_b:
            return 1
        else:
            if part_a < part_b:
                return -1
            if part_a > part_b:
                return 1

    if len(parts_a) < len(parts_b):
        return -1
    if len(parts_a) > len(parts_b):
        return 1
    return 0


class PythonSyntaxCheckTool(BaseTool):
    """Checks Python source code syntax validity."""

    def __init__(self) -> None:
        super().__init__(
            name="python_syntax_check",
            description="Checks Python code syntax and reports validity and line errors.",
            version="1.0.0",
        )

    def execute(self, code: Any = None, **kwargs: Any) -> ToolResult:
        if not isinstance(code, str):
            return ToolResult.fail("Parameter 'code' must be a string.")
        try:
            ast.parse(code)
            return ToolResult.ok({"valid": True, "error": None, "line": None})
        except SyntaxError as exc:
            return ToolResult.ok({"valid": False, "error": str(exc), "line": exc.lineno})
        except Exception as exc:
            return ToolResult.fail(f"Failed to parse code: {exc}")


class DiffTextsTool(BaseTool):
    """Generates unified diff between two text strings."""

    def __init__(self) -> None:
        super().__init__(
            name="diff_texts",
            description="Computes unified diff between two text strings.",
            version="1.0.0",
        )

    def execute(self, a: Any = None, b: Any = None, **kwargs: Any) -> ToolResult:
        if not isinstance(a, str) or not isinstance(b, str):
            return ToolResult.fail("Parameters 'a' and 'b' must be strings.")
        diff = list(difflib.unified_diff(a.splitlines(), b.splitlines(), lineterm=""))
        return ToolResult.ok(diff)


class SemverParseTool(BaseTool):
    """Parses semantic version strings into components."""

    def __init__(self) -> None:
        super().__init__(
            name="semver_parse",
            description="Parses a SemVer string into major, minor, patch, prerelease, and build.",
            version="1.0.0",
        )

    def execute(self, version: Any = None, **kwargs: Any) -> ToolResult:
        if not isinstance(version, str):
            return ToolResult.fail("Parameter 'version' must be a string.")
        parsed = _parse_semver(version)
        if parsed is None:
            return ToolResult.fail(f"Invalid semantic version string: {version}")
        return ToolResult.ok(parsed)


class SemverCompareTool(BaseTool):
    """Compares two semantic version strings according to precedence rules."""

    def __init__(self) -> None:
        super().__init__(
            name="semver_compare",
            description="Compares two SemVer strings and returns -1, 0, or 1 based on precedence.",
            version="1.0.0",
        )

    def execute(self, a: Any = None, b: Any = None, **kwargs: Any) -> ToolResult:
        if not isinstance(a, str) or not isinstance(b, str):
            return ToolResult.fail("Parameters 'a' and 'b' must be strings.")
        parsed_a = _parse_semver(a)
        if parsed_a is None:
            return ToolResult.fail(f"Invalid semantic version: {a}")
        parsed_b = _parse_semver(b)
        if parsed_b is None:
            return ToolResult.fail(f"Invalid semantic version: {b}")
        return ToolResult.ok(_compare_semver(parsed_a, parsed_b))


class CronNextTool(BaseTool):
    """Calculates the next execution time for a 5-field cron expression."""

    def __init__(self) -> None:
        super().__init__(
            name="cron_next",
            description="Calculates the next matching datetime for a cron expression after a given ISO datetime.",
            version="1.0.0",
        )

    @staticmethod
    def _parse_field(field_str: str, min_val: int, max_val: int, is_dow: bool = False) -> set[int]:
        values: set[int] = set()
        parts = field_str.split(",")
        for part in parts:
            if not part:
                raise ValueError(f"Empty segment in field: '{field_str}'")
            if "/" in part:
                subparts = part.split("/")
                if len(subparts) != 2:
                    raise ValueError(f"Invalid step format: '{part}'")
                base_str, step_str = subparts
                step = int(step_str)
                if step <= 0:
                    raise ValueError(f"Step must be positive integer: '{step_str}'")
                if base_str == "*":
                    start, end = min_val, max_val
                elif "-" in base_str:
                    range_parts = base_str.split("-")
                    if len(range_parts) != 2:
                        raise ValueError(f"Invalid range in step: '{base_str}'")
                    start, end = int(range_parts[0]), int(range_parts[1])
                else:
                    start = int(base_str)
                    end = max_val
            elif "-" in part:
                range_parts = part.split("-")
                if len(range_parts) != 2:
                    raise ValueError(f"Invalid range format: '{part}'")
                start, end = int(range_parts[0]), int(range_parts[1])
                step = 1
            elif part == "*":
                start, end, step = min_val, max_val, 1
            else:
                val = int(part)
                start, end, step = val, val, 1

            if start > end:
                raise ValueError(f"Range start {start} cannot exceed end {end}")
            if start < min_val or end > max_val:
                raise ValueError(f"Value out of bounds ({min_val}-{max_val}): '{part}'")

            for val in range(start, end + 1, step):
                if is_dow and val == 7:
                    values.add(0)
                else:
                    values.add(val)
        return values

    def execute(self, expression: str = "", after: str = "", **kwargs: Any) -> ToolResult:
        if not isinstance(expression, str) or not expression.strip():
            return ToolResult.fail("Missing or invalid cron expression")
        if not isinstance(after, str) or not after.strip():
            return ToolResult.fail("Missing or invalid after timestamp")

        try:
            after_dt = datetime.fromisoformat(after)
        except Exception as e:
            return ToolResult.fail(f"Invalid ISO datetime for 'after': {e}")

        fields = expression.strip().split()
        if len(fields) != 5:
            return ToolResult.fail(f"Expression must contain exactly 5 fields, got {len(fields)}")

        min_field, hour_field, dom_field, mon_field, dow_field = fields

        try:
            min_set = self._parse_field(min_field, 0, 59)
            hour_set = self._parse_field(hour_field, 0, 23)
            dom_set = self._parse_field(dom_field, 1, 31)
            mon_set = self._parse_field(mon_field, 1, 12)
            dow_set = self._parse_field(dow_field, 0, 7, is_dow=True)
        except Exception as e:
            return ToolResult.fail(f"Invalid cron expression: {e}")

        dom_restricted = dom_field != "*"
        dow_restricted = dow_field != "*"

        start_dt = after_dt.replace(second=0, microsecond=0) + timedelta(minutes=1)
        max_minutes = 366 * 24 * 60
        curr = start_dt

        for _ in range(max_minutes):
            if curr.minute in min_set and curr.hour in hour_set and curr.month in mon_set:
                cron_dow = (curr.weekday() + 1) % 7
                if dom_restricted and dow_restricted:
                    day_match = (curr.day in dom_set) or (cron_dow in dow_set)
                else:
                    day_match = (curr.day in dom_set) and (cron_dow in dow_set)

                if day_match:
                    return ToolResult.ok(curr.isoformat())

            curr += timedelta(minutes=1)

        return ToolResult.fail("No matching datetime within 366 days")


class MarkdownHeadingsTool(BaseTool):
    """Extract ATX headings from markdown text."""

    def __init__(self) -> None:
        super().__init__(
            name="markdown_headings",
            description="Extract ATX headings from markdown text outside code blocks.",
            version="1.0.0",
        )

    def execute(self, text: str = None, **kwargs: Any) -> ToolResult:
        if not isinstance(text, str):
            return ToolResult.fail("Parameter 'text' must be a string")
        headings: list[dict[str, Any]] = []
        in_code_block = False
        for line in text.splitlines():
            if line.startswith("```"):
                in_code_block = not in_code_block
                continue
            if in_code_block:
                continue
            match = re.match(r"^(#{1,6})\s+(.*)$", line)
            if match:
                level = len(match.group(1))
                heading_text = match.group(2).strip().rstrip("#").strip()
                headings.append({"level": level, "text": heading_text})
        return ToolResult.ok(headings)


class IniParseTool(BaseTool):
    """Parse INI-formatted text into a nested dictionary."""

    def __init__(self) -> None:
        super().__init__(
            name="ini_parse",
            description="Parse INI-formatted text into a nested dictionary.",
            version="1.0.0",
        )

    def execute(self, text: Any = None, **kwargs: Any) -> ToolResult:
        if not isinstance(text, str):
            return ToolResult.fail("Parameter 'text' must be a string")
        try:
            parser = configparser.ConfigParser(interpolation=None)
            parser.read_string(text)
            result: dict[str, dict[str, str]] = {"DEFAULT": dict(parser.defaults())}
            for section in parser.sections():
                result[section] = dict(parser[section])
            return ToolResult.ok(result)
        except configparser.Error as exc:
            return ToolResult.fail(f"INI parse error: {exc}")
        except Exception as exc:
            return ToolResult.fail(str(exc))


class LineSortTool(BaseTool):
    """Sort lines of text in ascending or descending order."""

    def __init__(self) -> None:
        super().__init__(
            name="line_sort",
            description="Sort lines of text in ascending or descending order.",
            version="1.0.0",
        )

    def execute(self, text: Any = None, reverse: bool = False, **kwargs: Any) -> ToolResult:
        if not isinstance(text, str):
            return ToolResult.fail("Parameter 'text' must be a string")
        if not isinstance(reverse, bool):
            return ToolResult.fail("Parameter 'reverse' must be a boolean")
        try:
            sorted_lines = sorted(text.splitlines(), reverse=reverse)
            return ToolResult.ok("\n".join(sorted_lines))
        except Exception as exc:
            return ToolResult.fail(str(exc))
