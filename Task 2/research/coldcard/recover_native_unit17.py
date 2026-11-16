"""Recover saved unit-17 traffic and finish its frozen three-source unit in a distinct scope.

Original markers remain immutable. The unresolved page counts against the
original fifty-attempt cap; only 2 further pages are reserved for comparison_0522.
No saved page is requested again. The two completed histories only get fresh reference checks; all 879 cached pages are preserved.
"""
import argparse
from contextlib import ExitStack, redirect_stdout
from copy import deepcopy
from datetime import datetime, timezone
import fcntl
import gzip
import hashlib
import importlib.util
import os
from pathlib import Path
import shutil

from build_source_registry import json_bytes
from prepare_frontier_checkpoint import read, sha, write
from native_extension_checkpoint import request_budget
import recorded_remaining_campaign as campaign
import recorded_mempool_resume as recorded

BASE = campaign.BASE
OLD = 'mempool_remaining_fifty_20261116_unit_17'
NEW = OLD + '_recovery_20261116'
UNKNOWN = ('comparison_0522', 'tail_0291')


def clocks(markers):
    fresh = [m for m in markers if not m.get('offline_reused')]
    complete = [m for m in fresh if m.get('http_status') == 200]
    unknown = [m for m in fresh if m.get('http_status') != 200]
    assert len(complete) == 152 and len(unknown) == 1
    marker = unknown[0]
    assert (marker['source_id'], marker['key']) == UNKNOWN
    assert not any(k in marker for k in ['sha256', 'http_status', 'error_type',
        'finished_at', 'dispatch_at', 'dispatch_clock_evidence', 'dispatch_not_attempted'])
    assert all(m['finished_at'] <= marker['started_at'] for m in complete)
    clock = recorded.verify_dispatch_evidence(complete)
    return dict(status='incomplete_unknown_intent', known_successful_dispatches=clock,
        unresolved_intents=1, original_marker_unchanged=True, unknown_outcome_not_imputed=True)


