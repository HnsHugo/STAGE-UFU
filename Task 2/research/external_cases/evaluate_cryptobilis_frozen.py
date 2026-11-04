"""Apply the existing inert Coldcard JSON tree to the fixed eligible external set.

Standard-library inference only: no estimator, fit, provider, resampling,
threshold search or mutation of earlier outputs is available in this runner.
"""
import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import gzip
import hashlib
import json
import math
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[1]
TARGET = 'cryptobilis_reference_source_membership'
ELIGIBLE = 'eligible_for_frozen_proxy_evaluation'
MODEL_SHA = '87101573c2de885adfdb9cfb194cf12366b4dc94b4bb9e51e0435bf5e570f537'
RULES = dict(target=TARGET, eligible_cases=122, eligible_comparisons=153,
    selected_sources=366, quarantined_complete=54, bounded_incomplete=37,
    eligibility='Exactly the previously published eligibility manifest; no replacement',
    preprocessing='Frozen Coldcard training medians and fourteen fixed missing indicators',
    input_conversion='float64 filling; float32 before JSON tree traversal; <= left branch',
    threshold=.5, threshold_operator='>=',
    comparators=['constant_train_prevalence', 'inactivity_rank', 'balance_rank'],
    comparator_policy='Same Coldcard-training median fills; float64 rankings only, no classification threshold',
    metrics=['average_precision_membership', 'roc_auc_membership', 'precision_membership',
             'recall_membership', 'f1_membership', 'membership_confusion'],
    reporting='Overall primary and descriptive by reference block, each error, missingness and fixed leaf support',
    model_fits=0, preprocessing_fits=0, threshold_searches=0, provider_requests=0,
    evaluation_scope='One previously inspected external structural-proxy incident, complete-case and measured-link quarantine')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == '.gz' else data)


def read_pin(pin):
    path = (ROOT / pin['file']).resolve()
    require(path.is_relative_to(ROOT), 'Input outside research root')
    require(sha(path.read_bytes()) == pin['sha256'], 'Input fingerprint mismatch: ' + pin['file'])
    return path


def index(rows):
    result = {r['source_id']: r for r in rows}
    require(len(result) == len(rows), 'Repeated source ID')
    return result


def transform(features, state):
    names = state['predictor_allowlist']
    require(len(names) == 14 and len(set(names)) == 14 and set(features) == set(names), 'Fourteen-feature allowlist mismatch')
    require(state['model_input_names'] == names + ['missing__' + n for n in names], 'Fixed missing indicators changed')
    require(len(state['medians']) == 14 and state['fit_partition'] == 'train' and state['fit_rows'] == 1033,
            'Not the frozen training preprocessor')
    filled, missing = [], []
    for name, median in zip(names, state['medians']):
        value = features[name]
        require(value is None or type(value) in (int, float), 'Invalid feature type')
        missing.append(value is None)
        value = float(median if value is None else value)
        require(math.isfinite(value), 'Nonfinite filled feature')
        filled.append(value)
    converted = []
    for value in filled + [float(m) for m in missing]:
        try:
            number = struct.unpack('!f', struct.pack('!f', value))[0]
        except OverflowError as error:
            raise ValueError('Float32 overflow') from error
        require(math.isfinite(number), 'Nonfinite float32 input')
        converted.append(number)
    return filled, converted, [n for n, m in zip(names, missing) if m]


def traverse(model, converted):
    require(len(converted) == len(model['model_input_names']) == 28, 'Invalid model input width')
    tree = model['tree'];node = 0;path = []
    while True:
        require(0 <= node < tree['node_count'] and node not in path, 'Invalid or cyclic JSON tree')
        path.append(node)
        left, right = tree['children_left'][node], tree['children_right'][node]
        if left == -1:
            require(right == -1, 'Asymmetric JSON tree leaf')
            score = tree['case_membership_score'][node]
            require(type(score) in (int, float) and math.isfinite(score) and 0 <= score <= 1,
                    'Invalid exported leaf score')
            return float(score), node, path
        feature = tree['feature_indices'][node]
        require(0 <= feature < 28 and math.isfinite(tree['thresholds'][node]), 'Invalid JSON split')
        node = left if converted[feature] <= tree['thresholds'][node] else right


