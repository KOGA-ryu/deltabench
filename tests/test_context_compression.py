from __future__ import annotations

import unittest

from adapters.codex.benchmark_packet import build_benchmark_recommendation_packet
from adapters.codex.context_pack import build_context_pack
from adapters.codex.review_packet import build_review_packet
from governance.compression_rules import validate_packet_budget


class ContextCompressionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.diff_evidence = {
            'schema_version': '1',
            'diff_id': 'feature_x_vs_main',
            'base': 'main',
            'head': 'feature_x',
            'files_changed': 3,
            'changed_files': [
                {'path': 'engine/scanner_engine.py', 'status': 'modified', 'additions': 18, 'deletions': 6, 'subsystem': 'engine'},
                {'path': 'tests/test_engine.py', 'status': 'added', 'additions': 4, 'deletions': 0, 'subsystem': 'tests'},
                {'path': 'docs/README.md', 'status': 'modified', 'additions': 1, 'deletions': 1, 'subsystem': 'docs'},
            ],
        }

    def test_review_packet_stays_under_budget(self) -> None:
        packet = build_review_packet(self.diff_evidence)
        self.assertEqual(validate_packet_budget('review_packet', packet), [])

    def test_benchmark_packet_stays_under_budget(self) -> None:
        packet = build_benchmark_recommendation_packet(self.diff_evidence)
        self.assertEqual(validate_packet_budget('benchmark_recommendation_packet', packet), [])

    def test_context_pack_stays_under_budget(self) -> None:
        packet = build_context_pack(self.diff_evidence)
        self.assertEqual(validate_packet_budget('context_pack', packet), [])

    def test_missing_required_key_produces_validation_error(self) -> None:
        packet = build_review_packet(self.diff_evidence)
        packet.pop('confidence', None)
        errors = validate_packet_budget('review_packet', packet)
        self.assertTrue(any('missing required key: confidence' in item for item in errors))

    def test_forbidden_key_produces_validation_error(self) -> None:
        packet = build_benchmark_recommendation_packet(self.diff_evidence)
        packet['full_diff'] = 'too much'
        errors = validate_packet_budget('benchmark_recommendation_packet', packet)
        self.assertTrue(any('forbidden key present: full_diff' in item for item in errors))

    def test_summary_line_overflow_produces_validation_error(self) -> None:
        packet = build_context_pack(self.diff_evidence)
        packet['summary'] = ['1', '2', '3', '4', '5', '6']
        errors = validate_packet_budget('context_pack', packet)
        self.assertTrue(any('summary exceeds max_summary_lines=5' in item for item in errors))

    def test_target_overflow_produces_validation_error(self) -> None:
        packet = build_benchmark_recommendation_packet(self.diff_evidence)
        packet['targets'] = packet['targets'] * 4
        errors = validate_packet_budget('benchmark_recommendation_packet', packet)
        self.assertTrue(any('targets exceed max_targets=3' in item for item in errors))


if __name__ == '__main__':
    unittest.main()
