"""A distinct twenty-history continuation, prioritizing smaller saved histories."""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path
import shutil
import tempfile

import recorded_twenty_campaign as inherited
import recorded_legacy_compat as compatibility
from prepare_frontier_checkpoint import read, sha, write
from independent_mempool_pilot import PROVIDER, legacy_source
from independent_mempool_bridge import choose_bridge
from native_extension_checkpoint import request_budget

BASE = inherited.BASE
CAMPAIGN = BASE / 'mempool_recorded_priority_20261116'
POLICY = inherited.POLICY
inherited.CAMPAIGN = CAMPAIGN


def build_units(candidates, count=20):
    ordered = sorted(candidates, key=lambda r: (r['historical_full_current_counter'], r['source_id']))
    assert len({r['source_id'] for r in ordered}) == len(ordered) >= count
    chosen = ordered[:count]
    groups = {}
    for item in chosen:
        groups.setdefault((item['kind'], item['previous_bound']), []).append(item['source_id'])
    units = []
    for (kind, bound), ids in groups.items():
        units.extend(dict(kind=kind, previous_bound=bound, source_ids=ids[i:i+3])
                     for i in range(0, len(ids), 3))
    return chosen, units


def initialize():
    assert not CAMPAIGN.exists()
    policy = read(POLICY)
    assert policy['collector_lease']['state'] == 'idle'
    parent = (BASE / policy['latest_consolidated_prefix_view']).parent
    assert read(parent / 'private_cache_backup.json')['saved_privately']
    rows = {r['source_id']: r for r in read(parent / 'precutoff_feature_view.json.gz')['rows']}
    queue = {r['source_id']: r for r in read(parent / 'resume_checkpoint.json')['retained_native_partial_queue']}
    work = BASE / ('source_cohort_work_' + parent.name)
    records = {r['pilot_id']: r for r in read(work / 'remaining_source_registry.json')}
    counters = {r['source_id']: r['tx_count'] for r in read(BASE / 'source_comparison_feasibility_20261102_1603/group_evidence.json.gz')['full_current_history_counter_evidence']}
    eligible, excluded = [], []
    with tempfile.TemporaryDirectory() as temporary:
        legacy_work = Path(temporary)
        (legacy_work / 'legacy').symlink_to(BASE / 'source_cohort_work_source_prefix_extension_20261112_02/requests', target_is_directory=True)
        for sid, row in rows.items():
            if row['features'] is not None:
                continue
            try:
                origin, source = inherited.evidence_for(row)
                if not source.exists():
                    raise ValueError('Saved evidence layer not restored locally; retained without traffic')
                entry = read(origin / 'checkpoint.json.gz')['entries'][sid]
                assert sha(source / entry['raw_file']) == entry['raw_sha256'] == row['precutoff_history_provenance']['raw_sha256']
                if sid in queue and queue[sid]['seed_kind'] == 'native':
                    kind, bound = 'native', queue[sid]['native_pages']
                elif sid in queue and queue[sid]['seed_kind'] == 'bridge_union':
                    raw = read(source / entry['raw_file'])
                    cur = read(source / 'native_cursors.json')[sid]
                    cursor_tx = next(t for t in raw['transactions'] if t['txid'] == cur['cursor'])
                    assert raw['partial_boundary_height'] > cursor_tx['status']['block_height']
                    assert hashlib.sha256(cur['cursor'].encode()).hexdigest() == queue[sid]['last_native_cursor_sha256']
                    kind, bound = 'mixed_resume', raw['pages_fetched']
                elif origin.name == 'source_prefix_extension_20261112_02':
                    pins = {p.stem: read(p) for p in (source / 'requests' / sid).glob('*.json')
                            if p.stem == 'reference' or p.stem.startswith('tail_')}
                    a, pages, tx, _ = legacy_source(records[sid], legacy_work, pins)
                    choose_bridge(records[sid], a, tx)
                    kind, bound = 'legacy_bridge', len(pages)
                else:
                    raise ValueError('Different verified successor needed; retained without traffic')
                eligible.append(dict(source_id=sid, kind=kind, previous_bound=bound,
                    historical_full_current_counter=counters[sid], origin_scope=origin.name))
            except (AssertionError, ValueError, FileNotFoundError) as error:
                excluded.append(dict(source_id=sid, reason=str(error) or type(error).__name__))
    chosen, units = build_units(eligible)
    ids = sum((u['source_ids'] for u in units), [])
    CAMPAIGN.mkdir()
    authorization = 'User: Continue. Persistent explicit GitHub/Mempool authorization and fifty-new-page bound; next twenty distinct histories with per-unit saves.'
    selection = dict(schema_version=1, created_on='2026-11-16', source_ids=ids, requested_sources=20,
        units=units, chosen_candidates=chosen, original_parent=parent.name,
        original_vectors=sum(r['features'] is not None for r in rows.values()),
        authorization=authorization, additional_native_pages_per_source=50, maximum_unit_sources=3,
        selection_rule='Twenty smallest historical full-current counters among currently cache-verifiable eligible missing histories, grouped by acquisition kind and saved evidence bound. This is operational scheduling, not a cohort, label or predictor change.',
        counter_limitation='Old full-current counters are scheduling diagnostics, not exact remaining pre-reference work or scientific predictors.',
        unit='Frozen source/reference pair', target='Operational incident membership; theft and hardware-use labels remain unknown',
        predictors='Unchanged fourteen predictors strictly before the reference block',
        model_fits=0, new_scores=0, automation_enabled=False)
    write(CAMPAIGN / 'selection.json', selection)
    write(CAMPAIGN / 'eligibility_preflight.json', dict(status='passed', eligible=eligible,
        excluded_but_retained=excluded, all_missing_source_ids=[s for s,r in rows.items() if r['features'] is None],
        fresh_provider_requests=0))
    write(CAMPAIGN / 'progress.json', dict(status='planned', source_ids=ids, pending_source_ids=ids,
        finalized_source_ids=[], new_complete_source_ids=[], completed_units=[], active_scope=None,
        next_unit=1, can_continue=True, available_vectors=selection['original_vectors'], automation_enabled=False))
    shutil.copyfile(BASE / 'mempool_recorded_twenty_20261115/compatibility_tests_20261116.json', CAMPAIGN / 'compatibility_tests_20261116.json')
    (CAMPAIGN / 'README.md').write_text('# Twenty prioritized saved histories\n\nThe twenty frozen source/reference pairs are selected only for operational scheduling among the unchanged 1,500-row cohort. Old full-current transaction counters do not measure the exact remaining historical work. Mixed histories resume from their actual native cursor only after verifying that it has crossed the partial legacy block; preserve the entire saved union and separate native/evidence counts. Legacy bridges retain the funding-closure eligibility check. Four noneligible restored histories and all unavailable/deep layers stay retained for distinct successors.\n\nAt most fifty new native pages per source, three sources per unit, one worker, recorded 5.25-second UTC/monotonic spacing and 45-second timeout on the unchanged route/TLS. Audit, privately save and publish each checkpoint. Stop on first actual failure/refusal/inconsistency. No model, label promotion, repeated saved pages, rotation or background schedule.\n')
    return dict(source_ids=ids, units=units, excluded=len(excluded), baseline_vectors=selection['original_vectors'])


