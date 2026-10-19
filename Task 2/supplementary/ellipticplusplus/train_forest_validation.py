"""Predefined random-forest comparison on validation only; no test evaluation."""
import argparse
import hashlib
import json
import time
from pathlib import Path
import numpy as np
import pandas as pd
import sklearn
from sklearn.ensemble import RandomForestClassifier
from train_benchmark import EXPECTED, EXCLUDED, prepare, split_indices
from tune_validation import threshold_results

CONFIGURATIONS = [('depth12_unweighted', 12, None),
                  ('depth12_illicit_weight3', 12, {0:1, 1:3}),
                  ('depth20_illicit_weight3', 20, {0:1, 1:3})]


def run(source, output):
    output.mkdir(parents=True, exist_ok=False)
    (output/'status.json').write_text(json.dumps({'status':'incomplete'}))
    for filename, expected in EXPECTED.items():
        with (source/filename).open('rb') as f:
            if hashlib.file_digest(f,'sha256').hexdigest()!=expected:
                raise ValueError('Input checksum mismatch')
    data=prepare(pd.read_csv(source/'wallets_features.csv'),pd.read_csv(source/'wallets_classes.csv'))
    train,validation,_=split_indices(data)
    columns=[c for c in data if c not in EXCLUDED]
    y=(data['class']==1).astype(int).to_numpy()
    x_train=data.iloc[train][columns].to_numpy(dtype=np.float32)
    x_validation=data.iloc[validation][columns].to_numpy(dtype=np.float32)
    report=dict(scope='Validation-only random-forest development; no held-out test score',
                source_sha256=EXPECTED, sklearn_version=sklearn.__version__, features=columns,
                train_addresses=len(train),validation_addresses=len(validation),configurations=[])
    print('Data prepared; fitting three forests',flush=True)
    for name,depth,weight in CONFIGURATIONS:
        started=time.perf_counter()
        model=RandomForestClassifier(n_estimators=100,max_depth=depth,min_samples_leaf=20,
                                     max_features='sqrt',class_weight=weight,bootstrap=True,
                                     random_state=42,n_jobs=2)
        model.fit(x_train,y[train])
        scores=model.predict_proba(x_validation)[:,1]
        grid=threshold_results(y[validation],scores)
        best=max(grid,key=lambda row:row['f1'])
        report['configurations'].append(dict(name=name,depth=depth,class_weight=weight,
            n_estimators=100,min_samples_leaf=20,max_features='sqrt',bootstrap=True,random_state=42,
            runtime_seconds=time.perf_counter()-started,grid=grid,best_validation_f1=best,
            feature_importances={c:float(v) for c,v in zip(columns,model.feature_importances_)}))
        print(name,json.dumps(best),flush=True)
    report['selected']=max([dict(model=r['name'],**r['best_validation_f1']) for r in report['configurations']],key=lambda r:r['f1'])
    report['limitations']=['Same validation reused for weight/depth/threshold selection; winning score is optimistic',
                          'Test addresses not fitted, evaluated or used for selection',
                          'Offline profiles and address separation do not prove time/case/entity independence',
                          'Original illicit/licit benchmark; not stolen-fund or hardware detection',
                          'Scores not calibrated; impurity feature importances not causal or SHAP',
                          'No deployed or independently validated forest artifact exported']
    (output/'forest_validation_metrics.json').write_text(json.dumps(report,indent=2)+'\n')
    (output/'status.json').write_text(json.dumps({'status':'complete','metrics_sha256':hashlib.sha256((output/'forest_validation_metrics.json').read_bytes()).hexdigest()},indent=2)+'\n')


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('source',type=Path)
    parser.add_argument('output',type=Path)
    a=parser.parse_args()
    run(a.source,a.output)
