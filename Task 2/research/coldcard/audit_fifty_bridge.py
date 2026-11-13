"""Verify actual-native-cursor continuation of the retained mixed-provider seed."""
import argparse
import copy
from datetime import datetime
import gzip
import hashlib
import json
from pathlib import Path
import sys

from build_source_registry import json_bytes
from prepare_frontier_checkpoint import read, sha, write
from resume_fifty_bridge import seed
from independent_mempool_native import validate_page
from independent_mempool_pilot import PROVIDER, status_check
import collect_reference_tail as tail


def audit(out, work):
    q=read(out/'protocol.json');assert not(out/'coverage_audit.json').exists()
    for p in q['inputs'].values():assert sha((out/p['file']).resolve())==p['sha256']
    assert sha(work/'plan.json')==q['private_plan_sha256'];records=read(work/'plan.json');assert len(records)==1
    record=records[0];sid=record['pilot_id'];assert q['source_ids']==[sid]
    spec,old,values,seen,height=seed(record,work,q);old_values=list(values);cursor=spec['native_cursor']
    baseline=read((out/q['inputs']['baseline_view']['file']).resolve());before={r['source_id']:r for r in baseline['rows']}
    assert before[sid]['features']is None and before[sid]['precutoff_history_provenance']['raw_sha256']==spec['raw_sha256']
    original=read((out/q['inputs']['bridge_cursor_proof']['file']).resolve())
    original_cursor=next(x for x in original['retained_native_partial_queue'] if x['source_id']==sid)
    assert original_cursor['last_native_cursor_sha256']==q['native_start_cursor_sha256']
    manifest=read(out/'request_manifest.json.gz');assert manifest==[read(p) for p in sorted((work/'requests').glob('*/*.json'))]
    consumed=set();folder=work/'requests'/sid
    def response(key,endpoint):
        marker=folder/(key+'.json');body=folder/(key+'.json.gz')
        if not marker.exists():return None
        m=read(marker);assert m['source_id']==sid and m['key']==key and m['provider']==PROVIDER
        assert key not in consumed;consumed.add(key)
        assert m['endpoint_sha256']==hashlib.sha256(endpoint.encode()).hexdigest()
        if not body.exists():assert 'sha256'not in m;return None
        assert m.get('http_status')==200 and sha(body)==m['sha256'];return read(body)
    first=response('reference_before','/tx/'+record['payment_txid']+'/status')
    if first is not None:status_check(record,first)
    pages=0;exhausted=False
    for i in range(q['maximum_new_native_pages']):
        page=response(f'extension_{i:04d}','/address/'+record['address']+'/txs/chain/'+cursor)
        if page is None:break
        height=validate_page(record,page,seen,height);pages+=1
        if not page:exhausted=True;break
        values.extend(page);cursor=page[-1]['txid']
    after=response('reference_after','/tx/'+record['payment_txid']+'/status');parents={}
    for txid in {v['txid'] for v in tail.anchor_check(record,old['anchor'])}:
        key='parent_'+hashlib.sha256(txid.encode()).hexdigest()
        if(folder/(key+'.json')).exists():
            value=response(key,'/tx/'+txid+'/status')
            if value is not None:parents[txid]=value
    cp=read(out/'checkpoint.json.gz');assert cp['protocol_sha256']==sha(out/'protocol.json');entries=cp['entries'];assert set(entries)<={sid}
    composed=copy.deepcopy(baseline);complete=[]
    if sid in entries:
        e=entries[sid];assert sha(work/e['raw_file'])==e['raw_sha256'];raw=read(work/e['raw_file']);assert first is not None
        assert raw['anchor']==old['anchor'] and raw['transactions']==values and raw['transactions'][:len(old_values)]==old_values
        assert raw['anchor_after']==after and raw['pagination_exhausted']==exhausted
        assert raw['native_continuation_start_cursor']==spec['native_cursor'] and raw['actual_native_last_cursor']==cursor
        assert raw['pages_fetched']==old['pages_fetched']+pages and raw['independent_provider_pages']==old['independent_provider_pages']+pages
        assert raw['legacy_provider_pages']==old['legacy_provider_pages'] and raw['partial_boundary_height']==old['partial_boundary_height']
        expected=tail.tail_check(record,old['anchor'],values,exhausted,after,parents)
        assert all(e[k]==expected[k] for k in ['status','features','prefix'])
        if e['features']is not None:
            sys.path.insert(0,str(out.parents[1]/'external_cases/cryptobilis_to_coldcard_20261109'))
            from experiment import recount_features
            assert recount_features(e['prefix'],record['cutoff_height'])==e['features'];complete=[sid]
        row=next(r for r in composed['rows'] if r['source_id']==sid)
        if complete:row['features']=e['features'];row['precutoff_history_status']='complete_prior_prefix'
        row['precutoff_history_provenance']=dict(pass_name=out.name,raw_sha256=e['raw_sha256'],pages_fetched=raw['pages_fetched'],provider=PROVIDER,method='Actual native cursor extension of verified mixed seed',full_current_history_counter_coverage_verified=False)
    return finish(out,work,q,before,composed,entries,manifest,consumed,old,old_values,values,cursor,pages,exhausted,complete)


