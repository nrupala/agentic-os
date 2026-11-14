# Copyright © 2026 2351485 ALBERTA INC.
# SPDX-License-Identifier: AGPL-3.0-only

"""Data, time, and numeric tools."""

import ast
import csv
import datetime
import io
import json
import math
import re
import secrets
import uuid
from typing import Any, Optional

from agentic_os.omega.tools.base import BaseTool, ToolResult


class JsonPrettyTool(BaseTool):
    """Format a JSON string with indentation and sorted keys."""

    def __init__(self) -> None:
        super().__init__(
            name="json_pretty",
            description="Format a JSON string with indentation and sorted keys.",
            version="1.0.0",
        )

    def execute(self, text: str, indent: int = 2, **kwargs: Any) -> ToolResult:
        if not isinstance(text, str):
            return ToolResult.fail("Parameter 'text' must be a string.")
        if not isinstance(indent, int) or isinstance(indent, bool):
            return ToolResult.fail("Parameter 'indent' must be an integer.")
        try:
            obj = json.loads(text)
            formatted = json.dumps(obj, indent=indent, sort_keys=True)
            return ToolResult.ok(formatted)
        except Exception as exc:
            return ToolResult.fail(f"Failed to parse or format JSON: {exc}")


class JsonQueryTool(BaseTool):
    """Query a JSON string using dot-separated keys and list index syntax."""

    def __init__(self) -> None:
        super().__init__(
            name="json_query",
            description="Query a JSON string using dot-separated keys and list indices.",
            version="1.0.0",
        )

    def execute(self, text: str, path: str = "", **kwargs: Any) -> ToolResult:
        if not isinstance(text, str):
            return ToolResult.fail("Parameter 'text' must be a string.")
        if not isinstance(path, str):
            return ToolResult.fail("Parameter 'path' must be a string.")

        try:
            curr = json.loads(text)
        except Exception as exc:
            return ToolResult.fail(f"Invalid JSON text: {exc}")

        path = path.strip()
        if not path:
            return ToolResult.ok(curr)

        tokens: list[Any] = []
        pos = 0
        length = len(path)
        while pos < length:
            if path[pos] == ".":
                pos += 1
                if pos == length or path[pos] == ".":
                    return ToolResult.fail(f"Invalid path syntax near position {pos}.")
                continue
            if path[pos] == "[":
                end = path.find("]", pos)
                if end == -1:
                    return ToolResult.fail("Unclosed bracket in path.")
                idx_str = path[pos + 1 : end]
                if not idx_str.isdigit():
                    return ToolResult.fail(f"Invalid list index in path: '{idx_str}'.")
                tokens.append(int(idx_str))
                pos = end + 1
            else:
                match = re.match(r"[^.\[\]]+", path[pos:])
                if not match:
                    return ToolResult.fail(f"Unexpected token in path at position {pos}.")
                tokens.append(match.group(0))
                pos += len(match.group(0))

        for token in tokens:
            if isinstance(token, int):
                if not isinstance(curr, list):
                    return ToolResult.fail(f"Cannot index non-list with [{token}].")
                if token < 0 or token >= len(curr):
                    return ToolResult.fail(f"List index out of range: {token}.")
                curr = curr[token]
            else:
                if not isinstance(curr, dict):
                    return ToolResult.fail(f"Cannot access key '{token}' on non-dict.")
                if token not in curr:
                    return ToolResult.fail(f"Key not found: '{token}'.")
                curr = curr[token]

        return ToolResult.ok(curr)


class CsvToJsonTool(BaseTool):
    """Convert CSV-formatted text into a list of dictionaries."""

    def __init__(self) -> None:
        super().__init__(
            name="csv_to_json",
            description="Convert CSV formatted text into a list of dictionaries.",
            version="1.0.0",
        )

    def execute(self, text: str, **kwargs: Any) -> ToolResult:
        if not isinstance(text, str):
            return ToolResult.fail("Parameter 'text' must be a string.")
        try:
            reader = csv.DictReader(io.StringIO(text))
            result = [dict(row) for row in reader]
            return ToolResult.ok(result)
        except Exception as exc:
            return ToolResult.fail(f"Failed to parse CSV: {exc}")


