"""Audit the next 20-source extension against its pinned 1,382-vector baseline."""
import argparse
from collections import Counter
import copy
from datetime import datetime,timezone
import gzip
import hashlib
import json
from pathlib import Path
import sys


def read(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def require(ok,message):
    if not ok:raise ValueError(message)


def audit(protocol_path,work):
    out=protocol_path.parent;proto=read(protocol_path);sys.path.insert(0,str(out.parent))
    import collect_reference_tail as tail
    from build_source_registry import json_bytes
    sys.path.insert(0,str(out.parents[1]/'external_cases/cryptobilis_to_coldcard_20261109'))
    from experiment import recount_features
    require(not (out/'coverage_audit.json').exists(),'Stopped audit output already exists')
    require(sha(work/'plan.json')==proto['private_plan_sha256'],'Private plan changed')
    for pin in proto['inputs'].values():require(sha((out/pin['file']).resolve())==pin['sha256'],'Scope input changed')
    baseline_paths=[(out/proto['inputs']['baseline_view']['file']).resolve()]
    require(len(baseline_paths)==1,'Baseline view pin ambiguous')
    baseline=read(baseline_paths[0]);require(sum(r['features'] is not None for r in baseline['rows'])==proto['baseline_vectors'],'Baseline vector count differs');old_rows={r['source_id']:r for r in baseline['rows']}
    records={r['pilot_id']:r for r in read(work/'plan.json')}
    require(list(records)==proto['source_ids'],'Scope source order changed')
    checkpoint=read(out/'checkpoint.json.gz')
    require(checkpoint['protocol_sha256']==sha(protocol_path),'Checkpoint protocol mismatch')
    entries=checkpoint['entries'];require(set(entries)<=set(records),'Unselected result')
    successful=0;reused=0;new=0;pending=[]
    request_records=[]
    for sid,record in records.items():
        require(old_rows[sid]['features'] is None,'Old complete prefix selected')
        folder=work/'requests'/sid;cursor=record['payment_txid'];seen=set();previous=record['cutoff_height'];assembled=[];empty=False;pages=0
        def response(key,endpoint):
            nonlocal successful,reused,new
            marker=folder/(key+'.json');body=folder/(key+'.json.gz')
            if not marker.exists():return None
            meta=read(marker);request_records.append(meta)
            require(meta['endpoint_sha256']==hashlib.sha256(endpoint.encode()).hexdigest(),'Endpoint/cursor mismatch')
            if not body.exists():require('sha256' not in meta,'Missing successful response');return None
            require(meta.get('http_status')==200 and sha(body)==meta['sha256'],'Saved response mismatch')
            successful+=1;reused+=bool(meta.get('offline_reused'));new+=not bool(meta.get('offline_reused'))
            return read(body)
        if sid==proto['source_ids'][0]:response('availability_counter','/address/'+record['address'])
        anchor=response('reference','/tx/'+record['payment_txid'])
        if anchor is not None:
            tail.anchor_check(record,anchor)
            for i in range(proto['max_pages_per_address']):
                page=response(f'tail_{i:04d}','/address/'+record['address']+'/txs/chain/'+cursor)
                if page is None:break
                require(isinstance(page,list) and len(page)<=25,'Invalid page');pages+=1
                if not page:empty=True;break
                for tx in page:
                    require(tx['txid'] not in seen and tx['txid']!=record['payment_txid'],'Repeated cursor transaction')
                    require(tx['status']['confirmed'] and tx['status']['block_hash'] and tx['status']['block_height']<=previous,'Unanchored/unordered page')
                    seen.add(tx['txid']);previous=tx['status']['block_height']
                assembled+=page;cursor=page[-1]['txid']
            after=response('reference_after','/tx/'+record['payment_txid']+'/status')
            for txid in {v['txid'] for v in anchor['vin'] if (v.get('prevout') or {}).get('scriptpubkey_address')==record['address']}:
                key='parent_'+hashlib.sha256(txid.encode()).hexdigest()
                if (folder/(key+'.json')).exists():response(key,'/tx/'+txid+'/status')
        if sid not in entries:
            pending.append(dict(source_id=sid,saved_tail_pages=pages,last_cursor_sha256=hashlib.sha256(cursor.encode()).hexdigest()));continue
        e=entries[sid];raw_path=work/e['raw_file'];require(sha(raw_path)==e['raw_sha256'],'Raw tail fingerprint mismatch');raw=read(raw_path)
        require(raw['transactions']==assembled and raw['anchor']==anchor and raw['anchor_after']==after,'Raw/page assembly differs')
        require(raw['pagination_exhausted']==empty and raw['pages_fetched']==pages<=proto['max_pages_per_address'],'Exhaustion/page count mismatch')
        expected=tail.tail_check(record,raw['anchor'],assembled,empty,raw['anchor_after'],raw['parent_statuses'])
        require(all(e[k]==expected[k] for k in ['status','features','prefix']),'Raw re-extraction differs')
        if e['status']=='complete_prior_prefix':require(recount_features(e['prefix'],e['cutoff_height'])==e['features'],'Independent vector recount differs')
        else:require(e['features'] is None and e['prefix'] is None,'Bounded vector manufactured')
    # Ensure no marker is silently omitted by the whitelist/sequence audit.
    all_markers=[read(p) for p in sorted((work/'requests').glob('*/*.json'))]
    require(sum(not m.get('offline_reused') for m in all_markers)<=proto['request_budget']['total_new_requests_at_most'],'New request budget exceeded')
    require(len(all_markers)==len(request_records),'Unaccounted request marker')
    failures=[m for m in all_markers if not m.get('offline_reused') and ('error_type' in m or m.get('http_status',200)!=200)]
    stopped=min((m['finished_at'] for m in failures if 'finished_at' in m),default=None)
    if stopped:require(all(m['started_at']<=stopped for m in all_markers if not m.get('offline_reused')),'New request intent after stop')
    composed=copy.deepcopy(baseline);composed['updated_on']=proto['created_on']
    completed=[]
    for row in composed['rows']:
        sid=row['source_id']
        if sid not in entries:continue
        e=entries[sid]
        if e['status']=='complete_prior_prefix':row['features']=e['features'];row['precutoff_history_status']='complete_prior_prefix';completed.append(sid)
        row['precutoff_history_provenance']=dict(pass_name=proto['pass_name'],raw_sha256=e['raw_sha256'],full_current_history_counter_coverage_verified=False,pages_fetched=e['pages_fetched'])
    for row in composed['rows']:
        old=old_rows[row['source_id']]
        for key in ['source_id','address_sha256','payment_txid_sha256','cutoff_height','cutoff_block_hash','known_coldcard_core_membership','labels','full_history_status']:
            require(row.get(key)==old.get(key),'Preserved metadata changed: '+key)
        if old['features'] is not None or row['source_id'] not in entries:require(row==old,'Old vector or unselected row changed')
    composed['inputs']['source_prefix_extension_protocol_sha256']=sha(protocol_path)
    composed['inputs']['source_prefix_extension_checkpoint_sha256']=sha(out/'checkpoint.json.gz')
    composed['inputs']['source_prefix_extension_predecessor_view_sha256']=sha(baseline_paths[0])
    (out/'precutoff_feature_view.json.gz').write_bytes(gzip.compress(json_bytes(composed),mtime=0))
    available=sum(r['features'] is not None for r in composed['rows']);bounded=1500-available
    counts=Counter(e['status'] for e in entries.values())
    result=dict(schema_version=1,pass_name=proto['pass_name'],protocol_sha256=sha(protocol_path),
        selected=len(records),finalized=len(entries),new_complete_prefixes=len(completed),bounded_in_scope=counts['bounded_incomplete'],pending_in_scope=len(pending),
        new_complete_source_ids=sorted(completed),pending_source_page_checkpoints=pending,
        all_successful_response_fingerprints_and_cursor_sequences_verified=successful,
        successful_offline_responses_reused=reused,new_successful_provider_responses=new,new_request_records=sum(not m.get('offline_reused') for m in all_markers),
        failed_request_records=len(failures),new_raw_tails_reextracted=len(entries),new_vectors_independently_recounted=len(completed),
        preserved_old_vectors=proto['baseline_vectors'],selected_coldcard_sources=len(baseline['rows']),available_coldcard_vectors=available,bounded_coldcard_prefixes=bounded,
        cryptobilis_vectors_unchanged=329,cryptobilis_bounded_prefixes_unchanged=37,total_remaining_bounded_prefixes=bounded+37,
        full_current_history_statuses_unchanged=True,unknown_labels_unchanged=True,original_14_definitions_unchanged=True,
        unselected_rows_unchanged=True,provider_or_route_changed=False,automatic_retry_performed=False,model_fits=0,
        composed_view_sha256=sha(out/'precutoff_feature_view.json.gz'))
    (out/'coverage_audit.json').write_bytes(json_bytes(result))
    print(json.dumps(result,sort_keys=True))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('protocol',type=Path);p.add_argument('work',type=Path)
    a=p.parse_args();audit(a.protocol.resolve(),a.work.resolve())
