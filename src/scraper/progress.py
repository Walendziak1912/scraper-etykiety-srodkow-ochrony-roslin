from __future__ import annotations

import queue
from dataclasses import dataclass, field
from typing import Any

_events = None


@dataclass(frozen=True)
class DownloadEvent:
    kind: str
    message: str = ""
    range_slug: str = ""
    filename: str = ""
    stored_path: str = ""
    status: str = ""
    stats: dict[str, Any] = field(default_factory=dict)


def init_progress_queue(event_queue=None):
    global _events
    _events = event_queue if event_queue is not None else queue.Queue()
    return _events


def get_progress_queue():
    return _events


def clear_progress_queue() -> None:
    global _events
    _events = None


def emit(event: DownloadEvent) -> None:
    if _events is None:
        return
    _events.put(event)


def progress_enabled() -> bool:
    return _events is not None
