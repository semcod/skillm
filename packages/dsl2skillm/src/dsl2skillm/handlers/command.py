"""Write command handlers."""

from __future__ import annotations

import json
from typing import Any

from dsl2skillm.result import DslResult
from dsl2skillm.uri import skill_name_from_uri
from skillm.invoke import invoke_skill
from skillm.registry import default_registry


def _manifest(cmd: dict[str, Any], default_file: str | None) -> str:
    return cmd.get("file") or default_file or "app.skillm.yaml"


def _load_spec(spec_json: str) -> dict[str, Any]:
    if not spec_json:
        return {}
    if spec_json.startswith("{"):
        return json.loads(spec_json)
    from pathlib import Path
    return json.loads(Path(spec_json).expanduser().read_text(encoding="utf-8"))


def handle_register(cmd: dict[str, Any], *, line: str, default_file: str | None) -> DslResult:
    reg = default_registry(_manifest(cmd, default_file))
    spec = _load_spec(cmd.get("spec_json", ""))
    spec["type"] = cmd.get("type") or spec.get("type", "cli")
    skill = reg.register(cmd.get("name", ""), spec)
    payload = {"ok": True, "name": skill.name, "uri": skill.uri(), "skill": skill.to_dict()}
    return DslResult(
        ok=True,
        command=line,
        action="register",
        output=json.dumps(payload, ensure_ascii=False, indent=2),
        data=payload,
    )


def handle_unregister(cmd: dict[str, Any], *, line: str, default_file: str | None) -> DslResult:
    reg = default_registry(_manifest(cmd, default_file))
    ok = reg.unregister(cmd.get("name", ""))
    payload = {"ok": ok, "name": cmd.get("name", "")}
    return DslResult(
        ok=ok,
        command=line,
        action="unregister",
        output=json.dumps(payload, ensure_ascii=False, indent=2),
        data=payload,
        error=None if ok else "skill not found",
    )


def handle_invoke(cmd: dict[str, Any], *, line: str, default_file: str | None) -> DslResult:
    name = skill_name_from_uri(cmd.get("target", ""))
    reg = default_registry(_manifest(cmd, default_file))
    args = json.loads(cmd.get("args_json") or "[]")
    result = invoke_skill(
        name,
        args=args,
        input_text=cmd.get("input_text", ""),
        body=cmd.get("body", ""),
        registry=reg,
    )
    return DslResult(
        ok=result.get("ok", False),
        command=line,
        action="invoke",
        output=json.dumps(result, ensure_ascii=False, indent=2),
        data=result,
        error=result.get("error"),
    )


def handle_patch(cmd: dict[str, Any], *, line: str, default_file: str | None) -> DslResult:
    name = skill_name_from_uri(cmd.get("target", ""))
    reg = default_registry(_manifest(cmd, default_file))
    existing = reg.get(name)
    if existing is None:
        return DslResult(ok=False, command=line, action="patch", error=f"unknown skill: {name}")
    spec = existing.to_dict()
    spec.update(_load_spec(cmd.get("spec_json", "")))
    skill = reg.register(name, spec)
    payload = {"ok": True, "name": skill.name, "uri": skill.uri(), "skill": skill.to_dict()}
    return DslResult(
        ok=True,
        command=line,
        action="patch",
        output=json.dumps(payload, ensure_ascii=False, indent=2),
        data=payload,
    )
