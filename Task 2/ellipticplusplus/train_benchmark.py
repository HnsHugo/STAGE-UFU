"""Offline address classification on pinned Elliptic++ data, not theft detection."""
import argparse
import hashlib
import json
import platform
from pathlib import Path
import numpy as np
import pandas as pd
import sklearn
from sklearn.metrics import average_precision_score, confusion_matrix, precision_recall_fscore_support
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, export_text

EXPECTED = {
    'wallets_classes.csv': '4e5132c99f941666bf1fefd4100a1428d339c9252ec6987909e1adf8eac902f9',
    'wallets_features.csv': '317daca2810c355ddfdb8c0dab34cf11d1aa90567fe975090c7e5a901386eb77',
}
EXCLUDED = ['address', 'Time step', 'first_block_appeared_in',
            'last_block_appeared_in', 'first_sent_block', 'first_received_block', 'class']


def prepare(features, labels):
    if labels.address.duplicated().any():
        raise ValueError('Duplicate address labels')
    if not set(labels['class']).issubset({1, 2, 3}):
        raise ValueError('Unsupported original class')
    if features.address.isna().any() or labels.address.isna().any():
        raise ValueError('Missing address')
    columns = [c for c in features if c not in ('address', 'Time step')]
    if not np.isfinite(features[columns].to_numpy(dtype=float)).all():
        raise ValueError('Missing or nonfinite features')
    # Repeated observations are collapsible only if all non-temporal features agree.
    profiles = features[['address'] + columns].drop_duplicates()
    if profiles.address.duplicated().any():
        raise ValueError('Address features vary across observations; revise protocol')
    if set(profiles.address) != set(labels.address):
        raise ValueError('Feature/label address coverage mismatch')
    joined = profiles.merge(labels, on='address', validate='one_to_one')
    return joined[joined['class'].isin([1, 2])].sort_values('address').reset_index(drop=True)


def split_indices(data):
    y = (data['class'] == 1).astype(int).to_numpy()
    indices = np.arange(len(data))
    train, remainder = train_test_split(indices, test_size=.4, stratify=y, random_state=42)
    validation, test = train_test_split(remainder, test_size=.5, stratify=y[remainder], random_state=43)
    sets = [set(data.iloc[i].address) for i in (train, validation, test)]
    if any(sets[a] & sets[b] for a, b in ((0, 1), (0, 2), (1, 2))):
        raise ValueError('Address leakage across splits')
    return train, validation, test


def evaluate(y, prediction, score):
    precision, recall, f1, _ = precision_recall_fscore_support(y, prediction, average='binary', zero_division=0)
    tn, fp, fn, tp = confusion_matrix(y, prediction, labels=[0, 1]).ravel()
    return dict(precision=float(precision), recall=float(recall), f1=float(f1),
                average_precision=float(average_precision_score(y, score)),
                true_negative=int(tn), false_positive=int(fp), false_negative=int(fn), true_positive=int(tp))


