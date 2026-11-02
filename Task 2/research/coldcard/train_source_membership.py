"""Fit the single prespecified Coldcard source-membership tree; verify without refitting.

One frozen within-window development split, fourteen prior-block predictors and
fourteen fixed missing indicators. Exports plain JSON instead of executable pickle.
"""
import argparse
from collections import Counter, defaultdict
import gzip
from io import BytesIO
import json
from pathlib import Path
import platform

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import scipy
import sklearn
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.tree import DecisionTreeClassifier
from threadpoolctl import threadpool_limits

import audit_source_comparison_feasibility as audit


ROOT = Path(__file__).resolve().parent
FEATURES = list(audit.FEATURE_NAMES)
INPUT_NAMES = FEATURES + ['missing__' + name for name in FEATURES]
TARGET = audit.TARGET
THRESHOLD = .5
EXTRA_PARAMETERS = dict(max_leaf_nodes=None, min_impurity_decrease=0.0,
                        min_weight_fraction_leaf=0.0, monotonic_cst=None)
PARTS = ('train', 'validation', 'test')


def runtime():
    return dict(python=platform.python_version(), numpy=np.__version__,
                scipy=scipy.__version__, sklearn=sklearn.__version__,
                matplotlib=matplotlib.__version__)


def compressed(value):
    return gzip.compress(audit.json_bytes(value), mtime=0)


def frozen_split(view, groups, feasibility):
    """Materialize exactly the audited eligible population and hash buckets."""
    rows = audit.index_rows(view['rows'])
    eligible = {key for key, row in rows.items() if row['features'] is not None}
    assignment, component_ids = {}, {}
    counts = {part: dict(case=0, comparison=0, components=0) for part in PARTS}
    for group in groups['components']:
        members = group['source_ids']
        audit.require(members == sorted(set(members)) and members, 'Invalid frozen component')
        audit.require(set(members) <= eligible, 'Unfinished source in component')
        minimum = min(rows[key]['address_sha256'] for key in members)
        audit.require(minimum == group['minimum_address_sha256'] and
                      group['component_id'] == audit.digest(audit.json_bytes(members)), 'Component identity changed')
        part = audit.partition_for(minimum)
        counts[part]['components'] += 1
        for key in members:
            audit.require(key not in assignment, 'Repeated component member')
            assignment[key], component_ids[key] = part, group['component_id']
            counts[part]['case' if rows[key][TARGET] else 'comparison'] += 1
    audit.require(set(assignment) == eligible, 'Frozen eligible universe changed')
    audit.require(counts == feasibility['frozen_partition_feasibility']['counts'], 'Audited buckets changed')
    audit.require(all(c[k] >= 20 for c in counts.values() for k in ('case', 'comparison')), 'Class minimum failed')
    for records in groups['shared_link_evidence'].values():
        for record in records:
            audit.require(len({assignment[key] for key in record['source_ids']}) == 1, 'Shared evidence crosses buckets')
    records = []
    for key, row in sorted(rows.items()):
        records.append(dict(source_id=key, address_sha256=row['address_sha256'],
                            cutoff_height=row['cutoff_height'], known_coldcard_core_membership=row[TARGET],
                            component_id=component_ids.get(key),
                            partition=assignment.get(key, 'excluded_unavailable_prefix'),
                            precutoff_history_status=row['precutoff_history_status'],
                            full_history_status=row['full_history_status']))
    return dict(schema_version=1, target=TARGET, partition_rule=audit.PARTITION,
                counts=counts, excluded_sources=len(rows)-len(eligible), rows=records,
                incident_count=1, independent_incident_split=False)


def matrix(rows):
    for row in rows:
        audit.vector_key(row['features'])
    return np.asarray([[np.nan if row['features'][key] is None else row['features'][key]
                        for key in FEATURES] for row in rows], dtype=np.float64)


def fit_preprocessing(train_rows):
    raw = matrix(train_rows)
    medians, all_missing = [], []
    for col, name in enumerate(FEATURES):
        observed = raw[~np.isnan(raw[:, col]), col]
        medians.append(float(np.median(observed)) if len(observed) else 0.0)
        if not len(observed):
            all_missing.append(name)
    return dict(predictor_allowlist=FEATURES, model_input_names=INPUT_NAMES,
                medians=medians, all_missing_training_columns=all_missing,
                zero_fallback_policy='Only all-missing training columns',
                fit_partition='train', fit_rows=len(train_rows),
                fit_source_ids_sha256=audit.digest(audit.json_bytes([r['source_id'] for r in train_rows])),
                comparator_missing_values='Use these same training medians; rank larger inactivity/balance higher.')


