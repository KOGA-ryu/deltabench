from __future__ import annotations

import unittest

from derive.risk_ranker import rank_diff_risk


class RiskRankerTests(unittest.TestCase):
    def test_rank_diff_risk_scores_boundary_crossings_and_missing_tests(self) -> None:
        diff_evidence = {
            "schema_version": "1",
            "diff_id": "feature_x_vs_main",
            "base": "main",
            "head": "feature_x",
            "files_changed": 2,
            "changed_files": [
                {"path": "engine/scanner_engine.py", "status": "modified", "additions": 18, "deletions": 6, "subsystem": "engine"},
                {"path": "core/massive_client.py", "status": "modified", "additions": 5, "deletions": 3, "subsystem": "core"},
            ],
        }

        payload = rank_diff_risk(diff_evidence)

        self.assertGreater(payload["risk_score"], 0.0)
        self.assertEqual(payload["blast_radius"]["boundary_crossings"], 1)
        self.assertFalse(payload["classification"]["tests_touched"])
        self.assertEqual(payload["primary_targets"][0]["path"], "engine/scanner_engine.py")


if __name__ == "__main__":
    unittest.main()
