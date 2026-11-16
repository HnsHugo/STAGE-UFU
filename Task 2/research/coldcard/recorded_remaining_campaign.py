"""All remaining Coldcard histories, in distinct saved recorded-clock scopes."""
import argparse
from copy import deepcopy
from datetime import datetime,timezone,timedelta
import hashlib
import os
from pathlib import Path
import re
import shutil
import tempfile

import recorded_priority_campaign as priority
import recorded_twenty_campaign as inherited
from prepare_frontier_checkpoint import read,sha,write
from independent_mempool_pilot import PROVIDER,status_check
from independent_mempool_bridge import choose_bridge
from planned_funding_bridge import legacy_source,funding_plan

BASE=priority.BASE
NAME=os.environ.get('UFU_REMAINING_CAMPAIGN','mempool_remaining_fifty_20261116')
assert re.fullmatch(r'mempool_remaining_fifty_20261116(?:_round_[0-9]{2})?',NAME)
CAMPAIGN=BASE/NAME
POLICY=priority.POLICY
priority.CAMPAIGN=inherited.CAMPAIGN=CAMPAIGN
_old_pins=priority.code_pins


def code_pins(out,q):
    _old_pins(out,q)
    for name in ['recorded_remaining_campaign.py','planned_funding_bridge.py','audit_planned_funding_bridge.py']:
        path=BASE/name
        q['inputs']['remaining_'+name.replace('.','_')]=dict(file=os.path.relpath(path,out),sha256=sha(path))
    write(out/'protocol.json',q)


priority.code_pins=code_pins


def build_units(candidates):
    chosen,units=priority.build_units(candidates,count=len(candidates))
    counters={r['source_id']:r['historical_full_current_counter']for r in chosen}
    units.sort(key=lambda u:(min(counters[s]for s in u['source_ids']),u['source_ids'][0]))
    return chosen,units


def merged_registry(parent,rows):
    oldwork=BASE/('source_cohort_work_'+parent.name)
    records={r['pilot_id']:r for r in read(oldwork/'remaining_source_registry.json')}
    paths={oldwork/'remaining_source_registry.json'}
    for row in rows.values():
        if row['features']is not None:continue
        origin=row['precutoff_history_provenance']['pass_name']
        path=BASE/('source_cohort_work_'+origin)/'plan.json';paths.add(path)
        for record in read(path):
            sid=record['pilot_id']
            if sid in records:assert records[sid]==record
            else:records[sid]=record
    for sid,row in rows.items():
        if row['features']is not None:continue
        record=records[sid]
        for key in ['address_sha256','payment_txid_sha256','cutoff_height','cutoff_block_hash']:
            assert row[key]==record[key]
        assert hashlib.sha256(record['address'].encode()).hexdigest()==record['address_sha256']
        assert hashlib.sha256(record['payment_txid'].encode()).hexdigest()==record['payment_txid_sha256']
    private=BASE/('source_cohort_work_'+CAMPAIGN.name+'_registry');private.mkdir(mode=0o700,exist_ok=True)
    write(private/'remaining_source_registry.json',[records[s]for s in sorted(records)])
    write(CAMPAIGN/'identity_registry_reconciliation.json',dict(status='passed',records=len(records),
        private_registry_sha256=sha(private/'remaining_source_registry.json'),
        verified_missing_ids=sorted(s for s,r in rows.items()if r['features']is None),
        source_registry_and_plans=[dict(file=os.path.relpath(p,BASE),sha256=sha(p))for p in sorted(paths)],
        rule='Union of saved identity records; exact duplicate equality; every missing row matched to its frozen address/reference hashes and cutoff. No feature or label changed.',provider_requests=0))
    return records


