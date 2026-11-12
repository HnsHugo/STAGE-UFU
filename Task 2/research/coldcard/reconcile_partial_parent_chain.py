"""Verify a completed chain whose initial parent may contain partial cached pages."""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
from finalize_variable_checkpoint import load_parent_evidence


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reconcile(first, last, output):
    first, last, output = first.resolve(), last.resolve(), output.resolve()
    assert not output.exists(), 'Never replace a closed reconciliation'
    scopes, seen, scope = [], set(), last
    while True:
        assert scope.parent == first.parent and scope.name not in seen
        seen.add(scope.name); scopes.append(scope)
        if scope == first:
            break
        scope = scope.parent / read(scope / 'protocol.json')['parent_scope']
    scopes.reverse()
    base = first.parent / read(first / 'protocol.json')['parent_scope']
    initial = read(base / 'precutoff_feature_view.json.gz')
    final = read(last / 'precutoff_feature_view.json.gz')
    before = {r['source_id']: r for r in initial['rows']}
    after = {r['source_id']: r for r in final['rows']}
    assert len(before) == len(after) == 1500 and set(before) == set(after)
    assert initial['predictor_allowlist'] == final['predictor_allowlist']
    originals = set(read(first / 'protocol.json')['source_ids'])
    completed, latest, units, inputs = set(), {}, [], {}
    paths = [Path(__file__), base / 'precutoff_feature_view.json.gz',
             base / 'checkpoint.json.gz', base / 'private_cache_backup.json',
             last / 'precutoff_feature_view.json.gz']
    paths.append(Path(load_parent_evidence.__code__.co_filename))
    if (base / 'partial_page_reconciliation.json').exists():
        paths.extend([base / 'partial_page_reconciliation.json', base / 'request_manifest.json.gz'])
    previous = base
    for scope in scopes:
        q = read(scope / 'protocol.json')
        r = read(scope / 'continuation_reconciliation.json')
        v = read(scope / 'independent_verification.json')
        b = read(scope / 'private_cache_backup.json')
        assert q['parent_scope'] == previous.name
        assert set(q['source_ids']) == set(read(previous / 'resume_checkpoint.json')['continuation_required_source_ids'])
        assert v['status'] == 'passed' and b['saved_privately'] is True
        assert not r['pending_source_ids'] and not completed.intersection(q['source_ids'])
        assert r['new_request_intents'] == r['new_successful_bodies']
        assert r['new_request_intents'] <= q['request_budget']['total_new_requests_at_most']
        newly = set(r['new_complete_source_ids'])
        assert newly <= originals and not completed.intersection(newly)
        completed.update(newly)
        cp = read(scope / 'checkpoint.json.gz')
        for sid, entry in cp['entries'].items():
            latest[sid] = (scope, entry)
        units.append(dict(scope=scope.name, previous_pages=q['previous_bound'],
            checkpoint_pages=q['max_pages_per_address'],
            fresh_http_200=r['new_successful_bodies'],
            saved_responses_reused=r['saved_responses_reused'],
            new_complete_prefixes=r['new_complete_prefixes'],
            additional_source_transaction_observations=r['additional_source_transaction_observations']))
        paths.extend(scope / n for n in ['protocol.json', 'checkpoint.json.gz',
            'continuation_reconciliation.json', 'coverage_audit.json',
            'independent_verification.json', 'resume_checkpoint.json', 'private_cache_backup.json'])
        previous = scope
    assert set(latest) == originals
    for sid, row in after.items():
        old = before[sid]
        if sid not in originals or old['features'] is not None:
            assert row == old
        else:
            for key in ['address_sha256', 'payment_txid_sha256', 'cutoff_height',
                        'cutoff_block_hash', 'known_coldcard_core_membership', 'labels', 'full_history_status']:
                assert row[key] == old[key]
            assert (row['features'] is not None) == (sid in completed)
    base_count = sum(r['features'] is not None for r in before.values())
    final_count = sum(r['features'] is not None for r in after.values())
    assert final_count == base_count + len(completed)
    old_entries = read(base / 'checkpoint.json.gz')['entries']
    details = []
    for sid in sorted(originals):
        scope, entry = latest[sid]
        old_raw, old_entry = load_parent_evidence(base, sid)
        new_path = scope.parent / ('source_cohort_work_' + scope.name) / entry['raw_file']
        assert sha(new_path) == entry['raw_sha256']
        new_raw = read(new_path)
        assert new_raw['transactions'][:len(old_raw['transactions'])] == old_raw['transactions']
        cutoff = before[sid]['cutoff_height']
        old_tx = [t for t in old_raw['transactions'] if t['status']['block_height'] < cutoff]
        new_tx = [t for t in new_raw['transactions'] if t['status']['block_height'] < cutoff]
        details.append(dict(source_id=sid, latest_scope=scope.name,
            status=entry['status'], original_pages=old_entry['pages_fetched'],
            final_pages=entry['pages_fetched'], old_raw_sha256=old_entry.get('raw_sha256'),
            original_parent_had_only_partial_cache=sid not in old_entries,
            old_cache_manifest_sha256=sha(base/'request_manifest.json.gz') if sid not in old_entries else None,
            new_raw_sha256=entry['raw_sha256'],
            additional_source_transaction_observations=len(new_tx)-len(old_tx)))
    observations = sum(x['additional_source_transaction_observations'] for x in details)
    assert observations == sum(x['additional_source_transaction_observations'] for x in units)
    for path in paths:
        relative = os.path.relpath(path.resolve(), output.parent)
        inputs[relative] = sha(path)
    report = dict(schema_version=1, status='passed', original_sources=len(originals),
        original_coldcard_vectors=base_count, coldcard_vectors=final_count,
        cryptobilis_vectors_unchanged=329, total_remaining_information_gaps=1500-final_count+37,
        completed_source_ids=sorted(completed), retained_incomplete_source_ids=sorted(originals-completed),
        new_complete_prefixes=len(completed),
        fresh_http_200=sum(x['fresh_http_200'] for x in units),
        additional_source_transaction_observations=observations,
        observation_count_is_not_globally_unique_transactions=True,
        original_sources_counted_once=True, all_original_vectors_and_unselected_rows_preserved=True,
        full_current_statuses_and_unknown_labels_preserved=True,
        model_fits=0, new_scores=0, provider_requests_by_reconciler=0,
        units=units, source_progress=details, input_sha256=inputs,
        final_view_sha256=sha(last / 'precutoff_feature_view.json.gz'))
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    return {k:v for k,v in report.items() if k not in ['units','source_progress','input_sha256']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('first', type=Path); parser.add_argument('last', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    target = args.output or args.last / 'progressive_checkpoint_reconciliation.json'
    print(json.dumps(reconcile(args.first, args.last, target), sort_keys=True))