def run(source, output):
    output.mkdir(parents=True, exist_ok=False)
    (output / 'status.json').write_text(json.dumps({'status': 'incomplete'}))
    for name, expected in EXPECTED.items():
        with (source / name).open('rb') as f:
            if hashlib.file_digest(f, 'sha256').hexdigest() != expected:
                raise ValueError('Input checksum mismatch: ' + name)
    features = pd.read_csv(source / 'wallets_features.csv')
    labels = pd.read_csv(source / 'wallets_classes.csv')
    audit = dict(raw_rows=len(features), unique_addresses=int(features.address.nunique()),
                 exact_duplicate_rows=int(features.duplicated().sum()),
                 duplicate_address_time_rows=int(features.duplicated(['address', 'Time step']).sum()),
                 original_class_counts={str(k): int(v) for k, v in labels['class'].value_counts().items()},
                 missing_feature_cells=int(features.isna().sum().sum()),
                 source_sha256=EXPECTED, time_steps=[int(features['Time step'].min()), int(features['Time step'].max())])
    data = prepare(features, labels)
    del features
    audit.update(eligible_addresses=len(data), collapsed_non_temporal_profiles=True,
                 address_feature_conflicts=0, unknown_addresses_excluded=int((labels['class'] == 3).sum()))
    (output / 'audit.json').write_text(json.dumps(audit, indent=2) + '\n')
    print('Audit complete:', len(data), 'labeled address profiles', flush=True)
    train, validation, test = split_indices(data)
    y = (data['class'] == 1).astype(int).to_numpy()
    splits = {}
    assignment = pd.DataFrame({'address': data.address, 'original_class': data['class'], 'split': ''})
    for name, indices in [('train', train), ('validation', validation), ('test', test)]:
        assignment.loc[indices, 'split'] = name
        splits[name] = dict(addresses=len(indices), illicit=int(y[indices].sum()), licit=int(len(indices) - y[indices].sum()))
    assignment.to_csv(output / 'split_assignments.csv.gz', index=False, compression='gzip')
    all_columns = [c for c in data if c not in EXCLUDED]
    candidates = []
    fitted = {}
    # Candidate settings are fixed before validation. The test set is not inspected here.
    for variant in ('all_profile_features', 'without_fee_features'):
        columns = [c for c in all_columns if variant == 'all_profile_features' or not c.startswith('fees')]
        for depth in (4, 8):
            name = f'{variant}_depth_{depth}'
            model = DecisionTreeClassifier(max_depth=depth, min_samples_leaf=20, class_weight='balanced', random_state=42)
            model.fit(data.iloc[train][columns], y[train])
            validation_scores = model.predict_proba(data.iloc[validation][columns])[:, 1]
            result = evaluate(y[validation], model.predict(data.iloc[validation][columns]), validation_scores)
            candidates.append(dict(name=name, max_depth=depth, feature_count=len(columns), validation=result))
            fitted[name] = (model, columns)
            (output / (name + '.txt')).write_text(export_text(model, feature_names=columns, decimals=5))
            print(name, 'validation', result, flush=True)
    # Maximize validation F1; candidate order breaks ties in favour of the first model.
    selected = max(candidates, key=lambda row: row['validation']['f1'])
    model, columns = fitted[selected['name']]
    scores = model.predict_proba(data.iloc[test][columns])[:, 1]
    prediction = model.predict(data.iloc[test][columns])
    test_metrics = evaluate(y[test], prediction, scores)
    test_data = pd.DataFrame(dict(address=data.iloc[test].address.to_numpy(), target=y[test],
                                 prediction=prediction, illicit_profile_score=scores))
    test_data.to_csv(output / 'test_predictions.csv.gz', index=False, compression='gzip')
    baseline = evaluate(y[test], np.zeros(len(test), dtype=int), np.zeros(len(test)))
    report = dict(target='Original Elliptic++ illicit (class 1) versus licit (class 2) address profiles',
                  scope='Offline historical-profile benchmark; not real-time, hardware-wallet or stolen-fund detection',
                  versions=dict(python=platform.python_version(), numpy=np.__version__, pandas=pd.__version__, sklearn=sklearn.__version__),
                  source_sha256=EXPECTED, splits=splits, split_policy='Sorted unique addresses; stratified 60/20/20; random states 42 and 43',
                  excluded_features=EXCLUDED, candidates=candidates, selected_model=selected['name'],
                  selection_rule='Maximum validation F1; threshold fixed by classifier; no test tuning',
                  selected_model_test=test_metrics, always_licit_test=baseline,
                  features=columns, feature_importances={c: float(v) for c, v in zip(columns, model.feature_importances_) if v},
                  limitations=['Address separation does not establish entity or case independence',
                               'Full-history aggregate features may include events later than their Time step',
                               'No causal temporal evaluation or theft-case external validation',
                               'Class-weighted scores are not calibrated illicitness probabilities',
                               'Unknown labels excluded; no claim of coverage/performance on unknown addresses'])
    (output / 'metrics.json').write_text(json.dumps(report, indent=2) + '\n')
    tree = model.tree_
    export = dict(schema_version=1, selected_model=selected['name'], features=columns, classes=[0, 1],
                  class_meanings={'0': 'Elliptic++ licit', '1': 'Elliptic++ illicit'},
                  children_left=tree.children_left.tolist(), children_right=tree.children_right.tolist(),
                  feature=tree.feature.tolist(), threshold=tree.threshold.tolist(),
                  weighted_class_proportions=tree.value[:, 0, :].tolist(),
                  input_precision='scikit-learn float32 conversion', scope=report['scope'], source_sha256=EXPECTED)
    (output / 'selected_tree.json').write_text(json.dumps(export, indent=2) + '\n')
    artifacts = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in output.iterdir() if p.name != 'status.json'}
    (output / 'status.json').write_text(json.dumps(dict(status='complete', artifacts_sha256=artifacts), indent=2) + '\n')
    print('SELECTED:', selected['name'], 'TEST:', test_metrics, flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    run(args.source, args.output)
