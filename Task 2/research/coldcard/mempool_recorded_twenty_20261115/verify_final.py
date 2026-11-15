"""Verify exactly twenty saved continuations and their recorded clock evidence."""
from contextlib import ExitStack
from datetime import datetime, timezone
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
    assert selection['requested_sources']==len(selection['source_ids'])==len(set(selection['source_ids']))==20
    assert state['status']=='all_twenty_saved' and not state['pending_source_ids'] and state['active_scope'] is None
    assert not state['can_continue'] and state['next_unit'] is None
    assert state['finalized_source_ids']==selection['source_ids']
    assert len(state['completed_units'])==len(selection['units'])
    baseline=read(BASE/selection['original_parent']/'precutoff_feature_view.json.gz')
    before={r['source_id']:r for r in baseline['rows']}
    assert len(before)==1500 and sum(r['features'] is not None for r in before.values())==1446
    previous=selection['original_parent'];seen=[];complete=[];requests=observations=files=pages=0;locks=set();ledger=[]
    for index,unit in enumerate(state['completed_units'],1):
        out=BASE/unit['scope'];work=BASE/('source_cohort_work_'+out.name)
        q=read(out/'protocol.json');a=read(out/'coverage_audit.json');r=read(out/'run_receipt.json');backup=read(out/'private_cache_backup.json')
        assert unit['unit']==q['campaign_unit']==index
        assert q['source_ids']==selection['units'][index-1]['source_ids'] and q['parent_scope']==previous
        assert q['kind']==selection['units'][index-1]['kind'] and q['previous_bound']==selection['units'][index-1]['previous_bound']
        assert q['maximum_new_native_pages']==50 and q['enforced_dispatch_spacing_seconds']==5.25
        assert q['workers']==1 and q['timeout_seconds']==45
        assert a['status']==read(out/'independent_verification.json')['status']=='passed'
        assert backup['saved_privately'] and backup['library_metadata_applied'] and unit['private_evidence_saved']
        assert r['status']=='completed' and r['provider_requests']==r['http200'] and r['failures']==0
        assert r['operational_locks_released'] and r['blockstream_provider_requests']==0
        manifest=read(out/'request_manifest.json.gz')
        assert manifest==[read(p) for p in sorted(work.glob('requests/*/*.json'))]
        assert verify_dispatch_evidence(manifest)==read(out/'dispatch_verification.json')
        fresh=[m for m in manifest if not m.get('offline_reused')]
        assert len(fresh)==r['provider_requests'] and all(m.get('http_status')==200 and 'error_type' not in m for m in fresh)
        for sid in q['source_ids']:
            assert sid not in seen;seen.append(sid)
            if q['kind']=='native':
                tails=[m for m in fresh if m['source_id']==sid and m['key'].startswith('tail_')]
                assert all(q['previous_bound']<=int(m['key'][5:])<q['previous_bound']+50 for m in tails)
            else:
                tails=[m for m in fresh if m['source_id']==sid and m['key'].startswith('native_tail_')]
                assert all(0<=int(m['key'][12:])<50 for m in tails)
            assert len(tails)<=50;pages+=len(tails)
        cp=read(out/'checkpoint.json.gz');assert set(cp['entries'])==set(q['source_ids'])
        assert cp['protocol_sha256']==sha(out/'protocol.json')
        for sid,e in cp['entries'].items():
            assert sha(work/e['raw_file'])==e['raw_sha256']
            if e['features'] is not None:complete.append(sid)
        assert a['available_coldcard_vectors']==1446+len(complete)
        for pin in q['inputs'].values():assert sha((out/pin['file']).resolve())==pin['sha256']
        requests+=r['http200'];observations+=a['fresh_native_source_transaction_observations'];files+=backup['private_files_verified']
        locks.update(read(work/'historical_locks.json'));locks.add(str(work/'collector.lock'))
        ledger.append(dict(scope=out.name,sources=q['source_ids'],new_complete=a['new_complete_source_ids'],http200=r['http200'],kind=q['kind']))
        previous=out.name
    assert seen==selection['source_ids'] and set(complete)==set(state['new_complete_source_ids'])
    final=BASE/previous;view=read(final/'precutoff_feature_view.json.gz');rows={r['source_id']:r for r in view['rows']}
    assert set(rows)==set(before)
    for sid,row in rows.items():
        for key in ['source_id','address_sha256','payment_txid_sha256','cutoff_height','cutoff_block_hash','labels','known_coldcard_core_membership','full_history_status']:
            assert row.get(key)==before[sid].get(key)
        if before[sid]['features'] is not None or sid not in seen:assert row==before[sid]
    available=sum(r['features'] is not None for r in rows.values())
    assert available==1446+len(complete)==state['available_vectors']
    assert view['collection_operational_warnings']==baseline['collection_operational_warnings']
    assert (final/'retained_deep_queue.json').read_bytes()==(BASE/selection['original_parent']/'retained_deep_queue.json').read_bytes()
    policy=read(BASE/'comparison_access_retries_20261030/retry_policy.json')
    assert policy['collector_lease']['state']=='idle' and policy['active_collection_scope']=='none' and not policy['automation_enabled']
    assert policy['latest_consolidated_prefix_view']==previous+'/precutoff_feature_view.json.gz'
    with ExitStack() as stack:
        for name in sorted(locks):
            f=stack.enter_context(Path(name).open('a+'));fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
    result=dict(status='passed',verified_at=datetime.now(timezone.utc).isoformat(),requested_histories=20,
        processed_histories=20,new_complete_prefixes=len(complete),new_complete_source_ids=complete,
        bounded_histories=20-len(complete),available_vectors=available,missing_vectors=1500-available,
        previous_complete_vectors_preserved=1446,http200=requests,http_failures=0,new_native_pages=pages,
        new_prior_block_address_transaction_observations=observations,observations_not_global_unique_transactions=True,
        private_evidence_files_saved=files,operational_locks_checked_free=len(locks),recorded_dispatch_audits_passed=len(ledger),
        minimum_enforced_dispatch_seconds=5.25,original_timing_failure_preserved=True,offline_admitted_prefix_preserved=True,
        all_labels_identities_cutoffs_and_current_history_statuses_preserved=True,deep_queue_preserved=True,
        lease_idle=True,automation_enabled=False,model_fits=0,new_scores=0,units=ledger,latest_scope=previous)
    write(CAMPAIGN/'final_verification.json',result)
    resume=read(final/'resume_checkpoint.json')
    write(CAMPAIGN/'remaining_coverage_inventory.json',dict(available_vectors=available,missing_vectors=1500-available,
        remaining_source_ids=sorted(s for s,r in rows.items() if r['features'] is None),
        retained_native_partial_queue=resume['retained_native_partial_queue'],latest_view='../'+previous+'/precutoff_feature_view.json.gz',
        latest_resume='../'+previous+'/resume_checkpoint.json',automatic_schedule=False,model_fits=0,new_scores=0))
    print(__import__('json').dumps(result,indent=2));return result


if __name__=='__main__':verify()
