import copy
import unittest
from snapshot_storage_profiles import features_at, instant


class SnapshotTests(unittest.TestCase):
    def setUp(self):
        def tx(key, date, received, spent):
            return {'txid': key, 'address': 'a', 'block_time_utc': date,
                    'address_received_sat': received, 'address_spent_sat': spent}
        self.doc = {'seed': {'address': 'a'}, 'history': {
            'address_stats_before': {'chain_stats': {'tx_count': 2}},
            'address_stats_after': {'chain_stats': {'tx_count': 2}},
            'summary': {'coverage': 'count_matches_stable_stats'},
            'transactions': [tx('past', '2025-03-01T00:00:00Z', 100, 0),
                             tx('future', '2025-04-01T00:00:00Z', 0, 100)]}}
        self.when = instant('2025-03-31T23:59:00Z')

    def test_future_spend_does_not_change_snapshot_balance(self):
        first = features_at(self.doc, self.when)
        self.doc['history']['transactions'][1]['address_received_sat'] = 999999
        self.assertEqual(features_at(self.doc, self.when), first)
        self.assertEqual(first['balance_sat'], 100)
        self.assertEqual(first['transaction_count'], 1)

    def test_boundary_included_and_no_prior_activity_null_age(self):
        when = instant('2025-03-01T00:00:00Z')
        self.assertEqual(features_at(self.doc, when)['transaction_count'], 1)
        self.assertIsNone(features_at(self.doc, instant('2025-02-01T00:00:00Z'))[
            'days_since_last_observed_transaction'])

    def test_partial_and_duplicate_histories_rejected(self):
        doc = copy.deepcopy(self.doc)
        doc['history']['summary']['coverage'] = 'partial'
        with self.assertRaises(ValueError): features_at(doc, self.when)
        self.doc['history']['transactions'][1]['txid'] = 'past'
        with self.assertRaises(ValueError): features_at(self.doc, self.when)

    def test_timezone_required(self):
        with self.assertRaises(ValueError): instant('2025-03-31T23:59:00')
