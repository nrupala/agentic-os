# Copyright © 2026 2351485 ALBERTA INC.
# SPDX-License-Identifier: AGPL-3.0-only
"""Web and URL tools (plain HTTP GET/HEAD only)."""

import socket
from typing import Any, Optional
import urllib.error
import urllib.parse
import urllib.request

from agentic_os.omega.tools.base import BaseTool, ToolResult


class HttpGetTool(BaseTool):
    """Perform plain HTTP GET requests with size limits and timeouts."""

    def __init__(self) -> None:
        super().__init__(
            name="http_get",
            description="Execute an HTTP GET request and retrieve the status, headers, and body.",
            version="1.0.0",
        )

    def execute(
        self,
        url: Optional[str] = None,
        timeout: float = 10.0,
        max_bytes: int = 1000000,
        **kwargs: Any,
    ) -> ToolResult:
        if not url or not isinstance(url, str):
            return ToolResult.fail("Parameter 'url' must be a non-empty string.")
        if not isinstance(timeout, (int, float)) or timeout <= 0:
            return ToolResult.fail("Parameter 'timeout' must be a positive number.")
        if not isinstance(max_bytes, int) or max_bytes < 0:
            return ToolResult.fail("Parameter 'max_bytes' must be a non-negative integer.")

        parsed = urllib.parse.urlsplit(url)
        if parsed.scheme.lower() not in ("http", "https"):
            return ToolResult.fail("Only HTTP and HTTPS URLs are supported.")

        req = urllib.request.Request(url, method="GET")
        try:
            with urllib.request.urlopen(req, timeout=float(timeout)) as response:
                status = int(response.status)
                headers = dict(response.headers)
                body_bytes = response.read(max_bytes)
                body = body_bytes.decode("utf-8", errors="replace")
                return ToolResult.ok({"status": status, "headers": headers, "body": body})
        except urllib.error.HTTPError as err:
            status = int(err.code)
            headers = dict(err.headers)
            body_bytes = err.read(max_bytes)
            body = body_bytes.decode("utf-8", errors="replace")
            return ToolResult.ok({"status": status, "headers": headers, "body": body})
        except (urllib.error.URLError, TimeoutError, socket.timeout, OSError) as err:
            return ToolResult.fail(f"HTTP GET request failed: {err}")
        except Exception as err:
            return ToolResult.fail(f"Unexpected error during HTTP GET: {err}")


class HttpHeadTool(BaseTool):
    """Perform plain HTTP HEAD requests with timeouts."""

    def __init__(self) -> None:
        super().__init__(
            name="http_head",
            description="Execute an HTTP HEAD request and retrieve the status and headers.",
            version="1.0.0",
        )

    def execute(
        self,
        url: Optional[str] = None,
        timeout: float = 10.0,
        **kwargs: Any,
    ) -> ToolResult:
        if not url or not isinstance(url, str):
            return ToolResult.fail("Parameter 'url' must be a non-empty string.")
        if not isinstance(timeout, (int, float)) or timeout <= 0:
            return ToolResult.fail("Parameter 'timeout' must be a positive number.")

        parsed = urllib.parse.urlsplit(url)
        if parsed.scheme.lower() not in ("http", "https"):
            return ToolResult.fail("Only HTTP and HTTPS URLs are supported.")

        req = urllib.request.Request(url, method="HEAD")
        try:
            with urllib.request.urlopen(req, timeout=float(timeout)) as response:
                status = int(response.status)
                headers = dict(response.headers)
                return ToolResult.ok({"status": status, "headers": headers})
        except urllib.error.HTTPError as err:
            status = int(err.code)
            headers = dict(err.headers)
            return ToolResult.ok({"status": status, "headers": headers})
        except (urllib.error.URLError, TimeoutError, socket.timeout, OSError) as err:
            return ToolResult.fail(f"HTTP HEAD request failed: {err}")
        except Exception as err:
            return ToolResult.fail(f"Unexpected error during HTTP HEAD: {err}")


