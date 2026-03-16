from __future__ import annotations

import json

PACKET_BUDGETS = {
    'review_packet': {
        'max_bytes': 3200,
        'max_top_level_keys': 9,
        'max_summary_lines': 3,
        'max_targets': 3,
        'required_keys': [
            'schema_version',
            'packet_type',
            'primary_risk_targets',
            'confidence',
            'review_map',
        ],
        'forbid_keys': [
            'full_diff',
            'full_patch',
            'raw_evidence_dump',
            'full_report_text',
        ],
    },
    'benchmark_recommendation_packet': {
        'max_bytes': 2600,
        'max_top_level_keys': 7,
        'max_summary_lines': 5,
        'max_targets': 3,
        'required_keys': [
            'schema_version',
            'packet_type',
            'diff_id',
            'chain_id',
            'review_target',
            'targets',
            'confidence',
        ],
        'forbid_keys': [
            'full_diff',
            'full_patch',
            'raw_evidence_dump',
            'full_report_text',
            'runtime_measurements',
        ],
    },
    'context_pack': {
        'max_bytes': 5000,
        'max_top_level_keys': 6,
        'max_summary_lines': 5,
        'required_keys': [
            'schema_version',
            'summary',
        ],
        'forbid_keys': [
            'full_diff',
            'full_patch',
            'raw_evidence_dump',
        ],
    },
}


def packet_size_bytes(packet: dict) -> int:
    return len(json.dumps(packet, separators=(',', ':'), sort_keys=True).encode('utf-8'))


def count_top_level_keys(packet: dict) -> int:
    return len(packet.keys())


def contains_forbidden_key(packet: dict, key: str) -> bool:
    if isinstance(packet, dict):
        for inner_key, inner_value in packet.items():
            if inner_key == key or contains_forbidden_key(inner_value, key):
                return True
    if isinstance(packet, list):
        return any(contains_forbidden_key(item, key) for item in packet)
    return False


def validate_packet_budget(packet_type: str, packet: dict) -> list[str]:
    budget = PACKET_BUDGETS[packet_type]
    errors: list[str] = []
    if packet_size_bytes(packet) > int(budget['max_bytes']):
        errors.append(f"packet exceeds max_bytes={budget['max_bytes']}")
    if count_top_level_keys(packet) > int(budget['max_top_level_keys']):
        errors.append(f"packet exceeds max_top_level_keys={budget['max_top_level_keys']}")
    for key in budget.get('required_keys', []):
        if key not in packet:
            errors.append(f"missing required key: {key}")
    for key in budget.get('forbid_keys', []):
        if contains_forbidden_key(packet, key):
            errors.append(f"forbidden key present: {key}")
    if 'summary_lines' in packet and len(list(packet.get('summary_lines') or [])) > int(budget.get('max_summary_lines', 999)):
        errors.append(f"summary_lines exceed max_summary_lines={budget['max_summary_lines']}")
    if 'summary' in packet and len(list(packet.get('summary') or [])) > int(budget.get('max_summary_lines', 999)):
        errors.append(f"summary exceeds max_summary_lines={budget['max_summary_lines']}")
    if 'primary_risk_targets' in packet and len(list(packet.get('primary_risk_targets') or [])) > int(budget.get('max_targets', 999)):
        errors.append(f"primary_risk_targets exceed max_targets={budget['max_targets']}")
    if 'targets' in packet and len(list(packet.get('targets') or [])) > int(budget.get('max_targets', 999)):
        errors.append(f"targets exceed max_targets={budget['max_targets']}")
    if 'review_map' in packet and len(list(packet.get('review_map') or [])) > int(budget.get('max_targets', 999)):
        errors.append(f"review_map exceeds max_targets={budget['max_targets']}")
    return errors
