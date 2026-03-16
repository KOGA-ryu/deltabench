from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import TextIO

_ACTION_MAP = {
    'rerun_hotspot_probe': lambda chain_id, path: ['bluebench', 'compare', '<baseline_run_id>', '<current_run_id>', '--chain-id', chain_id, '--target', path],
    'rerun_targeted_probe': lambda chain_id, path: ['bluebench', 'compare', '<baseline_run_id>', '<current_run_id>', '--chain-id', chain_id, '--target', path],
    'rerun_compare': lambda chain_id, path: ['bluebench', 'compare', '<baseline_run_id>', '<current_run_id>', '--chain-id', chain_id, '--target', path],
    'rerun_repeatability': lambda chain_id, path: ['TODO: map repeatability chain', chain_id, path],
}


def load_packet(packet_path: str | Path) -> dict[str, object]:
    payload = json.loads(Path(packet_path).read_text(encoding='utf-8'))
    if 'benchmark_recommendation_packet' in payload and isinstance(payload['benchmark_recommendation_packet'], dict):
        return dict(payload['benchmark_recommendation_packet'])
    return payload


def validate_packet(packet: dict[str, object]) -> list[str]:
    errors: list[str] = []
    if str(packet.get('packet_type') or '') != 'benchmark_recommendation':
        errors.append('packet_type must be benchmark_recommendation')
    if 'targets' not in packet:
        errors.append('missing required key: targets')
    elif not isinstance(packet.get('targets'), list):
        errors.append('targets must be a list')
    if 'confidence' not in packet:
        errors.append('missing required key: confidence')
    return errors


def map_target_to_command(target: dict[str, object]) -> dict[str, object]:
    review_target = str(target.get('review_target') or target.get('path') or '')
    action = str(target.get('recommended_bluebench_action') or '')
    chain_id = str(target.get('chain_id') or '')
    reasons = [str(item) for item in list(target.get('reason') or []) if str(item)]
    confidence = str(target.get('confidence') or '')
    builder = _ACTION_MAP.get(action)
    if builder is None:
        return {
            'target': review_target,
            'chain_id': chain_id,
            'reason': reasons,
            'suggested_bluebench_action': action,
            'command': [f'TODO: map BlueBench action {action} for {review_target}'],
            'confidence': confidence,
            'known_action': False,
        }
    return {
        'target': review_target,
        'chain_id': chain_id,
        'reason': reasons,
        'suggested_bluebench_action': action,
        'command': builder(chain_id, review_target),
        'confidence': confidence,
        'known_action': not action.startswith('rerun_repeatability'),
    }


def build_handoff_entries(packet: dict[str, object]) -> list[dict[str, object]]:
    errors = validate_packet(packet)
    if errors:
        raise ValueError('; '.join(errors))
    return [map_target_to_command(dict(item)) for item in list(packet.get('targets') or []) if isinstance(item, dict)]


def format_handoff_summary(entries: list[dict[str, object]]) -> list[str]:
    lines = ['DeltaBench -> BlueBench Handoff', '------------------------------']
    if not entries:
        lines.append('No runtime-relevant targets detected.')
        return lines
    primary = entries[0]
    lines.append(f"Target: {primary['target']}")
    reason = list(primary.get('reason') or [])
    if reason:
        lines.append(f'Reason: {reason[0]}')
    lines.append(f"Chain ID: {primary['chain_id']}")
    lines.append(f"Suggested BlueBench action: {primary['suggested_bluebench_action']}")
    command = primary.get('command') or []
    if command:
        lines.append(f"Command: {' '.join(str(item) for item in command)}")
    return lines


def execute_entries(entries: list[dict[str, object]]) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    for entry in entries:
        command = list(entry.get('command') or [])
        if not entry.get('known_action', False):
            results.append({'target': entry.get('target', ''), 'executed': False, 'returncode': None})
            continue
        completed = subprocess.run(command, capture_output=True, text=True, check=False)
        results.append(
            {
                'target': entry.get('target', ''),
                'executed': True,
                'returncode': completed.returncode,
                'stdout': completed.stdout,
                'stderr': completed.stderr,
            }
        )
    return results


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='DeltaBench -> BlueBench handoff')
    parser.add_argument('--packet', required=True)
    parser.add_argument('--execute', action='store_true')
    return parser


def main(argv: list[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    output = stdout or sys.stdout
    packet = load_packet(args.packet)
    try:
        entries = build_handoff_entries(packet)
    except ValueError as exc:
        output.write(str(exc) + '\n')
        return 2
    payload: dict[str, object] = {
        'formatted_summary': format_handoff_summary(entries),
        'handoff': entries,
    }
    if args.execute:
        payload['execution'] = execute_entries(entries)
    output.write(json.dumps(payload, indent=2, sort_keys=True) + '\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
