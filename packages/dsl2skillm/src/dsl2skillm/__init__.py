"""skillm control DSL."""

from dsl2skillm.bus import dispatch, execute_dsl, execute_dsl_line
from dsl2skillm.result import DslResult

__all__ = ["DslResult", "dispatch", "execute_dsl", "execute_dsl_line"]
