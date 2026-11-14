# Copyright © 2026 2351485 ALBERTA INC.
# SPDX-License-Identifier: AGPL-3.0-only
"""Text manipulation tools."""

import base64
import binascii
import hashlib
import re
from typing import Any

from agentic_os.omega.tools.base import BaseTool, ToolResult


class WordCountTool(BaseTool):
    """Counts words, characters, lines, and non-space characters in text."""

    def __init__(self) -> None:
        super().__init__(
            name="word_count",
            description="Count words, characters, and lines in a string.",
            version="1.0.0",
        )

    def execute(self, text: Any = None, **kwargs: Any) -> ToolResult:
        if not isinstance(text, str):
            return ToolResult.fail("Parameter 'text' must be a string.")
        return ToolResult.ok({
            "words": len(text.split()),
            "characters": len(text),
            "lines": len(text.splitlines()),
            "characters_no_spaces": len(text.replace(" ", "")),
        })


class CaseConvertTool(BaseTool):
    """Converts text between different casing conventions."""

    def __init__(self) -> None:
        super().__init__(
            name="case_convert",
            description="Convert text case to upper, lower, title, snake, kebab, camel, or pascal.",
            version="1.0.0",
        )

    def execute(self, text: Any = None, mode: Any = None, **kwargs: Any) -> ToolResult:
        if not isinstance(text, str):
            return ToolResult.fail("Parameter 'text' must be a string.")
        if not isinstance(mode, str):
            return ToolResult.fail("Parameter 'mode' must be a string.")

        valid_modes = {"upper", "lower", "title", "snake", "kebab", "camel", "pascal"}
        if mode not in valid_modes:
            return ToolResult.fail(
                f"Unknown mode '{mode}'. Expected one of: {', '.join(sorted(valid_modes))}."
            )

        if mode == "upper":
            return ToolResult.ok(text.upper())
        if mode == "lower":
            return ToolResult.ok(text.lower())
        if mode == "title":
            return ToolResult.ok(text.title())

        words = [w for w in re.split(r"[\s\-_]+", text) if w]
        if not words:
            return ToolResult.ok("")

        if mode == "snake":
            return ToolResult.ok("_".join(w.lower() for w in words))
        if mode == "kebab":
            return ToolResult.ok("-".join(w.lower() for w in words))
        if mode == "camel":
            return ToolResult.ok(words[0].lower() + "".join(w.capitalize() for w in words[1:]))
        if mode == "pascal":
            return ToolResult.ok("".join(w.capitalize() for w in words))

        return ToolResult.fail(f"Unhandled mode '{mode}'.")


class SlugifyTool(BaseTool):
    """Converts text into a URL-friendly slug."""

    def __init__(self) -> None:
        super().__init__(
            name="slugify",
            description="Generate a URL-friendly slug from input text.",
            version="1.0.0",
        )

    def execute(self, text: Any = None, **kwargs: Any) -> ToolResult:
        if not isinstance(text, str):
            return ToolResult.fail("Parameter 'text' must be a string.")
        lowered = text.lower()
        slug = re.sub(r"[^a-z0-9]+", "-", lowered).strip("-")
        return ToolResult.ok(slug)


class ExtractUrlsTool(BaseTool):
    """Extracts HTTP and HTTPS URLs from text."""

    def __init__(self) -> None:
        super().__init__(
            name="extract_urls",
            description="Extract HTTP and HTTPS URLs from text.",
            version="1.0.0",
        )

    def execute(self, text: Any = None, **kwargs: Any) -> ToolResult:
        if not isinstance(text, str):
            return ToolResult.fail("Parameter 'text' must be a string.")
        raw_matches = re.findall(r"https?://[^\s]+", text)
        cleaned = [url.rstrip(".,;:!?)") for url in raw_matches]
        return ToolResult.ok(cleaned)


class ExtractEmailsTool(BaseTool):
    """Extracts email addresses from text."""

    def __init__(self) -> None:
        super().__init__(
            name="extract_emails",
            description="Extract email addresses from text.",
            version="1.0.0",
        )

    def execute(self, text: Any = None, **kwargs: Any) -> ToolResult:
        if not isinstance(text, str):
            return ToolResult.fail("Parameter 'text' must be a string.")
        matches = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
        return ToolResult.ok(matches)


