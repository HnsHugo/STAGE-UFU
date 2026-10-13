"""Validation-only weighting and threshold exploration. No test evaluation."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier, export_text
from train_benchmark import EXPECTED, EXCLUDED, prepare, split_indices, evaluate

THRESHOLDS = [.05, .1, .15, .2, .25, .3, .35, .4, .45, .5,
              .55, .6, .65, .7, .75, .8, .85, .9, .95]
WEIGHTS = [('unweighted', None), ('illicit_weight_3', {0: 1, 1: 3}), ('balanced', 'balanced')]


def threshold_results(y, scores):
    scores = np.asarray(scores, dtype=float)
    # Strict > preserves sklearn's class-0 tie break at exactly .5.
    return [dict(threshold=t, **evaluate(y, (scores > t).astype(int), scores)) for t in THRESHOLDS]


def main(source, output):
    output.mkdir(parents=True, exist_ok=False)
    for filename, expected in EXPECTED.items():
        with (source / filename).open('rb') as f:
            if hashlib.file_digest(f, 'sha256').hexdigest() != expected:
                raise ValueError('Input checksum mismatch')
    data = prepare(pd.read_csv(source / 'wallets_features.csv'), pd.read_csv(source / 'wallets_classes.csv'))
    train, validation, _reserved_test = split_indices(data)
    columns = [c for c in data if c not in EXCLUDED]
    y = (data['class'] == 1).astype(int).to_numpy()
    report = dict(scope='Validation-only development; no new held-out test score',
                  comparison='Depth 8 full-profile trees; min leaf 20; seed 42; same original train/validation address split',
                  source_sha256=EXPECTED, thresholds=THRESHOLDS, threshold_operator='strictly greater than', models={})
    for name, weight in WEIGHTS:
        model = DecisionTreeClassifier(max_depth=8, min_samples_leaf=20, class_weight=weight, random_state=42)
        model.fit(data.iloc[train][columns], y[train])
        scores = model.predict_proba(data.iloc[validation][columns])[:, 1]
        results = threshold_results(y[validation], scores)
        best = max(results, key=lambda r: r['f1'])
        report['models'][name] = dict(class_weight=weight, grid=results, best_validation_f1=best)
        (output / (name + '_tree.txt')).write_text(export_text(model, feature_names=columns, decimals=5))
        print(name, json.dumps(best), flush=True)
    configurations = [dict(model=name, **row) for name, value in report['models'].items() for row in value['grid']]
    report['best_validation_f1'] = max(configurations, key=lambda r: r['f1'])
    report['limitations'] = ['Validation reused for configuration selection: selected scores are optimistic development results',
                             'Original test already inspected in previous experiment; not evaluated or used here',
                             'Independent evaluation required before claiming improved generalization',
                             'Offline Elliptic++ illicit/licit labels, not theft or real-time detection',
                             'Scores are not calibrated probabilities']
    (output / 'validation_metrics.json').write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    a = parser.parse_args()
    main(a.source, a.output)
