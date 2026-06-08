"""MCP adapter CLI."""

from __future__ import annotations

import argparse

from mcp2skillm.server import run_server


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="mcp2skillm")
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("serve")
    args = parser.parse_args(argv)
    if args.cmd == "serve" or args.cmd is None:
        run_server()
        return 0
    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
