"""Preserve a deeper work checkpoint and the exact queue of incomplete sources."""
from collections import Counter
from datetime import datetime,timezone
import gzip
import hashlib
import json
from pathlib import Path

OUT=Path(__file__).resolve().parent
BASE=OUT.parent
PARENT=BASE/'source_prefix_extension_20261110_03'


def read(p):
    b=p.read_bytes()
    return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    assert not (OUT/'continuation_reconciliation.json').exists()
    q=read(OUT/'protocol.json');cp=read(OUT/'checkpoint.json.gz');entries=cp['entries']
    assert cp['protocol_sha256']==sha(OUT/'protocol.json')
    assert read(OUT/'independent_verification.json')['status']=='passed'
    before=read(PARENT/'precutoff_feature_view.json.gz');after=read(OUT/'precutoff_feature_view.json.gz')
    old={r['source_id']:r for r in before['rows']};rows={r['source_id']:r for r in after['rows']}
    assert len(rows)==len(old)==1500 and len(set(q['source_ids']))==9
    assert set(entries)<=set(q['source_ids'])
    added=sorted(sid for sid,e in entries.items() if e['status']=='complete_prior_prefix')
    bounded=sorted(sid for sid,e in entries.items() if e['status']=='bounded_incomplete')
    pending=sorted(set(q['source_ids'])-set(entries))
    assert len(added)+len(bounded)+len(pending)==9
    for sid,row in rows.items():
        if old[sid]['features'] is not None or sid not in entries:assert row==old[sid]
        elif sid in added:assert row['features']==entries[sid]['features']
        else:assert row['features'] is None
    available=sum(r['features'] is not None for r in rows.values())
    assert available==1393+len(added)
    previous_entries={}
    for name in ['source_prefix_extension_20261110_03']:
        for sid,e in read(BASE/name/'checkpoint.json.gz')['entries'].items():
            if sid in q['source_ids']:previous_entries[sid]=(name,e)
    assert set(previous_entries)==set(q['source_ids'])
    details=[]
    for sid,e in sorted(entries.items()):
        name,prior=previous_entries[sid]
        w=BASE/('source_cohort_work_'+name);old_raw=read(w/prior['raw_file'])
        current_work=BASE/('source_cohort_work_'+q['pass_name']);raw=read(current_work/e['raw_file'])
        old_prior=[t for t in old_raw['transactions'] if t['status']['block_height']<old[sid]['cutoff_height']]
        new_prior=[t for t in raw['transactions'] if t['status']['block_height']<old[sid]['cutoff_height']]
        assert len(new_prior)>=len(old_prior)
        assert raw['transactions'][:len(old_raw['transactions'])]==old_raw['transactions']
        details.append(dict(source_id=sid,status=e['status'],previous_pages=64,pages_saved=e['pages_fetched'],
            prior_source_transaction_observations_before=len(old_prior),prior_source_transaction_observations_after=len(new_prior),
            additional_source_transaction_observations=len(new_prior)-len(old_prior),
            earliest_observed_prior_height_before=min((t['status']['block_height'] for t in old_prior),default=None),
            earliest_observed_prior_height_after=min((t['status']['block_height'] for t in new_prior),default=None)))
    unavailable=sorted(sid for sid,r in rows.items() if r['features'] is None)
    parent_resume=read(PARENT/'resume_checkpoint.json')
    unextended=parent_resume['coldcard_unextended_at_16_page_bound_source_ids']
    assert len(unextended)==82 and set(unextended)<=set(unavailable)
    queue=[dict(source_id=sid,saved_pages=entries[sid]['pages_fetched'] if sid in entries else None,
                next_checkpoint_pages=128,requires_distinct_pinned_successor=True) for sid in bounded+pending]
    request_records=read(OUT/'request_manifest.json.gz')
    fresh=[m for m in request_records if not m.get('offline_reused')]
    assert all(not m['key'].startswith('tail_') or int(m['key'][5:])>=64 for m in fresh)
    report=dict(schema_version=1,status='all_nine_finalized' if not pending else 'partial_checkpoint',
        selected=9,finalized=len(entries),new_complete_prefixes=len(added),new_complete_source_ids=added,
        bounded_at_96_page_checkpoint=bounded,pending_source_ids=pending,continuation_queue=queue,
        source_progress=details,additional_source_transaction_observations=sum(d['additional_source_transaction_observations'] for d in details),
        observation_count_is_not_a_global_unique_transaction_count=True,
        preceding_vectors_preserved=1393,coldcard_vectors=available,coldcard_unavailable_prefixes=len(unavailable),
        cryptobilis_vectors_unchanged=329,cryptobilis_unavailable_unchanged=37,total_remaining_information_gaps=len(unavailable)+37,
        saved_responses_reused=sum(bool(m.get('offline_reused')) for m in request_records),
        new_request_intents=len(fresh),new_successful_bodies=sum(m.get('http_status')==200 for m in fresh),
        old_tail_pages_requested_again=False,full_current_history_statuses_unchanged=True,
        verified_compromise_device_labels_remain_unknown=True,model_fits=0,new_scores=0,
        final_view_sha256=sha(OUT/'precutoff_feature_view.json.gz'),provider_requests_by_reconciler=0)
    (OUT/'continuation_reconciliation.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    p=OUT/'resume_checkpoint.json';(OUT/'prepared_resume_checkpoint.json').write_bytes(p.read_bytes())
    resume=dict(schema_version=2,pass_name=q['pass_name'],status='closed_checkpoint_audit_passed',
        source_ids=q['source_ids'],finalized_source_ids=sorted(entries),network_source_ids=pending,
        bounded_incomplete_source_ids=bounded,continuation_required_source_ids=bounded+pending,
        continuation_queue=queue,collection_can_resume=False,restart_same_scope_allowed=False,
        automation_enabled=False,is_enabled=False,checkpoint_pages=96,
        coldcard_vectors_available=available,coldcard_remaining_bounded_source_ids=unavailable,
        coldcard_unextended_at_16_page_bound_source_ids=unextended,
        cryptobilis_vectors_available=329,cryptobilis_bounded_incomplete=37,
        all_vectors_available=available+329,all_bounded_prefixes=len(unavailable)+37,
        protocol_sha256=sha(OUT/'protocol.json'),model_fits=0,new_scores=0,
        next_action='Continue the retained queue in a distinct pinned successor (suggested next work checkpoint 128 pages), reusing all verified saved pages. Preserve null features until exhaustion and funding closure. Fresh live lease/locks, due cooldown and one normal original-route counter HTTP200 remain mandatory. Preserve the 82 unextended IDs and other older bounded sources for further coverage.',
        overlap_recheck_required_before_updated_snapshot_model_work=True)
    p.write_text(json.dumps(resume,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ['source_progress','continuation_queue']},sort_keys=True))


if __name__=='__main__':main()
