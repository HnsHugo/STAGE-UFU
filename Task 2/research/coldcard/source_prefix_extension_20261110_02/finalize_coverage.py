"""Reconcile the original twenty IDs across the immutable interrupted layers."""
from collections import Counter
from datetime import datetime,timezone
import gzip
import hashlib
import json
from pathlib import Path

OUT=Path(__file__).resolve().parent
BASE=OUT.parent
PARENT=BASE/'source_prefix_extension_20261110_01'


def read(path):
    raw=path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix=='.gz' else raw)


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert not (OUT/'original_twenty_reconciliation.json').exists()
    protocol=read(OUT/'protocol.json');parent_protocol=read(PARENT/'protocol.json')
    first=read(PARENT/'checkpoint.json.gz')['entries']
    second=read(OUT/'checkpoint.json.gz')['entries']
    assert set(first).isdisjoint(second)
    assert set(protocol['source_ids'])==set(parent_protocol['source_ids'])-set(first)
    assert set(first)|set(second)<=set(parent_protocol['source_ids'])
    assert read(OUT/'independent_verification.json')['status']=='passed'
    entries=dict(first,**second)
    pending=[sid for sid in parent_protocol['source_ids'] if sid not in entries]
    statuses=Counter(e['status'] for e in entries.values())
    assert set(statuses)<=set(['complete_prior_prefix','bounded_incomplete'])
    original=read(BASE/'source_prefix_extension_20261109_01/precutoff_feature_view.json.gz')
    latest=read(OUT/'precutoff_feature_view.json.gz')
    before={r['source_id']:r for r in original['rows']}
    new_complete=[sid for sid,e in entries.items() if e['status']=='complete_prior_prefix']
    for row in latest['rows']:
        old=before[row['source_id']]
        if old['features'] is not None or row['source_id'] not in entries:
            assert row==old
        elif row['source_id'] in new_complete:
            assert row['features']==entries[row['source_id']]['features']
        else:
            assert row['features'] is None
    available=sum(r['features'] is not None for r in latest['rows'])
    assert available==1382+len(new_complete)
    missing=[r['source_id'] for r in latest['rows'] if r['features'] is None]
    old_resume=read(BASE/'source_prefix_extension_20261109_01/resume_checkpoint.json')
    unextended=sorted(set(old_resume['coldcard_unextended_at_16_page_bound_source_ids'])-set(parent_protocol['source_ids']))
    assert len(unextended)==82 and set(unextended)<=set(missing)
    requests_first=read(PARENT/'request_manifest.json.gz')
    requests_second=read(OUT/'request_manifest.json.gz')
    fresh_first=[r for r in requests_first if not r.get('offline_reused')]
    fresh_second=[r for r in requests_second if not r.get('offline_reused')]
    consumed=read(PARENT/'run_receipt.json')['consumed_interrupted_request_records']
    resolved=[]
    for old in consumed:
        matching=[r for r in fresh_second if r['source_id']==old['source_id'] and r['key']==old['key']]
        if matching:
            assert len(matching)==1 and matching[0]['endpoint_sha256']==old['endpoint_sha256']
            resolved.append(dict(source_id=old['source_id'],key=old['key'],
                successor_http_status=matching[0].get('http_status'),
                successor_saved_body='sha256' in matching[0],parent_outcome_remains_unknown=True))
    report=dict(schema_version=1,status='all_twenty_finalized' if not pending else 'partially_finalized',
        original_selected=20,finalized=len(entries),pending_source_ids=pending,
        new_complete_source_ids=sorted(new_complete),new_complete_prefixes=len(new_complete),
        bounded_at_32_pages=statuses['bounded_incomplete'],preserved_preceding_vectors=1382,
        coldcard_vectors=available,coldcard_bounded_prefixes=len(missing),cryptobilis_vectors_unchanged=329,
        cryptobilis_bounded_prefixes_unchanged=37,total_remaining_information_gaps=len(missing)+37,
        fresh_request_intents=len(fresh_first)+len(fresh_second),
        fresh_successful_bodies=sum(r.get('http_status')==200 for r in fresh_first+fresh_second),
        interrupted_parent_intents_preserved=len(consumed),distinct_successor_attempts=resolved,
        unextended_coldcard_source_ids=unextended,next_twenty_unextended_ids=unextended[:20],
        full_current_history_statuses_unchanged=True,verified_compromise_device_labels_remain_unknown=True,
        old_models_and_scores_unchanged=True,model_fits=0,new_scores=0,
        final_view_sha256=sha(OUT/'precutoff_feature_view.json.gz'),provider_requests_by_reconciler=0)
    (OUT/'original_twenty_reconciliation.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    prepared=OUT/'resume_checkpoint.json'
    (OUT/'prepared_resume_checkpoint.json').write_bytes(prepared.read_bytes())
    resume=dict(schema_version=2,pass_name=OUT.name,
        status='closed_bounded_scope_audit_passed' if not pending else 'closed_partial_scope_audit_passed',
        source_ids=protocol['source_ids'],finalized_source_ids=sorted(second),network_source_ids=pending,
        collection_can_resume=False,restart_same_scope_allowed=False,automation_enabled=False,is_enabled=False,
        original_twenty_finalized=len(entries),coldcard_vectors_available=available,
        coldcard_bounded_incomplete=len(missing),coldcard_remaining_bounded_source_ids=sorted(missing),
        coldcard_unextended_at_16_page_bound_source_ids=unextended,
        cryptobilis_vectors_available=329,cryptobilis_bounded_incomplete=37,
        all_vectors_available=available+329,all_bounded_prefixes=len(missing)+37,
        next_extension_source_ids=unextended[:20],next_extension_scope_status='not_prepared_or_started',
        protocol_sha256=sha(OUT/'protocol.json'),model_fits=0,new_scores=0,
        overlap_recheck_required_before_updated_snapshot_model_work=True,
        next_action='Prepare a distinct bounded successor over the next at most 20 unextended IDs after restoring/validating saved evidence. Do not repeat any completed or 32-page bounded outcome. Keep live lease/locks, original route, first-refusal stop and cooldown. Recheck overlap before updated-snapshot modeling.')
    prepared.write_text(json.dumps(resume,indent=2,sort_keys=True)+'\n')
    print(json.dumps(report,sort_keys=True))


if __name__=='__main__':main()
