"""Prepare a distinct checkpoint for the exact retained incomplete Coldcard queue."""
import argparse
from datetime import datetime
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys

BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE/'source_prefix_extension_20261110_01'))
from build_source_registry import json_bytes
from prepare_scope import validate_cached


def read(path):
    raw=path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix=='.gz' else raw)


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def retain_lineage(inputs,old_inputs,parent,out):
    """Keep every inherited file/hash pair even when descriptive keys collide."""
    for key,pin in old_inputs.items():
        path=(parent/pin['file']).resolve()
        if sha(path)!=pin['sha256']:raise ValueError('Inherited input changed: '+pin['file'])
        item=dict(file=os.path.relpath(path,out),sha256=pin['sha256'])
        if (item['file'],item['sha256']) in {(x['file'],x['sha256']) for x in inputs.values()}:continue
        name='inherited_'+key
        while name in inputs and inputs[name]!=item:name='inherited_'+name
        inputs[name]=item


def validate_selection(ids,entries,rows,previous):
    if not ids or len(ids)>20 or len(set(ids))!=len(ids):raise ValueError('Invalid fixed continuation queue')
    for sid in ids:
        if rows[sid]['features'] is not None:raise ValueError('Complete source selected')
        e=entries[sid]
        if e['status']!='bounded_incomplete' or e['features'] is not None or e['pages_fetched']!=previous:
            raise ValueError('Source is not an audited prefix at the preceding checkpoint')


