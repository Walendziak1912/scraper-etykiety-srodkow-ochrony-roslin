from __future__ import annotations
import re
from re import Match, Pattern
from typing import Any, Union
RegexInput = Union[str, Pattern[str]]

def _as_pattern(pattern: RegexInput, flags: int) -> Pattern[str]:
    if isinstance(pattern, Pattern):
        return pattern
    return re.compile(pattern, flags)

def contains(text: str, pattern: RegexInput, flags: int = 0) -> bool:
    return _as_pattern(pattern, flags).search(text) is not None

def search(text: str, pattern: RegexInput, flags: int = 0) -> Match[str] | None:
    return _as_pattern(pattern, flags).search(text)

def find_first(text: str, pattern: RegexInput, flags: int = 0) -> str | None:
    m = _as_pattern(pattern, flags).search(text)
    return m.group(0) if m else None

def find_all(text: str, pattern: RegexInput, flags: int = 0) -> list[Any]:
    return _as_pattern(pattern, flags).findall(text)

def find_groups(text: str, pattern: RegexInput, flags: int = 0) -> tuple[str, ...] | None:
    m = _as_pattern(pattern, flags).search(text)
    return m.groups() if m else None
