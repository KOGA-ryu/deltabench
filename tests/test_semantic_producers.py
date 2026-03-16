from __future__ import annotations

import unittest

from governance.semantic_rules import get_canonical_producer, validate_canonical_field


class SemanticProducerTests(unittest.TestCase):
    def test_risk_producer_is_canonical(self) -> None:
        self.assertTrue(validate_canonical_field('risk', 'derive/risk_ranker.py'))

    def test_blast_radius_producer_is_canonical(self) -> None:
        self.assertTrue(validate_canonical_field('blast_radius', 'derive/blast_radius.py'))

    def test_confidence_producer_is_canonical(self) -> None:
        self.assertTrue(validate_canonical_field('confidence', 'derive/change_significance.py'))

    def test_review_packet_producer_is_canonical(self) -> None:
        self.assertEqual(get_canonical_producer('review_packet'), 'adapters/codex/review_packet.py')

    def test_runtime_relevance_producer_is_canonical(self) -> None:
        self.assertTrue(validate_canonical_field('runtime_relevant_targets', 'derive/runtime_relevance.py'))

    def test_benchmark_packet_producer_is_canonical(self) -> None:
        self.assertEqual(get_canonical_producer('benchmark_recommendation_packet'), 'adapters/codex/benchmark_packet.py')


if __name__ == '__main__':
    unittest.main()
