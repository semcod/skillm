#!/usr/bin/env bash
# End-to-end smoke tests (offline-safe verbs).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
MANIFEST="$ROOT/app.skillm.yaml"

echo "==> VALIDATE"
cli2skillm exec "VALIDATE $MANIFEST"

echo "==> LIST"
cli2skillm exec "LIST FILE $MANIFEST"

echo "==> QUERY"
cli2skillm exec "QUERY skillm://skill/echo-python FILE $MANIFEST"

echo "==> INVOKE python"
cli2skillm exec "INVOKE skillm://skill/echo-python FILE $MANIFEST ARGS '[\"smoke\"]'" 

echo "==> INVOKE cli"
cli2skillm exec "INVOKE skillm://skill/echo-cli FILE $MANIFEST"

echo "==> nlp2skillm to-dsl"
nlp2skillm to-dsl "list all skills" --file "$MANIFEST"

echo "==> uri2skillm decode"
uri2skillm decode --uri "skillm://cmd/LIST?file=$MANIFEST"

echo "==> dsl2skillm validate-schema"
dsl2skillm validate-schema

echo "==> rest2skillm health (TestClient)"
python3 -c "
from fastapi.testclient import TestClient
from rest2skillm.app import create_app
r = TestClient(create_app()).get('/health')
assert r.status_code == 200, r.text
print('rest health OK')
"

echo "==> mcp2skillm server init"
python3 -c "
from mcp2skillm.server import create_server
assert create_server().name == 'skillm'
print('mcp server OK')
"

echo "==> all smoke tests passed"
