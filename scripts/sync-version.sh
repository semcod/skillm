#!/usr/bin/env bash
# Sync version from root VERSION file into all package pyproject.toml files.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VERSION="$(tr -d '[:space:]' < "$ROOT/VERSION")"

for toml in "$ROOT/skillm/pyproject.toml" "$ROOT"/packages/*/pyproject.toml; do
  python3 - "$toml" "$VERSION" <<'PY'
import re, sys
path, version = sys.argv[1], sys.argv[2]
text = open(path, encoding="utf-8").read()
text = re.sub(r'^version = ".*"$', f'version = "{version}"', text, count=1, flags=re.M)
text = re.sub(r'"skillm>=[^"]+"', f'"skillm>={version}"', text)
text = re.sub(r'"nlp2skillm>=[^"]+"', f'"nlp2skillm>={version}"', text)
text = re.sub(r'"dsl2skillm>=[^"]+"', f'"dsl2skillm>={version}"', text)
text = re.sub(r'"uri2skillm>=[^"]+"', f'"uri2skillm>={version}"', text)
text = re.sub(r'"cli2skillm>=[^"]+"', f'"cli2skillm>={version}"', text)
text = re.sub(r'"mcp2skillm>=[^"]+"', f'"mcp2skillm>={version}"', text)
text = re.sub(r'"rest2skillm>=[^"]+"', f'"rest2skillm>={version}"', text)
open(path, "w", encoding="utf-8").write(text)
print(f"  {path}: {version}")
PY
done

echo "Synced version $VERSION"