def code_pins(out, q):
    files = ['recorded_priority_campaign.py', 'recorded_mixed_resume.py', 'audit_recorded_mixed_resume.py',
             'resume_fifty_bridge.py', 'independent_mempool_native.py']
    for name in files:
        path = BASE / name
        q['inputs']['priority_' + name.replace('.', '_')] = dict(file=os.path.relpath(path, out), sha256=sha(path))
    q['prepared_at'] = datetime.now(timezone.utc).isoformat()
    write(out / 'protocol.json', q)


def prepare(number):
    selection = read(CAMPAIGN / 'selection.json')
    unit = selection['units'][number-1]
    if unit['kind'] != 'mixed_resume':
        result = compatibility.prepare(number) if unit['kind'] == 'legacy_bridge' else inherited.prepare(number)
        out = BASE / result['scope']
        q = read(out / 'protocol.json')
        q['created_on'] = '2026-11-16'
        code_pins(out, q)
        return result
    state = read(CAMPAIGN / 'progress.json')
    assert state['can_continue'] and state['next_unit'] == number and state['active_scope'] is None
    assert all(u['private_evidence_saved'] for u in state['completed_units'])
    policy = read(POLICY)
    assert policy['collector_lease']['state'] == 'idle' and policy['active_collection_scope'] == 'none'
    gate = policy['provider_access_policies'][PROVIDER]
    assert not gate.get('approval_required') and not gate.get('no_new_probe_authorized')
    due = gate.get('next_network_attempt_not_before')
    assert due is None or datetime.now(timezone.utc) >= datetime.fromisoformat(due)
    parent = (BASE / policy['latest_consolidated_prefix_view']).parent
    assert read(parent / 'private_cache_backup.json')['saved_privately']
    assert read(parent / 'independent_verification.json')['status'] == 'passed'
    oldwork = BASE / ('source_cohort_work_' + parent.name)
    rows = {r['source_id']: r for r in read(parent / 'precutoff_feature_view.json.gz')['rows']}
    queue = {r['source_id']: r for r in read(parent / 'resume_checkpoint.json')['retained_native_partial_queue']}
    ids = unit['source_ids']
    assert set(ids) <= set(state['pending_source_ids']) and all(rows[s]['features'] is None for s in ids)
    scope = f'{CAMPAIGN.name}_unit_{number:02d}'
    out, work = BASE / scope, BASE / ('source_cohort_work_' + scope)
    assert not out.exists() and not work.exists()
    out.mkdir(); work.mkdir(mode=0o700)
    for name in ['requests', 'raw', 'results', 'seeds']:
        (work / name).mkdir()
    registry = {r['pilot_id']: r for r in read(oldwork / 'remaining_source_registry.json')}
    records = [registry[s] for s in ids]
    write(work / 'plan.json', records)
    for name in ['remaining_source_registry.json', 'retained_bridge_native_cursors.json']:
        shutil.copyfile(oldwork / name, work / name)
    locks = set(read(oldwork / 'historical_locks.json'))
    index, cursors, origins = {}, {}, set()
    for record in records:
        sid = record['pilot_id']; row = rows[sid]
        for key in ['address_sha256', 'payment_txid_sha256', 'cutoff_height', 'cutoff_block_hash']:
            assert row[key] == record[key]
        assert hashlib.sha256(record['address'].encode()).hexdigest() == record['address_sha256']
        assert hashlib.sha256(record['payment_txid'].encode()).hexdigest() == record['payment_txid_sha256']
        origin, source = inherited.evidence_for(row); origins.add(origin.name)
        entry = read(origin / 'checkpoint.json.gz')['entries'][sid]
        assert sha(source / entry['raw_file']) == entry['raw_sha256'] == row['precutoff_history_provenance']['raw_sha256']
        current = read(source / 'native_cursors.json')[sid]
        assert hashlib.sha256(current['cursor'].encode()).hexdigest() == queue[sid]['last_native_cursor_sha256']
        folder = work / 'seeds' / sid; folder.mkdir()
        shutil.copyfile(source / entry['raw_file'], folder / 'seed_raw.json.gz')
        write(folder / 'bridge_seed.json', dict(raw_file='seed_raw.json.gz', raw_sha256=entry['raw_sha256'], native_cursor=current['cursor']))
        index[sid] = dict(spec_sha256=sha(folder / 'bridge_seed.json'), native_cursor_sha256=queue[sid]['last_native_cursor_sha256'])
        cursors[sid] = current
        locks.update(read(source / 'historical_locks.json'))
    locks.update(str(p / 'collector.lock') for p in BASE.glob('source_cohort_work_*') if p != work)
    for name in locks:
        Path(name).parent.mkdir(parents=True, exist_ok=True)
    write(work / 'historical_locks.json', sorted(locks))
    write(work / 'parent_native_cursors.json', cursors)
    write(work / 'bridge_seed_index.json', index)
    write(out / 'offline_reuse_manifest.json', dict(responses=[], native_cached_bodies_reused=0))
    write(out / 'legacy_reuse_manifest.json', dict(responses=[]))
    write(out / 'mixed_seed_manifest.json', dict(status='passed', seeds=index, raw_sha256={s: read(work / 'seeds' / s / 'bridge_seed.json')['raw_sha256'] for s in ids}))
    shutil.copyfile(parent / 'retained_deep_queue.json', out / 'retained_deep_queue.json')
    state.update(status='prepared_unit', active_scope=scope)
    write(CAMPAIGN / 'progress.json', state); write(out / 'prepared_campaign_state.json', state)
    paths = dict(baseline_view=parent/'precutoff_feature_view.json.gz', parent_resume=parent/'resume_checkpoint.json',
        parent_protocol=parent/'protocol.json', parent_verification=parent/'independent_verification.json',
        parent_private_backup=parent/'private_cache_backup.json', campaign_selection=CAMPAIGN/'selection.json',
        prepared_campaign_state=out/'prepared_campaign_state.json', tests=CAMPAIGN/'preflight_tests.json',
        recorded_dispatch_runner=BASE/'recorded_mempool_resume.py', native_collector=BASE/'independent_mempool_resume.py',
        offline_reuse=out/'offline_reuse_manifest.json', mixed_seeds=out/'mixed_seed_manifest.json',
        identifier_authorization=BASE/'mempool_identifier_authorization_20261114.json')
    for name in sorted(origins):
        for file in ['protocol.json', 'checkpoint.json.gz', 'private_cache_backup.json']:
            paths[name + '_' + file.replace('.', '_')] = BASE/name/file
    budget = request_budget(records, extra_pages=50)
    q = dict(schema_version=9, pass_name=scope, campaign=CAMPAIGN.name, campaign_unit=number, kind='mixed_resume',
        parent_scope=parent.name, created_on='2026-11-16', authorization=selection['authorization'], source_ids=ids, provider=PROVIDER,
        baseline_vectors=sum(r['features'] is not None for r in rows.values()), previous_bound=unit['previous_bound'],
        max_pages_per_address=unit['previous_bound']+50, maximum_new_native_pages=50, new_provider_page_limit=50,
        maximum_requests=budget['total_new_requests_at_most'], request_budget=budget,
        requests_per_second=.2, minimum_dispatch_interval_seconds=5, enforced_dispatch_spacing_seconds=5.25,
        dispatch_clock_evidence='monotonic_ns_and_utc', workers=1, timeout_seconds=45, offline_native_pages_reused=0,
        private_plan_sha256=sha(work/'plan.json'), private_lock_manifest_sha256=sha(work/'historical_locks.json'),
        private_identity_registry_sha256=sha(work/'remaining_source_registry.json'),
        private_retained_bridge_native_cursors_sha256=sha(work/'retained_bridge_native_cursors.json'),
        private_parent_native_cursors_sha256=sha(work/'parent_native_cursors.json'),
        private_bridge_seed_index_sha256=sha(work/'bridge_seed_index.json'),
        blockstream_cooldown_preserved_until=policy['provider_access_policies']['https://blockstream.info/api']['next_network_attempt_not_before'],
        live_policy_file='../comparison_access_retries_20261030/retry_policy.json', inputs=inherited.pins(paths,out),
        original_timing_failure_preserved=True, model_fits=0, new_scores=0, automation_enabled=False)
    code_pins(out,q)
    from recorded_mixed_resume import seed
    for record in records:
        seed(record,work,q)
    write(out/'preparation_verification.json',dict(status='passed',source_ids=ids,
        mixed_seeds_verified=len(ids),input_pins_verified=len(q['inputs']),provider_requests=0))
    return dict(scope=scope,sources=ids,kind=q['kind'],maximum_requests=q['maximum_requests'])