class Base64EncodeTool(BaseTool):
    """Encodes a UTF-8 text string to Base64."""

    def __init__(self) -> None:
        super().__init__(
            name="base64_encode",
            description="Encode a UTF-8 text string to Base64.",
            version="1.0.0",
        )

    def execute(self, text: str = None, **kwargs: Any) -> ToolResult:
        if not isinstance(text, str):
            return ToolResult.fail("Parameter 'text' must be a string.")
        try:
            encoded = base64.b64encode(text.encode("utf-8")).decode("ascii")
            return ToolResult.ok(data=encoded)
        except Exception as e:
            return ToolResult.fail(f"Encoding failed: {e}")


class Base64DecodeTool(BaseTool):
    """Decodes a Base64 encoded string to a UTF-8 text string."""

    def __init__(self) -> None:
        super().__init__(
            name="base64_decode",
            description="Decode a Base64 string to a UTF-8 text string.",
            version="1.0.0",
        )

    def execute(self, text: str = None, **kwargs: Any) -> ToolResult:
        if not isinstance(text, str):
            return ToolResult.fail("Parameter 'text' must be a string.")
        try:
            decoded_bytes = base64.b64decode(text, validate=True)
            decoded_text = decoded_bytes.decode("utf-8")
            return ToolResult.ok(data=decoded_text)
        except (binascii.Error, ValueError):
            return ToolResult.fail("Invalid base64 input.")
        except UnicodeDecodeError:
            return ToolResult.fail("Decoded data is not valid UTF-8.")
        except Exception as e:
            return ToolResult.fail(f"Decoding failed: {e}")


class HashTextTool(BaseTool):
    """Computes a cryptographic hash digest of a text string."""

    _SUPPORTED = {"sha256", "sha1", "md5"}

    def __init__(self) -> None:
        super().__init__(
            name="hash_text",
            description="Compute cryptographic hash of a text string.",
            version="1.0.0",
        )

    def execute(
        self, text: str = None, algorithm: str = "sha256", **kwargs: Any
    ) -> ToolResult:
        if not isinstance(text, str):
            return ToolResult.fail("Parameter 'text' must be a string.")
        if not isinstance(algorithm, str):
            return ToolResult.fail("Parameter 'algorithm' must be a string.")
        algo = algorithm.lower()
        if algo not in self._SUPPORTED:
            return ToolResult.fail(
                f"Unsupported algorithm '{algorithm}'. Must be one of: sha256, sha1, md5."
            )
        try:
            hasher = getattr(hashlib, algo)()
            hasher.update(text.encode("utf-8"))
            return ToolResult.ok(data=hasher.hexdigest())
        except Exception as e:
            return ToolResult.fail(f"Hashing failed: {e}")


class RegexReplaceTool(BaseTool):
    """Replaces regular expression matches in a text string."""

    def __init__(self) -> None:
        super().__init__(
            name="regex_replace",
            description="Replace regex pattern matches in text with a replacement string.",
            version="1.0.0",
        )

    def execute(
        self,
        text: str = None,
        pattern: str = None,
        replacement: str = None,
        **kwargs: Any,
    ) -> ToolResult:
        if not isinstance(text, str):
            return ToolResult.fail("Parameter 'text' must be a string.")
        if not isinstance(pattern, str):
            return ToolResult.fail("Parameter 'pattern' must be a string.")
        if not isinstance(replacement, str):
            return ToolResult.fail("Parameter 'replacement' must be a string.")
        try:
            result = re.sub(pattern, replacement, text)
            return ToolResult.ok(data=result)
        except re.error as e:
            return ToolResult.fail(f"Invalid regular expression: {e}")
        except Exception as e:
            return ToolResult.fail(f"Regex replacement failed: {e}")


class DedupeLinesTool(BaseTool):
    """Removes duplicate lines from text while preserving first occurrences and order."""

    def __init__(self) -> None:
        super().__init__(
            name="dedupe_lines",
            description="Remove duplicate lines from text preserving order.",
            version="1.0.0",
        )

    def execute(self, text: str = None, **kwargs: Any) -> ToolResult:
        if not isinstance(text, str):
            return ToolResult.fail("Parameter 'text' must be a string.")
        try:
            lines = text.split("\n")
            deduped = list(dict.fromkeys(lines))
            return ToolResult.ok(data="\n".join(deduped))
        except Exception as e:
            return ToolResult.fail(f"Deduplication failed: {e}")
