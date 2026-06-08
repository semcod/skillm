"""FastMCP server exposing skillm control tools."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any


def _require_fastmcp():
    try:
        from mcp.server.fastmcp import FastMCP
        return FastMCP
    except ImportError as exc:
        raise RuntimeError(
            "MCP support requires optional dependency 'mcp'. Install with: pip install mcp",
        ) from exc


@dataclass
class SkillmMCPServer:
    """Expose skill registry and invocation via MCP tools."""

    name: str = "skillm"

    def __post_init__(self) -> None:
        FastMCP = _require_fastmcp()
        self.app = FastMCP(self.name)
        self._register_tools()

    def _register_tools(self) -> None:
        from dsl2skillm import dispatch, execute_dsl, execute_dsl_line
        from dsl2skillm.pb_codec import encode_result_protobuf
        from nlp2skillm.to_dsl import apply_nl, to_dsl
        from skillm.invoke import health_skill, invoke_skill, list_skills, query_skill

        @self.app.tool()
        def skillm_list(file: str = "app.skillm.yaml") -> dict[str, Any]:
            """List registered skills from manifest."""
            return list_skills()

        @self.app.tool()
        def skillm_query(name: str, file: str = "app.skillm.yaml") -> dict[str, Any]:
            """Query metadata for a skill by name."""
            return query_skill(name)

        @self.app.tool()
        def skillm_invoke(
            name: str,
            args_json: str = "[]",
            input_text: str = "",
            body: str = "",
            file: str = "app.skillm.yaml",
        ) -> dict[str, Any]:
            """Invoke a registered skill (python, docker, cli, rest, mcp)."""
            import json as _json
            return invoke_skill(name, args=_json.loads(args_json or "[]"), input_text=input_text, body=body)

        @self.app.tool()
        def skillm_health(name: str, file: str = "app.skillm.yaml") -> dict[str, Any]:
            """Check health/reachability of a skill."""
            return health_skill(name)

        @self.app.tool()
        def skillm_run_dsl(script: str, default_file: str = "app.skillm.yaml") -> list[dict[str, Any]]:
            """Execute skillm control DSL commands (one per line)."""
            results = execute_dsl(script, default_file=default_file or None)
            return [r.to_dict() for r in results]

        @self.app.tool()
        def skillm_run_command(command: str, default_file: str = "app.skillm.yaml") -> dict[str, Any]:
            """Execute a single skillm control DSL command."""
            result = execute_dsl_line(command, default_file=default_file or None)
            return result.to_dict()

        @self.app.tool()
        def skillm_run_command_pb(envelope_bytes: bytes, default_file: str = "app.skillm.yaml") -> bytes:
            """Execute protobuf DslEnvelope; returns DslResult protobuf."""
            result = dispatch(envelope_bytes, default_file=default_file or None)
            return encode_result_protobuf(result)

        @self.app.tool()
        def skillm_to_dsl(prompt: str, file: str = "app.skillm.yaml") -> str:
            """Convert NL hint to DSL line (no side effects)."""
            return to_dsl(prompt, file=file)

        @self.app.tool()
        def skillm_apply_nl(prompt: str, file: str = "app.skillm.yaml") -> dict[str, Any]:
            """Apply natural-language skillm control (list/validate/invoke/resolve)."""
            return apply_nl(prompt, file=file)

    def run(self) -> None:
        self.app.run()


def create_server(name: str = "skillm") -> SkillmMCPServer:
    return SkillmMCPServer(name=name)


def run_server() -> None:
    create_server().run()


if __name__ == "__main__":
    run_server()
