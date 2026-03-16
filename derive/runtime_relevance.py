from __future__ import annotations

from pathlib import Path

_RUNTIME_SUBSYSTEMS = {'engine', 'scanner', 'runtime', 'core'}
_RUNTIME_NAME_HINTS = ('engine', 'scanner', 'runtime', 'client', 'worker')


def _is_runtime_relevant(path: str, subsystem: str) -> bool:
    normalized = Path(path).as_posix()
    if subsystem in _RUNTIME_SUBSYSTEMS:
        return True
    name = normalized.lower()
    return any(hint in name for hint in _RUNTIME_NAME_HINTS)


def _target_confidence(*, reasons: list[str], hotspot_overlap: bool, boundary_crossings: int) -> str:
    if hotspot_overlap:
        return 'high'
    if any('runtime subsystem' in reason for reason in reasons):
        return 'medium' if boundary_crossings > 0 else 'high'
    if boundary_crossings > 0:
        return 'medium'
    return 'low'


def build_runtime_relevance(
    diff_evidence: dict[str, object],
    change_significance: dict[str, object],
    *,
    hotspot_history: dict[str, object] | None = None,
) -> dict[str, object]:
    changed_files = [item for item in list(diff_evidence.get('changed_files') or []) if isinstance(item, dict)]
    blast_radius = dict(change_significance.get('blast_radius') or {})
    boundary_crossings = int(blast_radius.get('boundary_crossings', 0) or 0)
    hotspot_paths = {
        str(path)
        for path in list((hotspot_history or {}).get('hotspot_paths') or [])
        if isinstance(path, str)
    }

    runtime_targets: list[dict[str, object]] = []
    benchmark_recommendations: list[dict[str, object]] = []

    for item in changed_files:
        path = str(item.get('path') or '')
        subsystem = str(item.get('subsystem') or '')
        if not _is_runtime_relevant(path, subsystem):
            continue

        reasons: list[str] = []
        if subsystem in _RUNTIME_SUBSYSTEMS:
            reasons.append('touches runtime subsystem')
        if any(hint in path.lower() for hint in _RUNTIME_NAME_HINTS if hint != subsystem.lower()):
            reasons.append('likely affects runtime execution path')
        if boundary_crossings > 0:
            reasons.append('crosses subsystem boundary into runtime layer')

        hotspot_overlap = path in hotspot_paths
        if hotspot_overlap:
            reasons.append('matches known hotspot file name')

        confidence = _target_confidence(
            reasons=reasons,
            hotspot_overlap=hotspot_overlap,
            boundary_crossings=boundary_crossings,
        )
        action = 'rerun_hotspot_probe'
        if hotspot_overlap:
            action = 'rerun_targeted_probe'
        runtime_target = {
            'path': path,
            'subsystem': subsystem,
            'reason': reasons[:3],
            'recommended_bluebench_action': action,
            'confidence': confidence,
        }
        runtime_targets.append(runtime_target)
        benchmark_recommendations.append(
            {
                'path': path,
                'reason': reasons[:3],
                'recommended_bluebench_action': action,
                'confidence': confidence,
            }
        )

    runtime_targets.sort(key=lambda item: ({'high': 0, 'medium': 1, 'low': 2}.get(str(item.get('confidence')), 3), str(item.get('path') or '')))
    benchmark_recommendations = runtime_targets[:3]

    overall_confidence = 'low'
    if benchmark_recommendations:
        confidences = [str(item.get('confidence') or 'low') for item in benchmark_recommendations]
        if 'high' in confidences:
            overall_confidence = 'high'
        elif 'medium' in confidences:
            overall_confidence = 'medium'

    return {
        'runtime_relevant_targets': runtime_targets,
        'benchmark_recommendations': benchmark_recommendations,
        'confidence': overall_confidence,
    }
