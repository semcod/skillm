"""Skill manifest models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

SkillType = Literal["python", "docker", "cli", "rest", "mcp"]


@dataclass
class Skill:
    name: str
    type: SkillType
    description: str = ""
    command: str = ""
    args: list[str] = field(default_factory=list)
    entry: str = ""
    image: str = ""
    url: str = ""
    method: str = "GET"
    headers: dict[str, str] = field(default_factory=dict)
    body: str = ""
    transport: str = "stdio"
    env: dict[str, str] = field(default_factory=dict)
    extra: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, name: str, data: dict[str, Any]) -> Skill:
        return cls(
            name=name,
            type=str(data.get("type", "cli")),
            description=str(data.get("description", "")),
            command=str(data.get("command", "")),
            args=[str(a) for a in (data.get("args") or [])],
            entry=str(data.get("entry", "")),
            image=str(data.get("image", "")),
            url=str(data.get("url", "")),
            method=str(data.get("method", "GET")).upper(),
            headers={str(k): str(v) for k, v in (data.get("headers") or {}).items()},
            body=str(data.get("body", "")),
            transport=str(data.get("transport", "stdio")),
            env={str(k): str(v) for k, v in (data.get("env") or {}).items()},
            extra={k: v for k, v in data.items() if k not in {
                "type", "description", "command", "args", "entry", "image",
                "url", "method", "headers", "body", "transport", "env",
            }},
        )

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {"type": self.type}
        if self.description:
            out["description"] = self.description
        if self.command:
            out["command"] = self.command
        if self.args:
            out["args"] = self.args
        if self.entry:
            out["entry"] = self.entry
        if self.image:
            out["image"] = self.image
        if self.url:
            out["url"] = self.url
        if self.method != "GET":
            out["method"] = self.method
        if self.headers:
            out["headers"] = self.headers
        if self.body:
            out["body"] = self.body
        if self.transport != "stdio":
            out["transport"] = self.transport
        if self.env:
            out["env"] = self.env
        out.update(self.extra)
        return out

    def uri(self) -> str:
        return f"skillm://skill/{self.name}"


@dataclass
class Manifest:
    version: str = "1"
    skills: dict[str, Skill] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "skills": {name: skill.to_dict() for name, skill in sorted(self.skills.items())},
        }
