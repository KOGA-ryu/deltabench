from __future__ import annotations

import json
import tempfile
from io import StringIO
from pathlib import Path
import unittest
from unittest.mock import patch

from tools.bench_handoff import build_handoff_entries, main


class BenchHandoffTests(unittest.TestCase):
    def setUp(self) -> None:
        self.packet = {
            'schema_version': '1',
            'packet_type': 'benchmark_recommendation',
            'diff_id': 'feature_x_vs_main',
            'chain_id': 'chain-abc',
            'review_target': 'engine/scanner_engine.py',
            'targets': [
                {
                    'path': 'engine/scanner_engine.py',
                    'review_target': 'engine/scanner_engine.py',
                    'chain_id': 'chain-abc',
                    'reason': ['touches runtime subsystem'],
                    'recommended_bluebench_action': 'rerun_hotspot_probe',
                    'confidence': 'medium',
                }
            ],
            'confidence': 'medium',
        }

    def test_valid_packet_maps_to_expected_bluebench_command(self) -> None:
        entries = build_handoff_entries(self.packet)
        self.assertEqual(entries[0]['command'], ['bluebench', 'compare', '<baseline_run_id>', '<current_run_id>', '--chain-id', 'chain-abc', '--target', 'engine/scanner_engine.py'])

    def test_unknown_action_produces_clear_fallback(self) -> None:
        packet = dict(self.packet)
        packet['targets'] = [dict(self.packet['targets'][0], recommended_bluebench_action='unknown_action')]
        entries = build_handoff_entries(packet)
        self.assertFalse(entries[0]['known_action'])
        self.assertIn('TODO: map BlueBench action unknown_action', entries[0]['command'][0])

    def test_missing_packet_fields_produce_validation_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            packet_path = Path(tmp) / 'packet.json'
            packet_path.write_text(json.dumps({'packet_type': 'benchmark_recommendation'}), encoding='utf-8')
            stream = StringIO()
            exit_code = main(['--packet', str(packet_path)], stdout=stream)
            self.assertEqual(exit_code, 2)
            self.assertIn('missing required key: targets', stream.getvalue())

    def test_explain_mode_does_not_execute_commands(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            packet_path = Path(tmp) / 'packet.json'
            packet_path.write_text(json.dumps(self.packet), encoding='utf-8')
            stream = StringIO()
            with patch('tools.bench_handoff.subprocess.run') as run_mock:
                exit_code = main(['--packet', str(packet_path)], stdout=stream)
            self.assertEqual(exit_code, 0)
            run_mock.assert_not_called()
            payload = json.loads(stream.getvalue())
            self.assertIn('formatted_summary', payload)

    def test_execute_mode_uses_subprocess_safely(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            packet_path = Path(tmp) / 'packet.json'
            packet_path.write_text(json.dumps(self.packet), encoding='utf-8')
            stream = StringIO()
            with patch('tools.bench_handoff.subprocess.run') as run_mock:
                run_mock.return_value.returncode = 0
                run_mock.return_value.stdout = 'ok'
                run_mock.return_value.stderr = ''
                exit_code = main(['--packet', str(packet_path), '--execute'], stdout=stream)
            self.assertEqual(exit_code, 0)
            run_mock.assert_called_once_with(
                ['bluebench', 'compare', '<baseline_run_id>', '<current_run_id>', '--chain-id', 'chain-abc', '--target', 'engine/scanner_engine.py'],
                capture_output=True,
                text=True,
                check=False,
            )
            payload = json.loads(stream.getvalue())
            self.assertIn('execution', payload)


if __name__ == '__main__':
    unittest.main()
