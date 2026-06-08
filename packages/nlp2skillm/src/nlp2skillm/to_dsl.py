"""NL → DSL for skillm (no side effects)."""

from __future__ import annotations

import re

from skillm.registry import default_registry


def _to_text(cmd: dict) -> str:
    verb = str(cmd.get("verb", "")).upper()
    parts = [verb]
    for key in ("target", "path", "text", "name"):
        if val := cmd.get(key):
            parts.append(f'"{val}"' if " " in str(val) else str(val))
    for key, flag in (("file", "FILE"), ("type", "TYPE"), ("spec_json", "WITH")):
        if val := cmd.get(key):
            parts.extend([flag, str(val)])
    return " ".join(parts)


def _intent(text: str) -> str:
    t = text.lower().strip()
    if re.search(r"\b(list|pokaż|show|wypisz)\b.*\bskill", t):
        return "list"
    if re.search(r"\b(validate|sprawdź|waliduj)\b", t):
        return "validate"
    if re.search(r"\b(health|status|zdrowie)\b", t):
        return "health"
    if re.search(r"\b(invoke|run|wywołaj|uruchom|call)\b", t):
        return "invoke"
    if re.search(r"\b(register|dodaj|add)\b", t):
        return "register"
    return "resolve"


def to_dsl(prompt: str, *, file: str = "app.skillm.yaml") -> str:
    intent = _intent(prompt)
    if intent == "list":
        return _to_text({"verb": "LIST", "file": file})
    if intent == "validate":
        return _to_text({"verb": "VALIDATE", "path": file})
    if intent == "health":
        name = _extract_skill_name(prompt)
        if name:
            return _to_text({"verb": "HEALTH", "target": f"skillm://skill/{name}", "file": file})
    if intent == "invoke":
        name = _extract_skill_name(prompt)
        if name:
            return _to_text({"verb": "INVOKE", "target": f"skillm://skill/{name}", "file": file})
    return _to_text({"verb": "RESOLVE", "text": prompt, "file": file})


def apply_nl(prompt: str, *, file: str = "app.skillm.yaml") -> dict:
    from dsl2skillm import dispatch

    line = to_dsl(prompt, file=file)
    return dispatch(line, default_file=file).to_dict()


def resolve_skills(prompt: str, *, file: str = "app.skillm.yaml") -> list[dict]:
    reg = default_registry(file)
    hits: list[dict] = []
    q = prompt.lower()
    for skill in reg.list_skills():
        hay = f"{skill.name} {skill.description} {skill.type}".lower()
        if q in hay or any(tok in hay for tok in q.split() if len(tok) > 2):
            hits.append({"name": skill.name, "uri": skill.uri(), "type": skill.type, "description": skill.description})
    return hits


def _extract_skill_name(prompt: str) -> str | None:
    reg = default_registry()
    for skill in reg.list_skills():
        if skill.name.lower() in prompt.lower():
            return skill.name
    m = re.search(r"skill[:\s]+([a-zA-Z0-9_-]+)", prompt, re.I)
    return m.group(1) if m else None
