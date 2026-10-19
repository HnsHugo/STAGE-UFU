"""Offline eligibility audit; never infer storage labels or train a classifier."""
import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime
import hashlib
import json
from pathlib import Path


def utc(value):
    result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if result.utcoffset() is None:
        raise ValueError('Timezone required')
    return result


def label_covers_window(document):
    """Require explicit reviewed interval evidence, available by window end."""
    if document.get('storage_label_window_validity') != 'verified':
        return False
    evidence = document.get('storage_label_evidence', {})
    try:
        start = utc(document['window']['start_utc_inclusive'])
        end = utc(document['window']['end_utc_exclusive'])
        return (start < end
                and bool(document['seed']['storage_source_url'])
                and evidence['source_url'] == document['seed']['storage_source_url']
                and utc(evidence['valid_from_utc']) <= start
                and utc(evidence['valid_until_utc_exclusive']) >= end
                and utc(evidence['published_at_utc']) <= end)
    except (KeyError, TypeError, ValueError):
        return False


def assess(document):
    seed, window = document['seed'], document['window']
    reasons = []
    if seed['purpose'] != 'research_sample':
        reasons.append('not_research_sample')
    if seed['storage_type'] not in {'hot', 'cold'}:
        reasons.append('unknown_storage')
    covered = window['window_coverage'] == 'count_consistent_full_history'
    if not covered or window.get('metrics') is None:
        reasons.append('incomplete_window')
    if not label_covers_window(document):
        reasons.append('label_interval_or_availability_unverified')
    return {'address': seed['address'], 'entity': seed['entity_name'],
            'published_storage': seed['storage_type'], 'coverage_complete': covered,
            'window_transaction_count': (window['metrics']['transaction_count']
                                         if covered and window.get('metrics') else None),
            'eligible': not reasons, 'exclusion_reasons': reasons}


def verify_input(data, expected):
    actual = hashlib.sha256(data).hexdigest()
    if actual == expected:
        return "exact_bytes"
    # The saved extended CSV was committed with LF after collection used CRLF.
    if b"\r" not in data and hashlib.sha256(data.replace(b"\n", b"\r\n")).hexdigest() == expected:
        return "matches_only_after_LF_to_CRLF_reconstruction"
    raise ValueError("Input snapshot hash mismatch")


def audit(directories):
    observations = defaultdict(list)
    hashes, bounds, input_identity = {}, set(), []
    for directory in directories:
        manifest_path = directory / 'manifest.json'
        manifest = json.loads(manifest_path.read_text())
        input_path = directory / 'input.csv'
        match = verify_input(input_path.read_bytes(), manifest['input_sha256'])
        input_identity.append({'path': str(input_path), 'manifest_sha256': manifest['input_sha256'],
                               'match': match})
        for p in [manifest_path, input_path]:
            hashes[str(p)] = hashlib.sha256(p.read_bytes()).hexdigest()
        with input_path.open(newline='') as handle:
            seeds = list(csv.DictReader(handle))
        if len({s['address'] for s in seeds}) != len(seeds):
            raise ValueError('Duplicate input address')
        for seed in seeds:
            path = directory / (seed['address'] + '.json')
            doc = json.loads(path.read_text())
            if doc['seed'] != seed or doc['history']['address'] != seed['address']:
                raise ValueError('Observation identity mismatch')
            for key in ['start_utc_inclusive', 'end_utc_exclusive']:
                if doc['window'][key] != manifest[key]:
                    raise ValueError('Observation window mismatch')
            bound = (manifest['start_utc_inclusive'], manifest['end_utc_exclusive'])
            if utc(bound[0]) >= utc(bound[1]):
                raise ValueError('Invalid window')
            bounds.add(bound)
            hashes[str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
            observations[seed['address']].append((seed, assess(doc), str(path)))
    if len(bounds) != 1:
        raise ValueError('Cannot combine different windows')
    rows = []
    for address, candidates in sorted(observations.items()):
        if any(c[0] != candidates[0][0] for c in candidates):
            raise ValueError('Conflicting seed evidence across collections')
        complete = [c for c in candidates if c[1]['coverage_complete']]
        if len({c[1]['window_transaction_count'] for c in complete}) > 1:
            raise ValueError('Conflicting complete counts')
        chosen = max(candidates, key=lambda c: (c[1]['eligible'], c[1]['coverage_complete']))
        rows.append(dict(chosen[1], selected_observation=chosen[2]))
    research = [r for r in rows if 'not_research_sample' not in r['exclusion_reasons']]
    eligible = [r for r in research if r['eligible']]
    return {'schema_version': 1, 'status': 'not_ready' if not eligible else 'requires_group_split_review',
            'window': list(next(iter(bounds))), 'input_sha256': hashes,
            'input_identity_checks': input_identity,
            'counts': {'all_addresses': len(rows), 'research_addresses': len(research),
                       'research_complete_windows': sum(r['coverage_complete'] for r in research),
                       'published_storage': dict(Counter(r['published_storage'] for r in research)),
                       'eligible_addresses': len(eligible),
                       'eligible_entities_by_class': {label: sorted({r['entity'] for r in eligible
                           if r['published_storage'] == label}) for label in ['hot', 'cold']}},
            'addresses': rows,
            'limitations': ['Provider count consistency is not cryptographic completeness.',
                'Published storage labels do not establish validity across a later window.',
                'Review dates are not evidence publication or validity dates.',
                'Entity names are source attributions, not independently verified ownership groups.',
                'Eligibility is only an input check; disjoint entity/incident and temporal splits still require review.',
                'No model, performance estimate, hardware label or illicitness label is produced.']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('collections', type=Path, nargs='+')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.collections)
    with args.output.open('x') as handle:
        json.dump(result, handle, indent=2); handle.write('\n')
    print(json.dumps(result['counts']))
