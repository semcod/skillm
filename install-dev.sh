#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

ORDER=(
  packages/skillm
  packages/nlp2skillm
  packages/dsl2skillm
  packages/uri2skillm
  packages/cli2skillm
  packages/mcp2skillm
  packages/rest2skillm
)

for pkg in "${ORDER[@]}"; do
  echo "==> pip install -e $pkg"
  pip install -e "$pkg"[dev] -q
done

if [ -f packages/dsl2skillm/scripts/generate-proto.sh ]; then
  echo "==> generate protobuf"
  pip install grpcio-tools -q
  bash packages/dsl2skillm/scripts/generate-proto.sh
  touch packages/dsl2skillm/src/dsl2skillm/v1/__init__.py
fi

echo "==> done"
