# mcp2skillm

MCP server (stdio) exposing `skillm_run_command`, `skillm_invoke`, legacy granular tools.

Start: `mcp2skillm serve`

List, query and health tools remain read-only. Invoking Python, Docker, CLI,
REST or MCP skills (including execution through DSL/NL tools) is disabled unless
the server is started with `SKILLM_MCP_ALLOW_INVOKE=1`.
