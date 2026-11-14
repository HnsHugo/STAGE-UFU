"""Prepare/close a bounded native extension without reopening a closed campaign.

The existing guarded collector and independent auditor remain unchanged. Direct
parent fingerprints retain the immutable lineage without flattening every old
protocol into progressively longer ancestor keys.
"""
import argparse
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
import os
from pathlib import Path

from independent_mempool_resume import cached_prefix
from prepare_frontier_checkpoint import read, sha, write

BASE = Path(__file__).resolve().parent
PARENT = 'mempool_fifty_20261112_tail_native_five_recovery_20261114'
POLICY = BASE / 'comparison_access_retries_20261030/retry_policy.json'
PROVIDER = 'https://mempool.space/api'


def choose_sources(resume, rows, bound=48, limit=5):
    candidates = [x['source_id'] for x in resume['retained_native_partial_queue']
                  if x.get('seed_kind') == 'native' and x['native_pages'] == bound
                  and x['source_id'] in rows and rows[x['source_id']]['features'] is None]
    if len(candidates) != len(set(candidates)):
        raise ValueError('Repeated native source in retained queue')
    return sorted(candidates)[:limit]


def request_budget(records, extra_pages=16):
    n = len(records)
    budget = dict(before_statuses_at_most=n, tail_pages_at_most=n*extra_pages,
                  after_anchor_statuses_at_most=n,
                  funding_statuses_at_most=sum(r['registry_input_slots'] for r in records))
    budget['total_new_requests_at_most'] = sum(budget.values())
    return budget


