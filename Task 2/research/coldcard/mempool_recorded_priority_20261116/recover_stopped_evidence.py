"""Preserve successful unfinished pages offline after the first HTTP 503.

This does not finalize a source, create predictors, repeat a request or reopen
the consumed scope. The missing final reference check remains explicit.
"""
from pathlib import Path
import gzip
import hashlib
import sys

CAMPAIGN=Path(__file__).resolve().parent
BASE=CAMPAIGN.parent
sys.path.insert(0,str(BASE))
from build_source_registry import json_bytes
from prepare_frontier_checkpoint import read,sha,write
from independent_mempool_pilot import PROVIDER,legacy_source,core,status_check
from independent_mempool_bridge import choose_bridge,merge_transaction


def recover():
    scope='mempool_recorded_priority_20261116_unit_02'
    out=BASE/scope;work=BASE/('source_cohort_work_'+scope)
    assert not(out/'unfinalized_evidence_recovery.json').exists()
    q=read(out/'protocol.json');receipt=read(out/'run_receipt.json')
    assert receipt['status']=='stopped' and receipt['failures']==1 and receipt['operational_locks_released']
    for pin in q['inputs'].values():assert sha((out/pin['file']).resolve())==pin['sha256']
    original_resume=read(out/'resume_checkpoint.json')
    parent_resume=read(BASE/q['parent_scope']/'resume_checkpoint.json')
    records={r['pilot_id']:r for r in read(work/'plan.json')}
    entries=read(out/'checkpoint.json.gz')['entries']
    pins=read(out/'legacy_reuse_manifest.json')['responses']
    metadata=read(out/'request_manifest.json.gz')
    failures=[m for m in metadata if 'error_type'in m]
    assert len(failures)==1 and failures[0]['http_status']==503
    recovered,unstarted=[],[]
    queue={r['source_id']:r for r in original_resume['retained_native_partial_queue']}
    parent_queue={r['source_id']:r for r in parent_resume['retained_native_partial_queue']}
    for sid in q['source_ids']:
        if sid in entries:continue
        folder=work/'requests'/sid
        markers={m['key']:m for m in metadata if m['source_id']==sid}
        if not markers:
            if sid in parent_queue:queue[sid]=parent_queue[sid]
            else:queue.pop(sid,None)
            unstarted.append(sid);continue
        record=records[sid]
        anchor,oldpages,old,_=legacy_source(record,work,{m['key']:m for m in pins if m['source_id']==sid})
        bridge,boundary=choose_bridge(record,anchor,old)
        consumed=set()
        def response(key,endpoint):
            m=markers[key];assert key not in consumed;consumed.add(key)
            assert m['provider']==PROVIDER and m['endpoint_sha256']==hashlib.sha256(endpoint.encode()).hexdigest()
            body=folder/(key+'.json.gz')
            if m.get('http_status')!=200:
                assert m==failures[0] and not body.exists() and 'sha256'not in m
                return None
            assert sha(body)==m['sha256'];return read(body)
        status_check(record,response('reference_before','/tx/'+record['payment_txid']+'/status'))
        assert core(response('boundary','/tx/'+bridge['txid']))==core(bridge)
        existing={t['txid']:t for t in old};old_ids=set(existing)
        seen={bridge['txid']};cursor=bridge['txid'];height=bridge['status']['block_height'];pages=overlap=0
        for index in range(q['new_provider_page_limit']):
            key=f'native_tail_{index:04d}'
            if key not in markers:break
            page=response(key,'/address/'+record['address']+'/txs/chain/'+cursor)
            if page is None:break
            assert isinstance(page,list) and 0<len(page)<=25
            for tx in page:
                assert tx['status'].get('confirmed')is True and tx['status'].get('block_hash') and tx['status']['block_height']<=height
                height=tx['status']['block_height']
                if not merge_transaction(record,tx,existing,seen,boundary):overlap+=1
            pages+=1;cursor=page[-1]['txid']
        assert consumed==set(markers) and 'reference_after'not in markers
        raw=dict(address=record['address'],anchor=anchor,
            transactions=sorted(existing.values(),key=lambda t:(-t['status']['block_height'],t['txid'])),
            anchor_after=None,parent_statuses={},pagination_exhausted=False,
            legacy_provider_pages=len(oldpages),independent_provider_pages=pages,pages_fetched=len(oldpages)+pages,
            bridge_txid=bridge['txid'],partial_boundary_height=boundary,actual_native_last_cursor=cursor,
            fresh_native_txids=sorted(seen-{bridge['txid']}),reference_after_missing=True,
            features=None,source_finalized=False,recovery_method='Offline immutable complete-block union of successful saved pages; failed request preserved')
        path=work/'unfinalized_raw'/f'{sid}.json.gz';path.parent.mkdir(exist_ok=True)
        assert not path.exists();path.write_bytes(gzip.compress(json_bytes(raw),mtime=0))
        native_cur=read(work/'native_cursors.json')[sid]
        assert cursor==native_cur['cursor'] and pages==native_cur['saved_native_pages']
        detail=dict(source_id=sid,raw_file=str(path.relative_to(work)),raw_sha256=sha(path),
            saved_native_pages=pages,saved_evidence_pages=len(oldpages)+pages,
            last_native_cursor_sha256=hashlib.sha256(cursor.encode()).hexdigest(),
            crossed_legacy_boundary=height<boundary,verified_overlap_transactions=overlap,
            new_prior_block_observations=sum(t['status']['block_height']<record['cutoff_height'] for k,t in existing.items() if k not in old_ids),
            reference_after_missing=True,source_finalized=False,features_available=False)
        recovered.append(detail)
        queue[sid].update(evidence_state='successful_native_pages_without_final_reference_check',
            unfinalized_raw_file=detail['raw_file'],unfinalized_raw_sha256=detail['raw_sha256'],
            requires_unfinalized_recovery_manifest=True,source_finalized=False)
    resume=original_resume
    resume.update(retained_native_partial_queue=list(queue.values()),
        retained_unfinalized_bridge_evidence=recovered,
        next_action='Read unfinalized_evidence_recovery.json before a distinct successor; reuse every successful page and actual cursor, preserve failed native_tail_0007, fetch fresh reference checks only after a separately validated provider-access gate.',
        provider_stop_reason='HTTP 503 on comparison_0294 native_tail_0007; no further requests')
    write(out/'resume_checkpoint.json',resume)
    report=dict(status='passed',scope=scope,provider_requests=0,
        original_data_audit_unchanged=True,original_feature_view_unchanged=True,
        missing_final_reference_check_preserved=True,source_features_not_promoted=True,
        successful_unfinalized_evidence=recovered,unstarted_source_ids=unstarted,
        failed_request=dict(source_id=failures[0]['source_id'],key=failures[0]['key'],http_status=503,
            failure_origin=failures[0]['failure_origin'],marker_sha256=sha(work/'requests'/failures[0]['source_id']/(failures[0]['key']+'.json'))),
        old_resume_reconciliation='Remove the unstarted zero-page bridge from the native queue; explicitly link successful unfinished pages to their recovered union and actual cursor.',
        new_resume_sha256=sha(out/'resume_checkpoint.json'),restart_same_scope_allowed=False,model_fits=0,new_scores=0)
    write(out/'unfinalized_evidence_recovery.json',report)
    policy_path=BASE/'comparison_access_retries_20261030/retry_policy.json';p=read(policy_path)
    gate=p['provider_access_policies'][PROVIDER]
    assert gate['no_new_probe_authorized'] and p['collector_lease']['state']=='idle'
    gate.update(stop_reason='HTTP 503 provider response on comparison_0294 native_tail_0007; immediate stop; all successful evidence retained',
        last_http_status=503,last_refusals=1)
    p.update(latest_status='prioritized_recorded_collection_stopped_http503',latest_unfinalized_evidence_recovery=scope+'/unfinalized_evidence_recovery.json')
    write(policy_path,p)
    print(__import__('json').dumps(report,indent=2))


if __name__=='__main__':recover()
