from __future__ import annotations

import json
import tempfile
from io import StringIO
from pathlib import Path
import subprocess
import unittest

from adapters.cli.commands import main
from adapters.codex.benchmark_packet import build_benchmark_recommendation_packet
from governance.compression_rules import validate_packet_budget


class BenchmarkPacketTests(unittest.TestCase):
    def setUp(self) -> None:
        self.diff_evidence = {
            'schema_version': '1',
            'diff_id': 'feature_x_vs_main',
            'base': 'main',
            'head': 'feature_x',
            'files_changed': 3,
            'changed_files': [
                {'path': 'engine/scanner_engine.py', 'status': 'modified', 'additions': 18, 'deletions': 6, 'subsystem': 'engine'},
                {'path': 'core/diff_loader.py', 'status': 'modified', 'additions': 3, 'deletions': 1, 'subsystem': 'core'},
                {'path': 'docs/README.md', 'status': 'modified', 'additions': 1, 'deletions': 1, 'subsystem': 'docs'},
            ],
        }

    def test_packet_generation_is_compact_and_deterministic(self) -> None:
        packet = build_benchmark_recommendation_packet(self.diff_evidence)
        self.assertEqual(packet['schema_version'], '1')
        self.assertEqual(packet['packet_type'], 'benchmark_recommendation')
        self.assertTrue(packet['targets'])
        self.assertEqual(packet['targets'][0]['path'], 'core/diff_loader.py')
        self.assertTrue(packet['chain_id'])
        self.assertEqual(packet['review_target'], packet['targets'][0]['review_target'])
        self.assertEqual(validate_packet_budget('benchmark_recommendation_packet', packet), [])

    def test_packet_does_not_include_forbidden_fields(self) -> None:
        packet = build_benchmark_recommendation_packet(self.diff_evidence)
        self.assertFalse(any(key in packet for key in ('full_diff', 'full_patch', 'runtime_measurements')))

    def test_cli_emits_formatted_benchmark_summary_and_chain_artifact(self) -> None:
        with _sample_repo() as repo_root:
            stream = StringIO()
            exit_code = main(['benchmark-recommend', '--base', 'main', '--head', 'feature-x', '--repo-root', str(repo_root)], stdout=stream)
            self.assertEqual(exit_code, 0)
            payload = json.loads(stream.getvalue())
            self.assertIn('benchmark_recommendation_packet', payload)
            self.assertTrue(payload['formatted_summary'])
            self.assertIn('Benchmark Recommendations', payload['formatted_summary'][0])
            self.assertTrue(payload['chain_artifacts'])
            artifact = Path(payload['chain_artifacts'][0])
            self.assertTrue(artifact.is_file())
            chain_payload = json.loads(artifact.read_text(encoding='utf-8'))
            self.assertEqual(chain_payload['status'], 'recommended')
            self.assertEqual(chain_payload['runtime_result'], None)


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
