import unittest
from unittest.mock import patch
import numpy as np
import pandas as pd
import train_exploratory as train
import extract_candidate_groups as groups

class ExperimentTests(unittest.TestCase):
    def test_chronological_split_separates_heights_and_keeps_classes(self):
        df=pd.DataFrame({'relation':['unattributed']*40+['direct_parent_candidate']*40,
                         'block_height':[960180]*20+[960733]*20+[960185]*20+[960733]*20})
        splits=list(train.partitions(df))
        _,a,b=splits[1]
        self.assertFalse(set(a)&set(b))
        self.assertTrue((df.iloc[a].block_height<960377).all())
        self.assertTrue((df.iloc[b].block_height>=960377).all())
        self.assertFalse({'txid','block_height','relation'}&set(train.FEATURES))
    def test_metrics_expose_missed_positives(self):
        m=train.metrics(np.array([0,0,1,1]),np.array([0,1,0,0]))
        self.assertEqual(m['true_positive_proxy'],0)
        self.assertEqual(m['false_negative_proxy'],2)
        self.assertEqual(m['false_positive_proxy'],1)
    def test_shared_collector_merges_candidate_groups(self):
        a,b=sorted(groups.SEEDS)[:2]
        rows=[(1,{'hash':a,'tx_index':90,'inputs':[{'prev_out':{'addr':'collector','tx_index':10}}]}),
              (2,{'hash':b,'tx_index':91,'inputs':[{'prev_out':{'addr':'collector','tx_index':11}}]}),
              (0,{'hash':'parent-a','tx_index':10}),
              (0,{'hash':'parent-b','tx_index':11})]
        with patch.object(groups,'transactions',lambda path:iter(rows)):
            result=groups.grouping('fixture',{'parents':[{'txid':'parent-a'},{'txid':'parent-b'}]})
        self.assertEqual(len(result['group_counts']),1)
        self.assertEqual(sum(result['group_counts'].values()),2)
    def test_shared_parent_merges_seeds_without_shared_collector(self):
        a,b=sorted(groups.SEEDS)[:2]
        rows=[(1,{'hash':a,'tx_index':90,'inputs':[{'prev_out':{'addr':'a','tx_index':10}}]}),
              (2,{'hash':b,'tx_index':91,'inputs':[{'prev_out':{'addr':'b','tx_index':10}}]}),
              (0,{'hash':'parent','tx_index':10})]
        with patch.object(groups,'transactions',lambda path:iter(rows)):
            r=groups.grouping('fixture',{'parents':[{'txid':'parent'}]})
        self.assertEqual(r['candidates'][0]['descendant_seed_txids'],[a,b])
    def test_group_coverage_mismatch_refused(self):
        with patch.object(groups,'transactions',lambda path:iter([])):
            with self.assertRaises(ValueError):
                groups.grouping('fixture',{'parents':[{'txid':'missing'}]})

if __name__=='__main__':unittest.main()
