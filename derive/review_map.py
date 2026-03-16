from __future__ import annotations


def _priority_score(item: dict[str, object], tests_touched: bool) -> tuple[int, int, int, int, str]:
    reasons = [str(reason) for reason in list(item.get('reasons') or [])]
    hotspot = 1 if any('runtime hotspot' in reason for reason in reasons) else 0
    boundary = 1 if any('subsystem boundary' in reason for reason in reasons) else 0
    blast_radius = int(item.get('blast_radius', 0) or 0)
    change_size = int(item.get('change_size', 0) or 0)
    missing_tests = 0 if tests_touched else 1
    return (-hotspot, -boundary, -blast_radius, -change_size, str(item.get('path') or ''))


def build_review_map(
    diff_evidence: dict[str, object],
    change_significance: dict[str, object],
) -> list[dict[str, object]]:
    classification = dict((change_significance.get('classification') or {}))
    tests_touched = bool(classification.get('tests_touched', False))
    recommended_actions = list(change_significance.get('recommended_next_actions') or [])
    action_by_target = {
        str(item.get('target') or ''): str(item.get('action') or '')
        for item in recommended_actions
        if isinstance(item, dict)
    }
    ranked = [dict(item) for item in list(change_significance.get('risk_ranking') or []) if isinstance(item, dict)]
    ranked.sort(key=lambda item: _priority_score(item, tests_touched))

    review_map: list[dict[str, object]] = []
    for index, item in enumerate(ranked[:3], start=1):
        path = str(item.get('path') or '')
        suggested_action = action_by_target.get(path, 'review target first')
        if suggested_action == 'rerun_bluebench_hotspot_probe':
            suggested_action = 'rerun BlueBench hotspot probe'
        elif suggested_action == 'review_target':
            suggested_action = 'review target first'
        elif suggested_action == 'add_or_run_tests':
            suggested_action = 'check tests touching this area'
        review_map.append(
            {
                'path': path,
                'priority': index,
                'reasons': [str(reason) for reason in list(item.get('reasons') or [])][:3],
                'blast_radius': int(item.get('blast_radius', 0) or 0),
                'confidence': str(item.get('confidence') or 'medium'),
                'suggested_action': suggested_action,
            }
        )
    return review_map
