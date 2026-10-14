import unittest
from reconcile_training_profiles import probes


class CoinbaseProfileTests(unittest.TestCase):
    def test_coinbase_receipt_has_no_sender_or_fee(self):
        tx = dict(vin=[dict(is_coinbase=True, prevout=None)],
                  vout=[dict(scriptpubkey_address='donation', value=500)],
                  fee=0, status=dict(block_time=1000))
        values, _ = probes('donation', [tx])
        self.assertEqual(values['total_received_BTC'], 500)
        self.assertEqual(values['receipt_transactions'], 1)
        self.assertEqual(values['sent_counters'], 0)
        self.assertEqual(values['transaction_fee'], 0)
        self.assertEqual(values['payment_transactions'], 0)

    def test_coinbase_then_spend(self):
        receipt = dict(vin=[dict(is_coinbase=True, prevout=None)],
                       vout=[dict(scriptpubkey_address='donation', value=500)],
                       fee=0, status=dict(block_time=1000))
        spend = dict(vin=[dict(is_coinbase=False, prevout=dict(scriptpubkey_address='donation', value=500))],
                     vout=[dict(scriptpubkey_address='recipient', value=490)],
                     fee=10, status=dict(block_time=2000))
        values, _ = probes('donation', [receipt, spend])
        self.assertEqual(values['balance'], 0)
        self.assertEqual(values['total_sent_BTC'], 500)
        self.assertEqual(values['transaction_fee'], 10)
        self.assertEqual(values['received_counters'], 1)
        self.assertEqual(values['lifetime'], 1000)


if __name__ == '__main__':
    unittest.main()
