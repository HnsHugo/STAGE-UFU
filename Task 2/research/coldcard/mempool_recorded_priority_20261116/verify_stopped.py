"""Verify the saved partial campaign without treating HTTP 503 as completion."""
from contextlib import ExitStack
from datetime import datetime,timezone
import fcntl
from pathlib import Path
import sys

CAMPAIGN=Path(__file__).resolve().parent
BASE=CAMPAIGN.parent
sys.path.insert(0,str(BASE))
from prepare_frontier_checkpoint import read,sha,write
from recorded_mempool_resume import verify_dispatch_evidence


def verify():
    selection=read(CAMPAIGN/'selection.json');state=read(CAMPAIGN/'progress.json')
    assert selection['requested_sources']==len(set(selection['source_ids']))==20
    assert state['status']=='stopped_saved' and not state['can_continue'] and state['next_unit']is None
    assert state['active_scope']is None and len(state['completed_units'])==2
    assert len(state['finalized_source_ids'])==4 and len(state['pending_source_ids'])==16
    assert set(state['source_ids'])==set(state['finalized_source_ids'])|set(state['pending_source_ids'])
    baseline=read(BASE/selection['original_parent']/'precutoff_feature_view.json.gz')
    before={r['source_id']:r for r in baseline['rows']}
    assert len(before)==1500 and sum(r['features']is not None for r in before.values())==1447
    previous=selection['original_parent'];manifest_all=[];finalized=[];complete=[];locks=set();files=observations=pages=0
    for number,unit in enumerate(state['completed_units'],1):
        out=BASE/unit['scope'];work=BASE/('source_cohort_work_'+out.name)
        q=read(out/'protocol.json');a=read(out/'coverage_audit.json');receipt=read(out/'run_receipt.json')
        backup=read(out/'private_cache_backup.json');cp=read(out/'checkpoint.json.gz')
        assert q['parent_scope']==previous and q['source_ids']==selection['units'][number-1]['source_ids']
        assert q['campaign_unit']==unit['unit']==number and q['maximum_new_native_pages']==50
        assert q['workers']==1 and q['timeout_seconds']==45 and q['enforced_dispatch_spacing_seconds']==5.25
        for pin in q['inputs'].values():assert sha((out/pin['file']).resolve())==pin['sha256']
        assert a['status']==read(out/'independent_verification.json')['status']=='passed'
        assert backup['saved_privately'] and backup['library_metadata_applied'] and unit['private_evidence_saved']
        assert backup['scope_protocol_sha256']==cp['protocol_sha256']==sha(out/'protocol.json')
        assert receipt['operational_locks_released'] and receipt['blockstream_provider_requests']==0
        assert receipt['model_fits']==receipt['new_scores']==0
        assert receipt['status']==('completed'if number==1 else'stopped')
        metadata=read(out/'request_manifest.json.gz')
        assert metadata==[read(p)for p in sorted(work.glob('requests/*/*.json'))]
        assert verify_dispatch_evidence(metadata)==read(out/'dispatch_verification.json')
        fresh=[m for m in metadata if not m.get('offline_reused')]
        assert len(fresh)==receipt['provider_requests']
        assert sum(m.get('http_status')==200 for m in fresh)==receipt['http200']
        assert sum('error_type'in m for m in fresh)==receipt['failures']
        for m in fresh:
            path=work/'requests'/m['source_id']/(m['key']+'.json.gz')
            if m.get('http_status')==200:assert sha(path)==m['sha256']
            else:assert m['http_status']==503 and 'error_type'in m and not path.exists()
            if m.get('http_status')==200 and m['key'].startswith(('extension_','native_tail_','tail_')):pages+=1
        for sid,e in cp['entries'].items():
            assert sid not in finalized;finalized.append(sid)
            assert sha(work/e['raw_file'])==e['raw_sha256']
            if e['features']is not None:complete.append(sid)
        assert set(unit['finalized_source_ids'])==set(cp['entries'])
        assert a['available_coldcard_vectors']==1447+len(complete)
        observations+=a['fresh_native_source_transaction_observations'];files+=backup['private_files_verified']
        locks.update(read(work/'historical_locks.json'));locks.add(str(work/'collector.lock'))
        assert not(work/'lease_published').exists()
        manifest_all.extend(fresh);previous=out.name
    assert set(finalized)==set(state['finalized_source_ids']) and set(complete)==set(state['new_complete_source_ids'])
    failures=[m for m in manifest_all if 'error_type'in m]
    assert len(failures)==1 and failures[0]['http_status']==503
    assert all(m['started_at']<=failures[0]['finished_at']for m in manifest_all)
    final=BASE/previous;work=BASE/('source_cohort_work_'+previous)
    recovery=read(final/'unfinalized_evidence_recovery.json')
    assert recovery['status']=='passed' and recovery['provider_requests']==0
    assert recovery['unstarted_source_ids']==['comparison_0298']
    partial_observations=0
    for item in recovery['successful_unfinalized_evidence']:
        path=work/item['raw_file'];assert sha(path)==item['raw_sha256']
        raw=read(path)
        assert raw['anchor_after']is None and raw['reference_after_missing'] and not raw['source_finalized']
        assert raw['features']is None and not raw['pagination_exhausted']
        partial_observations+=item['new_prior_block_observations']
    view=read(final/'precutoff_feature_view.json.gz');rows={r['source_id']:r for r in view['rows']}
    assert set(rows)==set(before)
    for sid,row in rows.items():
        for key in ['source_id','address_sha256','payment_txid_sha256','cutoff_height','cutoff_block_hash','labels','known_coldcard_core_membership','full_history_status']:
            assert row.get(key)==before[sid].get(key)
        if before[sid]['features']is not None or sid not in finalized:assert row==before[sid]
    available=sum(r['features']is not None for r in rows.values())
    assert available==1450==state['available_vectors']
    assert view['collection_operational_warnings']==baseline['collection_operational_warnings']
    assert(final/'retained_deep_queue.json').read_bytes()==(BASE/selection['original_parent']/'retained_deep_queue.json').read_bytes()
    resume=read(final/'resume_checkpoint.json')
    assert resume['all_bounded_prefixes']==87 and resume['coldcard_vectors_available']==available
    assert resume['private_native_cursors_sha256']==sha(work/'native_cursors.json')
    assert 'comparison_0298'not in {r['source_id']for r in resume['retained_native_partial_queue']}
    policy_path=BASE/'comparison_access_retries_20261030/retry_policy.json';policy=read(policy_path)
    assert policy['collector_lease']['state']=='idle' and policy['active_collection_scope']=='none'
    assert policy['provider_access_policies']['https://mempool.space/api']['no_new_probe_authorized']
    assert not policy['automation_enabled'] and policy['latest_consolidated_prefix_view']==previous+'/precutoff_feature_view.json.gz'
    with ExitStack()as stack:
        for name in sorted(locks):
            f=stack.enter_context(Path(name).open('a+'));fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
    result=dict(status='passed',collection_status='stopped_on_first_http503',verified_at=datetime.now(timezone.utc).isoformat(),
        requested_histories=20,finalized_histories=4,unfinalized_started_histories=1,unstarted_histories=15,pending_histories=16,
        new_complete_prefixes=3,new_complete_source_ids=complete,bounded_finalized_histories=1,
        available_vectors=available,missing_vectors=50,previous_complete_vectors_preserved=1447,
        http200=sum(m.get('http_status')==200 for m in manifest_all),http_failures=1,http_failure_status=503,
        successful_new_native_pages=pages,new_finalized_prior_block_observations=observations,
        new_unfinalized_prior_block_observations=partial_observations,
        total_new_prior_block_observations=observations+partial_observations,observation_count_is_not_global_unique_transactions=True,
        private_evidence_files_saved=files,operational_locks_checked_free=len(locks),
        data_audits_passed=2,recorded_dispatch_audits_passed=2,minimum_dispatch_spacing_seconds=5.25,
        missing_final_reference_check_preserved=True,old_failures_unknown_labels_cutoffs_and_deep_queues_preserved=True,
        lease_idle=True,provider_gate_closed=True,automation_enabled=False,model_fits=0,new_scores=0,latest_scope=previous)
    write(CAMPAIGN/'stopped_verification.json',result)
    write(CAMPAIGN/'remaining_coverage_inventory.json',dict(available_vectors=available,missing_vectors=50,
        remaining_source_ids=sorted(s for s,r in rows.items()if r['features']is None),
        retained_native_partial_queue=resume['retained_native_partial_queue'],
        retained_unfinalized_bridge_evidence=resume['retained_unfinalized_bridge_evidence'],
        latest_view='../'+previous+'/precutoff_feature_view.json.gz',latest_resume='../'+previous+'/resume_checkpoint.json',
        provider_gate_closed=True,automatic_schedule=False,model_fits=0,new_scores=0))
    policy.update(latest_campaign_global_verification=CAMPAIGN.name+'/stopped_verification.json',
        latest_remaining_coverage_inventory=CAMPAIGN.name+'/remaining_coverage_inventory.json')
    write(policy_path,policy)
    print(__import__('json').dumps(result,indent=2));return result


if __name__=='__main__':verify()
