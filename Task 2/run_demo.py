"""Offline replay of saved research artifacts; never fit or evaluate a test set.

The standard library suffices. Installed research dependencies additionally allow
the existing 19-feature extractor to be replayed on the saved external histories.
Run ``python 'Task 2/run_demo.py' --help`` from the repository root.
"""
import argparse
from collections import Counter
import csv
import gzip
import hashlib
import importlib
import json
import math
from pathlib import Path
import struct
import sys


ROOT = Path(__file__).resolve().parent
MODEL_PATH = 'coldcard/grouped_results_20261008/research_proxy_model.json'
SCORE_PATHS = ('real_cats/expanded_external_scores_20261014.json',
               'real_cats/fsf_external_score_20261014.json')
EARLY_SCORE_PATH = 'real_cats/external_scores_20261014.json'
PINNED = {
    MODEL_PATH: 'd56c28539e65bb34a8b607b6a18dc372bfa812c9d0045f5f532dd7df7a292926',
    SCORE_PATHS[0]: 'a9830ee4b6bd9b13ad4de4eecca6ea7df72c1cccc7fcb2a93644029560b9c052',
    SCORE_PATHS[1]: '1dcf892f4be4133e4ff5317628b48d9f3b51cb6cecf5eff340a13ddaa0a6df7d',
    EARLY_SCORE_PATH: '1a91c33171d17577d51f31a5cefb7f0e01a77f8208788f4008e9218c05727855',
}
SOURCE_HASHES = {
    'BB.tsv': '3bfe26f493e5767737c9ecf4c654009067c162dc7fa6fec68b0ab8234d4431e9',
    'CB.tsv': 'faf3978f5c9ce3b1257af72ac01975d657ab7529f66faf1a66f1f22f99fbb1ec',
}
TREE_FEATURES = [
    'input_count', 'output_count', 'distinct_input_addresses', 'distinct_output_addresses',
    'input_address_missing_count', 'output_address_missing_count', 'input_total_sat',
    'output_total_sat', 'fee_sat', 'vsize_vb', 'fee_rate_sat_vb', 'version', 'lock_time',
    'min_output_sat', 'max_output_sat', 'zero_value_outputs',
]
EXTERNAL_FEATURES = [
    'balance', 'total_received_BTC', 'total_sent_BTC', 'transaction_fee',
    'transaction_number', 'payment_transactions', 'receipt_transactions', 'lifetime',
    'total_output_slots', 'total_input_slots', 'activity_w', 'activity_d', 'activity_time',
    'max_sent_amount', 'min_sent_amount', 'max_received_amount', 'min_received_amount',
    'sent_counters', 'received_counters',
]
FIXED_MODEL = dict(n_estimators=100, max_depth=20, min_samples_leaf=20,
                   max_features='sqrt', class_weight=1, random_state=42, threshold=0.15)
HISTORY_DIRS = ('theft_cases/eff_history_20261014', 'theft_cases/pilot_histories_20261013',
                'coldcard/theft_history_20261010', 'theft_cases/binance_seed_20261013')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def verify_hash(path, expected):
    with path.open('rb') as stream:
        actual = hashlib.file_digest(stream, 'sha256').hexdigest()
    require(actual == expected, f'SHA256 mismatch: {path.name}; expected {expected}, got {actual}')
    return actual


def read_json(path):
    opener = gzip.open if path.suffix == '.gz' else open
    with opener(path, 'rt', encoding='utf-8') as stream:
        return json.load(stream)


def validate_tree(model):
    require(model['features'] == TREE_FEATURES, 'Unsupported Coldcard feature schema')
    fields = ('children_left', 'children_right', 'feature', 'threshold', 'candidate_score')
    size = len(model['feature'])
    require(size > 0 and all(len(model[k]) == size for k in fields), 'Inconsistent tree arrays')
    visited = set()
    pending = [(0, 0)]
    leaves = depth = 0
    while pending:
        node, level = pending.pop()
        require(type(node) is int and 0 <= node < size, 'Invalid tree child index')
        require(node not in visited, 'Cycle or shared child in tree')
        visited.add(node)
        depth = max(depth, level)
        score = model['candidate_score'][node]
        require(type(score) in (int, float) and math.isfinite(score) and 0 <= score <= 1,
                'Invalid tree score')
        left, right = model['children_left'][node], model['children_right'][node]
        if left == right == -1:
            leaves += 1
        else:
            feature = model['feature'][node]
            require(type(feature) is int and 0 <= feature < len(TREE_FEATURES), 'Invalid feature index')
            require(math.isfinite(model['threshold'][node]), 'Invalid tree threshold')
            pending.extend([(left, level + 1), (right, level + 1)])
    require(len(visited) == size, 'Unreachable tree nodes')
    return dict(nodes=size, leaves=leaves, depth=depth)


