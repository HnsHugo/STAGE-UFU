"""Fixed univariate baselines on the existing grouped development protocol."""
import argparse
import hashlib
import json
from pathlib import Path
import platform

import numpy as np
import pandas as pd
import sklearn
from sklearn.tree import DecisionTreeClassifier
from train_exploratory import EXPECTED_SHA, metrics
from train_grouped import assign_folds, validate_groups

VARIANTS = {'fee_rate_stump': 'fee_rate_sat_vb',
            'output_count_stump': 'output_count',
            'output_value_stump': 'output_total_sat'}
SETTINGS = {'max_depth': 1, 'min_samples_leaf': 20,
            'class_weight': 'balanced', 'random_state': 42}


def fit_stump(x_train, y_train):
    if not np.isfinite(x_train).all():
        raise ValueError('Nonfinite training feature')
    return DecisionTreeClassifier(**SETTINGS).fit(np.asarray(x_train).reshape(-1, 1), y_train)


def describe(model):
    tree = model.tree_
    return {'threshold': float(tree.threshold[0]) if tree.node_count > 1 else None,
            'left_class': int(model.classes_[tree.value[tree.children_left[0]].argmax()])
                          if tree.node_count > 1 else None,
            'right_class': int(model.classes_[tree.value[tree.children_right[0]].argmax()])
                           if tree.node_count > 1 else None,
            'node_count': int(tree.node_count)}


def summarize(y, prediction):
    result = metrics(y, prediction)
    result['balanced_accuracy_proxy'] = .5 * (result['recall_proxy'] +
        result['true_negative_proxy'] / (result['true_negative_proxy'] + result['false_positive_proxy']))
    return result


def run(source, groups_path, manifest_path, reference_path, output):
    if output.exists():
        raise FileExistsError(output)
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    if digest != EXPECTED_SHA:
        raise ValueError('Unexpected feature data')
    grouping_bytes = groups_path.read_bytes()
    grouping = json.loads(grouping_bytes)
    manifest = json.loads(manifest_path.read_text())
    reference_bytes = reference_path.read_bytes()
    reference = json.loads(reference_bytes)
    df = pd.read_csv(source)
    if (manifest['status'] != 'complete' or len(df) != manifest['transaction_count']
            or df.txid.duplicated().any()):
        raise ValueError('Incomplete or duplicate feature data')
    mapping = validate_groups(df, grouping, manifest)
    df = df[(df.is_coinbase == 0) & (df.relation != 'source_attributed')].reset_index(drop=True)
    if (reference['dataset_sha256'] != digest
            or reference['groups_sha256'] != hashlib.sha256(grouping_bytes).hexdigest()
            or reference['eligible_rows'] != len(df)):
        raise ValueError('Historical reference provenance mismatch')
    y = df.relation.eq('direct_parent_candidate').astype(int).to_numpy()
    groups, folds = assign_folds(df, mapping)
    pooled = {name: np.zeros(len(df), dtype=int) for name in VARIANTS}
    seen = np.zeros(len(df), dtype=int)
    results = []
    for fold, group in enumerate(groups):
        train, test = np.flatnonzero(folds != fold), np.flatnonzero(folds == fold)
        if {mapping[t] for t in df.iloc[train].txid if t in mapping} & {group}:
            raise ValueError('Held-out candidate group leaked into training')
        prior = reference['folds'][fold]
        if (prior['held_out_group'] != group or prior['test_rows'] != len(test)
                or prior['test_candidates'] != int(y[test].sum())):
            raise ValueError('Fold differs from historical reference')
        row = {'held_out_group': group, 'train_rows': len(train), 'test_rows': len(test),
               'test_candidates': int(y[test].sum()), 'models': {}}
        for name, feature in VARIANTS.items():
            x = df[feature].to_numpy(dtype=float)
            if not np.isfinite(x).all():
                raise ValueError('Nonfinite feature')
            model = fit_stump(x[train], y[train])
            prediction = model.predict(x[test].reshape(-1, 1))
            pooled[name][test] = prediction
            row['models'][name] = {'metrics': summarize(y[test], prediction),
                                   'learned_rule': describe(model)}
        seen[test] += 1
        results.append(row)
    if not np.all(seen == 1):
        raise ValueError('Out-of-fold coverage failure')
    report = {'schema_version': 1, 'experiment': 'fixed_univariate_grouped_diagnostic_20261016',
        'dataset_sha256': digest, 'groups_sha256': hashlib.sha256(grouping_bytes).hexdigest(),
        'historical_reference_sha256': hashlib.sha256(reference_bytes).hexdigest(),
        'fold_membership_sha256': hashlib.sha256(''.join(
            f'{txid},{fold}\n' for txid, fold in sorted(zip(df.txid, folds))).encode()).hexdigest(),
        'versions': {'python': platform.python_version(), 'sklearn': sklearn.__version__,
                     'numpy': np.__version__, 'pandas': pd.__version__},
        'settings': SETTINGS, 'features': VARIANTS, 'eligible_rows': len(df),
        'candidate_count': int(y.sum()), 'folds': results,
        'pooled_out_of_fold': {name: summarize(y, pred) for name, pred in pooled.items()},
        'mean_group_recall': {name: float(np.mean([r['models'][name]['metrics']['recall_proxy']
                                                 for r in results])) for name in VARIANTS},
        'historical_reference_no_refit': reference['pooled_out_of_fold'],
        'limitations': ['Same previously inspected groups: development diagnostic, not a new untouched test.',
            'Settings and three features fixed before this run; no validation-based model or threshold selection.',
            'Each split threshold and class balancing use training rows only.',
            'No temporal holdout is imposed; retrospective features do not establish real-time detection.',
            'Candidate groups belong to one source-attributed case; background entity/incident links are unknown.',
            'Unknown background is not certified legitimate; alerts and misses concern proxy relations.',
            'Historical trees, models, scores and the external forest are not modified or retrained.']}
    with output.open('x') as handle:
        json.dump(report, handle, indent=2); handle.write('\n')
    print(json.dumps({'pooled': report['pooled_out_of_fold'],
                      'mean_group_recall': report['mean_group_recall']}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for argument in ['source', 'groups', 'manifest', 'reference', 'output']:
        parser.add_argument(argument, type=Path)
    args = parser.parse_args()
    run(args.source, args.groups, args.manifest, args.reference, args.output)
