"""Parity and dispatch tests."""

import json
from pathlib import Path

import yaml

from dsl2skillm import dispatch
from dsl2skillm.schema_registry import validate_schema_registry


def _write_manifest(tmp_path: Path) -> Path:
    manifest = tmp_path / "app.skillm.yaml"
    manifest.write_text(yaml.safe_dump({
        "version": "1",
        "skills": {
            "echo": {"type": "python", "entry": "skillm.examples.echo:run", "args": ["x"]},
        },
    }), encoding="utf-8")
    return manifest


def test_parity_text_vs_dict(tmp_path: Path) -> None:
    manifest = _write_manifest(tmp_path)
    line = f"VALIDATE {manifest}"
    r1 = dispatch(line)
    r2 = dispatch({"verb": "VALIDATE", "path": str(manifest)})
    assert r1.ok == r2.ok
    assert r1.action == r2.action


def test_list_and_invoke(tmp_path: Path) -> None:
    manifest = _write_manifest(tmp_path)
    listed = dispatch(f"LIST FILE {manifest}")
    assert listed.ok
    invoked = dispatch(f'INVOKE skillm://skill/echo FILE {manifest}')
    assert invoked.ok


def test_validate_schema_registry() -> None:
    assert validate_schema_registry() == []


def test_protobuf_roundtrip(tmp_path: Path) -> None:
    from dsl2skillm.pb_codec import decode_protobuf, encode_protobuf

    manifest = _write_manifest(tmp_path)
    cmd = {"verb": "VALIDATE", "path": str(manifest)}
    pb = encode_protobuf(cmd)
    decoded = decode_protobuf(pb)
    assert decoded["verb"] == "VALIDATE"
    result = dispatch(pb)
    assert result.action == "validate"
