from __future__ import annotations

import unittest

from adapters.codex.review_packet import build_review_packet


class ReviewPacketTests(unittest.TestCase):
    def test_review_packet_is_compact_and_machine_readable(self) -> None:
        diff_evidence = {
            'schema_version': '1',
            'diff_id': 'feature_x_vs_main',
            'base': 'main',
            'head': 'feature_x',
            'files_changed': 2,
            'changed_files': [
                {'path': 'engine/scanner_engine.py', 'status': 'modified', 'additions': 18, 'deletions': 6, 'subsystem': 'engine'},
                {'path': 'tests/test_engine.py', 'status': 'added', 'additions': 4, 'deletions': 0, 'subsystem': 'tests'},
            ],
        }

        packet = build_review_packet(diff_evidence)

        self.assertEqual(packet['schema_version'], '1')
        self.assertEqual(packet['packet_type'], 'review_packet')
        self.assertTrue(packet['primary_risk_targets'])
        self.assertTrue(packet['reason'])
        self.assertIn('boundary_crossings', packet['blast_radius'])
        self.assertTrue(packet['recommended_next_actions'])
        self.assertIsInstance(packet['low_risk_files'], list)
        self.assertIsInstance(packet['primary_risk_targets'][0]['reasons'], list)
        self.assertIn('confidence', packet['primary_risk_targets'][0])
        self.assertIsInstance(packet['review_map'], list)


if __name__ == '__main__':
    unittest.main()