def transform(rows, state):
    audit.require(state['predictor_allowlist'] == FEATURES and state['model_input_names'] == INPUT_NAMES,
                  'Preprocessor feature order changed')
    raw = matrix(rows)
    missing = np.isnan(raw)
    filled = np.where(missing, np.asarray(state['medians']), raw)
    output = np.concatenate([filled, missing.astype(np.float64)], axis=1)
    audit.require(np.isfinite(output).all(), 'Nonfinite transformed input')
    return output, missing


def score_export(model, transformed):
    """Replay scikit-learn's float32 input conversion and <= branch rule."""
    audit.require(model['model_input_names'] == INPUT_NAMES, 'Export feature allowlist changed')
    values = np.asarray(transformed, dtype=np.float32)
    audit.require(values.ndim == 2 and values.shape[1] == len(INPUT_NAMES) and np.isfinite(values).all(),
                  'Invalid tree inputs')
    tree = model['tree']
    scores, leaves, paths = [], [], []
    for row in values:
        node, path = 0, []
        while True:
            audit.require(0 <= node < len(tree['feature_indices']) and node not in path, 'Invalid/cyclic exported tree')
            path.append(node)
            left, right = tree['children_left'][node], tree['children_right'][node]
            if left == -1:
                audit.require(right == -1, 'Asymmetric leaf')
                break
            feature = tree['feature_indices'][node]
            audit.require(0 <= feature < len(INPUT_NAMES), 'Disallowed split feature')
            node = left if float(row[feature]) <= tree['thresholds'][node] else right
        scores.append(tree['case_membership_score'][node])
        leaves.append(node)
        paths.append(path)
    return np.asarray(scores), np.asarray(leaves), paths


def metrics(y, scores, classify=False):
    y, scores = np.asarray(y), np.asarray(scores)
    audit.require(set(y.tolist()) == {0, 1} and np.isfinite(scores).all(), 'Invalid metric input')
    result = dict(rows=len(y), case=int(y.sum()), comparison=int((y == 0).sum()),
                  sampled_membership_prevalence=float(y.mean()),
                  average_precision_membership=float(average_precision_score(y, scores)),
                  roc_auc_membership=float(roc_auc_score(y, scores)))
    if classify:
        pred = scores >= THRESHOLD
        tp, fp = int(np.sum(pred & (y == 1))), int(np.sum(pred & (y == 0)))
        fn, tn = int(np.sum(~pred & (y == 1))), int(np.sum(~pred & (y == 0)))
        result.update(threshold=THRESHOLD, threshold_operator='>=',
                      true_positive_membership=tp, false_positive_membership=fp,
                      false_negative_membership=fn, true_negative_membership=tn,
                      precision_membership=tp/(tp+fp) if tp+fp else 0.,
                      recall_membership=tp/(tp+fn), f1_membership=2*tp/(2*tp+fp+fn))
    return result


def independent_ranking(y, scores):
    """Tied score-group AP and pair-count ROC-AUC, without sklearn metrics."""
    groups = defaultdict(lambda: [0, 0])
    for label, score in zip(y, scores):
        groups[float(score)][int(label)] += 1
    positives, negatives = sum(y), len(y)-sum(y)
    tp, seen, ap = 0, 0, 0.
    for score in sorted(groups, reverse=True):
        neg, pos = groups[score]
        tp, seen = tp+pos, seen+pos+neg
        ap += pos/positives * tp/seen
    lower_negatives, wins = 0, 0.
    for score in sorted(groups):
        neg, pos = groups[score]
        wins += pos * (lower_negatives + .5*neg)
        lower_negatives += neg
    return dict(average_precision_membership=float(ap), roc_auc_membership=float(wins/(positives*negatives)))


