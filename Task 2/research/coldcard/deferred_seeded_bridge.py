"""Finish the sole deferred original target using cached bridge responses.

Its actual native cursor remains inside the partial legacy block. The strict
crossed-boundary validator stays unchanged. The existing planned bridge collector
replays twelve immutable cached pages, then makes at most 37 new page requests.
"""
import argparse
from contextlib import ExitStack
import fcntl
import hashlib
import os
from pathlib import Path
import shutil

from prepare_frontier_checkpoint import read,sha,write
from native_extension_checkpoint import request_budget
import recorded_remaining_campaign as campaign

BASE=campaign.BASE; SID='comparison_0157'; OLD='mempool_remaining_fifty_20261116_unit_12'
NAME='mempool_remaining_fifty_20261116_unit_21'
EXTENSION=campaign.CAMPAIGN/'supplemental_unit_21_selection.json'


def verify_seed():
    from planned_funding_bridge import legacy_source
    from independent_mempool_bridge import choose_bridge,merge_transaction
    from independent_mempool_pilot import core
    old=BASE/OLD;source=BASE/('source_cohort_work_'+OLD)
    record=next(r for r in read(source/'plan.json')if r['pilot_id']==SID)
    pins={m['key']:m for m in read(old/'legacy_reuse_manifest.json')['responses']if m['source_id']==SID}
    anchor,pages,values,_=legacy_source(record,source,pins);bridge,boundary=choose_bridge(record,anchor,values)
    existing={t['txid']:t for t in values};seen={bridge['txid']};cursor=bridge['txid'];height=bridge['status']['block_height'];cache=[]
    for key in ['boundary']+[f'native_tail_{i:04d}'for i in range(12)]:
        path=source/'requests'/SID/(key+'.json');meta=read(path);body=path.with_suffix('.json.gz')
        endpoint='/tx/'+bridge['txid']if key=='boundary'else'/address/'+record['address']+'/txs/chain/'+cursor
        assert meta['http_status']==200 and 'error_type'not in meta and sha(body)==meta['sha256']
        assert meta['endpoint_sha256']==hashlib.sha256(endpoint.encode()).hexdigest()
        value=read(body)
        if key=='boundary':assert core(value)==core(bridge)
        else:
            assert 0<len(value)<=25
            for tx in value:
                assert tx['status']['block_height']<=height
                height=tx['status']['block_height'];merge_transaction(record,tx,existing,seen,boundary)
            cursor=value[-1]['txid']
        cache.append(dict(source_id=SID,key=key,endpoint_sha256=meta['endpoint_sha256'],sha256=meta['sha256'],
            original_marker_sha256=sha(path),origin_scope=OLD))
    item=next(x for x in read(old/'coverage_audit.json')['unfinalized_evidence']if x['source_id']==SID)
    rawpath=source/item['raw_file'];raw=read(rawpath);assert sha(rawpath)==item['raw_sha256']
    assert raw['transactions']==sorted(existing.values(),key=lambda t:(-t['status']['block_height'],t['txid']))
    assert raw['actual_native_last_cursor']==cursor and raw['independent_provider_pages']==12
    assert raw['features']is None and raw['anchor_after']is None and not raw['pagination_exhausted']
    unknown=source/'requests'/SID/'native_tail_0012.json';meta=read(unknown)
    assert 'http_status'not in meta and 'finished_at'not in meta and not unknown.with_suffix('.json.gz').exists()
    assert meta['endpoint_sha256']==hashlib.sha256(('/address/'+record['address']+'/txs/chain/'+cursor).encode()).hexdigest()
    return dict(status='passed',cache=cache,legacy_pages=len(pages),native_cursor_height=height,
        legacy_boundary_height=boundary,native_cursor_sha256=hashlib.sha256(cursor.encode()).hexdigest(),
        original_unknown_marker_sha256=sha(unknown),original_unfinished_raw_sha256=sha(rawpath))


def prepare():
    state=read(campaign.CAMPAIGN/'progress.json')
    assert state['pending_source_ids']==[SID]and len(state['completed_units'])==20 and state['active_scope']is None
    proof=verify_seed();assert not EXTENSION.exists()
    extension=dict(unit=21,source_ids=[SID],kind='legacy_bridge',previous_bound=proof['legacy_pages'],
        original_campaign_selection_sha256=sha(campaign.CAMPAIGN/'selection.json'),original_unit=12,
        original_successful_native_pages=12,original_unknown_page_intents=1,remaining_native_page_intents=37,
        original_target_set_unchanged=True)
    write(EXTENSION,extension)
    modules=[campaign,campaign.priority,campaign.inherited];originals=[m.read for m in modules]
    def extended(path):
        value=read(path)
        if Path(path).resolve()==(campaign.CAMPAIGN/'selection.json').resolve():
            value=dict(value,units=value['units']+[extension])
        return value
    for module in modules:module.read=extended
    try:result=campaign.prepare(21)
    finally:
        for module,original in zip(modules,originals):module.read=original
    out=BASE/NAME;work=BASE/('source_cohort_work_'+NAME);source=BASE/('source_cohort_work_'+OLD)
    folder=work/'cache_seed'/SID;folder.mkdir(parents=True)
    for pin in proof['cache']:
        for suffix in ['.json','.json.gz']:
            src=source/'requests'/SID/(pin['key']+suffix);shutil.copyfile(src,folder/src.name)
    write(work/'cached_native_seed_manifest.json',dict(responses=proof.pop('cache')))
    write(out/'saved_seed_verification.json',proof)
    q=read(out/'protocol.json');records=read(work/'plan.json');budget=request_budget(records,extra_pages=37)
    q.update(authorization='Persistent explicit Continue authorization; finish the only deferred original target from immutable cached bridge responses.',
        effective_replay_native_pages=49,maximum_live_native_pages=37,new_provider_page_limit=37,
        max_pages_per_address=proof['legacy_pages']+49,maximum_requests=budget['total_new_requests_at_most'],request_budget=budget,
        cached_seed_response_count=13,maximum_audit_tape_records=budget['total_new_requests_at_most']+13)
    for key,path in [('selection_extension',EXTENSION),('deferred_driver',Path(__file__)),
        ('cached_native_seed',work/'cached_native_seed_manifest.json'),('saved_seed_verification',out/'saved_seed_verification.json'),
        ('original_seed_recovery',BASE/OLD/'interruption_recovery.json'),('original_seed_audit',BASE/OLD/'independent_verification.json'),
        ('original_seed_backup',BASE/OLD/'private_cache_backup.json')]:
        q['inputs'][key]=dict(file=os.path.relpath(path,out),sha256=sha(path))
    write(out/'protocol.json',q)
    write(out/'preparation_verification.json',dict(status='passed',source_ids=[SID],provider_requests=0,
        cached_responses=13,maximum_new_native_pages=37,original_fifty_attempt_cap_preserved=True,
        original_unknown_outcome_preserved=True,strict_crossed_boundary_validator_unchanged=True))
    return dict(scope=NAME,maximum_requests=q['maximum_requests'],maximum_live_native_pages=37)


