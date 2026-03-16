from __future__ import annotations

from derive.hotspot_overlap import build_hotspot_overlap
from derive.risk_ranker import rank_diff_risk


def build_change_significance(
    diff_evidence: dict[str, object],
    *,
    hotspot_history: dict[str, object] | None = None,
) -> dict[str, object]:
    risk = rank_diff_risk(diff_evidence)
    changed_files = [item for item in list(diff_evidence.get('changed_files') or []) if isinstance(item, dict)]
    ranked_targets = list(risk.get('primary_targets') or [])
    low_risk_files = [
        {'path': item.get('path', ''), 'subsystem': item.get('subsystem', '')}
        for item in sorted(
            changed_files,
            key=lambda item: (
                int(item.get('additions', 0) or 0) + int(item.get('deletions', 0) or 0),
                str(item.get('path') or ''),
            ),
        )[3:6]
    ]
    blast = dict(risk.get('blast_radius') or {})
    classification = dict(risk.get('classification') or {})
    hotspot_overlap = build_hotspot_overlap(diff_evidence, hotspot_history=hotspot_history)
    overlap_by_path = {str(item.get('path') or ''): item for item in list(hotspot_overlap.get('hotspot_overlap_targets') or []) if isinstance(item, dict)}

    reasons = [
        f"{diff_evidence.get('files_changed', 0)} files changed",
        f"{blast.get('boundary_crossings', 0)} subsystem boundary crossings",
    ]
    if not classification.get('tests_touched', False):
        reasons.append('no tests touched')
    reasons.extend(list(hotspot_overlap.get('hotspot_overlap_reason') or []))

    risk_ranking = []
    for item in ranked_targets:
        path = str(item.get('path') or '')
        change_size = int(item.get('additions', 0) or 0) + int(item.get('deletions', 0) or 0)
        entry_reasons: list[str] = []
        if change_size >= 20:
            entry_reasons.append('large change size')
        if blast.get('boundary_crossings', 0):
            entry_reasons.append('crosses subsystem boundary')
        overlap = overlap_by_path.get(path)
        if overlap:
            entry_reasons.append(str(overlap.get('reason') or ''))
        confidence = str(risk.get('confidence', 'medium'))
        if overlap:
            confidence = str(overlap.get('confidence') or confidence)
        risk_ranking.append(
            {
                'path': path,
                'subsystem': item.get('subsystem', ''),
                'change_size': change_size,
                'reasons': [reason for reason in entry_reasons if reason][:3],
                'blast_radius': int(blast.get('boundary_crossings', 0) or 0),
                'confidence': confidence,
            }
        )

    recommended_next_actions = []
    if hotspot_overlap.get('hotspot_overlap_confidence') in {'high', 'medium'} and ranked_targets:
        recommended_next_actions.append({'action': 'rerun_bluebench_hotspot_probe', 'target': ranked_targets[0].get('path', ''), 'confidence': hotspot_overlap.get('hotspot_overlap_confidence', 'medium')})
    recommended_next_actions.extend(
        {'action': 'review_target', 'target': item.get('path', ''), 'confidence': risk.get('confidence', 'medium')}
        for item in ranked_targets[:2]
    )
    if not classification.get('tests_touched', False):
        recommended_next_actions.append({'action': 'add_or_run_tests', 'target': 'tests', 'confidence': 'medium'})

    confidence = str(risk.get('confidence', 'medium'))
    if hotspot_overlap.get('hotspot_overlap_confidence') == 'high':
        confidence = 'high'

    return {
        'risk_ranking': risk_ranking,
        'blast_radius': blast,
        'review_reasons': reasons[:4],
        'confidence': confidence,
        'recommended_next_actions': recommended_next_actions[:3],
        'low_risk_files': low_risk_files,
        'hotspot_overlap': hotspot_overlap,
        'classification': classification,
    }