def inputs(protocol_path):
    protocol = audit.load_json(protocol_path)
    paths = {key: audit.read_pin(ROOT, pin) for key, pin in protocol['inputs'].items()}
    audit.require(protocol['runtime'] == runtime(), 'Pinned runtime differs')
    audit.require(paths['runner'] == Path(__file__).resolve(), 'Wrong runner implementation')
    design = audit.load_json(paths['design'])
    audit.require(protocol['estimator_parameters'] ==
                  dict(design['evaluation']['learned_baseline']['parameters'], **EXTRA_PARAMETERS), 'Frozen estimator changed')
    audit.require(protocol['partition_rule'] == audit.PARTITION and protocol['decision_threshold'] == THRESHOLD,
                  'Frozen evaluation rule changed')
    audit.require(design['predictors'] == FEATURES and design['primary_target']['name'] == TARGET, 'Target/features changed')
    old_protocol = audit.load_json(paths['feasibility_protocol'])
    # Reuse the already completed audit: verify its pins/outputs, do not refit or recollect.
    for pin in old_protocol['inputs'].values():
        audit.read_pin(ROOT, pin)
    old_verification = audit.load_json(paths['feasibility_verification'])
    audit.require(old_verification['protocol_sha256'] == audit.digest(paths['feasibility_protocol'].read_bytes()),
                  'Prior audit protocol mismatch')
    for name, expected in old_verification['outputs'].items():
        audit.require(audit.digest((paths['feasibility_protocol'].parent/name).read_bytes()) == expected,
                      'Prior audit output changed')
    view, groups, summary = [audit.load_json(paths[k]) for k in ('view', 'groups', 'feasibility_summary')]
    audit.require(view['predictor_allowlist'] == FEATURES and view['schema_version'] == 2, 'Wrong predictor view')
    split = frozen_split(view, groups, summary)
    audit.require(compressed(split) == paths['frozen_split'].read_bytes(), 'Pre-fit frozen split changed')
    by_id = audit.index_rows(view['rows'])
    selected = {p: [by_id[r['source_id']] for r in split['rows'] if r['partition'] == p] for p in PARTS}
    audit.require(sum(map(len, selected.values())) == summary['available_vectors'], 'Predictor coverage changed')
    return protocol, paths, split, selected, summary


def export_tree(fitted, preprocessing, protocol):
    audit.require(fitted.classes_.tolist() == [0, 1], 'Class order changed')
    tree = fitted.tree_
    values = tree.value[:, 0, :]
    audit.require(np.allclose(values.sum(axis=1), 1), 'Unexpected sklearn node value convention')
    return dict(schema_version=1, target=TARGET, model_input_names=INPUT_NAMES,
                preprocessing=preprocessing, parameters=fitted.get_params(), runtime=runtime(),
                input_commit=protocol['input_commit'], training_fit_calls=1,
                fit_partition='train', validation_used_for_selection=False, test_used_for_selection=False,
                score_interpretation='Class-balanced training leaf proportion; not calibrated theft/device probability.',
                threshold=THRESHOLD, threshold_operator='>=', input_conversion='float32 before tree traversal',
                tree=dict(children_left=tree.children_left.tolist(), children_right=tree.children_right.tolist(),
                          feature_indices=tree.feature.tolist(), thresholds=tree.threshold.tolist(),
                          case_membership_score=values[:, 1].tolist(),
                          training_node_samples=tree.n_node_samples.tolist(),
                          weighted_training_node_samples=tree.weighted_n_node_samples.tolist(),
                          max_depth=int(tree.max_depth), node_count=int(tree.node_count)),
                training_impurity_importances=fitted.feature_importances_.tolist())