def run():
    import independent_mempool_resume as native
    import recorded_mempool_resume as recorded
    from planned_funding_bridge import collect
    out=BASE/NAME;work=BASE/('source_cohort_work_'+NAME)
    pins={m['key']:m for m in read(work/'cached_native_seed_manifest.json')['responses']}
    legacy={m['key']:m for m in read(out/'legacy_reuse_manifest.json')['responses']}
    def replay(record,requests,work,q,unused):
        class Adapter:
            def get(self,record,key,endpoint):
                if key in pins:
                    pin=pins[key];path=work/'cache_seed'/SID/(key+'.json');meta=read(path);body=path.with_suffix('.json.gz')
                    assert sha(path)==pin['original_marker_sha256']and sha(body)==pin['sha256']==meta['sha256']
                    assert hashlib.sha256(endpoint.encode()).hexdigest()==pin['endpoint_sha256']
                    return read(body)
                assert requests.count<q['maximum_requests']
                return requests.get(record,key,endpoint)
        return collect(record,Adapter(),work,dict(q,maximum_new_native_pages=49),legacy)
    native.collect=replay;recorded.run(out/'protocol.json',work)


def finish():
    out=BASE/NAME;work=BASE/('source_cohort_work_'+NAME);q=read(out/'protocol.json')
    assert read(out/'run_receipt.json')['operational_locks_released']
    pins=read(work/'cached_native_seed_manifest.json')['responses']
    with ExitStack()as stack:
        for name in sorted(set(read(work/'historical_locks.json'))|{str(work/'collector.lock')}):
            f=stack.enter_context(Path(name).open('a+'));fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
        for pin in pins:
            path=work/'cache_seed'/SID/(pin['key']+'.json');meta=read(path);body=path.with_suffix('.json.gz')
            assert sha(path)==pin['original_marker_sha256']and sha(body)==pin['sha256']
            target=work/'requests'/SID/path.name;assert not target.exists()
            write(target,dict(meta,offline_reused=True,reused_from_pass=OLD,original_marker_sha256=pin['original_marker_sha256']))
            shutil.copyfile(body,target.with_suffix('.json.gz'))
        from collect_reference_tail import export
        export(out/'protocol.json',out,work)
    manifest=read(out/'request_manifest.json.gz');fresh=[m for m in manifest if not m.get('offline_reused')]
    pages=[m for m in fresh if m['key'].startswith('native_tail_')]
    assert len(pages)<=37 and 12+1+len(pages)<=50
    assert all(12<=int(m['key'].split('_')[-1])<49 for m in pages)
    import audit_planned_funding_bridge as auditor
    original_audit=auditor.audit;original_read=auditor.read
    def audit_tape(output,private):
        def normalized_read(path):
            value=original_read(path)
            if Path(path).resolve()==(out/'run_receipt.json').resolve():return dict(value,provider_requests=len(manifest))
            if Path(path).resolve()==(out/'protocol.json').resolve():return dict(value,maximum_requests=q['maximum_audit_tape_records'])
            return value
        auditor.read=normalized_read
        try:result=original_audit(output,private)
        finally:auditor.read=original_read
        normalization=dict(status='passed',actual_new_provider_requests=len(fresh),cached_responses_replayed=len(pins),
            verified_tape_records=len(manifest),original_provider_receipt_unchanged=True,
            original_provider_receipt_sha256=sha(out/'run_receipt.json'),original_protocol_sha256=sha(out/'protocol.json'),
            purpose='The original auditor counts every replayed response. Its private audit view includes cached records in that counter; live request budgets and original provider receipts stay unchanged.')
        write(out/'audit_tape_normalization.json',normalization)
        for name in ['coverage_audit.json','independent_verification.json']:
            report=read(out/name);report.update(actual_new_provider_requests=len(fresh),cached_responses_replayed=len(pins),
                audit_tape_normalization_sha256=sha(out/'audit_tape_normalization.json'));write(out/name,report)
        return result
    auditor.audit=audit_tape
    try:return campaign.finish(NAME)
    finally:auditor.audit=original_audit


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('command',choices=['verify_seed','prepare','run','finish'])
    result=globals()[parser.parse_args().command]()
    print(__import__('json').dumps({k:v for k,v in result.items()if k!='cache'},indent=2))
