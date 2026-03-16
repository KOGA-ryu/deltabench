from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import TextIO

from adapters.codex.benchmark_packet import build_benchmark_recommendation_packet
from adapters.codex.review_packet import build_review_packet
from core.change_writer import write_diff_evidence
from derive.hotspot_overlap import load_hotspot_artifact
from evidence.loaders.diff_loader import load_diff_evidence
from reports.json_exporter import export_json
from reports.markdown_exporter import export_markdown
from tools.bench_handoff import build_handoff_entries, format_handoff_summary
from tools.chain_artifact import write_recommended_chain_artifact


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='DeltaBench CLI')
    subparsers = parser.add_subparsers(dest='command', required=True)

    diff_parser = subparsers.add_parser('diff', help='Load and persist canonical diff evidence.')
    diff_parser.add_argument('--base', required=True)
    diff_parser.add_argument('--head', required=True)
    diff_parser.add_argument('--repo-root', default=str(Path.cwd()))

    review_parser = subparsers.add_parser('review-packet', help='Emit a compact review packet.')
    review_parser.add_argument('--base', required=True)
    review_parser.add_argument('--head', required=True)
    review_parser.add_argument('--repo-root', default=str(Path.cwd()))
    review_parser.add_argument('--hotspot-artifact', help='Optional BlueBench hotspot artifact JSON path.')

    benchmark_parser = subparsers.add_parser('benchmark-recommend', help='Emit a compact benchmark recommendation packet.')
    benchmark_parser.add_argument('--base', required=True)
    benchmark_parser.add_argument('--head', required=True)
    benchmark_parser.add_argument('--repo-root', default=str(Path.cwd()))
    benchmark_parser.add_argument('--handoff', action='store_true', help='Also print the mapped BlueBench handoff command.')
    return parser


def _build_review_summary(review_packet: dict[str, object]) -> list[str]:
    review_map = [dict(item) for item in list(review_packet.get('review_map') or []) if isinstance(item, dict)]
    lines = ['DeltaBench Review Map']
    if not review_map:
        lines.append('No prioritized review targets.')
        return lines
    primary = review_map[0]
    lines.append(f"1. {primary.get('path', '')}")
    for reason in list(primary.get('reasons') or [])[:2]:
        lines.append(f"reason: {reason}")
    lines.append(f"blast radius: {primary.get('blast_radius', 0)}")
    lines.append(f"confidence: {primary.get('confidence', '')}")
    lines.append(f"next action: {primary.get('suggested_action', '')}")
    low_risk_files = [dict(item) for item in list(review_packet.get('low_risk_files') or []) if isinstance(item, dict)]
    if low_risk_files:
        lines.append('Low Risk Files')
        lines.extend(str(item.get('path') or '') for item in low_risk_files[:2])
    return lines[:8]


def _build_benchmark_summary(packet: dict[str, object]) -> list[str]:
    targets = list(packet.get('targets') or [])
    if not targets:
        return ['Benchmark Recommendations', 'No runtime-relevant targets detected.']
    primary = dict(targets[0])
    summary = [
        'Benchmark Recommendations',
        f"Target: {primary.get('review_target', primary.get('path', ''))}",
        f"Chain ID: {primary.get('chain_id', '')}",
    ]
    for reason in list(primary.get('reason') or [])[:1]:
        summary.append(f"Reason: {reason}")
    summary.append(f"Suggested action: {primary.get('recommended_bluebench_action', '')}")
    return summary[:5]


def main(argv: list[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    output = stdout or sys.stdout
    repo_root = Path(args.repo_root).expanduser().resolve()

    if args.command == 'diff':
        evidence = load_diff_evidence(repo_root, base=args.base, head=args.head)
        evidence_path = write_diff_evidence(repo_root, evidence)
        payload = {'evidence': evidence, 'evidence_path': str(evidence_path)}
        output.write(json.dumps(payload, indent=2, sort_keys=True) + '\n')
        return 0
    if args.command == 'review-packet':
        evidence = load_diff_evidence(repo_root, base=args.base, head=args.head)
        evidence_path = write_diff_evidence(repo_root, evidence)
        hotspot_history = load_hotspot_artifact(args.hotspot_artifact) if args.hotspot_artifact else None
        review_packet = build_review_packet(evidence, hotspot_history=hotspot_history)
        root = repo_root / '.deltabench'
        export_json(review_packet, root / f"{evidence['diff_id']}_review_packet.json")
        export_markdown(review_packet, root / f"{evidence['diff_id']}_review_packet.md")
        payload = {
            'evidence_path': str(evidence_path),
            'formatted_summary': _build_review_summary(review_packet),
            'review_packet': review_packet,
        }
        output.write(json.dumps(payload, indent=2, sort_keys=True) + '\n')
        return 0
    if args.command == 'benchmark-recommend':
        evidence = load_diff_evidence(repo_root, base=args.base, head=args.head)
        evidence_path = write_diff_evidence(repo_root, evidence)
        packet = build_benchmark_recommendation_packet(evidence)
        root = repo_root / '.deltabench'
        export_json(packet, root / f"{evidence['diff_id']}_benchmark_recommendation.json")
        export_markdown(packet, root / f"{evidence['diff_id']}_benchmark_recommendation.md")
        chain_artifacts = []
        for item in list(packet.get('targets') or []):
            if not isinstance(item, dict):
                continue
            chain_artifacts.append(
                str(
                    write_recommended_chain_artifact(
                        repo_root,
                        chain_id=str(item.get('chain_id') or ''),
                        diff_id=str(packet.get('diff_id') or evidence.get('diff_id') or ''),
                        review_target=str(item.get('review_target') or item.get('path') or ''),
                        recommended_bluebench_action=str(item.get('recommended_bluebench_action') or ''),
                    )
                )
            )
        payload = {
            'evidence_path': str(evidence_path),
            'formatted_summary': _build_benchmark_summary(packet),
            'benchmark_recommendation_packet': packet,
            'chain_artifacts': chain_artifacts,
        }
        if args.handoff:
            handoff_entries = build_handoff_entries(packet)
            payload['handoff'] = {
                'formatted_summary': format_handoff_summary(handoff_entries),
                'entries': handoff_entries,
            }
        output.write(json.dumps(payload, indent=2, sort_keys=True) + '\n')
        return 0
    parser.error(f'Unknown command: {args.command}')
    return 2


if __name__ == '__main__':
    raise SystemExit(main())
