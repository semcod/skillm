"""CQRS bus — single dispatch entry point."""

from __future__ import annotations

from typing import Any

from dsl2skillm.events import default_event_store
from dsl2skillm.grammar import parse_line, split_command, to_text
from dsl2skillm.handlers.command import handle_invoke, handle_patch, handle_register, handle_unregister
from dsl2skillm.handlers.query import handle_health, handle_list, handle_query, handle_resolve, handle_validate
from dsl2skillm.result import DslResult
from dsl2skillm.schema_registry import validate_command_dict

QUERY_VERBS = frozenset({"LIST", "QUERY", "VALIDATE", "HEALTH", "RESOLVE"})
COMMAND_VERBS = frozenset({"REGISTER", "UNREGISTER", "INVOKE", "PATCH"})


def handle_from_tokens(line: str, tokens: list[str], *, default_file: str | None = None) -> DslResult:
    cmd = parse_line(line) or {"verb": tokens[0].upper()}
    verb = str(cmd.get("verb", "")).upper()
    if verb == "LIST":
        return handle_list(cmd, line=line, default_file=default_file)
    if verb == "QUERY":
        return handle_query(cmd, line=line, default_file=default_file)
    if verb == "VALIDATE":
        return handle_validate(cmd, line=line, default_file=default_file)
    if verb == "HEALTH":
        return handle_health(cmd, line=line, default_file=default_file)
    if verb == "RESOLVE":
        return handle_resolve(cmd, line=line, default_file=default_file)
    if verb == "REGISTER":
        return handle_register(cmd, line=line, default_file=default_file)
    if verb == "UNREGISTER":
        return handle_unregister(cmd, line=line, default_file=default_file)
    if verb == "INVOKE":
        return handle_invoke(cmd, line=line, default_file=default_file)
    if verb == "PATCH":
        return handle_patch(cmd, line=line, default_file=default_file)
    return DslResult(ok=False, command=line, action=verb.lower(), error=f"unknown verb: {verb}")


def _dispatch_cmd(cmd: dict[str, Any], *, line: str, default_file: str | None = None) -> DslResult:
    verb = str(cmd.get("verb", "")).upper()
    errors = validate_command_dict(cmd)
    if errors:
        return DslResult(ok=False, command=line, action=verb.lower(), error="; ".join(errors))
    tokens = split_command(line)
    result = handle_from_tokens(line, tokens, default_file=default_file)
    if verb in COMMAND_VERBS and result.ok:
        manifest = cmd.get("file") or default_file or "app.skillm.yaml"
        store = default_event_store(manifest)
        event = store.append(cmd, result.to_dict())
        result.event_id = event.id
    return result


def _bytes_to_cmd(data: bytes) -> tuple[dict[str, Any], str]:
    from dsl2skillm.pb_codec import decode_protobuf

    try:
        cmd = decode_protobuf(data)
        return cmd, to_text(cmd)
    except Exception:
        line = data.decode("utf-8").strip()
        cmd = parse_line(line)
        if cmd is None:
            return {"verb": "NOOP"}, line
        return cmd, line


def dispatch(
    envelope: str | dict[str, Any] | bytes,
    *,
    default_file: str | None = None,
) -> DslResult:
    if isinstance(envelope, bytes):
        cmd, line = _bytes_to_cmd(envelope)
        if cmd.get("verb") == "NOOP":
            return DslResult(ok=True, command=line, action="noop")
        return _dispatch_cmd(cmd, line=line, default_file=default_file)
    if isinstance(envelope, dict):
        line = to_text(envelope)
        return _dispatch_cmd(envelope, line=line, default_file=default_file)
    line = str(envelope).strip()
    tokens = split_command(line)
    if not tokens:
        return DslResult(ok=True, command=line, action="noop")
    cmd = parse_line(line) or {"verb": tokens[0].upper()}
    return _dispatch_cmd(cmd, line=line, default_file=default_file)


def execute_dsl_line(line: str, *, default_file: str | None = None) -> DslResult:
    return dispatch(line, default_file=default_file)


def execute_dsl(text: str, *, default_file: str | None = None) -> list[DslResult]:
    results: list[DslResult] = []
    for line in text.splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        results.append(execute_dsl_line(line, default_file=default_file))
    return results
