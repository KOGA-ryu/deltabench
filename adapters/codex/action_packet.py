from __future__ import annotations

from .review_packet import build_review_packet


def build_action_packet(diff_evidence: dict[str, object]) -> dict[str, object]:
    review_packet = build_review_packet(diff_evidence)
    return {
        "schema_version": "1",
        "packet_type": "action_packet",
        "diff_id": diff_evidence.get("diff_id", ""),
        "action": "review_first",
        "target": review_packet["primary_review_target"],
        "confidence": review_packet["confidence"],
    }
