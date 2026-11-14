# Copyright © 2026 2351485 ALBERTA INC.
# SPDX-License-Identifier: AGPL-3.0-only
"""Omegacode skills library — registry and data."""

from pathlib import Path
from .registry import Skill, SkillRegistry

__all__ = ["SkillRegistry", "Skill", "load_default_registry"]


def load_default_registry() -> SkillRegistry:
    """Load and return the default SkillRegistry bundled with this package."""
    return SkillRegistry.load_default()
