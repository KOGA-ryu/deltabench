from __future__ import annotations

import json
import tempfile
from io import StringIO
from pathlib import Path
import subprocess
import unittest

from adapters.cli.commands import main
from adapters.codex.review_packet import build_review_packet
from governance.compression_rules import validate_packet_budget


class ReviewMapTests(unittest.TestCase):
    def setUp(self) -> None:
        self.diff_evidence = {
            'schema_version': '1',
            'diff_id': 'feature_x_vs_main',
            'base': 'main',
            'head': 'feature_x',
            'files_changed': 3,
            'changed_files': [
                {'path': 'engine/scanner_engine.py', 'status': 'modified', 'additions': 18, 'deletions': 6, 'subsystem': 'engine'},
                {'path': 'core/repo_mapper.py', 'status': 'modified', 'additions': 8, 'deletions': 4, 'subsystem': 'core'},
                {'path': 'docs/README.md', 'status': 'modified', 'additions': 1, 'deletions': 1, 'subsystem': 'docs'},
            ],
        }
        self.hotspot_history = {'hotspots': [{'path': 'engine/scanner_engine.py'}]}

    def test_review_map_ranking_is_deterministic(self) -> None:
        packet_a = build_review_packet(self.diff_evidence, hotspot_history=self.hotspot_history)
        packet_b = build_review_packet(self.diff_evidence, hotspot_history=self.hotspot_history)
        self.assertEqual(packet_a['review_map'], packet_b['review_map'])

    def test_hotspot_overlap_increases_priority(self) -> None:
        packet = build_review_packet(self.diff_evidence, hotspot_history=self.hotspot_history)
        self.assertEqual(packet['review_map'][0]['path'], 'engine/scanner_engine.py')
        self.assertIn('runtime hotspot', ' '.join(packet['review_map'][0]['reasons']))

    def test_review_packet_stays_within_budget(self) -> None:
        packet = build_review_packet(self.diff_evidence, hotspot_history=self.hotspot_history)
        self.assertEqual(validate_packet_budget('review_packet', packet), [])

    def test_cli_prints_prioritized_review_map(self) -> None:
        with _sample_repo() as repo_root:
            artifact_path = repo_root / 'hotspots.json'
            artifact_path.write_text(json.dumps(self.hotspot_history), encoding='utf-8')
            stream = StringIO()
            exit_code = main([
                'review-packet', '--base', 'main', '--head', 'feature-x', '--repo-root', str(repo_root), '--hotspot-artifact', str(artifact_path)
            ], stdout=stream)
            self.assertEqual(exit_code, 0)
            payload = json.loads(stream.getvalue())
            self.assertIn('DeltaBench Review Map', payload['formatted_summary'][0])
            self.assertIn('engine/scanner_engine.py', ' '.join(payload['formatted_summary']))


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


if __name__ == '__main__':
    unittest.main()
