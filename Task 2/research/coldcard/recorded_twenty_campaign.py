"""Twenty frozen histories, recorded dispatch timing and durable bounded units."""
import argparse
from contextlib import redirect_stdout
from copy import deepcopy
from datetime import datetime, timezone, timedelta
import hashlib
import os
from pathlib import Path
import re
import shutil

from prepare_frontier_checkpoint import read, sha, write
from independent_mempool_resume import cached_prefix
from independent_mempool_pilot import PROVIDER, legacy_source
from independent_mempool_bridge import choose_bridge
from native_extension_checkpoint import request_budget
from recorded_mempool_resume import verify_dispatch_evidence

BASE = Path(__file__).resolve().parent
CAMPAIGN = BASE / 'mempool_recorded_twenty_20261115'
POLICY = BASE / 'comparison_access_retries_20261030/retry_policy.json'
FIRST = ['comparison_0907', 'comparison_0912', 'comparison_0966',
         'comparison_0391', 'comparison_0433', 'comparison_0522']


def pins(paths, out):
    return {k: dict(file=os.path.relpath(p, out), sha256=sha(p)) for k,p in paths.items()}


def units_for(native, queue, legacy):
    assert len(native) == 16 and len(legacy) == 4 and len(set(native + legacy)) == 20
    assert set(FIRST) <= set(native)
    result = []
    for ids in [FIRST[:3], FIRST[3:]]:
        assert len({queue[s]['native_pages'] for s in ids}) == 1
        result.append(dict(kind='native', source_ids=ids, previous_bound=queue[ids[0]]['native_pages']))
    rest = sorted(set(native) - set(FIRST), key=lambda s: (queue[s]['native_pages'], s))
    for bound in sorted({queue[s]['native_pages'] for s in rest}):
        ids = [s for s in rest if queue[s]['native_pages'] == bound]
        for i in range(0,len(ids),3):
            result.append(dict(kind='native', source_ids=ids[i:i+3], previous_bound=bound))
    result.extend(dict(kind='legacy_bridge',source_ids=legacy[i:i+3],previous_bound=32) for i in range(0,4,3))
    assert len(sum((u['source_ids'] for u in result),[])) == 20
    return result


def initialize(preflight):
    assert not CAMPAIGN.exists()
    policy = read(POLICY)
    assert policy['collector_lease']['state'] == 'idle'
    parent = (BASE / policy['latest_consolidated_prefix_view']).parent
    assert parent.name == 'mempool_data_admission_20261115'
    assert read(parent/'private_cache_backup.json')['saved_privately']
    view = read(parent/'precutoff_feature_view.json.gz')
    rows = {r['source_id']:r for r in view['rows']}
    resume = read(parent/'resume_checkpoint.json')
    queue = {r['source_id']:r for r in resume['retained_native_partial_queue']}
    native = [s for s,q in queue.items() if q['seed_kind']=='native' and rows[s]['features'] is None]
    legacy = read(preflight)['eligible']
    assert all(rows[s]['features'] is None and s not in native for s in legacy)
    units = units_for(native,queue,legacy)
    ids = sum((u['source_ids'] for u in units),[])
    CAMPAIGN.mkdir()
    shutil.copyfile(preflight,CAMPAIGN/'legacy_preflight.json')
    selection = dict(schema_version=1,source_ids=ids,requested_sources=20,units=units,
        original_parent=parent.name,original_vectors=1446,additional_native_pages_per_source=50,
        maximum_unit_sources=3,authorization='Explicit user: Aller go fais en 20 en plus de save. Existing API/GitHub authorization retained.',
        original_operational_failure_preserved=True,first_six_previously_unattempted=FIRST,
        selection_rule='All sixteen remaining pure-native histories, previously unattempted six first; four immutable-cache/complete-block-bridge eligible legacy histories from the restored 20-source layer.',
        unit='Frozen source/reference pair',target='Operational case membership, not verified theft or hardware-device use',
        predictors='The unchanged fourteen predictors strictly before the reference block',
        recorded_clock='UTC plus monotonic nanoseconds',enforced_dispatch_spacing_seconds=5.25,
        workers=1,timeout_seconds=45,automation_enabled=False,model_fits=0,new_scores=0)
    write(CAMPAIGN/'selection.json',selection)
    write(CAMPAIGN/'progress.json',dict(status='planned',source_ids=ids,pending_source_ids=ids,
        finalized_source_ids=[],new_complete_source_ids=[],completed_units=[],active_scope=None,
        next_unit=1,can_continue=True,available_vectors=1446,automation_enabled=False))
    (CAMPAIGN/'README.md').write_text('# Twenty additional saved histories\n\nExactly twenty distinct missing source/reference pairs are frozen before traffic. The six previously unattempted histories come first, followed by ten other native continuations and four complete-block legacy bridges. Each source adds at most fifty new native pages. Preserve all old pages, unknown labels, strict cutoffs, old failed/consumed scopes and every unselected queue. Use the recorded 5.25-second clock guard, one worker and 45-second timeout on the same Mempool route/TLS. Audit, save private evidence and publish every small unit before its successor. Stop on the first real failure/refusal/inconsistency; no retry, rotation, model or background schedule. A processed history need not be complete.\n')
    return selection