def analyze_export(model, selected, split, prior_summary):
    preprocessing = fit_preprocessing(selected['train'])
    audit.require(preprocessing == model['preprocessing'], 'Preprocessing is not training-only')
    train_n = len(selected['train'])
    train_case = sum(r[TARGET] for r in selected['train'])
    class_weights = {0: train_n/(2*(train_n-train_case)), 1: train_n/(2*train_case)}
    predictions, metric_records, errors = [], {}, []
    component_by_id = {r['source_id']: r['component_id'] for r in split['rows']}
    support = {i: {part: dict(case=0, comparison=0, imputed_split_rows=0) for part in PARTS}
               for i in range(model['tree']['node_count'])}
    missing_counts = {}
    for part in PARTS:
        rows = selected[part]
        x, missing = transform(rows, preprocessing)
        scores, leaves, paths = score_export(model, x)
        audit.require(max(map(len, paths))-1 <= 3, 'Actual tree depth exceeds frozen bound')
        y = np.asarray([r[TARGET] for r in rows])
        comparator_scores = dict(constant_train_prevalence=np.full(len(rows), train_case/train_n),
                                 inactivity_rank=x[:, FEATURES.index('blocks_since_last_activity')],
                                 balance_rank=x[:, FEATURES.index('balance_sat')])
        metric_records[part] = dict(tree=metrics(y, scores, True),
                                   **{name: metrics(y, values) for name, values in comparator_scores.items()})
        for name, values in dict(tree=scores, **comparator_scores).items():
            independent = independent_ranking(y, values)
            audit.require(all(abs(metric_records[part][name][k]-value) < 1e-12 for k, value in independent.items()),
                          'Independent ranking metric disagreement')
        missing_counts[part] = {name: int(missing[:, col].sum()) for col, name in enumerate(FEATURES)}
        for i, row in enumerate(rows):
            pred = int(scores[i] >= THRESHOLD)
            record = dict(source_id=row['source_id'], partition=part,
                          known_coldcard_core_membership=row[TARGET],
                          predicted_known_coldcard_core_membership=pred,
                          case_membership_score=float(scores[i]), leaf_id=int(leaves[i]),
                          component_id=component_by_id[row['source_id']],
                          missing_features=[name for col, name in enumerate(FEATURES) if missing[i, col]],
                          **{name: float(values[i]) for name, values in comparator_scores.items()})
            predictions.append(record)
            if pred != row[TARGET]:
                errors.append(dict(record, error_type='false_negative_membership' if row[TARGET] else 'false_positive_membership',
                                   features=row['features'], cutoff_height=row['cutoff_height'],
                                   compromise_status='unknown', independently_verified_device_status='unknown'))
            for node in paths[i]:
                c = support[node][part]
                c['case' if row[TARGET] else 'comparison'] += 1
                col = model['tree']['feature_indices'][node]
                c['imputed_split_rows'] += int(0 <= col < len(FEATURES) and missing[i, col])
    tree = model['tree']
    for node, counts in support.items():
        c = counts['train']
        raw_n = c['case'] + c['comparison']
        weight = c['case']*class_weights[1] + c['comparison']*class_weights[0]
        audit.require(raw_n == tree['training_node_samples'][node], 'Exported training node support mismatch')
        audit.require(abs(weight-tree['weighted_training_node_samples'][node]) < 1e-8, 'Class balancing not training-only')
        expected_score = c['case']*class_weights[1]/weight
        audit.require(abs(expected_score-tree['case_membership_score'][node]) < 1e-12, 'Weighted score/support mismatch')
        if tree['children_left'][node] == -1:
            audit.require(raw_n >= 20, 'Leaf violates frozen minimum size')
    audit.require(tree['max_depth'] <= 3, 'Depth bound exceeded')
    rules = leaf_rules(model, support)
    used = sorted({i for i in tree['feature_indices'] if i >= 0})
    summary = dict(schema_version=1, target=TARGET, partition_metrics=metric_records,
                   partition_counts=split['counts'], selected_sources=len(split['rows']),
                   available_vectors=sum(len(rows) for rows in selected.values()),
                   excluded_unavailable_prefixes=split['excluded_sources'],
                   full_history_comparison_statuses=prior_summary['full_history_comparison_statuses'],
                   node_count=tree['node_count'], depth=tree['max_depth'], leaves=len(rules),
                   split_feature_names=[INPUT_NAMES[i] for i in used],
                   used_missing_indicators=[INPUT_NAMES[i] for i in used if i >= len(FEATURES)],
                   node_support={str(k): v for k, v in support.items()}, missing_values_by_partition=missing_counts,
                   training_class_weights={str(k): v for k, v in class_weights.items()},
                   errors_by_partition={part: dict(Counter(e['error_type'] for e in errors if e['partition'] == part)) for part in PARTS},
                   independent_ranking_metrics_verified=True, exported_node_support_verified=True,
                   collection_performed=False, training_performed=True, training_fit_calls=1,
                   preprocessing_fit_partition='train', validation_used_for_selection=False,
                   test_used_for_selection=False, hyperparameter_search_performed=False,
                   resampling_performed=False, external_forest_modified=False,
                   evaluation_scope='Previously inspected within-window development. One incident; complete-case coverage bias. Unknown compromise/device labels. Not an independent-incident or untouched prospective test.')
    return summary, predictions, errors, rules


