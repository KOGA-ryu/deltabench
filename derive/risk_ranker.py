from __future__ import annotations

from derive.blast_radius import estimate_blast_radius
from derive.change_classifier import classify_change


def rank_diff_risk(diff_evidence: dict[str, object]) -> dict[str, object]:
    changed_files = [item for item in list(diff_evidence.get("changed_files") or []) if isinstance(item, dict)]
    file_count = len(changed_files)
    additions = sum(int(item.get("additions", 0) or 0) for item in changed_files)
    deletions = sum(int(item.get("deletions", 0) or 0) for item in changed_files)
    magnitude = additions + deletions
    blast = estimate_blast_radius(diff_evidence)
    classification = classify_change(diff_evidence)
    risk_score = file_count * 5 + min(magnitude, 400) * 0.1 + blast["boundary_crossings"] * 10
    if not classification["tests_touched"]:
        risk_score += 8
    confidence = "high" if file_count >= 1 else "low"
    ranked_files = sorted(
        changed_files,
        key=lambda item: (
            -(int(item.get("additions", 0) or 0) + int(item.get("deletions", 0) or 0)),
            str(item.get("path") or ""),
        ),
    )
    return {
        "risk_score": round(risk_score, 2),
        "blast_radius": blast,
        "classification": classification,
        "primary_targets": ranked_files[:3],
        "confidence": confidence,
    }