def run(scope):
    q=read(BASE/scope/'protocol.json')
    if q['kind'] != 'mixed_resume':
        return inherited.run(scope)
    import independent_mempool_resume as native
    import recorded_mempool_resume as recorded
    from recorded_mixed_resume import collect
    native.collect=collect
    recorded.run(BASE/scope/'protocol.json',BASE/('source_cohort_work_'+scope))


def finish(scope):
    out=BASE/scope;work=BASE/('source_cohort_work_'+scope);q=read(out/'protocol.json')
    if q['kind'] != 'mixed_resume':
        result=inherited.finish(scope)
    else:
        from audit_recorded_mixed_resume import audit
        from recorded_mempool_resume import verify_dispatch_evidence
        assert read(CAMPAIGN/'progress.json')==read(out/'prepared_campaign_state.json')
        write(out/'dispatch_verification.json',verify_dispatch_evidence(read(out/'request_manifest.json.gz')))
        a=audit(out,work);entries=read(out/'checkpoint.json.gz')['entries'];cur=read(work/'native_cursors.json')
        receipt=read(out/'run_receipt.json');resume=deepcopy(read(BASE/q['parent_scope']/'resume_checkpoint.json'))
        queue={r['source_id']:r for r in resume['retained_native_partial_queue']}
        for sid in q['source_ids']:
            if sid in entries and entries[sid]['features'] is not None:
                queue.pop(sid,None)
            else:
                c=cur[sid];queue[sid]=dict(source_id=sid,provider=PROVIDER,seed_kind='bridge_union',
                    native_pages=c['saved_native_pages'],saved_evidence_pages=c['saved_evidence_pages'],
                    last_native_cursor_sha256=hashlib.sha256(c['cursor'].encode()).hexdigest(),evidence_scope=scope,
                    finalized=sid in entries,requires_distinct_pinned_successor=True)
        missing=[r['source_id'] for r in read(out/'precutoff_feature_view.json.gz')['rows'] if r['features'] is None]
        assert a['available_coldcard_vectors']==q['baseline_vectors']+len(a['new_complete_source_ids'])==1500-len(missing)
        resume.update(pass_name=scope,status='closed_recorded_checkpoint',coldcard_vectors_available=1500-len(missing),
            coldcard_remaining_bounded_source_ids=missing,retained_native_partial_queue=list(queue.values()),
            source_ids=q['source_ids'],finalized_source_ids=list(entries),pending_source_ids=[s for s in q['source_ids'] if s not in entries],
            new_complete_source_ids=a['new_complete_source_ids'],collection_can_resume=False,model_fits=0,new_scores=0,automation_enabled=False)
        write(out/'resume_checkpoint.json',resume)
        p=read(POLICY);assert p['collector_lease']['owner']==scope
        p['collector_lease'].update(state='idle',owner=None,last_owner=scope,expires_at=None,
            finished_at=datetime.now(timezone.utc).isoformat(),operational_locks_released=True,stop_status=receipt['status'])
        p.update(active_collection_scope='none',coverage_collection_paused=True,
            latest_consolidated_prefix_view=scope+'/precutoff_feature_view.json.gz',latest_prefix_resume_file=scope+'/resume_checkpoint.json',
            latest_prefix_work=work.name,automation_enabled=False,
            comparison_pre_cutoff_predictors_available=1000-len(missing),comparison_pre_cutoff_predictors_unavailable=len(missing))
        p['provider_access_policies'][PROVIDER].update(status='closed_recorded_audited',last_http200=receipt['http200'])
        if receipt['status']!='completed':
            from datetime import timedelta
            p['provider_access_policies'][PROVIDER].update(status='stopped_after_first_failure',no_new_probe_authorized=True,
                next_network_attempt_not_before=(datetime.now(timezone.utc)+timedelta(hours=2)).isoformat())
        write(POLICY,p);(work/'lease_published').unlink(missing_ok=True)
        write(out/'collection_stop.json',dict(status=receipt['status'],operational_locks_released=True,restart_same_scope_allowed=False,automation_enabled=False))
        state=read(CAMPAIGN/'progress.json');done=set(state['finalized_source_ids'])|set(entries)
        state['finalized_source_ids']=[s for s in state['source_ids'] if s in done]
        state['pending_source_ids']=[s for s in state['source_ids'] if s not in done]
        state['new_complete_source_ids']+=a['new_complete_source_ids']
        okay=receipt['status']=='completed' and not a['pending_in_scope'] and not receipt['failures']
        state.update(status='verified_awaiting_save',active_scope=None,
            next_unit=q['campaign_unit']+1 if okay and state['pending_source_ids'] else None,
            can_continue=okay and bool(state['pending_source_ids']),available_vectors=1500-len(missing))
        state['completed_units'].append(dict(unit=q['campaign_unit'],scope=scope,source_ids=q['source_ids'],finalized_source_ids=list(entries),
            new_complete_source_ids=a['new_complete_source_ids'],fresh_requests=receipt['provider_requests'],http200=receipt['http200'],
            failures=receipt['failures'],new_prior_block_observations=a['fresh_native_source_transaction_observations'],private_evidence_saved=False))
        write(CAMPAIGN/'progress.json',state)
        result=dict(scope=scope,finalized=len(entries),new_complete=a['new_complete_source_ids'],available_vectors=1500-len(missing))
    # Repair derived counters before a successor pins this closed resume snapshot.
    resume=read(out/'resume_checkpoint.json');p=read(POLICY)
    remaining=len(resume['coldcard_remaining_bounded_source_ids'])
    resume.update(all_bounded_prefixes=remaining+37,private_native_cursors_sha256=sha(work/'native_cursors.json'),
        next_action='Distinct pinned successor from actual saved cursors; preserve all deep queues and unknown labels')
    write(out/'resume_checkpoint.json',resume)
    p.update(prefix_bounded_incomplete_sources=remaining,latest_prefix_output=scope,
        latest_prefix_protocol=scope+'/protocol.json',latest_prefix_coverage_audit=scope+'/coverage_audit.json',
        latest_prefix_result_file=scope+'/coverage_audit.json',latest_prefix_resume_checkpoint=scope+'/resume_checkpoint.json',
        latest_prefix_stop_file=scope+'/collection_stop.json',latest_status='prioritized_recorded_checkpoint_verified')
    write(POLICY,p)
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('command',choices=['init','prepare','authorize','run','finish','saved']);p.add_argument('value',nargs='?')
    a=p.parse_args()
    result=initialize() if a.command=='init' else prepare(int(a.value)) if a.command=='prepare' else inherited.authorize(a.value) if a.command=='authorize' else inherited.saved(a.value) if a.command=='saved' else globals()[a.command](a.value)
    if result is not None:print(__import__('json').dumps(result,sort_keys=True))
