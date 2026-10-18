"""Reproduce only the historical benchmark forest's validation predictions."""
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

SETTINGS = dict(n_estimators=100, max_depth=20, min_samples_leaf=20,
                max_features='sqrt', class_weight={0: 1, 1: 3}, random_state=42, n_jobs=2)


def diagnose(labels, prediction, missing):
    labels = np.asarray(labels)
    prediction = np.asarray(prediction)
    missing = np.asarray(missing, dtype=bool)
    if len(labels) != len(prediction) or missing.shape[0] != len(labels):
        raise ValueError('Mismatched diagnostic rows')
    if not set(labels).issubset({'benign', 'Hack', 'Theft'}):
        raise ValueError('Unexpected source category')
    positive = labels != 'benign'
    outcome = np.where(positive, np.where(prediction == 1, 'TP', 'FN'),
                       np.where(prediction == 1, 'FP', 'TN'))
    rows = []
    for label in ['benign', 'Hack', 'Theft']:
        for name, mask in [('all', np.ones(len(labels), dtype=bool)),
                           ('no_missing', ~missing.any(axis=1)),
                           ('any_missing', missing.any(axis=1))]:
            selected = (labels == label) & mask
            count = int(selected.sum())
            alerts = int(prediction[selected].sum())
            rows.append({'source_category': label, 'missingness': name, 'count': count,
                'alerts': alerts, 'alert_rate': alerts / count if count else None,
                'outcomes': {key: int(((outcome == key) & selected).sum()) for key in ['TP','FN','FP','TN']}})
    return {'strata': rows, 'outcomes': {key: int((outcome == key).sum()) for key in ['TP','FN','FP','TN']},
        'missing_by_outcome': {key: {'count': int((outcome == key).sum()),
            'rows_with_missing': int(missing[outcome == key].any(axis=1).sum()),
            'missing_cells_by_feature': missing[outcome == key].sum(axis=0).astype(int).tolist()}
            for key in ['TP','FN','FP','TN']}}


def run(source, reference_path, output):
    if output.exists(): raise FileExistsError(output)
    for name, expected in HASHES.items():
        with (source/name).open('rb') as handle:
            if hashlib.file_digest(handle, 'sha256').hexdigest() != expected:
                raise ValueError('Source checksum mismatch')
    reference_bytes = reference_path.read_bytes()
    reference = json.loads(reference_bytes)
    if reference['selected_model'] != 'forest_depth20' or reference['selected_threshold'] != .3:
        raise ValueError('Historical benchmark configuration changed')
    data = prepare(pd.read_csv(source/'BB.tsv', sep='\t'), pd.read_csv(source/'CB.tsv', sep='\t'))
    train, val, reserved_test = split(data)
    if set(train) & set(val) or set(train) & set(reserved_test) or set(val) & set(reserved_test):
        raise ValueError('Split overlap')
    columns = reference['features']
    def numeric(indices):
        return data.iloc[indices][columns].apply(pd.to_numeric, errors='coerce').replace([np.inf,-np.inf], np.nan)
    xt, xv = numeric(train), numeric(val)  # No reserved-test features are transformed or scored.
    if xt.isna().all().any(): raise ValueError('Entirely missing training feature')
    imputer = SimpleImputer(strategy='median')
    model = RandomForestClassifier(**SETTINGS)
    model.fit(imputer.fit_transform(xt), data.iloc[train].label.ne('benign').astype(int))
    score = model.predict_proba(imputer.transform(xv))[:,1]
    prediction = (score > .3).astype(int)
    labels = data.iloc[val].label.to_numpy()
    reproduced = metrics((labels != 'benign').astype(int), prediction, score)
    expected = next(c['best_validation'] for c in reference['candidates'] if c['name'] == 'forest_depth20')
    for key, value in reproduced.items():
        if not np.isclose(value, expected[key], rtol=0, atol=1e-12):
            raise ValueError('Historical validation mismatch: '+key)
    result = {'schema_version': 1, 'experiment': 'historical_validation_error_diagnostic_20261018',
        'reference_sha256': hashlib.sha256(reference_bytes).hexdigest(), 'source_sha256': HASHES,
        'features': columns, 'settings': SETTINGS, 'threshold_strictly_greater_than': .3,
        'versions': {'python': platform.python_version(), 'sklearn': sklearn.__version__,
                     'numpy': np.__version__, 'pandas': pd.__version__},
        'train_rows': len(train), 'validation_rows': len(val), 'reserved_test_scored': False,
        'membership_sha256': {name: hashlib.sha256('\n'.join(sorted(data.iloc[idx].address)).encode()).hexdigest()
                              for name,idx in [('train',train),('validation',val)]},
        'historical_validation_reproduced': True, 'validation_metrics': reproduced,
        'diagnostic': diagnose(labels, prediction, xv.isna().to_numpy()),
        'limitations': ['22-feature historical source-category benchmark, not the frozen external 19-feature model.',
            'Validation previously selected the model/threshold and is not independent external evaluation.',
            'Associations with missingness are descriptive, not causal explanations or feature attributions.',
            'Small strata have unstable rates; no significance or population performance is inferred.',
            'Source benign/crime categories are not independently verified roles; entity/incident independence unknown.',
            'Lifetime profiles are retrospective, not decision-time data. No hyperparameter or threshold is selected here.']}
    with output.open('x') as handle:
        json.dump(result, handle, indent=2, allow_nan=False); handle.write('\n')
    print(json.dumps({'metrics': reproduced, 'strata': result['diagnostic']['strata']}, indent=2), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ['source','reference','output']: parser.add_argument(key, type=Path)
    args = parser.parse_args(); run(args.source, args.reference, args.output)
