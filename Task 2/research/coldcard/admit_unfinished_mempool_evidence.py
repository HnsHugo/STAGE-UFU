"""Admit verified unfinished evidence as a continuation seed, never as a vector."""
from contextlib import ExitStack
from copy import deepcopy
import fcntl
import gzip
import hashlib
import os
from pathlib import Path
import shutil

from build_source_registry import json_bytes
from prepare_frontier_checkpoint import read,sha,write
from independent_mempool_pilot import legacy_source,core,status_check
from independent_mempool_bridge import choose_bridge,merge_transaction

BASE=Path(__file__).resolve().parent
SCOPE='mempool_unfinished_admission_20261116'
PARENT='mempool_recorded_priority_20261116_unit_02'
SID='comparison_0294'
POLICY=BASE/'comparison_access_retries_20261030/retry_policy.json'


def admit():
    out=BASE/SCOPE;work=BASE/('source_cohort_work_'+SCOPE)
    assert not out.exists()and not work.exists()
    p=read(POLICY);assert p['collector_lease']['state']=='idle'and p['active_collection_scope']=='none'
    assert p['latest_consolidated_prefix_view']==PARENT+'/precutoff_feature_view.json.gz'
    parent=BASE/PARENT;oldwork=BASE/('source_cohort_work_'+PARENT)
    assert read(parent/'private_cache_backup.json')['saved_privately']
    recovery=read(parent/'unfinalized_evidence_recovery.json')
    assert recovery['status']=='passed'and recovery['provider_requests']==0
    item=next(x for x in recovery['successful_unfinalized_evidence']if x['source_id']==SID)
    record=next(r for r in read(oldwork/'plan.json')if r['pilot_id']==SID)
    pins={m['key']:m for m in read(parent/'legacy_reuse_manifest.json')['responses']if m['source_id']==SID}
    anchor,legacy,old,_=legacy_source(record,oldwork,pins)
    bridge,boundary=choose_bridge(record,anchor,old)
    folder=oldwork/'requests'/SID
    def response(key,endpoint):
        marker=read(folder/(key+'.json'));body=folder/(key+'.json.gz')
        assert marker['endpoint_sha256']==hashlib.sha256(endpoint.encode()).hexdigest()
        assert marker['http_status']==200 and sha(body)==marker['sha256']and 'error_type'not in marker
        return read(body)
    status_check(record,response('reference_before','/tx/'+record['payment_txid']+'/status'))
    assert core(response('boundary','/tx/'+bridge['txid']))==core(bridge)
    existing={t['txid']:t for t in old};seen={bridge['txid']};cursor=bridge['txid'];height=bridge['status']['block_height']
    for i in range(item['saved_native_pages']):
        page=response(f'native_tail_{i:04d}','/address/'+record['address']+'/txs/chain/'+cursor)
        assert isinstance(page,list)and 0<len(page)<=25
        for tx in page:
            assert tx['status'].get('confirmed')is True and tx['status'].get('block_hash')and tx['status']['block_height']<=height
            height=tx['status']['block_height'];merge_transaction(record,tx,existing,seen,boundary)
        cursor=page[-1]['txid']
    failed=read(folder/'native_tail_0007.json')
    assert failed['http_status']==503 and failed['endpoint_sha256']==hashlib.sha256(('/address/'+record['address']+'/txs/chain/'+cursor).encode()).hexdigest()
    assert not(folder/'native_tail_0007.json.gz').exists()and not(folder/'reference_after.json').exists()
    rawpath=oldwork/item['raw_file'];assert sha(rawpath)==item['raw_sha256']
    raw=read(rawpath);actual={t['txid']:t for t in raw['transactions']}
    assert set(actual)==set(existing)and all(core(actual[k])==core(v)for k,v in existing.items())
    assert raw['anchor']==anchor and raw['anchor_after']is None and raw['features']is None and not raw['pagination_exhausted']
    assert raw['actual_native_last_cursor']==cursor and raw['independent_provider_pages']==item['saved_native_pages']
    assert hashlib.sha256(cursor.encode()).hexdigest()==item['last_native_cursor_sha256']and height<boundary
    locks=set(read(oldwork/'historical_locks.json'))|{str(w/'collector.lock')for w in BASE.glob('source_cohort_work_*')}
    out.mkdir();work.mkdir(mode=0o700);(work/'raw').mkdir()
    with ExitStack()as stack:
        for name in sorted(locks|{str(work/'collector.lock')}):
            path=Path(name);path.parent.mkdir(parents=True,exist_ok=True)
            f=stack.enter_context(path.open('a+'));fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
        shutil.copyfile(rawpath,work/'raw'/f'{SID}.json.gz')
        shutil.copyfile(folder/'native_tail_0007.json',work/'original_http503.json')
        for name in ['remaining_source_registry.json','retained_bridge_native_cursors.json']:
            shutil.copyfile(oldwork/name,work/name)
        write(work/'plan.json',[record]);write(work/'historical_locks.json',sorted(locks))
        write(work/'native_cursors.json',{SID:dict(cursor=cursor,saved_native_pages=raw['independent_provider_pages'],
            saved_evidence_pages=raw['pages_fetched'],pagination_exhausted=False,finalized=False)})
        entry=dict(source_id=SID,raw_file=f'raw/{SID}.json.gz',raw_sha256=sha(work/'raw'/f'{SID}.json.gz'),
            pages_fetched=raw['pages_fetched'],status='bounded_incomplete',features=None,prefix=None,
            final_reference_check_missing=True,source_finalized=False)
        paths=dict(parent_view=parent/'precutoff_feature_view.json.gz',parent_resume=parent/'resume_checkpoint.json',
            original_recovery=parent/'unfinalized_evidence_recovery.json',parent_backup=parent/'private_cache_backup.json',code=Path(__file__))
        q=dict(pass_name=SCOPE,kind='offline_unfinished_evidence_admission',source_ids=[SID],parent_scope=PARENT,
            authorization='Current user requests all fifty remaining rows; preserve seven saved successful pages before new traffic.',
            provider_requests=0,baseline_vectors=1450,new_complete_prefixes=0,model_fits=0,new_scores=0,
            private_plan_sha256=sha(work/'plan.json'),private_registry_sha256=sha(work/'remaining_source_registry.json'),
            inputs={k:dict(file=os.path.relpath(v,out),sha256=sha(v))for k,v in paths.items()})
        write(out/'protocol.json',q)
        (out/'checkpoint.json.gz').write_bytes(gzip.compress(json_bytes(dict(protocol_sha256=sha(out/'protocol.json'),entries={SID:entry})),mtime=0))
        view=deepcopy(read(parent/'precutoff_feature_view.json.gz'));before=deepcopy(view)
        row=next(r for r in view['rows']if r['source_id']==SID);assert row['features']is None
        previous=deepcopy(row['precutoff_history_provenance'])
        row['precutoff_history_provenance']=dict(pass_name=SCOPE,raw_sha256=entry['raw_sha256'],pages_fetched=raw['pages_fetched'],
            independent_provider_pages=raw['independent_provider_pages'],provider='https://mempool.space/api',
            method='Offline verified unfinished union admitted only as a continuation seed',final_reference_check_missing=True,
            full_current_history_counter_coverage_verified=False)
        assert sum(r['features']is not None for r in view['rows'])==1450
        for a,b in zip(before['rows'],view['rows']):
            if a['source_id']!=SID:assert a==b
            else:
                assert {k:v for k,v in a.items()if k!='precutoff_history_provenance'}=={k:v for k,v in b.items()if k!='precutoff_history_provenance'}
        view['inputs']['offline_unfinished_seed_admission_protocol_sha256']=sha(out/'protocol.json')
        (out/'precutoff_feature_view.json.gz').write_bytes(gzip.compress(json_bytes(view),mtime=0))
        resume=deepcopy(read(parent/'resume_checkpoint.json'))
        cur=next(r for r in resume['retained_native_partial_queue']if r['source_id']==SID)
        cur.update(evidence_scope=SCOPE,unfinalized_raw_file=entry['raw_file'],unfinalized_raw_sha256=entry['raw_sha256'],
            evidence_state='independently_verified_unfinished_continuation_seed')
        resume.update(pass_name=SCOPE,status='closed_offline_unfinished_admission',private_native_cursors_sha256=sha(work/'native_cursors.json'),
            source_ids=[SID],finalized_source_ids=[],pending_source_ids=[SID],new_complete_source_ids=[],provider_requests=0,
            next_action='Distinct acquisition scope from saved actual cursors after provider gate revalidation; no vector admitted')
        write(out/'resume_checkpoint.json',resume);shutil.copyfile(parent/'retained_deep_queue.json',out/'retained_deep_queue.json')
        proof=dict(status='passed',source_ids=[SID],provider_requests=0,available_coldcard_vectors=1450,
            preserved_old_vectors=1450,new_complete_source_ids=[],all_feature_values_unchanged=True,
            successful_native_pages_reconstructed=7,original_http503_preserved=True,final_reference_check_still_missing=True,
            actual_native_cursor_sha256=item['last_native_cursor_sha256'],recovered_raw_sha256=entry['raw_sha256'],
            previous_provenance=previous,composed_view_sha256=sha(out/'precutoff_feature_view.json.gz'),model_fits=0,new_scores=0)
        write(out/'coverage_audit.json',proof);write(out/'independent_verification.json',proof)
        write(out/'run_receipt.json',dict(status='completed_offline',provider_requests=0,http200=0,failures=0,operational_locks_released=True,model_fits=0,new_scores=0))
    p.update(latest_consolidated_prefix_view=SCOPE+'/precutoff_feature_view.json.gz',latest_prefix_resume_file=SCOPE+'/resume_checkpoint.json',
        latest_prefix_output=SCOPE,latest_prefix_protocol=SCOPE+'/protocol.json',latest_prefix_work=work.name,
        latest_prefix_coverage_audit=SCOPE+'/coverage_audit.json',latest_prefix_result_file=SCOPE+'/coverage_audit.json',
        latest_prefix_resume_checkpoint=SCOPE+'/resume_checkpoint.json',latest_status='unfinished_evidence_admitted_without_vector')
    write(POLICY,p)
    (out/'RESULTS.md').write_text('# Unfinished evidence admitted only for continuation\n\nSeven saved successful native pages are independently reconstructed and fingerprint-verified. The actual native cursor crossed the legacy boundary. Only the missing row\'s evidence provenance advances; all 1,450 vectors, labels, cutoffs and other rows are unchanged. No new request, feature vector or completed source. The original HTTP503 and absent final reference check remain explicit. Continue only in a distinct pinned acquisition scope after the saved access gate is revalidated.\n')
    print(__import__('json').dumps(proof,indent=2))


if __name__=='__main__':admit()
