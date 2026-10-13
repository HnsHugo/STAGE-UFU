import unittest
from extract_asof_features import features_asof


def tx(name,time,received=0,spent=0,fee=100):
    return dict(txid=name,status=dict(confirmed=True,block_time=time),
                vin=[dict(prevout=dict(scriptpubkey_address='a',value=spent))] if spent else [],
                vout=[dict(scriptpubkey_address='a',value=received)] if received else [],weight=400,fee=fee)


class SnapshotTests(unittest.TestCase):
    def test_future_spending_does_not_change_snapshot(self):
        receipt=tx('receipt',1000,received=10000)
        original=features_asof('a',[receipt],2000,1)
        with_future=features_asof('a',[receipt,tx('future',3000,spent=10000)],2000,1)
        self.assertEqual(original,with_future)
        self.assertEqual(original['balance_before_cutoff_sat'],10000)

    def test_cutoff_is_exclusive_and_window_start_inclusive(self):
        result=features_asof('a',[tx('start',200000-86400,received=10),tx('end',200000,received=20)],200000,1)
        self.assertEqual(result['received_sat'],10)
        self.assertEqual(result['transaction_count'],1)

    def test_receiver_fees_not_used_as_outgoing_policy(self):
        result=features_asof('a',[tx('receipt',1000,received=10,fee=99999)],2000,1)
        self.assertIsNone(result['median_outgoing_transaction_fee_rate'])

    def test_pre_window_receipts_count_in_balance_only(self):
        result=features_asof('a',[tx('old',1,received=100),tx('recent',199999,received=10)],200000,1)
        self.assertEqual(result['balance_before_cutoff_sat'],110)
        self.assertEqual(result['received_sat'],10)


if __name__=='__main__':unittest.main()
