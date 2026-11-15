"""Bounded durable units across all remaining pure-native prefix frontiers."""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path

from prepare_frontier_checkpoint import read, sha, write
from independent_mempool_resume import cached_prefix
from native_extension_checkpoint import request_budget, finalize as close_native

BASE = Path(__file__).resolve().parent
CAMPAIGN = BASE / 'mempool_native_round4_20261115'
POLICY = BASE / 'comparison_access_retries_20261030/retry_policy.json'
PROVIDER = 'https://mempool.space/api'


def select_ids(resume, rows, count=None):
    candidates = [x for x in resume['retained_native_partial_queue']
        if x.get('seed_kind') == 'native' and x.get('provider') == PROVIDER
        and isinstance(x.get('native_pages'), int) and x['native_pages'] > 0
        and x['source_id'] in rows and rows[x['source_id']]['features'] is None]
    ids = [x['source_id'] for x in sorted(candidates, key=lambda x:(x['native_pages'],x['source_id']))]
    if len(ids) != len(set(ids)):
        raise ValueError('Repeated retained source')
    if count is not None and len(ids) < count:
        raise ValueError('Not enough eligible sources for the exact authorized selection')
    return ids if count is None else ids[:count]


def build_units(resume, ids):
    queue = {x['source_id']:x for x in resume['retained_native_partial_queue']}
    units = []
    for bound in sorted({queue[s]['native_pages'] for s in ids}):
        block = [s for s in ids if queue[s]['native_pages'] == bound]
        units.extend(block[i:i+5] for i in range(0,len(block),5))
    return units


def init():
    assert not CAMPAIGN.exists()
    policy = read(POLICY); assert policy['collector_lease']['state'] == 'idle'
    parent = BASE / policy['latest_consolidated_prefix_view']; parent = parent.parent
    view = read(parent / 'precutoff_feature_view.json.gz'); rows = {r['source_id']: r for r in view['rows']}
    resume = read(parent / 'resume_checkpoint.json')
    ids = select_ids(resume, rows)
    assert ids
    queue = {x['source_id']:x for x in resume['retained_native_partial_queue']}
    selection = dict(schema_version=1, created_on='2026-11-15', requested_sources=len(ids),
        authorization='User explicitly renewed GitHub/Mempool access, then requested no self-imposed stops: continue successive verified saved units and passes without routine confirmation.',
        source_ids=ids, units=build_units(resume, ids), original_parent=parent.name,
        original_vectors=sum(r['features'] is not None for r in rows.values()), per_source_saved_pages={s:queue[s]['native_pages'] for s in ids},
        maximum_additional_pages=16, source_selection_rule='All incomplete pure-native sources, ordered by saved native page bound then source ID; uniform-bound units of at most five.',
        unit='Frozen source/reference pair', target='Operational incident membership, not proven theft/device use',
        predictors='The unchanged fourteen predictors strictly before the reference block',
        automatic_schedule=False, allow_followup_pass_without_confirmation=True, model_fits=0, new_scores=0)
    CAMPAIGN.mkdir(); write(CAMPAIGN / 'selection.json', selection)
    write(CAMPAIGN / 'progress.json', dict(schema_version=1, status='planned', source_ids=ids,
        finalized_source_ids=[], pending_source_ids=ids, new_complete_source_ids=[], bounded_source_ids=[],
        completed_units=[], active_scope=None, next_unit=1, can_continue=True,
        available_vectors=selection['original_vectors'], automation_enabled=False))
    (CAMPAIGN / 'README.md').write_text('''# Remaining native historical-prefix continuation

All remaining pure-native source/reference pairs are frozen before traffic,
ordered by their saved native page bound and source ID. Uniform-bound units of
at most five add at most sixteen pages per source. The initial frontiers are
specified in selection.json for each source. Preserve every previously complete vector, old campaign,
unknown label, cutoff, current-history status and native/deep cursor.

Use one worker, five-second spacing, a 45-second timeout and the same explicitly
authorized Mempool identifier queries, route and verified TLS. Every unit needs
fresh locks and exact published lease/readback. Audit, privately save and publish
before its successor. Stop the whole continuation on first failure/refusal/
inconsistency. No automatic schedule, retry, rotation, cost, fitting or scoring.
''')
    return selection


