"""Rebuild overlap edges and eligibility independently from pinned evidence."""
import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def encoded(value):
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n').encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == '.gz' else data)


def check(protocol_path):
    config = read(protocol_path);paths = {}
    for name, pin in config['inputs'].items():
        path = (ROOT / pin['file']).resolve()
        if not path.is_relative_to(ROOT) or sha(path.read_bytes()) != pin['sha256']:
            raise ValueError('Independent pinned input check failed: ' + name)
        paths[name] = path
    development, external = read(paths['coldcard_view']), read(paths['external_view'])
    dev_cps = {name: read(paths[key])['entries'] for name, key in config['development_checkpoints'].items()}
    ext_cps = {name: read(paths[spec['checkpoint']])['entries'] for name, spec in config['external_checkpoints'].items()}
    rows, graph, first_owner, prefix_counts = {}, defaultdict(set), {}, Counter()
    names = development['predictor_allowlist']
    for dataset, view in [('coldcard', development), ('cryptobilis', external)]:
        for row in view['rows']:
            key = dataset + ':' + row['source_id'];rows[key] = row;graph[key]
            reference = row['payment_txid_sha256'] if dataset == 'coldcard' else row['reference_txid_sha256']
            tokens = [('address', row['address_sha256']), ('reference', reference), ('any_tx', reference)]
            if row['features'] is not None:
                # Exact tuples provide an independent representation of the rational vector key.
                values = tuple(None if row['features'][name] is None else Fraction(row['features'][name]) for name in names)
                tokens.append(('vector', values))
                provenance = row.get('precutoff_history_provenance') or row['full_history_provenance']
                pass_name = provenance.get('pass_name', provenance.get('chosen_pass'))
                entry = (dev_cps if dataset == 'coldcard' else ext_cps)[pass_name][row['source_id']]
                for transaction in entry['prefix']:
                    tokens.extend([('prior', transaction['transaction_id']), ('any_tx', transaction['transaction_id'])])
                    prefix_counts[dataset] += 1
            for token in tokens:
                other = first_owner.setdefault(token, key)
                if other != key:
                    graph[key].add(other);graph[other].add(key)
    groups, unseen = [], set(graph)
    while unseen:
        frontier = [min(unseen)];visited = set()
        while frontier:
            current = frontier.pop()
            if current in visited:
                continue
            visited.add(current);frontier.extend(graph[current] - visited)
        groups.append(sorted(visited));unseen -= visited
    out = protocol_path.parent
    evidence = read(out/'overlap_evidence.json.gz')
    if sorted(groups) != sorted(g['source_keys'] for g in evidence['components']):
        raise ValueError('Independent complete graph reconstruction disagrees')
    manifest = read(out/'eligibility_manifest.json.gz')['rows']
    actual = {r['source_id']: r for r in manifest}
    if len(actual) != len(manifest) or set(actual) != {r['source_id'] for r in external['rows']}:
        raise ValueError('Independent external manifest coverage disagrees')
    expected, all_cross, bounded_cross = {}, set(), set()
    for group in groups:
        cross = any(k.startswith('coldcard:') for k in group) and any(k.startswith('cryptobilis:') for k in group)
        for key in group:
            if not key.startswith('cryptobilis:'):
                continue
            row = rows[key]
            status = ('excluded_bounded_incomplete' if row['features'] is None else
                      'quarantined_cross_development_component' if cross else
                      'eligible_for_frozen_proxy_evaluation')
            expected[row['source_id']] = status
            if cross:
                all_cross.add(row['source_id'])
                if row['features'] is None:
                    bounded_cross.add(row['source_id'])
    if expected != {key: row['status'] for key, row in actual.items()}:
        raise ValueError('Independent per-source eligibility disagrees')
    counts = Counter((rows['cryptobilis:'+key]['cryptobilis_reference_source_membership'], status)
                     for key, status in expected.items())
    eligible = {name: counts[(label, 'eligible_for_frozen_proxy_evaluation')] for label, name in [(1, 'case'), (0, 'comparison')]}
    summary = read(out/'summary.json')
    for label, name in [(1, 'case'), (0, 'comparison')]:
        if eligible[name] != summary['counts'][name]['eligible']:
            raise ValueError('Independent class support differs')
    return dict(schema_version=1, independent_verifier_sha256=sha(Path(__file__).read_bytes()),
        protocol_sha256=sha(protocol_path.read_bytes()), input_files_verified=len(paths),
        independently_rebuilt_components=len(groups), all_component_memberships_exact=True,
        independently_classified_external_sources=len(expected), eligible=eligible,
        external_members_of_cross_components=len(all_cross), bounded_external_members_of_cross_components=len(bounded_cross),
        prior_transaction_observations=dict(prefix_counts), complete_vectors=sum(r['features'] is not None for r in rows.values()),
        external_manifest_sha256=sha((out/'eligibility_manifest.json.gz').read_bytes()),
        frozen_model_sha256=sha(paths['frozen_model'].read_bytes()), frozen_split_sha256=sha(paths['frozen_split'].read_bytes()),
        provider_requests=0, model_fits=0, scores_computed=0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['build', 'verify'])
    parser.add_argument('protocol', type=Path)
    args = parser.parse_args();protocol = args.protocol.resolve();result = encoded(check(protocol))
    destination = protocol.parent/'independent_verification.json'
    if args.mode == 'build':
        if destination.exists():
            raise ValueError('Refusing to overwrite an independent verification')
        destination.write_bytes(result)
    elif destination.read_bytes() != result:
        raise ValueError('Independent verification differs')
    print(result.decode())