def leaf_rules(model, support):
    tree, result = model['tree'], []

    def visit(node, conditions):
        col = tree['feature_indices'][node]
        if tree['children_left'][node] == -1:
            result.append(dict(leaf_id=node, conditions=conditions,
                               case_membership_score=tree['case_membership_score'][node],
                               predicted_known_coldcard_core_membership=int(tree['case_membership_score'][node] >= THRESHOLD),
                               support=support[node]))
            return
        for child, op in [(tree['children_left'][node], '<='), (tree['children_right'][node], '>')]:
            visit(child, conditions + [dict(feature=INPUT_NAMES[col], operator=op, threshold=tree['thresholds'][node])])
    visit(0, [])
    return result


def tree_figure(model, summary):
    """Plain tree diagram showing raw train supports rather than weighted counts."""
    tree, coordinates, leaf_position = model['tree'], {}, [0]

    def position(node, depth):
        if tree['children_left'][node] == -1:
            x = leaf_position[0]
            leaf_position[0] += 1
        else:
            x = (position(tree['children_left'][node], depth+1) + position(tree['children_right'][node], depth+1))/2
        coordinates[node] = (x, -depth)
        return x
    position(0, 0)
    with matplotlib.rc_context({'svg.hashsalt': 'coldcard-membership-tree-42', 'font.family': 'DejaVu Sans'}):
        fig, ax = plt.subplots(figsize=(max(10, leaf_position[0]*3.1), 7.2))
        for node, (x, y) in coordinates.items():
            col = tree['feature_indices'][node]
            c = summary['node_support'][str(node)]['train']
            title = (INPUT_NAMES[col] + '\n<= ' + format(tree['thresholds'][node], '.8g')) if col >= 0 else f'Leaf {node}'
            text = title + f"\nTrain: {c['case']} case / {c['comparison']} comparison\nWeighted membership score: {tree['case_membership_score'][node]:.4f}"
            for child in (tree['children_left'][node], tree['children_right'][node]):
                if child >= 0:
                    cx, cy = coordinates[child]
                    ax.plot([x, cx], [y-.13, cy+.16], color='#94a3b8', linewidth=1.2, zorder=0)
                    ax.text((x+cx)/2, (y+cy)/2, '<=' if child == tree['children_left'][node] else '>',
                            fontsize=9, ha='center', bbox=dict(facecolor='white', edgecolor='none', pad=1))
            ax.text(x, y, text, ha='center', va='center', fontsize=8.5,
                    bbox=dict(boxstyle='round,pad=.55', facecolor='#e6f4ed' if tree['case_membership_score'][node] >= .5 else '#eef2f8', edgecolor='#64748b'))
        ax.set_xlim(-.7, leaf_position[0]-.3)
        ax.set_ylim(-tree['max_depth']-.55, .6)
        ax.axis('off')
        fig.suptitle('Coldcard core membership — frozen exploratory tree', fontsize=15, weight='bold')
        fig.text(.5, .025, '14 prior-block features + fixed missing indicators | Depth <= 3 | Min. training leaf = 20 | One incident; unknown theft/device labels', ha='center', fontsize=9)
        fig.subplots_adjust(left=.025, right=.975, bottom=.08, top=.9)
        output = BytesIO()
        fig.savefig(output, format='svg', metadata={'Date': None, 'Creator': 'Coldcard source-membership baseline'})
        plt.close(fig)
    return output.getvalue()