def evidence_for(row):
    origin = BASE / row['precutoff_history_provenance']['pass_name']
    admission = row['precutoff_history_provenance'].get('offline_data_admission_scope')
    if admission:
        admitted = BASE/admission
        proof = read(admitted/'independent_verification.json')
        assert proof['status']=='passed' and proof['original_failure_preserved']
        assert row['source_id'] in proof['admitted_partial_evidence_source_ids'] + proof['admitted_complete_source_ids']
    else:
        assert read(origin/'independent_verification.json')['status']=='passed'
    assert read(origin/'private_cache_backup.json')['saved_privately']
    return origin,BASE/('source_cohort_work_'+origin.name)


def prepare(number):
    selection,state = (read(CAMPAIGN/n) for n in ['selection.json','progress.json'])
    assert state['can_continue'] and state['next_unit']==number and state['active_scope'] is None
    assert all(u['private_evidence_saved'] for u in state['completed_units'])
    policy=read(POLICY)
    assert policy['collector_lease']['state']=='idle' and policy['active_collection_scope']=='none'
    gate=policy['provider_access_policies'][PROVIDER]
    due=gate.get('next_network_attempt_not_before')
    assert due is None or datetime.now(timezone.utc)>=datetime.fromisoformat(due)
    parent=(BASE/policy['latest_consolidated_prefix_view']).parent
    assert read(parent/'private_cache_backup.json')['saved_privately']
    assert read(parent/'independent_verification.json')['status']=='passed'
    view=read(parent/'precutoff_feature_view.json.gz');rows={r['source_id']:r for r in view['rows']}
    unit=selection['units'][number-1];ids=unit['source_ids'];bound=unit['previous_bound']
    assert set(ids)<=set(state['pending_source_ids']) and all(rows[s]['features'] is None for s in ids)
    scope=f'{CAMPAIGN.name}_unit_{number:02d}';out=BASE/scope;work=BASE/('source_cohort_work_'+scope)
    assert not out.exists() and not work.exists();out.mkdir();work.mkdir(mode=0o700)
    for name in ['requests','raw','results','legacy']:(work/name).mkdir()
    oldwork=BASE/('source_cohort_work_'+parent.name)
    registry=read(oldwork/'remaining_source_registry.json');by_id={r['pilot_id']:r for r in registry}
    records=[by_id[s] for s in ids];write(work/'plan.json',records)
    for name in ['remaining_source_registry.json','retained_bridge_native_cursors.json']:
        shutil.copyfile(oldwork/name,work/name)
    native_cursors={};reuse=[];legacy=[];origins=set();locks=set(read(oldwork/'historical_locks.json'))
    for record in records:
        sid=record['pilot_id'];row=rows[sid]
        for key in ['address_sha256','payment_txid_sha256','cutoff_height','cutoff_block_hash']:
            assert row[key]==record[key]
        assert hashlib.sha256(record['address'].encode()).hexdigest()==record['address_sha256']
        assert hashlib.sha256(record['payment_txid'].encode()).hexdigest()==record['payment_txid_sha256']
        origin,source=evidence_for(row);origins.add(origin.name)
        entry=read(origin/'checkpoint.json.gz')['entries'][sid]
        assert entry['features'] is None and entry['pages_fetched']==bound
        assert sha(source/entry['raw_file'])==entry['raw_sha256']==row['precutoff_history_provenance']['raw_sha256']
        dest=work/('requests' if unit['kind']=='native' else 'legacy')/sid;dest.mkdir()
        for key in ['reference']+[f'tail_{i:04d}' for i in range(bound)]:
            marker=source/'requests'/sid/(key+'.json');meta=read(marker);body=marker.with_suffix('.json.gz')
            assert meta.get('http_status')==200 and 'error_type' not in meta and sha(body)==meta['sha256']
            shutil.copyfile(body,dest/body.name)
            pin={k:meta[k] for k in ['source_id','key','provider','endpoint_sha256','sha256']}
            pin.update(origin_scope=origin.name,original_marker_sha256=sha(marker))
            if unit['kind']=='native':
                assert meta['provider']==PROVIDER
                write(dest/marker.name,dict(meta,offline_reused=True,reused_from_pass=origin.name,original_marker_sha256=sha(marker)))
                reuse.append(pin)
            else:
                shutil.copyfile(marker,dest/marker.name);legacy.append(pin)
        if unit['kind']=='native':
            anchor,pages,cursor,seen,height,terminal=cached_prefix(record,work,[p for p in reuse if p['source_id']==sid])
            assert len(pages)==bound and not terminal
            assert [t for p in pages for t in p]==read(source/entry['raw_file'])['transactions']
            queue={x['source_id']:x for x in read(parent/'resume_checkpoint.json')['retained_native_partial_queue']}
            assert hashlib.sha256(cursor.encode()).hexdigest()==queue[sid]['last_native_cursor_sha256']
            native_cursors[sid]=dict(cursor=cursor,saved_native_pages=bound,provider=PROVIDER,pagination_exhausted=False)
        else:
            a,p,t,c=legacy_source(record,work,{m['key']:m for m in legacy if m['source_id']==sid})
            choose_bridge(record,a,t)
        locks.update(read(source/'historical_locks.json'))
    locks.update(str(p/'collector.lock') for p in BASE.glob('source_cohort_work_*') if p!=work)
    for name in locks:Path(name).parent.mkdir(parents=True,exist_ok=True)
    write(work/'historical_locks.json',sorted(locks));write(work/'parent_native_cursors.json',native_cursors)
    write(out/'offline_reuse_manifest.json',dict(responses=reuse,native_cached_bodies_reused=len(reuse)))
    write(out/'legacy_reuse_manifest.json',dict(responses=legacy))
    shutil.copyfile(parent/'retained_deep_queue.json',out/'retained_deep_queue.json')
    state.update(status='prepared_unit',active_scope=scope);write(CAMPAIGN/'progress.json',state)
    write(out/'prepared_campaign_state.json',state)
    paths=dict(baseline_view=parent/'precutoff_feature_view.json.gz',parent_resume=parent/'resume_checkpoint.json',
        parent_protocol=parent/'protocol.json',parent_verification=parent/'independent_verification.json',
        parent_private_backup=parent/'private_cache_backup.json',campaign_selection=CAMPAIGN/'selection.json',
        prepared_campaign_state=out/'prepared_campaign_state.json',checkpoint_code=Path(__file__).resolve(),
        recorded_dispatch_runner=BASE/'recorded_mempool_resume.py',native_collector=BASE/'independent_mempool_resume.py',
        native_auditor=BASE/'audit_independent_mempool_resume.py',legacy_collector=BASE/'independent_mempool_bridge.py',
        legacy_auditor=BASE/'audit_independent_mempool_bridge.py',legacy_validation=BASE/'independent_mempool_pilot.py',
        offline_reuse=out/'offline_reuse_manifest.json',legacy_reuse=out/'legacy_reuse_manifest.json',
        tests=CAMPAIGN/'preflight_tests.json',identifier_authorization=BASE/'mempool_identifier_authorization_20261114.json')
    for name in sorted(origins):
        for file in ['protocol.json','checkpoint.json.gz','private_cache_backup.json']:
            paths[name+'_'+file.replace('.','_')]=BASE/name/file
    budget=request_budget(records,extra_pages=50)
    maximum=budget['total_new_requests_at_most']+(len(ids) if unit['kind']=='legacy_bridge' else 0)
    q=dict(schema_version=8,pass_name=scope,campaign=CAMPAIGN.name,campaign_unit=number,kind=unit['kind'],parent_scope=parent.name,
        created_on='2026-11-15',authorization=selection['authorization'],source_ids=ids,provider=PROVIDER,
        baseline_vectors=sum(r['features'] is not None for r in rows.values()),previous_bound=bound,
        max_pages_per_address=bound+50,maximum_new_native_pages=50,new_provider_page_limit=50,
        maximum_requests=maximum,request_budget=dict(budget,total_new_requests_at_most=maximum),
        requests_per_second=.2,minimum_dispatch_interval_seconds=5,enforced_dispatch_spacing_seconds=5.25,
        dispatch_clock_evidence='monotonic_ns_and_utc',workers=1,timeout_seconds=45,
        offline_native_pages_reused=bound*len(ids) if unit['kind']=='native' else 0,
        private_plan_sha256=sha(work/'plan.json'),private_lock_manifest_sha256=sha(work/'historical_locks.json'),
        private_identity_registry_sha256=sha(work/'remaining_source_registry.json'),
        private_retained_bridge_native_cursors_sha256=sha(work/'retained_bridge_native_cursors.json'),
        private_parent_native_cursors_sha256=sha(work/'parent_native_cursors.json'),
        blockstream_cooldown_preserved_until=policy['provider_access_policies']['https://blockstream.info/api']['next_network_attempt_not_before'],
        live_policy_file='../comparison_access_retries_20261030/retry_policy.json',inputs=pins(paths,out),
        original_timing_failure_preserved=True,model_fits=0,new_scores=0,automation_enabled=False)
    write(out/'protocol.json',q)
    write(out/'preparation_verification.json',dict(status='passed',source_ids=ids,native_responses_verified=len(reuse),
        legacy_responses_verified=len(legacy),input_pins_verified=len(paths),provider_requests=0))
    return dict(scope=scope,sources=ids,kind=q['kind'],maximum_requests=maximum)


