"""Leave one observed candidate group out; background assigned by TXID hash.
Usage: python train_grouped.py transactions.csv.gz candidate_groups.json manifest.json output_dir
Proxy classification only; background entities are not grouped or verified benign.
"""
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
import pandas as pd
import sklearn
from sklearn.tree import DecisionTreeClassifier, export_text
from train_exploratory import FEATURES, EXPECTED_SHA, metrics


def validate_groups(df, grouping, manifest):
    rows=grouping['candidates']
    mapping={r['txid']:r['group_id'] for r in rows}
    if len(mapping)!=len(rows): raise ValueError('Duplicate candidate TXID in groups.')
    expected=set(df.loc[df.relation=='direct_parent_candidate','txid'])
    if set(mapping)!=expected:raise ValueError('Candidate groups do not match feature TXIDs exactly.')
    if grouping['parent_report_sha256']!=manifest['parent_report_sha256']:raise ValueError('Parent provenance mismatch.')
    actual={}
    for g in mapping.values():actual[g]=actual.get(g,0)+1
    if actual!=grouping['group_counts']:raise ValueError('Group count mismatch.')
    if len(actual)<2:raise ValueError('At least two candidate groups required.')
    return mapping


def assign_folds(df,mapping):
    groups=sorted(set(mapping.values()));group_fold={g:i for i,g in enumerate(groups)}
    # Each candidate group appears in exactly one test fold. Each background TX too.
    folds=np.array([group_fold[mapping[t]] if t in mapping else
                    int(hashlib.sha256(t.encode()).hexdigest()[:16],16)%len(groups)
                    for t in df.txid],dtype=int)
    return groups,folds


def run(source,group_file,manifest_file,destination):
    with open(source,'rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
    if digest!=EXPECTED_SHA:raise ValueError('Input differs from inspected features.')
    raw=Path(group_file).read_bytes();grouping=json.loads(raw)
    manifest=json.loads(Path(manifest_file).read_text())
    df=pd.read_csv(source)
    if manifest['status']!='complete' or len(df)!=manifest['transaction_count'] or df.txid.duplicated().any():raise ValueError('Incomplete or duplicate dataset.')
    mapping=validate_groups(df,grouping,manifest)
    df=df[(df.is_coinbase==0)&(df.relation!='source_attributed')].reset_index(drop=True)
    if not np.isfinite(df[FEATURES].to_numpy(float)).all():raise ValueError('Missing/nonfinite features.')
    y=df.relation.eq('direct_parent_candidate').astype(int).to_numpy()
    groups,folds=assign_folds(df,mapping)
    out=Path(destination);out.mkdir(exist_ok=False)
    report={'target':'direct parent candidate versus unattributed background',
            'warning':'Candidate groups held apart. Background entity links and missing-block relationships remain unknown. Not external theft validation.',
            'dataset_sha256':digest,'groups_sha256':hashlib.sha256(raw).hexdigest(),
            'versions':{'python':sys.version.split()[0],'sklearn':sklearn.__version__,'pandas':pd.__version__,'numpy':np.__version__},
            'settings':{'max_depth':4,'min_samples_leaf':20,'class_weight':'balanced','random_state':42},
            'background_split':'SHA256(TXID) first 16 hex digits modulo number of candidate groups; not entity-level split',
            'candidate_group_count':len(groups),'candidate_group_counts':grouping['group_counts'],
            'eligible_rows':len(df),'folds':[]}
    variants={'tree_all':FEATURES,'tree_without_fees':[c for c in FEATURES if c not in ['fee_sat','fee_rate_sat_vb']]}
    pooled={k:np.zeros(len(df),dtype=int) for k in ['always_background','previously_observed_rule',*variants]}
    scores={k:np.zeros(len(df)) for k in variants}
    for i,g in enumerate(groups):
        test=np.flatnonzero(folds==i);train=np.flatnonzero(folds!=i)
        tg={mapping[t] for t in df.iloc[train].txid if t in mapping}
        vg={mapping[t] for t in df.iloc[test].txid if t in mapping}
        if tg&vg or vg!={g}:raise ValueError('Candidate group leakage detected.')
        row={'held_out_group':g,'train_rows':len(train),'test_rows':len(test),'train_candidates':int(y[train].sum()),'test_candidates':int(y[test].sum()),'models':{}}
        row['models']['always_background']=metrics(y[test],pooled['always_background'][test])
        rule=((df.iloc[test].output_count==1)&(df.iloc[test].fee_rate_sat_vb>=4.95)).astype(int).to_numpy()
        pooled['previously_observed_rule'][test]=rule
        row['models']['previously_observed_rule']=metrics(y[test],rule)
        for name,columns in variants.items():
            model=DecisionTreeClassifier(**report['settings'])
            model.fit(df.iloc[train][columns],y[train])
            pred=model.predict(df.iloc[test][columns]);score=model.predict_proba(df.iloc[test][columns])[:,1]
            pooled[name][test]=pred;scores[name][test]=score
            row['models'][name]=metrics(y[test],pred,score)
            row['models'][name]['feature_importances']={c:float(v) for c,v in zip(columns,model.feature_importances_) if v}
            (out/f'fold_{i}_{name}.txt').write_text(export_text(model,feature_names=columns,decimals=5,max_depth=4))
        report['folds'].append(row)
    report['pooled_out_of_fold']={k:metrics(y,p,scores.get(k)) for k,p in pooled.items()}
    report['macro_fold']={k:{metric:float(np.mean([f['models'][k][metric] for f in report['folds']]))
                           for metric in ['precision_proxy','recall_proxy','f1_proxy']} for k in pooled}
    # Aggregate disagreement, without publishing unsupported accusations about individual TXIDs.
    report['candidate_misses_by_model']={k:int(((y==1)&(p==0)).sum()) for k,p in pooled.items()}
    (out/'metrics.json').write_text(json.dumps(report,indent=2))
    print(json.dumps({'folds':[{'group':r['held_out_group'][:12],'candidates':r['test_candidates'],'all':r['models']['tree_all'],'without_fees':r['models']['tree_without_fees']} for r in report['folds']],
                      'pooled':report['pooled_out_of_fold'],'macro':report['macro_fold']},indent=2))

if __name__=='__main__':
    if len(sys.argv)!=5:sys.exit('Usage: python train_grouped.py transactions.csv.gz candidate_groups.json manifest.json output_dir')
    run(*sys.argv[1:])