class UrlParseTool(BaseTool):
    """Parse a URL into its structural components and query parameters."""

    def __init__(self) -> None:
        super().__init__(
            name="url_parse",
            description="Parse a URL into scheme, netloc, host, port, path, query, and fragment.",
            version="1.0.0",
        )

    def execute(self, url: Optional[str] = None, **kwargs: Any) -> ToolResult:
        if url is None or not isinstance(url, str):
            return ToolResult.fail("Parameter 'url' must be a string.")

        try:
            parsed = urllib.parse.urlsplit(url)
            query_params = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
            result = {
                "scheme": parsed.scheme,
                "netloc": parsed.netloc,
                "host": parsed.hostname,
                "port": parsed.port,
                "path": parsed.path,
                "query": parsed.query,
                "fragment": parsed.fragment,
                "query_params": query_params,
            }
            return ToolResult.ok(result)
        except Exception as err:
            return ToolResult.fail(f"Failed to parse URL: {err}")


class UrlBuildTool(BaseTool):
    """Construct or modify a URL with updated paths and query parameters."""

    def __init__(self) -> None:
        super().__init__(
            name="url_build",
            description="Build or modify a URL by appending a path suffix and merging query parameters.",
            version="1.0.0",
        )

    def execute(
        self,
        base: Optional[str] = None,
        params: Optional[dict] = None,
        path_suffix: Optional[str] = None,
        **kwargs: Any,
    ) -> ToolResult:
        if not base or not isinstance(base, str):
            return ToolResult.fail("Parameter 'base' must be a non-empty string.")
        if params is not None and not isinstance(params, dict):
            return ToolResult.fail("Parameter 'params' must be a dictionary if provided.")
        if path_suffix is not None and not isinstance(path_suffix, str):
            return ToolResult.fail("Parameter 'path_suffix' must be a string if provided.")

        try:
            parsed = urllib.parse.urlsplit(base)
            path = parsed.path

            if path_suffix:
                stripped_suffix = path_suffix.lstrip("/")
                if path:
                    path = f"{path.rstrip('/')}/{stripped_suffix}"
                else:
                    path = f"/{stripped_suffix}" if parsed.netloc else stripped_suffix

            query = parsed.query
            if params:
                current_params = urllib.parse.parse_qs(query, keep_blank_values=True)
                for k, v in params.items():
                    current_params[k] = v
                query = urllib.parse.urlencode(current_params, doseq=True)

            rebuilt = urllib.parse.urlunsplit(
                (parsed.scheme, parsed.netloc, path, query, parsed.fragment)
            )
            return ToolResult.ok(rebuilt)
        except Exception as err:
            return ToolResult.fail(f"Failed to build URL: {err}")


class DnsLookupTool(BaseTool):
    """Resolve hostnames to unique sorted IP addresses."""

    def __init__(self) -> None:
        super().__init__(
            name="dns_lookup",
            description="Resolve a hostname to a sorted list of unique IP addresses.",
            version="1.0.0",
        )

    def execute(self, hostname: Optional[str] = None, **kwargs: Any) -> ToolResult:
        if not hostname or not isinstance(hostname, str):
            return ToolResult.fail("Parameter 'hostname' must be a non-empty string.")

        try:
            addr_info = socket.getaddrinfo(hostname, None)
            unique_ips = set()
            for entry in addr_info:
                sockaddr = entry[4]
                if sockaddr and len(sockaddr) > 0:
                    unique_ips.add(sockaddr[0])
            return ToolResult.ok(sorted(unique_ips))
        except (socket.gaierror, socket.herror, OSError) as err:
            return ToolResult.fail(f"DNS lookup failed for '{hostname}': {err}")
        except Exception as err:
            return ToolResult.fail(f"Unexpected error during DNS lookup: {err}")
