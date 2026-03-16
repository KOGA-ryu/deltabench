from __future__ import annotations

from pathlib import Path

from core.diff_loader import load_git_diff


def load_diff_evidence(repo_root: Path, *, base: str, head: str) -> dict[str, object]:
    return load_git_diff(repo_root, base=base, head=head)
