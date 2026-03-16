from __future__ import annotations


def build_review_priority(diff_evidence: dict[str, object], risk: dict[str, object]) -> dict[str, object]:
    targets = list(risk.get("primary_targets") or [])
    return {
        "priority": "high" if float(risk.get("risk_score", 0.0) or 0.0) >= 25.0 else "medium",
        "targets": targets,
        "review_subsystems": [str(item.get("subsystem") or "") for item in targets if isinstance(item, dict)],
    }
