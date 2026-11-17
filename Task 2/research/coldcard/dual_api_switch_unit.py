"""One fresh reverse-provider bridge with journal replay and atomic page checkpoints."""
from copy import deepcopy
from datetime import datetime,timezone,timedelta
import gzip,hashlib,json,sys
from pathlib import Path
from build_source_registry import json_bytes
from prepare_frontier_checkpoint import read,write,sha
from source_cohort import atomic_write
from independent_mempool_native import validate_page
from independent_mempool_pilot import status_check
from dual_api_frontier import exclusive_run,PROVIDERS
from dual_api_frontier import collect_switch
from journaled_esplora import JournaledEsplora
import collect_reference_tail as tail
BASE=Path(__file__).resolve().parent
SCOPE='dual_api_blockstream_bridge_20261117_01';OUT=BASE/SCOPE;WORK=BASE/('source_cohort_work_'+SCOPE)
POLICY=BASE/'comparison_access_retries_20261030/retry_policy.json'
PARENT='mempool_remaining_fifty_20261116_round_02_unit_16';SID='comparison_0250'

def prepare():
    assert not OUT.exists()and not WORK.exists()
    p=read(POLICY);assert p['collector_lease']['state']=='idle'
    source=BASE/('source_cohort_work_'+PARENT);prior=read(BASE/PARENT/'protocol.json');provider=PROVIDERS[0]if prior['provider']==PROVIDERS[1]else PROVIDERS[1]
    gate=p['provider_access_policies'][provider];due=gate.get('next_network_attempt_not_before')
    assert gate.get('status')not in ['access_denied','disabled']and(not due or datetime.now(timezone.utc)>=datetime.fromisoformat(due))
    assert read(BASE/PARENT/'private_cache_backup.json')['saved_privately']
    record=next(r for r in read(source/'plan.json')if r['pilot_id']==SID)
    raw=source/'verified_frontier.json.gz';seed=read(raw);assert seed['provider']==prior['provider'] and not seed['pagination_exhausted']
    resume=read(BASE/PARENT/'resume_checkpoint.json');entry=next(r for r in resume['retained_native_partial_queue']if r['source_id']==SID)
    assert sha(raw)==entry['private_raw_sha256']
    locks=set(read(source/'historical_locks.json'))|{str(w/'collector.lock')for w in BASE.glob('source_cohort_work_*')}
    locks.add(str(BASE/'source_cohort_work_dual_api_automation_20261117/collector.lock'));locks.add(str(WORK/'collector.lock'))
    with exclusive_run(locks):
        OUT.mkdir();WORK.mkdir(exist_ok=True,mode=0o700);write(WORK/'plan.json',[record]);write(WORK/'historical_locks.json',sorted(locks))
        atomic_write(WORK/'seed.json.gz',gzip.compress(json_bytes(seed),mtime=0))
        baseline=read(BASE/PARENT/'precutoff_feature_view.json.gz');assert next(r for r in baseline['rows']if r['source_id']==SID)['features']is None
        q=dict(scope=SCOPE,provider=provider,source_ids=[SID],parent_scope=PARENT,unit_kind='explicit_cross_provider_bridge',maximum_new_native_pages=50,maximum_requests=53+record['registry_input_slots'],baseline_vectors=sum(r['features']is not None for r in baseline['rows']),original_successful_unfinished_pages_reused=0,seed_sha256=sha(WORK/'seed.json.gz'),plan_sha256=sha(WORK/'plan.json'),locks_sha256=sha(WORK/'historical_locks.json'),source_pins=[dict(file=str(raw.relative_to(BASE)),sha256=sha(raw))],baseline_view_sha256=sha(BASE/PARENT/'precutoff_feature_view.json.gz'),code_pins={n:sha(BASE/n)for n in ['dual_api_switch_unit.py','dual_api_frontier.py','journaled_esplora.py','provider_backoff.py']})
        write(OUT/'protocol.json',q);now=datetime.now(timezone.utc)
        p['collector_lease']=dict(state='running',owner=SCOPE,provider=provider,protocol=SCOPE+'/protocol.json',protocol_sha256=sha(OUT/'protocol.json'),started_at=now.isoformat(),expires_at=(now+timedelta(hours=2)).isoformat(),operational_locks_released=False)
        p['active_collection_scope']=SCOPE;write(POLICY,p);write(OUT/'authorization.json',dict(collector_lease=p['collector_lease']))
    return dict(scope=SCOPE,prepared=True,parent=PARENT,source_id=SID)

