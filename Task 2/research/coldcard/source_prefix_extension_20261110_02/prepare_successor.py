"""Prepare only the ten unfinished IDs after an execution-server interruption."""
import gzip
import hashlib
import json
import os
from pathlib import Path
import sys

OUT = Path(__file__).resolve().parent
BASE = OUT.parent
PARENT = BASE/'source_prefix_extension_20261110_01'
WORK = BASE/('source_cohort_work_'+OUT.name)
PARENT_WORK = BASE/('source_cohort_work_'+PARENT.name)
sys.path.insert(0, str(BASE))
sys.path.insert(0, str(PARENT))
from build_source_registry import json_bytes
from prepare_scope import validate_cached


def read(path):
    data=path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix=='.gz' else data)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert not (OUT/'protocol.json').exists() and not WORK.exists()
    parent=read(PARENT/'protocol.json')
    checkpoint=read(PARENT/'checkpoint.json.gz')
    previous=read(PARENT/'precutoff_feature_view.json.gz')
    ids=[sid for sid in parent['source_ids'] if sid not in checkpoint['entries']]
    assert len(ids)==10 and set(ids).isdisjoint(checkpoint['entries'])
    assert read(PARENT/'independent_verification.json')['status']=='passed'
    rows={r['source_id']:r for r in previous['rows']}
    assert sum(r['features'] is not None for r in rows.values())==1383
    records={r['pilot_id']:r for r in read(PARENT_WORK/'plan.json')}
    selected=[records[sid] for sid in ids]
    for r in selected:
        assert rows[r['pilot_id']]['features'] is None
        for key in ['address_sha256','payment_txid_sha256','cutoff_height','cutoff_block_hash']:
            assert r[key]==rows[r['pilot_id']][key]
    inputs={}
    for key,pin in parent['inputs'].items():
        path=(PARENT/pin['file']).resolve()
        assert sha(path)==pin['sha256']
        inputs[key]=dict(file=os.path.relpath(path,OUT),sha256=pin['sha256'])
    pins=dict(parent_protocol=PARENT/'protocol.json',parent_checkpoint=PARENT/'checkpoint.json.gz',
        parent_requests=PARENT/'request_manifest.json.gz',parent_audit=PARENT/'coverage_audit.json',
        parent_verification=PARENT/'independent_verification.json',parent_receipt=PARENT/'run_receipt.json',
        parent_stop=PARENT/'collection_stop.json',parent_resume=PARENT/'resume_checkpoint.json',
        parent_execution_protocol=PARENT/'execution_validation_protocol.json',
        baseline_view=PARENT/'precutoff_feature_view.json.gz',preparation_code=Path(__file__),
        execution_auditor=OUT/'audit_execution.py',execution_verifier=OUT/'verify_execution.py')
    for key,path in pins.items():
        inputs[key]=dict(file=os.path.relpath(path,OUT),sha256=sha(path))
    WORK.mkdir()
    for name in ['requests','raw','results']:(WORK/name).mkdir()
    (WORK/'plan.json').write_bytes(json_bytes(selected))
    (WORK/'preflight.json').write_bytes(json_bytes(selected[0]))
    locks=sorted(set(read(PARENT_WORK/'historical_locks.json'))|{str(PARENT_WORK/'collector.lock')})
    (WORK/'historical_locks.json').write_bytes(json_bytes(locks))
    reused=[];source_counts=[]
    for r in selected:
        saved=validate_cached(r,PARENT_WORK,max_pages=32)
        folder=WORK/'requests'/r['pilot_id'];folder.mkdir()
        for key,marker,body,meta in saved:
            (folder/body.name).write_bytes(body.read_bytes())
            (folder/marker.name).write_bytes(json_bytes(dict(meta,offline_reused=True,reused_from_pass=PARENT.name)))
            reused.append(dict(source_id=r['pilot_id'],key=key,predecessor_pass=PARENT.name,
                sha256=meta['sha256'],endpoint_sha256=meta['endpoint_sha256']))
        source_counts.append(dict(source_id=r['pilot_id'],saved_tail_pages=sum(x[0].startswith('tail_') for x in saved),saved_reference=bool(saved)))
    tail_pages=sum(x['saved_tail_pages'] for x in source_counts)
    refs=sum(x['saved_reference'] for x in source_counts)
    budget=dict(ordinary_counter_gets=1,new_reference_gets_at_most=len(ids)-refs,
        new_tail_pages_at_most=32*len(ids)-tail_pages,fresh_reference_statuses_at_most=len(ids),
        funding_status_gets_at_most=sum(r['registry_input_slots'] for r in selected))
    budget['total_new_requests_at_most']=sum(budget.values())
    (OUT/'offline_reuse_manifest.json').write_bytes(json_bytes(dict(schema_version=1,responses=reused)))
    capacity=dict(schema_version=1,scope='distinct_interruption_successor',selected_source_ids=ids,
        predecessor_finalized_sources_excluded=10,predecessor_old_vectors_preserved=1383,
        saved_responses_reused=len(reused),saved_tail_pages_reused=tail_pages,per_source=source_counts,
        request_budget=budget,old_failed_or_consumed_markers_copied=False,provider_requests_during_preparation=0,
        predecessor_consumed_interrupted_requests=read(PARENT/'run_receipt.json')['consumed_interrupted_request_records'],
        private_work_available=True,model_fits=0,verified_device_compromise_labels_remain_unknown=True)
    (OUT/'capacity_and_cache_audit.json').write_bytes(json_bytes(capacity))
    for name in ['offline_reuse_manifest','capacity_and_cache_audit']:
        key='successor_offline_reuse_manifest' if name=='offline_reuse_manifest' else name
        inputs[key]=dict(file=name+'.json',sha256=sha(OUT/(name+'.json')))
    # Preserve the immediate parent's reuse/capacity manifests as separate pins.
    for name in ['offline_reuse_manifest','capacity_and_cache_audit']:
        inputs['parent_'+name]=dict(file='../'+PARENT.name+'/'+name+'.json',sha256=sha(PARENT/(name+'.json')))
    retained={(p['file'],p['sha256']) for p in inputs.values()}
    for name,pin in parent['inputs'].items():
        path=(PARENT/pin['file']).resolve()
        converted=dict(file=os.path.relpath(path,OUT),sha256=pin['sha256'])
        if (converted['file'],converted['sha256']) not in retained:
            inputs['ancestor_'+name]=converted
    inputs['parent_private_backup']=dict(file='../'+PARENT.name+'/private_cache_backup.json',sha256=sha(PARENT/'private_cache_backup.json'))
    protocol=dict(parent,pass_name=OUT.name,source_ids=ids,inputs=inputs,baseline_vectors=1383,
        all_gap_targets=dict(coldcard=117,cryptobilis=37,total=154),batch_size=20,max_batches=1,
        authorization='Hugo authorized execution on 10 November 2026; distinct ten-ID successor after execution-server loss, preserving all completed outcomes and consumed intents.',
        coverage_scope='Only the ten unfinished original selections; reuse anchored successful pages, keep the 32-page total cap and all original transport/refusal guards.',
        private_plan_sha256=sha(WORK/'plan.json'),private_lock_manifest_sha256=sha(WORK/'historical_locks.json'),
        offline_reused_responses=len(reused),request_budget=budget,
        predecessor_interruption='Execution-server session lost; ten final outcomes retained, two consumed intents without bodies remain in the closed parent.',
        consumed_intent_policy='No marker is copied or retried in the old scope. A new attempt is allowed only in this distinct pinned successor after fresh locks, live policy/lease and one normal counter HTTP200.')
    (OUT/'protocol.json').write_bytes(json_bytes(protocol))
    (OUT/'resume_checkpoint.json').write_bytes(json_bytes(dict(schema_version=1,pass_name=OUT.name,
        status='prepared_not_started',network_source_ids=ids,finalized_source_ids=[],collection_can_resume=False,
        automation_enabled=False,provider_requests=0,model_fits=0,protocol_sha256=sha(OUT/'protocol.json'))))
    print(json.dumps(capacity,sort_keys=True))


if __name__=='__main__':main()
