from __future__ import annotations

import json
import tempfile
from io import StringIO
from pathlib import Path
import subprocess
import unittest

from adapters.cli.commands import main
from adapters.codex.review_packet import build_review_packet
from derive.hotspot_overlap import build_hotspot_overlap, load_hotspot_artifact
from governance.compression_rules import validate_packet_budget
from governance.semantic_rules import validate_canonical_field


class HotspotOverlapTests(unittest.TestCase):
    def setUp(self) -> None:
        self.diff_evidence = {
            'schema_version': '1',
            'diff_id': 'feature_x_vs_main',
            'base': 'main',
            'head': 'feature_x',
            'files_changed': 2,
            'changed_files': [
                {'path': 'engine/scanner_engine.py', 'status': 'modified', 'additions': 18, 'deletions': 6, 'subsystem': 'engine'},
                {'path': 'docs/README.md', 'status': 'modified', 'additions': 1, 'deletions': 1, 'subsystem': 'docs'},
            ],
        }
        self.hotspot_history = {
            'hotspots': [
                {'path': 'engine/scanner_engine.py'},
                {'path': 'engine/request_client.py'},
            ]
        }

    def test_overlap_detected_when_changed_file_matches_hotspot_artifact(self) -> None:
        overlap = build_hotspot_overlap(self.diff_evidence, self.hotspot_history)
        self.assertEqual(overlap['hotspot_overlap_confidence'], 'high')
        self.assertEqual(overlap['hotspot_overlap_targets'][0]['path'], 'engine/scanner_engine.py')

    def test_no_overlap_when_files_are_unrelated(self) -> None:
        overlap = build_hotspot_overlap(self.diff_evidence, {'hotspots': [{'path': 'core/other.py'}]})
        self.assertEqual(overlap['hotspot_overlap_confidence'], 'none')
        self.assertEqual(overlap['hotspot_overlap_targets'], [])

    def test_review_packet_integrates_hotspot_overlap_and_stays_compact(self) -> None:
        packet = build_review_packet(self.diff_evidence, hotspot_history=self.hotspot_history)
        self.assertIn('touches prior runtime hotspot', packet['primary_risk_targets'][0]['reasons'])
        self.assertEqual(packet['primary_risk_targets'][0]['confidence'], 'high')
        self.assertEqual(validate_packet_budget('review_packet', packet), [])

    def test_semantic_producer_for_hotspot_overlap_is_canonical(self) -> None:
        self.assertTrue(validate_canonical_field('hotspot_overlap_targets', 'derive/hotspot_overlap.py'))

    def test_cli_displays_overlap_reason_when_artifact_is_available(self) -> None:
        with _sample_repo() as repo_root:
            artifact_path = repo_root / 'hotspots.json'
            artifact_path.write_text(json.dumps(self.hotspot_history), encoding='utf-8')
            stream = StringIO()
            exit_code = main([
                'review-packet', '--base', 'main', '--head', 'feature-x', '--repo-root', str(repo_root), '--hotspot-artifact', str(artifact_path)
            ], stdout=stream)
            self.assertEqual(exit_code, 0)
            payload = json.loads(stream.getvalue())
            self.assertIn('touches prior runtime hotspot', ' '.join(payload['formatted_summary']))

    def test_hotspot_artifact_loader_uses_shared_json_interface(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            artifact = Path(tmp) / 'hotspots.json'
            artifact.write_text(json.dumps(self.hotspot_history), encoding='utf-8')
            loaded = load_hotspot_artifact(artifact)
            self.assertIn('engine/scanner_engine.py', loaded['hotspot_paths'])


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
        (self.root / 'docs').mkdir(parents=True, exist_ok=True)
        (self.root / 'engine' / 'scanner_engine.py').write_text("def scan():\n    return []\n", encoding='utf-8')
        (self.root / 'docs' / 'README.md').write_text('base\n', encoding='utf-8')
        _git(self.root, ['git', 'add', '.'])
        _git(self.root, ['git', 'commit', '-m', 'base'])
        _git(self.root, ['git', 'checkout', '-b', 'feature-x'])
        (self.root / 'engine' / 'scanner_engine.py').write_text("def scan():\n    return ['changed']\n", encoding='utf-8')
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
