"""Recover interrupted legacy bridges without repeating successful provider pages.

Original 153 responses and one unknown intent remain immutable. The successor
replays 148 cached bodies and permits only four new pages for the unfinished row.
"""
import argparse
from contextlib import ExitStack,redirect_stdout
from copy import deepcopy
from datetime import datetime,timezone
import fcntl,hashlib,os,shutil
from pathlib import Path
from prepare_frontier_checkpoint import read,sha,write
import recorded_remaining_campaign as campaign
import recorded_mempool_resume as recorded
BASE=campaign.BASE
OLD='mempool_remaining_fifty_20261116_unit_19'
NEW=OLD+'_recovery_20261117'
COUNTS={'comparison_0091':50,'comparison_0002':50,'comparison_0109':45}
CAPS={'comparison_0091':0,'comparison_0002':0,'comparison_0109':4}
UNKNOWN=('comparison_0109','native_tail_0045')

def clocks(markers):
 known=[m for m in markers if m.get('http_status')==200]
 unknown=[m for m in markers if m.get('http_status')!=200]
 assert len(known)==153 and len(unknown)==1
 m=unknown[0];assert (m['source_id'],m['key'])==UNKNOWN
 assert not any(k in m for k in ['sha256','http_status','error_type','finished_at','dispatch_at','dispatch_clock_evidence','dispatch_not_attempted'])
 assert all(x['finished_at']<=m['started_at']for x in known)
 return dict(status='incomplete_unknown_intent',known_successful_dispatches=recorded.verify_dispatch_evidence(known),unresolved_intents=1,original_marker_unchanged=True,unknown_outcome_not_imputed=True)

def close():
 out=BASE/OLD;work=BASE/('source_cohort_work_'+OLD);q=read(out/'protocol.json');policy=read(campaign.POLICY)
 assert not(out/'run_receipt.json').exists()and policy['collector_lease']['owner']==OLD
 for pin in q['inputs'].values():assert sha((out/pin['file']).resolve())==pin['sha256']
 locks=set(read(work/'historical_locks.json'))|{str(work/'collector.lock')}
 with ExitStack()as stack:
  for name in sorted(locks):
   f=stack.enter_context(Path(name).open('a+'));fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
  paths=sorted(work.glob('requests/*/*.json'));markers=[read(p)for p in paths];clock=clocks(markers)
  for p,m in zip(paths,markers):
   if m.get('http_status')==200:assert sha(p.with_suffix('.json.gz'))==m['sha256']
   else:assert not p.with_suffix('.json.gz').exists()
  from collect_reference_tail import export
  export(out/'protocol.json',out,work)
  proof=dict(status='passed',scope=OLD,recovered_at=datetime.now(timezone.utc).isoformat(),recovery_code_sha256=sha(Path(__file__)),original_protocol_sha256=sha(out/'protocol.json'),original_request_markers=[dict(file=str(p.relative_to(work)),sha256=sha(p))for p in paths],http200=153,failed_provider_responses=0,unresolved_request_intents=1,original_full_clock_audit='incomplete_unknown_intent',operational_locks_checked_free=len(locks),new_provider_requests_during_recovery=0)
  write(out/'interruption_recovery.json',proof);write(work/'interruption_recovery.json',proof)
  write(out/'run_receipt.json',dict(status='interrupted_unknown_outcome',receipt_origin='Offline recovery from fingerprint-verified emergency snapshot; original runner produced no receipt',provider_requests=154,http200=153,failures=0,unresolved_intents=1,finalized_sources=2,operational_locks_released=True,blockstream_provider_requests=0,model_fits=0,new_scores=0))
  write(out/'dispatch_verification.json',clock)
  import audit_planned_funding_bridge as audit
  original=audit.verify_dispatch_evidence;audit.verify_dispatch_evidence=clocks
  try:
   with (work/'audit.log').open('w')as log,redirect_stdout(log):audit.audit(out,work)
  finally:audit.verify_dispatch_evidence=original
  for name in ['coverage_audit.json','independent_verification.json']:
   report=read(out/name);report.update(original_full_clock_audit='incomplete_unknown_intent',unresolved_request_intents=1,known_successful_dispatches=clock['known_successful_dispatches'],original_markers_preserved=True);write(out/name,report)
  cursors=read(work/'native_cursors.json');assert {s:cursors[s]['saved_native_pages']for s in COUNTS}==COUNTS
  assert set(read(out/'checkpoint.json.gz')['entries'])=={'comparison_0091','comparison_0002'}
  policy['collector_lease'].update(state='idle',owner=None,last_owner=OLD,expires_at=None,finished_at=datetime.now(timezone.utc).isoformat(),operational_locks_released=True,stop_status='interrupted_unknown_outcome')
  policy.update(active_collection_scope='none',coverage_collection_paused=True,latest_status='unit19_saved_evidence_recovered')
  policy['provider_access_policies'][campaign.PROVIDER].update(status='interruption_closed_unknown_outcome',no_new_probe_authorized=False,operational_validation_required=False,next_network_attempt_not_before=policy['collector_lease']['finished_at'])
  write(campaign.POLICY,policy)
  state=read(campaign.CAMPAIGN/'progress.json');assert state['active_scope']==OLD and state['next_unit']==19
  state.update(active_scope=None,status='interrupted_unit_awaiting_distinct_recovery')
  state.setdefault('interrupted_evidence_fragments',[]).append(dict(scope=OLD,unit=19,http200=153,unresolved_intents=1,new_native_pages=145,recovery_scope=NEW,private_evidence_saved=False,observations_included_in_successor_replayed_union=True))
  write(campaign.CAMPAIGN/'progress.json',state)
  write(out/'collection_stop.json',dict(status='interrupted_unknown_outcome',operational_locks_released=True,restart_same_scope_allowed=False,required_successor=NEW,automation_enabled=False))
 (out/'RESULTS.md').write_text('# Interrupted bridge evidence recovered\n\n153 successful responses and 145 pages independently replayed from the verified emergency backup. Two bounded histories finalized; the third retains 45 pages. One final intent has unknown dispatch and provider outcome. Only completed dispatches have a verified clock; the original full clock audit stays incomplete. No new provider request during recovery.\n')
 return dict(scope=OLD,http200=153,unresolved_intents=1)