def tree_score(row, model, explain=False):
    # sklearn applies float32 conversion before comparing with float64 thresholds.
    values = [struct.unpack('f', struct.pack('f', float(row[c])))[0] for c in TREE_FEATURES]
    require(all(math.isfinite(v) for v in values), 'Missing/nonfinite Coldcard features')
    node, path = 0, []
    for _ in range(len(model['feature']) + 1):
        if model['children_left'][node] == -1:
            return model['candidate_score'][node], node, path
        col = model['feature'][node]
        left = values[col] <= model['threshold'][node]
        if explain:
            path.append(dict(feature=TREE_FEATURES[col], input_float32=values[col],
                             threshold=model['threshold'][node], branch='left' if left else 'right'))
        node = model['children_left' if left else 'children_right'][node]
    raise ValueError('Cyclic model tree')


def replay_coldcard(path, model, manifest):
    digest = verify_hash(path, model['training_sha256'])
    counts, leaf_counts, examples = Counter(), Counter(), []
    example_counts = Counter()
    seen = set()
    coinbase = eligible = above = 0
    with gzip.open(path, 'rt', encoding='utf-8', newline='') as stream:
        reader = csv.DictReader(stream)
        require(set(TREE_FEATURES + ['txid', 'relation', 'is_coinbase']) <= set(reader.fieldnames or []),
                'Coldcard CSV schema mismatch')
        for row in reader:
            txid, relation = row['txid'], row['relation']
            require(txid not in seen, 'Duplicate Coldcard transaction')
            seen.add(txid)
            require(relation in manifest['relation_counts'], 'Unexpected Coldcard relation')
            require(row['is_coinbase'] in ('0', '1'), 'Invalid coinbase flag')
            counts[relation] += 1
            if row['is_coinbase'] == '1':
                coinbase += 1
                continue
            if relation == 'source_attributed':
                continue
            score, leaf, _ = tree_score(row, model)
            eligible += 1
            above += score >= 0.5
            leaf_counts[str(leaf)] += 1
            if example_counts[relation] < 2:
                _, _, path_explanation = tree_score(row, model, explain=True)
                examples.append(dict(txid=txid, relation=relation, research_candidate_score=score,
                                     leaf=leaf, decisions=path_explanation))
                example_counts[relation] += 1
    require(len(seen) == manifest['transaction_count'], 'Coldcard row count mismatch')
    require(dict(counts) == manifest['relation_counts'], 'Coldcard relation counts mismatch')
    require(eligible == model['training_rows'], 'Coldcard training row count mismatch')
    require(counts['direct_parent_candidate'] == model['candidate_rows'], 'Candidate count mismatch')
    return dict(sha256=digest, rows=len(seen), coinbase_rows=coinbase, scored_rows=eligible,
                excluded_source_attributed=counts['source_attributed'], relation_counts=dict(counts),
                candidate_like_rows_at_0_5=above, leaf_counts=dict(sorted(leaf_counts.items())),
                examples=examples,
                interpretation='Replay on the fitted artifact\'s own training data; no performance estimate.')


def validate_saved_scores(documents):
    rows = []
    addresses = set()
    for document in documents:
        require(document['fixed_model'] == FIXED_MODEL, 'Frozen external model configuration changed')
        require(document['base_features'] == EXTERNAL_FEATURES, 'External feature schema changed')
        require(document['transformed_features'] == EXTERNAL_FEATURES +
                ['missingindicator_max_sent_amount', 'missingindicator_min_sent_amount'],
                'Transformed external feature schema changed')
        require(document['source_sha256'] == SOURCE_HASHES, 'External source checksums changed')
        require(document['training_addresses'] == 52736, 'External training population changed')
        for row in document['results']:
            require(row['address'] not in addresses, 'Repeated external address')
            addresses.add(row['address'])
            require(row['source_record']['address'] == row['address'], 'Source-record address mismatch')
            require(set(row['features']) == set(EXTERNAL_FEATURES), 'Saved profile feature schema mismatch')
            require(row['threshold'] == 0.15, 'External threshold changed')
            score = row['source_category_score']
            require(type(score) in (int, float) and math.isfinite(score) and 0 <= score <= 1,
                    'Invalid external score')
            require(type(row['above_fixed_threshold']) is bool and
                    row['above_fixed_threshold'] == (score > 0.15), 'Strict external threshold flag mismatch')
            missing = [c for c in EXTERNAL_FEATURES if row['features'][c] is None]
            require(row['missing_features'] == missing, 'Saved missing-feature flags mismatch')
            require(all(v is None or (type(v) in (int, float) and math.isfinite(v))
                        for v in row['features'].values()), 'Nonfinite saved external feature')
            require(set(row['outside_training_minmax']) <= set(EXTERNAL_FEATURES), 'Unknown out-of-range feature')
            rows.append(row)
    return rows