def initialize():
    CAMPAIGN.mkdir(exist_ok=True)
    assert not(CAMPAIGN/'selection.json').exists()
    p=read(POLICY);assert p['collector_lease']['state']=='idle'
    parent=(BASE/p['latest_consolidated_prefix_view']).parent
    assert read(parent/'private_cache_backup.json')['saved_privately']
    rows={r['source_id']:r for r in read(parent/'precutoff_feature_view.json.gz')['rows']}
    missing=[s for s,r in rows.items()if r['features']is None]
    assert len(missing)==50 if NAME=='mempool_remaining_fifty_20261116'else 0<len(missing)<=50
    oldwork=BASE/('source_cohort_work_'+parent.name)
    records=merged_registry(parent,rows)
    queue={r['source_id']:r for r in read(parent/'resume_checkpoint.json')['retained_native_partial_queue']}
    counters={r['source_id']:r['tx_count']for r in read(BASE/'source_comparison_feasibility_20261102_1603/group_evidence.json.gz')['full_current_history_counter_evidence']}
    candidates=[];plans={}
    with tempfile.TemporaryDirectory()as temporary:
        work=Path(temporary);(work/'legacy').mkdir()
        for sid in missing:
            row=rows[sid];origin,source=inherited.evidence_for(row)
            entry=read(origin/'checkpoint.json.gz')['entries'][sid]
            assert sha(source/entry['raw_file'])==entry['raw_sha256']==row['precutoff_history_provenance']['raw_sha256']
            if sid in queue and queue[sid]['seed_kind']=='native':
                kind,bound='native',queue[sid]['native_pages']
            elif sid in queue and queue[sid]['seed_kind']=='bridge_union':
                raw=read(source/entry['raw_file']);cur=read(source/'native_cursors.json')[sid]
                point=next(t for t in raw['transactions']if t['txid']==cur['cursor'])
                assert raw['partial_boundary_height']>point['status']['block_height']
                assert hashlib.sha256(cur['cursor'].encode()).hexdigest()==queue[sid]['last_native_cursor_sha256']
                kind,bound='mixed_resume',raw['pages_fetched']
            else:
                (work/'legacy'/sid).symlink_to(source/'requests'/sid,target_is_directory=True)
                pins={m.stem:read(m)for m in(source/'requests'/sid).glob('*.json')if m.stem=='reference'or m.stem.startswith('tail_')}
                anchor,pages,tx,_=legacy_source(records[sid],work,pins)
                choose_bridge(records[sid],anchor,tx);plans[sid]=funding_plan(records[sid],anchor,tx)
                kind,bound='legacy_bridge',len(pages)
            candidates.append(dict(source_id=sid,kind=kind,previous_bound=bound,
                origin_scope=origin.name,historical_full_current_counter=counters[sid]))
    chosen,units=build_units(candidates);ids=sum((u['source_ids']for u in units),[])
    assert set(ids)==set(missing)and len(ids)==len(set(ids))
    selection=dict(schema_version=1,source_ids=ids,requested_sources=len(ids),units=units,chosen_candidates=chosen,
        original_parent=parent.name,original_vectors=1500-len(missing),created_on='2026-11-16',
        authorization='User explicitly requests: Fais les 50 qui reste. Persistent GitHub/Mempool permissions; all fifty missing source/reference pairs included, no model.',
        selection_rule='All remaining missing rows, without exclusions. Small uniform-kind/bound units ordered by their smallest old full-current transaction counter for scheduling only.',
        counter_limitation='Historical full-current counters do not measure exact remaining pre-reference work and are not new predictors.',
        additional_native_pages_per_source=50,maximum_unit_sources=3,workers=1,timeout_seconds=45,
        enforced_dispatch_spacing_seconds=5.25,unit='Frozen source/reference pair',
        target='Operational incident membership; hardware-use and theft labels remain unknown',
        predictors='Unchanged fourteen features strictly before the reference block',
        original_http503_preserved=True,unfinalized_seven_pages_preserved=True,automation_enabled=False,model_fits=0,new_scores=0)
    write(CAMPAIGN/'selection.json',selection)
    write(CAMPAIGN/'eligibility_preflight.json',dict(status='passed',all_missing_source_ids=missing,
        candidates=candidates,excluded_source_ids=[],legacy_missing_parent_counts={s:len(v['missing_from_saved_prefix'])for s,v in plans.items()},
        provider_requests=0))
    write(CAMPAIGN/'progress.json',dict(status='planned',source_ids=ids,pending_source_ids=ids,finalized_source_ids=[],
        new_complete_source_ids=[],completed_units=[],active_scope=None,next_unit=1,can_continue=True,
        available_vectors=selection['original_vectors'],automation_enabled=False))
    (CAMPAIGN/'README.md').write_text('# All remaining Coldcard histories\n\nAll missing rows are frozen without exclusions. Fifty additional native pages per source per checkpoint; a bounded result is incomplete. Immutable legacy cache validation now includes an explicit budget and plan for absent reference-parent status checks after terminal pagination. Such a parent must be in the excluded reference block; omitted prior-block funding is rejected. Preserve the seven previously interrupted successful pages through the independently verified admission seed, all old failures and every previous vector/label/cutoff.\n\nUse one worker, recorded 5.25-second timing, 45-second timeout, original Mempool route/TLS, fresh locks and exact published lease/readback. Revalidate provider access only after the saved cooldown. Audit, privately save and publish every unit before its successor. Stop on first actual failure/refusal/inconsistency. No model, route rotation, paid service or background schedule. Further remaining coverage needs a distinct pinned successor pass.\n')
    return dict(selected=len(ids),units=len(units),baseline_vectors=selection['original_vectors'],missing_funding_legacy_sources=sum(bool(v['missing_from_saved_prefix'])for v in plans.values()))


