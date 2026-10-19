"""Descriptive validation error analysis; no test access or model tuning."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from train_benchmark import EXPECTED, EXCLUDED, prepare, split_indices, evaluate


def paths(model, columns):
    result = {}
    tree = model.tree_
    def walk(node, conditions):
        if tree.children_left[node] == -1:
            result[node] = conditions
            return
        feature = columns[tree.feature[node]]
        threshold = float(tree.threshold[node])
        walk(tree.children_left[node], conditions + [dict(feature=feature, operator='<=', threshold=threshold)])
        walk(tree.children_right[node], conditions + [dict(feature=feature, operator='>', threshold=threshold)])
    walk(0, [])
    return result


def run(source, output):
    output.mkdir(parents=True, exist_ok=False)
    for filename, digest in EXPECTED.items():
        with (source / filename).open('rb') as f:
            if hashlib.file_digest(f, 'sha256').hexdigest() != digest:
                raise ValueError('Input checksum mismatch')
    data = prepare(pd.read_csv(source/'wallets_features.csv'), pd.read_csv(source/'wallets_classes.csv'))
    train, validation, _ = split_indices(data)
    columns = [c for c in data if c not in EXCLUDED]
    y = (data['class'] == 1).astype(int).to_numpy()
    model = DecisionTreeClassifier(max_depth=8, min_samples_leaf=20, class_weight={0:1, 1:3}, random_state=42)
    model.fit(data.iloc[train][columns], y[train])
    view = data.iloc[validation].copy()
    score = model.predict_proba(view[columns])[:, 1]
    predicted = score > .75
    target = y[validation]
    masks = {'TP': (target==1)&predicted, 'FP': (target==0)&predicted,
             'FN': (target==1)&~predicted, 'TN': (target==0)&~predicted}
    summary = {}
    for name, mask in masks.items():
        subset = view.loc[mask, columns]
        summary[name] = dict(count=int(mask.sum()),
            score_quantiles={str(q):float(np.quantile(score[mask],q)) for q in [0,.25,.5,.75,1]},
            feature_quantiles={c:{str(q):float(subset[c].quantile(q)) for q in [.25,.5,.75]} for c in columns})
    view['error_group'] = np.select([masks[k] for k in ['TP','FP','FN','TN']], ['TP','FP','FN','TN'], default='unknown')
    view['score'] = score
    view['leaf'] = model.apply(view[columns])
    routes = paths(model, columns)
    train_leaves = model.apply(data.iloc[train][columns])
    leaves = []
    for leaf, subset in view.groupby('leaf'):
        counts = subset.error_group.value_counts().to_dict()
        train_mask = train_leaves == leaf
        leaves.append(dict(leaf=int(leaf), validation_count=len(subset), counts={k:int(counts.get(k,0)) for k in masks},
                           score=float(subset.score.iloc[0]),
                           training_count=int(train_mask.sum()), training_illicit_count=int(y[train][train_mask].sum()),
                           training_illicit_fraction=float(y[train][train_mask].mean()),
                           conditions=routes[int(leaf)]))
    report = dict(scope='Descriptive errors on reused validation; offline illicit/licit profiles, not theft diagnosis',
                  model=dict(depth=8, min_samples_leaf=20, class_weight={'0':1,'1':3}, threshold=.75, operator='>'),
                  metrics=evaluate(target,predicted.astype(int),score), groups=summary,
                  top_false_positive_leaves=sorted(leaves,key=lambda r:r['counts']['FP'],reverse=True)[:5],
                  top_false_negative_leaves=sorted(leaves,key=lambda r:r['counts']['FN'],reverse=True)[:5],
                  near_threshold_counts={k:int(((score>.65)&(score<=.85)&v).sum()) for k,v in masks.items()},
                  source_sha256=EXPECTED)
    (output/'error_analysis.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'metrics':report['metrics'],'near_threshold_counts':report['near_threshold_counts'],
                      'top_fp':[(r['leaf'],r['counts'],r['score']) for r in report['top_false_positive_leaves']],
                      'top_fn':[(r['leaf'],r['counts'],r['score']) for r in report['top_false_negative_leaves']]}),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('source',type=Path)
    parser.add_argument('output',type=Path)
    a=parser.parse_args()
    run(a.source,a.output)
