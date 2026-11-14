# Copyright © 2026 2351485 ALBERTA INC.
# SPDX-License-Identifier: AGPL-3.0-only
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union


@dataclass(frozen=True)
class Skill:
    id: str
    name: str
    description: str
    tags: Tuple[str, ...]
    instructions: str

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Skill":
        return cls(
            id=d["id"],
            name=d["name"],
            description=d["description"],
            tags=tuple(d.get("tags", ())),
            instructions=d["instructions"],
        )


class SkillRegistry:
    def __init__(self, skills: Optional[Iterable[Skill]] = None) -> None:
        self._skills: Dict[str, Skill] = {}
        if skills is not None:
            for skill in skills:
                if skill.id in self._skills:
                    raise ValueError(f"Duplicate skill id detected: {skill.id}")
                self._skills[skill.id] = skill

    @classmethod
    def load(cls, data_dir: Union[str, Path]) -> "SkillRegistry":
        target_dir = Path(data_dir)
        json_files = sorted(target_dir.glob("*.json"))
        loaded_skills: List[Skill] = []

        for json_path in json_files:
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception as exc:
                raise ValueError(
                    f"Malformed JSON in skill file {json_path.name}: {exc}"
                ) from exc

            if not isinstance(data, list):
                raise ValueError(
                    f"Invalid content in skill file {json_path.name}: top-level element must be a list"
                )

            for item in data:
                try:
                    loaded_skills.append(Skill.from_dict(item))
                except Exception as exc:
                    raise ValueError(
                        f"Malformed skill entry in file {json_path.name}: {exc}"
                    ) from exc

        return cls(loaded_skills)

    @classmethod
    def load_default(cls) -> "SkillRegistry":
        default_dir = Path(__file__).parent / "data"
        return cls.load(default_dir)

    def get(self, skill_id: str) -> Optional[Skill]:
        return self._skills.get(skill_id)

    def require(self, skill_id: str) -> Skill:
        if skill_id not in self._skills:
            raise KeyError(f"Skill not found in registry: {skill_id}")
        return self._skills[skill_id]

    def search(self, query: str) -> List[Skill]:
        stripped = query.strip().lower()
        if not stripped:
            return list(self._skills.values())

        results: List[Skill] = []
        for skill in self._skills.values():
            match_name = stripped in skill.name.lower()
            match_desc = stripped in skill.description.lower()
            match_tags = any(stripped in tag.lower() for tag in skill.tags)
            if match_name or match_desc or match_tags:
                results.append(skill)
        return results

    def list(self, tags: Optional[Iterable[str]] = None) -> List[Skill]:
        if tags is None:
            return list(self._skills.values())

        target_tags = {t.lower() for t in tags}
        if not target_tags:
            return list(self._skills.values())

        results: List[Skill] = []
        for skill in self._skills.values():
            skill_tag_set = {t.lower() for t in skill.tags}
            if not target_tags.isdisjoint(skill_tag_set):
                results.append(skill)
        return results

    def count(self) -> int:
        return len(self._skills)

    def __len__(self) -> int:
        return self.count()

    def __contains__(self, skill_id: object) -> bool:
        return skill_id in self._skills

    def ids(self) -> List[str]:
        return sorted(self._skills.keys())
