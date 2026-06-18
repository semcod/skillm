"""Load and persist skill manifests."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

from skillm.models import Manifest, Skill

DEFAULT_MANIFEST = "app.skillm.yaml"


def _default_manifest_path() -> str:
    return os.environ.get("SKILLM_MANIFEST", DEFAULT_MANIFEST)


class SkillRegistry:
    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path or DEFAULT_MANIFEST).expanduser()

    def load(self) -> Manifest:
        if not self.path.is_file():
            return Manifest()
        data = yaml.safe_load(self.path.read_text(encoding="utf-8")) or {}
        skills = {
            name: Skill.from_dict(name, spec if isinstance(spec, dict) else {})
            for name, spec in (data.get("skills") or {}).items()
        }
        return Manifest(version=str(data.get("version", "1")), skills=skills)

    def save(self, manifest: Manifest) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            yaml.safe_dump(manifest.to_dict(), sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )

    def get(self, name: str) -> Skill | None:
        return self.load().skills.get(name)

    def list_skills(self) -> list[Skill]:
        return list(self.load().skills.values())

    def register(self, name: str, spec: dict[str, Any]) -> Skill:
        manifest = self.load()
        skill = Skill.from_dict(name, spec)
        manifest.skills[name] = skill
        self.save(manifest)
        return skill

    def unregister(self, name: str) -> bool:
        manifest = self.load()
        if name not in manifest.skills:
            return False
        del manifest.skills[name]
        self.save(manifest)
        return True


def default_registry(manifest: str | None = None) -> SkillRegistry:
    return SkillRegistry(manifest or _default_manifest_path())
