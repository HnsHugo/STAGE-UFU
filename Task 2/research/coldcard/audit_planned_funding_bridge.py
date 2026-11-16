"""Replay planned legacy bridges, including fresh funding statuses and unfinished pages."""
from copy import deepcopy
import gzip
import hashlib
from pathlib import Path
import sys

from build_source_registry import json_bytes
from prepare_frontier_checkpoint import read,sha,write
from planned_funding_bridge import legacy_source,funding_plan
from independent_mempool_pilot import PROVIDER,core,status_check
from independent_mempool_bridge import choose_bridge
from recorded_mempool_resume import verify_dispatch_evidence
import collect_reference_tail as tail


def audit(out,work):
    q=read(out/'protocol.json');assert not(out/'coverage_audit.json').exists()
    for pin in q['inputs'].values():assert sha((out/pin['file']).resolve())==pin['sha256']
    assert sha(work/'plan.json')==q['private_plan_sha256']
    assert sha(work/'legacy_funding_plan.json')==q['private_legacy_funding_plan_sha256']
    records=read(work/'plan.json');assert[r['pilot_id']for r in records]==q['source_ids']
    plans=read(work/'legacy_funding_plan.json');pins=read(out/'legacy_reuse_manifest.json')['responses']
    baseline=read((out/q['inputs']['baseline_view']['file']).resolve());before={r['source_id']:r for r in baseline['rows']}
    cp=read(out/'checkpoint.json.gz');assert cp['protocol_sha256']==sha(out/'protocol.json')
    entries=cp['entries'];assert set(entries)<=set(q['source_ids'])
    metadata=read(out/'request_manifest.json.gz');assert metadata==[read(p)for p in sorted(work.glob('requests/*/*.json'))]
    verify_dispatch_evidence(metadata);assert len(metadata)<=q['maximum_requests']
    consumed=set();cursors={};details=[];complete=[];unfinished=[]
    view=deepcopy(baseline);rows={r['source_id']:r for r in view['rows']}
    sys.path.insert(0,str(out.parents[1]/'external_cases/cryptobilis_to_coldcard_20261109'))
    from experiment import recount_features
    for record in records:
        sid=record['pilot_id'];assert before[sid]['features']is None
        anchor,oldpages,old,_=legacy_source(record,work,{m['key']:m for m in pins if m['source_id']==sid})
        assert plans[sid]==funding_plan(record,anchor,old)
        bridge,boundary=choose_bridge(record,anchor,old);cursor=bridge['txid'];height=bridge['status']['block_height']
        existing={t['txid']:t for t in old};old_ids=set(existing);seen={bridge['txid']};pages=overlap=0;exhausted=False
        folder=work/'requests'/sid
        def response(key,endpoint):
            marker=folder/(key+'.json');body=folder/(key+'.json.gz')
            if not marker.exists():return None
            m=read(marker);assert(m['source_id'],m['key'],m['provider'])==(sid,key,PROVIDER)
            assert(sid,key)not in consumed;consumed.add((sid,key))
            assert m['endpoint_sha256']==hashlib.sha256(endpoint.encode()).hexdigest()
            if not body.exists():assert'sha256'not in m;return None
            assert m.get('http_status')==200 and sha(body)==m['sha256'];return read(body)
        first=response('reference_before','/tx/'+record['payment_txid']+'/status')
        if first is not None:status_check(record,first)
        point=response('boundary','/tx/'+bridge['txid'])
        if point is not None:assert core(point)==core(bridge)
        for i in range(q['maximum_new_native_pages']):
            page=response(f'native_tail_{i:04d}','/address/'+record['address']+'/txs/chain/'+cursor)
            if page is None:break
            assert isinstance(page,list)and len(page)<=25;pages+=1
            if not page:exhausted=True;break
            for tx in page:
                assert tx['txid']not in seen and tx['txid']!=record['payment_txid'];seen.add(tx['txid'])
                assert tx['status'].get('confirmed')is True and tx['status'].get('block_hash')and tx['status']['block_height']<=height
                assert any(o.get('scriptpubkey_address')==record['address']for o in tx['vout'])or any((v.get('prevout')or{}).get('scriptpubkey_address')==record['address']for v in tx['vin'])
                height=tx['status']['block_height']
                if tx['txid']in existing:assert core(existing[tx['txid']])==core(tx);overlap+=1
                else:assert height<=boundary;existing[tx['txid']]=tx
            cursor=page[-1]['txid']
        after=response('reference_after','/tx/'+record['payment_txid']+'/status')
        if after is not None:status_check(record,after)
        parents={}
        for txid in plans[sid]['reference_parent_txids']:
            key='parent_'+hashlib.sha256(txid.encode()).hexdigest()
            if(folder/(key+'.json')).exists():
                assert exhausted and txid not in existing
                value=response(key,'/tx/'+txid+'/status')
                if value is not None:status_check(record,value);parents[txid]=value
        values=sorted(existing.values(),key=lambda t:(-t['status']['block_height'],t['txid']))
        added=sum(t['status']['block_height']<record['cutoff_height']for k,t in existing.items()if k not in old_ids)
        cursors[sid]=dict(provider=PROVIDER,cursor=cursor,saved_native_pages=pages,saved_evidence_pages=len(oldpages)+pages,
            pagination_exhausted=exhausted,finalized=sid in entries)
        if sid in entries:
            e=entries[sid];assert sha(work/e['raw_file'])==e['raw_sha256']
            raw=read(work/e['raw_file']);assert first is not None and point is not None and after is not None
            assert raw['anchor']==anchor and raw['transactions']==values and raw['anchor_after']==after and raw['parent_statuses']==parents
            assert raw['pagination_exhausted']==exhausted and raw['pages_fetched']==len(oldpages)+pages
            assert raw['independent_provider_pages']==pages and raw['legacy_provider_pages']==len(oldpages)
            assert raw['cross_provider_overlap_verified']==overlap and raw['actual_native_last_cursor']==cursor
            expected=tail.tail_check(record,anchor,values,exhausted,after,parents)
            assert all(e[k]==expected[k]for k in ['status','features','prefix'])
            assert raw['additional_source_transaction_observations']==added
            if e['features']is not None:
                assert recount_features(e['prefix'],record['cutoff_height'])==e['features'];complete.append(sid)
                rows[sid]['features']=e['features'];rows[sid]['precutoff_history_status']='complete_prior_prefix'
            rows[sid]['precutoff_history_provenance']=dict(pass_name=out.name,raw_sha256=e['raw_sha256'],pages_fetched=len(oldpages)+pages,
                independent_provider_pages=pages,provider=PROVIDER,method='Complete-block bridge with planned reference-funding closure',full_current_history_counter_coverage_verified=False)
        elif pages:
            raw=dict(address=record['address'],anchor=anchor,transactions=values,anchor_after=after,parent_statuses=parents,
                pagination_exhausted=exhausted,pages_fetched=len(oldpages)+pages,legacy_provider_pages=len(oldpages),
                independent_provider_pages=pages,partial_boundary_height=boundary,actual_native_last_cursor=cursor,
                features=None,source_finalized=False,final_reference_check_missing=after is None)
            path=work/'unfinalized_raw'/f'{sid}.json.gz';path.parent.mkdir(exist_ok=True);assert not path.exists()
            path.write_bytes(gzip.compress(json_bytes(raw),mtime=0))
            unfinished.append(dict(source_id=sid,raw_file=str(path.relative_to(work)),raw_sha256=sha(path),
                saved_native_pages=pages,saved_evidence_pages=len(oldpages)+pages,last_native_cursor_sha256=hashlib.sha256(cursor.encode()).hexdigest(),
                new_prior_block_observations=added,final_reference_check_missing=after is None,features_available=False))
        details.append(dict(source_id=sid,new_native_pages=pages,old_transactions_retained=len(old),
            fresh_native_source_transaction_observations=added if sid in entries else 0,
            unfinalized_prior_block_observations=added if sid not in entries else 0,
            verified_overlap_transactions=overlap,fresh_funding_statuses=len(parents)))
    assert len(consumed)==len(metadata)
    receipt=read(out/'run_receipt.json');failures=[m for m in metadata if'error_type'in m]
    assert receipt['provider_requests']==len(metadata)and receipt['failures']==len(failures)
    assert receipt['operational_locks_released']and receipt['blockstream_provider_requests']==0
    if failures:assert all(m['started_at']<=min(f['finished_at']for f in failures)for m in metadata)
    for sid,row in rows.items():
        old=before[sid]
        for key in ['source_id','address_sha256','payment_txid_sha256','cutoff_height','cutoff_block_hash','labels','known_coldcard_core_membership','full_history_status']:
            assert row.get(key)==old.get(key)
        if old['features']is not None or sid not in entries:assert row==old
    assert len(rows)==1500 and sum(r['features']is not None for r in before.values())==q['baseline_vectors']
    view['inputs']['planned_funding_bridge_protocol_sha256']=sha(out/'protocol.json')
    (out/'precutoff_feature_view.json.gz').write_bytes(gzip.compress(json_bytes(view),mtime=0));write(work/'native_cursors.json',cursors)
    report=dict(status='passed',selected=len(records),finalized=len(entries),new_complete_source_ids=complete,
        bounded_in_scope=len(entries)-len(complete),pending_in_scope=len(records)-len(entries),available_coldcard_vectors=sum(r['features']is not None for r in rows.values()),
        preserved_old_vectors=q['baseline_vectors'],fresh_native_source_transaction_observations=sum(d['fresh_native_source_transaction_observations']for d in details),
        source_progress=details,unfinalized_evidence=unfinished,private_native_cursors_sha256=sha(work/'native_cursors.json'),
        composed_view_sha256=sha(out/'precutoff_feature_view.json.gz'),funding_closure_explicitly_planned=True,
        unknown_labels_cutoffs_and_current_statuses_unchanged=True,model_fits=0,new_scores=0)
    write(out/'coverage_audit.json',report);write(out/'independent_verification.json',dict(report,
        verification_basis='Saved endpoint/body fingerprints; separate immutable union replay; explicitly planned terminal funding closure; independent feature recount; unchanged rows and recorded dispatch clock'))
    return report
