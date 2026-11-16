"""Close a zero-network preparation and clone its frozen unit to a fresh scope.

The original protocol/authorization and all completed data stay immutable.
No provider request is made by either administrative command.
"""
import argparse
from contextlib import ExitStack
from copy import deepcopy
from datetime import datetime,timezone
import fcntl
import gzip
import os
from pathlib import Path
import shutil

from build_source_registry import json_bytes
from prepare_frontier_checkpoint import read,sha,write
from planned_funding_bridge import legacy_source,funding_plan
from recorded_mempool_resume import verify_dispatch_evidence
import recorded_remaining_campaign as campaign

BASE=campaign.BASE
OLD='mempool_remaining_fifty_20261116_unit_06'
NEW=OLD+'_recovery_20261116'
PUBLISHED_PREPARATION='8ec1cd6f9cf89ee914b6041d9e0b56e9aa67c3e0'


def close():
    out=BASE/OLD;work=BASE/('source_cohort_work_'+OLD);q=read(out/'protocol.json')
    assert not(out/'no_network_closure.json').exists()and not(out/'run_receipt.json').exists()
    assert not(work/'lease_published').exists()
    p=read(campaign.POLICY);state=read(campaign.CAMPAIGN/'progress.json')
    assert p['collector_lease']['owner']==p['active_collection_scope']==state['active_scope']==OLD
    assert state['next_unit']==q['campaign_unit']==6
    assert q['source_ids']==read(campaign.CAMPAIGN/'selection.json')['units'][5]['source_ids']
    for pin in q['inputs'].values():assert sha((out/pin['file']).resolve())==pin['sha256']
    for name,key in [('plan.json','private_plan_sha256'),('remaining_source_registry.json','private_identity_registry_sha256'),
                     ('historical_locks.json','private_lock_manifest_sha256'),('legacy_funding_plan.json','private_legacy_funding_plan_sha256')]:
        assert sha(work/name)==q[key]
    locks=set(read(work/'historical_locks.json'))|{str(work/'collector.lock')}
    with ExitStack()as stack:
        for name in sorted(locks):
            f=stack.enter_context(Path(name).open('a+'));fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
        metadata=[read(x)for x in work.glob('requests/*/*.json')]
        assert not metadata and not list((work/'results').glob('*.json.gz'))
        assert not list((work/'raw').glob('*.json.gz'))
        pins=read(out/'legacy_reuse_manifest.json')['responses'];plans=read(work/'legacy_funding_plan.json')
        for record in read(work/'plan.json'):
            sid=record['pilot_id'];anchor,_,values,_=legacy_source(record,work,{m['key']:m for m in pins if m['source_id']==sid})
            assert plans[sid]==funding_plan(record,anchor,values)
        assert sha(out/'protocol.json')==p['collector_lease']['protocol_sha256']
        report=dict(status='passed',scope=OLD,kind='administrative_no_network_closure',
            closed_at=datetime.now(timezone.utc).isoformat(),source_ids=q['source_ids'],campaign_unit=6,
            provider_requests=0,http200=0,fresh_request_intents=0,failed_provider_requests=0,
            cached_legacy_responses_verified=len(pins),operational_locks_checked_free=len(locks),
            original_runner_completion='Not recorded; no permit, no request intent, no active operational lock',
            published_preparation_commit=PUBLISHED_PREPARATION,permit_was_installed=False,
            interruption='Automatic approval review could not complete write_stdin because the usage limit was reached; not a safety determination',
            scientific_rows_changed=0,available_coldcard_vectors=1457,preserved_old_vectors=1457,
            new_complete_source_ids=[],original_protocol_sha256=sha(out/'protocol.json'),
            restart_same_scope_allowed=False,required_successor=NEW,model_fits=0,new_scores=0)
        write(out/'no_network_closure.json',report);write(out/'coverage_audit.json',report)
        write(out/'independent_verification.json',report);write(work/'closure_evidence.json',report)
        write(out/'run_receipt.json',dict(status='closed_without_network',receipt_origin='Offline administrative lock/intent verification, not a collector-produced receipt',
            provider_requests=0,http200=0,failures=0,finalized_sources=0,operational_locks_released=True,
            blockstream_provider_requests=0,model_fits=0,new_scores=0))
        write(out/'dispatch_verification.json',verify_dispatch_evidence([]))
        (out/'request_manifest.json.gz').write_bytes(gzip.compress(json_bytes([]),mtime=0))
        (out/'checkpoint.json.gz').write_bytes(gzip.compress(json_bytes(dict(protocol_sha256=sha(out/'protocol.json'),entries={})),mtime=0))
        write(out/'collection_stop.json',dict(status='closed_without_network',operational_locks_released=True,restart_same_scope_allowed=False))
        p['collector_lease'].update(state='idle',owner=None,last_owner=OLD,expires_at=None,
            finished_at=datetime.now(timezone.utc).isoformat(),operational_locks_released=True,stop_status='closed_without_network')
        p.update(active_collection_scope='none',coverage_collection_paused=True,automation_enabled=False,
            latest_status='tool_quota_interruption_closed_without_network',latest_no_network_closure=OLD+'/no_network_closure.json')
        p['provider_access_policies'][campaign.PROVIDER]['status']='preparation_closed_without_network'
        write(campaign.POLICY,p)
        state.setdefault('interrupted_preparations',[]).append(dict(scope=OLD,unit=6,source_ids=q['source_ids'],
            fresh_provider_requests=0,closure_file=OLD+'/no_network_closure.json',required_successor=NEW))
        state.update(status='checkpoint_saved_after_tool_quota',active_scope=None,next_unit=6,can_continue=True)
        write(campaign.CAMPAIGN/'progress.json',state)
    (out/'RESULTS.md').write_text('# Preparation closed without network traffic\n\nUsage-limit approval review interrupted publication/readback of the prepared unit. The preparation commit exists, but no permit was installed and no fresh request intent exists. Every cached response and all locks were verified. No source, feature vector or scientific row changed. The original protocol/authorization remains intact. This scope is closed; continue the same three frozen sources only in the distinct recovery scope after a fresh published lease/readback.\n')
    return report


