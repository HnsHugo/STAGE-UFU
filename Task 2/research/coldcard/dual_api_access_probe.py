"""One status GET in a fresh published scope; never a consumed-scope retry."""
from datetime import datetime,timezone,timedelta
from email.utils import parsedate_to_datetime
import json,os,sys
from pathlib import Path
from dual_api_frontier import exclusive_run,PROVIDERS
from journaled_esplora import JournaledEsplora
from independent_mempool_pilot import status_check
from prepare_frontier_checkpoint import read,write,sha
BASE=Path(__file__).resolve().parent
POLICY=BASE/'comparison_access_retries_20261030/retry_policy.json'
SCOPE='dual_api_blockstream_access_20261117_01'
OUT=BASE/SCOPE;WORK=BASE/('source_cohort_work_'+SCOPE)

def prepare():
    assert not OUT.exists()and not WORK.exists()
    p=read(POLICY);assert p['collector_lease']['state']=='idle'
    provider=PROVIDERS[1];gate=p['provider_access_policies'][provider]
    due=gate.get('next_network_attempt_not_before')
    assert not due or datetime.now(timezone.utc)>=datetime.fromisoformat(due)
    parent=BASE/'source_cohort_work_mempool_remaining_fifty_20261116_round_02_unit_16'
    record=next(r for r in read(parent/'plan.json')if r['pilot_id']=='comparison_0250')
    locks=set(read(parent/'historical_locks.json'))|{str(w/'collector.lock')for w in BASE.glob('source_cohort_work_*')}
    locks.add(str(BASE/'source_cohort_work_dual_api_automation_20261117/collector.lock'))
    with exclusive_run(locks):
        OUT.mkdir();WORK.mkdir(mode=0o700);write(WORK/'plan.json',[record]);write(WORK/'historical_locks.json',sorted(locks))
        q=dict(scope=SCOPE,provider=provider,source_ids=[record['pilot_id']],maximum_requests=1,
            authorization='Explicit user request 17 November: alternate independently eligible public APIs with no repeated saved work',
            purpose='Fresh before-reference status validation only, no history page and no feature promotion',
            plan_sha256=sha(WORK/'plan.json'),lock_manifest_sha256=sha(WORK/'historical_locks.json'),
            code_sha256=sha(Path(__file__)),transport_sha256=sha(BASE/'journaled_esplora.py'),
            original_gate=gate,baseline_vectors=1463)
        write(OUT/'protocol.json',q)
        now=datetime.now(timezone.utc);p['collector_lease']=dict(state='running',owner=SCOPE,provider=provider,
            protocol=SCOPE+'/protocol.json',protocol_sha256=sha(OUT/'protocol.json'),
            started_at=now.isoformat(),expires_at=(now+timedelta(hours=2)).isoformat(),operational_locks_released=False)
        p['active_collection_scope']=SCOPE;write(POLICY,p);write(OUT/'authorization.json',dict(collector_lease=p['collector_lease']))
    return dict(scope=SCOPE,prepared=True,maximum_requests=1)

def run(commit):
    q=read(OUT/'protocol.json');p=read(POLICY);lease=p['collector_lease']
    assert not(OUT/'run_receipt.json').exists()
    assert q['code_sha256']==sha(Path(__file__))and q['transport_sha256']==sha(BASE/'journaled_esplora.py')
    assert q['plan_sha256']==sha(WORK/'plan.json')and q['lock_manifest_sha256']==sha(WORK/'historical_locks.json')
    def check():
        live=read(POLICY)['collector_lease']
        assert live==lease and live['state']=='running'and live['owner']==SCOPE
        assert live['protocol_sha256']==sha(OUT/'protocol.json')
        assert datetime.now(timezone.utc)<datetime.fromisoformat(live['expires_at'])
    record=read(WORK/'plan.json')[0];error=None
    with exclusive_run(read(WORK/'historical_locks.json')+[str(WORK/'collector.lock')]):
        check();write(WORK/'published_lease.json',dict(commit=commit,collector_lease=lease))
        client=JournaledEsplora(q['provider'],WORK,record['pilot_id'],1,check)
        try:status_check(record,client.get('reference_status','/tx/'+record['payment_txid']+'/status'))
        except BaseException as e:error=type(e).__name__
        meta=read(WORK/'requests'/record['pilot_id']/'reference_status.json')
        if meta.get('http_status')==200:assert sha(WORK/'requests'/record['pilot_id']/'reference_status.json.gz')==meta['sha256']
        receipt=dict(scope=SCOPE,status='passed'if error is None else'stopped',error_type=error,
            provider_requests=1,http200=int(meta.get('http_status')==200),http_status=meta.get('http_status'),
            history_pages=0,features_promoted=0,original_vectors_preserved=1463,published_commit=commit,
            operational_locks_released=True,provider_outcome=meta.get('provider_outcome'))
        write(OUT/'run_receipt.json',receipt)
        p=read(POLICY);assert p['collector_lease']==lease
        p['collector_lease'].update(state='idle',owner=None,last_owner=SCOPE,expires_at=None,
            finished_at=datetime.now(timezone.utc).isoformat(),operational_locks_released=True)
        p['active_collection_scope']='none';gate=p['provider_access_policies'][q['provider']]
        gate.update(last_http_status=meta.get('http_status'),last_access_revalidation_scope=SCOPE)
        if error:
            now=datetime.now(timezone.utc);delay=7200
            retry=meta.get('retry_after')
            if retry:
                try:delay=max(delay,int(retry))
                except ValueError:delay=max(delay,(parsedate_to_datetime(retry)-now).total_seconds())
            gate.update(status='access_denied'if meta.get('http_status')==403 else'cooldown',
                next_network_attempt_not_before=(now+timedelta(seconds=delay)).isoformat(),no_new_probe_authorized=True)
        else:gate.update(status='access_revalidated',next_network_attempt_not_before=None,no_new_probe_authorized=False)
        write(POLICY,p)
    return receipt
if __name__=='__main__':print(json.dumps(prepare()if sys.argv[1]=='prepare'else run(sys.argv[2])))
