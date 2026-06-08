"""Backward-compatible shim."""

from dsl2skillm.bus import dispatch, execute_dsl, execute_dsl_line

__all__ = ["dispatch", "execute_dsl", "execute_dsl_line"]
