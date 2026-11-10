"""Prepare a distinct same-target successor from validated variable partial pages."""
import argparse
from datetime import datetime
import os
from pathlib import Path
import shutil
from prepare_coldcard_checkpoint import read, sha, retain_lineage, validate_cached, json_bytes

BASE = Path(__file__).resolve().parent


def prepare(parent, out):
    parent, out = parent.resolve(), out.resolve()
    work = BASE / ('source_cohort_work_' + out.name)
    old_work = BASE / ('source_cohort_work_' + parent.name)
    assert parent.parent == out.parent == BASE and not out.exists() and not work.exists()
    old = read(parent / 'protocol.json'); resume = read(parent / 'resume_checkpoint.json')
    partial = read(parent / 'partial_page_reconciliation.json')
    assert read(parent / 'independent_verification.json')['status'] == partial['status'] == 'passed'
    assert read(parent / 'run_receipt.json')['first_refusal_status'] == 429
    assert read(parent / 'private_cache_backup.json')['saved_privately']
    assert not read(parent / 'checkpoint.json.gz')['entries']
    for path, digest in partial['input_sha256'].items():
        assert sha((parent / path).resolve()) == digest
    assert sha(old_work / 'plan.json') == old['private_plan_sha256']
    assert sha(old_work / 'historical_locks.json') == old['private_lock_manifest_sha256']
    due = resume['next_network_attempt_not_before']
    assert due == partial['next_network_attempt_not_before'] and datetime.fromisoformat(due).tzinfo
    ids = resume['network_source_ids']
    assert ids and len(ids) <= 20 and len(ids) == len(set(ids))
    assert set(ids) == set(resume['continuation_required_source_ids'])
    records = {r['pilot_id']:r for r in read(old_work / 'plan.json')}
    selected = [records[sid] for sid in ids]
    view = read(parent / 'precutoff_feature_view.json.gz')
    rows = {r['source_id']:r for r in view['rows']}
    goal = old['max_pages_per_address']
    expected = {r['source_id']:r['saved_pages'] for r in partial['partial_checkpoints']}
    approved = {(m['source_id'],m['key']):m for m in read(parent / 'request_manifest.json.gz')}
    saved = {}
    for record in selected:
        sid = record['pilot_id']; assert rows[sid]['features'] is None
        for key in ['address_sha256','payment_txid_sha256','cutoff_height','cutoff_block_hash']:
            assert record[key] == rows[sid][key]
        assert 0 < expected[sid] < goal
        saved[sid] = validate_cached(record, old_work, max_pages=goal)
        assert len(saved[sid]) == expected[sid] + 1
        for key, _, _, meta in saved[sid]:
            assert all(meta[k] == approved[(sid,key)][k] for k in ['source_id','key','http_status','sha256','endpoint_sha256'])
    out.mkdir(); work.mkdir()
    for name in ['requests','raw','results']:(work / name).mkdir()
    for name in ['audit_execution.py','verify_execution.py']:shutil.copyfile(parent / name,out / name)
    inputs = {k:dict(file=os.path.relpath((parent / p['file']).resolve(),out),sha256=p['sha256']) for k,p in old['inputs'].items()}
    paths = dict(parent_protocol=parent/'protocol.json',parent_checkpoint=parent/'checkpoint.json.gz',
        parent_requests=parent/'request_manifest.json.gz',parent_audit=parent/'coverage_audit.json',
        parent_verification=parent/'independent_verification.json',parent_receipt=parent/'run_receipt.json',
        parent_stop=parent/'collection_stop.json',parent_resume=parent/'resume_checkpoint.json',
        parent_private_backup=parent/'private_cache_backup.json',parent_partial_pages=parent/'partial_page_reconciliation.json',
        parent_reconciliation=parent/'continuation_reconciliation.json',baseline_view=parent/'precutoff_feature_view.json.gz',
        preparation_code=Path(__file__),finalization_code=BASE/'finalize_variable_checkpoint.py',
        clock_guard=BASE/'run_after_cooldown.py',clock_guard_tests=BASE/'test_cooldown_guard.py',
        execution_auditor=out/'audit_execution.py',execution_verifier=out/'verify_execution.py')
    for key,path in paths.items():inputs[key] = dict(file=os.path.relpath(path,out),sha256=sha(path))
    (work / 'plan.json').write_bytes(json_bytes(selected))
    (work / 'preflight.json').write_bytes(json_bytes(selected[0]))
    locks = sorted(set(read(old_work/'historical_locks.json')) | {str(old_work/'collector.lock')})
    assert all(Path(p).parent.is_dir() for p in locks)
    (work / 'historical_locks.json').write_bytes(json_bytes(locks))
    reused = []
    for sid in ids:
        folder = work / 'requests' / sid; folder.mkdir()
        for key, marker, body, meta in saved[sid]:
            (folder/body.name).write_bytes(body.read_bytes())
            (folder/marker.name).write_bytes(json_bytes(dict(meta,offline_reused=True,reused_from_pass=parent.name)))
            assert sha(folder/body.name) == meta['sha256']
            reused.append(dict(source_id=sid,key=key,predecessor_pass=parent.name,
                sha256=meta['sha256'],endpoint_sha256=meta['endpoint_sha256']))
    budget = dict(ordinary_counter_gets=1,new_reference_gets_at_most=0,
        new_tail_pages_at_most=sum(goal-expected[sid] for sid in ids),
        fresh_reference_statuses_at_most=len(ids),funding_status_gets_at_most=sum(r['registry_input_slots'] for r in selected))
    budget['total_new_requests_at_most'] = sum(budget.values())
    (out/'offline_reuse_manifest.json').write_bytes(json_bytes(dict(schema_version=1,responses=reused)))
    capacity = dict(schema_version=1,selected_source_ids=ids,per_source_saved_pages=expected,
        new_page_checkpoint=goal,saved_responses_reused=len(reused),saved_tail_pages_reused=sum(expected.values()),
        request_budget=budget,network_not_before=due,provider_requests=0,model_fits=0,new_scores=0,
        old_failed_counter_status_or_operational_markers_copied=False)
    (out/'capacity_and_cache_audit.json').write_bytes(json_bytes(capacity))
    for name in ['offline_reuse_manifest','capacity_and_cache_audit']:
        inputs['current_'+name] = dict(file=name+'.json',sha256=sha(out/(name+'.json')))
    retain_lineage(inputs,old['inputs'],parent,out)
    available = sum(r['features'] is not None for r in rows.values())
    q = dict(old,pass_name=out.name,parent_scope=parent.name,inputs=inputs,source_ids=ids,
        previous_bound=min(expected.values()),per_source_saved_pages=expected,max_pages_per_address=goal,
        previous_requested_page_target=goal,network_not_before=due,baseline_vectors=available,
        private_plan_sha256=sha(work/'plan.json'),private_lock_manifest_sha256=sha(work/'historical_locks.json'),
        offline_reused_responses=len(reused),request_budget=budget,batch_size=20,max_batches=1,
        authorization='Hugo requests continued collection while preserving all completed work; this successor is prepared offline and cannot run before the pinned cooldown.',
        coverage_scope='Only the three pending sources after HTTP429; reuse every validated partial page and finish the same 448-page checkpoint in a distinct scope.',
        network_entrypoint='../run_after_cooldown.py',finalization_entrypoint='../finalize_variable_checkpoint.py',
        consumed_intent_policy='Old refusals remain immutable. No marker is copied except verified successful reference/tail bodies. After due time require fresh live locks/lease/cooldown and one normal original-route counter HTTP200.')
    (out/'protocol.json').write_bytes(json_bytes(q))
    (out/'resume_checkpoint.json').write_bytes(json_bytes(dict(schema_version=2,pass_name=out.name,
        status='prepared_offline_waiting_cooldown',source_ids=ids,network_source_ids=ids,
        finalized_source_ids=[],per_source_saved_pages=expected,network_not_before=due,
        collection_can_resume=False,automation_enabled=False,is_enabled=False,
        protocol_sha256=sha(out/'protocol.json'),provider_requests=0,model_fits=0)))
    for pin in inputs.values():assert sha((out/pin['file']).resolve()) == pin['sha256']
    report = dict(schema_version=1,status='passed',selected=len(ids),saved_responses_verified=len(reused),
        input_pins_verified=len(inputs),all_inherited_pins_retained=True,
        per_source_saved_pages=expected,request_budget=budget,network_not_before=due,
        protocol_sha256=sha(out/'protocol.json'),provider_requests=0,model_fits=0)
    (out/'preparation_verification.json').write_bytes(json_bytes(report))
    return report


if __name__ == '__main__':
    import json
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('parent',type=Path);parser.add_argument('output',type=Path)
    args = parser.parse_args()
    print(json.dumps(prepare(args.parent,args.output),sort_keys=True))
