"""Complete-block bridges with an explicitly budgeted reference-funding closure."""
import gzip
import hashlib
from pathlib import Path

from build_source_registry import json_bytes
from prepare_frontier_checkpoint import read,sha
from independent_mempool_native import validate_page
from independent_mempool_pilot import PROVIDER,require,status_check,core
from independent_mempool_bridge import choose_bridge,merge_transaction
import collect_reference_tail as tail


def legacy_source(record,work,pins):
    folder=work/'legacy'/record['pilot_id']
    require(set(pins)=={'reference'}|{f'tail_{i:04d}'for i in range(len(pins)-1)},'Legacy cache has a page gap')
    def response(key,endpoint):
        meta=read(folder/(key+'.json'));body=folder/(key+'.json.gz');pin=pins[key]
        require(meta.get('http_status')==200 and 'error_type'not in meta,'Unsuccessful saved legacy response')
        require(sha(body)==meta['sha256']==pin['sha256'],'Legacy body fingerprint differs')
        require(meta['endpoint_sha256']==pin['endpoint_sha256']==hashlib.sha256(endpoint.encode()).hexdigest(),'Legacy cursor endpoint differs')
        return read(body)
    anchor=response('reference','/tx/'+record['payment_txid']);tail.anchor_check(record,anchor)
    pages=[];values=[];seen={record['payment_txid']};height=record['cutoff_height'];cursor=record['payment_txid']
    for i in range(len(pins)-1):
        page=response(f'tail_{i:04d}','/address/'+record['address']+'/txs/chain/'+cursor)
        height=validate_page(record,page,seen,height)
        require(bool(page),'A terminal legacy cache needs a separate cross-provider completeness validation')
        pages.append(page);values.extend(page);cursor=page[-1]['txid']
    require(bool(values),'No verified legacy boundary')
    return anchor,pages,values,cursor


def funding_plan(record,anchor,transactions):
    own=tail.anchor_check(record,anchor);ids={t['txid']for t in transactions}
    return dict(reference_parent_txids=sorted({v['txid']for v in own}),
        missing_from_saved_prefix=sorted({v['txid']for v in own if v['txid']not in ids}),
        rule='Only after terminal pagination: every still-absent reference parent gets a fresh status and must belong to the excluded reference block; prior-block funding may not be silently omitted')


def collect(record,requests,work,q,pins):
    require(sha(work/'legacy_funding_plan.json')==q['private_legacy_funding_plan_sha256'],'Planned funding closure changed')
    anchor,oldpages,old,_=legacy_source(record,work,pins)
    planned=read(work/'legacy_funding_plan.json')[record['pilot_id']]
    require(planned==funding_plan(record,anchor,old),'Legacy funding plan differs')
    bridge,boundary=choose_bridge(record,anchor,old)
    status_check(record,requests.get(record,'reference_before','/tx/'+record['payment_txid']+'/status'))
    require(core(requests.get(record,'boundary','/tx/'+bridge['txid']))==core(bridge),'Cross-provider bridge changed')
    existing={t['txid']:t for t in old};old_ids=set(existing);seen={bridge['txid']}
    cursor=bridge['txid'];height=bridge['status']['block_height'];exhausted=False;pages=overlap=0
    for i in range(q['maximum_new_native_pages']):
        page=requests.get(record,f'native_tail_{i:04d}','/address/'+record['address']+'/txs/chain/'+cursor)
        require(isinstance(page,list)and len(page)<=25,'Invalid native cursor page');pages+=1
        if not page:exhausted=True;break
        for tx in page:
            require(tx['status'].get('confirmed')is True and tx['status'].get('block_hash')and tx['status']['block_height']<=height,'Unanchored native page order')
            height=tx['status']['block_height']
            if not merge_transaction(record,tx,existing,seen,boundary):overlap+=1
        cursor=page[-1]['txid']
    after=requests.get(record,'reference_after','/tx/'+record['payment_txid']+'/status');status_check(record,after)
    parents={}
    if exhausted:
        for txid in planned['reference_parent_txids']:
            if txid not in existing:
                value=requests.get(record,'parent_'+hashlib.sha256(txid.encode()).hexdigest(),'/tx/'+txid+'/status')
                status_check(record,value);parents[txid]=value
    values=sorted(existing.values(),key=lambda t:(-t['status']['block_height'],t['txid']))
    result=tail.tail_check(record,anchor,values,exhausted,after,parents)
    if result['features']is not None:
        result['audit'].update(provider=PROVIDER,completeness_basis='Verified complete-block legacy bridge, exhausted native walk and explicitly planned reference-funding closure')
    raw=dict(address=record['address'],anchor=anchor,transactions=values,anchor_after=after,parent_statuses=parents,
        pagination_exhausted=exhausted,pages_fetched=len(oldpages)+pages,legacy_provider_pages=len(oldpages),
        independent_provider_pages=pages,actual_native_last_cursor=cursor,bridge_txid=bridge['txid'],
        bridge_height=bridge['status']['block_height'],partial_boundary_height=boundary,cross_provider_overlap_verified=overlap,
        additional_source_transaction_observations=sum(t['status']['block_height']<record['cutoff_height']for k,t in existing.items()if k not in old_ids))
    path=work/'raw'/f"{record['pilot_id']}.json.gz";path.write_bytes(gzip.compress(json_bytes(raw),mtime=0))
    entry=dict(source_id=record['pilot_id'],raw_file='raw/'+path.name,raw_sha256=sha(path),pages_fetched=raw['pages_fetched'],**result)
    (work/'results'/path.name).write_bytes(gzip.compress(json_bytes(entry),mtime=0))
    return entry
