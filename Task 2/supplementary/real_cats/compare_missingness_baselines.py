"""Fixed missingness-only baselines; validation diagnostic, no reserved-test scoring."""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import numpy as np
import pandas as pd
import sklearn
from sklearn.tree import DecisionTreeClassifier, export_text
from train_source_categories import HASHES, prepare, split, metrics

SETTINGS = dict(max_depth=2, min_samples_leaf=20, random_state=42)


def missing_indicators(frame):
    numeric = frame.apply(pd.to_numeric, errors='coerce').replace([np.inf, -np.inf], np.nan)
    return numeric.isna().to_numpy(dtype=np.uint8)


def fit_baseline(x, y, balanced):
    x = np.asarray(x)
    if x.ndim != 2 or not np.isin(x, [0, 1]).all():
        raise ValueError('Binary missingness indicators required')
    return DecisionTreeClassifier(**SETTINGS, class_weight='balanced' if balanced else None).fit(x, y)


def evaluate(y, scores):
    result = metrics(y, (scores > .5).astype(int), scores)
    result['alert_count'] = result['true_positive'] + result['false_positive']
    return result


def run(source, diagnostic_path, output):
    if output.exists(): raise FileExistsError(output)
    for name, digest in HASHES.items():
        with (source/name).open('rb') as handle:
            if hashlib.file_digest(handle, 'sha256').hexdigest() != digest:
                raise ValueError('Source checksum mismatch')
    raw = diagnostic_path.read_bytes(); reference = json.loads(raw)
    data = prepare(pd.read_csv(source/'BB.tsv', sep='\t'), pd.read_csv(source/'CB.tsv', sep='\t'))
    train, val, reserved_test = split(data)
    if set(train) & set(val) or set(train) & set(reserved_test) or set(val) & set(reserved_test):
        raise ValueError('Split overlap')
    memberships = {name: hashlib.sha256('\n'.join(sorted(data.iloc[idx].address)).encode()).hexdigest()
                   for name,idx in [('train',train), ('validation',val)]}
    if memberships != reference['membership_sha256']:
        raise ValueError('Split changed since validation diagnostic')
    features = reference['features']
    xt = missing_indicators(data.iloc[train][features])
    xv = missing_indicators(data.iloc[val][features])
    yt = data.iloc[train].label.ne('benign').astype(int).to_numpy()
    yv = data.iloc[val].label.ne('benign').astype(int).to_numpy()
    prevalence = float(yt.mean())
    results = {'constant_training_prevalence': evaluate(yv, np.full(len(val), prevalence))}
    rules = {}
    for name, balanced in [('missingness_tree_unweighted', False), ('missingness_tree_balanced', True)]:
        model = fit_baseline(xt, yt, balanced)
        scores = model.predict_proba(xv)[:,1]
        results[name] = evaluate(yv, scores)
        results[name]['per_category'] = {label: {'count': int((data.iloc[val].label == label).sum()),
            'alerts': int(((scores > .5) & (data.iloc[val].label.to_numpy() == label)).sum())}
            for label in ['benign','Hack','Theft']}
        rules[name] = export_text(model, feature_names=['missing__'+f for f in features], decimals=6)
    patterns = {tuple(row) for row in xt}
    report = {'schema_version': 1, 'experiment': 'missingness_only_validation_baselines_20261018',
        'diagnostic_sha256': hashlib.sha256(raw).hexdigest(), 'source_sha256': HASHES,
        'membership_sha256': memberships, 'original_features': features,
        'feature_definition': '1 iff numeric value is missing, nonnumeric or nonfinite; otherwise 0. No actual values supplied.',
        'settings': SETTINGS, 'threshold_strictly_greater_than': .5,
        'train_rows': len(train), 'validation_rows': len(val), 'training_positive_prevalence': prevalence,
        'validation_positive_prevalence': float(yv.mean()),
        'missingness_patterns': {'train': len(patterns), 'validation': len({tuple(row) for row in xv}),
                                'validation_rows_with_unseen_pattern': sum(tuple(row) not in patterns for row in xv)},
        'versions': {'python': platform.python_version(), 'numpy': np.__version__,
                     'pandas': pd.__version__, 'sklearn': sklearn.__version__},
        'reserved_test_scored': False, 'models': results, 'rules': rules,
        'historical_numeric_forest_validation_no_refit': reference['validation_metrics'],
        'limitations': ['Development diagnostic prompted by previously inspected validation; not independent evaluation.',
            'Two fixed weighting variants and threshold 0.5; no model, threshold or hyperparameter selection.',
            'Historical numeric forest used a previously selected threshold 0.3; compare ranking AP separately from operating-point metrics.',
            'Missingness associations may reflect source selection, behavior or feature definitions; no causal source-bias conclusion.',
            'Source labels do not independently verify attacker/victim roles; entity and incident independence unknown.',
            'Lifetime features and retrospective split do not establish decision-time detection.',
            'External 19-feature model and its threshold remain untouched; leaf scores are not calibrated theft probabilities.']}
    with output.open('x') as handle:
        json.dump(report, handle, indent=2, allow_nan=False); handle.write('\n')
    print(json.dumps({'models':results, 'patterns':report['missingness_patterns']}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ['source','diagnostic','output']: parser.add_argument(key, type=Path)
    args = parser.parse_args(); run(args.source, args.diagnostic, args.output)
