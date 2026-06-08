"""CLI for uri2skillm."""

from __future__ import annotations

import argparse
import json
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="uri2skillm")
    sub = parser.add_subparsers(dest="cmd", required=True)
    dec = sub.add_parser("decode")
    dec.add_argument("--uri", required=True)
    run = sub.add_parser("run")
    run.add_argument("--uri", required=True)
    run.add_argument("--file", default="")
    args = parser.parse_args(argv)
    from uri2skillm.decode import decode_uri, run_uri

    if args.cmd == "decode":
        print(decode_uri(args.uri))
        return 0
    result = run_uri(args.uri, default_file=args.file or None)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
