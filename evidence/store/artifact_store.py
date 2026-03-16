from __future__ import annotations

import json
from pathlib import Path


class ArtifactStore:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root.expanduser().resolve()
        self.root = self.repo_root / ".deltabench"
        self.root.mkdir(parents=True, exist_ok=True)

    def write_diff_evidence(self, evidence: dict[str, object]) -> Path:
        diff_id = str(evidence.get("diff_id") or "diff")
        path = self.root / f"{diff_id}_evidence.json"
        path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return path

    def load_diff_evidence(self, diff_id: str) -> dict[str, object]:
        path = self.root / f"{diff_id}_evidence.json"
        return json.loads(path.read_text(encoding="utf-8"))
