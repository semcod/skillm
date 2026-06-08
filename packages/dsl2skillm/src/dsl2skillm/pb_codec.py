"""Dict ↔ protobuf DslEnvelope / DslResult."""

from __future__ import annotations

import json
from typing import Any

from dsl2skillm.grammar import parse_line, to_text
from dsl2skillm.result import DslResult
from dsl2skillm.v1 import command_pb2, result_pb2

_BODY_MAP = {
    "LIST": "list",
    "QUERY": "query",
    "VALIDATE": "validate",
    "HEALTH": "health",
    "RESOLVE": "resolve",
    "REGISTER": "register",
    "UNREGISTER": "unregister",
    "INVOKE": "invoke",
    "PATCH": "patch",
}


def _set_body(envelope: command_pb2.DslEnvelope, cmd: dict[str, Any]) -> None:
    verb = str(cmd.get("verb", "")).upper()
    field = _BODY_MAP.get(verb)
    if not field:
        return
    msg = getattr(envelope, field)
    if verb == "QUERY":
        msg.target = str(cmd.get("target", ""))
        msg.file = str(cmd.get("file", ""))
    elif verb == "VALIDATE":
        msg.path = str(cmd.get("path", ""))
    elif verb == "HEALTH":
        msg.target = str(cmd.get("target", ""))
        msg.file = str(cmd.get("file", ""))
    elif verb == "RESOLVE":
        msg.text = str(cmd.get("text", ""))
        msg.file = str(cmd.get("file", ""))
    elif verb == "REGISTER":
        msg.name = str(cmd.get("name", ""))
        msg.type = str(cmd.get("type", ""))
        msg.spec_json = str(cmd.get("spec_json", ""))
        msg.file = str(cmd.get("file", ""))
    elif verb == "UNREGISTER":
        msg.name = str(cmd.get("name", ""))
        msg.file = str(cmd.get("file", ""))
    elif verb == "INVOKE":
        msg.target = str(cmd.get("target", ""))
        msg.args_json = str(cmd.get("args_json", ""))
        msg.input_text = str(cmd.get("input_text", ""))
        msg.body = str(cmd.get("body", ""))
        msg.file = str(cmd.get("file", ""))
    elif verb == "PATCH":
        msg.target = str(cmd.get("target", ""))
        msg.spec_json = str(cmd.get("spec_json", ""))
        msg.file = str(cmd.get("file", ""))


def envelope_to_dict(envelope: command_pb2.DslEnvelope) -> dict[str, Any]:
    verb = envelope.verb.upper()
    cmd: dict[str, Any] = {"verb": verb}
    field = _BODY_MAP.get(verb)
    if not field or envelope.WhichOneof("body") != field:
        return cmd
    msg = getattr(envelope, field)
    if verb == "QUERY":
        if msg.target:
            cmd["target"] = msg.target
        if msg.file:
            cmd["file"] = msg.file
    elif verb == "VALIDATE" and msg.path:
        cmd["path"] = msg.path
    elif verb == "HEALTH":
        if msg.target:
            cmd["target"] = msg.target
        if msg.file:
            cmd["file"] = msg.file
    elif verb == "RESOLVE":
        if msg.text:
            cmd["text"] = msg.text
        if msg.file:
            cmd["file"] = msg.file
    elif verb == "REGISTER":
        if msg.name:
            cmd["name"] = msg.name
        if msg.type:
            cmd["type"] = msg.type
        if msg.spec_json:
            cmd["spec_json"] = msg.spec_json
        if msg.file:
            cmd["file"] = msg.file
    elif verb == "UNREGISTER":
        if msg.name:
            cmd["name"] = msg.name
        if msg.file:
            cmd["file"] = msg.file
    elif verb == "INVOKE":
        if msg.target:
            cmd["target"] = msg.target
        if msg.args_json:
            cmd["args_json"] = msg.args_json
        if msg.input_text:
            cmd["input_text"] = msg.input_text
        if msg.body:
            cmd["body"] = msg.body
        if msg.file:
            cmd["file"] = msg.file
    elif verb == "PATCH":
        if msg.target:
            cmd["target"] = msg.target
        if msg.spec_json:
            cmd["spec_json"] = msg.spec_json
        if msg.file:
            cmd["file"] = msg.file
    return cmd


def encode_protobuf(cmd: dict[str, Any], *, correlation_id: str = "", default_file: str = "") -> bytes:
    envelope = command_pb2.DslEnvelope()
    envelope.verb = str(cmd.get("verb", "")).upper()
    if default_file:
        envelope.default_file = default_file
    if correlation_id:
        envelope.correlation_id = correlation_id
    _set_body(envelope, cmd)
    return envelope.SerializeToString()


def decode_protobuf(data: bytes) -> dict[str, Any]:
    envelope = command_pb2.DslEnvelope()
    envelope.ParseFromString(data)
    return envelope_to_dict(envelope)


def result_to_pb(result: DslResult) -> result_pb2.DslResult:
    pb = result_pb2.DslResult()
    pb.ok = result.ok
    pb.verb = result.action.upper()
    pb.output = result.output
    pb.data_json = json.dumps(result.data, ensure_ascii=False).encode("utf-8")
    if result.error:
        pb.error = result.error
    if result.event_id:
        pb.event_id = result.event_id
    return pb


def encode_result_protobuf(result: DslResult) -> bytes:
    return result_to_pb(result).SerializeToString()


def decode_line_or_pb(data: bytes) -> tuple[dict[str, Any], str]:
    try:
        cmd = decode_protobuf(data)
        return cmd, to_text(cmd)
    except Exception:
        line = data.decode("utf-8").strip()
        cmd = parse_line(line)
        if cmd is None:
            return {"verb": "NOOP"}, line
        return cmd, line