def close():
    out, work = BASE / OLD, BASE / ('source_cohort_work_' + OLD)
    assert not (out / 'run_receipt.json').exists()
    policy = read(campaign.POLICY); q = read(out / 'protocol.json')
    assert policy['collector_lease']['owner'] == OLD
    assert policy['collector_lease']['protocol_sha256'] == sha(out / 'protocol.json')
    for pin in q['inputs'].values():
        assert sha((out / pin['file']).resolve()) == pin['sha256']
    locks = set(read(work / 'historical_locks.json')) | {str(work / 'collector.lock')}
    with ExitStack() as stack:
        for path in sorted(locks):
            handle = stack.enter_context(Path(path).open('a+'))
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        paths = sorted(work.glob('requests/*/*.json'))
        markers = [read(p) for p in paths]; clock = clocks(markers)
        for path, marker in zip(paths, markers):
            body = path.with_suffix('.json.gz')
            if marker.get('http_status') == 200:
                assert sha(body) == marker['sha256']
            else:
                assert not body.exists()
        from collect_reference_tail import export
        export(out / 'protocol.json', out, work)
        proof = dict(status='passed', scope=OLD, recovered_at=datetime.now(timezone.utc).isoformat(),
            recovery_code_sha256=sha(Path(__file__)), original_protocol_sha256=sha(out / 'protocol.json'),
            original_request_markers=[dict(file=str(p.relative_to(work)), sha256=sha(p)) for p in paths],
            http200=152, failed_provider_responses=0, unresolved_request_intents=1,
            original_full_clock_audit='incomplete_unknown_intent', dispatch_verification=clock,
            operational_locks_checked_free=len(locks), restart_same_scope_allowed=False,
            new_provider_requests_during_recovery=0, model_fits=0, new_scores=0)
        write(out / 'interruption_recovery.json', proof)
        write(work / 'interruption_recovery.json', proof)
        write(out / 'run_receipt.json', dict(status='interrupted_unknown_outcome',
            receipt_origin='Offline recovery, original runner did not produce a receipt',
            provider_requests=153, http200=152, failures=0, unresolved_intents=1,
            finalized_sources=2, operational_locks_released=True,
            blockstream_provider_requests=0, model_fits=0, new_scores=0))
        write(out / 'dispatch_verification.json', clock)
        import audit_independent_mempool_resume as auditor
        with (work / 'audit.log').open('w') as log, redirect_stdout(log):
            auditor.audit(out / 'protocol.json', work)
        for name in ['coverage_audit.json', 'independent_verification.json']:
            report = read(out / name)
            report.update(original_full_clock_audit='incomplete_unknown_intent',
                known_successful_dispatches=clock['known_successful_dispatches'],
                unresolved_request_intents=1, original_request_markers_preserved=True,
                verification_basis='Original immutable native endpoint/cursor/body replay; timing verified for 152 completed responses only; final intent remains unknown.')
            write(out / name, report)
        assert read(out / 'checkpoint.json.gz')['entries'].keys() == {'comparison_0391','comparison_0433'}
        cursor = read(work / 'native_cursors.json')
        assert cursor['comparison_0391']['saved_native_pages'] == 294
        assert cursor['comparison_0433']['saved_native_pages'] == 294
        assert cursor['comparison_0522']['saved_native_pages'] == 291
        policy['collector_lease'].update(state='idle', owner=None, last_owner=OLD,
            expires_at=None, finished_at=datetime.now(timezone.utc).isoformat(),
            operational_locks_released=True, stop_status='interrupted_unknown_outcome')
        policy.update(active_collection_scope='none', coverage_collection_paused=True,
            latest_status='native_unit17_interruption_saved_bytes_recovered')
        gate = policy['provider_access_policies'][campaign.PROVIDER]
        gate.update(status='interruption_closed_unknown_outcome', no_new_probe_authorized=False,
            operational_validation_required=False, next_network_attempt_not_before=policy['collector_lease']['finished_at'])
        write(campaign.POLICY, policy); (work / 'lease_published').unlink(missing_ok=True)
        state = read(campaign.CAMPAIGN / 'progress.json')
        assert state['active_scope'] == OLD and state['next_unit'] == 17
        state.update(active_scope=None, status='interrupted_unit_awaiting_distinct_recovery')
        state.setdefault('interrupted_evidence_fragments', []).append(dict(scope=OLD,
            unit=17, http200=152, unresolved_intents=1, new_native_pages=147,
            recovery_scope=NEW, private_evidence_saved=False))
        write(campaign.CAMPAIGN / 'progress.json', state)
        write(out / 'collection_stop.json', dict(status='interrupted_unknown_outcome',
            operational_locks_released=True, restart_same_scope_allowed=False,
            required_successor=NEW, automation_enabled=False))
    (out / 'RESULTS.md').write_text('# Native interruption recovered offline\n\n'
        '152 successful responses and 147 new pages preserved. Two histories reached their caps; the third has 47 successful new pages and one unresolved page intent. '
        'Data replay passes; the original full clock audit remains incomplete. No request during recovery. The consumed scope is closed. '
        'The distinct successor reuses all saved pages and reserves at most 2 further pages for the unfinished source, counting its unknown intent against the original cap.\n')
    return dict(scope=OLD, http200=152, unresolved_intents=1, provider_requests_during_recovery=0)