def prepare():
    old=BASE/OLD;oldwork=BASE/('source_cohort_work_'+OLD)
    proof=read(old/'no_network_closure.json');assert proof['status']=='passed'and proof['provider_requests']==0
    assert read(old/'private_cache_backup.json')['saved_privately']
    campaign.validated_access()
    p=read(campaign.POLICY);state=read(campaign.CAMPAIGN/'progress.json')
    assert p['collector_lease']['state']=='idle'and p['active_collection_scope']=='none'
    assert state['active_scope']is None and state['next_unit']==6 and state['can_continue']
    out=BASE/NEW;work=BASE/('source_cohort_work_'+NEW)
    assert not out.exists()and not work.exists();out.mkdir();work.mkdir(mode=0o700)
    for name in ['legacy','requests','raw','results']:(work/name).mkdir()
    copied=0
    for source in sorted((oldwork/'legacy').rglob('*')):
        if source.is_file():
            target=work/'legacy'/source.relative_to(oldwork/'legacy');target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(source,target);assert sha(source)==sha(target);copied+=1
    for name in ['plan.json','legacy_funding_plan.json','remaining_source_registry.json','retained_bridge_native_cursors.json','parent_native_cursors.json']:
        shutil.copyfile(oldwork/name,work/name)
    for name in ['legacy_reuse_manifest.json','legacy_provider_provenance.json','offline_reuse_manifest.json','retained_deep_queue.json']:
        shutil.copyfile(old/name,out/name)
    locks=set(read(oldwork/'historical_locks.json'))|{str(w/'collector.lock')for w in BASE.glob('source_cohort_work_*')if w!=work}
    for name in locks:Path(name).parent.mkdir(parents=True,exist_ok=True)
    write(work/'historical_locks.json',sorted(locks))
    state.update(status='prepared_unit',active_scope=NEW)
    write(campaign.CAMPAIGN/'progress.json',state);write(out/'prepared_campaign_state.json',state)
    q=deepcopy(read(old/'protocol.json'));q.update(pass_name=NEW,prepared_at=datetime.now(timezone.utc).isoformat(),
        supersedes_no_network_preparation=OLD,authorization='User: poursuit, after quota availability returned. Same frozen unit-6 sources, limits and existing API/GitHub authorization; no old scope restart.')
    for pin in q['inputs'].values():
        source=(old/pin['file']).resolve()
        if source.is_relative_to(oldwork):source=work/source.relative_to(oldwork)
        elif source.is_relative_to(old):source=out/source.relative_to(old)
        pin.update(file=os.path.relpath(source,out),sha256=sha(source))
    for key,path in [('quota_recovery_code',Path(__file__)),('closed_preparation',old/'no_network_closure.json'),
                     ('closed_preparation_protocol',old/'protocol.json'),('closed_preparation_backup',old/'private_cache_backup.json')]:
        q['inputs'][key]=dict(file=os.path.relpath(path,out),sha256=sha(path))
    q['private_lock_manifest_sha256']=sha(work/'historical_locks.json')
    for name,key in [('plan.json','private_plan_sha256'),('remaining_source_registry.json','private_identity_registry_sha256'),
                     ('legacy_funding_plan.json','private_legacy_funding_plan_sha256'),('parent_native_cursors.json','private_parent_native_cursors_sha256'),
                     ('retained_bridge_native_cursors.json','private_retained_bridge_native_cursors_sha256')]:assert sha(work/name)==q[key]
    for pin in q['inputs'].values():assert sha((out/pin['file']).resolve())==pin['sha256']
    write(out/'protocol.json',q)
    write(out/'preparation_verification.json',dict(status='passed',source_ids=q['source_ids'],
        old_source_ids_unchanged=True,private_cached_files_copied_and_verified=copied,
        zero_provider_requests=True,original_consumed_preparation_preserved=True,input_pins_verified=len(q['inputs'])))
    return dict(scope=NEW,source_ids=q['source_ids'],maximum_requests=q['maximum_requests'],provider_requests=0)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['close','prepare'])
    print(__import__('json').dumps(globals()[p.parse_args().command](),indent=2))
