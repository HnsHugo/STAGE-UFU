"""Validation-only ablation of an unreconciled extraction feature."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from train_source_categories import HASHES, DROP, THRESHOLDS, prepare, split, metrics


def run(source, output):
    if output.exists():raise ValueError('Output must be new')
    for name,expected in HASHES.items():
        with (source/name).open('rb') as f:
            if hashlib.file_digest(f,'sha256').hexdigest()!=expected:raise ValueError('Source checksum mismatch')
    data=prepare(pd.read_csv(source/'BB.tsv',sep='\t'),pd.read_csv(source/'CB.tsv',sep='\t'))
    train,val,reserved=split(data);y=data.label.isin(['Hack','Theft']).astype(int).to_numpy();candidates=[]
    for omit in [False,True]:
        columns=[c for c in data if c not in DROP and 'USD' not in c and (not omit or c!='sent_Variance_BTC')]
        xt=data.iloc[train][columns].apply(pd.to_numeric,errors='coerce').replace([np.inf,-np.inf],np.nan)
        xv=data.iloc[val][columns].apply(pd.to_numeric,errors='coerce').replace([np.inf,-np.inf],np.nan)
        imputer=SimpleImputer(strategy='median',add_indicator=True)
        model=RandomForestClassifier(n_estimators=100,max_depth=20,min_samples_leaf=20,max_features='sqrt',class_weight={0:1,1:1},random_state=42,n_jobs=2)
        model.fit(imputer.fit_transform(xt),y[train]);scores=model.predict_proba(imputer.transform(xv))[:,1]
        grid=[]
        for t in THRESHOLDS:
            pred=(scores>t).astype(int)
            grid.append(dict(threshold=t,**metrics(y[val],pred,scores),category_recall={label:float(pred[data.iloc[val].label.to_numpy()==label].mean()) for label in ['Hack','Theft']}))
        if not omit:
            baseline=next(v for v in grid if v['threshold']==.15)
            assert (baseline['true_positive'],baseline['false_positive'])==(81,147),'Baseline reproduction failed'
        r=dict(omit_sent_variance=omit,features=columns,grid=grid,best_validation=max(grid,key=lambda r:r['f1']),at_frozen_threshold=next(v for v in grid if v['threshold']==.15))
        candidates.append(r);print(json.dumps(r['best_validation']),flush=True)
    output.write_text(json.dumps(dict(status='Exploratory validation ablation; not independent confirmation',reserved_test_count=len(reserved),test_predicted=False,source_sha256=HASHES,candidates=candidates,
        limitations=['Validation reused for development','Dropping one feature changes sqrt feature sampling and tree construction','Other extraction edge cases still unresolved','No external model prediction or verified theft-label evaluation']),indent=2)+'\n')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('output',type=Path);a=p.parse_args();run(a.source,a.output)