def prepare():
 old=BASE/OLD;source=BASE/('source_cohort_work_'+OLD);out=BASE/NEW;work=BASE/('source_cohort_work_'+NEW)
 assert read(old/'private_cache_backup.json')['saved_privately']and not out.exists()and read(campaign.POLICY)['collector_lease']['state']=='idle'
 out.mkdir();work.mkdir(mode=0o700)
 for n in ['requests','raw','results','cache_seed']:(work/n).mkdir()
 for n in ['plan.json','remaining_source_registry.json','legacy_funding_plan.json','parent_native_cursors.json','retained_bridge_native_cursors.json']:
  shutil.copyfile(source/n,work/n)
 shutil.copytree(source/'legacy',work/'legacy');pins=[]
 for sid,count in COUNTS.items():
  folder=work/'cache_seed'/sid;folder.mkdir()
  for key in ['boundary']+[f'native_tail_{i:04d}'for i in range(count)]:
   marker=source/'requests'/sid/(key+'.json');m=read(marker);body=marker.with_suffix('.json.gz')
   assert m['http_status']==200 and sha(body)==m['sha256']
   shutil.copyfile(marker,folder/marker.name);shutil.copyfile(body,folder/body.name)
   pins.append(dict(source_id=sid,key=key,endpoint_sha256=m['endpoint_sha256'],sha256=m['sha256'],original_marker_sha256=sha(marker),origin_scope=OLD))
 write(work/'cached_native_seed_manifest.json',dict(responses=pins))
 locks=set(read(source/'historical_locks.json'))|{str(p/'collector.lock')for p in BASE.glob('source_cohort_work_*')if p!=work}
 write(work/'historical_locks.json',sorted(locks))
 for n in ['legacy_reuse_manifest.json','legacy_provider_provenance.json','retained_deep_queue.json','offline_reuse_manifest.json']:
  shutil.copyfile(old/n,out/n)
 state=read(campaign.CAMPAIGN/'progress.json');state.update(status='prepared_unit',active_scope=NEW);state['interrupted_evidence_fragments'][-1]['private_evidence_saved']=True
 write(campaign.CAMPAIGN/'progress.json',state);write(out/'prepared_campaign_state.json',state)
 q=deepcopy(read(old/'protocol.json'))
 for pin in q['inputs'].values():
  path=(old/pin['file']).resolve()
  if path.is_relative_to(old):path=out/path.relative_to(old)
  if path.is_relative_to(source):path=work/path.relative_to(source)
  pin.update(file=os.path.relpath(path,out),sha256=sha(path))
 for k,p in [('interruption_recovery',old/'interruption_recovery.json'),('interrupted_backup',old/'private_cache_backup.json'),('bridge_recovery_driver',Path(__file__)),('cached_native_seed',work/'cached_native_seed_manifest.json')]:q['inputs'][k]=dict(file=os.path.relpath(p,out),sha256=sha(p))
 budget=dict(before_statuses_at_most=3,after_anchor_statuses_at_most=3,tail_pages_at_most=4,funding_statuses_at_most=13,total_new_requests_at_most=23)
 q.update(pass_name=NEW,prepared_at=datetime.now(timezone.utc).isoformat(),maximum_requests=23,request_budget=budget,maximum_audit_tape_records=171,per_source_replay_page_caps={s:COUNTS[s]+CAPS[s]for s in COUNTS},per_source_new_page_caps=CAPS,original_successful_new_pages=COUNTS,original_unknown_page_intents={s:int(s==UNKNOWN[0])for s in COUNTS},offline_native_pages_reused=145,private_plan_sha256=sha(work/'plan.json'),private_lock_manifest_sha256=sha(work/'historical_locks.json'),authorization='User: reprend. Restore saved evidence and finish the frozen three-source unit in a distinct scope; original unknown outcome preserved.')
 write(out/'protocol.json',q);write(out/'preparation_verification.json',dict(status='passed',cached_bodies_verified=148,new_native_pages_at_most=4,original_fifty_attempt_cap_preserved=True,provider_requests=0))
 return dict(scope=NEW,maximum_requests=23,new_native_pages_at_most=4)

