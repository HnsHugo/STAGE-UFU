"""Offline development/external overlap and frozen-model eligibility audit.

Only pinned normalized evidence is read. No network, model inference, fitting,
replacement, new partition or mutation of an earlier artifact is performed.
"""
import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'coldcard'))
import audit_source_comparison_feasibility as frozen

EXTERNAL_TARGET = 'cryptobilis_reference_source_membership'
KINDS = ('address', 'prior_transaction', 'reference_transaction', 'full_vector',
         'transaction_any_role')
UNKNOWN = ('hardware_signing_at_event', 'independently_verified_compromise',
           'independently_verified_seed_origin')
RULES = dict(
    link_kinds=list(KINDS), include_all_selected_identities=True,
    prior_links_from_complete_normalized_prefixes_only=True,
    numeric_vector_equality='Exact rational equality including missingness; no float32 rounding',
    cross_role_policy='Also join an observed prior TXID to a reference TXID; conservative prescoring guard',
    quarantine='Every external member of a measured component containing any development member',
    unavailable='Retain null bounded prefixes outside eligibility; unknown prior links are not absent',
    minimum_eligible_per_class=20, replacement=False, score_based_filtering=False,
    preserve_development_partitions=True, model_fits=0, scores_computed=0,
    provider_requests=0)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == '.gz' else data)


def resolve_pin(root, pin):
    path = (root / pin['file']).resolve()
    require(path.is_relative_to(root.resolve()), 'Pinned input outside research root')
    require(sha(path.read_bytes()) == pin['sha256'], 'Input fingerprint mismatch: ' + pin['file'])
    return path


def index(rows):
    result = {r['source_id']: r for r in rows}
    require(len(result) == len(rows), 'Repeated source ID')
    return result


def normalized_prefix(row, entry, external=False):
    require(entry['source_id'] == row['source_id'], 'Checkpoint source ID mismatch')
    for field in ('address_sha256', 'cutoff_height', 'cutoff_block_hash'):
        if field in entry:
            require(row[field] == entry[field], 'Checkpoint identity mismatch: ' + field)
    reference = row['reference_txid_sha256'] if external else row['payment_txid_sha256']
    if 'payment_txid_sha256' in entry:
        require(reference == entry['payment_txid_sha256'], 'Checkpoint reference mismatch')
    require(entry['features'] == row['features'], 'Checkpoint vector mismatch')
    if row['features'] is None:
        require(row['precutoff_history_status'] == 'bounded_incomplete', 'Unresolved source remains')
        require(entry['status'] in ('incomplete', 'bounded_incomplete') and entry['prefix'] is None,
                'Unfinished prefix supplies features or an asserted normalized prefix')
        return []
    require(entry['status'] in ('complete', 'complete_prior_prefix'), 'Unfinished source supplies a vector')
    require(row['precutoff_history_status'] in ('complete_full_history', 'complete_prior_prefix'),
            'View supplies a vector from an unfinished prefix')
    prefix = entry['prefix']
    require(isinstance(prefix, list), 'Missing complete normalized prefix')
    ids = [tx['transaction_id'] for tx in prefix]
    require(all(re.fullmatch('[0-9a-f]{64}', value) for value in ids), 'Invalid transaction hash')
    require(len(set(ids)) == len(ids), 'Repeated prior transaction')
    require(reference not in ids, 'Reference transaction leaked into its prior prefix')
    require(all(type(tx['height']) is int and 0 <= tx['height'] < row['cutoff_height'] for tx in prefix),
            'Reference-block or future transaction leaked into prefix')
    frozen.vector_key(row['features'])
    require(frozen.features(prefix, row['cutoff_height']) == row['features'], 'Vector does not reproduce')
    return prefix


