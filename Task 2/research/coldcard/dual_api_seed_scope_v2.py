"""Offline source selection: old audited frontier plus latest global feature view."""
from pathlib import Path
from copy import deepcopy
import gzip,hashlib,sys
from prepare_frontier_checkpoint import read,write,sha
from source_cohort import atomic_write
from build_source_registry import json_bytes
from dual_api_frontier import exclusive_run
BASE=Path(__file__).resolve().parent

def verified_native_cursor(source,origin,sid,record,raw,entry):
 """Replay saved Mempool pages in native order; never derive a cursor from a union."""
 from independent_mempool_native import validate_page
 audit=read(origin/'independent_verification.json')
 assert sha(source/'native_cursors.json')==audit['private_native_cursors_sha256']
 current=read(source/'native_cursors.json')[sid];cursor=current['cursor']
 assert current['provider']==raw['provider']=='https://mempool.space/api'
 assert current['finalized']and not current['pagination_exhausted']
 if 'actual_native_last_cursor'in raw:
  assert raw['actual_native_last_cursor']==cursor
  return cursor
 assert entry['pages_fetched']==raw['pages_fetched']==current['saved_native_pages']
 folder=source/'requests'/sid
 def response(key,endpoint):
  marker=read(folder/(key+'.json'));body=folder/(key+'.json.gz')
  assert marker['http_status']==200 and 'error_type'not in marker
  assert marker['provider']==raw['provider']
  assert marker['endpoint_sha256']==hashlib.sha256(endpoint.encode()).hexdigest()
  assert marker['sha256']==sha(body)
  return read(body)
 anchor=response('reference','/tx/'+record['payment_txid']);assert anchor==raw['anchor']
 actual=record['payment_txid'];seen={actual};height=record['cutoff_height'];txs=[]
 for i in range(entry['pages_fetched']):
  page=response(f'tail_{i:04d}','/address/'+record['address']+'/txs/chain/'+actual)
  assert page
  height=validate_page(record,page,seen,height);txs.extend(page);actual=page[-1]['txid']
 assert txs==raw['transactions']and actual==cursor
 return cursor

def prepare(scope,global_parent,sid):
 assert all('/'not in s and s not in ['.','..']for s in [scope,global_parent,sid])
 out=BASE/scope;work=BASE/('source_cohort_work_'+scope);parent=BASE/global_parent
 assert not out.exists()and not work.exists()
 policy=read(BASE/'comparison_access_retries_20261030/retry_policy.json');assert policy['collector_lease']['state']=='idle'
 assert read(parent/'private_cache_backup.json')['saved_privately']
 view=read(parent/'precutoff_feature_view.json.gz');row=next(r for r in view['rows']if r['source_id']==sid);assert row['features']is None
 resume=read(parent/'resume_checkpoint.json');queued=next(r for r in resume['retained_native_partial_queue']if r['source_id']==sid)
 origin=BASE/queued['evidence_scope'];source=BASE/('source_cohort_work_'+origin.name)
 assert read(origin/'private_cache_backup.json')['saved_privately']and read(origin/'independent_verification.json')['status']=='passed'
 entry=read(origin/'checkpoint.json.gz')['entries'][sid];raw_path=source/entry['raw_file'];assert sha(raw_path)==entry['raw_sha256'];raw=read(raw_path)
 record=next(r for r in read(source/'plan.json')if r['pilot_id']==sid)
 for key in ['address_sha256','payment_txid_sha256','cutoff_height','cutoff_block_hash']:assert record[key]==row[key]
 cursor=verified_native_cursor(source,origin,sid,record,raw,entry)
 assert hashlib.sha256(cursor.encode()).hexdigest()==queued['last_native_cursor_sha256']
 assert not raw['pagination_exhausted']and entry['features']is None
 locks=set(read(BASE/('source_cohort_work_'+global_parent)/'historical_locks.json'))|set(read(source/'historical_locks.json'))|{str(w/'collector.lock')for w in BASE.glob('source_cohort_work_*')}
 locks|={str(work/'collector.lock'),str(BASE/'source_cohort_work_dual_api_automation_20261117/collector.lock')}
 with exclusive_run(locks):
  out.mkdir();work.mkdir(exist_ok=True,mode=0o700);write(work/'plan.json',[record]);write(work/'historical_locks.json',sorted(locks))
  frontier=dict(provider=queued['provider'],anchor=raw['anchor'],transactions=raw['transactions'],actual_native_cursor=cursor,pagination_exhausted=False,native_pages=queued['native_pages'],new_transactions=0,verified_overlap=0,status='offline_seed_not_new_coverage')
  atomic_write(work/'verified_frontier.json.gz',gzip.compress(json_bytes(frontier),mtime=0))
  atomic_write(out/'precutoff_feature_view.json.gz',(parent/'precutoff_feature_view.json.gz').read_bytes())
  selected=next(r for r in resume['retained_native_partial_queue']if r['source_id']==sid);selected.update(evidence_scope=scope,private_raw_file='verified_frontier.json.gz',private_raw_sha256=sha(work/'verified_frontier.json.gz'),finalized=True)
  resume.update(pass_name=scope,status='offline_source_seed',next_action='Prepare fresh native scope from saved actual cursor; no old page replay');write(out/'resume_checkpoint.json',resume)
  write(out/'protocol.json',dict(scope=scope,provider=queued['provider'],source_ids=[sid],global_parent=global_parent,source_parent=origin.name,source_raw_sha256=sha(raw_path),global_view_sha256=sha(parent/'precutoff_feature_view.json.gz'),seed_sha256=sha(work/'verified_frontier.json.gz'),code_sha256=sha(Path(__file__)),provider_requests=0))
  assert read(work/'verified_frontier.json.gz')['transactions']==raw['transactions']
  assert (out/'precutoff_feature_view.json.gz').read_bytes()==(parent/'precutoff_feature_view.json.gz').read_bytes()
  write(out/'audit.json',dict(status='passed',offline_seed_only=True,provider_requests=0,new_transactions=0,available_vectors=sum(r['features']is not None for r in view['rows']),latest_global_view_preserved=True,old_audited_frontier_preserved=True))
 return dict(scope=scope,source_id=sid,requests=0)
if __name__=='__main__':print(__import__('json').dumps(prepare(*sys.argv[1:])))

