"""Dual-mode CLI for dsl2skillm."""

from __future__ import annotations

import argparse
import json
import sys

from dsl2skillm import dispatch, execute_dsl
from dsl2skillm.pb_codec import decode_protobuf, encode_protobuf
from dsl2skillm.schema_registry import validate_schema_registry

_SUBCOMMANDS = frozenset({"validate-schema", "encode", "decode", "replay"})


def _main_legacy(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="dsl2skillm")
    parser.add_argument("-c", "--command", help="Single DSL command")
    parser.add_argument("script", nargs="?", help="DSL script file")
    parser.add_argument("--file", default="", help="Default manifest path")
    args = parser.parse_args(argv)
    default_file = args.file or None
    if args.command:
        result = dispatch(args.command, default_file=default_file)
        print(result.output or json.dumps(result.to_dict(), ensure_ascii=False))
        return 0 if result.ok else 1
    if args.script:
        from pathlib import Path
        text = Path(args.script).read_text(encoding="utf-8")
        failed = False
        for result in execute_dsl(text, default_file=default_file):
            print(result.output or json.dumps(result.to_dict(), ensure_ascii=False))
            failed = failed or not result.ok
        return 1 if failed else 0
    parser.print_help()
    return 2


def _main_subcommand(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="dsl2skillm")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("validate-schema")
    enc = sub.add_parser("encode")
    enc.add_argument("line")
    enc.add_argument("--format", choices=["protobuf", "json"], default="protobuf")
    dec = sub.add_parser("decode")
    dec.add_argument("--input", required=True)
    dec.add_argument("--format", choices=["protobuf", "json"], default="protobuf")
    rep = sub.add_parser("replay")
    rep.add_argument("--file", default="app.skillm.yaml")
    args = parser.parse_args(argv[1:])
    if args.cmd == "validate-schema":
        errors = validate_schema_registry()
        if errors:
            print("\n".join(errors), file=sys.stderr)
            return 1
        print("schema registry OK")
        return 0
    if args.cmd == "encode":
        from dsl2skillm.grammar import parse_line
        cmd = parse_line(args.line)
        if cmd is None:
            print("invalid DSL line", file=sys.stderr)
            return 1
        if args.format == "json":
            print(json.dumps(cmd))
        else:
            sys.stdout.buffer.write(encode_protobuf(cmd))
        return 0
    if args.cmd == "decode":
        data = open(args.input, "rb").read()
        if args.format == "json":
            print(json.dumps(json.loads(data.decode("utf-8")), indent=2))
        else:
            print(json.dumps(decode_protobuf(data), indent=2))
        return 0
    if args.cmd == "replay":
        from dsl2skillm.events import default_event_store
        for event in default_event_store(args.file).replay():
            print(json.dumps(event.to_dict(), ensure_ascii=False))
        return 0
    return 2


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] in _SUBCOMMANDS:
        return _main_subcommand(["dsl2skillm", *argv])
    return _main_legacy(argv)


if __name__ == "__main__":
    raise SystemExit(main())
