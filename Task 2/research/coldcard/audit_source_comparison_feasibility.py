"""Offline coverage and frozen grouped-partition feasibility; never fit a model.

Only aggregate partition counts are exported. The component evidence contains
source IDs and hashes, without train/validation/test assignments or raw IDs.
"""
import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import gzip
import hashlib
import json
import math
from pathlib import Path
import re

from prepayment_pilot import FEATURE_NAMES, features


ROOT = Path(__file__).resolve().parent
TARGET = 'known_coldcard_core_membership'
PARTITION = dict(hash_prefix='coldcard-source-split-v1:42:', modulus=10,
                 train_residues=list(range(7)), validation_residues=[7],
                 test_residues=[8, 9], minimum_per_class_per_partition=20)
IDENTITY = ('address_sha256', 'payment_txid_sha256', 'cutoff_height', 'cutoff_block_hash')
UNKNOWN_LABELS = dict(hardware_signing_at_event=None,
                      independently_verified_compromise=None,
                      independently_verified_seed_origin=None,
                      reported_hardware_association=None, reported_loss=None)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def json_bytes(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()


def load_json(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == '.gz' else data)


def read_pin(root, pin):
    path = (root / pin['file']).resolve()
    require(path.is_relative_to(root.resolve()), 'Input outside audit root')
    require(digest(path.read_bytes()) == pin['sha256'], 'Input fingerprint mismatch: ' + pin['file'])
    return path


def index_rows(rows):
    result = {r['source_id']: r for r in rows}
    require(len(result) == len(rows), 'Duplicate source ID')
    return result


def distribution(values):
    present = sorted(v for v in values if v is not None)
    require(all(type(v) in (int, float) and math.isfinite(v) for v in present),
            'Nonfinite or nonnumeric observation')
    result = dict(nonmissing=len(present), missing=len(values)-len(present),
                  zeros=present.count(0), distinct_nonmissing=len(set(present)))
    for name, p in [('min', 0), ('p25', .25), ('p50', .5), ('p75', .75), ('p95', .95), ('max', 1)]:
        result[name] = present[max(0, math.ceil(p*len(present))-1)] if present else None
    return result


def vector_key(vector):
    """Include missingness; preserve integer precision and numeric equality."""
    require(set(vector) == set(FEATURE_NAMES), 'Fourteen-feature allowlist mismatch')
    result = []
    for name in FEATURE_NAMES:
        value = vector[name]
        if value is None:
            result.append(None)
        else:
            require(type(value) in (int, float) and math.isfinite(value), 'Invalid feature value')
            fraction = Fraction(value)
            result.append([fraction.numerator, fraction.denominator])
    return digest(json_bytes(result))


def link_sets(rows, prefixes):
    links = {key: defaultdict(set) for key in ('address', 'prior_transaction', 'reference_transaction', 'full_vector')}
    for row in rows:
        key = row['source_id']
        links['address'][row['address_sha256']].add(key)
        links['reference_transaction'][row['payment_txid_sha256']].add(key)
        links['full_vector'][vector_key(row['features'])].add(key)
        for tx in prefixes[key]:
            links['prior_transaction'][tx['transaction_id']].add(key)
    return links


def components(rows, links):
    parent = {row['source_id']: row['source_id'] for row in rows}

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for values in links.values():
        for members in values.values():
            first, *others = sorted(members)
            for member in others:
                parent[find(member)] = find(first)
    groups = defaultdict(list)
    for key in sorted(parent):
        groups[find(key)].append(key)
    return sorted(groups.values())


def check_components_independently(rows, links, groups):
    """Breadth-first graph traversal, independent of union-find roots."""
    graph = {r['source_id']: set() for r in rows}
    for values in links.values():
        for members in values.values():
            first, *others = sorted(members)
            graph[first].update(others)
            for member in others:
                graph[member].add(first)
    unseen, expected = set(graph), []
    while unseen:
        start = min(unseen)
        queue, visited = [start], {start}
        while queue:
            key = queue.pop()
            for neighbor in graph[key] - visited:
                visited.add(neighbor)
                queue.append(neighbor)
        expected.append(sorted(visited))
        unseen -= visited
    require(sorted(expected) == sorted(groups), 'Independent component traversal disagrees')


def partition_for(minimum_address_hash):
    value = int(digest((PARTITION['hash_prefix'] + minimum_address_hash).encode()), 16) % 10
    return 'train' if value < 7 else 'validation' if value == 7 else 'test'


def evaluate_partitions(rows, groups, links):
    by_id = index_rows(rows)
    counts = {p: dict(case=0, comparison=0, components=0) for p in ('train', 'validation', 'test')}
    assignment = {}
    for group in groups:
        part = partition_for(min(by_id[key]['address_sha256'] for key in group))
        counts[part]['components'] += 1
        for key in group:
            require(key not in assignment, 'Source occurs in multiple components')
            assignment[key] = part
            counts[part]['case' if by_id[key][TARGET] else 'comparison'] += 1
    require(set(assignment) == set(by_id), 'Component coverage mismatch')
    crossings = {kind: sum(len({assignment[key] for key in members}) > 1
                           for members in values.values()) for kind, values in links.items()}
    failures = [f'{part}.{label}={c[label]} < 20' for part, c in counts.items()
                for label in ('case', 'comparison') if c[label] < 20]
    failures += [kind + ' crosses partitions' for kind, n in crossings.items() if n]
    return dict(counts=counts, cross_partition_link_groups=crossings,
                minimum_per_class_per_partition=20, feasible=not failures, failures=failures)


def check_prefix(row, entry):
    require(entry['status'] in ('complete', 'complete_prior_prefix'), 'Unfinished prefix evidence')
    for field in IDENTITY:
        if field in entry:
            require(row[field] == entry[field], 'Checkpoint identity mismatch: ' + field)
    prefix = entry['prefix']
    require(isinstance(prefix, list), 'Missing normalized prefix')
    require(all(re.fullmatch('[0-9a-f]{64}', tx['transaction_id']) for tx in prefix),
            'Unhashed prior transaction reference')
    require(all(type(tx['height']) is int and 0 <= tx['height'] < row['cutoff_height'] for tx in prefix),
            'Non-prior-block transaction in prefix')
    require(row['payment_txid_sha256'] not in {tx['transaction_id'] for tx in prefix},
            'Reference payment occurs in prefix')
    vector_key(row['features'])
    require(entry['features'] == row['features'] == features(prefix, row['cutoff_height']),
            'Fourteen-feature reproduction mismatch')
    return prefix


def coverage(rows):
    result = []
    for height in [None] + sorted({r['cutoff_height'] for r in rows}):
        for label, name in [(1, 'case'), (0, 'comparison')]:
            group = [r for r in rows if r[TARGET] == label and (height is None or r['cutoff_height'] == height)]
            available = sum(r['features'] is not None for r in group)
            result.append(dict(cutoff_height=height, membership=name, selected=len(group),
                               available=available, unavailable=len(group)-available,
                               coverage_fraction=available/len(group)))
    return result


def build(protocol_path):
    protocol = load_json(protocol_path)
    require(protocol['partition'] == PARTITION, 'Frozen partition rule changed')
    paths = {key: read_pin(ROOT, pin) for key, pin in protocol['inputs'].items()}
    require(paths['auditor'] == Path(__file__).resolve(), 'Wrong auditor pin')
    design, view = load_json(paths['design']), load_json(paths['view'])
    require(design['predictors'] == view['predictor_allowlist'] == list(FEATURE_NAMES), 'Predictors changed')
    require(design['primary_target']['name'] == TARGET and view['schema_version'] == 2, 'Target/schema changed')
    require(PARTITION['hash_prefix'] in design['evaluation']['partition'], 'Design split salt mismatch')
    cases, selection = load_json(paths['cases']), load_json(paths['selection'])
    require(selection['protocol_sha256'] == protocol['inputs']['design']['sha256'], 'Selection/design mismatch')
    require(selection['case_sources_reconciled'] == len(cases['rows']) == design['case_source_count'],
            'Case census mismatch')
    require(selection['selected_comparison_sources'] == len(selection['rows']) == 1000, 'Comparison census mismatch')
    expected = index_rows(cases['rows'] + selection['rows'])
    rows = view['rows']
    require(set(index_rows(rows)) == set(expected), 'Selected source universe changed')
    require(len({r['address_sha256'] for r in rows}) == len(rows), 'Repeated source address in selection')
    case_ids = {r['source_id'] for r in cases['rows']}
    blocks = {b['height']: b['hash'] for b in design['blocks']}
    for row in rows:
        original = expected[row['source_id']]
        require(all(row[k] == original[k] for k in IDENTITY), 'Selected source/payment/cutoff changed')
        require(row[TARGET] == int(row['source_id'] in case_ids), 'Membership target changed')
        require(blocks[row['cutoff_height']] == row['cutoff_block_hash'], 'Reference block/hash mismatch')
        require(row['labels'] == (original['labels'] if row[TARGET] else UNKNOWN_LABELS), 'Labels changed')
        require(all(row['labels'][k] is None for k in
                    ('hardware_signing_at_event', 'independently_verified_compromise', 'independently_verified_seed_origin')),
                'Independently unknown labels changed')
        require(all(re.fullmatch('[0-9a-f]{64}', row[k]) for k in
                    ('address_sha256', 'payment_txid_sha256', 'cutoff_block_hash')), 'Invalid identity hash')
        if row[TARGET]:
            require(row['features'] == original['features'], 'Previously saved case vector changed')
        if row['features'] is None:
            require(row['precutoff_history_status'] == 'bounded_incomplete', 'Unresolved network outcome')
        else:
            require(row['precutoff_history_status'] in ('complete_full_history', 'complete_prior_prefix'),
                    'Vector supplied for unfinished prefix')
    for quota in design['comparison_selection']['quotas']:
        for label, count in [(1, quota['case_sources']), (0, quota['comparison_quota'])]:
            require(sum(r[TARGET] == label and r['cutoff_height'] == quota['height'] for r in rows) == count,
                    'Frozen stratum count changed')
    resume = load_json(paths['completion_resume'])
    require(resume['network_source_ids'] == [] and resume['network_sources'] == 0, 'Continuation not closed')
    require(set(resume['excluded_bounded_incomplete_source_ids']) ==
            {r['source_id'] for r in rows if r['features'] is None}, 'Completion/resume disagreement')

    checkpoints = {key: load_json(paths[key])['entries'] for key in protocol['checkpoints'].values()}
    prefixes, evidence, counters = {}, [], []
    extended_counts = load_json(paths['extended_progress'])['current_full_transaction_counts']
    for row in rows:
        key = row['source_id']
        full_key = protocol['checkpoints'][row['full_history_provenance']['chosen_pass']]
        full = checkpoints[full_key][key]
        require(full['status'] == row['full_history_status'], 'Full-history status changed')
        require(full['address_sha256'] == row['address_sha256'] and full['cutoff_height'] == row['cutoff_height'],
                'Full-history evidence identity changed')
        if not row[TARGET]:
            # Complete full histories reconcile the provider count; unfinished
            # histories instead use the later explicitly saved counter snapshot.
            if row['full_history_status'] == 'complete':
                require(full['history_audit']['coverage_complete_by_provider_counters'], 'Unreconciled full history')
                counter = full['history_audit']['observed']['tx_count']
                counter_origin = protocol['inputs'][full_key]['file']
            else:
                counter = extended_counts[key]
                counter_origin = protocol['inputs']['extended_progress']['file']
            require(type(counter) is int and counter >= 0, 'Invalid full-current-history counter')
            counters.append(dict(source_id=key, predictor_available=row['features'] is not None,
                                 tx_count=counter, evidence_file=counter_origin))
        if row['features'] is None:
            continue
        prior = row.get('precutoff_history_provenance')
        evidence_key = protocol['checkpoints'][prior['pass_name']] if prior else full_key
        entry = checkpoints[evidence_key][key]
        if prior:
            require(entry['raw_sha256'] == prior['raw_sha256'], 'Prefix provenance fingerprint mismatch')
        prefixes[key] = check_prefix(row, entry)
        evidence.append(dict(source_id=key, checkpoint_file=protocol['inputs'][evidence_key]['file'],
                             normalized_prefix_sha256=digest(json_bytes(prefixes[key])),
                             prior_transaction_count=len(prefixes[key])))

    eligible = [r for r in rows if r['features'] is not None]
    links = link_sets(eligible, prefixes)
    groups = components(eligible, links)
    check_components_independently(eligible, links, groups)
    partition = evaluate_partitions(eligible, groups, links)
    by_id = index_rows(eligible)
    group_records = [dict(component_id=digest(json_bytes(group)), source_ids=group,
                          minimum_address_sha256=min(by_id[key]['address_sha256'] for key in group),
                          size=len(group), case=sum(by_id[key][TARGET] for key in group),
                          comparison=sum(1-by_id[key][TARGET] for key in group)) for group in groups]
    link_records = {kind: [dict(reference_sha256=ref, source_ids=sorted(members))
                           for ref, members in sorted(values.items()) if len(members) > 1]
                    for kind, values in links.items()}
    link_summary = {kind: dict(shared_groups=len(records),
                               rows_in_shared_groups=len({key for rec in records for key in rec['source_ids']}),
                               star_edges=sum(len(rec['source_ids'])-1 for rec in records))
                    for kind, records in link_records.items()}
    distributions = {name: {feature: distribution([r['features'][feature] for r in eligible if r[TARGET] == label])
                             for feature in FEATURE_NAMES} for label, name in [(1, 'case'), (0, 'comparison')]}
    counter_profiles = {name: distribution([r['tx_count'] for r in counters if r['predictor_available'] == available])
                        for available, name in [(True, 'available_comparison'), (False, 'unavailable_comparison')]}
    available_cases = sum(r[TARGET] for r in eligible)
    selected_cases = sum(r[TARGET] for r in rows)
    summary = dict(schema_version=1, created_at=protocol['created_at'], target=TARGET,
                   output_folder=protocol_path.parent.name,
                   input_commit=protocol['input_commit'], selected_sources=len(rows),
                   available_vectors=len(eligible), unavailable_vectors=len(rows)-len(eligible),
                   available_case_vectors=available_cases,
                   available_comparison_vectors=len(eligible)-available_cases,
                   selected_membership_prevalence=selected_cases/len(rows),
                   available_membership_prevalence=available_cases/len(eligible),
                   coverage=coverage(rows),
                   full_history_comparison_statuses=dict(Counter(r['full_history_status'] for r in rows if not r[TARGET])),
                   precutoff_comparison_statuses=dict(Counter(r['precutoff_history_status'] for r in rows if not r[TARGET])),
                   vectors_reproduced=len(prefixes), prior_address_transaction_observations=sum(map(len, prefixes.values())),
                   distinct_prior_transaction_references=len(links['prior_transaction']),
                   component_count=len(groups), mixed_membership_components=sum(g['case'] > 0 and g['comparison'] > 0 for g in group_records),
                   singleton_components=sum(g['size'] == 1 for g in group_records),
                   largest_components=[{k: v for k, v in g.items() if k != 'source_ids'} for g in
                                       sorted(group_records, key=lambda g: (-g['size'], g['component_id']))[:10]],
                   link_summary=link_summary, frozen_partition_feasibility=partition,
                   feature_distributions=distributions,
                   full_current_history_counter_diagnostic=counter_profiles,
                   counter_diagnostic_policy='Provider counts at different collection snapshots, not prior-block features. Complete histories use reconciled observed totals; incomplete histories use the saved supplemental counter snapshot. Descriptive attrition diagnostic only.',
                   quantile_method='Empirical inverse CDF, rank max(1, ceil(p*n)); p50 is lower median for even n; missing values excluded.',
                   label_counts=dict(independently_verified_compromise=0, independently_verified_device=0,
                                     owner_reported_loss=sum(r['labels']['reported_loss'] == 1 for r in rows)),
                   incident_count=1, independent_incident_evaluation_possible=False,
                   independent_component_check='BFS traversal agrees with union-find',
                   grouping_scope='Observed completed prior prefixes only; unknown prior links of 122 excluded sources are not claimed absent. Components are not ownership clusters.',
                   partition_feasibility_evaluated=True, dataset_split_materialized=False,
                   training_performed=False, preprocessing_fitted=False, resampling_performed=False,
                   collection_performed=False, prior_results_modified=False)
    artifacts = dict(components=group_records, shared_link_evidence=link_records,
                     prefix_evidence=evidence, full_current_history_counter_evidence=counters,
                     partition_assignments_exported=False)
    files = {'summary.json': json_bytes(summary),
             'group_evidence.json.gz': gzip.compress(json_bytes(artifacts), mtime=0),
             'README.md': report(summary).encode()}
    verification = dict(schema_version=1, protocol_sha256=digest(protocol_path.read_bytes()),
                        input_files_verified=len(paths), reproduced_vectors=len(prefixes),
                        independent_components_agree=True, frozen_rule_used=True,
                        outputs={name: digest(data) for name, data in files.items()},
                        dataset_split_materialized=False, training_performed=False,
                        collection_performed=False)
    files['verification.json'] = json_bytes(verification)
    return files, summary


def report(s):
    lines = ['# Source comparison feasibility — 2 November 2026', '',
             'Offline audit of the latest schema-v2 view. The unit is one selected input source address; the target is `known_coldcard_core_membership`. This is retrospective within-window case association, not verified theft or hardware identification. No provider request, model, fitted preprocessing or dataset split was performed.', '',
             '## Coverage and attrition', '',
             '| Reference block | Membership | Selected | Available | Unavailable | Coverage |',
             '| --- | --- | ---: | ---: | ---: | ---: |']
    for c in s['coverage']:
        lines.append(f"| {c['cutoff_height'] or 'All'} | {c['membership']} | {c['selected']} | {c['available']} | {c['unavailable']} | {100*c['coverage_fraction']:.2f}% |")
    lines += ['', f"All {s['vectors_reproduced']:,} available vectors reproduce exactly from the pinned normalized prefixes ({s['prior_address_transaction_observations']:,} address/transaction observations). The entire reference block and all future heights remain excluded. The 122 bounded-incomplete comparisons retain null vectors and remain outside this assessment's eligible population.", '',
              f"Membership prevalence changes from {100*s['selected_membership_prevalence']:.2f}% in the selected cohort to {100*s['available_membership_prevalence']:.2f}% among available vectors. Completion is asymmetric by class and block. The following saved full-current-history counts help describe this selection effect; they were observed at different collection snapshots and are **not** pre-cutoff predictors or estimates for missing features.", '',
              '| Comparison vectors | Count | Full-current transaction count p50 | p95 | Maximum |',
              '| --- | ---: | ---: | ---: | ---: |']
    for key in ('available_comparison', 'unavailable_comparison'):
        c = s['full_current_history_counter_diagnostic'][key]
        lines.append(f"| {key.replace('_comparison', '')} | {c['nonmissing']} | {c['p50']} | {c['p95']} | {c['max']} |")
    lines += ['', 'The incomplete group cannot be assumed missing at random. These data support a complete-case exploratory study with an explicit coverage limitation, not an unbiased study of every selected source. A page bound does not establish the exact number of prior transactions. No unavailable vector was imputed, replaced or recollected.', '',
              'Full-current-history coverage stays separate: 864 comparison histories are complete and 136 incomplete. Fourteen of the incomplete current histories have a validated exhausted prior prefix. The remaining 122 prior prefixes are bounded-incomplete. A prefix does not reconcile the current full-history counters.', '',
              '## Frozen grouping and partition feasibility', '',
              f"The {s['available_vectors']:,} eligible addresses form {s['component_count']} connected components ({s['singleton_components']} singletons). The largest contains {s['largest_components'][0]['size']} comparisons. An independent breadth-first graph traversal reproduces every component. Groups combine repeated address hashes, shared prior transactions, common reference TXIDs and identical fourteen-feature vectors including missingness. They prevent measured overlap and do not establish common ownership.", '',
              '| Link criterion | Shared groups | Addresses in shared groups | Star edges before transitive closure |',
              '| --- | ---: | ---: | ---: |']
    for kind, c in s['link_summary'].items():
        lines.append(f"| {kind} | {c['shared_groups']} | {c['rows_in_shared_groups']} | {c['star_edges']} |")
    lines += ['', 'The original salt `coldcard-source-split-v1:42:` and lexical minimum address SHA256 determine each component bucket, modulo ten (0–6 train, 7 validation, 8–9 test). This dry run exports aggregate counts only; it does not create model datasets or per-row partition files.', '',
              '| Prospective partition | Components | Cases | Comparisons |',
              '| --- | ---: | ---: | ---: |']
    for name, c in s['frozen_partition_feasibility']['counts'].items():
        lines.append(f"| {name} | {c['components']} | {c['case']} | {c['comparison']} |")
    gate = s['frozen_partition_feasibility']
    lines += ['', ('**The frozen feasibility gate passes:** each partition has at least 20 members of each class, with zero measured link groups crossing partitions.' if gate['feasible'] else '**The frozen feasibility gate fails:** ' + '; '.join(gate['failures']) + '.'),
              'No seed reroll, group splitting or resampling was used. Links involving unknown histories of excluded sources are not claimed absent. Retain the selected eligible population and component evidence unchanged for any subsequently authorized baseline.', '',
              '## Descriptive feature profiles', '',
              'Quantiles use the empirical inverse CDF (rank max(1, ceil(p*n))); missing values are excluded. Medians below are descriptive only and were not fitted as imputation values.', '',
              '| Prior-block feature | Case p50 | Comparison p50 | Case missing | Comparison missing |',
              '| --- | ---: | ---: | ---: | ---: |']
    for feature in FEATURE_NAMES:
        a, b = (s['feature_distributions'][k][feature] for k in ('case', 'comparison'))
        lines.append(f"| {feature} | {a['p50']} | {b['p50']} | {a['missing']} | {b['missing']} |")
    lines += ['', 'Full distributions, including zeros and tails, are in `summary.json`. Feature availability remains distinct from a legitimately undefined spending fee rate. No post-cutoff counters, reference-payment fields, identifiers, labels or collection artifacts enter the fourteen predictors.', '',
              '## Decision and reproducibility', '',
              'The numerical coverage/grouping gate supports a later prespecified shallow decision-tree baseline on the available vectors, conditional on explicit complete-case interpretation. This audit does not authorize or execute that model. It cannot validate theft/device detection: independently verified compromise and device labels remain unknown for every row; one owner report is preserved separately, and all cases come from one incident. No independent-incident generalization or untouched-test claim is justified.', '',
              'Inputs and implementation are SHA256-pinned in `protocol.json`; redacted component membership, shared link evidence and prefix/counter joins are in `group_evidence.json.gz`. Old checkpoints and views are unchanged. `verification.json` fingerprints all generated outputs.', '',
              'Reproduce from `Task 2/research/coldcard`:', '', '```sh',
              f"python audit_source_comparison_feasibility.py verify {s['output_folder']}/protocol.json",
              'python -m unittest discover -s . -p test_source_comparison_feasibility.py', '```', '']
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['build', 'verify'])
    parser.add_argument('protocol', type=Path)
    args = parser.parse_args()
    files, summary = build(args.protocol.resolve())
    output = args.protocol.resolve().parent
    if args.mode == 'build':
        require(not any((output/name).exists() for name in files), 'Refusing to overwrite existing audit outputs')
        for name, data in files.items():
            (output/name).write_bytes(data)
    else:
        for name, data in files.items():
            require((output/name).read_bytes() == data, 'Output differs from pinned reconstruction: ' + name)
    print(json.dumps(dict(mode=args.mode, vectors_reproduced=summary['vectors_reproduced'],
                          components=summary['component_count'],
                          frozen_partition_feasible=summary['frozen_partition_feasibility']['feasible'],
                          output_files=len(files), training_performed=False)))


if __name__ == '__main__':
    main()
