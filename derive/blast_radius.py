from __future__ import annotations

from core.dependency_mapper import count_boundary_crossings


def estimate_blast_radius(diff_evidence: dict[str, object]) -> dict[str, int]:
    changed_files = list(diff_evidence.get("changed_files") or [])
    subsystems = [str(item.get("subsystem") or "") for item in changed_files if isinstance(item, dict)]
    boundary_crossings = count_boundary_crossings(subsystems)
    return {
        "subsystems_touched": len({item for item in subsystems if item}),
        "boundary_crossings": boundary_crossings,
    }
