from __future__ import annotations

CANONICAL_PRODUCERS = {
    'diff': 'core/diff_loader.py',
    'subsystem': 'core/repo_mapper.py',
    'risk': 'derive/risk_ranker.py',
    'blast_radius': 'derive/blast_radius.py',
    'review_priority': 'derive/review_priority.py',
    'confidence': 'derive/change_significance.py',
    'primary_risk_targets': 'adapters/codex/review_packet.py',
    'low_risk_files': 'derive/change_significance.py',
    'review_packet': 'adapters/codex/review_packet.py',
    'runtime_relevant_targets': 'derive/runtime_relevance.py',
    'benchmark_recommendations': 'derive/runtime_relevance.py',
    'benchmark_recommendation_packet': 'adapters/codex/benchmark_packet.py',
    'hotspot_overlap_targets': 'derive/hotspot_overlap.py',
    'hotspot_overlap_confidence': 'derive/hotspot_overlap.py',
    'review_map': 'derive/review_map.py',
}


def get_canonical_producer(field_name: str) -> str | None:
    return CANONICAL_PRODUCERS.get(str(field_name))


def validate_canonical_field(field_name: str, producer_path: str) -> bool:
    return str(get_canonical_producer(field_name) or '') == str(producer_path)
