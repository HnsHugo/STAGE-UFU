"""Distinct two-target continuation; immutable legacy and native cache reuse."""
import argparse,os,shutil
from pathlib import Path
from copy import deepcopy
from datetime import datetime,timezone
from prepare_frontier_checkpoint import read,sha,write
import recorded_remaining_campaign as c
import recover_legacy_unit19 as engine
B=c.BASE;NAME='mempool_remaining_fifty_20261116_unit_21';OUT=B/NAME;WORK=B/('source_cohort_work_'+NAME)
ORIGINS={'comparison_0026':'mempool_remaining_fifty_20261116_unit_20','comparison_0157':'mempool_remaining_fifty_20261116_unit_12'}
COUNTS={'comparison_0026':0,'comparison_0157':12};CAPS={'comparison_0026':49,'comparison_0157':37}
engine.NEW=NAME;engine.COUNTS=COUNTS;engine.CAPS=CAPS;engine.UNKNOWN=('comparison_0157','native_tail_0012');engine.OLD='original_scopes_20_and_12'
def prepare():
 assert not OUT.exists();c.validated_access();state=read(c.CAMPAIGN/'progress.json');assert set(state['pending_source_ids'])==set(ORIGINS) and state['active_scope']is None
 OUT.mkdir();WORK.mkdir(mode=0o700)
 for n in ['requests','raw','results','cache_seed','legacy']:(WORK/n).mkdir()
 records=[];plans={};legacy=[];pins=[];locks=set()
 for sid,origin in ORIGINS.items():
  old=B/origin;w=B/('source_cohort_work_'+origin)
  assert read(old/'private_cache_backup.json')['saved_privately']
  records.append(next(r for r in read(w/'plan.json')if r['pilot_id']==sid));plans[sid]=read(w/'legacy_funding_plan.json')[sid]
  shutil.copytree(w/'legacy'/sid,WORK/'legacy'/sid)
  legacy += [m for m in read(old/'legacy_reuse_manifest.json')['responses']if m['source_id']==sid]
  folder=WORK/'cache_seed'/sid;folder.mkdir()
  for key in ['boundary']+[f'native_tail_{i:04d}'for i in range(COUNTS[sid])]:
   p=w/'requests'/sid/(key+'.json');m=read(p);assert m['http_status']==200 and sha(p.with_suffix('.json.gz'))==m['sha256']
   for suffix in ['.json','.json.gz']:shutil.copyfile(p.with_suffix(suffix),folder/(key+suffix))
   pins.append(dict(source_id=sid,key=key,origin_scope=origin,original_marker_sha256=sha(p),sha256=m['sha256'],endpoint_sha256=m['endpoint_sha256']))
  locks.update(read(w/'historical_locks.json'))
 parent=B/ORIGINS['comparison_0026'];pw=B/('source_cohort_work_'+parent.name)
 for n in ['remaining_source_registry.json','retained_bridge_native_cursors.json','parent_native_cursors.json']:shutil.copyfile(pw/n,WORK/n)
 locks.update(str(w/'collector.lock')for w in B.glob('source_cohort_work_*')if w!=WORK)
 for p in locks:Path(p).parent.mkdir(parents=True,exist_ok=True)
 write(WORK/'historical_locks.json',sorted(locks));write(WORK/'plan.json',records);write(WORK/'legacy_funding_plan.json',plans);write(WORK/'cached_native_seed_manifest.json',dict(responses=pins))
 write(OUT/'legacy_reuse_manifest.json',dict(responses=legacy));write(OUT/'offline_reuse_manifest.json',dict(responses=[]))
 shutil.copyfile(parent/'retained_deep_queue.json',OUT/'retained_deep_queue.json')
 state.update(active_scope=NAME,status='prepared_unit',next_unit=21,can_continue=True);write(c.CAMPAIGN/'progress.json',state);write(OUT/'prepared_campaign_state.json',state)
 q=deepcopy(read(parent/'protocol.json'))
 replacements={'baseline_view':parent/'precutoff_feature_view.json.gz','parent_private_backup':parent/'private_cache_backup.json','parent_protocol':parent/'protocol.json','parent_resume':parent/'resume_checkpoint.json','parent_verification':parent/'independent_verification.json','prepared_campaign_state':OUT/'prepared_campaign_state.json','legacy_reuse':OUT/'legacy_reuse_manifest.json','offline_reuse':OUT/'offline_reuse_manifest.json','legacy_funding_plan':WORK/'legacy_funding_plan.json'}
 for k,pin in q['inputs'].items():
  p=replacements.get(k,(parent/pin['file']).resolve());pin.update(file=os.path.relpath(p,OUT),sha256=sha(p))
 for k,p in [('pair_driver',Path(__file__)),('cached_seed',WORK/'cached_native_seed_manifest.json'),('saved_access',B/'mempool_remaining_fifty_20261116_access_retry_20261117/private_cache_backup.json')]:q['inputs'][k]=dict(file=os.path.relpath(p,OUT),sha256=sha(p))
 funding=sum(len(p['reference_parent_txids'])for p in plans.values());budget=86+4+funding
 q.update(pass_name=NAME,parent_scope=parent.name,campaign_unit=21,source_ids=list(ORIGINS),prepared_at=datetime.now(timezone.utc).isoformat(),baseline_vectors=1457,maximum_requests=budget,maximum_audit_tape_records=budget+14,per_source_replay_page_caps={s:49 for s in ORIGINS},per_source_new_page_caps=CAPS,original_successful_new_pages=COUNTS,original_unknown_page_intents={'comparison_0026':0,'comparison_0157':1},original_failed_page_intents={'comparison_0026':1,'comparison_0157':0},maximum_new_native_pages=50,offline_native_pages_reused=12,private_plan_sha256=sha(WORK/'plan.json'),private_legacy_funding_plan_sha256=sha(WORK/'legacy_funding_plan.json'),private_lock_manifest_sha256=sha(WORK/'historical_locks.json'),private_parent_native_cursors_sha256=sha(WORK/'parent_native_cursors.json'),private_retained_bridge_native_cursors_sha256=sha(WORK/'retained_bridge_native_cursors.json'))
 write(OUT/'protocol.json',q);write(OUT/'preparation_verification.json',dict(status='passed',cached_responses=14,maximum_new_pages=CAPS,original_selection_sha256=sha(c.CAMPAIGN/'selection.json'),provider_requests=0))
 return {'scope':NAME,'maximum_requests':budget}
p=argparse.ArgumentParser();p.add_argument('command',choices=['prepare','run','finish']);cmd=p.parse_args().command
r=prepare()if cmd=='prepare'else engine.run()if cmd=='run'else engine.finish()
if r is not None:print(__import__('json').dumps(r))
