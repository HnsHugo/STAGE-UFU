"""Reject source/anchor/evidence errors without provider requests or model imports."""
from copy import deepcopy
import unittest
from unittest.mock import patch

import build_cryptobilis_source_protocol as build


def tx(key='payment', source='sourceA', value=100, when=100, height=10):
    return dict(txid=build.hashed(key), fee=1,
                status=dict(confirmed=True,block_height=height,block_hash=build.hashed('block'+str(height)),block_time=when),
                vin=[dict(txid=build.hashed('funding'+key),vout=0,
                          prevout=dict(scriptpubkey_address=source,value=value))],
                vout=[dict(scriptpubkey_address='collector',value=value-1)])


def history(transactions):
    outputs=[o for t in transactions for o in t['vout'] if o.get('scriptpubkey_address')=='collector']
    inputs=[v['prevout'] for t in transactions for v in t['vin'] if v.get('prevout') and v['prevout'].get('scriptpubkey_address')=='collector']
    stats=dict(tx_count=len(transactions),funded_txo_count=len(outputs),funded_txo_sum=sum(o['value'] for o in outputs),
               spent_txo_count=len(inputs),spent_txo_sum=sum(v['value'] for v in inputs))
    h=dict(address='collector',provider='https://blockstream.info/api',transactions=transactions,
           before=dict(chain_stats=stats),after=dict(chain_stats=deepcopy(stats)))
    h['audit']=build.check_history('collector',transactions,h['before'],h['after'],True)
    return h


class SourceReadinessTests(unittest.TestCase):
    def setUp(self):
        self.refs=[dict(address='collector')]
        self.blocks=[dict(height=10,hash=build.hashed('block10'),time=100)]

    def recover(self,transactions):
        return build.recover({'collector':history(transactions)},self.refs,self.blocks,100,200)

    def test_multiple_utxos_remain_one_address_and_unknown_labels(self):
        payment=tx()
        payment['vin'].append(dict(txid=build.hashed('otherfunding'),vout=1,
                                   prevout=dict(scriptpubkey_address='sourceA',value=50)))
        payment['vout'][0]['value']=149
        with patch('socket.create_connection',side_effect=AssertionError('Unexpected network')):
            rows,evidence,audit,outside=self.recover([payment])
        self.assertEqual((len(rows),len(evidence)),(1,2))
        self.assertEqual(rows[0]['reference_input_count'],2)
        self.assertTrue(all(v is None for v in rows[0]['labels'].values()))
        self.assertIsNone(rows[0]['features'])
        self.assertEqual(rows[0]['case_relation'],'graph_candidate')
        self.assertNotIn('sourceA',build.encoded(rows).decode())
        self.assertEqual(audit['multi_input_payments'],1)

    def test_distinct_input_addresses_are_not_collapsed_to_a_wallet(self):
        payment=tx()
        payment['vin'].append(dict(txid=build.hashed('otherfunding'),vout=0,
                                   prevout=dict(scriptpubkey_address='sourceB',value=50)))
        payment['vout'][0]['value']=149
        rows,evidence,audit,_=self.recover([payment])
        self.assertEqual((len(rows),len(evidence)),(2,2))
        self.assertEqual(audit['multi_address_payments'],1)

    def test_event_end_is_exclusive_and_outside_source_is_retained(self):
        rows,evidence,audit,outside=self.recover([tx(),tx('later','sourceB',when=200,height=11)])
        self.assertEqual(len(rows),1)
        self.assertEqual(outside,{'sourceB'})
        self.assertEqual(audit['outside_window_payments'],1)
        self.assertEqual(audit['outside_window_source_overlap'],0)

    def test_reference_value_or_fee_mismatch_fails(self):
        payment=tx();payment['fee']=2
        with self.assertRaisesRegex(ValueError,'input/output/fee'):
            self.recover([payment])

    def test_wrong_anchor_and_unconfirmed_reference_fail(self):
        payment=tx();payment['status']['block_hash']=build.hashed('different')
        with self.assertRaisesRegex(ValueError,'block anchor'):
            self.recover([payment])
        payment=tx();payment['status']['confirmed']=False
        with self.assertRaisesRegex(ValueError,'Unconfirmed'):
            self.recover([payment])

    def test_missing_source_prevout_cannot_be_guessed(self):
        payment=tx();payment['vin'][0]['prevout']=None
        with self.assertRaisesRegex(ValueError,'Unresolved source'):
            self.recover([payment])

    def test_duplicate_reference_or_spent_outpoint_fails(self):
        payment=tx()
        with self.assertRaisesRegex(ValueError,'Duplicate transactions'):
            self.recover([payment,deepcopy(payment)])
        other=tx('other');other['vin'][0]['txid']=payment['vin'][0]['txid']
        with self.assertRaisesRegex(ValueError,'Repeated spent outpoint'):
            self.recover([payment,other])

    def test_collector_self_input_is_not_promoted_to_source_candidate(self):
        with self.assertRaisesRegex(ValueError,'Collector self-input'):
            self.recover([tx(source='collector')])

    def test_changed_provider_counters_and_incomplete_collector_fail(self):
        h=history([tx()]);h['after']['chain_stats']['tx_count']=2
        with self.assertRaisesRegex(ValueError,'does not reconcile'):
            build.recover({'collector':h},self.refs,self.blocks,100,200)
        h=history([tx()]);h['audit']['pagination_exhausted']=False
        with self.assertRaisesRegex(ValueError,'does not reconcile'):
            build.recover({'collector':h},self.refs,self.blocks,100,200)

    def test_source_order_is_deterministic_and_earliest_reference_is_fixed(self):
        first=tx('a');second=tx('b')
        rows,evidence,audit,_=self.recover([first,second])
        reverse=self.recover([second,first])
        self.assertEqual((rows,evidence,audit),reverse[:3])
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]['reference_txid_sha256'],build.hashed(min(first['txid'],second['txid'])))


if __name__=='__main__':
    unittest.main()
