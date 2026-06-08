"""Tests for rest2skillm."""

from fastapi.testclient import TestClient

from rest2skillm.app import create_app


def test_health() -> None:
    client = TestClient(create_app())
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["service"] == "rest2skillm"
