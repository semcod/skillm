"""EventStore — protobuf + jsonl."""

from __future__ import annotations

import json
import time
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal

from dsl2skillm.result import DslResult

StoreFormat = Literal["protobuf", "jsonl"]


@dataclass
class DslEvent:
    id: str
    ts_unix: int
    command: dict[str, Any]
    result: dict[str, Any]
    correlation_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class EventStore:
    def __init__(self, path: Path | str, *, fmt: StoreFormat | None = None) -> None:
        self.path = Path(path)
        if fmt is not None:
            self.fmt = fmt
        elif self.path.suffix == ".pb":
            self.fmt = "protobuf"
        else:
            self.fmt = "jsonl"

    def append(self, command: dict[str, Any], result: dict[str, Any], *, correlation_id: str = "") -> DslEvent:
        event = DslEvent(
            id=str(uuid.uuid4()),
            ts_unix=int(time.time()),
            command=command,
            result=result,
            correlation_id=correlation_id,
        )
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(event.to_dict(), ensure_ascii=False) + "\n")
        return event

    def replay(self) -> list[DslEvent]:
        if not self.path.is_file():
            return []
        events: list[DslEvent] = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            events.append(DslEvent(**data))
        return events


def default_event_store(manifest: str = "app.skillm.yaml") -> EventStore:
    stem = Path(manifest).stem
    return EventStore(Path(manifest).with_name(f"{stem}.events.jsonl"))
