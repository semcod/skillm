"""Parse skillm:// URIs."""

from __future__ import annotations

from urllib.parse import parse_qs, urlparse


def skill_name_from_uri(uri: str) -> str:
    parsed = urlparse(uri)
    if parsed.scheme != "skillm":
        raise ValueError(f"expected skillm:// URI, got {uri!r}")
    path = parsed.path.lstrip("/")
    if path.startswith("skill/"):
        return path.split("/", 1)[1]
    if path.startswith("cmd/"):
        qs = parse_qs(parsed.query)
        target = (qs.get("target") or [""])[0]
        if target.startswith("skillm://skill/"):
            return target.split("/", 3)[-1]
    raise ValueError(f"cannot resolve skill name from {uri!r}")
