"""Smoke test for mcp2skillm."""

from mcp2skillm.server import create_server


def test_create_server() -> None:
    server = create_server()
    assert server.name == "skillm"
