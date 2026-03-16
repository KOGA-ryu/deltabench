from __future__ import annotations

import json
from pathlib import Path

from core.repo_mapper import map_path_to_subsystem


def load_hotspot_artifact(artifact_path: str | Path) -> dict[str, object]:
    payload = json.loads(Path(artifact_path).read_text(encoding='utf-8'))
    return normalize_hotspot_history(payload)


def normalize_hotspot_history(payload: dict[str, object] | None) -> dict[str, object]:
    payload = dict(payload or {})

    if 'hotspot_paths' in payload:
        hotspot_paths = sorted({str(path) for path in list(payload.get('hotspot_paths') or []) if str(path)})
    else:
        hotspot_paths: list[str] = []
        hotspots = payload.get('hotspots')
        if isinstance(hotspots, list):
            for item in hotspots:
                if isinstance(item, str):
                    hotspot_paths.append(item)
                elif isinstance(item, dict):
                    path = str(item.get('path') or item.get('file') or '')
                    if path:
                        hotspot_paths.append(path)
        files = payload.get('files')
        if isinstance(files, dict):
            for key in files.keys():
                if isinstance(key, str) and key:
                    hotspot_paths.append(key)
        hotspot_paths = sorted({path for path in hotspot_paths if path})

    if 'hotspot_subsystems' in payload:
        hotspot_subsystems = sorted({str(item) for item in list(payload.get('hotspot_subsystems') or []) if str(item)})
    else:
        hotspot_subsystems = sorted({map_path_to_subsystem(path) for path in hotspot_paths})

    return {
        'hotspot_paths': hotspot_paths,
        'hotspot_subsystems': hotspot_subsystems,
        'overlap_count': int(payload.get('overlap_count', 0) or 0),
    }


def build_hotspot_overlap(
    diff_evidence: dict[str, object],
    hotspot_history: dict[str, object] | None = None,
) -> dict[str, object]:
    history = normalize_hotspot_history(hotspot_history)
    hotspot_paths = set(str(path) for path in list(history.get('hotspot_paths') or []))
    hotspot_subsystems = set(str(item) for item in list(history.get('hotspot_subsystems') or []))
    changed_files = [item for item in list(diff_evidence.get('changed_files') or []) if isinstance(item, dict)]

    overlap_targets: list[dict[str, object]] = []
    file_matches = 0
    subsystem_matches = 0

    for item in changed_files:
        path = str(item.get('path') or '')
        subsystem = str(item.get('subsystem') or map_path_to_subsystem(path))
        if path in hotspot_paths:
            file_matches += 1
            overlap_targets.append(
                {
                    'path': path,
                    'subsystem': subsystem,
                    'reason': 'touches prior runtime hotspot',
                    'confidence': 'high',
                    'severity': 'file_match',
                }
            )
            continue
        if subsystem in hotspot_subsystems:
            subsystem_matches += 1
            overlap_targets.append(
                {
                    'path': path,
                    'subsystem': subsystem,
                    'reason': 'shares subsystem with prior runtime hotspot',
                    'confidence': 'medium',
                    'severity': 'subsystem_match',
                }
            )

    overlap_targets.sort(key=lambda item: ({'file_match': 0, 'subsystem_match': 1}.get(str(item.get('severity') or ''), 2), str(item.get('path') or '')))

    reasons: list[str] = []
    if file_matches:
        reasons.append(f'{file_matches} changed files touch prior runtime hotspots')
    if subsystem_matches:
        reasons.append(f'{subsystem_matches} changed files share hotspot subsystems')

    confidence = 'none'
    if file_matches:
        confidence = 'high'
    elif subsystem_matches:
        confidence = 'medium'

    return {
        'hotspot_overlap_targets': overlap_targets,
        'hotspot_overlap_reason': reasons,
        'hotspot_overlap_confidence': confidence,
        'overlap_count': file_matches + subsystem_matches,
        'hotspot_paths': sorted(hotspot_paths),
        'hotspot_subsystems': sorted(hotspot_subsystems),
    }
