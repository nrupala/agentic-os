# Copyright © 2026 2351485 ALBERTA INC.
# SPDX-License-Identifier: AGPL-3.0-only
"""
agentic_os.omega.tools.base
Abstract Base Tool definitions and standard execution payload contracts.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class ToolResult:
    """Standardized tool response payload."""

    success: bool
    data: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def ok(cls, data: Any = None, **metadata: Any) -> ToolResult:
        return cls(success=True, data=data, error=None, metadata=metadata)

    @classmethod
    def fail(cls, error: str, data: Any = None, **metadata: Any) -> ToolResult:
        return cls(success=False, data=data, error=error, metadata=metadata)


class BaseTool(ABC):
    """Abstract interface governing all executable tools in the Omega toolchain."""

    def __init__(self, name: str, description: str, version: str = "1.0.0") -> None:
        self.name = name
        self.description = description
        self.version = version

    @abstractmethod
    def execute(self, **kwargs: Any) -> ToolResult:
        """Execute the tool operation with supplied keyword arguments."""
        pass

    def get_schema(self) -> Dict[str, Any]:
        """Returns metadata documentation schema for introspection."""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
        }
