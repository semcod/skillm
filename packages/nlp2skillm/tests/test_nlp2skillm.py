"""Tests for nlp2skillm."""

from nlp2skillm.to_dsl import to_dsl


def test_to_dsl_list() -> None:
    line = to_dsl("list all skills")
    assert line.startswith("LIST")


def test_to_dsl_validate() -> None:
    line = to_dsl("validate manifest")
    assert line.startswith("VALIDATE")
