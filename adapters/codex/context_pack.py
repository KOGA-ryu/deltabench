from __future__ import annotations

from adapters.codex.review_packet import build_review_packet
from derive.review_priority import build_review_priority
from derive.risk_ranker import rank_diff_risk
from derive.summary_builder import build_diff_summary


def build_context_pack(diff_evidence: dict[str, object]) -> dict[str, object]:
    risk = rank_diff_risk(diff_evidence)
    review_priority = build_review_priority(diff_evidence, risk)
    summary = build_diff_summary(diff_evidence, risk, review_priority)
    return {
        'schema_version': '1',
        'summary': summary['summary_lines'],
        'diff': {
            'diff_id': diff_evidence.get('diff_id', ''),
            'files_changed': diff_evidence.get('files_changed', 0),
        },
        'risk': risk,
        'review_packet': build_review_packet(diff_evidence),
    }
