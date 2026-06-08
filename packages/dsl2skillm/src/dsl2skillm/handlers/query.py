"""Read-only query handlers."""

from __future__ import annotations

import json
from typing import Any

from dsl2skillm.result import DslResult
from dsl2skillm.uri import skill_name_from_uri
from skillm.invoke import health_skill, list_skills, query_skill
from skillm.registry import default_registry
from skillm.validate import validate_manifest


def _manifest(cmd: dict[str, Any], default_file: str | None) -> str:
    return cmd.get("file") or default_file or "app.skillm.yaml"


def handle_list(cmd: dict[str, Any], *, line: str, default_file: str | None) -> DslResult:
    reg = default_registry(_manifest(cmd, default_file))
    result = list_skills(registry=reg)
    return DslResult(
        ok=result.get("ok", False),
        command=line,
        action="list",
        output=json.dumps(result, ensure_ascii=False, indent=2),
        data=result,
    )


def handle_query(cmd: dict[str, Any], *, line: str, default_file: str | None) -> DslResult:
    name = skill_name_from_uri(cmd.get("target", ""))
    reg = default_registry(_manifest(cmd, default_file))
    result = query_skill(name, registry=reg)
    return DslResult(
        ok=result.get("ok", False),
        command=line,
        action="query",
        output=json.dumps(result, ensure_ascii=False, indent=2),
        data=result,
        error=result.get("error"),
    )


def handle_validate(cmd: dict[str, Any], *, line: str, default_file: str | None) -> DslResult:
    path = cmd.get("path") or default_file or "app.skillm.yaml"
    result = validate_manifest(path)
    return DslResult(
        ok=bool(result.get("ok")),
        command=line,
        action="validate",
        output=json.dumps(result, ensure_ascii=False, indent=2),
        data=result,
        error=None if result.get("ok") else "; ".join(result.get("errors") or []),
    )


def handle_health(cmd: dict[str, Any], *, line: str, default_file: str | None) -> DslResult:
    name = skill_name_from_uri(cmd.get("target", ""))
    reg = default_registry(_manifest(cmd, default_file))
    result = health_skill(name, registry=reg)
    return DslResult(
        ok=result.get("ok", False),
        command=line,
        action="health",
        output=json.dumps(result, ensure_ascii=False, indent=2),
        data=result,
        error=result.get("error"),
    )


def handle_resolve(cmd: dict[str, Any], *, line: str, default_file: str | None) -> DslResult:
    from nlp2skillm.to_dsl import resolve_skills

    hits = resolve_skills(cmd.get("text", ""), file=_manifest(cmd, default_file))
    return DslResult(
        ok=bool(hits),
        command=line,
        action="resolve",
        output=json.dumps(hits, ensure_ascii=False, indent=2),
        data={"hits": hits},
        error=None if hits else "no skill matches",
    )
