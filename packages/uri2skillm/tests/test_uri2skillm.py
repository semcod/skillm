"""Tests for uri2skillm."""

from uri2skillm.decode import decode_uri


def test_decode_invoke_uri() -> None:
    line = decode_uri("skillm://cmd/INVOKE?target=skillm://skill/echo&file=app.skillm.yaml")
    assert "INVOKE" in line
    assert "skillm://skill/echo" in line
