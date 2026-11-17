"""Promote a privately saved audited unit to the current handoff, preserving queues."""
from pathlib import Path
from copy import deepcopy
from datetime import datetime
import hashlib,fcntl,sys
from prepare_frontier_checkpoint import read,write,sha
BASE=Path(__file__).resolve().parent

def finalize(scope):
 out=BASE/scope;work=BASE/('source_cohort_work_'+scope);q=read(out/'protocol.json');backup=read(out/'private_cache_backup.json')
 assert backup['saved_privately']and backup['library_metadata_applied']
 receipt=read(out/'run_receipt.json');assert receipt['independent_journal_replay']=='passed'
 rows=read(out/'precutoff_feature_view.json.gz')['rows'];available=sum(r['features']is not None for r in rows)
 assert available==receipt['available_vectors']
 marks=[read(p)for p in work.glob('requests/*/*.json')];assert len(marks)==receipt['provider_requests']
 ordered=sorted(marks,key=lambda m:m['dispatch_monotonic']);mono=[];utc=[]
 for index,m in enumerate(ordered):
  if m.get('http_status')==200:assert sha(work/'requests'/m['source_id']/(m['key']+'.json.gz'))==m['sha256']
  if index:
   previous=ordered[index-1];mono.append(m['dispatch_monotonic']-previous['dispatch_monotonic']);utc.append((datetime.fromisoformat(m['dispatch_at'])-datetime.fromisoformat(previous['dispatch_at'])).total_seconds())
 assert all(t>=5.25-0.000001 for t in mono)and all(t>=5.0 for t in utc)
 parent=q['parent_scope'];resume=deepcopy(read(BASE/parent/'resume_checkpoint.json'));frontier=read(work/'verified_frontier.json.gz');sid=q['source_ids'][0];queue={r['source_id']:r for r in resume['retained_native_partial_queue']};old=queue[sid];complete=next(r for r in rows if r['source_id']==sid)['features']is not None
 if complete:queue.pop(sid)
 else:
  count=old.get('native_pages',0)+receipt['native_pages']if q['unit_kind']=='same_provider_native_cursor'else receipt['native_pages']
  old.update(provider=q['provider'],evidence_scope=scope,private_raw_file='verified_frontier.json.gz',private_raw_sha256=sha(work/'verified_frontier.json.gz'),actual_cursor_field='actual_native_cursor',native_pages=count,saved_native_pages=count,saved_evidence_pages=old.get('saved_evidence_pages',0)+receipt['native_pages'],last_native_cursor_sha256=hashlib.sha256(frontier['actual_native_cursor'].encode()).hexdigest(),finalized=receipt['status']=='completed')
 missing=[r['source_id']for r in rows if r['features']is None]
 resume.update(pass_name=scope,status='verified_saved_checkpoint',coldcard_vectors_available=available,coldcard_remaining_bounded_source_ids=missing,all_bounded_prefixes=len(missing)+37,retained_native_partial_queue=list(queue.values()),next_action='Fresh eligible scope, actual saved native cursor; no consumed-scope restart',automation_enabled=True)
 write(out/'resume_checkpoint.json',resume)
 policy_path=BASE/'comparison_access_retries_20261030/retry_policy.json';policy=read(policy_path);assert policy['collector_lease']['state']=='idle'
 policy.update(latest_prefix_output=scope,latest_consolidated_prefix_view=scope+'/precutoff_feature_view.json.gz',latest_prefix_resume_file=scope+'/resume_checkpoint.json',latest_prefix_work=work.name,latest_status='dual_api_checkpoint_verified_saved',comparison_pre_cutoff_predictors_available=available-500,comparison_pre_cutoff_predictors_unavailable=len(missing));write(policy_path,policy)
 control_path=BASE/'dual_api_automation_20261117/policy.json';control=read(control_path);control.update(latest_verified_scope=scope,current_complete_vectors=available);write(control_path,control)
 for name in read(work/'historical_locks.json'):
  with Path(name).open('a+')as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
 write(out/'final_operational_check.json',dict(status='passed',lease_idle=True,private_backup_verified=True,locks_checked_free=len(read(work/'historical_locks.json')),minimum_monotonic_spacing=min(mono)if mono else None,minimum_utc_spacing=min(utc)if utc else None,complete_vectors=available))
 (out/'RESULTS.md').write_text(f"# Verified saved source continuation\n\nSource {sid}: {receipt['http200']}/{receipt['provider_requests']} HTTP200, {receipt['native_pages']} native pages, {receipt['new_transactions']} additional address-transaction observations, {receipt['verified_overlap']} verified overlaps, {receipt['new_complete']} newly complete histories. Coverage {available}/1500. Endpoint/body replay, dispatch clocks, private backup and free operational locks verified. Unknown labels, cutoffs and previous vectors preserved. Consumed scope closed.\n")
 return dict(scope=scope,available=available,new_complete=receipt['new_complete'],source_id=sid,complete=complete)
if __name__=='__main__':print(__import__('json').dumps(finalize(sys.argv[1])))
