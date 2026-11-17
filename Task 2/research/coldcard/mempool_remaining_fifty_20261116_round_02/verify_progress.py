"""Verify durable collection progress without confusing bounded and complete rows."""
from contextlib import ExitStack
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
    ids=selection['source_ids'];assert len(ids)==len(set(ids))==43
    assert set(state['finalized_source_ids']).isdisjoint(state['pending_source_ids'])
    assert set(state['finalized_source_ids'])|set(state['pending_source_ids'])==set(ids)
    assert state['active_scope']is None
    original=BASE/selection['original_parent'];baseline=read(original/'precutoff_feature_view.json.gz')
    before={r['source_id']:r for r in baseline['rows']};assert sum(r['features']is not None for r in before.values())==1457
    previous=original.name;done=[];new=[];requests=errors=observations=files=pages=unfinalized_observations=0;locks=set();ledger=[]
    locks.update(read(BASE/('source_cohort_work_'+original.name)/'historical_locks.json'))
    locks.update(str(w/'collector.lock')for w in BASE.glob('source_cohort_work_*'))
    for number,unit in enumerate(state['completed_units'],1):
        out=BASE/unit['scope'];work=BASE/('source_cohort_work_'+out.name);q=read(out/'protocol.json')
        assert unit['unit']==q['campaign_unit']==number and q['parent_scope']==previous
        assert q['source_ids']==selection['units'][number-1]['source_ids']
        assert q['maximum_new_native_pages']==50 and q['workers']==1 and q['timeout_seconds']==45
        assert q['enforced_dispatch_spacing_seconds']==5.25
        for pin in q['inputs'].values():assert sha((out/pin['file']).resolve())==pin['sha256']
        audit=read(out/'coverage_audit.json');receipt=read(out/'run_receipt.json');backup=read(out/'private_cache_backup.json')
        assert audit['status']==read(out/'independent_verification.json')['status']=='passed'
        assert unit['private_evidence_saved']and backup['saved_privately']and backup['library_metadata_applied']
        assert receipt['operational_locks_released']and receipt['blockstream_provider_requests']==0
        metadata=read(out/'request_manifest.json.gz');assert metadata==[read(p)for p in sorted(work.glob('requests/*/*.json'))]
        assert verify_dispatch_evidence(metadata)==read(out/'dispatch_verification.json')
        fresh=[m for m in metadata if not m.get('offline_reused')]
        assert len(fresh)==receipt['provider_requests']and sum(m.get('http_status')==200 for m in fresh)==receipt['http200']
        for sid in q['source_ids']:
            prefix='tail_'if q['kind']=='native'else'extension_'if q['kind']=='mixed_resume'else'native_tail_'
            tails=[m for m in fresh if m['source_id']==sid and m['key'].startswith(prefix)]
            assert len(tails)<=50
            for m in tails:
                index=int(m['key'][len(prefix):]);start=q['previous_bound']if q['kind']=='native'else 0
                assert start<=index<start+50
                if m.get('http_status')==200:pages+=1
        for m in fresh:
            body=work/'requests'/m['source_id']/(m['key']+'.json.gz')
            if m.get('http_status')==200:assert sha(body)==m['sha256']
        cp=read(out/'checkpoint.json.gz');assert cp['protocol_sha256']==sha(out/'protocol.json')
        assert set(cp['entries'])==set(unit['finalized_source_ids'])
        for sid,e in cp['entries'].items():
            assert sid not in done;done.append(sid);assert sha(work/e['raw_file'])==e['raw_sha256']
            if e['features']is not None:new.append(sid)
        assert audit['available_coldcard_vectors']==1457+len(new)
        requests+=receipt['http200'];errors+=receipt['failures'];observations+=audit['fresh_native_source_transaction_observations']
        unfinalized_observations+=sum(r['fresh_native_source_transaction_observations']for r in audit.get('source_progress',[])if r['source_id']not in cp['entries'])
        files+=backup['private_files_verified'];locks.update(read(work/'historical_locks.json'));locks.add(str(work/'collector.lock'))
        assert not(work/'lease_published').exists()
        ledger.append(dict(scope=out.name,finalized=len(cp['entries']),new_complete=audit['new_complete_source_ids'],http200=receipt['http200'],failures=receipt['failures']))
        previous=out.name
    assert set(done)==set(state['finalized_source_ids'])and set(new)==set(state['new_complete_source_ids'])
    final=BASE/previous;view=read(final/'precutoff_feature_view.json.gz');rows={r['source_id']:r for r in view['rows']}
    assert set(rows)==set(before)
    for sid,row in rows.items():
        for key in ['source_id','address_sha256','payment_txid_sha256','cutoff_height','cutoff_block_hash','labels','known_coldcard_core_membership','full_history_status']:
            assert row.get(key)==before[sid].get(key)
        if before[sid]['features']is not None or sid not in done:assert row==before[sid]
    available=sum(r['features']is not None for r in rows.values());assert available==1457+len(new)==state['available_vectors']
    assert view['collection_operational_warnings']==baseline['collection_operational_warnings']
    assert(final/'retained_deep_queue.json').read_bytes()==(original/'retained_deep_queue.json').read_bytes()
    resume=read(final/'resume_checkpoint.json');work=BASE/('source_cohort_work_'+previous)
    assert resume['all_bounded_prefixes']==1500-available+37 and resume['private_native_cursors_sha256']==sha(work/'native_cursors.json')
    policy_path=BASE/'comparison_access_retries_20261030/retry_policy.json';policy=read(policy_path)
    assert policy['collector_lease']['state']=='idle'and policy['active_collection_scope']=='none'and not policy['automation_enabled']
    assert policy['latest_consolidated_prefix_view']==previous+'/precutoff_feature_view.json.gz'
    with ExitStack()as stack:
        for name in sorted(locks):
            f=stack.enter_context(Path(name).open('a+'));fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
    report=dict(status='passed',requested_histories=43,finalized_histories=len(done),pending_histories=len(state['pending_source_ids']),
        new_complete_prefixes=len(new),new_complete_source_ids=new,available_vectors=available,missing_vectors=1500-available,
        original_vectors_preserved=1457,http200=requests,failed_intents=errors,successful_new_native_pages=pages,
        new_prior_block_observations=observations,
        new_finalized_prior_block_observations=observations-unfinalized_observations,
        retained_unfinalized_prior_block_observations=unfinalized_observations,
        observation_count_is_not_globally_unique_transactions=True,
        private_data_unit_files_saved=files,operational_locks_checked_free=len(locks),units=ledger,
        old_failures_unknown_labels_cutoffs_and_unselected_queues_preserved=True,lease_idle=True,
        automation_enabled=False,model_fits=0,new_scores=0,latest_scope=previous)
    write(CAMPAIGN/'progress_verification.json',report)
    unfinished=[];queue={r['source_id']:r for r in resume['retained_native_partial_queue']}
    for item in resume.get('retained_unfinalized_bridge_evidence',[]):
        value=dict(item);sid=value['source_id'];scope=queue[sid]['evidence_scope'];source=BASE/('source_cohort_work_'+scope)
        if not(source/value['raw_file']).exists():
            entry=read(BASE/scope/'checkpoint.json.gz')['entries'][sid];value['raw_file']=entry['raw_file']
        assert sha(source/value['raw_file'])==value['raw_sha256'];value['evidence_scope']=scope;unfinished.append(value)
    write(CAMPAIGN/'remaining_coverage_inventory.json',dict(available_vectors=available,missing_vectors=1500-available,
        remaining_source_ids=sorted(s for s,r in rows.items()if r['features']is None),
        retained_native_partial_queue=resume['retained_native_partial_queue'],
        retained_unfinalized_bridge_evidence=unfinished,
        latest_view='../'+previous+'/precutoff_feature_view.json.gz',latest_resume='../'+previous+'/resume_checkpoint.json',
        automatic_schedule=False,model_fits=0,new_scores=0))
    policy.update(latest_campaign_global_verification=CAMPAIGN.name+'/progress_verification.json',
        latest_remaining_coverage_inventory=CAMPAIGN.name+'/remaining_coverage_inventory.json')
    write(policy_path,policy)
    print(__import__('json').dumps(report,indent=2));return report


if __name__=='__main__':verify()
