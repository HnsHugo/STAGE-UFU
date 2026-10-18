"""Fixed retraining diagnostic without the previously defined monetary family."""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import numpy as np
import pandas as pd
import sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from train_source_categories import HASHES, prepare, split, metrics
from analyze_validation_errors import SETTINGS
from grouped_permutation_importance import FAMILIES, validate_families

THRESHOLD = .3


def retained_features(columns):
    validate_families(columns)
    result = [c for c in columns if c not in FAMILIES['monetary']]
    if not result: raise ValueError('No retained features')
    return result


def summarize_categories(labels, prediction):
    return {label: {'count': int((labels == label).sum()),
                    'alerts': int(prediction[labels == label].sum())}
            for label in ['benign','Hack','Theft']}


def run(source, diagnostic, output):
    if output.exists(): raise FileExistsError(output)
    for name, expected in HASHES.items():
        with (source/name).open('rb') as handle:
            if hashlib.file_digest(handle, 'sha256').hexdigest() != expected:
                raise ValueError('Source checksum mismatch')
    reference_raw = diagnostic.read_bytes(); reference = json.loads(reference_raw)
    columns = retained_features(reference['features'])
    data = prepare(pd.read_csv(source/'BB.tsv', sep='\t'), pd.read_csv(source/'CB.tsv', sep='\t'))
    train, val, test = split(data)
    if set(train) & set(val) or set(train) & set(test) or set(val) & set(test):
        raise ValueError('Split overlap')
    memberships = {name: hashlib.sha256('\n'.join(sorted(data.iloc[idx].address)).encode()).hexdigest()
                   for name,idx in [('train',train),('validation',val)]}
    if memberships != reference['membership_sha256']: raise ValueError('Split mismatch')
    def numeric(indices):
        return data.iloc[indices][columns].apply(pd.to_numeric, errors='coerce').replace([np.inf,-np.inf], np.nan)
    xt,xv = numeric(train),numeric(val)
    if xt.isna().all().any(): raise ValueError('Entirely missing training feature')
    imputer = SimpleImputer(strategy='median')
    forest = RandomForestClassifier(**SETTINGS)
    forest.fit(imputer.fit_transform(xt), data.iloc[train].label.ne('benign').astype(int))
    scores = forest.predict_proba(imputer.transform(xv))[:,1]
    prediction = (scores > THRESHOLD).astype(int)
    labels = data.iloc[val].label.to_numpy()
    observed = metrics((labels != 'benign').astype(int), prediction, scores)
    baseline = reference['validation_metrics']
    report = {'schema_version':1,'experiment':'monetary_family_ablation_validation_20261018',
        'reference_sha256':hashlib.sha256(reference_raw).hexdigest(),'source_sha256':HASHES,
        'membership_sha256':memberships,'retained_features':columns,'removed_features':FAMILIES['monetary'],
        'model_settings':SETTINGS,'threshold_strictly_greater_than':THRESHOLD,
        'feature_count':len(columns),'effective_max_features_per_tree_split':forest.estimators_[0].max_features_,
        'train_rows':len(train),'validation_rows':len(val),'reserved_test_scored':False,
        'missing_cells':{'train':int(xt.isna().sum().sum()),'validation':int(xv.isna().sum().sum())},
        'preprocessing':'Median fitted on training only, separately for retained columns.',
        'versions':{'python':platform.python_version(),'sklearn':sklearn.__version__,
                    'numpy':np.__version__,'pandas':pd.__version__},
        'validation_metrics':observed,'per_source_category':summarize_categories(labels,prediction),
        'historical_full_forest_validation_no_refit':baseline,
        'delta_against_full_forest':{key:observed[key]-baseline[key] for key in observed},
        'limitations':['Ablation hypothesis prompted by previously inspected validation; development diagnostic, not independent evaluation.',
            'Hyperparameters and threshold reused unchanged; no search, threshold selection or reserved-test evaluation.',
            'max_features=sqrt implies fewer candidate columns per split when feature count changes.',
            'Retraining changes feature interactions and split randomness; result is not a unique causal contribution of amounts.',
            'Fees are retained: removing the monetary family does not remove all financially related information.',
            'One seed and one historical split; no statistical significance or independent entity/incident generalization claimed.',
            'Source labels and lifetime profiles retain attribution and temporal limitations.',
            'External 19-feature model and its threshold remain unchanged.']}
    with output.open('x') as handle:
        json.dump(report,handle,indent=2,allow_nan=False);handle.write('\n')
    print(json.dumps({'metrics':observed,'delta':report['delta_against_full_forest'],
                      'categories':report['per_source_category'],'features':len(columns)},indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for key in ['source','diagnostic','output']:parser.add_argument(key,type=Path)
    args=parser.parse_args();run(args.source,args.diagnostic,args.output)
