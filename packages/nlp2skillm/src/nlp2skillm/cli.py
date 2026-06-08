"""CLI for nlp2skillm."""

from __future__ import annotations

import argparse
import json
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="nlp2skillm")
    sub = parser.add_subparsers(dest="cmd", required=True)
    to_dsl_p = sub.add_parser("to-dsl")
    to_dsl_p.add_argument("prompt")
    to_dsl_p.add_argument("--file", default="app.skillm.yaml")
    apply_p = sub.add_parser("apply")
    apply_p.add_argument("prompt")
    apply_p.add_argument("--file", default="app.skillm.yaml")
    args = parser.parse_args(argv)
    from nlp2skillm.to_dsl import apply_nl, to_dsl

    if args.cmd == "to-dsl":
        print(to_dsl(args.prompt, file=args.file))
        return 0
    result = apply_nl(args.prompt, file=args.file)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