def find_history(root, row, data_dir, history_dirs=()):
    paths = [root / folder / row['history_file'] for folder in HISTORY_DIRS]
    directories = ([data_dir] if data_dir is not None else []) + list(history_dirs)
    for directory in directories:
        if directory.is_dir():
            paths.extend(sorted(directory.rglob(row['history_file'])))
    existing = [p for p in paths if p.is_file()]
    for path in existing:
        with path.open('rb') as stream:
            if hashlib.file_digest(stream, 'sha256').hexdigest() == row['history_sha256']:
                return path
    require(not existing, 'Found history files, but none has the recorded SHA256: ' + row['history_file'])
    return None


def audit_history(path, row):
    verify_hash(path, row['history_sha256'])
    history = read_json(path)
    require(history['address'] == row['address'], 'History address mismatch')
    require(history['collected_at'] == row['collected_at'], 'History collection time mismatch')
    require(history.get('source_record', history.get('record')) == row['source_record'],
            'History attribution metadata changed')
    require(history['audit']['pagination_exhausted'] is True, 'History pagination unfinished')
    require(history['before']['chain_stats'] == history['after']['chain_stats'], 'Unstable provider counters')
    address = row['address']
    observed = dict(tx_count=0, funded_txo_count=0, spent_txo_count=0, funded_txo_sum=0, spent_txo_sum=0)
    seen, coinbase = set(), 0
    for tx in history['transactions']:
        require(tx['txid'] not in seen, 'Repeated history transaction')
        seen.add(tx['txid'])
        require(tx['status'].get('confirmed') is True, 'Unconfirmed transaction in history')
        inputs = [v['prevout']['value'] for v in tx['vin']
                  if (v.get('prevout') or {}).get('scriptpubkey_address') == address]
        outputs = [v['value'] for v in tx['vout'] if v.get('scriptpubkey_address') == address]
        require(bool(inputs or outputs), 'Transaction unrelated to history address')
        observed['tx_count'] += 1
        observed['funded_txo_count'] += len(outputs)
        observed['spent_txo_count'] += len(inputs)
        observed['funded_txo_sum'] += sum(outputs)
        observed['spent_txo_sum'] += sum(inputs)
        coinbase += any(v.get('is_coinbase', False) for v in tx['vin'])
    require(observed == history['after']['chain_stats'], 'Provider-counter reconciliation failed')
    comparisons = dict(transaction_number=observed['tx_count'], total_output_slots=observed['funded_txo_count'],
                       total_input_slots=observed['spent_txo_count'], total_received_BTC=observed['funded_txo_sum'],
                       total_sent_BTC=observed['spent_txo_sum'],
                       balance=observed['funded_txo_sum'] - observed['spent_txo_sum'])
    require(all(row['features'][k] == v for k, v in comparisons.items()), 'Saved profile counter mismatch')
    return dict(sha256=row['history_sha256'], transactions=len(seen), coinbase_transactions=coinbase,
                provider_counter_reconciliation=observed,
                interpretation='Agreement with saved provider counters, not cryptographic inclusion verification.')


def replay_external_features(path, row):
    # Reuse the research extractor; no forest is fitted or scored here.
    folder = str(ROOT / 'real_cats')
    if folder not in sys.path:
        sys.path.insert(0, folder)
    module = importlib.import_module('score_external_histories')
    _, actual, _ = module.extract(path)
    require(set(actual) == set(row['features']), 'Recomputed feature schema differs')
    for name, expected in row['features'].items():
        value = actual[name]
        match = value is None if expected is None else (
            value is not None and math.isclose(value, expected, rel_tol=1e-12, abs_tol=1e-6))
        require(match, 'Recomputed feature differs: ' + name)
    return dict(features_recomputed=len(actual), tolerance='rtol=1e-12, atol=1e-6',
                interpretation='Replays the same extractor; does not independently certify its conventions.')


def audit_source(source, rows):
    hashes, overlaps = {}, {}
    external = {r['address'] for r in rows}
    for name, expected in SOURCE_HASHES.items():
        path = source / name
        hashes[name] = verify_hash(path, expected)
        with path.open(encoding='utf-8', newline='') as stream:
            overlap = {r['address'] for r in csv.DictReader(stream, delimiter='\t')} & external
        overlaps[name] = sorted(overlap)
        require(not overlap, 'External exact-address overlap with ' + name)
    return dict(sha256=hashes, exact_address_overlaps=overlaps,
                interpretation='Exact-address check only; entity and incident independence remain unverified.')


