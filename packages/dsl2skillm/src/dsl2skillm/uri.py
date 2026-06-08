"""Parse skillm:// URIs."""

from __future__ import annotations

from urllib.parse import parse_qs, urlparse


def _path_parts(uri: str) -> list[str]:
    parsed = urlparse(uri)
    if parsed.scheme != "skillm":
        raise ValueError(f"expected skillm:// URI, got {uri!r}")
    if parsed.netloc:
        tail = parsed.path.lstrip("/")
        rest = tail.split("/") if tail else []
        return [parsed.netloc, *rest]
    return [p for p in parsed.path.lstrip("/").split("/") if p]


def skill_name_from_uri(uri: str) -> str:
    parts = _path_parts(uri)
    if parts and parts[0] == "skill" and len(parts) >= 2:
        return parts[1]
    parsed = urlparse(uri)
    if parsed.path.startswith("/skill/"):
        return parsed.path.split("/", 2)[2]
    qs = parse_qs(parsed.query)
    target = (qs.get("target") or [""])[0]
    if target:
        return skill_name_from_uri(target)
    raise ValueError(f"cannot resolve skill name from {uri!r}")