def validated_access():
    p=read(POLICY);gate=p['provider_access_policies'][PROVIDER]
    assert not gate.get('no_new_probe_authorized')and not gate.get('operational_validation_required')
    location=p['latest_mempool_access_validation'];out=(BASE/location).parent
    report=read(out/'coverage_audit.json');backup=read(out/'private_cache_backup.json')
    assert report['status']=='passed'and report['access_available']is True
    assert backup['saved_privately']and backup['library_metadata_applied']
    return out


def prepare(number):
    access=validated_access()
    original_read=inherited.read;original_priority_read=priority.read
    registry=read(BASE/('source_cohort_work_'+CAMPAIGN.name+'_registry')/'remaining_source_registry.json')
    def with_registry(path):
        if Path(path).name=='remaining_source_registry.json':return registry
        return original_read(path)
    inherited.read=priority.read=with_registry
    try:result=_prepare(number)
    finally:inherited.read=original_read;priority.read=original_priority_read
    out=BASE/result['scope'];work=BASE/('source_cohort_work_'+result['scope']);q=read(out/'protocol.json')
    write(work/'remaining_source_registry.json',registry)
    q['private_identity_registry_sha256']=sha(work/'remaining_source_registry.json')
    proof=CAMPAIGN/'identity_registry_reconciliation.json'
    q['inputs']['identity_registry_reconciliation']=dict(file=os.path.relpath(proof,out),sha256=sha(proof))
    for key,path in [('validated_provider_access',access/'coverage_audit.json'),('validated_access_protocol',access/'protocol.json'),('saved_access_evidence',access/'private_cache_backup.json')]:
        q['inputs'][key]=dict(file=os.path.relpath(path,out),sha256=sha(path))
    write(out/'protocol.json',q)
    return result


