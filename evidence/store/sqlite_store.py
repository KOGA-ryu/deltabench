from __future__ import annotations

from pathlib import Path


class SqliteStore:
    """Placeholder for future indexed evidence storage."""

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root.expanduser().resolve()
        self.path = self.repo_root / ".deltabench" / "evidence.sqlite3"
