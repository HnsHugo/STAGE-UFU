"""Failure-oriented guards for temporal boundaries, overlap and score replay."""
import unittest

from experiment import partition,recount_features
from verify_results import rankings,replay


class ScientificGuards(unittest.TestCase):
    def test_reference_block_is_excluded(self):
        row=dict(transaction_id='a',height=100,received=[],spent=[],spending_tx_fee_sat=None,spending_tx_vsize_vb=None)
        with self.assertRaisesRegex(ValueError,'Reference/future'):
            recount_features([row],100)

    def test_duplicate_transaction_cannot_inflate_activity(self):
        row=dict(transaction_id='a',height=99,received=[],spent=[],spending_tx_fee_sat=None,spending_tx_vsize_vb=None)
        with self.assertRaisesRegex(ValueError,'Repeated'):
            recount_features([row,row],100)

    def test_empty_prefix_keeps_undefined_activity_and_fees(self):
        f=recount_features([],100)
        self.assertEqual(f['balance_sat'],0)
        self.assertIsNone(f['blocks_since_last_activity'])
        self.assertIsNone(f['median_spending_tx_fee_rate_sat_vb'])

    def test_reference_prior_roles_connect_transitively(self):
        tokens={'cb:a':[('any_tx','x')], 'cc:b':[('any_tx','x'),('address','z')],
                'cc:bounded':[('address','z')], 'cc:clear':[('address','other')]}
        self.assertEqual(partition(tokens),[['cb:a','cc:b','cc:bounded'],['cc:clear']])

    def test_missing_vector_does_not_break_known_reference_link(self):
        self.assertEqual(partition({'cb:incomplete':[('reference','r')],
            'cc:complete':[('reference','r')]}),[['cb:incomplete','cc:complete']])

    def test_ranking_ties_are_grouped(self):
        self.assertEqual(rankings([1,0,1,0],[.9,.9,.1,.1]),{'average_precision':.5,'roc_auc':.5})
        self.assertEqual(rankings([1,0],[2,1]),{'average_precision':1.0,'roc_auc':1.0})

    def test_replay_casts_to_float32_before_branch(self):
        names=['x'+str(i) for i in range(14)]
        model={'feature_names':names+[n+'__missing' for n in names],
            'medians':{n:0 for n in names},'nodes':[
                {'left':1,'right':2,'feature_index':0,'threshold':16777216.5},
                {'left':-1,'positive_probability':.1}, {'left':-1,'positive_probability':.9}]}
        row={'features':{n:0 for n in names}};row['features'][names[0]]=16777217
        self.assertEqual(replay(model,row),(.1,1,[0,1]))
        with self.assertRaisesRegex(ValueError,'unavailable'):
            replay(model,{'features':None})


if __name__=='__main__':unittest.main()
