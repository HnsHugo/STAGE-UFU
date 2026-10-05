import unittest
from collect_history import sample, transaction_row

A = 'test-address'


def tx(txid='one'):
    return {'txid': txid, 'weight': 401, 'fee': 100,
        'vin': [{'prevout': {'scriptpubkey_address': A, 'value': 1000}},
                {'prevout': {'scriptpubkey_address': 'other', 'value': 500}}],
        'vout': [{'scriptpubkey_address': A, 'value': 200},
                 {'scriptpubkey_address': 'other', 'value': 1200}],
        'status': {'confirmed': True, 'block_height': 100, 'block_time': 1700000000}}


def stats(count):
    return {'address': A, 'chain_stats': {'tx_count': count, 'funded_txo_sum': 2000, 'spent_txo_sum': 1000}}


class HistoryTests(unittest.TestCase):
    def test_amounts_are_address_specific_but_fee_is_transaction_wide(self):
        r = transaction_row(A, tx())
        self.assertEqual((r['address_received_sat'], r['address_spent_sat'], r['address_net_sat']), (200, 1000, -800))
        self.assertEqual(r['vsize_vb'], 101)
        self.assertAlmostEqual(r['fee_rate_sat_vb'], 100/101)
        self.assertEqual(r['transaction_fee_sat'], 100)

    def getter(self, responses, paths=None):
        queue = iter(responses)
        def get(path):
            if paths is not None:
                paths.append(path)
            return next(queue), {'url': path, 'retrieved_at_utc': 'test'}
        return get

    def test_short_page_is_not_complete_if_count_disagrees(self):
        for expected, label in [(1, 'count_matches_stable_stats'), (100, 'partial')]:
            r = sample(A, getter=self.getter([stats(expected), [tx()], stats(expected)]), sleeper=lambda _: None)
            self.assertEqual(r['summary']['coverage'], label)

    def test_pagination_cursor_and_change_detection(self):
        paths = []
        r = sample(A, 2, self.getter([stats(26), [tx(str(i)) for i in range(25)], [tx('last')], stats(27)], paths), lambda _: None)
        self.assertTrue(paths[2].endswith('/24'))
        self.assertEqual(r['summary']['observed_tx_count'], 26)
        self.assertEqual(r['summary']['coverage'], 'stats_changed')

    def test_duplicate_and_unconfirmed_transactions_rejected(self):
        unconfirmed = tx()
        unconfirmed['status']['confirmed'] = False
        for page in ([tx(), tx()], [unconfirmed]):
            with self.assertRaises(ValueError):
                sample(A, getter=self.getter([stats(2), page]), sleeper=lambda _: None)

    def test_zero_history_and_coinbase(self):
        r = sample(A, getter=self.getter([stats(0), [], stats(0)]), sleeper=lambda _: None)
        self.assertEqual(r['summary']['oldest_observed_utc'], '')
        t = tx()
        t['vin'] = [{'is_coinbase': True}]
        t['fee'] = 0
        self.assertEqual(transaction_row(A, t)['address_spent_sat'], 0)


if __name__ == '__main__':
    unittest.main()
