"""Extend the fifteen retained 32-page prefixes to a resumable 64-page checkpoint."""
import gzip
import hashlib
import json
import os
from pathlib import Path
import sys

OUT=Path(__file__).resolve().parent
BASE=OUT.parent
PARENT=BASE/'source_prefix_extension_20261110_02'
WORK=BASE/('source_cohort_work_'+OUT.name)
sys.path.insert(0,str(BASE/'source_prefix_extension_20261110_01'))
sys.path.insert(0,str(BASE))
from build_source_registry import json_bytes
from prepare_scope import validate_cached


def read(path):
    b=path.read_bytes()
    return json.loads(gzip.decompress(b) if path.suffix=='.gz' else b)


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert not WORK.exists() and not (OUT/'protocol.json').exists()
    parent=read(PARENT/'protocol.json');view=read(PARENT/'precutoff_feature_view.json.gz')
    rows={r['source_id']:r for r in view['rows']}
    assert sum(r['features'] is not None for r in rows.values())==1387
    selected_from={};records={}
    for name in ['source_prefix_extension_20261110_01','source_prefix_extension_20261110_02']:
        scope=BASE/name;work=BASE/('source_cohort_work_'+name)
        assert read(scope/'independent_verification.json')['status']=='passed'
        for r in read(work/'plan.json'):
            if r['pilot_id'] in records:assert records[r['pilot_id']]==r
            records[r['pilot_id']]=r
        for sid,e in read(scope/'checkpoint.json.gz')['entries'].items():
            if e['status']=='bounded_incomplete':
                assert e['pages_fetched']==32 and e['features'] is None
                selected_from[sid]=(scope,work)
    ids=sorted(selected_from);assert len(ids)==15
    reconciliation=read(PARENT/'original_twenty_reconciliation.json')
    assert set(ids).isdisjoint(reconciliation['new_complete_source_ids'])
    plan=[records[sid] for sid in ids]
    for r in plan:
        assert rows[r['pilot_id']]['features'] is None
        for key in ['address_sha256','payment_txid_sha256','cutoff_height','cutoff_block_hash']:
            assert rows[r['pilot_id']][key]==r[key]
    inputs={}
    for key,pin in parent['inputs'].items():
        p=(PARENT/pin['file']).resolve();assert sha(p)==pin['sha256']
        inputs[key]=dict(file=os.path.relpath(p,OUT),sha256=pin['sha256'])
    pins=dict(parent_protocol=PARENT/'protocol.json',parent_checkpoint=PARENT/'checkpoint.json.gz',
        parent_requests=PARENT/'request_manifest.json.gz',parent_audit=PARENT/'coverage_audit.json',
        parent_verification=PARENT/'independent_verification.json',parent_receipt=PARENT/'run_receipt.json',
        parent_resume=PARENT/'resume_checkpoint.json',parent_stop=PARENT/'collection_stop.json',
        parent_private_backup=PARENT/'private_cache_backup.json',
        parent_reconciliation=PARENT/'original_twenty_reconciliation.json',
        baseline_view=PARENT/'precutoff_feature_view.json.gz',preparation_code=Path(__file__),
        execution_auditor=OUT/'audit_execution.py',execution_verifier=OUT/'verify_execution.py',
        deeper_resume_tests=OUT/'test_deeper_resume.py')
    for key,p in pins.items():inputs[key]=dict(file=os.path.relpath(p,OUT),sha256=sha(p))
    WORK.mkdir()
    for name in ['requests','raw','results']:(WORK/name).mkdir()
    (WORK/'plan.json').write_bytes(json_bytes(plan))
    (WORK/'preflight.json').write_bytes(json_bytes(plan[0]))
    old_work=BASE/('source_cohort_work_'+PARENT.name)
    locks=sorted(set(read(old_work/'historical_locks.json'))|{str(old_work/'collector.lock')})
    assert all(Path(p).parent.is_dir() for p in locks)
    (WORK/'historical_locks.json').write_bytes(json_bytes(locks))
    reused=[];sizes=[]
    for r in plan:
        sid=r['pilot_id'];scope,work=selected_from[sid]
        saved=validate_cached(r,work,max_pages=32);assert len(saved)==33
        public={(m['source_id'],m['key']):m for m in read(scope/'request_manifest.json.gz')}
        folder=WORK/'requests'/sid;folder.mkdir()
        raw_bytes=0
        for key,marker,body,m in saved:
            approved=public[(sid,key)]
            assert all(m[k]==approved[k] for k in ['source_id','key','http_status','sha256','endpoint_sha256'])
            (folder/body.name).write_bytes(body.read_bytes())
            (folder/marker.name).write_bytes(json_bytes(dict(m,offline_reused=True,reused_from_pass=scope.name)))
            reused.append(dict(source_id=sid,key=key,predecessor_pass=scope.name,sha256=m['sha256'],endpoint_sha256=m['endpoint_sha256']))
            if key.startswith('tail_'):raw_bytes+=len(gzip.decompress(body.read_bytes()))
        sizes.append(dict(source_id=sid,saved_pages=32,decompressed_saved_page_bytes=raw_bytes))
    assert len(reused)==495
    (OUT/'offline_reuse_manifest.json').write_bytes(json_bytes(dict(schema_version=1,responses=reused)))
    budget=dict(ordinary_counter_gets=1,new_reference_gets_at_most=0,new_tail_pages_at_most=15*32,
        fresh_reference_statuses_at_most=15,funding_status_gets_at_most=sum(r['registry_input_slots'] for r in plan))
    budget['total_new_requests_at_most']=sum(budget.values())
    capacity=dict(schema_version=1,scope='deepen_all_fifteen_recent_bounded_prefixes',selected_source_ids=ids,
        old_page_checkpoint=32,new_page_checkpoint=64,saved_responses_reused=495,saved_tail_pages_reused=480,
        request_budget=budget,observed_saved_payload_sizes=sizes,
        no_saved_tail_page_requested_again=True,old_failed_or_consumed_markers_copied=False,
        complete_prefixes_selected=False,provider_requests=0,model_fits=0,new_scores=0,
        bounded_outcome_policy='Retain evidence and a continuation queue; the checkpoint is not permanent exclusion. Features stay null until exhaustion and closure verify.')
    (OUT/'capacity_and_cache_audit.json').write_bytes(json_bytes(capacity))
    for name in ['offline_reuse_manifest','capacity_and_cache_audit']:
        inputs['current_'+name]=dict(file=name+'.json',sha256=sha(OUT/(name+'.json')))
    present={(p['file'],p['sha256']) for p in inputs.values()}
    for key,pin in parent['inputs'].items():
        p=(PARENT/pin['file']).resolve();rel=os.path.relpath(p,OUT)
        if (rel,pin['sha256']) not in present:inputs['retained_'+key]=dict(file=rel,sha256=pin['sha256'])
    q=dict(parent,pass_name=OUT.name,created_on='2026-11-10',source_ids=ids,inputs=inputs,
        baseline_vectors=1387,all_gap_targets=dict(coldcard=113,cryptobilis=37,total=150),
        authorization='Hugo asks to continue after discussing that the page limit is operational and that incomplete histories should be progressively completed.',
        coverage_scope='Distinct 32-to-64-page continuation for all fifteen recent bounded sources, preserving the old scopes and using only verified saved anchors/tails.',
        previous_bound=32,max_pages_per_address=64,batch_size=20,max_batches=1,
        private_plan_sha256=sha(WORK/'plan.json'),private_lock_manifest_sha256=sha(WORK/'historical_locks.json'),
        offline_reused_responses=495,request_budget=budget,
        checkpoint_policy='64 is a work checkpoint; any still-unexhausted source remains in a separately pinned continuation queue, without replacement or fabricated features.')
    q.pop('predecessor_interruption',None);q.pop('consumed_intent_policy',None)
    (OUT/'protocol.json').write_bytes(json_bytes(q))
    (OUT/'resume_checkpoint.json').write_bytes(json_bytes(dict(schema_version=1,pass_name=OUT.name,
        status='prepared_not_started',source_ids=ids,network_source_ids=ids,finalized_source_ids=[],
        collection_can_resume=False,automation_enabled=False,protocol_sha256=sha(OUT/'protocol.json'),
        next_action='Hold all local/historical locks, check live lease/cooldown, publish/read back the exact running lease, then one ordinary counter HTTP200 before new pages.')))
    print(json.dumps(dict(selected=len(ids),saved_responses=495,request_budget=budget,input_pins=len(inputs),protocol_sha256=sha(OUT/'protocol.json')),sort_keys=True))


if __name__=='__main__':main()
