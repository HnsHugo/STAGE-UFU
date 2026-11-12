"""Prepare the next frozen frontier unit from a saved, fingerprinted private registry."""
import argparse
import hashlib
import os
from pathlib import Path

from prepare_frontier_checkpoint import read, sha, write

BASE = Path(__file__).resolve().parent


def choose_next(resume, view, registry):
    remaining = resume['coldcard_unextended_at_16_page_bound_source_ids']
    assert remaining == sorted(set(remaining))
    ids = remaining[:20]
    assert 0 < len(ids) <= 20 and ids == resume['next_extension_source_ids']
    assert set(ids).isdisjoint(resume['source_ids'])
    rows = {r['source_id']: r for r in view['rows']}
    records = {r['pilot_id']: r for r in registry}
    assert len(records) == len(registry)
    assert set(remaining) <= set(records)
    for sid in remaining:
        record, row = records[sid], rows[sid]
        assert row['features'] is None
        assert hashlib.sha256(record['address'].encode()).hexdigest() == record['address_sha256']
        assert hashlib.sha256(record['payment_txid'].encode()).hexdigest() == record['payment_txid_sha256']
        for key in ['address_sha256', 'payment_txid_sha256', 'cutoff_height', 'cutoff_block_hash']:
            assert record[key] == row[key]
    return ids, rows, [records[sid] for sid in ids]


def inherited_inputs(prior, parent, output):
    inputs = {}
    for key, pin in prior['inputs'].items():
        path = (parent / pin['file']).resolve()
        assert sha(path) == pin['sha256']
        inputs['prior_' + key] = dict(file=os.path.relpath(path, output), sha256=pin['sha256'])
    inputs['pilot_validation'] = dict(inputs['prior_pilot_validation'])
    return inputs


