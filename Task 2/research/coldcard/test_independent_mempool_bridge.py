import copy
import unittest

import independent_mempool_bridge as bridge


def tx(txid, height, value=10):
    return dict(txid=txid, version=2, locktime=0, size=100, weight=400, fee=0,
        vin=[dict(is_coinbase=True)], vout=[dict(scriptpubkey='script', scriptpubkey_address='source', value=value)],
        status=dict(confirmed=True, block_height=height, block_hash='block-' + str(height), block_time=height * 100))


class IndependentBridgeContracts(unittest.TestCase):
    def setUp(self):
        self.record = dict(address='source', payment_txid='reference', cutoff_height=10)

    def test_bridge_is_above_the_partially_saved_block(self):
        old = [tx('newer', 8), tx('a', 5), tx('b', 5)]
        point, height = bridge.choose_bridge(self.record, tx('reference', 10), old)
        self.assertEqual((point['txid'], height), ('newer', 5))

    def test_reference_is_a_safe_bridge_if_only_one_old_block_is_cached(self):
        point, height = bridge.choose_bridge(self.record, tx('reference', 10), [tx('a', 5)])
        self.assertEqual((point['txid'], height), ('reference', 5))

    def test_intra_block_reordering_merges_only_identical_overlaps(self):
        old = {t['txid']: t for t in [tx('a', 5), tx('b', 5), tx('c', 5)]}
        fresh_seen = set()
        outcomes = [bridge.merge_transaction(self.record, t, old, fresh_seen, 5)
            for t in [tx('c', 5), tx('b', 5), tx('d', 5), tx('e', 4)]]
        self.assertEqual(outcomes, [False, False, True, True])
        self.assertEqual(len(old), 5)

    def test_same_txid_with_changed_value_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Conflicting'):
            bridge.merge_transaction(self.record, tx('a', 5, 11), {'a': tx('a', 5)}, set(), 5)

    def test_unknown_newer_block_data_is_not_silently_filled(self):
        with self.assertRaisesRegex(ValueError, 'complete newer block'):
            bridge.merge_transaction(self.record, tx('unknown', 6), {}, set(), 5)

    def test_repeated_native_page_transaction_is_still_rejected(self):
        old = {}; seen = set()
        bridge.merge_transaction(self.record, tx('a', 5), old, seen, 5)
        with self.assertRaisesRegex(ValueError, 'provider-native'):
            bridge.merge_transaction(self.record, tx('a', 5), old, seen, 5)


if __name__ == '__main__':
    unittest.main()