class JsonToCsvTool(BaseTool):
    """Convert a JSON array of flat objects into CSV formatted text."""

    def __init__(self) -> None:
        super().__init__(
            name="json_to_csv",
            description="Convert a JSON array of flat objects into CSV formatted text.",
            version="1.0.0",
        )

    def execute(self, text: str, **kwargs: Any) -> ToolResult:
        if not isinstance(text, str):
            return ToolResult.fail("Parameter 'text' must be a string.")

        try:
            data = json.loads(text)
        except Exception as exc:
            return ToolResult.fail(f"Invalid JSON text: {exc}")

        if not isinstance(data, list):
            return ToolResult.fail("JSON data must be an array of objects.")
        if len(data) == 0:
            return ToolResult.fail("JSON array cannot be empty.")

        for idx, item in enumerate(data):
            if not isinstance(item, dict):
                return ToolResult.fail(f"Element at index {idx} is not an object.")

        header = list(data[0].keys())
        buffer = io.StringIO()
        try:
            writer = csv.DictWriter(
                buffer,
                fieldnames=header,
                lineterminator="\n",
                extrasaction="ignore",
                restval="",
            )
            writer.writeheader()
            for row in data:
                cleaned = {k: ("" if row.get(k) is None else row.get(k)) for k in header}
                writer.writerow(cleaned)
            return ToolResult.ok(buffer.getvalue())
        except Exception as exc:
            return ToolResult.fail(f"Failed to generate CSV: {exc}")


class TimestampConvertTool(BaseTool):
    """Convert between Unix epoch timestamps and ISO 8601 strings."""

    def __init__(self) -> None:
        super().__init__(
            name="timestamp_convert",
            description="Convert between Unix epoch timestamps and ISO 8601 strings.",
            version="1.0.0",
        )

    def execute(
        self,
        timestamp: Optional[Any] = None,
        iso: Optional[Any] = None,
        **kwargs: Any,
    ) -> ToolResult:
        has_ts = timestamp is not None
        has_iso = iso is not None

        if (has_ts and has_iso) or (not has_ts and not has_iso):
            return ToolResult.fail("Exactly one of 'timestamp' or 'iso' must be provided.")

        if has_ts:
            if not isinstance(timestamp, (int, float)) or isinstance(timestamp, bool):
                return ToolResult.fail("Parameter 'timestamp' must be an int or float.")
            try:
                dt = datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc)
                return ToolResult.ok(dt.isoformat())
            except Exception as exc:
                return ToolResult.fail(f"Invalid timestamp value: {exc}")

        if not isinstance(iso, str):
            return ToolResult.fail("Parameter 'iso' must be a string.")
        try:
            dt = datetime.datetime.fromisoformat(iso)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=datetime.timezone.utc)
            return ToolResult.ok(dt.timestamp())
        except Exception as exc:
            return ToolResult.fail(f"Invalid ISO string: {exc}")


class DateDiffTool(BaseTool):
    """Calculates the difference between two ISO-formatted date or datetime strings."""

    def __init__(self) -> None:
        super().__init__(
            name="date_diff",
            description="Calculate the difference between two ISO-formatted date or datetime strings.",
            version="1.0.0",
        )

    def execute(self, start: str, end: str) -> ToolResult:
        try:
            if not isinstance(start, str) or not isinstance(end, str):
                return ToolResult.fail("Both start and end must be strings.")

            start_dt = datetime.datetime.fromisoformat(start)
            end_dt = datetime.datetime.fromisoformat(end)

            if start_dt.tzinfo is None:
                start_dt = start_dt.replace(tzinfo=datetime.timezone.utc)
            if end_dt.tzinfo is None:
                end_dt = end_dt.replace(tzinfo=datetime.timezone.utc)

            delta = end_dt - start_dt
            return ToolResult.ok(
                {
                    "days": delta.days,
                    "seconds": delta.seconds,
                    "total_seconds": delta.total_seconds(),
                }
            )
        except Exception as e:
            return ToolResult.fail(f"Failed to calculate date difference: {e}")
class UuidGenerateTool(BaseTool):
    """Generates a random UUID version 4."""

    def __init__(self) -> None:
        super().__init__(
            name="uuid_generate",
            description="Generates a random UUIDv4 string.",
            version="1.0.0",
        )

    def execute(self, **kwargs: Any) -> ToolResult:
        return ToolResult.ok(str(uuid.uuid4()))


class RandomTokenTool(BaseTool):
    """Generates a cryptographically secure random hexadecimal token."""

    def __init__(self) -> None:
        super().__init__(
            name="random_token",
            description="Generates a cryptographically secure random hex token.",
            version="1.0.0",
        )

    def execute(self, nbytes: int = 16, **kwargs: Any) -> ToolResult:
        if not isinstance(nbytes, int) or isinstance(nbytes, bool):
            return ToolResult.fail("'nbytes' must be an integer.")
        if nbytes <= 0 or nbytes > 256:
            return ToolResult.fail("'nbytes' must be a positive integer <= 256.")
        return ToolResult.ok(secrets.token_hex(nbytes))