def prepare(parent, output):
    parent, output = parent.resolve(), output.resolve()
    assert parent.parent == output.parent == BASE and not output.exists()
    parent_work = BASE / ('source_cohort_work_' + parent.name)
    work = BASE / ('source_cohort_work_' + output.name)
    assert not work.exists()
    prior = read(parent / 'protocol.json')
    resume = read(parent / 'resume_checkpoint.json')
    view = read(parent / 'precutoff_feature_view.json.gz')
    assert not resume['collection_can_resume'] and not resume['network_source_ids']
    assert read(parent / 'independent_verification.json')['status'] == 'passed'
    assert read(parent / 'private_cache_backup.json')['saved_privately']
    assert read(parent / 'run_receipt.json')['operational_locks_released']
    registry_path = parent_work / 'remaining_source_registry.json'
    assert sha(registry_path) == prior['private_remaining_registry_sha256']
    registry = read(registry_path)
    ids, rows, selected = choose_next(resume, view, registry)
    inputs = inherited_inputs(prior, parent, output)
    expected = []
    origins = {}
    for sid in ids:
        origin = BASE / rows[sid]['precutoff_history_provenance']['pass_name']
        cp = read(origin / 'checkpoint.json.gz')['entries'][sid]
        assert cp['status'] == 'bounded_incomplete' and cp['pages_fetched'] == 16
        assert cp['raw_sha256'] == rows[sid]['precutoff_history_provenance']['raw_sha256']
        old = {m['key']: m for m in read(origin / 'request_manifest.json.gz') if m['source_id'] == sid}
        keys = ['reference'] + [f'tail_{i:04d}' for i in range(16)] + ['reference_after']
        assert set(old) == set(keys)
        for key in keys:
            assert old[key]['http_status'] == 200 and 'error_type' not in old[key]
            expected.append({k: old[key][k] for k in ['source_id', 'key', 'sha256', 'endpoint_sha256']})
        origins[sid] = origin.name
        for name in ['checkpoint.json.gz', 'request_manifest.json.gz']:
            path = origin / name
            inputs['origin_' + origin.name + '_' + name.replace('.', '_')] = dict(file=os.path.relpath(path, output), sha256=sha(path))
    output.mkdir()
    work.mkdir(mode=0o700)
    for name in ['requests', 'raw', 'results']:
        (work / name).mkdir()
    for name in ['audit_execution.py', 'verify_execution.py']:
        (output / name).write_bytes((parent / name).read_bytes())
    (work / 'remaining_source_registry.json').write_bytes(registry_path.read_bytes())
    write(work / 'plan.json', selected)
    write(work / 'preflight.json', selected[0])
    locks = set(read(parent_work / 'historical_locks.json')) | {str(parent_work / 'collector.lock')}
    locks.update(str(p / 'collector.lock') for p in BASE.glob('source_cohort_work_*') if p != work)
    for name in locks:
        Path(name).parent.mkdir(parents=True, exist_ok=True)
    write(work / 'historical_locks.json', sorted(locks))
    write(output / 'expected_recovery_manifest.json', dict(schema_version=1, old_page_bound=16,
        source_origin_scopes=origins, responses=expected))
    write(output / 'offline_reuse_manifest.json', dict(schema_version=1, responses=[]))
    write(output / 'retained_parent_queues.json', dict(schema_version=1,
        parent_scope=parent.name, parent_resume_sha256=sha(parent / 'resume_checkpoint.json'),
        parent_continuation_queue=resume['continuation_queue'],
        parent_retained_deep_queue=read(parent / 'retained_deep_queue.json'),
        all_preceding_unavailable_source_ids=resume['coldcard_remaining_bounded_source_ids'],
        all_preceding_queues_preserved=True))
    budget = dict(ordinary_counter_gets=1, new_reference_gets_at_most=len(ids),
        new_tail_pages_at_most=32 * len(ids), fresh_reference_statuses_at_most=len(ids),
        funding_status_gets_at_most=sum(r['registry_input_slots'] for r in selected))
    budget['total_new_requests_at_most'] = sum(budget.values())
    available = sum(row['features'] is not None for row in view['rows'])
    report = dict(schema_version=1, scope='offline_next_fixed_frontier_preparation', selected_source_ids=ids,
        selected_sources=len(ids), saved_responses_reused=0, old_tail_pages_requiring_explicit_recovery=16 * len(ids),
        expected_recovered_response_fingerprints=len(expected), request_budget=budget,
        old_page_recovery_is_network_work_not_added_coverage=True, coldcard_vectors_unchanged=available,
        cryptobilis_vectors_unchanged=329, remaining_information_gaps_unchanged=1500 - available + 37,
        retained_deep_queue_preserved=True, retained_parent_queues_preserved=True,
        remaining_private_identities_preserved=len(registry), private_registry_fingerprint_verified=True,
        original_input_pins_verified=len(prior['inputs']), historical_lock_paths=len(locks),
        provider_requests=0, model_fits=0, new_scores=0, large_archive_retrieval_required=False)
    write(output / 'capacity_and_cache_audit.json', report)
    pins = dict(baseline_view=parent / 'precutoff_feature_view.json.gz',
        parent_protocol=parent / 'protocol.json', parent_resume=parent / 'resume_checkpoint.json',
        parent_checkpoint=parent / 'checkpoint.json.gz', parent_audit=parent / 'coverage_audit.json',
        parent_verification=parent / 'independent_verification.json', parent_backup=parent / 'private_cache_backup.json',
        parent_reconciliation=parent / 'continuation_reconciliation.json', parent_deep_queue=parent / 'retained_deep_queue.json',
        expected_recovery_manifest=output / 'expected_recovery_manifest.json',
        successor_offline_reuse_manifest=output / 'offline_reuse_manifest.json', frontier_capacity=output / 'capacity_and_cache_audit.json',
        retained_parent_queues=output / 'retained_parent_queues.json', frontier_preparation_code=Path(__file__),
        frontier_preparation_tests=BASE / 'test_next_frontier_checkpoint.py',
        frontier_audit_entrypoint=output / 'audit_execution.py', frontier_verification_entrypoint=output / 'verify_execution.py',
        frontier_runner=BASE / 'run_frontier_checkpoint.py', frontier_finalizer=BASE / 'finalize_frontier_checkpoint.py')
    for key, path in pins.items():
        inputs[key] = dict(file=os.path.relpath(path, output), sha256=sha(path))
    protocol = dict(prior, pass_name=output.name, source_ids=ids, created_on='2026-11-12',
        inputs=inputs, parent_scope=parent.name, baseline_vectors=available, max_pages_per_address=32,
        all_gap_targets=dict(coldcard=1500 - available, cryptobilis=37, total=1500 - available + 37),
        previous_bound=16, previous_requested_page_target=16, per_source_saved_pages={sid: 0 for sid in ids},
        offline_reused_responses=0, request_budget=budget,
        private_plan_sha256=sha(work / 'plan.json'), private_lock_manifest_sha256=sha(work / 'historical_locks.json'),
        private_remaining_registry_sha256=sha(work / 'remaining_source_registry.json'),
        authorization='Hugo explicitly approved publication and requests the next fixed twenty-source unit with Go on 12 November 2026.',
        coverage_scope='Next untouched source/reference pairs in frozen registry order. Recover missing old bodies against their pinned fingerprints, extend through 32 pages, and preserve every prior queue, vector, cutoff and unknown label.')
    write(output / 'protocol.json', protocol)
    write(output / 'resume_checkpoint.json', dict(schema_version=1, pass_name=output.name,
        status='prepared_offline_not_started', source_ids=ids, network_source_ids=ids, finalized_source_ids=[],
        collection_can_resume=False, restart_same_scope_allowed=False, protocol_sha256=sha(output / 'protocol.json'),
        provider_requests=0, model_fits=0, automation_enabled=False, requires_fresh_live_lease_locks_counter=True))
    for pin in inputs.values():
        assert sha((output / pin['file']).resolve()) == pin['sha256']
    old_pairs = {(str((parent / pin['file']).resolve()), pin['sha256']) for pin in prior['inputs'].values()}
    new_pairs = {(str((output / pin['file']).resolve()), pin['sha256']) for pin in inputs.values()}
    assert old_pairs <= new_pairs
    write(output / 'preparation_verification.json', dict(status='passed', input_pins_verified=len(inputs),
        ancestor_file_hash_pairs_preserved=True, frozen_source_identities_verified=len(registry),
        recovery_fingerprints_pinned=len(expected), selected_sources=len(ids), provider_requests=0,
        model_fits=0, protocol_sha256=sha(output / 'protocol.json')))
    return report


if __name__ == '__main__':
    import json
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('parent', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    print(json.dumps(prepare(args.parent, args.output), sort_keys=True))
