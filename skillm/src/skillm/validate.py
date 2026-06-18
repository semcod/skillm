"""Validate skill manifests."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from skillm.models import SkillType

VALID_TYPES: frozenset[SkillType] = frozenset({"python", "docker", "cli", "rest", "mcp"})


def validate_manifest(path: str | Path) -> dict[str, Any]:
    p = Path(path).expanduser()
    errors: list[str] = []
    warnings: list[str] = []

    if not p.is_file():
        return {"ok": False, "path": str(p), "errors": [f"manifest not found: {p}"]}

    try:
        data = yaml.safe_load(p.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return {"ok": False, "path": str(p), "errors": [f"invalid YAML: {exc}"]}

    if not isinstance(data, dict):
        return {"ok": False, "path": str(p), "errors": ["manifest root must be a mapping"]}

    skills = data.get("skills")
    if skills is None:
        warnings.append("no skills defined")
        skills = {}
    if not isinstance(skills, dict):
        errors.append("skills must be a mapping")

    for name, spec in (skills or {}).items():
        if not isinstance(spec, dict):
            errors.append(f"{name}: skill spec must be a mapping")
            continue
        stype = spec.get("type", "cli")
        if stype not in VALID_TYPES:
            errors.append(f"{name}: unknown type {stype!r}")
        if stype == "python" and not spec.get("entry"):
            errors.append(f"{name}: python skill requires entry")
        if stype == "docker" and not spec.get("image"):
            errors.append(f"{name}: docker skill requires image")
        if stype == "cli" and not spec.get("command"):
            errors.append(f"{name}: cli skill requires command")
        if stype == "rest" and not spec.get("url"):
            errors.append(f"{name}: rest skill requires url")
        if stype == "mcp" and not spec.get("command"):
            errors.append(f"{name}: mcp skill requires command")

    return {
        "ok": not errors,
        "path": str(p),
        "skill_count": len(skills or {}),
        "errors": errors,
        "warnings": warnings,
    }