def report(protocol_path, model, s, rules):
    lines = ['# Frozen source-membership baseline — 2 November 2026', '',
             'One prespecified shallow decision tree was fitted on training addresses only. Target: `known_coldcard_core_membership`. The unit is one unique selected input source address. This is retrospective within-window development on previously inspected case profiles; all 500 cases belong to one incident. Independently verified compromise/device labels remain unknown.', '',
             '## Frozen inputs and preparation', '',
             'The latest schema-v2 view supplies 1,378 vectors (500 cases, 878 comparisons) from 1,500 fixed selections. The 122 bounded-incomplete comparison prefixes retain null vectors and no scores. Their much larger saved full-current-history counters establish an important coverage limitation; no unavailable prior-block vector was imputed. Full-history comparison statuses stay 864 complete / 136 incomplete, separate from prefix coverage.', '',
             'The 918 audited components and the original SHA256 salt/buckets are unchanged. Shared prior references, reference TXIDs and full vectors do not cross partitions in the observed completed evidence. Unknown links of excluded histories are not claimed absent. The entire reference block and future are excluded from the fourteen predictors.', '',
             '| Partition | Cases | Comparisons | Components |', '| --- | ---: | ---: | ---: |']
    for part, c in s['partition_counts'].items():
        lines.append(f"| {part} | {c['case']} | {c['comparison']} | {c['components']} |")
    lines += ['', 'Depth 3, minimum 20 training rows per leaf, balanced training class weights, seed 42; all other parameters are pinned in `protocol.json`. One training fit, no parameter search, rerolled groups, threshold selection or refit on validation/test. The membership threshold is **score >= 0.5**, including equality.', '',
              'Each original column uses its training median; zero is a fallback only if that entire training column is missing. Fourteen fixed missingness indicators accompany the fourteen unchanged predictors. The inactivity and balance ranking comparators use the same training-only median fills. No identifiers, block metadata, collection counters, reference-payment fields or evidence labels enter the model.', '',
              '## Metrics', '',
              '| Partition | Method | Membership AP | Membership ROC-AUC | Membership precision | Membership recall | Membership F1 |',
              '| --- | --- | ---: | ---: | ---: | ---: | ---: |']
    for part in PARTS:
        for name, m in s['partition_metrics'][part].items():
            classification = [f"{m[key]:.6f}" if key in m else '—' for key in ('precision_membership', 'recall_membership', 'f1_membership')]
            lines.append(f"| {part} | {name} | {m['average_precision_membership']:.6f} | {m['roc_auc_membership']:.6f} | " + ' | '.join(classification) + ' |')
    lines += ['', 'Train metrics are resubstitution diagnostics. Validation and test are fixed development partitions from the same previously inspected incident/window. Every AP and ROC-AUC was independently recomputed from tied score groups and pair counts. Constant/univariate methods have ranking metrics only. Scores are class-balanced leaf proportions, not calibrated theft/device probabilities. The sampled prevalences differ from blockchain prevalence.', '',
              '| Partition | True positive membership | False positive membership | False negative membership | True negative membership |',
              '| --- | ---: | ---: | ---: | ---: |']
    for part in PARTS:
        m = s['partition_metrics'][part]['tree']
        lines.append(f"| {part} | {m['true_positive_membership']} | {m['false_positive_membership']} | {m['false_negative_membership']} | {m['true_negative_membership']} |")
    lines += ['', '## Rules, support and missingness', '',
              '![Frozen membership tree](tree.svg)', '',
              'Node supports in the diagram are raw training-address counts. Scores use training class weights. Exact float32-routing thresholds, node supports by partition and leaf conditions are saved in `model.json`, `summary.json` and `rules.json`.', '',
              '| Leaf | Conditions (all required) | Score | Train case/comparison | Validation case/comparison | Test case/comparison |',
              '| --- | --- | ---: | ---: | ---: | ---: |']
    for rule in rules:
        conditions = '; '.join(f"{c['feature']} {c['operator']} {c['threshold']:.10g}" for c in rule['conditions']) or 'All rows'
        counts = [f"{rule['support'][p]['case']}/{rule['support'][p]['comparison']}" for p in PARTS]
        lines.append(f"| {rule['leaf_id']} | {conditions} | {rule['case_membership_score']:.6f} | " + ' | '.join(counts) + ' |')
    lines += ['', f"Used input columns: {', '.join(s['split_feature_names'])}. Used explicit missing indicators: {', '.join(s['used_missing_indicators']) or 'none'}.", '',
              'No explicit indicator split does not imply independence from missingness: a numeric split can route a median-imputed value. `node_support` records how many addresses use an imputed value at each numeric split; per-feature missingness by partition is also saved. Undefined fees remain distinct from unavailable vectors. No ablation or additional model was fitted.', '',
              '`predictions.json.gz` records all 1,378 eligible source IDs, components, partitions, scores, comparator ranks and missing columns. `errors.json.gz` lists each membership error with the original fourteen features; comparisons are not relabeled as legitimate or compromised. `split_manifest.json.gz` retains all 1,500 selections, including the 122 exclusions.', '',
              '## Interpretation and next unit', '',
              'Interpret performance only as retrospective separation of this selected, covered case-membership cohort. Strong separation can reflect incident-specific age, balance or usage profiles; it does not prove compromise, hardware identity, causation or transfer to another incident. There are zero independently verified compromise/device labels. The one owner report remains separate evidence. Coverage excludes 12.2% of selected comparisons, disproportionately large histories. The frozen external nineteen-feature forest and all older results are unchanged. No network collection or automation was started.', '',
              'The next aligned unit is a bounded review of the saved rules, membership errors and evidence limitations for the research report. Do not tune on these validation/test outcomes or present them as a new independent test; a new independent evaluation needs its own evidence and protocol.', '',
              '## Reproduction', '',
              'Python/scikit-learn/NumPy/SciPy/Matplotlib versions and SHA256 inputs are pinned. The model is inert JSON; verification performs no fitting and replays every score with float32 input conversion, training-only preprocessing, class weights, node counts, ranking metrics and output fingerprints.', '',
              'From `Task 2/research/coldcard`:', '', '```sh',
              f'python train_source_membership.py verify {protocol_path.parent.name}/protocol.json',
              'python -m unittest test_source_membership test_source_comparison_feasibility test_prepayment_pilot',
              '```', '',
              'Method references: [scikit-learn 1.8 tree](https://scikit-learn.org/1.8/modules/generated/sklearn.tree.DecisionTreeClassifier.html), [training-only preparation](https://scikit-learn.org/1.8/common_pitfalls.html), [average precision](https://scikit-learn.org/1.8/modules/generated/sklearn.metrics.average_precision_score.html). Reviewed 2 November 2026. Parameter choices and cutoff/group rules come from the already frozen project protocol.', '']
    return '\n'.join(lines).encode()


