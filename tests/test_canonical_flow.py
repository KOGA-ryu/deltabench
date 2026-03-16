from __future__ import annotations

import json
import tempfile
from pathlib import Path
import subprocess
import unittest

from adapters.cli.commands import main
from adapters.codex.review_packet import build_review_packet
from core.change_writer import write_diff_evidence
from derive.review_priority import build_review_priority
from derive.risk_ranker import rank_diff_risk
from derive.summary_builder import build_diff_summary
from evidence.loaders.diff_loader import load_diff_evidence
from reports.json_exporter import export_json
from reports.markdown_exporter import export_markdown


class CanonicalFlowTests(unittest.TestCase):
    def test_end_to_end_diff_to_review_packet_flow(self) -> None:
        with _sample_repo() as repo_root:
            diff_evidence = load_diff_evidence(repo_root, base='main', head='feature-x')
            evidence_path = write_diff_evidence(repo_root, diff_evidence)
            risk = rank_diff_risk(diff_evidence)
            review_priority = build_review_priority(diff_evidence, risk)
            summary = build_diff_summary(diff_evidence, risk, review_priority)
            review_packet = build_review_packet(diff_evidence)
            json_path = export_json(review_packet, repo_root / '.deltabench' / 'review_packet.json')
            markdown_path = export_markdown(review_packet, repo_root / '.deltabench' / 'review_packet.md')

            self.assertTrue(evidence_path.exists())
            self.assertTrue(json_path.exists())
            self.assertTrue(markdown_path.exists())
            self.assertEqual(review_packet['primary_risk_targets'][0]['path'], 'engine/scanner_engine.py')
            self.assertEqual(review_packet['review_map'][0]['path'], 'engine/scanner_engine.py')
            self.assertEqual(summary['summary_lines'][0], 'Files changed: 2')

            stream_output = _run_cli(repo_root, ['review-packet', '--base', 'main', '--head', 'feature-x'])
            payload = json.loads(stream_output)
            self.assertEqual(payload['review_packet']['primary_risk_targets'][0]['path'], 'engine/scanner_engine.py')
            self.assertTrue(payload['formatted_summary'])


class _sample_repo:
    def __init__(self) -> None:
        self.tmp_dir: tempfile.TemporaryDirectory[str] | None = None
        self.root: Path | None = None

    def __enter__(self) -> Path:
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp_dir.name)
        _git(self.root, ['git', 'init', '-b', 'main'])
        _git(self.root, ['git', 'config', 'user.email', 'test@example.com'])
        _git(self.root, ['git', 'config', 'user.name', 'DeltaBench Test'])
        (self.root / 'engine').mkdir(parents=True, exist_ok=True)
        (self.root / 'tests').mkdir(parents=True, exist_ok=True)
        (self.root / 'engine' / 'scanner_engine.py').write_text("def scan():\n    return []\n", encoding='utf-8')
        (self.root / 'README.md').write_text('base\n', encoding='utf-8')
        _git(self.root, ['git', 'add', '.'])
        _git(self.root, ['git', 'commit', '-m', 'base'])
        _git(self.root, ['git', 'checkout', '-b', 'feature-x'])
        (self.root / 'engine' / 'scanner_engine.py').write_text("def scan():\n    return ['changed']\n", encoding='utf-8')
        (self.root / 'tests' / 'test_engine.py').write_text("def test_scan():\n    assert True\n", encoding='utf-8')
        _git(self.root, ['git', 'add', '.'])
        _git(self.root, ['git', 'commit', '-m', 'feature'])
        return self.root

    def __exit__(self, exc_type, exc, tb) -> None:
        assert self.tmp_dir is not None
        self.tmp_dir.cleanup()


def _git(repo_root: Path, command: list[str]) -> None:
    completed = subprocess.run(command, cwd=str(repo_root), capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr)


def _run_cli(repo_root: Path, argv: list[str]) -> str:
    from io import StringIO

    stream = StringIO()
    exit_code = main([*argv, '--repo-root', str(repo_root)], stdout=stream)
    if exit_code != 0:
        raise AssertionError(f'CLI failed with code {exit_code}')
    return stream.getvalue()


if __name__ == '__main__':
    unittest.main()