def _prepare(number):
    unit=read(CAMPAIGN/'selection.json')['units'][number-1]
    if unit['kind']!='legacy_bridge':
        return priority.prepare(number)
    original_read=inherited.read;original_legacy=inherited.legacy_source
    inferred=set()
    def compatible(path):
        value=original_read(path);path=Path(path).resolve()
        if path.suffix=='.json'and path.parent.parent.name=='requests'and path.parents[2].name.startswith('source_cohort_work_'):
            sid=path.parent.name
            if sid in unit['source_ids']:
                origin=path.parents[2].name.removeprefix('source_cohort_work_')
                acquisition=original_read(BASE/origin/'protocol.json')
                expected=acquisition['provider'];assert expected=='https://blockstream.info/api'
                assert value.get('provider',expected)==expected
                if'provider'not in value:inferred.add((sid,value['key']))
                return dict(value,provider=expected)
        return value
    inherited.read=compatible;inherited.legacy_source=legacy_source
    try:result=inherited.prepare(number)
    finally:inherited.read=original_read;inherited.legacy_source=original_legacy
    out=BASE/result['scope'];work=BASE/('source_cohort_work_'+result['scope']);q=read(out/'protocol.json')
    pins=read(out/'legacy_reuse_manifest.json')['responses'];plans={}
    for record in read(work/'plan.json'):
        sid=record['pilot_id']
        anchor,_,tx,_=legacy_source(record,work,{m['key']:m for m in pins if m['source_id']==sid})
        plans[sid]=funding_plan(record,anchor,tx)
    write(work/'legacy_funding_plan.json',plans)
    write(out/'legacy_provider_provenance.json',dict(status='passed',inferred_provider_fields=len(inferred),
        rule='Only the original fingerprint-pinned acquisition protocol supplies omitted provider tags; cached bytes unchanged',
        fresh_requests=0))
    q.update(private_legacy_funding_plan_sha256=sha(work/'legacy_funding_plan.json'),created_on='2026-11-16',
        terminal_funding_closure='Explicitly planned and included in the original per-reference-input request budget')
    for key,path in [('legacy_funding_plan',work/'legacy_funding_plan.json'),('legacy_provider_provenance',out/'legacy_provider_provenance.json')]:
        q['inputs'][key]=dict(file=os.path.relpath(path,out),sha256=sha(path))
    code_pins(out,q)
    return result


def run(scope):
    q=read(BASE/scope/'protocol.json')
    if q['kind']!='legacy_bridge':return priority.run(scope)
    import independent_mempool_resume as native
    import recorded_mempool_resume as recorded
    from planned_funding_bridge import collect
    pins=read(BASE/scope/'legacy_reuse_manifest.json')['responses']
    def bridged(record,requests,work,protocol,unused):
        return collect(record,requests,work,protocol,{m['key']:m for m in pins if m['source_id']==record['pilot_id']})
    native.collect=bridged
    recorded.run(BASE/scope/'protocol.json',BASE/('source_cohort_work_'+scope))


def authorize(scope):
    q=read(BASE/scope/'protocol.json');p=read(POLICY)
    due=p['provider_access_policies'][PROVIDER].get('next_network_attempt_not_before')
    assert due is None or datetime.now(timezone.utc)>=datetime.fromisoformat(due)
    if q['kind']!='bounded_access_revalidation':validated_access()
    result=inherited.authorize(scope)
    p=read(POLICY);p['collector_lease']['purpose']='Explicit user request for all fifty remaining histories, recorded timing and durable checkpoints'
    write(POLICY,p)
    authorization=read(BASE/scope/'run_authorization.json');authorization['collector_lease']=p['collector_lease']
    write(BASE/scope/'run_authorization.json',authorization)
    return result