def generated(protocol_path, model, selected, split, prior_summary):
    s, predictions, errors, rules = analyze_export(model, selected, split, prior_summary)
    files = {'model.json': audit.json_bytes(model), 'summary.json': audit.json_bytes(s),
             'predictions.json.gz': compressed(predictions), 'errors.json.gz': compressed(errors),
             'rules.json': audit.json_bytes(rules), 'tree.svg': tree_figure(model, s),
             'README.md': report(protocol_path, model, s, rules)}
    return files, s


def execute(protocol_path, mode):
    protocol, paths, split, selected, prior_summary = inputs(protocol_path)
    output = protocol_path.parent
    if mode == 'run':
        audit.require(not any((output/name).exists() for name in protocol['generated_outputs']),
                      'Refusing to overwrite a fitted experiment')
        state = fit_preprocessing(selected['train'])
        x_train, _ = transform(selected['train'], state)
        y_train = np.asarray([r[TARGET] for r in selected['train']])
        with threadpool_limits(limits=1):
            fitted = DecisionTreeClassifier(**protocol['estimator_parameters'])
            fitted.fit(x_train, y_train)
        model = export_tree(fitted, state, protocol)
        for part in PARTS:
            x, _ = transform(selected[part], state)
            replay, leaves, _ = score_export(model, x)
            audit.require(np.array_equal(replay, fitted.predict_proba(x)[:, 1]) and
                          np.array_equal(leaves, fitted.apply(x)), 'JSON replay differs from fitted estimator')
    else:
        model = audit.load_json(output/'model.json')
        audit.require(model['parameters'] == protocol['estimator_parameters'] and model['runtime'] == protocol['runtime'],
                      'Model parameters/runtime changed')
    files, summary = generated(protocol_path, model, selected, split, prior_summary)
    verification = dict(schema_version=1, protocol_sha256=audit.digest(protocol_path.read_bytes()),
                        frozen_split_sha256=audit.digest(paths['frozen_split'].read_bytes()),
                        outputs={name: audit.digest(data) for name, data in files.items()},
                        training_fit_calls=1, native_estimator_and_json_predictions_agree=True,
                        train_only_preprocessing_and_class_weights_verified=True,
                        training_node_support_verified=True, independent_ranking_metrics_agree=True,
                        replayed_eligible_sources=summary['available_vectors'], excluded_sources=split['excluded_sources'],
                        group_rule_unchanged=True, new_collection_performed=False,
                        verification_mode_requires_refit=False)
    files['verification.json'] = audit.json_bytes(verification)
    for name, data in files.items():
        if mode == 'run':
            (output/name).write_bytes(data)
        else:
            audit.require((output/name).read_bytes() == data, 'Saved artifact differs: ' + name)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['run', 'verify'])
    parser.add_argument('protocol', type=Path)
    args = parser.parse_args()
    s = execute(args.protocol.resolve(), args.mode)
    print(json.dumps(dict(mode=args.mode, tree_metrics={p: s['partition_metrics'][p]['tree'] for p in PARTS},
                          leaves=s['leaves'], used_features=s['split_feature_names'])))


if __name__ == '__main__':
    main()
