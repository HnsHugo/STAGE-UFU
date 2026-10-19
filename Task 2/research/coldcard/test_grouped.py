import unittest
import pandas as pd
from train_grouped import validate_groups,assign_folds

class GroupTests(unittest.TestCase):
    def setUp(self):
        self.df=pd.DataFrame({'txid':['a','b','c','d','e'],
            'relation':['direct_parent_candidate']*3+['unattributed']*2})
        self.groups={'parent_report_sha256':'abc','candidates':[
            {'txid':'a','group_id':'one'},{'txid':'b','group_id':'one'},
            {'txid':'c','group_id':'two'}],'group_counts':{'one':2,'two':1}}
        self.manifest={'parent_report_sha256':'abc'}
    def test_group_members_always_share_fold(self):
        m=validate_groups(self.df,self.groups,self.manifest)
        g,f=assign_folds(self.df,m)
        self.assertEqual(f[0],f[1]);self.assertNotEqual(f[0],f[2])
        for n in range(len(g)):
            train={m[t] for t in self.df.loc[f!=n,'txid'] if t in m}
            test={m[t] for t in self.df.loc[f==n,'txid'] if t in m}
            self.assertFalse(train&test)
    def test_deterministic_background_assignment(self):
        m=validate_groups(self.df,self.groups,self.manifest)
        _,a=assign_folds(self.df,m);_,b=assign_folds(self.df,m)
        self.assertTrue((a==b).all())
    def test_missing_candidate_refused(self):
        self.groups['candidates'].pop()
        with self.assertRaises(ValueError):validate_groups(self.df,self.groups,self.manifest)
    def test_duplicate_candidate_refused(self):
        self.groups['candidates'].append(self.groups['candidates'][0])
        with self.assertRaises(ValueError):validate_groups(self.df,self.groups,self.manifest)
    def test_stale_provenance_refused(self):
        self.manifest['parent_report_sha256']='changed'
        with self.assertRaises(ValueError):validate_groups(self.df,self.groups,self.manifest)
    def test_false_counts_refused(self):
        self.groups['group_counts']['one']=100
        with self.assertRaises(ValueError):validate_groups(self.df,self.groups,self.manifest)

if __name__=='__main__':unittest.main()
