"""Descriptive external scores using a fixed, separately fitted 19-feature forest."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from train_source_categories import HASHES, DROP, prepare, split
from reconcile_training_profiles import probes
sys.path.insert(0,str(Path(__file__).parent.parent/'theft_cases'))
from collect_binance_research_seed import helper

UNRECONCILED={'transaction_fee_Variance','received_Variance_BTC','sent_Variance_BTC'}


def extract(path):
    raw=path.read_bytes()
    history=json.loads(gzip.decompress(raw) if path.suffix=='.gz' else raw)
    if not history['audit']['pagination_exhausted']:raise ValueError('Unfinished history pagination')
    audit=helper().check_history(history['address'],history['transactions'],history['before'],history['after'],True)
    if not audit['coverage_complete_by_provider_counters']:raise ValueError('History reconciliation failed')
    values,_=probes(history['address'],history['transactions'])
    return history,{k:v for k,v in values.items() if k not in UNRECONCILED},hashlib.sha256(raw).hexdigest()


def run(source,paths,output):
    if output.exists():raise ValueError('Output must be new')
    for name,expected in HASHES.items():
        with (source/name).open('rb') as f:
            if hashlib.file_digest(f,'sha256').hexdigest()!=expected:raise ValueError('Source checksum mismatch')
    bb=pd.read_csv(source/'BB.tsv',sep='\t');cb=pd.read_csv(source/'CB.tsv',sep='\t')
    all_source=set(bb.address)|set(cb.address)
    data=prepare(bb,cb);train,_,_=split(data)
    columns=[c for c in data if c not in DROP and 'USD' not in c and c not in UNRECONCILED]
    if len(columns)!=19:raise ValueError('Unexpected feature schema')
    xt=data.iloc[train][columns].apply(pd.to_numeric,errors='coerce').replace([np.inf,-np.inf],np.nan)
    y=data.iloc[train].label.isin(['Hack','Theft']).astype(int)
    imputer=SimpleImputer(strategy='median',add_indicator=True)
    model=RandomForestClassifier(n_estimators=100,max_depth=20,min_samples_leaf=20,max_features='sqrt',class_weight={0:1,1:1},random_state=42,n_jobs=2)
    model.fit(imputer.fit_transform(xt),y)
    rows=[];seen=set()
    for path in paths:
        h,values,digest=extract(path);address=h['address']
        if address in all_source:raise ValueError('External address overlaps Real-CATS')
        if address in seen:raise ValueError('Duplicate external address')
        seen.add(address)
        if set(values)!=set(columns):raise ValueError('Extractor feature names mismatch')
        x=pd.DataFrame([{c:values[c] for c in columns}],columns=columns).astype(float)
        score=float(model.predict_proba(imputer.transform(x))[0,1]);threshold=.15
        rows.append(dict(address=address,history_file=path.name,history_sha256=digest,collected_at=h['collected_at'],
                         source_record=h.get('source_record',h.get('record')),features=values,source_category_score=score,
                         above_fixed_threshold=score>threshold,threshold=threshold,
                         missing_features=[c for c in columns if pd.isna(x.iloc[0][c])],
                         outside_training_minmax=[c for c in columns if pd.notna(x.iloc[0][c]) and (x.iloc[0][c]<xt[c].min() or x.iloc[0][c]>xt[c].max())]))
    report=dict(status='Descriptive external pilot; no ground-truth performance evaluation',source_sha256=HASHES,
                training_addresses=len(train),base_features=columns,transformed_features=list(imputer.get_feature_names_out()),
                fixed_model=dict(n_estimators=100,max_depth=20,min_samples_leaf=20,max_features='sqrt',class_weight=1,random_state=42,threshold=.15),
                observation_policy='Complete confirmed provider histories at individual saved collection times; no 24-hour snapshot scoring',
                results=rows,limitations=['Scores are not calibrated probabilities of theft or illegality',
                'Training target is retrospective Real-CATS Hack/Theft versus assumed benign, not verified stolen-fund recipients',
                'Small grouped address pilot cannot establish precision/recall; attribution confidence varies',
                '19-feature conventions reconciled only on seven training development addresses; unresolved edge cases remain',
                'External observation calendars and collection dates differ; domain shift is uncontrolled',
                'No external labels used for fitting; no validation or reserved-test prediction in this scoring script'])
    output.write_text(json.dumps(report,indent=2)+'\n')
    for row in rows:print(row['address'],row['source_category_score'],row['above_fixed_threshold'],row['outside_training_minmax'],flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('output',type=Path);p.add_argument('histories',type=Path,nargs='+');a=p.parse_args();run(a.source,a.histories,a.output)