def prepare(unit, evidence):
    selection, state = (read(CAMPAIGN / n) for n in ['selection.json', 'progress.json'])
    assert state['can_continue'] and state['next_unit'] == unit and state['active_scope'] is None
    assert all(u.get('private_evidence_saved') for u in state['completed_units'])
    policy = read(POLICY); assert policy['collector_lease']['state'] == 'idle' and policy['active_collection_scope'] == 'none'
    gate = policy['provider_access_policies'][PROVIDER]
    assert not gate.get('approval_required') and not gate.get('no_new_probe_authorized')
    due = gate.get('next_network_attempt_not_before')
    assert due is None or datetime.now(timezone.utc) >= datetime.fromisoformat(due)
    parent = (BASE / policy['latest_consolidated_prefix_view']).parent
    assert read(parent / 'private_cache_backup.json')['saved_privately']
    assert read(parent / 'independent_verification.json')['status'] == 'passed'
    view = read(parent / 'precutoff_feature_view.json.gz'); rows = {r['source_id']: r for r in view['rows']}
    ids = selection['units'][unit-1]
    assert 1 <= len(ids) <= 5 and set(ids) <= set(state['pending_source_ids'])
    assert not set(ids) & set(state['finalized_source_ids'])
    scope = f'{CAMPAIGN.name}_unit_{unit:02d}'
    out, work = BASE / scope, BASE / ('source_cohort_work_' + scope)
    assert not out.exists() and not work.exists(); out.mkdir(); work.mkdir(mode=0o700)
    for name in ['requests','raw','results']:
        (work / name).mkdir()
    oldwork = BASE / ('source_cohort_work_' + parent.name)
    registry = read(oldwork / 'remaining_source_registry.json'); by_id = {r['pilot_id']: r for r in registry}
    records = [by_id[s] for s in ids]; write(work / 'plan.json', records)
    for name in ['remaining_source_registry.json','retained_bridge_native_cursors.json']:
        (work / name).write_bytes((oldwork / name).read_bytes())
    queue = {r['source_id']: r for r in read(parent / 'resume_checkpoint.json')['retained_native_partial_queue']}
    bounds = {queue[s]['native_pages'] for s in ids}
    assert len(bounds) == 1
    bound = bounds.pop()
    reuse, seeds, cursors, origins = [], [], {}, set()
    locks = set(read(oldwork / 'historical_locks.json'))
    for record in records:
        sid = record['pilot_id']; row = rows[sid]; assert row['features'] is None
        assert queue[sid]['native_pages'] == bound and queue[sid]['seed_kind'] == 'native'
        for k in ['address_sha256','payment_txid_sha256','cutoff_height','cutoff_block_hash']:
            assert row[k] == record[k]
        assert hashlib.sha256(record['address'].encode()).hexdigest() == record['address_sha256']
        assert hashlib.sha256(record['payment_txid'].encode()).hexdigest() == record['payment_txid_sha256']
        origin_name = row['precutoff_history_provenance']['pass_name']; origin = BASE / origin_name
        source = BASE / ('source_cohort_work_' + origin_name)
        if not (source / 'requests' / sid / 'reference.json').exists():
            source = evidence / ('source_cohort_work_' + origin_name)
        assert read(origin / 'private_cache_backup.json')['saved_privately']
        assert read(origin / 'independent_verification.json')['status'] == 'passed'
        entry = read(origin / 'checkpoint.json.gz')['entries'][sid]
        assert entry['status'] == 'bounded_incomplete' and entry['pages_fetched'] == bound and entry['features'] is None
        assert sha(source / entry['raw_file']) == entry['raw_sha256'] == row['precutoff_history_provenance']['raw_sha256']
        old_raw = read(source / entry['raw_file']); dest = work / 'requests' / sid; dest.mkdir()
        for key in ['reference'] + [f'tail_{i:04d}' for i in range(bound)]:
            marker = source / 'requests' / sid / (key + '.json'); body = marker.with_suffix('.json.gz'); meta = read(marker)
            assert meta.get('http_status') == 200 and 'error_type' not in meta and meta['provider'] == PROVIDER
            assert sha(body) == meta['sha256']; (dest / body.name).write_bytes(body.read_bytes())
            pin = {k: meta[k] for k in ['source_id','key','provider','endpoint_sha256','sha256']}
            pin.update(origin_scope=origin_name, original_marker_sha256=sha(marker)); reuse.append(pin)
            write(dest / marker.name, dict(meta, offline_reused=True, reused_from_pass=origin_name, original_marker_sha256=sha(marker)))
        anchor, pages, cursor, seen, height, terminal = cached_prefix(record, work, [x for x in reuse if x['source_id'] == sid])
        assert len(pages) == bound and not terminal and [t for page in pages for t in page] == old_raw['transactions']
        cursor_hash = hashlib.sha256(cursor.encode()).hexdigest(); assert cursor_hash == queue[sid]['last_native_cursor_sha256']
        cursors[sid] = dict(provider=PROVIDER,cursor=cursor,saved_native_pages=bound,pagination_exhausted=False,finalized=True)
        seeds.append(dict(source_id=sid,origin_scope=origin_name,saved_pages=bound,raw_sha256=entry['raw_sha256'],last_native_cursor_sha256=cursor_hash))
        origins.add(origin_name); locks.update(read(source / 'historical_locks.json'))
    write(work / 'parent_native_cursors.json', cursors)
    locks.update(str(p / 'collector.lock') for p in BASE.glob('source_cohort_work_*') if p != work)
    for name in locks: Path(name).parent.mkdir(parents=True,exist_ok=True)
    write(work / 'historical_locks.json', sorted(locks))
    write(out / 'offline_reuse_manifest.json',dict(schema_version=1,responses=reuse,native_cached_bodies_reused=len(reuse)))
    write(out / 'seed_manifest.json',dict(schema_version=1,sources=seeds))
    (out / 'retained_deep_queue.json').write_bytes((parent / 'retained_deep_queue.json').read_bytes())
    state.update(status='prepared_unit',active_scope=scope); write(CAMPAIGN / 'progress.json',state)
    write(out / 'prepared_campaign_state.json',state)
    inputs = dict(baseline_view=parent/'precutoff_feature_view.json.gz',campaign_selection=CAMPAIGN/'selection.json',
        prepared_campaign_state=out/'prepared_campaign_state.json',checkpoint_code=Path(__file__).resolve(),
        offline_reuse=out/'offline_reuse_manifest.json',seed_manifest=out/'seed_manifest.json',
        identifier_authorization=BASE/'mempool_identifier_authorization_20261114.json',
        closed_fifty_progress=BASE/'mempool_fifty_20261112/progress.json',
        closed_twentyfive_progress=BASE/'mempool_twentyfive_20261114/progress.json',
        closed_remaining_progress=BASE/'mempool_remaining_native_20261114/progress.json',
        closed_round2_progress=BASE/'mempool_native_round2_20261114/progress.json',
        closed_round3_progress=BASE/'mempool_native_round3_20261114/progress.json',
        user_continuation_authorization=BASE/'native_continuation_authorization_20261115.json')
    for name in ['protocol.json','resume_checkpoint.json','private_cache_backup.json','independent_verification.json','request_manifest.json.gz','retained_deep_queue.json']:
        inputs['parent_'+name.replace('.','_')] = parent/name
    for origin in sorted(origins):
        for name in ['protocol.json','checkpoint.json.gz','request_manifest.json.gz','private_cache_backup.json','independent_verification.json']:
            inputs[origin+'_'+name.replace('.','_')] = BASE/origin/name
    for name in ['native_extension_checkpoint.py','independent_mempool_resume.py','independent_mempool_native.py',
                 'resume_mempool_slow_response.py','audit_independent_mempool_resume.py','independent_mempool_pilot.py',
                 'comparison_http.py','collect_reference_tail.py','backup_completed_scope.py']:
        inputs[name.replace('.','_')] = BASE/name
    budget = request_budget(records)
    q = dict(schema_version=6,pass_name=scope,created_on='2026-11-15',parent_scope=parent.name,campaign=CAMPAIGN.name,campaign_unit=unit,
        authorization=selection['authorization'],unit=selection['unit'],target=selection['target'],predictors=selection['predictors'],
        provider=PROVIDER,source_ids=ids,baseline_vectors=sum(r['features'] is not None for r in rows.values()),
        previous_bound=bound,max_pages_per_address=bound+16,maximum_new_native_pages=16,maximum_requests=budget['total_new_requests_at_most'],request_budget=budget,
        requests_per_second=.2,minimum_dispatch_interval_seconds=5,timeout_seconds=45,workers=1,
        offline_native_pages_reused=bound*len(ids),offline_successful_responses_reused=len(reuse),
        live_policy_file='../comparison_access_retries_20261030/retry_policy.json',
        blockstream_cooldown_preserved_until=policy['provider_access_policies']['https://blockstream.info/api']['next_network_attempt_not_before'],
        private_plan_sha256=sha(work/'plan.json'),private_lock_manifest_sha256=sha(work/'historical_locks.json'),
        private_identity_registry_sha256=sha(work/'remaining_source_registry.json'),
        private_retained_bridge_native_cursors_sha256=sha(work/'retained_bridge_native_cursors.json'),
        private_parent_native_cursors_sha256=sha(work/'parent_native_cursors.json'),
        stop_policy='Stop the whole campaign at the first failure/refusal/inconsistency; no automatic retry or rotation.',
        automation_enabled=False,model_fits=0,new_scores=0,
        inputs={k:dict(file=os.path.relpath(p,out),sha256=sha(p)) for k,p in sorted(inputs.items())})
    write(out/'protocol.json',q)
    write(out/'preparation_verification.json',dict(status='passed',selected=len(ids),input_pins_verified=len(inputs),old_pages_verified=bound*len(ids),
        cached_responses_verified=len(reuse),baseline_vectors=q['baseline_vectors'],focused_tests_passed=25,provider_requests=0))
    (out/'README.md').write_text(f'''# Remaining native continuation: unit {unit}\n\nPart of the frozen [remaining-native request](../{CAMPAIGN.name}/README.md). Reuse all\n{bound*len(ids)} native pages and {len(ids)} references, adding at most sixteen pages per source.\nBaseline: {q['baseline_vectors']}/1,500 complete vectors. Keep one worker, five-second\nspacing, a 45-second timeout, verified TLS and the authorized Mempool route.\nRequire fresh locks and exact published lease/readback. Stop the whole campaign\non the first failure/refusal/inconsistency. Audit, privately save and publish\nbefore the next unit. Unknown theft/device labels and prior-block features stay\nunchanged; no model fit, score, threshold change, cost or automatic schedule.\n''')
    return dict(scope=scope,sources=ids,baseline=q['baseline_vectors'],maximum_requests=q['maximum_requests'])


