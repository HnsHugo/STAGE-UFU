"""Descriptive validation diagnostics for the fixed source-category forest."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from train_source_categories import HASHES,DROP,prepare,split,metrics


def error_masks(target,scores,threshold=.3):
    prediction=np.asarray(scores)>threshold;positive=np.asarray(target)==1
    return {'TP':positive&prediction,'FP':~positive&prediction,'FN':positive&~prediction,'TN':~positive&~prediction}


def run(source,reference,output):
    output.mkdir(parents=True,exist_ok=False)
    for name,digest in HASHES.items():
        with (source/name).open('rb') as f:
            if hashlib.file_digest(f,'sha256').hexdigest()!=digest:raise ValueError('Input checksum mismatch')
    data=prepare(pd.read_csv(source/'BB.tsv',sep='\t'),pd.read_csv(source/'CB.tsv',sep='\t'))
    columns=[c for c in data if c not in DROP and 'USD' not in c]
    train,validation,_reserved_test=split(data)
    # Only training/validation feature values are transformed and inspected below.
    raw_train=data.iloc[train][columns].apply(pd.to_numeric,errors='coerce').replace([np.inf,-np.inf],np.nan)
    raw_val=data.iloc[validation][columns].apply(pd.to_numeric,errors='coerce').replace([np.inf,-np.inf],np.nan)
    imputer=SimpleImputer(strategy='median');xt=imputer.fit_transform(raw_train);xv=imputer.transform(raw_val)
    model=RandomForestClassifier(n_estimators=100,max_depth=20,min_samples_leaf=20,max_features='sqrt',class_weight={0:1,1:3},random_state=42,n_jobs=2)
    model.fit(xt,data.iloc[train].label.isin(['Hack','Theft']).astype(int))
    scores=model.predict_proba(xv)[:,1];labels=data.iloc[validation].label.to_numpy()
    target=np.isin(labels,['Hack','Theft']).astype(int);masks=error_masks(target,scores)
    observed=metrics(target,(scores>.3).astype(int),scores)
    previous=json.loads(reference.read_text())
    expected=next(c for c in previous['candidates'] if c['name']=='forest_depth20')['best_validation']
    for name,value in observed.items():
        if not np.isclose(value,expected[name],rtol=0,atol=1e-12):raise ValueError('Baseline validation does not reproduce')
    categories={}
    missing=raw_val.isna()
    for label in ['Hack','Theft','benign']:
        mask=labels==label;detected=int((mask&(scores>.3)).sum())
        categories[label]=dict(count=int(mask.sum()),alerted=detected,not_alerted=int(mask.sum())-detected,
            alert_rate=detected/int(mask.sum()),score_quantiles={str(q):float(np.quantile(scores[mask],q)) for q in [0,.25,.5,.75,1]},
            rows_with_missing=int(missing.loc[mask].any(axis=1).sum()),
            missing_by_feature={c:int(missing.loc[mask,c].sum()) for c in columns if missing.loc[mask,c].any()})
    groups={}
    for name,mask in masks.items():
        groups[name]=dict(count=int(mask.sum()),rows_with_missing=int(missing.loc[mask].any(axis=1).sum()),
            missing_by_feature={c:int(missing.loc[mask,c].sum()) for c in columns if missing.loc[mask,c].any()},
            score_quantiles={str(q):float(np.quantile(scores[mask],q)) for q in [0,.25,.5,.75,1]},
            raw_feature_medians={c:None if raw_val.loc[mask,c].dropna().empty else float(raw_val.loc[mask,c].median()) for c in columns})
    report=dict(scope='Fixed-model descriptive validation diagnostics; no test evaluation or new threshold selection',
        baseline_validation=observed,categories=categories,error_groups=groups,
        training_missing_cells=int(raw_train.isna().sum().sum()),validation_missing_cells=int(missing.sum().sum()),
        training_imputation_medians={c:float(v) for c,v in zip(columns,imputer.statistics_)},
        false_negative_scores_below_005=int((masks['FN']&(scores<.05)).sum()),
        near_threshold_counts={k:int((mask&(scores>.2)&(scores<=.4)).sum()) for k,mask in masks.items()},
        missing_sent_amount_diagnostic=dict(rows=int(missing['max_sent_amount'].sum()),rows_with_zero_payment_transactions=int((missing['max_sent_amount']&(raw_val['payment_transactions']==0)).sum())),
        feature_importances={c:float(v) for c,v in zip(columns,model.feature_importances_)},
        source_sha256=HASHES,reference_metrics_sha256=hashlib.sha256(reference.read_bytes()).hexdigest(),
        limitations=['Source categories, not independently established theft roles',
                     'Missingness associations do not establish that imputation caused errors',
                     'Repeated use of validation is development, not independent confirmation',
                     'Full-history aggregate features; no case/entity-disjoint or causal temporal test'])
    (output/'validation_analysis.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['baseline_validation','categories','training_missing_cells','validation_missing_cells','false_negative_scores_below_005','near_threshold_counts']}),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('reference',type=Path);p.add_argument('output',type=Path)
    a=p.parse_args();run(a.source,a.reference,a.output)