def run(commit):
    assert not(OUT/'run_receipt.json').exists();q=read(OUT/'protocol.json');lease=read(POLICY)['collector_lease']
    assert all(sha(BASE/n)==h for n,h in q['code_pins'].items())
    assert sha(WORK/'seed.json.gz')==q['seed_sha256']and sha(WORK/'plan.json')==q['plan_sha256']and sha(WORK/'historical_locks.json')==q['locks_sha256']
    assert all(sha(BASE/p['file'])==p['sha256']for p in q['source_pins'])
    seed=read(WORK/'seed.json.gz');record=read(WORK/'plan.json')[0]
    def check():
        live=read(POLICY)['collector_lease'];assert live==lease and live['owner']==SCOPE and live['state']=='running'
        assert live['protocol_sha256']==sha(OUT/'protocol.json')and datetime.now(timezone.utc)<datetime.fromisoformat(live['expires_at'])
    result=None;error=None;parents={}
    with exclusive_run(read(WORK/'historical_locks.json')):
        check();client=JournaledEsplora(q['provider'],WORK,SID,q['maximum_requests'],check)
        def save(snapshot):atomic_write(WORK/'page_checkpoint.json.gz',gzip.compress(json_bytes(snapshot),mtime=0))
        try:
            result=collect_switch(record,seed['anchor'],seed['transactions'],q['provider'],client.get,save)
            if result['pagination_exhausted']:
                ids={t['txid']for t in result['transactions']}
                for vin in tail.anchor_check(record,seed['anchor']):
                    if vin['txid']not in ids and vin['txid']not in parents:
                        status=client.get('parent_'+vin['txid'],'/tx/'+vin['txid']+'/status');status_check(record,status);parents[vin['txid']]=status
        except Exception as e:error=type(e).__name__
        markers=[read(p)for p in sorted((WORK/'requests'/SID).glob('*.json'))]
        assert client.count==len(markers)
        for m in markers:
            if m.get('http_status')==200:assert sha(WORK/'requests'/SID/(m['key']+'.json.gz'))==m['sha256']
        replay_snapshots=[]
        def replay(key,endpoint):
            m=read(WORK/'requests'/SID/(key+'.json'))
            assert m['provider']==q['provider']and m['endpoint_sha256']==hashlib.sha256(endpoint.encode()).hexdigest()
            if m.get('http_status')!=200:raise ValueError('Recorded provider stop')
            return read(WORK/'requests'/SID/(key+'.json.gz'))
        try:replayed=collect_switch(record,seed['anchor'],seed['transactions'],q['provider'],replay,replay_snapshots.append)
        except Exception:
            assert error is not None
        if replay_snapshots:
            snapshot=read(WORK/'page_checkpoint.json.gz');assert snapshot==replay_snapshots[-1]
        else:snapshot=dict(transactions=seed['transactions'],native_pages=0,new_transactions=0,verified_overlap=0,pagination_exhausted=False,actual_native_cursor=None)
        view=read(BASE/PARENT/'precutoff_feature_view.json.gz');assert sha(BASE/PARENT/'precutoff_feature_view.json.gz')==q['baseline_view_sha256']
        baseline=deepcopy(view);row=next(r for r in view['rows']if r['source_id']==SID);assert row['features']is None
        features=None
        if error is None:
            after=read(WORK/'requests'/SID/'reference_after.json.gz')
            values=sorted(result['transactions'],key=lambda t:(-t['status']['block_height'],t['txid']))
            checked=tail.tail_check(record,seed['anchor'],values,result['pagination_exhausted'],after,parents)
            features=checked['features']
            if features is not None:
                sys.path.insert(0,str(BASE.parent/'external_cases/cryptobilis_to_coldcard_20261109'))
                from experiment import recount_features
                assert features==recount_features(checked['prefix'],record['cutoff_height'])
                row['features']=features;row['precutoff_history_status']='complete_prior_prefix'
                row['precutoff_history_provenance']=dict(pass_name=SCOPE,provider=q['provider'],method='complete-block overlap, native cursor, journal replay and independent feature recount')
        for a,b in zip(view['rows'],baseline['rows']):
            if a['source_id']!=SID:assert a==b
            else:
                for k in ['labels','cutoff_height','cutoff_block_hash','address_sha256','payment_txid_sha256','full_history_status']:assert a.get(k)==b.get(k)
        atomic_write(OUT/'precutoff_feature_view.json.gz',gzip.compress(json_bytes(view),mtime=0))
        atomic_write(WORK/'verified_frontier.json.gz',gzip.compress(json_bytes(dict(snapshot,anchor=seed['anchor'])),mtime=0))
        receipt=dict(scope=SCOPE,status='stopped'if error else'completed',error_type=error,http200=sum(m.get('http_status')==200 for m in markers),
            provider_requests=len(markers),failures=sum(m.get('http_status')!=200 for m in markers),native_pages=snapshot['native_pages'],
            new_transactions=snapshot['new_transactions'],verified_overlap=snapshot['verified_overlap'],new_complete=int(features is not None),
            available_vectors=sum(r['features']is not None for r in view['rows']),original_unfinished_pages_reused=q['original_successful_unfinished_pages_reused'],
            independent_journal_replay='passed',operational_locks_released=True,published_commit=commit)
        write(OUT/'run_receipt.json',receipt);write(OUT/'audit.json',dict(**receipt,verification_status='passed',private_frontier_sha256=sha(WORK/'verified_frontier.json.gz')))
        p=read(POLICY);assert p['collector_lease']==lease;p['collector_lease'].update(state='idle',owner=None,last_owner=SCOPE,expires_at=None,finished_at=datetime.now(timezone.utc).isoformat(),operational_locks_released=True);p['active_collection_scope']='none'
        if error:
            failed=next(m for m in markers if m.get('http_status')!=200);g=p['provider_access_policies'][q['provider']]
            from provider_backoff import deadline
            due,delay=deadline(failed,g)
            g.update(last_retry_delay_seconds=delay,last_http_status=failed.get('http_status'),status='access_denied'if failed.get('http_status')==403 else'cooldown',no_new_probe_authorized=True,next_network_attempt_not_before=due)
        write(POLICY,p)
    return receipt
if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['prepare','run']);parser.add_argument('scope');parser.add_argument('parent');parser.add_argument('source');parser.add_argument('commit',nargs='?');a=parser.parse_args()
    assert all('/'not in s and s not in ['.','..']for s in [a.scope,a.parent,a.source])
    SCOPE,PARENT,SID=a.scope,a.parent,a.source;OUT=BASE/SCOPE;WORK=BASE/('source_cohort_work_'+SCOPE)
    print(json.dumps(prepare()if a.command=='prepare'else run(a.commit)))