def prepare(evidence, scope):
    parent = BASE / PARENT
    out, work = BASE / scope, BASE / ('source_cohort_work_' + scope)
    assert not out.exists() and not work.exists()
    policy = read(POLICY)
    assert policy['collector_lease']['state'] == 'idle' and policy['active_collection_scope'] == 'none'
    gate = policy['provider_access_policies'][PROVIDER].get('next_network_attempt_not_before')
    assert gate is None or datetime.now(timezone.utc) >= datetime.fromisoformat(gate)
    assert read(parent / 'independent_verification.json')['status'] == 'passed'
    assert read(parent / 'private_cache_backup.json')['saved_privately']
    baseline = read(parent / 'precutoff_feature_view.json.gz')
    rows = {r['source_id']: r for r in baseline['rows']}
    resume = read(parent / 'resume_checkpoint.json')
    ids = choose_sources(resume, rows)
    assert len(ids) == 5 and sum(r['features'] is not None for r in rows.values()) == 1429
    prior_work = evidence / ('source_cohort_work_' + PARENT)
    registry = read(prior_work / 'remaining_source_registry.json')
    by_id = {r['pilot_id']: r for r in registry}
    records = [by_id[s] for s in ids]
    out.mkdir(); work.mkdir(mode=0o700)
    for name in ['requests', 'raw', 'results']:
        (work / name).mkdir()
    write(work / 'plan.json', records)
    for name in ['remaining_source_registry.json', 'retained_bridge_native_cursors.json']:
        (work / name).write_bytes((prior_work / name).read_bytes())
    reuse, seeds, cursors, origins, locks = [], [], {}, set(), set()
    queue = {r['source_id']: r for r in resume['retained_native_partial_queue']}
    for record in records:
        sid = record['pilot_id']; row = rows[sid]
        for key in ['address_sha256', 'payment_txid_sha256', 'cutoff_height', 'cutoff_block_hash']:
            assert record[key] == row[key]
        assert hashlib.sha256(record['address'].encode()).hexdigest() == record['address_sha256']
        assert hashlib.sha256(record['payment_txid'].encode()).hexdigest() == record['payment_txid_sha256']
        origin_name = row['precutoff_history_provenance']['pass_name']
        origin = BASE / origin_name; source = evidence / ('source_cohort_work_' + origin_name)
        assert read(origin / 'independent_verification.json')['status'] == 'passed'
        assert read(origin / 'private_cache_backup.json')['saved_privately']
        entry = read(origin / 'checkpoint.json.gz')['entries'][sid]
        assert entry['status'] == 'bounded_incomplete' and entry['features'] is None and entry['pages_fetched'] == 48
        assert sha(source / entry['raw_file']) == entry['raw_sha256'] == row['precutoff_history_provenance']['raw_sha256']
        old_raw = read(source / entry['raw_file'])
        dest = work / 'requests' / sid; dest.mkdir()
        for key in ['reference'] + [f'tail_{i:04d}' for i in range(48)]:
            marker = source / 'requests' / sid / (key + '.json'); body = marker.with_suffix('.json.gz')
            meta = read(marker)
            assert meta.get('http_status') == 200 and 'error_type' not in meta and meta['provider'] == PROVIDER
            assert sha(body) == meta['sha256']
            (dest / body.name).write_bytes(body.read_bytes())
            pin = {k: meta[k] for k in ['source_id', 'key', 'sha256', 'endpoint_sha256', 'provider']}
            pin.update(origin_scope=origin_name, original_marker_sha256=sha(marker)); reuse.append(pin)
            write(dest / marker.name, dict(meta, offline_reused=True, reused_from_pass=origin_name,
                  original_marker_sha256=sha(marker)))
        anchor, pages, cursor, seen, height, terminal = cached_prefix(record, work, [r for r in reuse if r['source_id'] == sid])
        assert len(pages) == 48 and not terminal and [t for p in pages for t in p] == old_raw['transactions']
        cursor_hash = hashlib.sha256(cursor.encode()).hexdigest()
        assert cursor_hash == queue[sid]['last_native_cursor_sha256']
        cursors[sid] = dict(provider=PROVIDER, cursor=cursor, saved_native_pages=48, pagination_exhausted=False, finalized=True)
        seeds.append(dict(source_id=sid, origin_scope=origin_name, saved_pages=48,
                          raw_sha256=entry['raw_sha256'], last_native_cursor_sha256=cursor_hash))
        locks.update(read(source / 'historical_locks.json')); origins.add(origin_name)
    write(work / 'parent_native_cursors.json', cursors)
    locks.update(str(p / 'collector.lock') for p in BASE.glob('source_cohort_work_*') if p != work)
    for name in locks:
        Path(name).parent.mkdir(parents=True, exist_ok=True)
    write(work / 'historical_locks.json', sorted(locks))
    write(out / 'offline_reuse_manifest.json', dict(schema_version=1, responses=reuse, native_cached_bodies_reused=len(reuse)))
    write(out / 'seed_manifest.json', dict(schema_version=1, sources=seeds))
    (out / 'retained_deep_queue.json').write_bytes((parent / 'retained_deep_queue.json').read_bytes())
    inputs = dict(baseline_view=parent / 'precutoff_feature_view.json.gz',
                  parent_resume=parent / 'resume_checkpoint.json', parent_protocol=parent / 'protocol.json',
                  parent_audit=parent / 'independent_verification.json', parent_backup=parent / 'private_cache_backup.json',
                  parent_deep_queue=parent / 'retained_deep_queue.json',
                  closed_campaign_progress=BASE / 'mempool_fifty_20261112/progress.json',
                  closed_campaign_selection=BASE / 'mempool_fifty_20261112/selection.json',
                  offline_reuse=out / 'offline_reuse_manifest.json', seed_manifest=out / 'seed_manifest.json',
                  checkpoint_code=Path(__file__).resolve())
    for origin in sorted(origins):
        for name in ['protocol.json', 'checkpoint.json.gz', 'request_manifest.json.gz', 'independent_verification.json', 'private_cache_backup.json']:
            inputs[origin + '_' + name.replace('.', '_')] = BASE / origin / name
    for name in ['independent_mempool_resume.py', 'independent_mempool_native.py', 'resume_mempool_slow_response.py',
                 'audit_independent_mempool_resume.py', 'independent_mempool_pilot.py', 'comparison_http.py', 'collect_reference_tail.py']:
        inputs[name.replace('.', '_')] = BASE / name
    budget = request_budget(records)
    q = dict(schema_version=5, pass_name=scope, created_on='2026-11-14', parent_scope=PARENT,
        authorization='Current user instruction Tu peux faire la suite; publication permission from 14 November remains in force.',
        unit='Frozen source/reference pair', target='Operational incident membership, not proven theft/device use',
        predictors='The unchanged fourteen predictors strictly before the reference block',
        provider=PROVIDER, source_ids=ids, baseline_vectors=1429, previous_bound=48, max_pages_per_address=64,
        maximum_new_native_pages=16, maximum_requests=budget['total_new_requests_at_most'], request_budget=budget,
        requests_per_second=.2, minimum_dispatch_interval_seconds=5, timeout_seconds=45, workers=1,
        offline_successful_responses_reused=len(reuse), offline_native_pages_reused=240,
        live_policy_file='../comparison_access_retries_20261030/retry_policy.json',
        blockstream_cooldown_preserved_until=policy['provider_access_policies']['https://blockstream.info/api']['next_network_attempt_not_before'],
        private_plan_sha256=sha(work / 'plan.json'), private_lock_manifest_sha256=sha(work / 'historical_locks.json'),
        private_identity_registry_sha256=sha(work / 'remaining_source_registry.json'),
        private_retained_bridge_native_cursors_sha256=sha(work / 'retained_bridge_native_cursors.json'),
        private_parent_native_cursors_sha256=sha(work / 'parent_native_cursors.json'),
        lineage_policy='Direct parent fingerprints preserve the immutable transitive lineage; no flattened ancestor-key duplication.',
        stop_policy='Stop at first failure/refusal/inconsistency. No automatic retry or provider/account/IP/proxy/TLS rotation.',
        automation_enabled=False, model_fits=0, new_scores=0,
        inputs={k: dict(file=os.path.relpath(p, out), sha256=sha(p)) for k, p in sorted(inputs.items())})
    write(out / 'protocol.json', q)
    write(out / 'preparation_verification.json', dict(status='passed', selected=5, baseline_vectors=1429,
        reused_pages_verified=240, successful_responses_verified=len(reuse), input_pins_verified=len(inputs),
        provider_requests=0, old_completed_campaign_not_reopened=True))
    (out / 'README.md').write_text('''# Native historical-prefix extension — 14 November 2026

This distinct unit extends the first five remaining pure-native 48-page sources,
ordered by source ID, to at most 64 pages each. Reuse all 240 verified old pages;
request at most sixteen new pages per source. The completed fifty-source campaign
and every older outcome remain immutable. Baseline: 1,429/1,500 complete vectors.

The unit is the same frozen source/reference pair; the target is operational
incident membership. Theft and hardware-device labels stay unknown. The fourteen
predictors use only earlier blocks. No model, split, score or threshold change.

Require fresh locks and exact published lease/readback. One worker, five-second
spacing, a 45-second timeout and the same Mempool route/TLS are retained. Stop at
the first failure, refusal or inconsistency. No paid service or automatic schedule.
Only exhaustion, fresh before/after reference anchors and funding closure can
promote a vector. Preserve all missing rows, native cursors and deep histories.
''')
    return dict(scope=scope, sources=ids, reused_pages=240, maximum_requests=q['maximum_requests'], input_pins=len(inputs))


