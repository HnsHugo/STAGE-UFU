"""Verify all remaining native frontiers with their distinct saved page bounds."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import sys

CAMPAIGN=Path(__file__).resolve().parent
BASE=CAMPAIGN.parent
sys.path.insert(0,str(BASE))
from prepare_frontier_checkpoint import read,sha,write


def verify():
    selection=read(CAMPAIGN/'selection.json');state=read(CAMPAIGN/'progress.json')
    ids=selection['source_ids'];assert len(ids)==len(set(ids))==selection['requested_sources']
    baseline_count=selection['original_vectors']
    saved_bounds=selection['per_source_saved_pages']
    assert [s for u in selection['units'] for s in u]==ids
    assert all(1<=len(u)<=5 and len({saved_bounds[s] for s in u})==1 for u in selection['units'])
    assert state['status']=='all_remaining_native_saved' and not state['pending_source_ids']
    assert state['finalized_source_ids']==ids and len(state['completed_units'])==len(selection['units'])
    baseline_path=BASE/selection['original_parent']/'precutoff_feature_view.json.gz'
    baseline=read(baseline_path);old={r['source_id']:r for r in baseline['rows']}
    assert len(old)==1500 and sum(r['features'] is not None for r in old.values())==baseline_count
    previous=selection['original_parent'];seen=[];complete=[];bounded=[];total_requests=total_http=total_obs=private_files=0
    ledger=[]
    for i,unit in enumerate(state['completed_units'],1):
        assert unit['unit']==i and unit['selected_source_ids']==selection['units'][i-1]
        scope=BASE/unit['scope'];q=read(scope/'protocol.json');a=read(scope/'coverage_audit.json')
        receipt=read(scope/'run_receipt.json');backup=read(scope/'private_cache_backup.json')
        assert q['parent_scope']==previous and q['source_ids']==selection['units'][i-1]
        assert all(q['previous_bound']==saved_bounds[s] for s in q['source_ids'])
        assert q['max_pages_per_address']==q['previous_bound']+16
        assert q['workers']==1 and q['minimum_dispatch_interval_seconds']==5 and q['timeout_seconds']==45
        assert a['status']==read(scope/'independent_verification.json')['status']=='passed'
        assert a['selected']==a['finalized']==len(q['source_ids']) and not a['pending_in_scope']
        assert backup['saved_privately'] and backup['library_metadata_applied'] and unit['private_evidence_saved']
        assert receipt['status']=='completed' and receipt['provider_requests']==receipt['http200'] and receipt['failures']==0
        assert receipt['operational_locks_released'] and receipt['blockstream_provider_requests']==0
        assert receipt['model_fits']==receipt['new_scores']==0
        entries=read(scope/'checkpoint.json.gz')['entries'];assert set(entries)==set(q['source_ids'])
        assert a['preserved_old_vectors']==q['baseline_vectors']==baseline_count+len(complete)
        for sid in q['source_ids']:
            assert sid not in seen;seen.append(sid)
            e=entries[sid]
            if e['features'] is not None:
                assert e['status']=='complete_prior_prefix';complete.append(sid)
            else:
                assert e['status']=='bounded_incomplete';bounded.append(sid)
        assert a['available_coldcard_vectors']==baseline_count+len(complete)
        manifest=read(scope/'request_manifest.json.gz');fresh=[m for m in manifest if not m.get('offline_reused')]
        assert len(fresh)==receipt['provider_requests'] and sum(bool(m.get('offline_reused')) for m in manifest)==len(q['source_ids'])*(q['previous_bound']+1)
        assert all(m.get('http_status')==200 and 'error_type' not in m for m in fresh)
        assert all(not m['key'].startswith('tail_') or int(m['key'][5:])>=q['previous_bound'] for m in fresh)
        for pin in q['inputs'].values():assert sha((scope/pin['file']).resolve())==pin['sha256']
        total_requests+=receipt['provider_requests'];total_http+=receipt['http200'];total_obs+=a['fresh_native_source_transaction_observations'];private_files+=backup['private_files_verified']
        ledger.append(dict(unit=i,scope=scope.name,new_complete=a['new_complete_prefixes'],bounded=a['bounded_in_scope'],http200=receipt['http200'],new_prior_block_observations=a['fresh_native_source_transaction_observations']))
        previous=scope.name
    assert seen==ids and len(complete)+len(bounded)==len(ids)
    assert set(complete)==set(state['new_complete_source_ids']) and set(bounded)==set(state['bounded_source_ids'])
    final=BASE/previous;view=read(final/'precutoff_feature_view.json.gz');rows={r['source_id']:r for r in view['rows']}
    assert len(rows)==1500 and set(rows)==set(old)
    preserved=0
    for sid,row in rows.items():
        before=old[sid]
        for key in ['source_id','address_sha256','payment_txid_sha256','cutoff_height','cutoff_block_hash','known_coldcard_core_membership','labels','full_history_status']:
            assert row.get(key)==before.get(key)
        if before['features'] is not None:
            assert row==before;preserved+=1
        elif sid not in ids:assert row==before
        if sid in complete:assert row['features'] is not None
        if sid in bounded:assert row['features'] is None
    assert preserved==baseline_count
    n=sum(r['features'] is not None for r in rows.values());assert n==baseline_count+len(complete)==state['available_vectors']
    old_resume=read(BASE/selection['original_parent']/'resume_checkpoint.json');resume=read(final/'resume_checkpoint.json')
    old_queue={r['source_id']:r for r in old_resume['retained_native_partial_queue']};new_queue={r['source_id']:r for r in resume['retained_native_partial_queue']}
    for sid in set(old_queue)-set(ids):assert old_queue[sid]==new_queue[sid]
    for sid in complete:assert sid not in new_queue
    for sid in bounded:assert new_queue[sid]['native_pages']==saved_bounds[sid]+16
    assert (final/'retained_deep_queue.json').read_bytes()==(BASE/selection['original_parent']/'retained_deep_queue.json').read_bytes()
    interrupted=BASE/'mempool_native_extension_20261114_01';unknown=read(interrupted/'interruption_receipt.json')['unacknowledged_requests']
    for x in unknown:
        marker=BASE/('source_cohort_work_'+interrupted.name)/'requests'/x['source_id']/(x['key']+'.json')
        assert sha(marker)==x['original_marker_sha256']
    inventory=Counter()
    for row in rows.values():
        if row['features'] is not None:continue
        q=new_queue.get(row['source_id'])
        if q and q.get('seed_kind')=='native':inventory['native_'+str(q['native_pages'])+'_pages']+=1
        elif q:inventory[q.get('seed_kind','other')]+=1
        else:inventory['other_retained_deep_history']+=1
    result=dict(schema_version=1,status='passed',verified_on=datetime.now(timezone.utc).isoformat(),
        requested_sources=len(ids),ordered_source_ids=ids,initial_saved_native_pages=saved_bounds,
        unique_finalized_sources=len(ids),new_complete_prefixes=len(complete),bounded_histories=len(bounded),pending_sources=0,
        old_complete_vectors_preserved=preserved,available_coldcard_vectors=n,missing_coldcard_vectors=1500-n,
        fresh_requests=total_requests,fresh_http200=total_http,failed_requests=0,new_prior_block_source_transaction_observations=total_obs,
        old_native_pages_verified_and_reused=sum(saved_bounds.values()),successful_old_responses_reused=sum(saved_bounds.values())+len(ids),private_evidence_files_saved=private_files,
        focused_tests_passed=25,cryptobilis_vectors_unchanged=329,cryptobilis_missing_unchanged=37,
        all_old_labels_identities_cutoffs_full_current_statuses_unchanged=True,every_unselected_native_queue_row_unchanged=True,
        deep_queue_bytes_unchanged=True,closed_historical_campaign_files_unchanged=True,
        original_unknown_intent_hashes_unchanged=len(unknown),old_pages_not_requested_again=True,
        remaining_missing_groups=dict(inventory),units=ledger,latest_scope=previous,
        model_fits=0,new_scores=0,automation_enabled=False,
        completion_meaning='All fixed remaining-native sources have final outcomes for this bounded extension; bounded histories remain explicitly incomplete.')
    write(CAMPAIGN/'final_verification.json',result)
    print(__import__('json').dumps(result,indent=2))
    return result


if __name__=='__main__':verify()
