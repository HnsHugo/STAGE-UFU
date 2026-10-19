"""Offline Real-CATS source-label benchmark: Hack/Theft versus selected benign pool."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier,export_text
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_recall_fscore_support,confusion_matrix,average_precision_score

HASHES={'BB.tsv':'3bfe26f493e5767737c9ecf4c654009067c162dc7fa6fec68b0ab8234d4431e9',
        'CB.tsv':'faf3978f5c9ce3b1257af72ac01975d657ab7529f66faf1a66f1f22f99fbb1ec'}
DROP={'address','label','first_time','last_time','watchback_checked','gs_checked',
      'max_sent_transaction_id','min_sent_transaction_id','max_received_transaction_id','min_received_transaction_id'}
THRESHOLDS=[.05,.1,.15,.2,.25,.3,.35,.4,.45,.5,.55,.6,.65,.7,.75,.8,.85,.9,.95]


def metrics(y,p,s):
    precision,recall,f1,_=precision_recall_fscore_support(y,p,average='binary',zero_division=0)
    tn,fp,fn,tp=confusion_matrix(y,p,labels=[0,1]).ravel()
    return dict(precision=float(precision),recall=float(recall),f1=float(f1),average_precision=float(average_precision_score(y,s)),
                true_negative=int(tn),false_positive=int(fp),false_negative=int(fn),true_positive=int(tp))


def prepare(benign,criminal):
    a=benign[(benign.label=='benign')&(benign.transaction_number>0)].copy()
    b=criminal[criminal.label.isin(['Hack','Theft'])&(criminal.transaction_number>0)].copy()
    data=pd.concat([a,b],ignore_index=True).sort_values('address').reset_index(drop=True)
    if data.address.isna().any() or data.address.duplicated().any():raise ValueError('Missing/duplicate/conflicting address')
    return data


def split(data):
    idx=np.arange(len(data));train,rest=train_test_split(idx,test_size=.4,stratify=data.label,random_state=42)
    val,test=train_test_split(rest,test_size=.5,stratify=data.iloc[rest].label,random_state=43)
    return train,val,test


def run(source,output):
    output.mkdir(parents=True,exist_ok=False);(output/'status.json').write_text('{"status":"incomplete"}')
    for filename,expected in HASHES.items():
        with (source/filename).open('rb') as f:
            if hashlib.file_digest(f,'sha256').hexdigest()!=expected:raise ValueError('Input checksum mismatch')
    data=prepare(pd.read_csv(source/'BB.tsv',sep='\t'),pd.read_csv(source/'CB.tsv',sep='\t'))
    columns=[c for c in data if c not in DROP and 'USD' not in c]
    x=data[columns].apply(pd.to_numeric,errors='coerce').replace([np.inf,-np.inf],np.nan)
    train,val,test=split(data);y=data.label.isin(['Hack','Theft']).astype(int).to_numpy()
    if x.iloc[train].isna().all().any():raise ValueError('Entirely missing training feature')
    imputer=SimpleImputer(strategy='median');xt=imputer.fit_transform(x.iloc[train]);xv=imputer.transform(x.iloc[val])
    assignment=pd.DataFrame(dict(address=data.address,source_label=data.label,split=''))
    for name,idx in [('train',train),('validation',val),('test',test)]:assignment.loc[idx,'split']=name
    assignment.to_csv(output/'split_assignments.csv.gz',index=False,compression='gzip')
    candidates=[('tree_depth8',DecisionTreeClassifier(max_depth=8,min_samples_leaf=20,class_weight={0:1,1:3},random_state=42)),
                ('forest_depth20',RandomForestClassifier(n_estimators=100,max_depth=20,min_samples_leaf=20,max_features='sqrt',class_weight={0:1,1:3},random_state=42,n_jobs=2))]
    report=dict(target='Real-CATS Hack/Theft source categories versus benign source category; offline historical profiles',
                source_sha256=HASHES,features=columns,excluded=list(sorted(DROP))+['all USD columns'],
                missing_numeric_cells=int(x.isna().sum().sum()),preprocessing='Median imputation fitted on training only',
                splits={name:dict(addresses=len(i),source_labels={str(k):int(v) for k,v in data.iloc[i].label.value_counts().items()}) for name,i in [('train',train),('validation',val),('test',test)]},
                candidates=[])
    models={}
    print('Eligible profiles:',len(data),'features:',len(columns),flush=True)
    for name,model in candidates:
        model.fit(xt,y[train]);scores=model.predict_proba(xv)[:,1]
        grid=[dict(threshold=t,**metrics(y[val],(scores>t).astype(int),scores)) for t in THRESHOLDS]
        best=max(grid,key=lambda r:r['f1']);models[name]=model
        report['candidates'].append(dict(name=name,grid=grid,best_validation=best))
        if name.startswith('tree'):(output/'tree_rules.txt').write_text(export_text(model,feature_names=columns,decimals=5))
        print(name,json.dumps(best),flush=True)
    choice=max(report['candidates'],key=lambda r:r['best_validation']['f1']);model=models[choice['name']];threshold=choice['best_validation']['threshold']
    scores=model.predict_proba(imputer.transform(x.iloc[test]))[:,1];pred=(scores>threshold).astype(int)
    report.update(selected_model=choice['name'],selected_threshold=threshold,test_metrics=metrics(y[test],pred,scores),
                  always_benign_test=metrics(y[test],np.zeros(len(test),dtype=int),np.zeros(len(test))),
                  feature_importances={c:float(v) for c,v in zip(columns,model.feature_importances_)},
                  per_positive_category={label:dict(count=int((data.iloc[test].label.to_numpy()==label).sum()),detected=int(pred[data.iloc[test].label.to_numpy()==label].sum())) for label in ['Hack','Theft']},
                  limitations=['Source categories not independent incident/role verification','Benign sampling assumes exchange recipients are benign',
                               'Case IDs/label availability unknown; address-disjoint not case/entity-disjoint',
                               'Full-history profiles not decision-time snapshots or real-time detection',
                               'Other crime categories excluded, not silently treated as benign',
                               'No direct cross-dataset application of Elliptic++ model',
                               'Validation selects configuration/threshold; test evaluated once afterward'])
    (output/'metrics.json').write_text(json.dumps(report,indent=2)+'\n')
    (output/'status.json').write_text(json.dumps(dict(status='complete',metrics_sha256=hashlib.sha256((output/'metrics.json').read_bytes()).hexdigest()),indent=2)+'\n')
    print('TEST',json.dumps(report['test_metrics']),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('output',type=Path)
    a=p.parse_args();run(a.source,a.output)