def authorize(scope):
    out=BASE/scope;q=read(out/'protocol.json');p=read(POLICY)
    assert p['collector_lease']['state']=='idle' and p['active_collection_scope']=='none'
    for pin in q['inputs'].values():assert sha((out/pin['file']).resolve())==pin['sha256']
    assert read(CAMPAIGN/'preflight_tests.json')['status']=='passed'
    now=datetime.now(timezone.utc)
    lease=dict(state='running',owner=scope,provider=PROVIDER,protocol=scope+'/protocol.json',protocol_sha256=sha(out/'protocol.json'),
        started_at=now.isoformat(),expires_at=(now+timedelta(hours=2)).isoformat(),operational_locks_released=False,
        purpose='Explicitly authorized twenty-history continuation with saved evidence and recorded dispatch clock')
    p.update(collector_lease=lease,active_collection_scope=scope,coverage_collection_paused=False,automation_enabled=False)
    p['provider_access_policies'][PROVIDER].update(status='running_recorded_clock',scope=scope,source_ids=q['source_ids'],
        no_new_probe_authorized=False,approval_required=False,operational_validation_required=False,
        operational_resolution='Distinct pinned recorded-clock runner and passing regressions; old failure remains preserved.',
        minimum_dispatch_interval_seconds=5,enforced_dispatch_spacing_seconds=5.25,timeout_seconds=45,maximum_requests=q['maximum_requests'])
    write(POLICY,p);write(out/'run_authorization.json',dict(status='awaiting_exact_published_lease_readback',scope=scope,collector_lease=lease))
    return dict(scope=scope,lease_expires_at=lease['expires_at'])


