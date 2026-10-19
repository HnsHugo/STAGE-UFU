"""Scientific boundary tests for collection-pattern descriptions and saved data."""
import gzip
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from collection_patterns import analyze, describe


def tx(name, when=100, source='source', target='collector', value=1000,
       fee=100, weight=401, other_outputs=None, height=1):
    outputs = [dict(scriptpubkey_address=target, value=value)] + (other_outputs or [])
    return dict(txid=name, status=dict(confirmed=True, block_time=when, block_height=height),
                vin=[dict(txid='parent_'+name, vout=0,
                          prevout=dict(scriptpubkey_address=source, value=value+fee))],
                vout=outputs, fee=fee, weight=weight)


class PatternTests(unittest.TestCase):
    def test_future_spend_does_not_change_prefix(self):
        receipt = tx('a')
        future = tx('b', when=200, source='collector', target='elsewhere', value=900)
        self.assertEqual(describe('collector', [receipt], 200),
                         describe('collector', [receipt, future], 200))

    def test_window_keeps_prior_funding_in_balance_but_not_activity(self):
        spend = tx('b', when=150, source='collector', target='elsewhere', value=900)
        result = describe('collector', [tx('a', when=50), spend], 200, start=100)
        self.assertEqual(result['received_sat'], 0)
        self.assertEqual(result['receipt_transaction_count'], 0)
        self.assertEqual(result['spending_transaction_count'], 1)
        self.assertEqual(result['observed_balance_sat'], 0)

    def test_window_start_inclusive_and_cutoff_exclusive(self):
        result = describe('collector', [tx('a', when=100), tx('b', when=200)], 200, start=100)
        self.assertEqual(result['receipt_transaction_count'], 1)
        self.assertEqual(result['received_sat'], 1000)

    def test_empty_activity_keeps_missing_ratios_and_existing_balance(self):
        result = describe('collector', [tx('a', when=50)], 200, start=100)
        self.assertIsNone(result['receipt_top_block_transaction_share'])
        self.assertIsNone(result['incoming_transaction_median_fee_rate_sat_vbyte'])
        self.assertEqual(result['observed_balance_sat'], 1000)

    def test_invalid_window_rejected(self):
        with self.assertRaises(ValueError):
            describe('collector', [], 100, start=100)

    def test_coinbase_prevout_null_and_fee_policy(self):
        receipt = tx('a')
        receipt['vin'] = [dict(is_coinbase=True, prevout=None)]
        result = describe('collector', [receipt], 200)
        self.assertEqual(result['funding_transaction_distinct_input_addresses'], 0)
        self.assertEqual(result['single_output_external_funding_transaction_count'], 0)
        self.assertIsNone(result['incoming_transaction_median_fee_rate_sat_vbyte'])

    def test_multi_output_does_not_count_as_no_change_proxy(self):
        receipt = tx('a', other_outputs=[dict(value=1, scriptpubkey_address='change')])
        result = describe('collector', [receipt], 200)
        self.assertEqual(result['single_output_external_funding_transaction_count'], 0)
        self.assertEqual(result['received_sat'], 1000)

    def test_input_cooccurrence_is_not_a_victim_count(self):
        a, b = tx('a'), tx('b', height=2)
        result = describe('collector', [a, b], 200)
        self.assertEqual(result['funding_transaction_distinct_input_addresses'], 1)
        self.assertEqual(result['receipt_transaction_count'], 2)
        self.assertEqual(result['receipt_top_block_transaction_share'], 0.5)
        self.assertNotIn('victim_count', result)

    def test_weight_is_rounded_up_to_vbytes(self):
        result = describe('collector', [tx('a', fee=101, weight=401)], 200)
        self.assertEqual(result['incoming_transaction_median_fee_rate_sat_vbyte'], 1)

    def test_self_change_and_spending_are_separate(self):
        spend = tx('b', source='collector', target='elsewhere', value=800, fee=100,
                   other_outputs=[dict(scriptpubkey_address='collector', value=100)])
        spend['vin'][0]['prevout']['value'] = 1000
        result = describe('collector', [tx('a'), spend], 200)
        self.assertEqual(result['observed_balance_sat'], 100)
        self.assertEqual(result['spending_transaction_distinct_other_output_addresses'], 1)
        self.assertEqual(result['single_output_external_funding_transaction_count'], 1)

    def test_duplicate_transactions_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Duplicate transaction'):
            describe('collector', [tx('a'), tx('a')], 200)

    def test_repeated_consumed_outpoint_rejected(self):
        a, b = tx('a'), tx('b')
        b['vin'] = a['vin']
        with self.assertRaisesRegex(ValueError, 'Repeated consumed outpoint'):
            describe('collector', [a, b], 200)

    def test_negative_or_float_values_rejected(self):
        for value in (-1, 1.5, True):
            with self.subTest(value=value), self.assertRaises(ValueError):
                describe('collector', [tx('a', value=value)], 200)

    def test_missing_pre_window_funding_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Negative observed balance'):
            describe('collector', [tx('a', source='collector', target='elsewhere')], 200)

    def test_unrelated_and_unconfirmed_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Unrelated'):
            describe('collector', [tx('a', target='elsewhere')], 200)
        receipt = tx('a')
        receipt['status']['confirmed'] = False
        with self.assertRaisesRegex(ValueError, 'Confirmed'):
            describe('collector', [receipt], 200)

    def test_saved_observations_reproduce_report_and_remain_one_case(self):
        root = Path(__file__).resolve().parent
        histories = root / 'collection_pilot_20261019'
        saved = json.loads((histories / 'patterns_asof_20261010.json').read_text())
        with tempfile.TemporaryDirectory() as directory:
            report = analyze(root / 'hardware_case_registry_20261019.json', histories,
                             saved['cutoff_exclusive_utc'], Path(directory) / 'new.json')
        self.assertEqual(saved, report)
        self.assertEqual(len({r['case_group'] for r in report['rows']}), 1)
        self.assertTrue(all(r['hardware_control'] == 'unknown' for r in report['rows']))
        for row in report['rows']:
            raw = (histories / row['file']).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), row['history_sha256'])
            self.assertTrue(json.loads(gzip.decompress(raw))['audit']['coverage_complete_by_provider_counters'])


if __name__ == '__main__':
    unittest.main()
