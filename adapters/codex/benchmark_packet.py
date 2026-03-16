from __future__ import annotations

from derive.change_significance import build_change_significance
from derive.runtime_relevance import build_runtime_relevance
from tools.chain_artifact import build_chain_id


def build_benchmark_recommendation_packet(
    diff_evidence: dict[str, object],
    *,
    hotspot_history: dict[str, object] | None = None,
) -> dict[str, object]:
    significance = build_change_significance(diff_evidence, hotspot_history=hotspot_history)
    runtime_relevance = build_runtime_relevance(
        diff_evidence,
        significance,
        hotspot_history=hotspot_history,
    )
    diff_id = str(diff_evidence.get('diff_id') or '')
    targets = []
    for item in list(runtime_relevance['benchmark_recommendations'] or []):
        target = dict(item)
        review_target = str(target.get('path') or '')
        chain_id = build_chain_id(diff_id, review_target)
        target['chain_id'] = chain_id
        target['review_target'] = review_target
        targets.append(target)
    primary_target = dict(targets[0]) if targets else {}
    return {
        'schema_version': '1',
        'packet_type': 'benchmark_recommendation',
        'diff_id': diff_id,
        'chain_id': str(primary_target.get('chain_id') or ''),
        'review_target': str(primary_target.get('review_target') or ''),
        'targets': targets,
        'confidence': runtime_relevance['confidence'],
    }
