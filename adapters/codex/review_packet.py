from __future__ import annotations

from derive.change_significance import build_change_significance
from derive.review_map import build_review_map


def build_review_packet(diff_evidence: dict[str, object], *, hotspot_history: dict[str, object] | None = None) -> dict[str, object]:
    significance = build_change_significance(diff_evidence, hotspot_history=hotspot_history)
    return {
        'schema_version': '1',
        'packet_type': 'review_packet',
        'primary_risk_targets': significance['risk_ranking'][:3],
        'reason': significance['review_reasons'],
        'blast_radius': significance['blast_radius'],
        'confidence': significance['confidence'],
        'recommended_next_actions': significance['recommended_next_actions'][:3],
        'low_risk_files': significance['low_risk_files'],
        'review_map': build_review_map(diff_evidence, significance),
    }