def finalize(scope):
    out = BASE / scope; work = BASE / ('source_cohort_work_' + scope)
    q, a, receipt = (read(out / n) for n in ['protocol.json', 'coverage_audit.json', 'run_receipt.json'])
    assert a['status'] == read(out / 'independent_verification.json')['status'] == 'passed'
    assert receipt['operational_locks_released'] and receipt['blockstream_provider_requests'] == 0
    assert not (out / 'resume_checkpoint.json').exists()
    for pin in q['inputs'].values():
        assert sha((out / pin['file']).resolve()) == pin['sha256']
    parent = read(BASE / q['parent_scope'] / 'resume_checkpoint.json')
    entries = read(out / 'checkpoint.json.gz')['entries']; cursors = read(work / 'native_cursors.json')
    assert set(entries) <= set(q['source_ids'])
    queue = {r['source_id']: deepcopy(r) for r in parent['retained_native_partial_queue']}
    for sid in q['source_ids']:
        if sid in entries and entries[sid]['features'] is not None:
            queue.pop(sid, None)
        else:
            cur = cursors[sid]
            queue[sid] = dict(source_id=sid, provider=PROVIDER, seed_kind='native',
                native_pages=cur['saved_native_pages'], saved_evidence_pages=cur['saved_native_pages'],
                last_native_cursor_sha256=hashlib.sha256(cur['cursor'].encode()).hexdigest(),
                evidence_scope=scope, finalized=sid in entries, requires_distinct_pinned_successor=True)
    view = read(out / 'precutoff_feature_view.json.gz'); missing = [r['source_id'] for r in view['rows'] if r['features'] is None]
    assert a['available_coldcard_vectors'] == q['baseline_vectors'] + a['new_complete_prefixes'] == 1500-len(missing)
    pending = [s for s in q['source_ids'] if s not in entries]
    action = 'Use a distinct pinned continuation for retained incomplete sources, reusing saved pages and actual native cursors. Preserve all old vectors, unknown labels, cutoffs, full-current statuses and native/deep queues. Do not restart consumed scopes. Recheck overlap before model work.'
    resume = dict(schema_version=7, pass_name=scope, status='closed_verified_checkpoint', source_ids=q['source_ids'],
        finalized_source_ids=list(entries), new_complete_source_ids=a['new_complete_source_ids'], pending_source_ids=pending,
        coldcard_vectors_available=a['available_coldcard_vectors'], coldcard_remaining_bounded_source_ids=missing,
        coldcard_unextended_at_16_page_bound_source_ids=parent['coldcard_unextended_at_16_page_bound_source_ids'],
        retained_native_partial_queue=list(queue.values()), retained_deep_queue_file='retained_deep_queue.json',
        private_native_cursors_sha256=sha(work / 'native_cursors.json'),
        private_identity_registry_sha256=sha(work / 'remaining_source_registry.json'),
        private_retained_bridge_native_cursors_sha256=sha(work / 'retained_bridge_native_cursors.json'),
        cryptobilis_vectors_available=329, all_bounded_prefixes=len(missing)+37,
        blockstream_cooldown_preserved_until=q['blockstream_cooldown_preserved_until'],
        closed_fifty_source_campaign_preserved=True, collection_can_resume=False, restart_same_scope_allowed=False,
        next_action=action, automation_enabled=False, model_fits=0, new_scores=0)
    write(out / 'resume_checkpoint.json', resume)
    policy = read(POLICY); assert policy['collector_lease']['owner'] == scope
    now = datetime.now(timezone.utc)
    policy['collector_lease'].update(state='idle', owner=None, last_owner=scope, expires_at=None,
        finished_at=now.isoformat(), operational_locks_released=True, stop_status=receipt['status'])
    policy.update(active_collection_scope='none', coverage_collection_paused=True, automation_enabled=False,
        latest_status='native_extension_closed_audit_passed', latest_consolidated_prefix_view=scope+'/precutoff_feature_view.json.gz',
        latest_prefix_output=scope, latest_prefix_protocol=scope+'/protocol.json', latest_prefix_work=work.name,
        latest_prefix_result_file=scope+'/coverage_audit.json', latest_prefix_coverage_audit=scope+'/coverage_audit.json',
        latest_prefix_resume_file=scope+'/resume_checkpoint.json', latest_prefix_resume_checkpoint=scope+'/resume_checkpoint.json',
        latest_prefix_stop_file=scope+'/collection_stop.json', comparison_pre_cutoff_predictors_available=a['available_coldcard_vectors']-500,
        comparison_pre_cutoff_predictors_unavailable=len(missing), prefix_bounded_incomplete_sources=len(missing),
        prefix_network_pending_sources=len(pending), latest_pass_pending_sources=len(pending), next_coverage_action=action,
        coverage_pause_reason='Finite native extension closed and audited; preserve all actual cursors. No automatic restart.')
    gate = policy['provider_access_policies'][PROVIDER]
    gate.update(status='closed_audited', last_http200=receipt['http200'], next_network_attempt_not_before=None)
    failures = [m for m in read(out / 'request_manifest.json.gz') if not m.get('offline_reused') and 'error_type' in m]
    if failures:
        delay = max(7200, 2*gate.get('last_retry_delay_seconds', 0))
        due = now + timedelta(seconds=delay)
        for m in failures:
            if m.get('retry_after'):
                from email.utils import parsedate_to_datetime
                try: server = now + timedelta(seconds=int(m['retry_after']))
                except ValueError: server = parsedate_to_datetime(m['retry_after'])
                due = max(due, server)
        gate.update(status='stopped_after_first_failure', next_network_attempt_not_before=due.isoformat(),
                    last_retry_delay_seconds=delay, no_new_probe_authorized=any(m.get('http_status') == 403 for m in failures))
    write(POLICY, policy)
    write(out / 'collection_stop.json', dict(status=receipt['status'], operational_locks_released=True,
        automation_enabled=False, restart_same_scope_allowed=False, blockstream_requests=0))
    write(out / 'execution_verification.json', dict(status='passed', old_vectors_preserved=1429,
        input_pins_verified=len(q['inputs']), new_vectors_independently_recounted=a['new_complete_prefixes'],
        native_cursors_preserved=True, closed_campaign_files_unchanged=True, retained_deep_queue_unchanged=True,
        model_fits=0, new_scores=0))
    return dict(finalized=len(entries), pending=len(pending), new_vectors=a['new_complete_prefixes'], vectors=a['available_coldcard_vectors'])


if __name__ == '__main__':
    import json
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('command', choices=['prepare', 'finalize'])
    p.add_argument('scope'); p.add_argument('--evidence', type=Path)
    args = p.parse_args()
    result = prepare(args.evidence.resolve(), args.scope) if args.command == 'prepare' else finalize(args.scope)
    print(json.dumps(result, sort_keys=True))
