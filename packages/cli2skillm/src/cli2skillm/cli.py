"""CLI adapter for skillm control DSL."""

from __future__ import annotations

import argparse
import json
import sys

from cli2skillm.shell import run_shell
from dsl2skillm import dispatch, execute_dsl


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="cli2skillm")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("shell").add_argument("--file", default="app.skillm.yaml")
    exec_p = sub.add_parser("exec")
    exec_p.add_argument("command")
    exec_p.add_argument("--file", default="app.skillm.yaml")
    run_p = sub.add_parser("run")
    run_p.add_argument("script")
    run_p.add_argument("--file", default="app.skillm.yaml")
    args = parser.parse_args(argv)
    default_file = getattr(args, "file", None) or None
    if args.cmd == "shell":
        return run_shell(default_file=default_file)
    if args.cmd == "exec":
        result = dispatch(args.command, default_file=default_file)
        print(result.output or json.dumps(result.to_dict(), ensure_ascii=False))
        return 0 if result.ok else 1
    text = open(args.script, encoding="utf-8").read()
    failed = False
    for result in execute_dsl(text, default_file=default_file):
        print(result.output or json.dumps(result.to_dict(), ensure_ascii=False))
        failed = failed or not result.ok
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
