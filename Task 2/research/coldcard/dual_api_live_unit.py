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
from dual_api_frontier import collect_switch,exclusive_run,PROVIDERS
from journaled_esplora import JournaledEsplora
import collect_reference_tail as tail
BASE=Path(__file__).resolve().parent
SCOPE='dual_api_blockstream_bridge_20261117_01';OUT=BASE/SCOPE;WORK=BASE/('source_cohort_work_'+SCOPE)
POLICY=BASE/'comparison_access_retries_20261030/retry_policy.json'
PARENT='mempool_remaining_fifty_20261116_round_02_unit_16';SID='comparison_0250'

def prepare():
    assert not OUT.exists()and not WORK.exists()
    p=read(POLICY);assert p['collector_lease']['state']=='idle'
    gate=p['provider_access_policies'][PROVIDERS[1]];assert gate['status']=='access_revalidated'
    source=BASE/('source_cohort_work_'+PARENT);old=read(source/'seeds'/SID/'seed_raw.json.gz')
    record=next(r for r in read(source/'plan.json')if r['pilot_id']==SID)
    values=list(old['transactions']);cursor=read(source/'seeds'/SID/'bridge_seed.json')['native_cursor'];seen={record['payment_txid']}|{t['txid']for t in values};height=values[-1]['status']['block_height'];pins=[]
    for i in range(14):
        f=source/'requests'/SID/f'extension_{i:04d}.json';m=read(f);body=f.with_suffix('.json.gz')
        assert m['http_status']==200 and m['sha256']==sha(body)
        assert m['endpoint_sha256']==hashlib.sha256(('/address/'+record['address']+'/txs/chain/'+cursor).encode()).hexdigest()
        page=read(body);height=validate_page(record,page,seen,height);assert page
        values.extend(page);cursor=page[-1]['txid'];pins.append(dict(file=str(body.relative_to(BASE)),sha256=sha(body)))
    assert cursor==read(source/'native_cursors.json')[SID]['cursor']
    locks=set(read(source/'historical_locks.json'))|{str(w/'collector.lock')for w in BASE.glob('source_cohort_work_*')}
    locks.add(str(BASE/'source_cohort_work_dual_api_automation_20261117/collector.lock'));locks.add(str(WORK/'collector.lock'))
    with exclusive_run(locks):
        OUT.mkdir();WORK.mkdir(exist_ok=True,mode=0o700);write(WORK/'plan.json',[record]);write(WORK/'historical_locks.json',sorted(locks))
        seed=dict(anchor=old['anchor'],transactions=values,provider=PROVIDERS[0],actual_native_cursor=cursor)
        atomic_write(WORK/'seed.json.gz',gzip.compress(json_bytes(seed),mtime=0))
        q=dict(scope=SCOPE,provider=PROVIDERS[1],source_ids=[SID],parent_scope=PARENT,
            unit_kind='explicitly_authorized_reverse_bridge',maximum_new_native_pages=50,maximum_requests=53+record['registry_input_slots'],
            baseline_vectors=1463,original_successful_unfinished_pages_reused=14,seed_sha256=sha(WORK/'seed.json.gz'),
            plan_sha256=sha(WORK/'plan.json'),locks_sha256=sha(WORK/'historical_locks.json'),
            source_pins=pins,seed_origin_sha256=sha(source/'seeds'/SID/'seed_raw.json.gz'),
            baseline_view_sha256=sha(BASE/PARENT/'precutoff_feature_view.json.gz'),
            code_pins={n:sha(BASE/n)for n in ['dual_api_live_unit.py','dual_api_frontier.py','journaled_esplora.py']})
        write(OUT/'protocol.json',q);now=datetime.now(timezone.utc)
        p['collector_lease']=dict(state='running',owner=SCOPE,provider=q['provider'],protocol=SCOPE+'/protocol.json',
            protocol_sha256=sha(OUT/'protocol.json'),started_at=now.isoformat(),expires_at=(now+timedelta(hours=2)).isoformat(),operational_locks_released=False)
        p['active_collection_scope']=SCOPE;write(POLICY,p);write(OUT/'authorization.json',dict(collector_lease=p['collector_lease']))
    return dict(scope=SCOPE,prepared=True,old_unfinished_pages_preserved=14)

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
            available_vectors=sum(r['features']is not None for r in view['rows']),original_unfinished_pages_reused=14,
            independent_journal_replay='passed',operational_locks_released=True,published_commit=commit)
        write(OUT/'run_receipt.json',receipt);write(OUT/'audit.json',dict(status='passed',**receipt,private_frontier_sha256=sha(WORK/'verified_frontier.json.gz')))
        p=read(POLICY);assert p['collector_lease']==lease;p['collector_lease'].update(state='idle',owner=None,last_owner=SCOPE,expires_at=None,finished_at=datetime.now(timezone.utc).isoformat(),operational_locks_released=True);p['active_collection_scope']='none'
        if error:
            failed=next(m for m in markers if m.get('http_status')!=200);g=p['provider_access_policies'][q['provider']]
            g.update(last_http_status=failed.get('http_status'),status='access_denied'if failed.get('http_status')==403 else'cooldown',no_new_probe_authorized=True,next_network_attempt_not_before=(datetime.now(timezone.utc)+timedelta(hours=2)).isoformat())
        write(POLICY,p)
    return receipt
if __name__=='__main__':print(json.dumps(prepare()if sys.argv[1]=='prepare'else run(sys.argv[2])))
