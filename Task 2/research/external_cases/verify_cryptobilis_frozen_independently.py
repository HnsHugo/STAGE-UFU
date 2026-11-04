"""Check every external score with the preserved NumPy/Coldcard implementation.

Estimator fitting and preprocessing fitting are explicitly blocked. Metrics use
the existing NumPy/scikit-learn path, independently of the stdlib evaluator.
"""
import argparse
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'coldcard'))
import train_source_membership as reference
import numpy as np


def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == '.gz' else data)


def forbid_fit(*args, **kwargs):
    raise AssertionError('No fit is permitted in frozen external verification')


def check(protocol_path):
    config = read(protocol_path);paths = {}
    for key, pin in config['inputs'].items():
        path = (ROOT/pin['file']).resolve()
        if not path.is_relative_to(ROOT) or sha(path.read_bytes()) != pin['sha256']:
            raise ValueError('Independent input fingerprint mismatch: ' + key)
        paths[key] = path
    model = read(paths['frozen_model']);view = read(paths['external_view'])
    by_id = {r['source_id']: r for r in view['rows']}
    eligible = {r['source_id']: r for r in read(paths['eligibility_manifest'])['rows']
                if r['status'] == 'eligible_for_frozen_proxy_evaluation'}
    keys = sorted(eligible);rows = [by_id[key] for key in keys]
    out = protocol_path.parent;predictions = read(out/'predictions.json.gz')
    if [r['source_id'] for r in predictions] != keys or len(keys) != 275:
        raise ValueError('Independent scoring population differs')
    # These original helpers never call the blocked training paths.
    with patch.object(reference.DecisionTreeClassifier, 'fit', forbid_fit), patch.object(reference, 'fit_preprocessing', forbid_fit):
        values, missing = reference.transform(rows, model['preprocessing'])
        scores, leaves, paths_taken = reference.score_export(model, values)
        baseline = read(paths['coldcard_baseline_summary'])['partition_counts']['train']
        prevalence = baseline['case'] / (baseline['case'] + baseline['comparison'])
        comparators = dict(constant_train_prevalence=np.full(len(rows), prevalence),
            inactivity_rank=values[:, reference.FEATURES.index('blocks_since_last_activity')],
            balance_rank=values[:, reference.FEATURES.index('balance_sat')])
        for i, row in enumerate(predictions):
            if row['frozen_coldcard_membership_score'] != float(scores[i]) or row['leaf_id'] != int(leaves[i]) or row['path_node_ids'] != paths_taken[i]:
                raise ValueError('Independent tree traversal differs: ' + row['source_id'])
            if row['predicted_cryptobilis_reference_source_membership'] != int(scores[i] >= .5):
                raise ValueError('Independent fixed-threshold decision differs')
            converted = np.asarray(values[i], dtype=np.float32).astype(float).tolist()
            expected_missing = [name for j, name in enumerate(reference.FEATURES) if missing[i, j]]
            if row['float32_input_sha256'] != sha(encoded(converted)) or row['missing_features'] != expected_missing:
                raise ValueError('Independent preprocessing differs')
            if any(row[name] != float(comp[i]) for name, comp in comparators.items()):
                raise ValueError('Independent fixed comparator differs')
        summary = read(out/'summary.json');methods = dict(frozen_tree=scores, **comparators)
        for height in [None] + sorted({row['cutoff_height'] for row in rows}):
            positions = [i for i, row in enumerate(rows) if height is None or row['cutoff_height'] == height]
            labels = np.asarray([rows[i]['cryptobilis_reference_source_membership'] for i in positions])
            recorded = summary['primary_metrics'] if height is None else summary['descriptive_metrics_by_block'][str(height)]
            for method, method_scores in methods.items():
                expected = reference.metrics(labels, method_scores[positions], method == 'frozen_tree')
                if set(recorded[method]) != set(expected) or any(abs(recorded[method][key]-value) > 1e-12
                        if isinstance(value, (int, float)) else recorded[method][key] != value for key, value in expected.items()):
                    raise ValueError('Independent sklearn metrics differ: ' + method)
    manifest = read(out/'scoring_manifest.json.gz')['rows']
    if len(manifest) != 366 or len({r['source_id'] for r in manifest}) != 366:
        raise ValueError('A selected source was lost from the scoring manifest')
    for row in manifest:
        selected = row['source_id'] in eligible
        if row['score_available'] != selected or (not selected and row['frozen_coldcard_membership_score'] is not None):
            raise ValueError('Excluded source acquired a score')
        if selected and row['frozen_coldcard_membership_score'] != predictions[keys.index(row['source_id'])]['frozen_coldcard_membership_score']:
            raise ValueError('Scoring manifest score differs from the verified prediction')
    expected_errors = {row['source_id'] for i, row in enumerate(rows)
        if int(scores[i] >= .5) != row['cryptobilis_reference_source_membership']}
    errors = read(out/'errors.json.gz')
    if {row['source_id'] for row in errors} != expected_errors or len(errors) != len(expected_errors):
        raise ValueError('Error export is incomplete or duplicated')
    for row in errors:
        original = by_id[row['source_id']]
        if row['features'] != original['features'] or row['labels'] != original['labels']:
            raise ValueError('Error evidence or unknown labels changed')
        expected_type = 'false_negative_membership' if original['cryptobilis_reference_source_membership'] else 'false_positive_membership'
        if row['error_type'] != expected_type:
            raise ValueError('Membership error type changed')
    node_support = {str(i): dict(case=0, comparison=0, false_positive_membership=0, false_negative_membership=0)
                    for i in range(model['tree']['node_count'])}
    for i, row in enumerate(rows):
        label = row['cryptobilis_reference_source_membership'];wrong = int(scores[i] >= .5) != label
        for node in paths_taken[i]:
            c = node_support[str(node)];c['case' if label else 'comparison'] += 1
            if wrong:
                c['false_negative_membership' if label else 'false_positive_membership'] += 1
    if node_support != summary['fixed_node_support']:
        raise ValueError('Independent fixed-tree node support differs')
    return dict(schema_version=1, protocol_sha256=sha(protocol_path.read_bytes()),
        verifier_sha256=sha(Path(__file__).read_bytes()), input_files_verified=len(paths),
        exact_numpy_float32_scores_and_paths=275, exact_training_only_preprocessing_rows=275,
        fixed_comparators_verified=3, overall_and_two_block_metric_sets_verified=12,
        each_error_verified=len(expected_errors), excluded_sources_verified_unscored=91,
        sklearn_metrics_agree=True, fixed_node_support_verified=True, fit_paths_explicitly_blocked=True,
        prediction_export_sha256=sha((out/'predictions.json.gz').read_bytes()),
        frozen_model_sha256=sha(paths['frozen_model'].read_bytes()),
        runtime=reference.runtime(), new_model_fits=0, preprocessing_fits=0, provider_requests=0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['build', 'verify']);parser.add_argument('protocol', type=Path)
    args = parser.parse_args();protocol = args.protocol.resolve();result = encoded(check(protocol))
    destination = protocol.parent/'independent_verification.json'
    if args.mode == 'build':
        if destination.exists():
            raise ValueError('Refusing to overwrite an independent verification')
        destination.write_bytes(result)
    elif destination.read_bytes() != result:
        raise ValueError('Independent inference verification differs')
    print(result.decode())
