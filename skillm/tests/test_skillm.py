"""Tests for skillm core."""

from pathlib import Path

import yaml

from skillm.invoke import invoke_skill, list_skills
from skillm.registry import SkillRegistry
from skillm.validate import validate_manifest


def test_validate_manifest_ok(tmp_path: Path) -> None:
    manifest = tmp_path / "app.skillm.yaml"
    manifest.write_text(yaml.safe_dump({
        "version": "1",
        "skills": {
            "echo": {"type": "python", "entry": "skillm.examples.echo:run"},
        },
    }), encoding="utf-8")
    result = validate_manifest(manifest)
    assert result["ok"] is True


def test_invoke_python_skill(tmp_path: Path) -> None:
    manifest = tmp_path / "app.skillm.yaml"
    reg = SkillRegistry(manifest)
    reg.register("echo", {"type": "python", "entry": "skillm.examples.echo:run"})
    result = invoke_skill("echo", args=["test"], registry=reg)
    assert result["ok"] is True
    assert "test" in result["output"]


def test_list_skills(tmp_path: Path) -> None:
    manifest = tmp_path / "app.skillm.yaml"
    reg = SkillRegistry(manifest)
    reg.register("a", {"type": "cli", "command": "echo", "args": ["a"]})
    payload = list_skills(registry=reg)
    assert payload["count"] == 1