def metrics(labels, scores, classify=False):
    require(len(labels) == len(scores) > 0 and set(labels) == {0, 1}, 'Metrics need both membership classes')
    require(all(type(x) in (int, float) and math.isfinite(x) for x in scores), 'Invalid metric score')
    groups = defaultdict(lambda: [0, 0])
    for label, score in zip(labels, scores):
        require(type(label) is int, 'Invalid metric label')
        groups[float(score)][label] += 1
    positives, negatives = sum(labels), len(labels) - sum(labels)
    seen = tp = 0;ap = Fraction(0)
    for score in sorted(groups, reverse=True):
        neg, pos = groups[score];seen += neg + pos;tp += pos
        ap += Fraction(pos, positives) * Fraction(tp, seen)
    pos_scores = [score for label, score in zip(labels, scores) if label]
    neg_scores = [score for label, score in zip(labels, scores) if not label]
    doubled_wins = sum(2 * (a > b) + (a == b) for a in pos_scores for b in neg_scores)
    result = dict(rows=len(labels), case=positives, comparison=negatives,
        sampled_membership_prevalence=positives/len(labels),
        average_precision_membership=float(ap), roc_auc_membership=doubled_wins/(2*positives*negatives))
    if classify:
        predictions = [score >= .5 for score in scores]
        tp = sum(pred and label == 1 for pred, label in zip(predictions, labels))
        fp = sum(pred and label == 0 for pred, label in zip(predictions, labels))
        fn, tn = positives-tp, negatives-fp
        result.update(threshold=.5, threshold_operator='>=', true_positive_membership=tp,
            false_positive_membership=fp, false_negative_membership=fn, true_negative_membership=tn,
            precision_membership=tp/(tp+fp) if tp+fp else 0., recall_membership=tp/positives,
            f1_membership=2*tp/(2*tp+fp+fn))
    return result


def eligibility(view, manifest, resume):
    rows, chosen = index(view['rows']), index(manifest['rows'])
    require(set(rows) == set(chosen) and len(rows) == 366, 'Fixed external source universe changed')
    require(view['schema_version'] == 2 and view['operational_target'] == TARGET, 'External view target/schema changed')
    groups = {status: [] for status in (ELIGIBLE, 'quarantined_cross_development_component', 'excluded_bounded_incomplete')}
    for key, row in rows.items():
        member = chosen[key]
        require(member['status'] in groups, 'Unrecognized eligibility status')
        require(row[TARGET] == member['membership'] and type(row[TARGET]) is int and row[TARGET] in (0, 1),
                'External membership target changed')
        require(row['cutoff_height'] == member['cutoff_height'] and row['full_history_status'] == member['full_history_status'],
                'Source cutoff or full-history status changed')
        require(all(value is None for value in row['labels'].values()), 'Unknown source labels changed')
        require(row['full_history_status'] == 'not_collected_for_this_source', 'Full-history status promoted')
        require(row['incident_group'] == 'cryptobilis_2026', 'External incident grouping changed')
        available = member['status'] != 'excluded_bounded_incomplete'
        require((row['features'] is not None) == available, 'Vector/eligibility availability mismatch')
        require(row['precutoff_history_status'] == ('complete_prior_prefix' if available else 'bounded_incomplete'),
                'Unfinished prefix selected for inference')
        require(member['status'] != ELIGIBLE or not member['cross_development_component'], 'Quarantined component selected for inference')
        groups[member['status']].append(key)
    require([len(groups[k]) for k in groups] == [275, 54, 37], 'Fixed eligible or excluded source counts changed')
    require(set(groups[ELIGIBLE]) == set(resume['eligible_source_ids']) and
            set(groups['quarantined_cross_development_component']) == set(resume['quarantined_complete_source_ids']) and
            set(groups['excluded_bounded_incomplete']) == set(resume['bounded_incomplete_source_ids']),
            'Published eligibility checkpoint IDs changed')
    require(sum(rows[key][TARGET] for key in groups[ELIGIBLE]) == 122, 'Eligible class support changed')
    return rows, chosen, sorted(groups[ELIGIBLE])


