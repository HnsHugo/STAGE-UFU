import copy
import json
from pathlib import Path
import tempfile
import unittest

from rank_block_recipients import (FEATURES, add_rows, evaluate, rank_interval,
                                   recipient_features, reproduce, validate_block, verify_history_receipts)


def tx(name, outputs, source='source'):
    return dict(hash=name, vin_sz=1, vout_sz=len(outputs), inputs=[dict(prev_out=dict(addr=source,n=0,tx_index=1))],
                out=[dict(addr=a,value=v,n=i) for i,(a,v) in enumerate(outputs)])


def miner():
    result = tx('miner',[('miner',100000)])
    result['inputs'] = [dict(prev_out=dict(n=4294967295,tx_index=0))]
    return result


class RankingTests(unittest.TestCase):
    def test_multiple_outputs_to_one_recipient_count_once(self):
        rows = recipient_features([tx('a',[('collector',10),('collector',20)])])
        self.assertEqual(rows['collector']['receipt_transaction_count'],1)
        self.assertEqual(rows['collector']['received_sat'],30)
        self.assertEqual(rows['collector']['single_output_external_funding_transaction_count'],0)

    def test_coinbase_zero_value_and_unaddressed_outputs_excluded(self):
        rows = recipient_features([miner(),tx('a',[('zero',0),(None,10),('valid',5)])])
        self.assertEqual(set(rows),{'valid'})

    def test_self_change_is_not_external_single_output(self):
        row = recipient_features([tx('a',[('collector',10)],source='collector')])['collector']
        self.assertEqual(row['receipt_transaction_count'],1)
        self.assertEqual(row['single_output_external_funding_transaction_count'],0)

    def test_missing_input_address_cannot_establish_external_funding(self):
        row = recipient_features([tx('a',[('collector',10)],source=None)])['collector']
        self.assertEqual(row['single_output_external_funding_transaction_count'],0)

    def test_tie_interval_not_broken_by_reference_address_name(self):
        rows = recipient_features([tx('a',[('z_reference',10)]),tx('b',[('a_other',10)])])
        rank = rank_interval(rows,'z_reference',FEATURES[0])
        self.assertEqual((rank['rank_best'],rank['rank_worst']),(1,2))

    def test_unknown_high_score_recipient_keeps_priority_over_reference(self):
        rows = recipient_features([tx('a',[('known',10)]),tx('b',[('other',10)]),tx('c',[('other',10)])])
        result = evaluate(rows,['known'])['baselines'][0]
        self.assertEqual(result['top10'][0]['address'],'other')
        self.assertEqual(result['targets'][0]['rank_best'],2)

    def test_prefix_snapshot_does_not_change_when_later_block_is_added(self):
        total = recipient_features([tx('a',[('known',10)])])
        first = evaluate(total,['known'])
        expected = copy.deepcopy(first)
        add_rows(total,recipient_features([tx('b',[('other',10)]),tx('c',[('other',10)])]))
        self.assertEqual(first,expected)
        self.assertEqual(evaluate(total,['known'])['baselines'][0]['targets'][0]['rank_best'],2)

    def test_duplicate_transaction_rejected(self):
        t = tx('a',[('known',10)])
        with self.assertRaises(ValueError):recipient_features([t,t])

    def test_incomplete_or_duplicate_block_rejected(self):
        reference=dict(hash='block',height=1,time=2)
        block=dict(**reference,main_chain=True,n_tx=2,tx=[miner()])
        with self.assertRaises(ValueError):validate_block(block,reference)
        block['tx']=[miner(),miner()]
        with self.assertRaises(ValueError):validate_block(block,reference)

    def test_exact_receipt_amount_disagreement_rejected(self):
        block=dict(hash='block',tx=[tx('a',[('known',10)])])
        history=dict(address='known',transactions=[dict(txid='a',status=dict(block_hash='block'),
                     vout=[dict(scriptpubkey_address='known',value=11)])])
        with self.assertRaises(ValueError):verify_history_receipts(block,history)

    def test_truncated_transaction_cannot_remove_background_competitors(self):
        reference = dict(hash='block',height=1,time=2)
        ordinary = tx('a',[('known',10),('other',50)])
        ordinary['out'].pop()
        block = dict(**reference,main_chain=True,n_tx=2,tx=[miner(),ordinary])
        with self.assertRaisesRegex(ValueError,'Truncated'):
            validate_block(block,reference)

    def test_future_spending_metadata_does_not_change_ranking_features(self):
        ordinary = tx('a',[('known',10)])
        before = recipient_features([ordinary])
        ordinary['out'][0].update(spent=True,spending_outpoints=[dict(tx_index=999999999,n=0)])
        self.assertEqual(before,recipient_features([ordinary]))

    def test_saved_full_population_rankings_reproduce_offline(self):
        root = Path(__file__).resolve().parent
        result = reproduce(root/'central_results_20261020',root/'central_protocol_20261020.json')
        self.assertEqual(result['status'],'passed')
        self.assertEqual(result['cohorts'],2)

    def test_modified_population_summary_rejected(self):
        root = Path(__file__).resolve().parent
        report = json.loads((root/'central_results_20261020/summary.json').read_text())
        with tempfile.TemporaryDirectory() as directory:
            dest = Path(directory)
            (dest/'summary.json').write_text(json.dumps(report))
            (dest/report['score_summary']['file']).write_bytes(b'altered')
            with self.assertRaisesRegex(ValueError,'checksum'):
                reproduce(dest,root/'central_protocol_20261020.json')


if __name__=='__main__':unittest.main()
