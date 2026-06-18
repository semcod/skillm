"""Invoke registered skills by type."""

from __future__ import annotations

import importlib
import json
import os
import shlex
import subprocess
import urllib.error
import urllib.request
from typing import Any

from skillm.models import Skill
from skillm.registry import SkillRegistry, default_registry


def _merge_env(base: dict[str, str]) -> dict[str, str]:
    env = os.environ.copy()
    env.update(base)
    return env


def invoke_cli(skill: Skill, *, args: list[str] | None = None, input_text: str = "") -> dict[str, Any]:
    cmd = [skill.command, *(args or skill.args)]
    proc = subprocess.run(
        cmd,
        input=input_text or None,
        capture_output=True,
        text=True,
        env=_merge_env(skill.env),
        timeout=120,
    )
    return {
        "ok": proc.returncode == 0,
        "type": "cli",
        "command": shlex.join(cmd),
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "returncode": proc.returncode,
    }


def invoke_python(skill: Skill, *, args: list[str] | None = None, input_text: str = "") -> dict[str, Any]:
    if not skill.entry or ":" not in skill.entry:
        return {"ok": False, "type": "python", "error": "entry must be module:callable"}
    module_name, func_name = skill.entry.split(":", 1)
    module = importlib.import_module(module_name)
    func = getattr(module, func_name)
    call_args = args if args is not None else skill.args
    if input_text:
        result = func(*call_args, input_text=input_text)
    else:
        result = func(*call_args)
    if isinstance(result, dict):
        return {"ok": bool(result.get("ok", True)), "type": "python", **result}
    return {"ok": True, "type": "python", "output": str(result)}


def invoke_docker(skill: Skill, *, args: list[str] | None = None) -> dict[str, Any]:
    cmd = ["docker", "run", "--rm", skill.image, *(args or skill.args)]
    proc = subprocess.run(cmd, capture_output=True, text=True, env=_merge_env(skill.env), timeout=300)
    return {
        "ok": proc.returncode == 0,
        "type": "docker",
        "command": shlex.join(cmd),
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "returncode": proc.returncode,
    }


def invoke_rest(skill: Skill, *, body: str = "", args: list[str] | None = None) -> dict[str, Any]:
    url = skill.url
    if args:
        url = url.format(*args)
    payload = body or skill.body
    req = urllib.request.Request(
        url,
        data=payload.encode("utf-8") if payload and skill.method not in {"GET", "HEAD"} else None,
        method=skill.method,
        headers=dict(skill.headers),
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            text = resp.read().decode("utf-8", errors="replace")
            return {"ok": True, "type": "rest", "status": resp.status, "output": text}
    except urllib.error.HTTPError as exc:
        text = exc.read().decode("utf-8", errors="replace")
        return {"ok": False, "type": "rest", "status": exc.code, "output": text, "error": str(exc)}
    except Exception as exc:
        return {"ok": False, "type": "rest", "error": str(exc)}


def invoke_mcp(skill: Skill) -> dict[str, Any]:
    return {
        "ok": True,
        "type": "mcp",
        "transport": skill.transport,
        "command": skill.command,
        "args": skill.args,
        "hint": "Connect MCP client with this command (stdio transport)",
    }


def invoke_skill(
    name: str,
    *,
    args: list[str] | None = None,
    input_text: str = "",
    body: str = "",
    registry: SkillRegistry | None = None,
) -> dict[str, Any]:
    reg = registry or default_registry()
    skill = reg.get(name)
    if skill is None:
        return {"ok": False, "error": f"unknown skill: {name}"}

    if skill.type == "cli":
        return invoke_cli(skill, args=args, input_text=input_text)
    if skill.type == "python":
        return invoke_python(skill, args=args, input_text=input_text)
    if skill.type == "docker":
        return invoke_docker(skill, args=args)
    if skill.type == "rest":
        return invoke_rest(skill, body=body, args=args)
    if skill.type == "mcp":
        return invoke_mcp(skill)
    return {"ok": False, "error": f"unsupported type: {skill.type}"}


def query_skill(name: str, *, registry: SkillRegistry | None = None) -> dict[str, Any]:
    reg = registry or default_registry()
    skill = reg.get(name)
    if skill is None:
        return {"ok": False, "error": f"unknown skill: {name}"}
    return {"ok": True, "name": name, "uri": skill.uri(), "skill": skill.to_dict()}


def list_skills(*, registry: SkillRegistry | None = None) -> dict[str, Any]:
    reg = registry or default_registry()
    skills = reg.list_skills()
    payload = [{"name": s.name, "type": s.type, "uri": s.uri(), "description": s.description} for s in skills]
    return {"ok": True, "count": len(payload), "skills": payload}


def health_skill(name: str, *, registry: SkillRegistry | None = None) -> dict[str, Any]:
    info = query_skill(name, registry=registry)
    if not info.get("ok"):
        return info
    skill = (registry or default_registry()).get(name)
    assert skill is not None
    if skill.type == "mcp":
        return {"ok": True, "name": name, "status": "configured", "detail": invoke_mcp(skill)}
    if skill.type == "rest":
        result = invoke_rest(skill)
        return {"ok": result.get("ok", False), "name": name, "status": "reachable" if result.get("ok") else "down", "detail": result}
    if skill.type == "python":
        try:
            importlib.import_module(skill.entry.split(":", 1)[0])
            return {"ok": True, "name": name, "status": "importable"}
        except Exception as exc:
            return {"ok": False, "name": name, "status": "error", "error": str(exc)}
    if skill.type == "cli":
        proc = subprocess.run(["which", skill.command], capture_output=True, text=True)
        return {"ok": proc.returncode == 0, "name": name, "status": "found" if proc.returncode == 0 else "missing"}
    if skill.type == "docker":
        proc = subprocess.run(["docker", "image", "inspect", skill.image], capture_output=True, text=True)
        return {"ok": proc.returncode == 0, "name": name, "status": "image_present" if proc.returncode == 0 else "missing"}
    return {"ok": False, "name": name, "error": "unknown type"}