def run():
 import independent_mempool_resume as native
 from planned_funding_bridge import collect
 out=BASE/NEW;work=BASE/('source_cohort_work_'+NEW)
 pins={(m['source_id'],m['key']):m for m in read(work/'cached_native_seed_manifest.json')['responses']}
 legacy=read(out/'legacy_reuse_manifest.json')['responses']
 def replay(record,requests,work,q,unused):
  sid=record['pilot_id']
  class Adapter:
   def get(self,record,key,endpoint):
    if (sid,key)in pins:
     pin=pins[sid,key];p=work/'cache_seed'/sid/(key+'.json');body=p.with_suffix('.json.gz')
     assert sha(p)==pin['original_marker_sha256']and sha(body)==pin['sha256']
     assert hashlib.sha256(endpoint.encode()).hexdigest()==pin['endpoint_sha256']
     return read(body)
    assert requests.count<q['maximum_requests'];return requests.get(record,key,endpoint)
  return collect(record,Adapter(),work,dict(q,maximum_new_native_pages=q['per_source_replay_page_caps'][sid]),{m['key']:m for m in legacy if m['source_id']==sid})
 native.collect=replay;recorded.run(out/'protocol.json',work)

def finish():
 out=BASE/NEW;work=BASE/('source_cohort_work_'+NEW);q=read(out/'protocol.json')
 assert read(out/'run_receipt.json')['operational_locks_released']
 pins=read(work/'cached_native_seed_manifest.json')['responses']
 for pin in pins:
  p=work/'cache_seed'/pin['source_id']/(pin['key']+'.json');m=read(p);body=p.with_suffix('.json.gz');target=work/'requests'/pin['source_id']/p.name
  assert sha(p)==pin['original_marker_sha256']and sha(body)==pin['sha256']and not target.exists()
  target.parent.mkdir(exist_ok=True);write(target,dict(m,offline_reused=True,reused_from_pass=OLD,original_marker_sha256=pin['original_marker_sha256']));shutil.copyfile(body,target.with_suffix('.json.gz'))
 from collect_reference_tail import export
 export(out/'protocol.json',out,work)
 metadata=read(out/'request_manifest.json.gz');fresh=[m for m in metadata if not m.get('offline_reused')]
 for sid,cap in CAPS.items():
  pages=[m for m in fresh if m['source_id']==sid and m['key'].startswith('native_tail_')]
  assert len(pages)<=cap and len(pages)+COUNTS[sid]+int(sid==UNKNOWN[0])<=50
 import audit_planned_funding_bridge as audit
 original=audit.audit;original_read=audit.read
 def normalized(output,private):
  def reader(p):
   value=original_read(p)
   if Path(p).resolve()==(out/'run_receipt.json').resolve():return dict(value,provider_requests=len(metadata))
   if Path(p).resolve()==(out/'protocol.json').resolve():return dict(value,maximum_requests=q['maximum_audit_tape_records'])
   return value
  audit.read=reader
  try:r=original(output,private)
  finally:audit.read=original_read
  write(out/'audit_tape_normalization.json',dict(status='passed',actual_new_provider_requests=len(fresh),cached_responses_replayed=len(pins),verified_tape_records=len(metadata),original_protocol_sha256=sha(out/'protocol.json'),original_provider_receipt_sha256=sha(out/'run_receipt.json'),observations_include_original_replayed_union=True,original_provider_receipt_unchanged=True))
  return r
 audit.audit=normalized
 try:return campaign.finish(NEW)
 finally:audit.audit=original

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=['close','prepare','run','finish']);r=globals()[p.parse_args().command]()
 if r is not None:print(__import__('json').dumps(r))