def build(protocol_path):
    protocol = read(protocol_path)
    require(protocol['rules'] == RULES, 'Frozen inference rules changed')
    paths = {name: read_pin(pin) for name, pin in protocol['inputs'].items()}
    require(paths['runner'] == Path(__file__).resolve(), 'Wrong inference runner')
    model = read(paths['frozen_model']);transfer = read(paths['transfer_protocol'])
    require(sha(paths['frozen_model'].read_bytes()) == transfer['frozen_model']['sha256'] == MODEL_SHA, 'Frozen model changed')
    require(model['target'] == 'known_coldcard_core_membership' and model['threshold'] == .5 and
            model['threshold_operator'] == '>=' and model['training_fit_calls'] == 1, 'Frozen model target/threshold/provenance changed')
    state = model['preprocessing'];names = state['predictor_allowlist']
    require(names == transfer['predictor_allowlist'] and model['model_input_names'] == state['model_input_names'],
            'Predictor order changed')
    view = read(paths['external_view']);manifest = read(paths['eligibility_manifest']);resume = read(paths['eligibility_resume'])
    rows, chosen, selected = eligibility(view, manifest, resume)
    require(view['predictor_allowlist'] == names, 'External predictor order changed')
    overlap = read(paths['overlap_summary'])
    require(overlap['can_score_primary_structural_proxy'] and overlap['minimum_20_per_class_passed'] and
            overlap['eligible_external'] == 275 and overlap['independent_components_agree'], 'Prescoring gates failed')
    independent = read(paths['overlap_independent_verification'])
    require(independent['eligible'] == dict(case=122, comparison=153) and independent['all_component_memberships_exact'],
            'Independent eligibility verification missing')
    split = read(paths['frozen_split']);development = read(paths['coldcard_view']);dev = index(development['rows'])
    require(len(split['rows']) == len(dev) == 1500, 'Frozen development selection changed')
    train_ids = [row['source_id'] for row in split['rows'] if row['partition'] == 'train']
    train_cases = sum(dev[key]['known_coldcard_core_membership'] for key in train_ids)
    require(len(train_ids) == 1033 and train_cases == 346, 'Frozen training prevalence changed')
    require(sha(encoded(train_ids)) == state['fit_source_ids_sha256'], 'Preprocessor training-source identity changed')
    prevalence = train_cases / len(train_ids)
    predictions, errors = [], []
    for key in selected:
        row = rows[key];filled, converted, missing = transform(row['features'], state)
        score, leaf, path = traverse(model, converted);label = row[TARGET];pred = int(score >= .5)
        record = dict(source_id=key, address_sha256=row['address_sha256'], component_id=chosen[key]['component_id'],
            cutoff_height=row['cutoff_height'], full_history_status=row['full_history_status'],
            cryptobilis_reference_source_membership=label, predicted_cryptobilis_reference_source_membership=pred,
            frozen_coldcard_membership_score=score, leaf_id=leaf, path_node_ids=path, missing_features=missing,
            float32_input_sha256=sha(encoded(converted)), constant_train_prevalence=prevalence,
            inactivity_rank=filled[names.index('blocks_since_last_activity')], balance_rank=filled[names.index('balance_sat')])
        predictions.append(record)
        if pred != label:
            errors.append(dict(record, error_type='false_negative_membership' if label else 'false_positive_membership',
                features=row['features'], labels=row['labels'], reference_txid_sha256=row['reference_txid_sha256']))
    metrics_by_block = {}
    methods = dict(frozen_tree='frozen_coldcard_membership_score', constant_train_prevalence='constant_train_prevalence',
                   inactivity_rank='inactivity_rank', balance_rank='balance_rank')
    def evaluate(records):
        y = [r[TARGET] for r in records]
        return {name: metrics(y, [r[field] for r in records], name == 'frozen_tree') for name, field in methods.items()}
    overall = evaluate(predictions)
    for height in sorted({r['cutoff_height'] for r in predictions}):
        metrics_by_block[str(height)] = evaluate([r for r in predictions if r['cutoff_height'] == height])
    node_support = {str(node): dict(case=0, comparison=0, false_positive_membership=0, false_negative_membership=0)
                    for node in range(model['tree']['node_count'])}
    for record in predictions:
        for node in record['path_node_ids']:
            support = node_support[str(node)];label = record[TARGET]
            support['case' if label else 'comparison'] += 1
            if record['predicted_cryptobilis_reference_source_membership'] != label:
                support['false_negative_membership' if label else 'false_positive_membership'] += 1
    scoring_rows = []
    by_id = index(predictions)
    for key, member in sorted(chosen.items()):
        scoring_rows.append(dict(member, score_available=key in by_id,
            frozen_coldcard_membership_score=by_id[key]['frozen_coldcard_membership_score'] if key in by_id else None))
    summary = dict(schema_version=1, input_commit=protocol['input_commit'], target=TARGET,
        model_origin_target=model['target'], evaluation_scope=RULES['evaluation_scope'],
        selected_sources=366, complete_external_vectors=329, scored_sources=len(predictions),
        scored_cases=122, scored_comparisons=153, quarantined_complete=54, bounded_incomplete=37,
        primary_metrics=overall, descriptive_metrics_by_block=metrics_by_block,
        threshold=.5, threshold_operator='>=', training_prevalence=prevalence,
        training_prevalence_support=dict(case=train_cases, comparison=len(train_ids)-train_cases),
        error_counts=dict(Counter(e['error_type'] for e in errors)), error_rows=len(errors),
        fixed_node_support=node_support,
        missing_values_by_class={name: {feature: sum(feature in r['missing_features'] for r in predictions if r[TARGET] == label)
            for feature in names} for label, name in [(1, 'case'), (0, 'comparison')]},
        original_selected_case_fraction=122/366, available_vector_case_fraction=122/329, scored_case_fraction=122/275,
        frozen_model_sha256=MODEL_SHA, frozen_split_sha256=sha(paths['frozen_split'].read_bytes()),
        input_files_verified=len(paths), new_model_fits=0, preprocessing_fits=0, provider_requests=0,
        new_partitions=0, parameter_or_threshold_searches=0, scored_quarantined_or_bounded_sources=0,
        full_current_history_status_not_promoted=True, source_level_verified_compromise_or_device_evaluation_possible=False,
        entity_independence_established=False, external_incidents=1, untouched_test_claim=False,
        score_interpretation=model['score_interpretation'],
        limitation='Descriptive transport of a source-linkage proxy in one previously inspected incident; complete-case and quarantine attrition, unknown missing-prefix/entity links and unknown theft/device labels remain.')
    files = {'summary.json': encoded(summary), 'predictions.json.gz': gzip.compress(encoded(predictions), mtime=0),
        'errors.json.gz': gzip.compress(encoded(errors), mtime=0),
        'scoring_manifest.json.gz': gzip.compress(encoded(dict(schema_version=1, rows=scoring_rows)), mtime=0)}
    files['verification.json'] = encoded(dict(schema_version=1, protocol_sha256=sha(protocol_path.read_bytes()),
        input_files_verified=len(paths), outputs={name: sha(data) for name, data in files.items()},
        evaluated_sources=275, scored_excluded_sources=0, frozen_model_sha256=MODEL_SHA,
        new_model_fits=0, preprocessing_fits=0, provider_requests=0))
    return files, summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['build', 'verify']);parser.add_argument('protocol', type=Path)
    args = parser.parse_args();protocol = args.protocol.resolve();files, summary = build(protocol)
    if args.mode == 'build':
        require(not any((protocol.parent/name).exists() for name in files), 'Refusing to overwrite an inference output')
        for name, data in files.items():
            (protocol.parent/name).write_bytes(data)
    else:
        for name, data in files.items():
            require((protocol.parent/name).read_bytes() == data, 'Frozen reconstruction differs: ' + name)
    print(json.dumps({key: summary[key] for key in ('scored_sources', 'primary_metrics', 'error_counts',
        'input_files_verified', 'new_model_fits', 'preprocessing_fits', 'provider_requests')}))


if __name__ == '__main__':
    main()
