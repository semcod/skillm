#!/usr/bin/env bash
# Build and publish all skillm packages to PyPI (dependency order).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VERSION="$(tr -d '[:space:]' < "$ROOT/VERSION")"
DIST="$ROOT/dist"
ORDER=(
  skillm
  nlp2skillm
  dsl2skillm
  uri2skillm
  cli2skillm
  mcp2skillm
  rest2skillm
)

bash "$ROOT/scripts/sync-version.sh"
bash "$ROOT/install-dev.sh"
python3 -m pytest "$ROOT/skillm/tests" "$ROOT/packages/" -q

rm -rf "$DIST"
mkdir -p "$DIST"
python3 -m pip install -q build twine

for name in "${ORDER[@]}"; do
  if [[ "$name" == "skillm" ]]; then
    pkg="$ROOT/skillm"
  else
    pkg="$ROOT/packages/$name"
  fi
  echo "==> build $name"
  (cd "$pkg" && python3 -m build --outdir "$DIST")
done

echo "==> dist contents"
ls -la "$DIST"

if [[ "${1:-}" == "--dry-run" ]]; then
  echo "Dry run — skipping upload"
  exit 0
fi

for name in "${ORDER[@]}"; do
  echo "==> upload $name (waiting 90s for PyPI rate limit)"
  sleep 90
  if [[ -n "${PYPI_TOKEN:-}" ]]; then
    python3 -m twine upload --non-interactive \
      -u __token__ -p "$PYPI_TOKEN" \
      "$DIST/${name}-${VERSION}"* || {
        echo "retry $name in 120s..."
        sleep 120
        python3 -m twine upload --non-interactive \
          -u __token__ -p "$PYPI_TOKEN" \
          "$DIST/${name}-${VERSION}"*
      }
  else
    python3 -m twine upload --non-interactive "$DIST/${name}-${VERSION}"* || {
        echo "retry $name in 120s..."
        sleep 120
        python3 -m twine upload --non-interactive "$DIST/${name}-${VERSION}"*
      }
  fi
done

echo "==> published $VERSION"
for name in "${ORDER[@]}"; do
  echo "  https://pypi.org/project/$name/$VERSION/"
done
