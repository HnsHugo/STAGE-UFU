"""Prepare a fixed missing-prefix unit with explicit fingerprinted page recovery."""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path

BASE = Path(__file__).resolve().parent


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == '.gz' else data)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def choose_sources(resume, view, restored):
    ids = resume['coldcard_unextended_at_16_page_bound_source_ids'][:20]
    assert ids == sorted(set(ids)) and 0 < len(ids) <= 20
    assert ids == restored['next_twenty_source_ids']
    rows = {r['source_id']: r for r in view['rows']}
    assert all(rows[sid]['features'] is None for sid in ids)
    assert set(ids).isdisjoint(resume['source_ids'])
    return ids, rows


def prepare(primary, restoration_report, parent, output, deep_work):
    parent, output = parent.resolve(), output.resolve()
    assert parent.parent == output.parent == BASE and not output.exists()
    work = BASE / ('source_cohort_work_' + output.name)
    assert not work.exists()
    resume = read(parent / 'resume_checkpoint.json')
    view = read(parent / 'precutoff_feature_view.json.gz')
    restored = read(restoration_report)
    assert restored['status'] == 'passed' and restored['all_primary_files_verified'] == 4419
    assert sha(restoration_report) == sha(BASE / 'frontier_cache_restoration_20261112.json')
    assert read(parent / 'independent_verification.json')['status'] == 'passed'
    assert not resume['collection_can_resume'] and not resume['network_source_ids']
    ids, rows = choose_sources(resume, view, restored)
    plan_path = primary / 'coldcard/source_cohort_work_reference_tail_coverage_20261031_221432/plan.json'
    records = {r['pilot_id']: r for r in read(plan_path)}
    registry = [records[sid] for sid in resume['coldcard_unextended_at_16_page_bound_source_ids']]
    for r in registry:
        assert hashlib.sha256(r['address'].encode()).hexdigest() == r['address_sha256']
        assert hashlib.sha256(r['payment_txid'].encode()).hexdigest() == r['payment_txid_sha256']
        for key in ['address_sha256', 'payment_txid_sha256', 'cutoff_height', 'cutoff_block_hash']:
            assert r[key] == rows[r['pilot_id']][key]
    selected = [records[sid] for sid in ids]
    old_scope = BASE / 'reference_tail_continuation_20261101_0653'
    old_requests = read(old_scope / 'request_manifest.json.gz')
    expected = []
    for sid in ids:
        old = {m['key']: m for m in old_requests if m['source_id'] == sid}
        keys = ['reference'] + [f'tail_{i:04d}' for i in range(16)] + ['reference_after']
        assert set(old) == set(keys)
        entry = read(old_scope / 'checkpoint.json.gz')['entries'][sid]
        assert entry['status'] == 'bounded_incomplete' and entry['pages_fetched'] == 16
        assert rows[sid]['precutoff_history_provenance']['raw_sha256'] == entry['raw_sha256']
        for key in keys:
            meta = old[key]
            assert meta['http_status'] == 200 and 'error_type' not in meta
            expected.append({k: meta[k] for k in ['source_id', 'key', 'sha256', 'endpoint_sha256']})
    output.mkdir()
    (output / 'audit_execution.py').write_text('''"""Run the unchanged raw/response auditor for this fixed scope."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / 'source_prefix_extension_20261112_01'))
from audit_execution import audit
if __name__ == '__main__':
    audit(ROOT / 'protocol.json', ROOT.parent / ('source_cohort_work_' + ROOT.name))
''')
    (output / 'verify_execution.py').write_text('''"""Run the independent export verifier against this scope's frozen baseline."""
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / 'source_prefix_extension_20261112_01'))
import verify_execution as verifier
verifier.ROOT = ROOT
if __name__ == '__main__':
    report = verifier.verify()
    (ROOT / 'independent_verification.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\\n')
    print(json.dumps(report, sort_keys=True))
''')
    work.mkdir(mode=0o700)
    for name in ['requests', 'raw', 'results']:
        (work / name).mkdir()
    # Keep the remaining fixed identities in this small private layer for future units.
    write(work / 'remaining_source_registry.json', registry)
    write(work / 'plan.json', selected)
    write(work / 'preflight.json', selected[0])
    locks = set(read(deep_work / 'historical_locks.json'))
    locks.add(str(deep_work / 'collector.lock'))
    locks.update(str(p.parent / 'collector.lock') for p in primary.rglob('plan.json'))
    locks.update(str(p / 'collector.lock') for p in BASE.glob('source_cohort_work_*') if p != work)
    for name in locks:
        Path(name).parent.mkdir(parents=True, exist_ok=True)
    write(work / 'historical_locks.json', sorted(locks))
    write(output / 'expected_recovery_manifest.json', dict(schema_version=1,
        parent_scope=old_scope.name, old_page_bound=16, responses=expected))
    write(output / 'offline_reuse_manifest.json', dict(schema_version=1, responses=[]))
    prior = read(parent / 'protocol.json')
    inputs = {}
    for key, pin in prior['inputs'].items():
        path = (parent / pin['file']).resolve()
        assert sha(path) == pin['sha256']
        inputs['prior_' + key] = dict(file=os.path.relpath(path, output), sha256=pin['sha256'])
    # The reused collector requires this exact key for its eight-control gate.
    inputs['pilot_validation'] = dict(inputs['prior_pilot_validation'])
    pins = dict(baseline_view=parent / 'precutoff_feature_view.json.gz',
        parent_protocol=parent / 'protocol.json', parent_resume=parent / 'resume_checkpoint.json',
        parent_audit=parent / 'coverage_audit.json', parent_verification=parent / 'independent_verification.json',
        parent_backup=parent / 'private_cache_backup.json', parent_deep_queue=parent / 'retained_deep_queue.json',
        restored_identity_report=BASE / 'frontier_cache_restoration_20261112.json',
        original_response_fingerprints=old_scope / 'request_manifest.json.gz',
        original_16_page_checkpoint=old_scope / 'checkpoint.json.gz',
        expected_recovery_manifest=output / 'expected_recovery_manifest.json',
        successor_offline_reuse_manifest=output / 'offline_reuse_manifest.json',
        frontier_preparation_code=Path(__file__), frontier_runner=BASE / 'run_frontier_checkpoint.py',
        frontier_finalizer=BASE / 'finalize_frontier_checkpoint.py',
        frontier_tests=BASE / 'test_frontier_checkpoint.py',
        frontier_audit_entrypoint=output / 'audit_execution.py',
        frontier_verification_entrypoint=output / 'verify_execution.py')
    for key, path in pins.items():
        inputs[key] = dict(file=os.path.relpath(path, output), sha256=sha(path))
    budget = dict(ordinary_counter_gets=1, new_reference_gets_at_most=len(ids),
        new_tail_pages_at_most=32 * len(ids), fresh_reference_statuses_at_most=len(ids),
        funding_status_gets_at_most=sum(r['registry_input_slots'] for r in selected))
    budget['total_new_requests_at_most'] = sum(budget.values())
    available = sum(r['features'] is not None for r in view['rows'])
    report = dict(schema_version=1, scope='offline_fixed_frontier_preparation', selected_source_ids=ids,
        selected_sources=len(ids), saved_responses_reused=0, old_tail_pages_requiring_explicit_recovery=16 * len(ids),
        expected_recovered_response_fingerprints=len(expected), request_budget=budget,
        old_page_recovery_is_network_work_not_added_coverage=True,
        coldcard_vectors_unchanged=available, cryptobilis_vectors_unchanged=329,
        remaining_information_gaps_unchanged=1500 - available + 37,
        retained_deep_queue_preserved=True, remaining_private_identities_preserved=len(registry),
        original_input_pins_verified=len(prior['inputs']), historical_lock_paths=len(locks),
        provider_requests=0, model_fits=0, new_scores=0)
    write(output / 'capacity_and_cache_audit.json', report)
    inputs['frontier_capacity'] = dict(file='capacity_and_cache_audit.json', sha256=sha(output / 'capacity_and_cache_audit.json'))
    protocol = dict(prior, pass_name=output.name, source_ids=ids, created_on='2026-11-12',
        inputs=inputs, parent_scope=parent.name, baseline_vectors=available, max_pages_per_address=32,
        previous_bound=16, previous_requested_page_target=16, per_source_saved_pages={sid: 0 for sid in ids},
        offline_reused_responses=0, request_budget=budget,
        private_plan_sha256=sha(work / 'plan.json'), private_lock_manifest_sha256=sha(work / 'historical_locks.json'),
        private_remaining_registry_sha256=sha(work / 'remaining_source_registry.json'),
        authorization='Hugo requests resumption on 12 November 2026; current alignment fixes the next twenty previously unselected Coldcard IDs.',
        coverage_scope='Recover the missing original 16-page bodies against their published fingerprints, then extend these fixed source/reference pairs through 32 pages. Preserve the three retained 576-page histories and every unselected row.',
        recovery_old_page_bound=16, recovery_body_mismatch_policy='Stop before extending a mismatched source; never accept changed old bodies as added coverage.',
        network_entrypoint='../run_frontier_checkpoint.py', finalization_entrypoint='../finalize_frontier_checkpoint.py')
    write(output / 'protocol.json', protocol)
    write(output / 'resume_checkpoint.json', dict(schema_version=1, pass_name=output.name,
        status='prepared_offline_not_started', source_ids=ids, network_source_ids=ids,
        finalized_source_ids=[], collection_can_resume=False, restart_same_scope_allowed=False,
        protocol_sha256=sha(output / 'protocol.json'), provider_requests=0, model_fits=0,
        automation_enabled=False, requires_fresh_live_lease_locks_counter=True))
    # Validate the real prepared scope before a collector is ever started.
    for pin in inputs.values():
        assert sha((output / pin['file']).resolve()) == pin['sha256']
    write(output / 'preparation_verification.json', dict(status='passed', input_pins_verified=len(inputs),
        frozen_source_identities_verified=len(registry), recovery_fingerprints_pinned=len(expected),
        selected_sources=len(ids), provider_requests=0, model_fits=0,
        protocol_sha256=sha(output / 'protocol.json')))
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['primary', 'restoration_report', 'parent', 'output', 'deep_work']:
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    print(json.dumps(prepare(args.primary, args.restoration_report, args.parent, args.output, args.deep_work), sort_keys=True))
