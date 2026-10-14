"""Compare six preset forests on validation; never predict the reserved test."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from train_source_categories import HASHES, DROP, THRESHOLDS, prepare, split, metrics


def run(source, output):
    output.mkdir(parents=True, exist_ok=False)
    for filename, expected in HASHES.items():
        with (source / filename).open('rb') as handle:
            if hashlib.file_digest(handle, 'sha256').hexdigest() != expected:
                raise ValueError('Input checksum mismatch')
    data = prepare(pd.read_csv(source / 'BB.tsv', sep='\t'), pd.read_csv(source / 'CB.tsv', sep='\t'))
    columns = [c for c in data if c not in DROP and 'USD' not in c]
    train, val, reserved_test = split(data)
    # Only training and validation feature matrices are constructed.
    x = data.iloc[np.concatenate([train, val])][columns].apply(pd.to_numeric, errors='coerce').replace([np.inf, -np.inf], np.nan)
    xt_raw, xv_raw = x.iloc[:len(train)], x.iloc[len(train):]
    y = data.label.isin(['Hack', 'Theft']).astype(int).to_numpy()
    labels = data.iloc[val].label.to_numpy()
    report = dict(source_sha256=HASHES, evaluation='Validation only; reserved test not predicted',
                  reserved_test_count=len(reserved_test), candidates=[],
                  fixed_parameters=dict(n_estimators=100, max_depth=20, min_samples_leaf=20, max_features='sqrt', random_state=42),
                  threshold_rule='score strictly greater than threshold; maximize validation F1; first grid threshold wins ties')
    for indicators in [False, True]:
        imputer = SimpleImputer(strategy='median', add_indicator=indicators)
        xt = imputer.fit_transform(xt_raw)
        xv = imputer.transform(xv_raw)
        for weight in [1, 3, 10]:
            model = RandomForestClassifier(**report['fixed_parameters'], class_weight={0:1, 1:weight}, n_jobs=2)
            model.fit(xt, y[train])
            scores = model.predict_proba(xv)[:, 1]
            grid = []
            for threshold in THRESHOLDS:
                pred = (scores > threshold).astype(int)
                categories = {label:dict(count=int((labels == label).sum()), detected=int(pred[labels == label].sum()),
                                        recall=float(pred[labels == label].mean())) for label in ['Hack', 'Theft']}
                grid.append(dict(threshold=threshold, **metrics(y[val], pred, scores), categories=categories))
            if weight == 3 and not indicators:
                baseline = next(row for row in grid if row['threshold'] == .3)
                assert [baseline[k] for k in ['true_positive','false_positive','false_negative','true_negative']] == [72,134,190,17183], 'Baseline reproduction failed'
            candidate = dict(weight=weight, missing_indicators=indicators, features=list(imputer.get_feature_names_out()),
                             best_validation=max(grid, key=lambda row:row['f1']), grid=grid)
            report['candidates'].append(candidate)
            print(weight, indicators, json.dumps(candidate['best_validation']), flush=True)
    best = max(report['candidates'], key=lambda row:row['best_validation']['f1'])
    report['selected_on_validation'] = dict(weight=best['weight'], missing_indicators=best['missing_indicators'], **best['best_validation'])
    report['limitations'] = ['Repeated validation selection is optimistic; improvement is not independently confirmed',
                            'Source Hack/Theft reports and assumed benign recipients are not verified incident roles',
                            'Full-history features support an offline benchmark, not decision-time detection',
                            'Class weighting changes scores; scores are not calibrated probabilities']
    (output / 'metrics.json').write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    run(args.source, args.output)
