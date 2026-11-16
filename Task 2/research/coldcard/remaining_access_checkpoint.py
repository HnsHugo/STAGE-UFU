"""One two-request access validation after the saved cooldown, with no predictors."""
import argparse
from datetime import datetime,timezone,timedelta
import gzip
import hashlib
import os
from pathlib import Path
import shutil

import recorded_remaining_campaign as campaign
from build_source_registry import json_bytes
from prepare_frontier_checkpoint import read,sha,write
from independent_mempool_pilot import PROVIDER,status_check
from recorded_mempool_resume import verify_dispatch_evidence

BASE=campaign.BASE;OUT=BASE/(campaign.CAMPAIGN.name+'_access');WORK=BASE/('source_cohort_work_'+OUT.name)


def prepare():
    assert not OUT.exists()and not WORK.exists()
    p=read(campaign.POLICY);assert p['collector_lease']['state']=='idle'and p['active_collection_scope']=='none'
    parent=(BASE/p['latest_consolidated_prefix_view']).parent
    assert read(parent/'private_cache_backup.json')['saved_privately']
    first=read(campaign.CAMPAIGN/'selection.json')['source_ids'][0]
    registry=BASE/('source_cohort_work_'+campaign.CAMPAIGN.name+'_registry')/'remaining_source_registry.json'
    record=next(r for r in read(registry)if r['pilot_id']==first)
    OUT.mkdir();WORK.mkdir(mode=0o700)
    for name in ['requests','raw','results']:(WORK/name).mkdir()
    write(WORK/'plan.json',[record]);shutil.copyfile(registry,WORK/'remaining_source_registry.json')
    previous=BASE/('source_cohort_work_'+parent.name)
    shutil.copyfile(previous/'retained_bridge_native_cursors.json',WORK/'retained_bridge_native_cursors.json')
    write(WORK/'parent_native_cursors.json',{})
    locks=set(read(previous/'historical_locks.json'))|{str(w/'collector.lock')for w in BASE.glob('source_cohort_work_*')if w!=WORK}
    for name in locks:Path(name).parent.mkdir(parents=True,exist_ok=True)
    write(WORK/'historical_locks.json',sorted(locks));write(OUT/'offline_reuse_manifest.json',dict(responses=[]))
    gate=p['provider_access_policies'][PROVIDER]
    write(OUT/'prior_gate_snapshot.json',dict(provider_policy=gate,authorization='Current user requests completion of all fifty; exactly one bounded revalidation after the recorded cooldown, same provider and transport'))
    paths=dict(baseline_view=parent/'precutoff_feature_view.json.gz',parent_backup=parent/'private_cache_backup.json',
        campaign_selection=campaign.CAMPAIGN/'selection.json',prior_gate=OUT/'prior_gate_snapshot.json',
        identity_registry_reconciliation=campaign.CAMPAIGN/'identity_registry_reconciliation.json',
        recorded_dispatch_runner=BASE/'recorded_mempool_resume.py',native_runner=BASE/'independent_mempool_resume.py',
        access_code=Path(__file__),remaining_campaign=BASE/'recorded_remaining_campaign.py',
        lease_authorization=BASE/'recorded_twenty_campaign.py',tests=campaign.CAMPAIGN/'preflight_tests.json')
    q=dict(pass_name=OUT.name,campaign=campaign.CAMPAIGN.name,kind='bounded_access_revalidation',created_on='2026-11-16',
        source_ids=[first],provider=PROVIDER,authorization='User: Fais les 50 qui reste; persistent explicit API/GitHub authorization; revalidate the saved HTTP503 gate once after cooldown',
        network_not_before=gate['next_network_attempt_not_before'],maximum_requests=2,max_pages_per_address=0,maximum_new_native_pages=0,
        requests_per_second=.2,minimum_dispatch_interval_seconds=5,enforced_dispatch_spacing_seconds=5.25,
        dispatch_clock_evidence='monotonic_ns_and_utc',workers=1,timeout_seconds=45,
        live_policy_file='../comparison_access_retries_20261030/retry_policy.json',
        blockstream_cooldown_preserved_until=p['provider_access_policies']['https://blockstream.info/api']['next_network_attempt_not_before'],
        private_plan_sha256=sha(WORK/'plan.json'),private_lock_manifest_sha256=sha(WORK/'historical_locks.json'),
        private_identity_registry_sha256=sha(WORK/'remaining_source_registry.json'),
        private_retained_bridge_native_cursors_sha256=sha(WORK/'retained_bridge_native_cursors.json'),
        private_parent_native_cursors_sha256=sha(WORK/'parent_native_cursors.json'),
        parent_scope=parent.name,baseline_vectors=1450,model_fits=0,new_scores=0,automation_enabled=False,
        inputs={k:dict(file=os.path.relpath(v,OUT),sha256=sha(v))for k,v in paths.items()})
    write(OUT/'protocol.json',q)
    return dict(scope=OUT.name,maximum_requests=2,network_not_before=q['network_not_before'],provider_requests=0)