def run(scope):
    import recorded_mempool_resume as recorded
    import independent_mempool_resume as native
    out=BASE/scope;work=BASE/('source_cohort_work_'+scope);q=read(out/'protocol.json')
    if q['kind']=='legacy_bridge':
        from independent_mempool_bridge import collect
        legacy=read(out/'legacy_reuse_manifest.json')['responses']
        def bridged(record,requests,work,protocol,unused):
            return collect(record,requests,work,protocol,{m['key']:m for m in legacy if m['source_id']==record['pilot_id']})
        native.collect=bridged
    recorded.run(out/'protocol.json',work)


def finish(scope):
    out=BASE/scope;work=BASE/('source_cohort_work_'+scope);q=read(out/'protocol.json')
    assert read(CAMPAIGN/'progress.json')==read(out/'prepared_campaign_state.json')
    manifest=read(out/'request_manifest.json.gz')
    write(out/'dispatch_verification.json',verify_dispatch_evidence(manifest))
    if q['kind']=='native':
        import audit_independent_mempool_resume
        with (work/'audit.log').open('w') as log,redirect_stdout(log):audit_independent_mempool_resume.audit(out/'protocol.json',work)
        a=read(out/'coverage_audit.json')
    else:
        import audit_independent_mempool_bridge
        assert all(m['source_id'] in q['source_ids'] and (m['key'] in ['reference_before','boundary','reference_after'] or
            re.fullmatch(r'native_tail_[0-9]{4}',m['key'])) for m in manifest)
        a=audit_independent_mempool_bridge.audit(out,work)
        cur={};records={r['pilot_id']:r for r in read(work/'plan.json')};lp=read(out/'legacy_reuse_manifest.json')['responses']
        entries=read(out/'checkpoint.json.gz')['entries']
        for sid,record in records.items():
            anchor,oldpages,old,_=legacy_source(record,work,{m['key']:m for m in lp if m['source_id']==sid})
            bridge,_=choose_bridge(record,anchor,old);cursor=bridge['txid'];count=0;terminal=False
            for i in range(50):
                marker=work/'requests'/sid/(f'native_tail_{i:04d}.json')
                if not marker.exists() or read(marker).get('http_status')!=200:break
                page=read(marker.with_suffix('.json.gz'));count+=1
                if not page:terminal=True;break
                cursor=page[-1]['txid']
            cur[sid]=dict(cursor=cursor,saved_native_pages=count,saved_evidence_pages=32+count,pagination_exhausted=terminal,finalized=sid in entries)
        write(work/'native_cursors.json',cur)
        a.update(available_coldcard_vectors=a['coldcard_vectors'],bounded_in_scope=len(a['bounded_source_ids']),
            pending_in_scope=a['pending'],fresh_native_source_transaction_observations=a['additional_source_transaction_observations'])
        write(out/'coverage_audit.json',a);write(out/'independent_verification.json',dict(a,dispatch_verification='passed'))
    parent=BASE/q['parent_scope'];resume=deepcopy(read(parent/'resume_checkpoint.json'))
    queue={r['source_id']:r for r in resume['retained_native_partial_queue']}
    entries=read(out/'checkpoint.json.gz')['entries'];cur=read(work/'native_cursors.json');receipt=read(out/'run_receipt.json')
    for sid in q['source_ids']:
        if sid in entries and entries[sid]['features'] is not None:queue.pop(sid,None)
        else:
            c=cur[sid];queue[sid]=dict(source_id=sid,provider=PROVIDER,seed_kind='native' if q['kind']=='native' else 'bridge_union',
                native_pages=c['saved_native_pages'],saved_evidence_pages=c.get('saved_evidence_pages',c['saved_native_pages']),
                last_native_cursor_sha256=hashlib.sha256(c['cursor'].encode()).hexdigest(),evidence_scope=scope,
                finalized=sid in entries,requires_distinct_pinned_successor=True)
    view=read(out/'precutoff_feature_view.json.gz');missing=[r['source_id'] for r in view['rows'] if r['features'] is None]
    assert a['available_coldcard_vectors']==q['baseline_vectors']+len(a['new_complete_source_ids'])==1500-len(missing)
    resume.update(pass_name=scope,status='closed_recorded_checkpoint',coldcard_vectors_available=1500-len(missing),
        coldcard_remaining_bounded_source_ids=missing,retained_native_partial_queue=list(queue.values()),
        source_ids=q['source_ids'],finalized_source_ids=list(entries),pending_source_ids=[s for s in q['source_ids'] if s not in entries],
        new_complete_source_ids=a['new_complete_source_ids'],collection_can_resume=False,model_fits=0,new_scores=0,automation_enabled=False)
    write(out/'resume_checkpoint.json',resume)
    p=read(POLICY);assert p['collector_lease']['owner']==scope
    p['collector_lease'].update(state='idle',owner=None,last_owner=scope,expires_at=None,finished_at=datetime.now(timezone.utc).isoformat(),operational_locks_released=True,stop_status=receipt['status'])
    p.update(active_collection_scope='none',coverage_collection_paused=True,latest_consolidated_prefix_view=scope+'/precutoff_feature_view.json.gz',
        latest_prefix_resume_file=scope+'/resume_checkpoint.json',latest_prefix_work=work.name,automation_enabled=False,
        comparison_pre_cutoff_predictors_available=1000-len(missing),comparison_pre_cutoff_predictors_unavailable=len(missing))
    gate=p['provider_access_policies'][PROVIDER];gate.update(status='closed_recorded_audited',last_http200=receipt['http200'])
    if receipt['status']!='completed':
        gate.update(status='stopped_after_first_failure',no_new_probe_authorized=True,
            next_network_attempt_not_before=(datetime.now(timezone.utc)+timedelta(hours=2)).isoformat())
    write(POLICY,p);(work/'lease_published').unlink(missing_ok=True)
    write(out/'collection_stop.json',dict(status=receipt['status'],operational_locks_released=True,restart_same_scope_allowed=False,automation_enabled=False))
    state=read(CAMPAIGN/'progress.json');done=set(state['finalized_source_ids'])|set(entries)
    state['finalized_source_ids']=[s for s in state['source_ids'] if s in done]
    state['pending_source_ids']=[s for s in state['source_ids'] if s not in done]
    state['new_complete_source_ids']+=a['new_complete_source_ids']
    okay=receipt['status']=='completed' and not a['pending_in_scope'] and not receipt['failures']
    state.update(status='verified_awaiting_save',active_scope=None,next_unit=q['campaign_unit']+1 if okay and state['pending_source_ids'] else None,
        can_continue=okay and bool(state['pending_source_ids']),available_vectors=1500-len(missing))
    state['completed_units'].append(dict(unit=q['campaign_unit'],scope=scope,source_ids=q['source_ids'],finalized_source_ids=list(entries),
        new_complete_source_ids=a['new_complete_source_ids'],fresh_requests=receipt['provider_requests'],http200=receipt['http200'],failures=receipt['failures'],
        new_prior_block_observations=a['fresh_native_source_transaction_observations'],private_evidence_saved=False))
    write(CAMPAIGN/'progress.json',state)
    return dict(scope=scope,finalized=len(entries),new_complete=a['new_complete_source_ids'],available_vectors=1500-len(missing))