def finish(scope):
    out=BASE/scope;work=BASE/('source_cohort_work_'+scope);q=read(out/'protocol.json')
    if q['kind'] == 'native':
        result=inherited.finish(scope)
    else:
        from audit_recorded_mixed_resume import audit as mixed_audit
        from audit_planned_funding_bridge import audit as legacy_audit
        audit=legacy_audit if q['kind']=='legacy_bridge' else mixed_audit
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
                c=cur[sid]
                if q['kind']=='legacy_bridge' and c['saved_native_pages']==0 and sid not in entries:
                    continue
                queue[sid]=dict(source_id=sid,provider=PROVIDER,seed_kind='bridge_union',
                    native_pages=c['saved_native_pages'],saved_evidence_pages=c['saved_evidence_pages'],
                    last_native_cursor_sha256=hashlib.sha256(c['cursor'].encode()).hexdigest(),evidence_scope=scope,
                    finalized=sid in entries,requires_distinct_pinned_successor=True)
        missing=[r['source_id'] for r in read(out/'precutoff_feature_view.json.gz')['rows'] if r['features'] is None]
        assert a['available_coldcard_vectors']==q['baseline_vectors']+len(a['new_complete_source_ids'])==1500-len(missing)
        resume.update(pass_name=scope,status='closed_recorded_checkpoint',coldcard_vectors_available=1500-len(missing),
            coldcard_remaining_bounded_source_ids=missing,retained_native_partial_queue=list(queue.values()),
            source_ids=q['source_ids'],finalized_source_ids=list(entries),pending_source_ids=[s for s in q['source_ids'] if s not in entries],
            new_complete_source_ids=a['new_complete_source_ids'],collection_can_resume=False,model_fits=0,new_scores=0,automation_enabled=False)
        prior_unfinished=[x for x in resume.get('retained_unfinalized_bridge_evidence',[]) if x['source_id']not in entries]
        fresh_unfinished=a.get('unfinalized_evidence',[])
        resume['retained_unfinalized_bridge_evidence']=[x for x in prior_unfinished if x['source_id']not in {n['source_id']for n in fresh_unfinished}]+fresh_unfinished
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
        private_identity_registry_sha256=sha(work/'remaining_source_registry.json'),
        next_action='Distinct pinned successor from actual saved cursors; preserve all deep queues and unknown labels')
    write(out/'resume_checkpoint.json',resume)
    p.update(prefix_bounded_incomplete_sources=remaining,latest_prefix_output=scope,
        latest_prefix_protocol=scope+'/protocol.json',latest_prefix_coverage_audit=scope+'/coverage_audit.json',
        latest_prefix_result_file=scope+'/coverage_audit.json',latest_prefix_resume_checkpoint=scope+'/resume_checkpoint.json',
        latest_prefix_stop_file=scope+'/collection_stop.json',latest_status='prioritized_recorded_checkpoint_verified')
    write(POLICY,p)
    return result


def saved(scope):
    out=BASE/scope;backup=read(out/'private_cache_backup.json')
    assert backup['saved_privately']and backup['library_metadata_applied']
    state=read(CAMPAIGN/'progress.json');unit=next(u for u in state['completed_units']if u['scope']==scope)
    unit.update(private_evidence_saved=True,private_evidence_sha256=backup['sha256'])
    state['status']='pass_saved'if not state['pending_source_ids']else('checkpoint_saved'if state['can_continue']else'stopped_saved')
    write(CAMPAIGN/'progress.json',state)
    (out/'RESULTS.md').write_text(f"# Verified saved remaining-history unit\n\n{len(unit['finalized_source_ids'])} finalized histories; {len(unit['new_complete_source_ids'])} new complete prefixes. {unit['http200']}/{unit['fresh_requests']} HTTP200; {unit['failures']} failed intents. {unit['new_prior_block_observations']} new prior-block address–transaction observations, not globally unique transactions. Data and recorded-clock audits pass. {backup['private_files_verified']} private evidence files verified and saved. Coverage: {state['available_vectors']}/1,500. Unknown labels, strict cutoffs and preceding vectors are unchanged. No fit/score.\n")
    selection=read(CAMPAIGN/'selection.json')
    table='\n'.join(f"| {u['unit']} | {len(u['finalized_source_ids'])} | {len(u['new_complete_source_ids'])} | {u['http200']} | {u['failures']} |"for u in state['completed_units'])
    (CAMPAIGN/'RESULTS.md').write_text(f"# All remaining histories — saved progress\n\n{len(state['finalized_source_ids'])}/{selection['requested_sources']} frozen histories finalized for this pass; {len(state['new_complete_source_ids'])} newly complete, {len(state['pending_source_ids'])} pending. Official coverage: {state['available_vectors']}/1,500. A page-capped history remains incomplete. All completed checkpoints pass data/clock audits and are privately saved. Original failures and unfinished evidence remain preserved. No model or background schedule.\n\n| Unit | Finalized | Newly complete | HTTP200 | Failed intents |\n|---|---:|---:|---:|---:|\n{table}\n")
    return dict(processed=len(state['finalized_source_ids']),pending=len(state['pending_source_ids']),vectors=state['available_vectors'],next_unit=state['next_unit'])


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['init','prepare','authorize','run','finish','saved'])
    parser.add_argument('value',nargs='?');args=parser.parse_args()
    result=initialize()if args.command=='init'else prepare(int(args.value))if args.command=='prepare'else globals()[args.command](args.value)
    if result is not None:print(__import__('json').dumps(result,sort_keys=True))