def authorize():
    q=read(OUT/'protocol.json')
    assert datetime.now(timezone.utc)>=datetime.fromisoformat(q['network_not_before'])
    return campaign.authorize(OUT.name)


def counter_check(record,counter):
    assert counter['address']==record['address']
    count=counter['chain_stats']['tx_count'];assert type(count)is int and count>=0
    return count


def collect(record,requests,work,q,unused):
    counter=requests.get(record,'availability_counter','/address/'+record['address'])
    count=counter_check(record,counter)
    status_check(record,requests.get(record,'reference_status','/tx/'+record['payment_txid']+'/status'))
    entry=dict(source_id=record['pilot_id'],status='access_validated',current_counter=count,
        features=None,prefix=None,predictors_admitted=False,scientific_rows_changed=0)
    (work/'results'/f"{record['pilot_id']}.json.gz").write_bytes(gzip.compress(json_bytes(entry),mtime=0))
    return entry


def run():
    import independent_mempool_resume as native
    import recorded_mempool_resume as recorded
    native.collect=collect
    recorded.run(OUT/'protocol.json',WORK)


def finish():
    q=read(OUT/'protocol.json');receipt=read(OUT/'run_receipt.json');record=read(WORK/'plan.json')[0]
    assert receipt['operational_locks_released']
    for pin in q['inputs'].values():assert sha((OUT/pin['file']).resolve())==pin['sha256']
    metadata=read(OUT/'request_manifest.json.gz');assert metadata==[read(p)for p in sorted(WORK.glob('requests/*/*.json'))]
    clock=verify_dispatch_evidence(metadata);write(OUT/'dispatch_verification.json',clock)
    assert len(metadata)==receipt['provider_requests']<=2
    endpoints=dict(availability_counter='/address/'+record['address'],reference_status='/tx/'+record['payment_txid']+'/status')
    successful=[];errors=[]
    for m in metadata:
        assert m['provider']==PROVIDER and m['source_id']==record['pilot_id']
        assert m['endpoint_sha256']==hashlib.sha256(endpoints[m['key']].encode()).hexdigest()
        body=WORK/'requests'/record['pilot_id']/(m['key']+'.json.gz')
        if m.get('http_status')==200:
            assert sha(body)==m['sha256'];value=read(body)
            try:
                if m['key']=='availability_counter':counter_check(record,value)
                else:status_check(record,value)
                successful.append(m['key'])
            except(AssertionError,ValueError,KeyError):errors.append('Response contract differs: '+m['key'])
        else:assert not body.exists()
    failures=[m for m in metadata if'error_type'in m]
    assert len(failures)==receipt['failures']
    if failures:assert all(m['started_at']<=min(f['finished_at']for f in failures)for m in metadata)
    available=receipt['status']=='completed'and set(successful)==set(endpoints)and not errors
    report=dict(status='passed',access_available=available,provider_requests=len(metadata),http200=receipt['http200'],
        failures=len(failures),failed_http_statuses=[m.get('http_status')for m in failures],semantic_errors=errors,
        original_http503_preserved=True,scientific_feature_values_changed=0,labels_changed=0,model_fits=0,new_scores=0)
    write(OUT/'coverage_audit.json',report);write(OUT/'independent_verification.json',report)
    p=read(campaign.POLICY);assert p['collector_lease']['owner']==OUT.name
    p['collector_lease'].update(state='idle',owner=None,last_owner=OUT.name,expires_at=None,
        finished_at=datetime.now(timezone.utc).isoformat(),operational_locks_released=True,stop_status=receipt['status'])
    p.update(active_collection_scope='none',coverage_collection_paused=True,automation_enabled=False,
        latest_mempool_access_validation=OUT.name+'/coverage_audit.json')
    gate=p['provider_access_policies'][PROVIDER]
    gate.update(status='access_revalidated_after_cooldown'if available else'stopped_after_access_validation_failure',
        no_new_probe_authorized=not available,operational_validation_required=not available,last_http200=receipt['http200'],
        last_http_status=200 if available else next((m.get('http_status')for m in reversed(metadata)if m.get('http_status')),None),
        last_failure_preserved_in=OUT.name+'/prior_gate_snapshot.json')
    if not available:
        gate.update(next_network_attempt_not_before=(datetime.now(timezone.utc)+timedelta(hours=2)).isoformat(),
            stop_reason='Bounded post-cooldown access revalidation failed; original failure and all fresh evidence preserved')
    write(campaign.POLICY,p);(WORK/'lease_published').unlink(missing_ok=True)
    write(OUT/'collection_stop.json',dict(status=receipt['status'],operational_locks_released=True,restart_same_scope_allowed=False))
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['prepare','authorize','run','finish'])
    result=globals()[parser.parse_args().command]()
    if result is not None:print(__import__('json').dumps(result,sort_keys=True))
