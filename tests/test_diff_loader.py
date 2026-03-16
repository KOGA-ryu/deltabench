from __future__ import annotations

import tempfile
from pathlib import Path
import subprocess
import unittest

from core.diff_loader import load_git_diff


class DiffLoaderTests(unittest.TestCase):
    def test_load_git_diff_emits_canonical_raw_evidence(self) -> None:
        with _sample_repo() as repo_root:
            evidence = load_git_diff(repo_root, base="main", head="feature-x")

        self.assertEqual(evidence["schema_version"], "1")
        self.assertEqual(evidence["base"], "main")
        self.assertEqual(evidence["head"], "feature-x")
        self.assertEqual(evidence["files_changed"], 2)
        changed = {item["path"]: item for item in evidence["changed_files"]}
        self.assertEqual(changed["engine/scanner_engine.py"]["subsystem"], "engine")
        self.assertEqual(changed["tests/test_engine.py"]["subsystem"], "tests")


class _sample_repo:
    def __init__(self) -> None:
        self.tmp_dir: tempfile.TemporaryDirectory[str] | None = None
        self.root: Path | None = None

    def __enter__(self) -> Path:
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp_dir.name)
        _git(self.root, ["git", "init", "-b", "main"])
        _git(self.root, ["git", "config", "user.email", "test@example.com"])
        _git(self.root, ["git", "config", "user.name", "DeltaBench Test"])
        (self.root / "engine").mkdir(parents=True, exist_ok=True)
        (self.root / "tests").mkdir(parents=True, exist_ok=True)
        (self.root / "engine" / "scanner_engine.py").write_text("def scan():\n    return []\n", encoding="utf-8")
        (self.root / "README.md").write_text("base\n", encoding="utf-8")
        _git(self.root, ["git", "add", "."])
        _git(self.root, ["git", "commit", "-m", "base"])
        _git(self.root, ["git", "checkout", "-b", "feature-x"])
        (self.root / "engine" / "scanner_engine.py").write_text("def scan():\n    return ['changed']\n", encoding="utf-8")
        (self.root / "tests" / "test_engine.py").write_text("def test_scan():\n    assert True\n", encoding="utf-8")
        _git(self.root, ["git", "add", "."])
        _git(self.root, ["git", "commit", "-m", "feature"])
        return self.root

    def __exit__(self, exc_type, exc, tb) -> None:
        assert self.tmp_dir is not None
        self.tmp_dir.cleanup()


def _git(repo_root: Path, command: list[str]) -> None:
    completed = subprocess.run(command, cwd=str(repo_root), capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr)


if __name__ == "__main__":
    unittest.main()
