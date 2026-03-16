from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def build_chain_id(diff_id: str, review_target: str) -> str:
    digest = hashlib.sha1(f'{diff_id}:{review_target}'.encode('utf-8')).hexdigest()[:10]
    return f'chain-{digest}'


def chain_artifact_path(project_root: Path, chain_id: str) -> Path:
    root = Path(project_root).expanduser().resolve() / '.benchchain'
    root.mkdir(parents=True, exist_ok=True)
    return root / f'{chain_id}.json'


def write_recommended_chain_artifact(
    project_root: Path,
    *,
    chain_id: str,
    diff_id: str,
    review_target: str,
    recommended_bluebench_action: str,
) -> Path:
    payload: dict[str, Any] = {
        'chain_id': chain_id,
        'diff_id': diff_id,
        'review_target': review_target,
        'recommended_bluebench_action': recommended_bluebench_action,
        'bluebench_run_id': None,
        'runtime_result': None,
        'status': 'recommended',
    }
    path = chain_artifact_path(project_root, chain_id)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding='utf-8')
    return path
