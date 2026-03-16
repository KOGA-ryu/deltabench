from __future__ import annotations

import subprocess
from pathlib import Path

from .repo_mapper import map_path_to_subsystem


def load_git_diff(repo_root: Path, *, base: str, head: str) -> dict[str, object]:
    repo_root = repo_root.expanduser().resolve()
    diff_id = f"{_normalize_id(head)}_vs_{_normalize_id(base)}"
    name_status = _run_git(
        repo_root,
        ["git", "diff", "--name-status", "--find-renames", base, head],
    )
    numstat = _run_git(
        repo_root,
        ["git", "diff", "--numstat", "--find-renames", base, head],
    )
    counts_by_path = _parse_numstat(numstat)
    changed_files = []
    for line in name_status.splitlines():
        raw = line.strip()
        if not raw:
            continue
        parts = raw.split("\t")
        status_token = parts[0]
        if status_token.startswith("R") and len(parts) >= 3:
            path = parts[2]
            previous_path = parts[1]
            status = "renamed"
        else:
            path = parts[-1]
            previous_path = None
            status = _normalize_status(status_token)
        additions, deletions = counts_by_path.get(path, (0, 0))
        changed_files.append(
            {
                "path": path,
                "status": status,
                "additions": additions,
                "deletions": deletions,
                "subsystem": map_path_to_subsystem(path),
                "previous_path": previous_path,
            }
        )
    return {
        "schema_version": "1",
        "diff_id": diff_id,
        "base": base,
        "head": head,
        "files_changed": len(changed_files),
        "changed_files": changed_files,
    }


def _run_git(repo_root: Path, command: list[str]) -> str:
    completed = subprocess.run(
        command,
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or f"git command failed: {' '.join(command)}")
    return completed.stdout


def _parse_numstat(raw_output: str) -> dict[str, tuple[int, int]]:
    counts: dict[str, tuple[int, int]] = {}
    for line in raw_output.splitlines():
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        additions_raw, deletions_raw, path = parts[0], parts[1], parts[2]
        additions = int(additions_raw) if additions_raw.isdigit() else 0
        deletions = int(deletions_raw) if deletions_raw.isdigit() else 0
        counts[path] = (additions, deletions)
    return counts


def _normalize_status(token: str) -> str:
    lead = token[:1].upper()
    if lead == "A":
        return "added"
    if lead == "D":
        return "deleted"
    if lead == "M":
        return "modified"
    return "unknown"


def _normalize_id(value: str) -> str:
    return str(value).replace("/", "_").replace(" ", "_")
