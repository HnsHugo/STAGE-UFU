"""One locked-configuration evaluation on the original held-out test addresses."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from train_benchmark import EXPECTED, EXCLUDED, prepare, split_indices, evaluate

CONFIGURATION = dict(n_estimators=100, max_depth=20, min_samples_leaf=20,
                     max_features='sqrt', class_weight={0:1, 1:3}, bootstrap=True,
                     random_state=42, n_jobs=2)
THRESHOLD = .55


def run(source, output):
    output.mkdir(parents=True, exist_ok=False)
    (output/'status.json').write_text(json.dumps({'status':'incomplete'}))
    for filename, expected in EXPECTED.items():
        with (source/filename).open('rb') as f:
            if hashlib.file_digest(f,'sha256').hexdigest()!=expected:
                raise ValueError('Input checksum mismatch')
    data=prepare(pd.read_csv(source/'wallets_features.csv'),pd.read_csv(source/'wallets_classes.csv'))
    train,validation,test=split_indices(data)
    columns=[c for c in data if c not in EXCLUDED]
    y=(data['class']==1).astype(int).to_numpy()
    model=RandomForestClassifier(**CONFIGURATION)
    model.fit(data.iloc[train][columns].to_numpy(dtype=np.float32),y[train])
    # Configuration/threshold fixed before evaluation; no additional model selection.
    scores=model.predict_proba(data.iloc[test][columns].to_numpy(dtype=np.float32))[:,1]
    metrics=evaluate(y[test],(scores>THRESHOLD).astype(int),scores)
    report=dict(configuration=CONFIGURATION,threshold=THRESHOLD,threshold_operator='>',
                source_sha256=EXPECTED,training_addresses=len(train),test_addresses=len(test),
                test_illicit=int(y[test].sum()),test_licit=int(len(test)-y[test].sum()),
                metrics=metrics,scope='Held-out address-profile test, not independent-case or real-time validation',
                limitations=['Original test previously inspected for the baseline tree; not pristine after research history',
                             'Forest settings selected on validation only; test not used for fitting or adjustment',
                             'No refit with validation; same training-only forest as development comparison',
                             'Related entities/cases may occur across splits',
                             'Original offline licit/illicit labels do not mean stolen funds',
                             'No independent external dataset evaluated'])
    (output/'forest_test_metrics.json').write_text(json.dumps(report,indent=2)+'\n')
    (output/'status.json').write_text(json.dumps(dict(status='complete',metrics_sha256=hashlib.sha256((output/'forest_test_metrics.json').read_bytes()).hexdigest()),indent=2)+'\n')
    print(json.dumps(metrics),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('source',type=Path)
    parser.add_argument('output',type=Path)
    a=parser.parse_args()
    run(a.source,a.output)