def saved(scope):
    out=BASE/scope;backup=read(out/'private_cache_backup.json');assert backup['saved_privately'] and backup['library_metadata_applied']
    state=read(CAMPAIGN/'progress.json');unit=next(u for u in state['completed_units'] if u['scope']==scope)
    unit.update(private_evidence_saved=True,private_evidence_sha256=backup['sha256'])
    state['status']='all_twenty_saved' if not state['pending_source_ids'] else ('checkpoint_saved' if state['can_continue'] else 'stopped_saved')
    write(CAMPAIGN/'progress.json',state)
    (out/'RESULTS.md').write_text(f"# Verified saved recorded-clock unit\n\n{len(unit['finalized_source_ids'])} finalized histories, {len(unit['new_complete_source_ids'])} new complete prefixes. {unit['http200']}/{unit['fresh_requests']} HTTP200; {unit['failures']} failed intents. {unit['new_prior_block_observations']} additional prior-block address–transaction observations, not globally unique transactions. Both the data audit and monotonic/UTC dispatch verification pass. All {backup['private_files_verified']} private evidence files are verified and saved. Coverage: {state['available_vectors']}/1,500. Unknown labels, cutoffs, prior vectors and unselected native/deep queues remain preserved; no fit/score.\n")
    table='\n'.join(f"| {u['unit']} | {len(u['finalized_source_ids'])} | {len(u['new_complete_source_ids'])} | {u['http200']} |" for u in state['completed_units'])
    (CAMPAIGN/'RESULTS.md').write_text(f"# Twenty-history recorded-clock campaign\n\n{len(state['finalized_source_ids'])}/20 frozen histories processed and saved; {len(state['new_complete_source_ids'])} newly complete, {len(state['pending_source_ids'])} pending. Official coverage: {state['available_vectors']}/1,500. A bounded outcome remains incomplete. Every completed unit passes the data and recorded-clock audits and is privately saved. Original timing failure and offline data admission remain preserved. No model, retry, rotation or background schedule.\n\n| Unit | Processed | Newly complete | HTTP200 |\n|---|---:|---:|---:|\n{table}\n")
    return dict(processed=len(state['finalized_source_ids']),pending=len(state['pending_source_ids']),vectors=state['available_vectors'],next_unit=state['next_unit'])


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=['init','prepare','authorize','run','finish','saved']);p.add_argument('value')
    args=p.parse_args()
    result=initialize(Path(args.value)) if args.command=='init' else prepare(int(args.value)) if args.command=='prepare' else globals()[args.command](args.value)
    if result is not None:print(__import__('json').dumps(result,sort_keys=True))
