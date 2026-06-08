"""Interactive REPL shell for skillm DSL."""

from __future__ import annotations

import json
import sys

from dsl2skillm import dispatch


def run_shell(*, default_file: str | None = None) -> int:
    print("skillm shell — enter DSL lines (Ctrl+D to exit)")
    while True:
        try:
            line = input("skillm> ").strip()
        except EOFError:
            print()
            return 0
        if not line:
            continue
        result = dispatch(line, default_file=default_file)
        print(result.output or json.dumps(result.to_dict(), ensure_ascii=False))
        if not result.ok:
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(run_shell())
