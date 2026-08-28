"""Smoke and safety tests for mcp2skillm."""

import pytest

from mcp2skillm.server import _require_invoke, create_server


def test_create_server() -> None:
    server = create_server()
    assert server.name == "skillm"


def test_mcp_invocation_requires_operator_capability(monkeypatch) -> None:
    monkeypatch.delenv("SKILLM_MCP_ALLOW_INVOKE", raising=False)
    with pytest.raises(PermissionError, match="SKILLM_MCP_ALLOW_INVOKE"):
        _require_invoke("skillm_invoke")

    monkeypatch.setenv("SKILLM_MCP_ALLOW_INVOKE", "true")
    _require_invoke("skillm_invoke")
