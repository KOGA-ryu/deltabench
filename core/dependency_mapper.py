from __future__ import annotations


def count_boundary_crossings(subsystems: list[str]) -> int:
    distinct = [item for item in dict.fromkeys(subsystems) if item]
    return max(0, len(distinct) - 1)
