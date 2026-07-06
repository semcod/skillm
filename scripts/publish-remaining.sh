#!/usr/bin/env bash
# Upload remaining packages to PyPI (skip already published).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VERSION="$(tr -d '[:space:]' < "$ROOT/VERSION")"
DIST="$ROOT/dist"
REMAINING=(dsl2skillm uri2skillm cli2skillm mcp2skillm rest2skillm)

is_published() {
  local pkg=$1
  curl -sf "https://pypi.org/pypi/$pkg/$VERSION/json" >/dev/null 2>&1
}

for name in "${REMAINING[@]}"; do
  if is_published "$name"; then
    echo "skip $name (already on PyPI)"
    continue
  fi
  echo "==> waiting 120s before upload $name"
  sleep 120
  echo "==> upload $name"
  for attempt in 1 2 3; do
    if python3 -m twine upload --non-interactive "$DIST/${name}-${VERSION}"*; then
      echo "OK $name"
      break
    fi
    echo "attempt $attempt failed, wait 180s..."
    sleep 180
  done
if ! is_published "$name"; then
    echo "FAILED $name (PyPI may rate-limit new projects — retry in a few hours)" >&2
    exit 1
  fi
done

echo "==> all remaining packages published"
