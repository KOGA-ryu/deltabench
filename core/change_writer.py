from __future__ import annotations

from pathlib import Path

from evidence.store.artifact_store import ArtifactStore


def write_diff_evidence(repo_root: Path, evidence: dict[str, object], store: ArtifactStore | None = None) -> Path:
    artifact_store = store or ArtifactStore(repo_root)
    return artifact_store.write_diff_evidence(evidence)