def validate_external(view, selected):
    require(view['schema_version'] == 2 and view['operational_target'] == EXTERNAL_TARGET,
            'External schema or target changed')
    originals, rows = index(selected['rows']), index(view['rows'])
    require(set(originals) == set(rows), 'Fixed external selection changed')
    require(len({r['address_sha256'] for r in rows.values()}) == len(rows), 'Repeated external address')
    for key, row in rows.items():
        require(type(row[EXTERNAL_TARGET]) is int and row[EXTERNAL_TARGET] in (0, 1), 'Invalid external target')
        for field, value in originals[key].items():
            if field not in ('features', 'prior_prefix_status'):
                require(row[field] == value, 'Frozen external selection field changed: ' + field)
        require(all(v is None for v in row['labels'].values()), 'Unknown external labels changed')
        require(row['full_history_status'] == 'not_collected_for_this_source', 'Full-history status promoted')
        require(row['incident_group'] == 'cryptobilis_2026', 'External incident group changed')
        require(row['prior_prefix_status'] == row['precutoff_history_status'], 'Prefix status mismatch')
    return rows


def validate_development_declaration(view):
    # The preserved schema-v2 view appends its interpretation after a semicolon;
    # the actual per-row and fitted-model target remains the canonical name.
    require(view['schema_version'] == 2 and
            view['target'].split(';', 1)[0] == frozen.TARGET,
            'Development schema/target changed')


def link_catalog(nodes, prefixes):
    links = {kind: defaultdict(set) for kind in KINDS}
    for node in nodes:
        key = node['key']
        links['address'][node['address_sha256']].add(key)
        links['reference_transaction'][node['reference_sha256']].add(key)
        links['transaction_any_role'][node['reference_sha256']].add(key)
        if node['features'] is not None:
            links['full_vector'][frozen.vector_key(node['features'])].add(key)
        for tx in prefixes[key]:
            links['prior_transaction'][tx['transaction_id']].add(key)
            links['transaction_any_role'][tx['transaction_id']].add(key)
    return links


def components(keys, links):
    parent = {key: key for key in keys}

    def find(key):
        while parent[key] != key:
            parent[key] = parent[parent[key]]
            key = parent[key]
        return key

    for values in links.values():
        for members in values.values():
            first, *others = sorted(members)
            for other in others:
                parent[find(other)] = find(first)
    groups = defaultdict(list)
    for key in sorted(parent):
        groups[find(key)].append(key)
    return sorted(groups.values())


def independent_components(keys, links):
    """Traverse the row/token bipartite graph, independently of union-find."""
    tokens_for = defaultdict(list)
    members_for = {}
    for kind, values in links.items():
        for token, members in values.items():
            if len(members) < 2:
                continue
            full_token = (kind, token)
            members_for[full_token] = members
            for key in members:
                tokens_for[key].append(full_token)
    unseen, groups, visited_tokens = set(keys), [], set()
    while unseen:
        start = min(unseen)
        queue, visited = [start], {start}
        while queue:
            key = queue.pop()
            for token in tokens_for[key]:
                if token in visited_tokens:
                    continue
                visited_tokens.add(token)
                new = members_for[token] - visited
                visited.update(new)
                queue.extend(new)
        groups.append(sorted(visited))
        unseen -= visited
    return sorted(groups)


def classify(nodes, groups):
    by_key = {n['key']: n for n in nodes}
    require(len(by_key) == len(nodes), 'Repeated namespaced source ID')
    require(sorted(key for group in groups for key in group) == sorted(by_key), 'Component coverage differs')
    records, assignments = [], {}
    for group in groups:
        component_id = sha(encoded(group))
        datasets = {by_key[key]['dataset'] for key in group}
        cross = datasets == {'coldcard', 'cryptobilis'}
        records.append(dict(component_id=component_id, source_keys=group,
                            cross_development=cross, size=len(group),
                            dataset_counts=dict(Counter(by_key[k]['dataset'] for k in group))))
        for key in group:
            node = by_key[key]
            if node['dataset'] != 'cryptobilis':
                continue
            status = ('excluded_bounded_incomplete' if node['features'] is None else
                      'quarantined_cross_development_component' if cross else
                      'eligible_for_frozen_proxy_evaluation')
            assignments[key] = dict(source_id=node['source_id'], component_id=component_id,
                membership=node['membership'], cutoff_height=node['cutoff_height'], status=status,
                cross_development_component=cross, full_history_status=node['full_history_status'])
    return records, [assignments[key] for key in sorted(assignments)]


