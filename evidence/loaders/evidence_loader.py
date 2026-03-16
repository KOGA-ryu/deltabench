from __future__ import annotations

from pathlib import Path

from evidence.store.artifact_store import ArtifactStore


def load_saved_diff_evidence(repo_root: Path, diff_id: str) -> dict[str, object]:
    return ArtifactStore(repo_root).load_diff_evidence(diff_id)
