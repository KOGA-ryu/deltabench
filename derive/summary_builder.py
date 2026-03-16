from __future__ import annotations

from derive.evidence_labels import label


def build_diff_summary(diff_evidence: dict[str, object], risk: dict[str, object], review_priority: dict[str, object]) -> dict[str, object]:
    blast = dict(risk.get("blast_radius") or {})
    summary_lines = [
        f"Files changed: {diff_evidence.get('files_changed', 0)}",
        f"Boundary crossings: {blast.get('boundary_crossings', 0)}",
        f"Review priority: {review_priority.get('priority', 'medium')}",
    ]
    return {
        "summary_lines": summary_lines,
        "labels": [
            label("measured", "files_changed", diff_evidence.get("files_changed", 0)),
            label("derived", "risk_score", risk.get("risk_score", 0.0)),
            label("derived", "boundary_crossings", blast.get("boundary_crossings", 0)),
        ],
    }