def support(assignments, height=None):
    result = {}
    for label, name in [(1, 'case'), (0, 'comparison')]:
        rows = [a for a in assignments if a['membership'] == label and
                (height is None or a['cutoff_height'] == height)]
        counts = Counter(a['status'] for a in rows)
        result[name] = dict(selected=len(rows), bounded_incomplete=counts['excluded_bounded_incomplete'],
            quarantined_complete=counts['quarantined_cross_development_component'],
            eligible=counts['eligible_for_frozen_proxy_evaluation'],
            in_cross_development_components=sum(a['cross_development_component'] for a in rows))
    return result


def build(configuration):
    config = read(configuration)
    require(config['rules'] == RULES, 'Prespecified overlap rules changed')
    paths = {k: resolve_pin(ROOT, p) for k, p in config['inputs'].items()}
    require(paths['auditor'] == Path(__file__).resolve(), 'Wrong overlap auditor')
    transfer, model = read(paths['transfer_protocol']), read(paths['frozen_model'])
    require(sha(paths['frozen_model'].read_bytes()) == transfer['frozen_model']['sha256'], 'Frozen model changed')
    require(sha(paths['frozen_model_protocol'].read_bytes()) == transfer['frozen_model_protocol']['sha256'],
            'Frozen model protocol changed')
    require(model['threshold'] == transfer['threshold'] == .5 and
            model['threshold_operator'] == transfer['threshold_operator'] == '>=', 'Threshold changed')
    names = list(frozen.FEATURE_NAMES)
    require(model['preprocessing']['predictor_allowlist'] == transfer['predictor_allowlist'] == names,
            'Model or transfer predictor allowlist changed')
    require(model['fit_partition'] == model['preprocessing']['fit_partition'] == 'train' and
            model['training_fit_calls'] == 1, 'Frozen training provenance changed')
    require(model['model_input_names'] == names + ['missing__' + n for n in names], 'Missing indicators changed')
    development, external = read(paths['coldcard_view']), read(paths['external_view'])
    validate_development_declaration(development)
    require(model['target'] == frozen.TARGET, 'Frozen model target changed')
    require(development['predictor_allowlist'] == external['predictor_allowlist'] == names, 'View predictors changed')
    require(len(development['rows']) == 1500 and len(external['rows']) == 366, 'Cohort sizes changed')
    validate_external(external, read(paths['source_selection']))
    closure = read(paths['acquisition_audit'])
    require(closure['selected_sources'] == 366 and closure['complete_vectors'] == 329 and
            closure['network_sources_remaining'] == 0 and closure['raw_tails_reextracted'] == 366,
            'External acquisition is not audited/closed')
    resume = read(paths['acquisition_resume'])
    require(resume['network_source_ids'] == [] and resume['collection_can_resume'] is False,
            'External acquisition is not stopped')
    development_rows = index(development['rows'])
    split = read(paths['frozen_split']); split_rows = index(split['rows'])
    require(set(split_rows) == set(development_rows), 'Frozen development partition coverage changed')
    feasibility = read(paths['feasibility_protocol'])
    dev_checkpoints = {name: read(paths[key])['entries'] for name, key in config['development_checkpoints'].items()}
    ext_checkpoints = {}
    for name, spec in config['external_checkpoints'].items():
        cp, proto = read(paths[spec['checkpoint']]), read(paths[spec['protocol']])
        require(cp['protocol_sha256'] == sha(paths[spec['protocol']].read_bytes()), 'External checkpoint protocol differs')
        require(set(cp['entries']) == set(proto['source_ids']), 'External pass source coverage differs')
        ext_checkpoints[name] = cp['entries']
    require(sum(len(e) for e in ext_checkpoints.values()) == 366, 'External pass outcomes overlap or are missing')
    nodes, prefixes, reproduction = [], {}, Counter()
    for dataset, view in [('coldcard', development), ('cryptobilis', external)]:
        target = frozen.TARGET if dataset == 'coldcard' else EXTERNAL_TARGET
        for row in view['rows']:
            key = dataset + ':' + row['source_id']
            require(all(row['labels'][label] is None for label in UNKNOWN), 'Verified unknown label changed')
            require(type(row[target]) is int and row[target] in (0, 1), 'Invalid membership target')
            if dataset == 'coldcard':
                s = split_rows[row['source_id']]
                for field in ('address_sha256', 'cutoff_height', target, 'precutoff_history_status', 'full_history_status'):
                    require(s[field] == row[field], 'Frozen partition identity changed: ' + field)
                require((s['partition'] in ('train', 'validation', 'test')) == (row['features'] is not None),
                        'Frozen partition eligibility changed')
                full_name = row['full_history_provenance']['chosen_pass']
                full = dev_checkpoints[full_name][row['source_id']]
                require(full['status'] == row['full_history_status'], 'Full-current-history status changed')
                provenance = row.get('precutoff_history_provenance')
                pass_name = provenance['pass_name'] if provenance else full_name
                entry = dev_checkpoints[pass_name][row['source_id']]
                reference = row['payment_txid_sha256']
            else:
                provenance = row['precutoff_history_provenance']
                pass_name = provenance['pass_name'];entry = ext_checkpoints[pass_name][row['source_id']]
                reference = row['reference_txid_sha256']
            if provenance:
                require(provenance['raw_sha256'] == entry['raw_sha256'], 'Prefix raw provenance changed')
            prefixes[key] = normalized_prefix(row, entry, external=(dataset == 'cryptobilis'))
            reproduction[dataset] += row['features'] is not None
            nodes.append(dict(key=key, dataset=dataset, source_id=row['source_id'], membership=row[target],
                address_sha256=row['address_sha256'], reference_sha256=reference,
                cutoff_height=row['cutoff_height'], full_history_status=row['full_history_status'],
                features=row['features']))
    require(reproduction == {'coldcard': 1378, 'cryptobilis': 329}, 'Vector availability changed')
    # Reconstruct the original development components without reassigning a single partition.
    dev_available = [r for r in development['rows'] if r['features'] is not None]
    dev_prefixes = {r['source_id']: prefixes['coldcard:' + r['source_id']] for r in dev_available}
    old_links = frozen.link_sets(dev_available, dev_prefixes)
    old_groups = frozen.components(dev_available, old_links)
    frozen.check_components_independently(dev_available, old_links, old_groups)
    expected_groups = read(paths['frozen_groups'])['components']
    require(sorted(old_groups) == sorted(g['source_ids'] for g in expected_groups), 'Frozen 918 development groups differ')
    require(feasibility['partition'] == split['partition_rule'], 'Frozen partition rule differs')
    links = link_catalog(nodes, prefixes)
    groups = components([n['key'] for n in nodes], links)
    require(groups == independent_components([n['key'] for n in nodes], links), 'Independent bipartite traversal differs')
    records, assignments = classify(nodes, groups)
    by_key = {n['key']: n for n in nodes}
    witnesses = {}
    for kind, values in links.items():
        witnesses[kind] = [dict(reference_sha256=token, source_keys=sorted(members))
            for token, members in sorted(values.items()) if
            {by_key[k]['dataset'] for k in members} == {'coldcard', 'cryptobilis'}]
    counts = support(assignments)
    minimum = all(counts[name]['eligible'] >= RULES['minimum_eligible_per_class'] for name in counts)
    selected = sum(v['selected'] for v in counts.values())
    eligible = sum(v['eligible'] for v in counts.values())
    summary = dict(schema_version=1, input_commit=config['input_commit'],
        target=EXTERNAL_TARGET, development_target=frozen.TARGET, scope='All selected identities and all available validated normalized prior prefixes',
        selected_external=selected, available_external_vectors=329, bounded_incomplete_external=37,
        development_rows=1500, development_vectors_reproduced=reproduction['coldcard'],
        external_vectors_reproduced=reproduction['cryptobilis'],
        counts=counts, coverage_by_block={str(h): support(assignments, h) for h in sorted({a['cutoff_height'] for a in assignments})},
        eligible_external=eligible, quarantined_complete_external=329-eligible,
        cross_development_components=sum(r['cross_development'] for r in records), total_measured_components=len(records),
        cross_dataset_link_groups={kind: len(values) for kind, values in witnesses.items()},
        independent_components_agree=True, frozen_development_components_reproduced=len(old_groups),
        frozen_development_split_unchanged=True, minimum_20_per_class_passed=minimum,
        can_score_primary_structural_proxy=minimum, scoring_executed=False,
        cutoff='Each normalized transaction height is strictly below its own frozen reference block',
        unobserved_prior_prefixes=dict(coldcard=122, cryptobilis=37),
        full_current_source_histories_reconciled=0, full_history_status_not_promoted=True,
        source_level_verified_compromise_or_device_evaluation_possible=False,
        entity_independence_established=False, external_incidents=1, untouched_test_claim=False,
        frozen_model_sha256=sha(paths['frozen_model'].read_bytes()), frozen_split_sha256=sha(paths['frozen_split'].read_bytes()),
        input_files_verified=len(paths), provider_requests=0, model_fits=0, scores_computed=0,
        replacement_performed=False, new_partition_created=False,
        limitation='All available-prefix links were checked; unknown links of 159 bounded prefixes and unobserved entities remain unresolved. Exact vector matches are dependence guards, not evidence of ownership.')
    evidence = dict(schema_version=1, components=records, cross_dataset_witnesses=witnesses,
        node_catalog=[{k: v for k, v in n.items() if k != 'features'} for n in nodes],
        prior_transaction_observations={name: sum(len(prefixes[n['key']]) for n in nodes if n['dataset'] == name)
                                        for name in ('coldcard', 'cryptobilis')})
    files = {'summary.json': encoded(summary), 'overlap_evidence.json.gz': gzip.compress(encoded(evidence), mtime=0),
             'eligibility_manifest.json.gz': gzip.compress(encoded(dict(schema_version=1, rows=assignments)), mtime=0)}
    files['verification.json'] = encoded(dict(schema_version=1, protocol_sha256=sha(configuration.read_bytes()),
        input_files_verified=len(paths), outputs={name: sha(data) for name, data in files.items()},
        independent_graph_traversal_agrees=True, vectors_reproduced=dict(reproduction),
        frozen_split_unchanged=True, provider_requests=0, model_fits=0, scores_computed=0))
    return files, summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['build', 'verify'])
    parser.add_argument('protocol', type=Path)
    args = parser.parse_args()
    protocol = args.protocol.resolve();files, summary = build(protocol)
    if args.mode == 'build':
        require(not any((protocol.parent / name).exists() for name in files), 'Refusing to overwrite an audit output')
        for name, data in files.items():
            (protocol.parent / name).write_bytes(data)
    else:
        for name, data in files.items():
            require((protocol.parent / name).read_bytes() == data, 'Pinned audit reconstruction differs: ' + name)
    print(json.dumps({k: summary[k] for k in ('counts', 'eligible_external', 'cross_dataset_link_groups',
        'minimum_20_per_class_passed', 'input_files_verified', 'provider_requests', 'model_fits', 'scores_computed')}))


if __name__ == '__main__':
    main()
