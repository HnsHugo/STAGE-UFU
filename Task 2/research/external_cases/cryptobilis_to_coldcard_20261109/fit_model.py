"""Fit the single frozen-parameter reverse-transfer baseline once."""
import argparse
import json
from pathlib import Path
import platform
import statistics

from experiment import read, require, save, sha, verify_protocol


def fit(protocol_path,root,published_commit):
    out=protocol_path.parent
    require(len(published_commit)==40 and all(c in '0123456789abcdef' for c in published_commit), 'Published protocol commit required')
    require(not any((out/name).exists() for name in ['model.json','predictions.json','summary.json']), 'Prior fit outputs exist; do not refit')
    protocol,(rows,names,manifest,preflight)=verify_protocol(protocol_path,root)
    import numpy as np
    import sklearn
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.metrics import precision_score,recall_score,f1_score,average_precision_score,roc_auc_score,confusion_matrix
    require(np.__version__==protocol['software']['numpy'] and sklearn.__version__==protocol['software']['scikit-learn'], 'Runtime differs from protocol')
    train=[m for m in manifest if m['status']=='training']
    medians={name:statistics.median(values) if values else 0 for name in names
        for values in [[rows[m['key']]['features'][name] for m in train if rows[m['key']]['features'][name] is not None]]}
    def vector(row):
        f=row['features']
        return [medians[n] if f[n] is None else f[n] for n in names]+[int(f[n] is None) for n in names]
    x=np.asarray([vector(rows[m['key']]) for m in train],dtype=np.float32)
    y=np.asarray([m['membership'] for m in train],dtype=np.int64)
    model=DecisionTreeClassifier(**protocol['model'])
    model.fit(x,y)
    nodes=[]
    for i in range(model.tree_.node_count):
        value=[float(v) for v in model.tree_.value[i,0]];total=sum(value)
        nodes.append(dict(node_id=i,left=int(model.tree_.children_left[i]),right=int(model.tree_.children_right[i]),
            feature_index=int(model.tree_.feature[i]),threshold=float(model.tree_.threshold[i]),
            sample_count=int(model.tree_.n_node_samples[i]),weighted_sample_count=float(model.tree_.weighted_n_node_samples[i]),
            positive_probability=value[1]/total))
    exported=dict(schema_version=1,classes=[int(c) for c in model.classes_],feature_names=names+[n+'__missing' for n in names],
        medians=medians,nodes=nodes,input_dtype='float32',threshold=0.5,
        params=protocol['model'],training_rows=len(train),training_cases=int(y.sum()),
        score_meaning='Class-balanced training leaf proportion; not a calibrated theft/device probability')
    save(out/'model.json',exported)
    predictions=[];metrics={};prevalence=float(y.mean())
    for split,status in [('training_diagnostic','training'),('coldcard_evaluation','evaluation')]:
        chosen=[m for m in manifest if m['status']==status]
        xx=np.asarray([vector(rows[m['key']]) for m in chosen],dtype=np.float32)
        yy=np.asarray([m['membership'] for m in chosen],dtype=np.int64)
        scores=model.predict_proba(xx)[:,1];decisions=(scores>=0.5).astype(int);leaves=model.apply(xx)
        rankings={'tree':scores,'training_prevalence_constant':np.full(len(yy),prevalence),
            'prior_inactivity':np.asarray([medians['blocks_since_last_activity'] if rows[m['key']]['features']['blocks_since_last_activity'] is None else rows[m['key']]['features']['blocks_since_last_activity'] for m in chosen],dtype=np.float64),
            'prior_balance':np.asarray([medians['balance_sat'] if rows[m['key']]['features']['balance_sat'] is None else rows[m['key']]['features']['balance_sat'] for m in chosen],dtype=np.float64)}
        metrics[split]={'rows':len(yy),'cases':int(yy.sum()),'comparisons':int(len(yy)-yy.sum()),
            'ranking':{k:{'average_precision':float(average_precision_score(yy,v)),'roc_auc':float(roc_auc_score(yy,v))} for k,v in rankings.items()},
            'tree':{'precision':float(precision_score(yy,decisions,zero_division=0)),
                'recall':float(recall_score(yy,decisions,zero_division=0)),
                'f1':float(f1_score(yy,decisions,zero_division=0)),
                'confusion_tn_fp_fn_tp':[int(v) for v in confusion_matrix(yy,decisions,labels=[0,1]).ravel()]}}
        for i,m in enumerate(chosen):
            predictions.append(dict(key=m['key'],source_id=m['source_id'],dataset=m['dataset'],split=split,
                component_id=m['component_id'],membership=m['membership'],case_membership_score=float(scores[i]),
                predicted_membership=int(decisions[i]),leaf_node_id=int(leaves[i]),
                prior_inactivity_score=float(rankings['prior_inactivity'][i]),prior_balance_score=float(rankings['prior_balance'][i]),
                training_prevalence_score=prevalence))
    save(out/'predictions.json',dict(schema_version=1,rows=predictions))
    errors=[dict(**p,features=rows[p['key']]['features'],cutoff_height=rows[p['key']]['cutoff_height'])
        for p in predictions if p['split']=='coldcard_evaluation' and p['membership']!=p['predicted_membership']]
    save(out/'errors.json',dict(schema_version=1,rows=errors))
    summary=dict(schema_version=1,published_protocol_commit=published_commit,protocol_sha256=sha(protocol_path),
        model_sha256=sha(out/'model.json'),predictions_sha256=sha(out/'predictions.json'),errors_sha256=sha(out/'errors.json'),
        provider_requests=0,model_fits=1,preprocessing_fits=1,hyperparameter_searches=0,
        threshold_searches=0,all_row_refits=0,metrics=metrics,coverage=preflight,
        external_errors=len(errors),python=platform.python_version(),
        limits=['Retrospective reverse-time operational membership transfer; both incidents previously inspected',
            '122 Coldcard and 37 CryptoBilis bounded prefixes remain unavailable',
            '312 complete Coldcard vectors quarantined on the evaluation side; observed links do not establish entity independence',
            'Verified compromise, seed origin and signing-device labels remain unknown'])
    save(out/'summary.json',summary)
    print(json.dumps(metrics['coldcard_evaluation'],sort_keys=True))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('protocol',type=Path);parser.add_argument('--repo-root',required=True,type=Path)
    parser.add_argument('--published-protocol-commit',required=True)
    a=parser.parse_args();fit(a.protocol.resolve(),a.repo_root.resolve(),a.published_protocol_commit)
