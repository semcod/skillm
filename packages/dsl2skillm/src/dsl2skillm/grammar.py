"""Text DSL → dict."""

from __future__ import annotations

import shlex
from typing import Any


def split_command(line: str) -> list[str]:
    line = line.strip()
    if not line or line.startswith("#"):
        return []
    try:
        return shlex.split(line, posix=True)
    except ValueError:
        return line.split()


def pick_flag(tokens: list[str], flag: str) -> str | None:
    if flag in tokens:
        idx = tokens.index(flag)
        if idx + 1 < len(tokens):
            return tokens[idx + 1]
    return None


def parse_line(line: str) -> dict[str, Any] | None:
    tokens = split_command(line)
    if not tokens:
        return None
    verb = tokens[0].upper()
    rest = tokens[1:]
    cmd: dict[str, Any] = {"verb": verb}

    if verb == "LIST":
        if f := pick_flag(rest, "FILE"):
            cmd["file"] = f
    elif verb in {"QUERY", "HEALTH", "INVOKE", "PATCH"}:
        cmd["target"] = rest[0] if rest else ""
        if f := pick_flag(rest, "FILE"):
            cmd["file"] = f
        if verb == "INVOKE":
            if f := pick_flag(rest, "ARGS"):
                cmd["args_json"] = f
            if f := pick_flag(rest, "INPUT"):
                cmd["input_text"] = f
            if f := pick_flag(rest, "BODY"):
                cmd["body"] = f
        if verb == "PATCH":
            if f := pick_flag(rest, "WITH"):
                cmd["spec_json"] = f
    elif verb == "VALIDATE":
        cmd["path"] = rest[0] if rest else ""
    elif verb == "RESOLVE":
        cmd["text"] = " ".join(rest)
        if f := pick_flag(rest, "FILE"):
            cmd["file"] = f
    elif verb == "REGISTER":
        cmd["name"] = rest[0] if rest else ""
        if f := pick_flag(rest, "TYPE"):
            cmd["type"] = f.lower()
        if f := pick_flag(rest, "WITH"):
            cmd["spec_json"] = f
        if f := pick_flag(rest, "FILE"):
            cmd["file"] = f
    elif verb == "UNREGISTER":
        cmd["name"] = rest[0] if rest else ""
        if f := pick_flag(rest, "FILE"):
            cmd["file"] = f
    else:
        cmd["args"] = rest
    return cmd


def to_text(cmd: dict[str, Any]) -> str:
    verb = str(cmd.get("verb", "")).upper()
    parts = [verb]
    for key in ("target", "path", "text", "name"):
        if val := cmd.get(key):
            parts.append(f'"{val}"' if " " in str(val) else str(val))
    for key, flag in (
        ("file", "FILE"),
        ("type", "TYPE"),
        ("spec_json", "WITH"),
        ("args_json", "ARGS"),
        ("input_text", "INPUT"),
        ("body", "BODY"),
    ):
        if val := cmd.get(key):
            parts.extend([flag, str(val)])
    return " ".join(parts)