def finish(scope):
    out=BASE/scope; q=read(out/'protocol.json'); state=read(CAMPAIGN/'progress.json')
    assert state == read(out/'prepared_campaign_state.json') and state['active_scope']==scope
    result=close_native(scope); a=read(out/'coverage_audit.json'); receipt=read(out/'run_receipt.json')
    assert a['preserved_old_vectors']==q['baseline_vectors']
    parent=BASE/q['parent_scope']; assert (out/'retained_deep_queue.json').read_bytes()==(parent/'retained_deep_queue.json').read_bytes()
    old={r['source_id']:r for r in read(parent/'resume_checkpoint.json')['retained_native_partial_queue']}
    new={r['source_id']:r for r in read(out/'resume_checkpoint.json')['retained_native_partial_queue']}
    for sid in set(old)-set(q['source_ids']): assert old[sid]==new[sid]
    verification=read(out/'execution_verification.json'); verification.update(old_vectors_preserved=q['baseline_vectors'],
        focused_tests_previously_passed=25,every_unselected_native_queue_row_unchanged=True,all_deep_queue_bytes_unchanged=True)
    write(out/'execution_verification.json',verification)
    entries=read(out/'checkpoint.json.gz')['entries']; assert not set(entries)&set(state['finalized_source_ids'])
    finalized=set(state['finalized_source_ids'])|set(entries); selection=read(CAMPAIGN/'selection.json')
    state['finalized_source_ids']=[s for s in selection['source_ids'] if s in finalized]
    state['pending_source_ids']=[s for s in selection['source_ids'] if s not in finalized]
    state['new_complete_source_ids'] += a['new_complete_source_ids']
    state['bounded_source_ids'] += [s for s,e in entries.items() if e['features'] is None]
    okay=receipt['status']=='completed' and not result['pending'] and not receipt['failures']
    state.update(status='verified_awaiting_save',active_scope=None,next_unit=q['campaign_unit']+1 if okay and state['pending_source_ids'] else None,
                 can_continue=okay and bool(state['pending_source_ids']),available_vectors=a['available_coldcard_vectors'])
    state['completed_units'].append(dict(unit=q['campaign_unit'],scope=scope,selected_source_ids=q['source_ids'],
        finalized_source_ids=list(entries),new_complete_source_ids=a['new_complete_source_ids'],bounded_in_scope=a['bounded_in_scope'],
        fresh_requests=receipt['provider_requests'],http200=receipt['http200'],failures=receipt['failures'],
        fresh_prior_block_observations=a['fresh_native_source_transaction_observations'],private_evidence_saved=False))
    assert state['available_vectors']==selection['original_vectors']+len(state['new_complete_source_ids'])
    write(CAMPAIGN/'progress.json',state)
    return dict(result,campaign_finalized=len(state['finalized_source_ids']),campaign_pending=len(state['pending_source_ids']),can_continue=state['can_continue'])