def prepare(parent,out,max_pages):
    parent=parent.resolve();out=out.resolve()
    if not re.fullmatch(r'source_prefix_extension_[0-9]{8}_[0-9]{2}',out.name):raise ValueError('Unique dated scope name required')
    work=BASE/('source_cohort_work_'+out.name);old_work=BASE/('source_cohort_work_'+parent.name)
    if out.exists() or work.exists():raise FileExistsError('Never overwrite or restart a scope')
    old=read(parent/'protocol.json');resume=read(parent/'resume_checkpoint.json')
    if read(parent/'independent_verification.json')['status']!='passed':raise ValueError('Parent audit missing')
    if not read(parent/'private_cache_backup.json')['saved_privately']:raise ValueError('Save parent evidence before extending')
    previous=old['max_pages_per_address']
    if not previous<max_pages<=previous+64:raise ValueError('A finite checkpoint increment of at most 64 pages is required')
    ids=resume['continuation_required_source_ids'];entries=read(parent/'checkpoint.json.gz')['entries']
    baseline=read(parent/'precutoff_feature_view.json.gz');rows={r['source_id']:r for r in baseline['rows']}
    validate_selection(ids,entries,rows,previous)
    records={r['pilot_id']:r for r in read(old_work/'plan.json')};plan=[records[sid] for sid in ids]
    for r in plan:
        for key in ['address_sha256','payment_txid_sha256','cutoff_height','cutoff_block_hash']:
            if r[key]!=rows[r['pilot_id']][key]:raise ValueError('Frozen source identity changed')
    out.mkdir();work.mkdir()
    for name in ['requests','raw','results']:(work/name).mkdir()
    for name in ['audit_execution.py','verify_execution.py']:shutil.copyfile(parent/name,out/name)
    inputs={key:dict(file=os.path.relpath((parent/p['file']).resolve(),out),sha256=p['sha256']) for key,p in old['inputs'].items()}
    paths=dict(parent_protocol=parent/'protocol.json',parent_checkpoint=parent/'checkpoint.json.gz',
        parent_requests=parent/'request_manifest.json.gz',parent_audit=parent/'coverage_audit.json',
        parent_verification=parent/'independent_verification.json',parent_receipt=parent/'run_receipt.json',
        parent_resume=parent/'resume_checkpoint.json',parent_private_backup=parent/'private_cache_backup.json',
        baseline_view=parent/'precutoff_feature_view.json.gz',preparation_code=Path(__file__),
        finalization_code=BASE/'finalize_coldcard_checkpoint.py',workflow_tests=BASE/'test_checkpoint_workflow.py',
        execution_auditor=out/'audit_execution.py',execution_verifier=out/'verify_execution.py')
    for name in ['continuation_reconciliation.json','two_checkpoint_reconciliation.json']:
        if (parent/name).exists():paths['parent_'+name.removesuffix('.json')]=parent/name
    for key,path in paths.items():inputs[key]=dict(file=os.path.relpath(path,out),sha256=sha(path))
    (work/'plan.json').write_bytes(json_bytes(plan));(work/'preflight.json').write_bytes(json_bytes(plan[0]))
    locks=sorted(set(read(old_work/'historical_locks.json'))|{str(old_work/'collector.lock')})
    if not all(Path(p).parent.is_dir() for p in locks):raise ValueError('Historical lock directory missing')
    (work/'historical_locks.json').write_bytes(json_bytes(locks))
    manifest={(m['source_id'],m['key']):m for m in read(parent/'request_manifest.json.gz')}
    reused=[]
    for r in plan:
        saved=validate_cached(r,old_work,max_pages=previous)
        if len(saved)!=previous+1:raise ValueError('A saved contiguous page is missing')
        folder=work/'requests'/r['pilot_id'];folder.mkdir()
        for key,marker,body,meta in saved:
            approved=manifest[(r['pilot_id'],key)]
            if any(meta[k]!=approved[k] for k in ['source_id','key','http_status','sha256','endpoint_sha256']):raise ValueError('Saved/public response metadata differs')
            (folder/body.name).write_bytes(body.read_bytes())
            (folder/marker.name).write_bytes(json_bytes(dict(meta,offline_reused=True,reused_from_pass=parent.name)))
            reused.append(dict(source_id=r['pilot_id'],key=key,predecessor_pass=parent.name,sha256=meta['sha256'],endpoint_sha256=meta['endpoint_sha256']))
    budget=dict(ordinary_counter_gets=1,new_reference_gets_at_most=0,
        new_tail_pages_at_most=len(ids)*(max_pages-previous),fresh_reference_statuses_at_most=len(ids),
        funding_status_gets_at_most=sum(r['registry_input_slots'] for r in plan))
    budget['total_new_requests_at_most']=sum(budget.values())
    (out/'offline_reuse_manifest.json').write_bytes(json_bytes(dict(schema_version=1,responses=reused)))
    available=sum(r['features'] is not None for r in rows.values())
    capacity=dict(schema_version=1,selected_source_ids=ids,previous_page_checkpoint=previous,new_page_checkpoint=max_pages,
        saved_responses_reused=len(reused),saved_tail_pages_reused=len(ids)*previous,request_budget=budget,
        preceding_vectors_preserved=available,old_failed_or_consumed_markers_copied=False,provider_requests=0,model_fits=0,new_scores=0)
    (out/'capacity_and_cache_audit.json').write_bytes(json_bytes(capacity))
    for name in ['offline_reuse_manifest','capacity_and_cache_audit']:inputs['current_'+name]=dict(file=name+'.json',sha256=sha(out/(name+'.json')))
    retain_lineage(inputs,old['inputs'],parent,out)
    created=datetime.strptime(out.name.split('_')[-2],'%Y%m%d').date().isoformat()
    q=dict(old,pass_name=out.name,parent_scope=parent.name,created_on=created,source_ids=ids,inputs=inputs,
        baseline_vectors=available,all_gap_targets=dict(coldcard=len(rows)-available,cryptobilis=37,total=len(rows)-available+37),
        previous_bound=previous,max_pages_per_address=max_pages,batch_size=20,max_batches=1,
        private_plan_sha256=sha(work/'plan.json'),private_lock_manifest_sha256=sha(work/'historical_locks.json'),
        offline_reused_responses=len(reused),request_budget=budget,
        authorization='Hugo authorizes continuing the exact retained source queue, preserving completed work and extending operational checkpoints.',
        coverage_scope='Distinct deeper checkpoint for the exact retained incomplete queue; preserve every closed scope and request only pages beyond the validated saved cursor.',
        checkpoint_policy='A work checkpoint is not permanent exclusion. Preserve null features until anchored exhaustion and funding closure verify.')
    (out/'protocol.json').write_bytes(json_bytes(q))
    (out/'resume_checkpoint.json').write_bytes(json_bytes(dict(schema_version=1,pass_name=out.name,status='prepared_not_started',
        source_ids=ids,network_source_ids=ids,finalized_source_ids=[],collection_can_resume=False,automation_enabled=False,
        protocol_sha256=sha(out/'protocol.json'),provider_requests=0,model_fits=0)))
    for pin in inputs.values():
        if sha((out/pin['file']).resolve())!=pin['sha256']:raise ValueError('Prepared pin changed')
    verification=dict(schema_version=1,status='passed',selected=len(ids),saved_responses_verified=len(reused),
        input_pins_verified=len(inputs),all_inherited_pins_retained=True,private_plan_and_lock_manifest_verified=True,
        protocol_sha256=sha(out/'protocol.json'),provider_requests=0,model_fits=0)
    (out/'preparation_verification.json').write_bytes(json_bytes(verification))
    return dict(verification,request_budget=budget)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('parent',type=Path);p.add_argument('output',type=Path);p.add_argument('max_pages',type=int)
    a=p.parse_args();print(json.dumps(prepare(a.parent,a.output,a.max_pages),sort_keys=True))
