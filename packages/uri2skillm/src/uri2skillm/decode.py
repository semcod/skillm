"""Decode skillm://cmd/* URIs to DSL lines."""

from __future__ import annotations

from urllib.parse import parse_qs, urlparse

from dsl2skillm.grammar import to_text


def decode_uri(uri: str) -> str:
    parsed = urlparse(uri)
    if parsed.scheme != "skillm":
        raise ValueError(f"expected skillm:// URI, got {uri!r}")
    path = parsed.path.lstrip("/")
    if not path.startswith("cmd/"):
        raise ValueError(f"expected skillm://cmd/VERB, got {uri!r}")
    verb = path.split("/", 1)[1].upper()
    qs = parse_qs(parsed.query)
    cmd: dict[str, str] = {"verb": verb}
    for key in ("target", "file", "path", "text", "name", "type", "spec_json", "args_json", "input_text", "body"):
        if key in qs:
            cmd[key] = qs[key][0]
    return to_text(cmd)


def run_uri(uri: str, *, default_file: str | None = None) -> dict:
    from dsl2skillm import dispatch

    line = decode_uri(uri)
    return dispatch(line, default_file=default_file).to_dict()