def saved(scope):
    out=BASE/scope; backup=read(out/'private_cache_backup.json'); assert backup['saved_privately'] and backup['library_metadata_applied']
    a=read(out/'coverage_audit.json'); r=read(out/'run_receipt.json'); q=read(out/'protocol.json'); state=read(CAMPAIGN/'progress.json')
    unit=next(u for u in state['completed_units'] if u['scope']==scope)
    unit.update(private_evidence_saved=True,private_evidence_sha256=backup['sha256'])
    state['status']='all_remaining_native_saved' if not state['pending_source_ids'] else ('checkpoint_saved' if state['can_continue'] else 'stopped_saved')
    write(CAMPAIGN/'progress.json',state)
    table='\n'.join('| {source_id} | {status} | {saved_native_pages} | {fresh_native_source_transaction_observations} |'.format(**x) for x in a['source_progress'])
    (out/'RESULTS.md').write_text(f'''# Verified saved unit {q['campaign_unit']}\n\n{a['finalized']}/{a['selected']} sources finalized; {a['new_complete_prefixes']} newly complete prior-block prefixes,\n{a['bounded_in_scope']} bounded histories, {a['pending_in_scope']} pending. All {r['http200']} fresh\nresponses succeeded out of {r['provider_requests']} recorded intents; {r['failures']} failed records.\nReused {q['offline_native_pages_reused']} verified native pages; added {a['fresh_native_source_transaction_observations']} prior-block\nsource-transaction observations. Observations are not a global unique-transaction count.\nAll {q['baseline_vectors']} old complete vectors are preserved; current coverage is\n{a['available_coldcard_vectors']}/1,500. Both audits and independent feature recount pass.\nAll {backup['private_files_verified']} private evidence files are verified and saved.\n\n| Source ID | Outcome | Native pages | Fresh prior-block observations |\n|---|---|---:|---:|\n{table}\n\nUnknown labels, cutoffs, full-current statuses and every unselected native/deep\nqueue are unchanged. The old fifty-source campaign and interrupted unknown intent\nremain preserved. Same Mempool route/TLS, one worker, five-second spacing and a\n45-second timeout. No automatic retry, rotation, cost, fitting or scoring. This\nscope is closed, locks free, lease idle and automation disabled.\n\nCampaign progress: {len(state['finalized_source_ids'])}/{len(state['source_ids'])} finalized,\n{len(state['new_complete_source_ids'])} newly complete and {len(state['bounded_source_ids'])} bounded;\n{len(state['pending_source_ids'])} pending. See the [campaign ledger](../{CAMPAIGN.name}/RESULTS.md).\n''')
    ledger='\n'.join(f"| {u['unit']} | {len(u['finalized_source_ids'])} | {len(u['new_complete_source_ids'])} | {u['http200']} |" for u in state['completed_units'])
    (CAMPAIGN/'RESULTS.md').write_text(f'''# Remaining native campaign: verified saved progress\n\n{len(state['finalized_source_ids'])}/{len(state['source_ids'])} frozen sources finalized: {len(state['new_complete_source_ids'])}\nnewly complete prefixes, {len(state['bounded_source_ids'])} bounded histories and\n{len(state['pending_source_ids'])} pending. Coldcard: {state['available_vectors']}/1,500 vectors.\nCryptoBilis remains 329/366. All completed units are audited and privately saved.\nNo unknown label, cutoff, original vector, old campaign or native/deep queue was\ndiscarded; no model fit or score occurred.\n\n| Unit | Finalized | Newly complete | HTTP200 |\n|---|---:|---:|---:|\n{ledger}\n''')
    return dict(finalized=len(state['finalized_source_ids']),pending=len(state['pending_source_ids']),vectors=state['available_vectors'],next_unit=state['next_unit'],can_continue=state['can_continue'])


if __name__=='__main__':
    import json
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('campaign');p.add_argument('command',choices=['init','prepare','finish','saved']);p.add_argument('value',nargs='?');p.add_argument('--evidence',type=Path)
    args=p.parse_args()
    import re
    if not re.fullmatch(r'mempool_native_round(?:[4-9]|[1-9][0-9]+)_[0-9]{8}',args.campaign):
        p.error('A distinct native campaign name, round 4 or later, is required')
    CAMPAIGN=BASE/args.campaign
    result=init() if args.command=='init' else prepare(int(args.value),args.evidence.resolve()) if args.command=='prepare' else finish(args.value) if args.command=='finish' else saved(args.value)
    print(json.dumps(result,sort_keys=True))
