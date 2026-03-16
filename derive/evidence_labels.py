from __future__ import annotations


def label(kind: str, key: str, value) -> dict[str, object]:
    return {"type": kind, "key": key, "value": value}
