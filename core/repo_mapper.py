from __future__ import annotations

from pathlib import Path


def map_path_to_subsystem(path: str) -> str:
    normalized = Path(path).as_posix().strip("./")
    if not normalized:
        return "root"
    first = normalized.split("/", 1)[0]
    if first in {"tests", "test"}:
        return "tests"
    return first
