from pathlib import Path
import sys, shutil, hashlib, os
from datetime import datetime,timezone
B=Path(__file__).resolve().parent;sys.path.insert(0,str(B))
from prepare_frontier_checkpoint import read,write,sha
from independent_mempool_resume import cached_prefix
C=B/'mempool_native_round3_20261114'; old=B/'mempool_native_round3_20261114_unit_02'; scope='mempool_native_round3_20261114_unit_02_recovery_20261115';out=B/scope;work=B/('source_cohort_work_'+scope)
p=read(B/'comparison_access_retries_20261030/retry_policy.json');lease=p['collector_lease'];assert lease['owner']==old.name and datetime.fromisoformat(lease['expires_at'])<datetime.now(timezone.utc)
assert not (old/'run_receipt.json').exists() and not (B/('source_cohort_work_'+old.name)).exists()
assert not out.exists() and not work.exists()
q=read(old/'protocol.json');state=read(C/'progress.json');assert state['active_scope']==old.name
for pin in q['inputs'].values():assert sha((old/pin['file']).resolve())==pin['sha256']
write(old/'interruption_20261115.json',dict(status='expired_unsaved_scope',original_lease=lease,request_count=None,request_outcomes='unknown',new_results_promoted=False,restart_same_scope_allowed=False,successor=scope))
out.mkdir();work.mkdir(mode=0o700)
for n in ['requests','raw','results']:(work/n).mkdir()
parent=B/q['parent_scope'];pw=B/('source_cohort_work_'+parent.name)
for n in ['remaining_source_registry.json','retained_bridge_native_cursors.json']:shutil.copyfile(pw/n,work/n)
reg={r['pilot_id']:r for r in read(work/'remaining_source_registry.json')};records=[reg[s] for s in q['source_ids']];write(work/'plan.json',records)
locks=set(read(pw/'historical_locks.json'));locks.update(str(w/'collector.lock') for w in B.glob('source_cohort_work_*') if w!=work)
for n in locks:Path(n).parent.mkdir(parents=True,exist_ok=True)
write(work/'historical_locks.json',sorted(locks))
reuse=read(old/'offline_reuse_manifest.json');cursors={}
for s in read(old/'seed_manifest.json')['sources']:
 sid=s['source_id'];origin=B/('source_cohort_work_'+s['origin_scope']);dest=work/'requests'/sid;dest.mkdir()
 assert sha(origin/'raw'/ (sid+'.json.gz'))==s['raw_sha256']
 for pin in [m for m in reuse['responses'] if m['source_id']==sid]:
  key=pin['key'];marker=origin/'requests'/sid/(key+'.json');meta=read(marker);body=marker.with_suffix('.json.gz')
  assert sha(marker)==pin['original_marker_sha256'] and sha(body)==pin['sha256'] and meta['http_status']==200
  shutil.copyfile(body,dest/body.name);write(dest/marker.name,dict(meta,offline_reused=True,reused_from_pass=s['origin_scope'],original_marker_sha256=sha(marker)))
 anchor,pages,cursor,seen,height,terminal=cached_prefix(reg[sid],work,[m for m in reuse['responses'] if m['source_id']==sid]);assert len(pages)==80 and not terminal and hashlib.sha256(cursor.encode()).hexdigest()==s['last_native_cursor_sha256']
 cursors[sid]=dict(provider=q['provider'],cursor=cursor,saved_native_pages=80,pagination_exhausted=False,finalized=True)
write(work/'parent_native_cursors.json',cursors)
for n in ['offline_reuse_manifest.json','seed_manifest.json','retained_deep_queue.json']:shutil.copyfile(old/n,out/n)
state.update(active_scope=scope,status='prepared_unit');write(C/'progress.json',state);write(out/'prepared_campaign_state.json',state)
inputs={k:(old/v['file']).resolve() for k,v in q['inputs'].items()}
for k,v in list(inputs.items()):
 if v.parent==old:inputs[k]=out/v.name
inputs['interrupted_scope']=old/'interruption_20261115.json';inputs['recovery_preparer']=B/'prepare_round3_recovery_20261115.py'
q.update(pass_name=scope,created_on='2026-11-15',interrupted_scope=old.name,restart_of_expired_scope=False)
for n,k in [('plan.json','private_plan_sha256'),('historical_locks.json','private_lock_manifest_sha256'),('parent_native_cursors.json','private_parent_native_cursors_sha256')]:q[k]=sha(work/n)
q['inputs']={k:dict(file=os.path.relpath(v,out),sha256=sha(v)) for k,v in inputs.items()};write(out/'protocol.json',q)
write(out/'preparation_verification.json',dict(status='passed',old_pages_verified=400,cached_responses_verified=405,input_pins_verified=len(inputs),baseline_vectors=1439,provider_requests=0,interrupted_outcomes_preserved_as_unknown=True))
(out/'README.md').write_text('# Distinct recovery of third native unit 2\n\nThe expired unsaved predecessor is closed with unknown request counts/outcomes. Reuse 400 verified native pages and five references for the same five frozen source/reference pairs. Add at most sixteen pages per source. Preserve all 1,439 complete vectors and unknown theft/device labels. Fourteen features strictly precede the reference block. One worker, five-second spacing, 45-second timeout, original authorized Mempool route and verified TLS. Fresh locks and exact published lease/readback are mandatory. Stop on first failure; no retry, rotation, cost, model fit or score.\n')
p['collector_lease'].update(state='idle',owner=None,last_owner=old.name,expires_at=None,operational_locks_released=True,stop_status='expired_unsaved_unknown');p.update(active_collection_scope='none',coverage_collection_paused=True,coverage_pause_reason='Expired unsaved scope preserved; distinct recovery prepared, no traffic yet.')
write(B/'comparison_access_retries_20261030/retry_policy.json',p)
print(scope,'405 cached responses verified; no network request')
