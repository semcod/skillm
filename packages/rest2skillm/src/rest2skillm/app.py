"""FastAPI app — text/json/protobuf DSL dispatch."""

from __future__ import annotations

import json
from pathlib import Path

from dsl2skillm import dispatch
from dsl2skillm.events import default_event_store
from dsl2skillm.pb_codec import encode_result_protobuf
from dsl2skillm.schema_registry import all_schemas, schema_for_verb

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse, Response

_PROTO_DIR = Path(__file__).resolve().parents[3] / "dsl2skillm" / "proto" / "dsl2skillm" / "v1"


def create_app() -> FastAPI:
    app = FastAPI(title="rest2skillm", version="0.1.0")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "rest2skillm"}

    @app.get("/v1/schema/{verb}")
    def get_schema(verb: str) -> JSONResponse:
        schema = schema_for_verb(verb)
        if schema is None:
            return JSONResponse({"error": f"unknown verb: {verb}"}, status_code=404)
        return JSONResponse(schema)

    @app.get("/v1/schema")
    def list_schemas() -> JSONResponse:
        return JSONResponse(all_schemas())

    @app.get("/v1/proto")
    def list_proto() -> JSONResponse:
        files = {p.name: p.read_text(encoding="utf-8") for p in sorted(_PROTO_DIR.glob("*.proto"))} if _PROTO_DIR.is_dir() else {}
        return JSONResponse({"package": "dsl2skillm.v1", "files": files})

    @app.get("/v1/events")
    def list_events(file: str = "app.skillm.yaml") -> JSONResponse:
        return JSONResponse([e.to_dict() for e in default_event_store(file).replay()])

    async def _handle(request: Request, default_file: str = "") -> Response:
        ct = request.headers.get("content-type", "text/plain").split(";")[0].strip()
        body = await request.body()
        if ct == "application/json":
            result = dispatch(json.loads(body.decode("utf-8")), default_file=default_file or None)
        elif ct == "application/x-protobuf":
            result = dispatch(body, default_file=default_file or None)
            return Response(encode_result_protobuf(result), media_type="application/x-protobuf")
        else:
            result = dispatch(body.decode("utf-8").strip(), default_file=default_file or None)
        if ct == "text/plain":
            return PlainTextResponse(result.output or json.dumps(result.to_dict(), ensure_ascii=False))
        return JSONResponse(result.to_dict())

    @app.post("/v1/dsl")
    async def post_dsl(request: Request, file: str = "") -> Response:
        return await _handle(request, default_file=file)

    @app.post("/v1/commands")
    async def post_commands(request: Request, file: str = "") -> Response:
        return await _handle(request, default_file=file)

    return app
