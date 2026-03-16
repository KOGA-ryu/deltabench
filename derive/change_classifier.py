from __future__ import annotations


def classify_change(diff_evidence: dict[str, object]) -> dict[str, object]:
    changed_files = [item for item in list(diff_evidence.get("changed_files") or []) if isinstance(item, dict)]
    tests_touched = any(str(item.get("subsystem") or "") == "tests" for item in changed_files)
    code_subsystems = {str(item.get("subsystem") or "") for item in changed_files if str(item.get("subsystem") or "") != "tests"}
    return {
        "tests_touched": tests_touched,
        "code_subsystems_touched": len({item for item in code_subsystems if item}),
    }