def prepare():
    old, source = BASE / OLD, BASE / ('source_cohort_work_' + OLD)
    assert read(old / 'private_cache_backup.json')['saved_privately']
    assert read(old / 'independent_verification.json')['status'] == 'passed'
    assert read(campaign.POLICY)['collector_lease']['state'] == 'idle'
    out, work = BASE / NEW, BASE / ('source_cohort_work_' + NEW)
    assert not out.exists() and not work.exists()
    out.mkdir(); work.mkdir(mode=0o700)
    for name in ['requests', 'raw', 'results']: (work / name).mkdir()
    for name in ['plan.json', 'remaining_source_registry.json', 'retained_bridge_native_cursors.json']:
        shutil.copyfile(source / name, work / name)
    records = read(work / 'plan.json'); pins = []
    cursors = read(source / 'native_cursors.json')
    for record in records:
        sid = record['pilot_id']; folder = work / 'requests' / sid; folder.mkdir()
        for key in ['reference'] + [f'tail_{i:04d}' for i in range(cursors[sid]['saved_native_pages'])]:
            marker = source / 'requests' / sid / (key + '.json'); meta = read(marker)
            body = marker.with_suffix('.json.gz'); assert meta['http_status'] == 200 and sha(body) == meta['sha256']
            shutil.copyfile(body, folder / body.name)
            pin = {k: meta[k] for k in ['source_id', 'key', 'provider', 'endpoint_sha256', 'sha256']}
            pin.update(origin_scope=OLD, original_marker_sha256=sha(marker)); pins.append(pin)
            write(folder / marker.name, dict(meta, offline_reused=True, reused_from_pass=OLD,
                original_marker_sha256=sha(marker)))
        from independent_mempool_resume import cached_prefix
        cached_prefix(record, work, [p for p in pins if p['source_id'] == sid])
    locks = set(read(source / 'historical_locks.json')) | {str(p / 'collector.lock')
        for p in BASE.glob('source_cohort_work_*') if p != work}
    write(work / 'historical_locks.json', sorted(locks)); write(work / 'parent_native_cursors.json', cursors)
    write(out / 'offline_reuse_manifest.json', dict(responses=pins, native_cached_bodies_reused=len(pins)))
    shutil.copyfile(old / 'legacy_reuse_manifest.json', out / 'legacy_reuse_manifest.json')
    shutil.copyfile(old / 'retained_deep_queue.json', out / 'retained_deep_queue.json')
    state = read(campaign.CAMPAIGN / 'progress.json')
    state.update(status='prepared_unit', active_scope=NEW)
    state['interrupted_evidence_fragments'][-1]['private_evidence_saved'] = True
    write(campaign.CAMPAIGN / 'progress.json', state); write(out / 'prepared_campaign_state.json', state)
    q = deepcopy(read(old / 'protocol.json'))
    for pin in q['inputs'].values():
        path = (old / pin['file']).resolve()
        if path.is_relative_to(old): path = out / path.relative_to(old)
        pin.update(file=os.path.relpath(path, out), sha256=sha(path))
    for key, path in [('interruption_recovery', old / 'interruption_recovery.json'),
        ('recovered_native_audit', old / 'independent_verification.json'),
        ('recovered_native_backup', old / 'private_cache_backup.json'),
        ('recovery_driver', Path(__file__))]:
        q['inputs'][key] = dict(file=os.path.relpath(path, out), sha256=sha(path))
    budget = request_budget(records, extra_pages=0)
    budget['tail_pages_at_most'] = 2; budget['total_new_requests_at_most'] = sum(v for k,v in budget.items() if k != 'total_new_requests_at_most')
    q.update(pass_name=NEW, prepared_at=datetime.now(timezone.utc).isoformat(),
        authorization='User: Continue ce chat. Reuse every verified page; preserve original unknown outcomes; finish the frozen unit in a distinct scope.',
        maximum_requests=budget['total_new_requests_at_most'], request_budget=budget,
        per_source_max_pages={'comparison_0391':294,'comparison_0433':294,'comparison_0522':293},
        per_source_new_page_caps={'comparison_0391':0,'comparison_0433':0,'comparison_0522':2},
        original_successful_new_pages={'comparison_0391':50,'comparison_0433':50,'comparison_0522':47},
        original_unknown_page_intents={'comparison_0391':0,'comparison_0433':0,'comparison_0522':1},
        offline_native_pages_reused=879, private_plan_sha256=sha(work / 'plan.json'),
        private_lock_manifest_sha256=sha(work / 'historical_locks.json'),
        private_parent_native_cursors_sha256=sha(work / 'parent_native_cursors.json'))
    write(out / 'protocol.json', q)
    write(out / 'preparation_verification.json', dict(status='passed', cached_native_pages=879,
        cached_bodies_verified=len(pins), new_native_page_budget=2, original_unknown_intent_preserved=True,
        original_fifty_attempt_cap_preserved=True, provider_requests=0))
    return dict(scope=NEW, maximum_requests=q['maximum_requests'], new_native_pages=2)


def run():
    import independent_mempool_resume as native
    original = native.collect
    def bounded(record, requests, work, q, pins):
        return original(record, requests, work,
            dict(q, max_pages_per_address=q['per_source_max_pages'][record['pilot_id']]), pins)
    native.collect = bounded
    recorded.run(BASE / NEW / 'protocol.json', BASE / ('source_cohort_work_' + NEW))


def finish():
    out = BASE / NEW; q = read(out / 'protocol.json')
    manifest = read(out / 'request_manifest.json.gz')
    for sid, cap in q['per_source_new_page_caps'].items():
        fresh = [m for m in manifest if not m.get('offline_reused') and m['source_id'] == sid and m['key'].startswith('tail_')]
        assert len(fresh) <= cap
        assert len(fresh) + q['original_successful_new_pages'][sid] + q['original_unknown_page_intents'][sid] <= 50
    result = campaign.finish(NEW)
    write(out / 'original_cap_verification.json', dict(status='passed',
        cached_native_pages_preserved=879, old_unknown_intents_preserved=1,
        saved_pages_requested_again=0, maximum_fifty_new_page_intents_per_original_source=True))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['close', 'prepare', 'run', 'finish'])
    print(__import__('json').dumps(globals()[parser.parse_args().command](), indent=2))
