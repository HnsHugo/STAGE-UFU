"""Prepare a distinct successor when a workspace and an expired lease were lost.

This command issues no HTTP, does not recreate consumed flags, and never assumes
that an unsaved request did not happen. Only pinned successful native pages are
reused. The ordinary collector still requires fresh locks and published lease.
"""
import argparse
from contextlib import ExitStack
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import fcntl
import hashlib
from pathlib import Path

from independent_mempool_resume import cached_prefix
from prepare_frontier_checkpoint import read, sha, write

BASE = Path(__file__).resolve().parent
OLD = 'mempool_fifty_20261112_tail_native_five_20261113'
PARENT = 'mempool_fifty_20261112_tail_native_pair_20261113'
NEW = 'mempool_fifty_20261112_tail_native_five_recovery_20261114'
PROVIDER = 'https://mempool.space/api'


def require_expired(lease, now, timeout):
    if lease['state'] != 'running' or lease['owner'] != OLD:
        raise ValueError('Expected the unchanged interrupted lease')
    if now <= datetime.fromisoformat(lease['expires_at']) + timedelta(seconds=timeout):
        raise ValueError('Lease or a bounded in-flight response could still be live')


def prepare(evidence, archives):
    old, parent, out = (BASE / n for n in [OLD, PARENT, NEW])
    work = BASE / ('source_cohort_work_' + NEW)
    policy_path = BASE / 'comparison_access_retries_20261030/retry_policy.json'
    policy = read(policy_path)
    q = read(old / 'protocol.json')
    now = datetime.now(timezone.utc)
    require_expired(policy['collector_lease'], now, q['timeout_seconds'])
    assert policy['active_collection_scope'] == OLD
    assert not out.exists() and not work.exists()
    assert not (old / 'run_receipt.json').exists()
    assert read(parent / 'independent_verification.json')['status'] == 'passed'
    assert read(parent / 'private_cache_backup.json')['saved_privately']
    gate = policy['provider_access_policies'][PROVIDER].get('next_network_attempt_not_before')
    assert gate is None or now >= datetime.fromisoformat(gate)
    for pin in q['inputs'].values():
        assert sha((old / pin['file']).resolve()) == pin['sha256']
    # Check actual archive bytes against the previously published saved hashes.
    for name in [PARENT, 'independent_provider_native_20261112_02', 'independent_provider_native_20261112_03']:
        backup = read(BASE / name / 'private_cache_backup.json')
        archive = archives / backup['file_name']
        assert archive.stat().st_size == backup['bytes'] and sha(archive) == backup['sha256']
    prior = evidence / ('source_cohort_work_' + PARENT)
    registry = read(prior / 'remaining_source_registry.json')
    records = [{r['pilot_id']: r for r in registry}[sid] for sid in q['source_ids']]
    progress = read(BASE / 'mempool_fifty_20261112/progress.json')
    assert q['source_ids'] == progress['pending_source_ids']
    baseline = read(parent / 'precutoff_feature_view.json.gz')
    rows = {r['source_id']: r for r in baseline['rows']}
    assert sum(r['features'] is not None for r in rows.values()) == q['baseline_vectors'] == 1427
    for r in records:
        row = rows[r['pilot_id']]
        assert row['features'] is None
        for key in ['address_sha256', 'payment_txid_sha256', 'cutoff_height', 'cutoff_block_hash']:
            assert r[key] == row[key]
        assert hashlib.sha256(r['address'].encode()).hexdigest() == r['address_sha256']
        assert hashlib.sha256(r['payment_txid'].encode()).hexdigest() == r['payment_txid_sha256']
    locks = set(read(prior / 'historical_locks.json'))
    locks.update(str(p / 'collector.lock') for p in BASE.glob('source_cohort_work_*'))
    locks.add(str(BASE / ('source_cohort_work_' + OLD) / 'collector.lock'))
    locks.add(str(work / 'collector.lock'))
    for name in locks:
        Path(name).parent.mkdir(parents=True, exist_ok=True)
    with ExitStack() as stack:
        for name in sorted(locks):
            lock = stack.enter_context(Path(name).open('a+'))
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        # Guard against a concurrent local policy change during verification.
        assert read(policy_path) == policy
        work.mkdir(exist_ok=True, mode=0o700)
        for n in ['requests', 'raw', 'results']:
            (work / n).mkdir()
        write(work / 'plan.json', records)
        assert sha(work / 'plan.json') == q['private_plan_sha256']
        for name in ['remaining_source_registry.json', 'retained_bridge_native_cursors.json']:
            (work / name).write_bytes((prior / name).read_bytes())
        (work / 'parent_native_cursors.json').write_bytes((prior / 'native_cursors.json').read_bytes())
        write(work / 'historical_locks.json', sorted(locks - {str(work / 'collector.lock')}))
        reuse = read(old / 'offline_reuse_manifest.json')
        for pin in reuse['responses']:
            source = evidence / ('source_cohort_work_' + pin['origin_scope']) / 'requests' / pin['source_id']
            marker = source / (pin['key'] + '.json')
            body = source / (pin['key'] + '.json.gz')
            meta = read(marker)
            assert sha(marker) == pin['original_marker_sha256']
            assert meta.get('http_status') == 200 and 'error_type' not in meta
            for key in ['source_id', 'key', 'provider', 'endpoint_sha256', 'sha256']:
                assert meta[key] == pin[key]
            assert sha(body) == pin['sha256']
            dest = work / 'requests' / pin['source_id']
            dest.mkdir(exist_ok=True)
            (dest / body.name).write_bytes(body.read_bytes())
            write(dest / marker.name, dict(meta, offline_reused=True,
                  reused_from_pass=pin['origin_scope'], original_marker_sha256=sha(marker)))
        for record in records:
            pins = [p for p in reuse['responses'] if p['source_id'] == record['pilot_id']]
            anchor, pages, cursor, seen, height, terminal = cached_prefix(record, work, pins)
            assert len(pages) == 32 and not terminal
        out.mkdir()
        (out / 'offline_reuse_manifest.json').write_bytes((old / 'offline_reuse_manifest.json').read_bytes())
        (out / 'retained_deep_queue.json').write_bytes((parent / 'retained_deep_queue.json').read_bytes())
        write(old / 'interruption_receipt.json', dict(schema_version=1, observed_at=now.isoformat(),
            scope=OLD, status='closed_after_workspace_loss', original_lease=policy['collector_lease'],
            original_request_count=None, original_http200=None, original_failures=None,
            original_request_outcomes='unknown_not_recoverable_from_saved_artifacts',
            original_operational_flags_reconstructed=False, restart_same_scope_allowed=False,
            recovered_new_vectors=0, baseline_vectors_preserved=1427,
            offline_closure_provider_requests=0, all_historical_and_local_locks_acquired=True,
            no_inflight_request_after_expiry_and_declared_timeout=True,
            distinct_successor=NEW,
            limitation='No missing response is counted as success, failure, or proof that no request happened.'))
        newq = deepcopy(q)
        newq.update(pass_name=NEW, created_on='2026-11-14',
            authorization='Current user request resumes the final five frozen IDs after the expired interrupted workspace; distinct successor, no old-scope restart.',
            interrupted_predecessor=OLD, private_lock_manifest_sha256=sha(work / 'historical_locks.json'),
            focused_tests_previously_passed=20)
        newq['inputs'].update(
            interrupted_prepared_protocol=dict(file='../' + OLD + '/protocol.json', sha256=sha(old / 'protocol.json')),
            interrupted_scope_closure=dict(file='../' + OLD + '/interruption_receipt.json', sha256=sha(old / 'interruption_receipt.json')),
            expired_lease_recovery_preparer=dict(file='../' + Path(__file__).name, sha256=sha(Path(__file__))))
        write(out / 'protocol.json', newq)
        for pin in newq['inputs'].values():
            assert sha((out / pin['file']).resolve()) == pin['sha256']
        write(out / 'preparation_verification.json', dict(status='passed', selected=5,
            frozen_identities_verified=5, input_pins_verified=len(newq['inputs']),
            baseline_vectors=1427, native_pages_reused=160, successful_responses_reused=165,
            provider_requests=0, tests_previously_passed=20,
            unknown_interrupted_outcomes_not_classified=True, old_scope_not_restarted=True))
        (out / 'README.md').write_text('''# Final five frozen sources: workspace-loss recovery\n\nThe final five source/reference pairs of the original fifty-source campaign are\nunchanged. The expired 13 November lease has an explicit interruption record;\nits unsaved request counts and outcomes remain unknown. No old operational flag\nwas recreated and the old scope cannot restart.\n\nThe three required archives match their published hashes. Reuse 160 verified\nnative pages and five references. Extend each source by at most sixteen pages,\nwith fresh before/after reference anchors and funding closure if exhausted.\nOne worker, five-second dispatch spacing, a 45-second timeout and at most 95\nnew requests remain unchanged. Require fresh locks and published lease/readback.\nStop at the first failure, refusal or inconsistency; no automatic retry.\n\nThe unit is the frozen source/reference pair. The target remains operational\nincident membership; theft/device labels stay unknown. The fourteen predictors\nuse only transactions before the reference block. No split, fitting, scoring,\npaid service or automation is introduced. Preserve all 1,427 complete vectors,\nall 73 missing rows, CryptoBilis and every deep-history/native-cursor queue.\n''')
        policy['collector_lease'].update(state='idle', owner=None, last_owner=OLD, expires_at=None,
            finished_at=now.isoformat(), stop_status='expired_workspace_loss_unknown_outcomes',
            operational_locks_released=True)
        policy.update(active_collection_scope='none', coverage_collection_paused=True,
            latest_status='final_five_distinct_recovery_prepared', automation_enabled=False,
            coverage_pause_reason='Expired interrupted scope closed offline. Distinct successor awaits fresh locks and exact published lease/readback.')
        write(policy_path, policy)
    return dict(scope=NEW, selected=5, old_vectors_preserved=1427, cached_pages_verified=160,
                provider_requests=0, maximum_new_requests=newq['maximum_requests'])


if __name__ == '__main__':
    import json
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('evidence', type=Path)
    p.add_argument('archives', type=Path)
    a = p.parse_args()
    print(json.dumps(prepare(a.evidence.resolve(), a.archives.resolve()), sort_keys=True))
