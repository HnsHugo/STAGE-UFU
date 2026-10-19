import unittest
import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from proxy_model import export,score_rows
from train_exploratory import FEATURES

class ProxyTests(unittest.TestCase):
    def test_json_scores_match_sklearn_at_boundaries(self):
        x=pd.DataFrame(np.tile(np.arange(12).reshape(-1,1),(1,len(FEATURES))),columns=FEATURES)
        y=np.array([0]*6+[1]*6)
        model=DecisionTreeClassifier(max_depth=2,random_state=42).fit(x,y)
        encoded=export(model)
        self.assertTrue(np.allclose(score_rows(x,encoded),model.predict_proba(x)[:,1]))
        boundary=model.tree_.threshold[0]
        q=pd.DataFrame(np.full((2,len(FEATURES)),boundary),columns=FEATURES)
        q.iloc[1,:]=boundary+1
        self.assertTrue(np.allclose(score_rows(q,encoded),model.predict_proba(q)[:,1]))
    def test_large_satoshi_values_match_float32_tree_semantics(self):
        amounts=np.arange(16777216,16777228,dtype=float)
        x=pd.DataFrame(np.tile(amounts.reshape(-1,1),(1,len(FEATURES))),columns=FEATURES)
        model=DecisionTreeClassifier(max_depth=3,random_state=42).fit(x,np.array([0]*5+[1]*7))
        q=pd.DataFrame(np.tile(np.arange(16777216,16777228,.25).reshape(-1,1),(1,len(FEATURES))),columns=FEATURES)
        self.assertTrue(np.allclose(score_rows(q,export(model)),model.predict_proba(q)[:,1]))
    def test_missing_features_refused(self):
        model={'features':FEATURES}
        with self.assertRaises(KeyError):score_rows(pd.DataFrame({'input_count':[1]}),model)
    def test_nonfinite_values_refused(self):
        x=pd.DataFrame(np.ones((1,len(FEATURES))),columns=FEATURES);x.iloc[0,0]=np.nan
        with self.assertRaises(ValueError):score_rows(x,{'features':FEATURES})

if __name__=='__main__':unittest.main()
