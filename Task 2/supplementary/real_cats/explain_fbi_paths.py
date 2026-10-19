"""Exact path-score decomposition for a fixed forest; not SHAP or causal effects."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from train_source_categories import HASHES, DROP, prepare, split
from score_external_histories import UNRECONCILED


def decompose(model, x):
    contributions=np.zeros(x.shape[1]);baseline=0.0
    for estimator in model.estimators_:
        tree=estimator.tree_;values=tree.value[:,0,:];prob=values[:,1]/values.sum(axis=1)
        baseline+=prob[0];node=0
        while tree.children_left[node]!=tree.children_right[node]:
            feature=tree.feature[node]
            child=tree.children_left[node] if x[0,feature]<=tree.threshold[node] else tree.children_right[node]
            contributions[feature]+=prob[child]-prob[node];node=child
    return baseline/len(model.estimators_),contributions/len(model.estimators_)


def run(source, scored, output):
    if output.exists():raise ValueError('Output must be new')
    for name,expected in HASHES.items():
        with (source/name).open('rb') as f:
            if hashlib.file_digest(f,'sha256').hexdigest()!=expected:raise ValueError('Source checksum mismatch')
    data=prepare(pd.read_csv(source/'BB.tsv',sep='\t'),pd.read_csv(source/'CB.tsv',sep='\t'))
    train,_,_=split(data);columns=[c for c in data if c not in DROP and 'USD' not in c and c not in UNRECONCILED]
    xt=data.iloc[train][columns].apply(pd.to_numeric,errors='coerce').replace([np.inf,-np.inf],np.nan)
    imputer=SimpleImputer(strategy='median',add_indicator=True)
    model=RandomForestClassifier(n_estimators=100,max_depth=20,min_samples_leaf=20,max_features='sqrt',class_weight={0:1,1:1},random_state=42,n_jobs=2)
    model.fit(imputer.fit_transform(xt),data.iloc[train].label.isin(['Hack','Theft']).astype(int));names=list(imputer.get_feature_names_out());rows=[]
    for record in json.loads(scored.read_text())['results']:
        if not str(record['source_record'].get('case_group','')).startswith('fbi'):continue
        frame=pd.DataFrame([{c:record['features'][c] for c in columns}],columns=columns).astype(float)
        x=imputer.transform(frame).astype(np.float32)
        score=float(model.predict_proba(x)[0,1]);baseline,delta=decompose(model,x)
        assert np.isclose(score,record['source_category_score'],rtol=0,atol=1e-12),'Fixed score reproduction failed'
        assert np.isclose(baseline+delta.sum(),score,rtol=0,atol=1e-12),'Decomposition sum failed'
        items=sorted([dict(feature=n,contribution=float(v)) for n,v in zip(names,delta)],key=lambda r:abs(r['contribution']),reverse=True)
        rows.append(dict(address=record['address'],features=record['features'],score=score,above_threshold=score>.15,
                         distance_to_threshold=score-.15,baseline=baseline,contributions=items))
    if len(rows)!=6:raise ValueError('Expected six FBI references')
    output.write_text(json.dumps(dict(method='Mean tree-path changes in positive-class leaf proportion; exact additive accounting, not SHAP',
        input_report_sha256=hashlib.sha256(scored.read_bytes()).hexdigest(),fixed_threshold=.15,results=rows,
        limitations=['Contributions depend on split order and correlated predictors','Not causal effects or independent evidence of criminality','No threshold changes or external fitting','Full-history profiles, not early detection snapshots']),indent=2)+'\n')
    for r in rows:print(r['address'],r['score'],r['contributions'][:4])


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('scored',type=Path);p.add_argument('output',type=Path);a=p.parse_args();run(a.source,a.scored,a.output)
