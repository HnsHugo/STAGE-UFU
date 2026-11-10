"""Reconcile an audited successor including variable saved partial-page prefixes."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path


def read(p):
    b=p.read_bytes()
    return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def load_parent_evidence(parent,sid):
    """Read finalized raw evidence or independently validated partial cache pages."""
    parent=parent.resolve();base=parent.parent
    q=read(parent/'protocol.json');entries=read(parent/'checkpoint.json.gz')['entries']
    work=base/('source_cohort_work_'+parent.name)
    if sid in entries:
        prior=entries[sid];path=work/prior['raw_file']
        assert sha(path)==prior['raw_sha256']
        return read(path),prior
    import sys
    sys.path.insert(0,str(base/'source_prefix_extension_20261110_01'))
    from prepare_scope import validate_cached
    assert sha(work/'plan.json')==q['private_plan_sha256']
    record=next(r for r in read(work/'plan.json') if r['pilot_id']==sid)
    saved=validate_cached(record,work,max_pages=q['max_pages_per_address'])
    expected={r['source_id']:r['saved_tail_pages'] for r in read(parent/'coverage_audit.json')['pending_source_page_checkpoints']}
    assert len(saved)==expected[sid]+1
    approved={(m['source_id'],m['key']):m for m in read(parent/'request_manifest.json.gz')}
    for key,_,_,meta in saved:
        assert all(meta[k]==approved[(sid,key)][k] for k in ['source_id','key','http_status','sha256','endpoint_sha256'])
    transactions=[tx for key,_,body,_ in saved if key.startswith('tail_') for tx in read(body)]
    return dict(transactions=transactions),dict(pages_fetched=len(saved)-1)


def finalize(out):
    out=out.resolve();base=out.parent;q=read(out/'protocol.json');parent=base/q['parent_scope']
    if (out/'continuation_reconciliation.json').exists():raise FileExistsError('Do not overwrite a closed reconciliation')
    assert read(out/'independent_verification.json')['status']=='passed'
    cp=read(out/'checkpoint.json.gz');entries=cp['entries'];selected=set(q['source_ids'])
    assert cp['protocol_sha256']==sha(out/'protocol.json') and set(entries)<=selected
    before=read(parent/'precutoff_feature_view.json.gz');after=read(out/'precutoff_feature_view.json.gz')
    old={r['source_id']:r for r in before['rows']};rows={r['source_id']:r for r in after['rows']}
    assert set(rows)==set(old) and len(rows)==1500
    complete=sorted(sid for sid,e in entries.items() if e['status']=='complete_prior_prefix')
    bounded=sorted(sid for sid,e in entries.items() if e['status']=='bounded_incomplete')
    pending=sorted(selected-set(entries));assert len(complete)+len(bounded)+len(pending)==len(selected)
    for sid,r in rows.items():
        if old[sid]['features'] is not None or sid not in entries:assert r==old[sid]
        elif sid in complete:assert r['features']==entries[sid]['features']
        else:assert r['features'] is None
    available=sum(r['features'] is not None for r in rows.values())
    assert available==q['baseline_vectors']+len(complete)
    old_entries=read(parent/'checkpoint.json.gz')['entries'];details=[]
    old_work=base/('source_cohort_work_'+parent.name);work=base/('source_cohort_work_'+out.name)
    for sid,e in sorted(entries.items()):
        a,prior=load_parent_evidence(parent,sid);new_path=work/e['raw_file']
        assert sha(new_path)==e['raw_sha256']
        b=read(new_path);assert b['transactions'][:len(a['transactions'])]==a['transactions']
        x=[t for t in a['transactions'] if t['status']['block_height']<old[sid]['cutoff_height']]
        y=[t for t in b['transactions'] if t['status']['block_height']<old[sid]['cutoff_height']]
        assert len(y)>=len(x)
        details.append(dict(source_id=sid,status=e['status'],previous_pages=prior['pages_fetched'],pages_saved=e['pages_fetched'],
            additional_source_transaction_observations=len(y)-len(x),
            earliest_observed_prior_height_before=min((t['status']['block_height'] for t in x),default=None),
            earliest_observed_prior_height_after=min((t['status']['block_height'] for t in y),default=None)))
    raw_audit=read(out/'coverage_audit.json');partial={r['source_id']:r['saved_tail_pages'] for r in raw_audit['pending_source_page_checkpoints']}
    queue=[dict(source_id=sid,saved_pages=entries[sid]['pages_fetched'] if sid in entries else partial.get(sid),
                next_checkpoint_pages=q['max_pages_per_address']+32,requires_distinct_pinned_successor=True) for sid in bounded+pending]
    records=read(out/'request_manifest.json.gz');fresh=[m for m in records if not m.get('offline_reused')]
    saved_bounds=q.get('per_source_saved_pages',{sid:q['previous_bound'] for sid in q['source_ids']})
    assert all(not m['key'].startswith('tail_') or int(m['key'][5:])>=saved_bounds[m['source_id']] for m in fresh)
    missing=sorted(sid for sid,r in rows.items() if r['features'] is None)
    unextended=read(parent/'resume_checkpoint.json')['coldcard_unextended_at_16_page_bound_source_ids']
    assert set(unextended)<=set(missing)
    report=dict(schema_version=1,status='all_selected_finalized' if not pending else 'partial_checkpoint',selected=len(selected),
        finalized=len(entries),new_complete_prefixes=len(complete),new_complete_source_ids=complete,
        bounded_incomplete_source_ids=bounded,pending_source_ids=pending,checkpoint_pages=q['max_pages_per_address'],
        continuation_queue=queue,source_progress=details,
        additional_source_transaction_observations=sum(x['additional_source_transaction_observations'] for x in details),
        observation_count_is_not_a_global_unique_transaction_count=True,
        preceding_vectors_preserved=q['baseline_vectors'],coldcard_vectors=available,coldcard_unavailable_prefixes=len(missing),
        cryptobilis_vectors_unchanged=329,cryptobilis_unavailable_unchanged=37,total_remaining_information_gaps=len(missing)+37,
        saved_responses_reused=sum(bool(m.get('offline_reused')) for m in records),
        new_request_intents=len(fresh),new_successful_bodies=sum(m.get('http_status')==200 for m in fresh),
        old_tail_pages_requested_again=False,full_current_history_statuses_unchanged=True,
        verified_compromise_device_labels_remain_unknown=True,model_fits=0,new_scores=0,
        final_view_sha256=sha(out/'precutoff_feature_view.json.gz'),provider_requests_by_reconciler=0)
    (out/'continuation_reconciliation.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    p=out/'resume_checkpoint.json';(out/'prepared_resume_checkpoint.json').write_bytes(p.read_bytes())
    resume=dict(schema_version=2,pass_name=out.name,status='closed_checkpoint_audit_passed',source_ids=q['source_ids'],
        finalized_source_ids=sorted(entries),network_source_ids=pending,bounded_incomplete_source_ids=bounded,
        continuation_required_source_ids=bounded+pending,continuation_queue=queue,collection_can_resume=False,
        restart_same_scope_allowed=False,automation_enabled=False,is_enabled=False,checkpoint_pages=q['max_pages_per_address'],
        coldcard_vectors_available=available,coldcard_remaining_bounded_source_ids=missing,
        coldcard_unextended_at_16_page_bound_source_ids=unextended,cryptobilis_vectors_available=329,
        cryptobilis_bounded_incomplete=37,all_vectors_available=available+329,all_bounded_prefixes=len(missing)+37,
        protocol_sha256=sha(out/'protocol.json'),model_fits=0,new_scores=0,
        next_action='Continue the exact retained queue in a distinct pinned successor, reusing every verified page and preserving null features until exhaustion. Keep live locks/lease/cooldown, original route and one normal counter gate. Preserve all other incomplete sources and recheck overlap before new snapshot models.' if queue else 'This retained queue is complete. Select a separately pinned coverage unit for the other retained incomplete sources; preserve all old evidence and scientific guards.',
        overlap_recheck_required_before_updated_snapshot_model_work=True)
    p.write_text(json.dumps(resume,indent=2,sort_keys=True)+'\n')
    return {k:v for k,v in report.items() if k not in ['source_progress','continuation_queue']}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('scope',type=Path);a=p.parse_args();print(json.dumps(finalize(a.scope),sort_keys=True))