def finish(out,work,q,before,composed,entries,manifest,consumed,old,old_values,values,cursor,pages,exhausted,complete):
    assert len(consumed)==len(manifest)<=q['maximum_requests']
    dispatch=sorted(m['dispatch_at'] for m in manifest if m.get('dispatch_at'))
    assert all((datetime.fromisoformat(b)-datetime.fromisoformat(a)).total_seconds()>=4.9 for a,b in zip(dispatch,dispatch[1:]))
    failures=[m for m in manifest if 'error_type'in m]
    if failures:
        stop=min(m['finished_at'] for m in failures);assert all(m['started_at']<=stop for m in manifest)
    receipt=read(out/'run_receipt.json');assert receipt['provider_requests']==len(manifest) and receipt['failures']==len(failures)
    assert receipt['operational_locks_released'] and receipt['blockstream_provider_requests']==0
    assert receipt['model_fits']==receipt['new_scores']==0
    for row in composed['rows']:
        previous=before[row['source_id']]
        for key in ['source_id','address_sha256','payment_txid_sha256','cutoff_height','cutoff_block_hash','known_coldcard_core_membership','labels','full_history_status']:
            assert row.get(key)==previous.get(key)
        if previous['features']is not None or row['source_id']not in entries:assert row==previous
    assert len(composed['rows'])==1500 and sum(r['features']is not None for r in before.values())==q['baseline_vectors']
    composed['updated_on']=q['created_on'];composed['inputs']['actual_native_bridge_extension_protocol_sha256']=sha(out/'protocol.json')
    (out/'precutoff_feature_view.json.gz').write_bytes(gzip.compress(json_bytes(composed),mtime=0))
    sid=q['source_ids'][0];cur={sid:dict(provider=PROVIDER,cursor=cursor,saved_native_pages=old['independent_provider_pages']+pages,saved_evidence_pages=old['pages_fetched']+pages,pagination_exhausted=exhausted,finalized=sid in entries)}
    write(work/'native_cursors.json',cur);available=sum(r['features']is not None for r in composed['rows'])
    height=before[sid]['cutoff_height'];retained=sum(t['status']['block_height']<height for t in old_values)
    fresh=sum(t['status']['block_height']<height for t in values[len(old_values):])
    details=[dict(source_id=sid,status=entries[sid]['status'] if sid in entries else 'pending',saved_native_pages=old['independent_provider_pages']+pages,saved_evidence_pages=old['pages_fetched']+pages,new_native_pages=pages,old_native_observations_retained=retained,fresh_native_source_transaction_observations=fresh,last_native_cursor_sha256=hashlib.sha256(cursor.encode()).hexdigest())]
    result=dict(schema_version=1,status='passed',selected=1,finalized=len(entries),new_complete_prefixes=len(complete),new_complete_source_ids=complete,bounded_in_scope=len(entries)-len(complete),pending_in_scope=1-len(entries),preserved_old_vectors=q['baseline_vectors'],available_coldcard_vectors=available,bounded_coldcard_prefixes=1500-available,cryptobilis_vectors_unchanged=329,total_remaining_bounded_prefixes=1500-available+37,provider=PROVIDER,new_request_records=len(manifest),new_successful_provider_responses=sum(m.get('http_status')==200 for m in manifest),failed_request_records=len(failures),retained_native_observations=retained,fresh_native_source_transaction_observations=fresh,source_progress=details,private_native_cursors_sha256=sha(work/'native_cursors.json'),composed_view_sha256=sha(out/'precutoff_feature_view.json.gz'),full_current_history_statuses_unchanged=True,unknown_labels_unchanged=True,original_14_definitions_unchanged=True,unselected_rows_unchanged=True,blockstream_provider_requests=0,automatic_retry_performed=False,model_fits=0,new_scores=0)
    write(out/'coverage_audit.json',result);write(out/'independent_verification.json',dict(result,verification_basis='Verified immutable mixed seed and actual native cursor; fresh response assembly; original UTXO extraction; separate feature recount; old-row and provider rate/budget/stop invariants'))
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('scope',type=Path);p.add_argument('work',type=Path)
    a=p.parse_args();print(json.dumps(audit(a.scope.resolve(),a.work.resolve()),sort_keys=True))
