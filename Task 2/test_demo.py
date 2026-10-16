"""Regression checks for offline replay boundaries and honest verification status."""
from contextlib import redirect_stderr
import copy
import gzip
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import run_demo as demo


class DemoTests(unittest.TestCase):
    def model(self):
        return dict(features=demo.TREE_FEATURES, children_left=[1, -1, -1],
                    children_right=[2, -1, -1], feature=[0, -2, -2],
                    threshold=[16777216.5, -2, -2], candidate_score=[0.5, 0.1, 0.9])

    def test_tree_uses_sklearn_float32_rounding_at_large_integer_boundary(self):
        model = self.model()
        demo.validate_tree(model)
        row = dict.fromkeys(demo.TREE_FEATURES, 1)
        row['input_count'] = 16777217.0  # rounds down to 16777216 in float32
        self.assertEqual(demo.tree_score(row, model)[0], 0.1)
        row['input_count'] = 16777218.0
        self.assertEqual(demo.tree_score(row, model)[0], 0.9)

    def test_model_cycle_and_unreachable_nodes_are_rejected(self):
        model = self.model()
        model['children_left'][0] = 0
        with self.assertRaisesRegex(ValueError, 'Cycle'):
            demo.validate_tree(model)
        model = self.model()
        model['children_left'][0] = model['children_right'][0] = -1
        with self.assertRaisesRegex(ValueError, 'Unreachable'):
            demo.validate_tree(model)

    def test_nonfinite_features_are_refused(self):
        row = dict.fromkeys(demo.TREE_FEATURES, 1)
        row['fee_sat'] = float('nan')
        with self.assertRaisesRegex(ValueError, 'nonfinite'):
            demo.tree_score(row, self.model())

    def test_external_alert_uses_strict_greater_than_not_greater_equal(self):
        document = demo.read_json(demo.ROOT / demo.SCORE_PATHS[1])
        document['results'][0]['source_category_score'] = 0.15
        document['results'][0]['above_fixed_threshold'] = False
        self.assertEqual(len(demo.validate_saved_scores([document])), 1)
        document['results'][0]['above_fixed_threshold'] = True
        with self.assertRaisesRegex(ValueError, 'Strict external threshold'):
            demo.validate_saved_scores([document])

    def test_external_model_changes_and_duplicate_addresses_are_refused(self):
        document = demo.read_json(demo.ROOT / demo.SCORE_PATHS[1])
        with self.assertRaisesRegex(ValueError, 'Repeated external address'):
            demo.validate_saved_scores([document, copy.deepcopy(document)])
        document['fixed_model']['min_samples_leaf'] = 1
        with self.assertRaisesRegex(ValueError, 'configuration changed'):
            demo.validate_saved_scores([document])

    def test_checksum_mismatch_cannot_be_reported_as_verified(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'changed.json'
            path.write_text('{"changed":true}')
            with self.assertRaisesRegex(ValueError, 'SHA256 mismatch'):
                demo.verify_hash(path, '0' * 64)

    def test_coinbase_history_has_no_spending_input_and_reconciles(self):
        address = 'fixture-address'
        counters = dict(tx_count=1, funded_txo_count=1, spent_txo_count=0,
                        funded_txo_sum=50, spent_txo_sum=0)
        metadata = dict(address=address, source_role='fixture_only')
        history = dict(address=address, source_record=metadata, collected_at='2026-10-14T00:00:00Z',
                       audit=dict(pagination_exhausted=True), before=dict(chain_stats=counters),
                       after=dict(chain_stats=counters), transactions=[dict(txid='fixture-tx',
                       status=dict(confirmed=True), vin=[dict(is_coinbase=True, prevout=None)],
                       vout=[dict(scriptpubkey_address=address, value=50)])])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'history.json.gz'
            with gzip.open(path, 'wt') as stream:
                json.dump(history, stream)
            row = dict(address=address, source_record=metadata, collected_at=history['collected_at'],
                       history_sha256=hashlib.sha256(path.read_bytes()).hexdigest(), features=dict(
                       transaction_number=1, total_output_slots=1, total_input_slots=0,
                       total_received_BTC=50, total_sent_BTC=0, balance=50))
            result = demo.audit_history(path, row)
            self.assertEqual(result['coinbase_transactions'], 1)
            self.assertEqual(result['provider_counter_reconciliation']['spent_txo_sum'], 0)

    def test_minimal_demo_is_offline_and_marks_absent_data_and_inference(self):
        with patch('socket.socket', side_effect=AssertionError('Network forbidden in demo')):
            report = demo.run()
        self.assertEqual(report['execution_status'], 'completed')
        by_name = {c['check']: c for c in report['checks']}
        self.assertEqual(by_name['coldcard_data_replay']['status'], 'missing')
        self.assertEqual(by_name['external_forest_inference']['status'], 'unchecked')
        self.assertEqual(by_name['attribution_and_generalization']['status'], 'unchecked')
        self.assertEqual(len(by_name['external_saved_reports']['details']['rows']), 11)
        self.assertEqual(by_name['external_saved_reports']['status'], 'verified')

    def test_existing_report_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'existing.json'
            path.write_text('preserve me')
            with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                demo.main(['--output', str(path)])
            self.assertEqual(path.read_text(), 'preserve me')


if __name__ == '__main__':
    unittest.main()