def run(root=ROOT, data_dir=None, source=None, history_dirs=()):
    checks = []

    def check(name, action):
        try:
            details = action()
        except FileNotFoundError as error:
            checks.append(dict(check=name, status='missing', reason=str(error)))
        except ModuleNotFoundError as error:
            checks.append(dict(check=name, status='unchecked', reason='Optional dependency absent: ' + str(error)))
        except (ValueError, KeyError, TypeError, IndexError, OSError, OverflowError) as error:
            checks.append(dict(check=name, status='failed', reason=str(error)))
        else:
            checks.append(dict(check=name, status='verified', details=details))
            return details
        return None

    def pinned_json(relative):
        verify_hash(root / relative, PINNED[relative])
        return read_json(root / relative)

    model = check('coldcard_saved_model', lambda: dict(model=pinned_json(MODEL_PATH)))
    if model is not None:
        model = model['model']
        check('coldcard_tree_structure', lambda: validate_tree(model))
        if data_dir is None:
            checks.append(dict(check='coldcard_data_replay', status='missing',
                               reason='Supply --data-dir containing transactions.csv.gz.'))
        elif checks[-1]['status'] == 'verified':
            check('coldcard_data_replay', lambda: replay_coldcard(data_dir / 'transactions.csv.gz', model,
                  read_json(root / 'coldcard/inputs_20261008/manifest.json')))

    def saved_external():
        documents = [pinned_json(p) for p in SCORE_PATHS]
        rows = validate_saved_scores(documents)
        require(len(rows) == 11, 'Expected eleven saved external profiles, including FSF')
        by_address = {r['address']: r for r in rows}
        early = pinned_json(EARLY_SCORE_PATH)
        validate_saved_scores([early])
        require(all(by_address[r['address']] == r for r in early['results']),
                'Earlier three-profile report differs from expanded report')
        return dict(rows=rows, fixed_model=FIXED_MODEL, strict_threshold='score > 0.15',
                    interpretation='Saved scores/configuration are consistent; forest inference is not rerun.')

    external = check('external_saved_reports', saved_external)
    if external is not None:
        for row in external['rows']:
            address = row['address']
            located = check('history_location:' + address,
                            lambda row=row: dict(path=str(find_history(root, row, data_dir, history_dirs) or '')))
            if located is None:
                continue
            if not located['path']:
                checks[-1].update(status='missing', reason='Raw history absent: ' + row['history_file'])
                checks[-1].pop('details', None)
                continue
            path = Path(located['path'])
            history = check('history_integrity:' + address, lambda path=path, row=row: audit_history(path, row))
            if history is not None:
                check('history_features:' + address, lambda path=path, row=row: replay_external_features(path, row))
        if source is not None:
            check('real_cats_exact_address_overlap', lambda: audit_source(source, external['rows']))
        else:
            checks.append(dict(check='real_cats_exact_address_overlap', status='unchecked',
                               reason='Supply --real-cats-source with the pinned BB.tsv and CB.tsv.'))
    checks.extend([
        dict(check='external_forest_inference', status='unchecked',
             reason='No fitted forest was committed. Demo never retrains or evaluates reserved sets.'),
        dict(check='attribution_and_generalization', status='unchecked',
             reason='No independent ground-truth, entity independence or prospective performance is certified.'),
    ])
    counts = dict(Counter(c['status'] for c in checks))
    return dict(schema_version=1, execution_status='failed' if counts.get('failed') else 'completed',
                status_counts=counts, checks=checks,
                meaning='Verified applies only to the named check. Missing and unchecked checks remain open; '
                        'saved scores are not calibrated probabilities of theft or hardware control.')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir', type=Path, help='Directory with transactions.csv.gz and optional raw histories')
    parser.add_argument('--history-dir', type=Path, action='append', default=[],
                        help='Additional local history directory; repeat for multiple directories')
    parser.add_argument('--real-cats-source', type=Path, help='Optional local directory containing pinned BB.tsv/CB.tsv')
    parser.add_argument('--output', type=Path, help='New JSON report; existing files are never overwritten')
    args = parser.parse_args(argv)
    if args.output is not None and args.output.exists():
        parser.error('Output already exists; choose a new report path.')
    report = run(data_dir=args.data_dir, source=args.real_cats_source, history_dirs=args.history_dir)
    for check in report['checks']:
        suffix = ': ' + check['reason'] if 'reason' in check else ''
        print(f"[{check['status']}] {check['check']}{suffix}")
        if check['check'] == 'external_saved_reports' and check['status'] == 'verified':
            for row in check['details']['rows']:
                print(f"  {row['address']}  saved_score={row['source_category_score']:.6f}  "
                      f"above_0.15={row['above_fixed_threshold']}")
    print(json.dumps(report['status_counts'], sort_keys=True))
    if args.output is not None:
        with args.output.open('x', encoding='utf-8') as stream:
            json.dump(report, stream, indent=2, allow_nan=False)
            stream.write('\n')
        print('Report:', args.output)
    return 1 if report['execution_status'] == 'failed' else 0


if __name__ == '__main__':
    raise SystemExit(main())
