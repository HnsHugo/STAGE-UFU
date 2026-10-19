import unittest
import pandas as pd
from audit_dataset import audit
from train_exploratory import FEATURES

class DatasetTests(unittest.TestCase):
    def setUp(self):
        rows=[]
        for name in ['a','b']:
            r={k:1 for k in FEATURES}
            r.update(txid=name,relation='direct_parent_candidate',block_height=10,is_coinbase=0,
                     input_total_sat=100,output_total_sat=90,fee_sat=10,vsize_vb=10,fee_rate_sat_vb=1)
            rows.append(r)
        self.df=pd.DataFrame(rows)
        self.manifest={'status':'complete','transaction_count':2,'relation_counts':{'direct_parent_candidate':2},'parent_report_sha256':'same'}
        self.groups={'parent_report_sha256':'same','candidates':[{'txid':'a','group_id':'g1'},{'txid':'b','group_id':'g2'}],'group_counts':{'g1':1,'g2':1}}
    def test_consistent_fixture(self):
        self.assertEqual(audit(self.df,self.manifest,self.groups)['status'],'consistent')
    def test_balance_error_refused(self):
        self.df.loc[0,'fee_sat']=20
        with self.assertRaises(ValueError):audit(self.df,self.manifest,self.groups)
    def test_rate_error_refused(self):
        self.df.loc[0,'fee_rate_sat_vb']=100
        with self.assertRaises(ValueError):audit(self.df,self.manifest,self.groups)
    def test_incomplete_manifest_refused(self):
        self.manifest['status']='incomplete'
        with self.assertRaises(ValueError):audit(self.df,self.manifest,self.groups)

if __name__=='__main__':unittest.main()