class UnitConvertTool(BaseTool):
    """Converts values between length, mass, and temperature units."""

    _LENGTH: dict[str, float] = {
        "m": 1.0,
        "km": 1000.0,
        "cm": 0.01,
        "mm": 0.001,
        "mi": 1609.344,
        "ft": 0.3048,
        "in": 0.0254,
    }

    _MASS: dict[str, float] = {
        "kg": 1.0,
        "g": 0.001,
        "lb": 0.45359237,
        "oz": 0.028349523125,
    }

    _TEMP: set[str] = {"c", "f", "k"}

    def __init__(self) -> None:
        super().__init__(
            name="unit_convert",
            description="Converts numerical values between length, mass, or temperature units.",
            version="1.0.0",
        )

    def execute(self, value: float, from_unit: str, to_unit: str, **kwargs: Any) -> ToolResult:
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            return ToolResult.fail("'value' must be a number.")
        if not isinstance(from_unit, str) or not isinstance(to_unit, str):
            return ToolResult.fail("'from_unit' and 'to_unit' must be strings.")

        f = from_unit.strip().lower()
        t = to_unit.strip().lower()

        val = float(value)

        if f in self._LENGTH and t in self._LENGTH:
            base_val = val * self._LENGTH[f]
            return ToolResult.ok(base_val / self._LENGTH[t])

        if f in self._MASS and t in self._MASS:
            base_val = val * self._MASS[f]
            return ToolResult.ok(base_val / self._MASS[t])

        if f in self._TEMP and t in self._TEMP:
            if f == "c":
                c = val
            elif f == "f":
                c = (val - 32.0) * 5.0 / 9.0
            else:
                c = val - 273.15

            if t == "c":
                out = c
            elif t == "f":
                out = (c * 9.0 / 5.0) + 32.0
            else:
                out = c + 273.15
            return ToolResult.ok(out)

        known = set(self._LENGTH) | set(self._MASS) | self._TEMP
        if f not in known or t not in known:
            return ToolResult.fail(f"Unknown unit: '{f}' or '{t}'.")

        return ToolResult.fail(f"Cannot convert between incompatible units: '{f}' and '{t}'.")


class MathEvalTool(BaseTool):
    """Safely evaluates a basic mathematical expression using AST parsing."""

    def __init__(self) -> None:
        super().__init__(
            name="math_eval",
            description="Safely evaluates an arithmetic expression without using eval.",
            version="1.0.0",
        )

    def execute(self, expression: str, **kwargs: Any) -> ToolResult:
        if not isinstance(expression, str):
            return ToolResult.fail("'expression' must be a string.")
        expr_str = expression.strip()
        if not expr_str:
            return ToolResult.fail("Expression cannot be empty.")

        try:
            tree = ast.parse(expr_str, mode="eval")
        except SyntaxError as exc:
            return ToolResult.fail(f"Syntax error in expression: {exc}")

        try:
            result = self._evaluate_node(tree.body)
        except ZeroDivisionError:
            return ToolResult.fail("Division by zero.")
        except OverflowError:
            return ToolResult.fail("Mathematical overflow.")
        except ValueError as exc:
            return ToolResult.fail(str(exc))

        return ToolResult.ok(result)

    def _evaluate_node(self, node: ast.AST) -> int | float:
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
                return node.value
            raise ValueError(f"Unsupported literal type: {type(node.value).__name__}")

        if isinstance(node, ast.UnaryOp):
            operand = self._evaluate_node(node.operand)
            if isinstance(node.op, ast.UAdd):
                return +operand
            if isinstance(node.op, ast.USub):
                return -operand
            raise ValueError(f"Unsupported unary operator: {type(node.op).__name__}")

        if isinstance(node, ast.BinOp):
            left = self._evaluate_node(node.left)
            right = self._evaluate_node(node.right)
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            if isinstance(node.op, ast.Div):
                return left / right
            if isinstance(node.op, ast.FloorDiv):
                return left // right
            if isinstance(node.op, ast.Mod):
                return left % right
            if isinstance(node.op, ast.Pow):
                if isinstance(right, (int, float)) and right > 10000:
                    raise ValueError("Exponent too large.")
                return left ** right
            raise ValueError(f"Unsupported binary operator: {type(node.op).__name__}")

        raise ValueError(f"Disallowed expression node: {type(node).__name__}")
