from __future__ import annotations

from pathlib import Path


def export_markdown(review_packet: dict[str, object], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        '# DeltaBench Review Packet',
        '',
        f"- Diff: `{review_packet.get('diff_id', '')}`",
        f"- Primary target: `{review_packet.get('primary_review_target', {}).get('path', '')}`",
        f"- Confidence: `{review_packet.get('confidence', 'medium')}`",
        '',
        '## Why This Diff Matters',
    ]
    for line in list(review_packet.get('reason') or []):
        lines.append(f'- {line}')
    lines.extend(['', '## Summary'])
    for line in list(review_packet.get('summary_lines') or []):
        lines.append(f'- {line}')
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return path
