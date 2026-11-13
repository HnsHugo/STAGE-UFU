"""Prepare smaller durable checkpoints of the same frozen fifty-source campaign."""
import argparse
from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path

from prepare_frontier_checkpoint import read, sha, write

BASE = Path(__file__).resolve().parent
CAMPAIGN = BASE / 'mempool_fifty_20261112'


def prepare(kind, parent):
    selection = read(CAMPAIGN / 'recovery_plan_20261113.json')
    initial = read(CAMPAIGN / 'selection.json')
    assert kind == 'bridge'
    ids = ['comparison_0351']; unit = 9; maximum_pages = 50
    parent = parent.resolve(); oldwork = BASE / ('source_cohort_work_' + parent.name)
    assert read(parent / 'independent_verification.json')['status'] == 'passed'
    assert read(parent / 'private_cache_backup.json')['saved_privately']
    progress = read(CAMPAIGN / 'progress.json')
    assert set(ids) <= set(progress['pending_source_ids']) and not set(ids) & set(progress['finalized_source_ids'])
    policy = read(BASE / 'comparison_access_retries_20261030/retry_policy.json')
    assert policy['collector_lease']['state'] == 'idle' and policy['active_collection_scope'] == 'none'
    gate = policy['provider_access_policies']['https://mempool.space/api'].get('next_network_attempt_not_before')
    assert gate is None or datetime.now(timezone.utc) >= datetime.fromisoformat(gate)
    out = BASE / (CAMPAIGN.name + f'_tail_{kind}_20261113'); work = BASE / ('source_cohort_work_' + out.name)
    assert not out.exists() and not work.exists(); out.mkdir(); work.mkdir(mode=0o700)
    for n in ['requests', 'raw', 'results']:
        (work / n).mkdir()
    registry = read(oldwork / 'remaining_source_registry.json'); by_id = {r['pilot_id']: r for r in registry}
    baseline = read(parent / 'precutoff_feature_view.json.gz'); rows = {r['source_id']: r for r in baseline['rows']}
    records = [by_id[s] for s in ids]
    for r in records:
        assert rows[r['pilot_id']]['features'] is None
        for k in ['address_sha256', 'payment_txid_sha256', 'cutoff_height', 'cutoff_block_hash']:
            assert r[k] == rows[r['pilot_id']][k]
        assert hashlib.sha256(r['address'].encode()).hexdigest() == r['address_sha256']
        assert hashlib.sha256(r['payment_txid'].encode()).hexdigest() == r['payment_txid_sha256']
    write(work / 'plan.json', records)
    for name in ['remaining_source_registry.json', 'retained_bridge_native_cursors.json']:
        (work / name).write_bytes((oldwork / name).read_bytes())
    (work / 'parent_native_cursors.json').write_bytes((oldwork / 'native_cursors.json').read_bytes())
    locks = set(read(oldwork / 'historical_locks.json'))
    locks.update(str(p / 'collector.lock') for p in BASE.glob('source_cohort_work_*') if p != work)
    for name in locks:
        Path(name).parent.mkdir(parents=True, exist_ok=True)
    write(work / 'historical_locks.json', sorted(locks))
    reuse = []
    origins = {}
    if kind in ['native_pair','native_five']:
        origin_names = dict(comparison_0390='independent_provider_native_20261112_01', comparison_0391='independent_provider_native_20261112_01', comparison_0433='independent_provider_native_20261112_02', comparison_0471='independent_provider_native_20261112_02', comparison_0476='independent_provider_native_20261112_02', comparison_0508='independent_provider_native_20261112_02', comparison_0522='independent_provider_native_20261112_03')
        for record in records:
            sid = record['pilot_id']; origin = BASE / origin_names[sid]; source = BASE / ('source_cohort_work_' + origin.name)
            old = read(origin / 'checkpoint.json.gz')['entries'][sid]
            assert old['status'] == 'bounded_incomplete' and old['pages_fetched'] == 32 and old['raw_sha256'] == rows[sid]['precutoff_history_provenance']['raw_sha256']
            assert sha(source / old['raw_file']) == old['raw_sha256']
            origins[sid] = origin
            dest = work / 'requests' / sid; dest.mkdir()
            for key in ['reference'] + [f'tail_{i:04d}' for i in range(32)]:
                marker = source / 'requests' / sid / (key + '.json'); body = marker.with_suffix('.json.gz'); meta = read(marker)
                assert meta.get('http_status') == 200 and 'error_type' not in meta and meta['provider'] == 'https://mempool.space/api' and sha(body) == meta['sha256']
                (dest / body.name).write_bytes(body.read_bytes())
                pin = {k: meta[k] for k in ['source_id','key','sha256','endpoint_sha256']}; pin.update(provider=meta['provider'], origin_scope=origin.name, original_marker_sha256=sha(marker)); reuse.append(pin)
                write(dest / marker.name, dict(meta, offline_reused=True, reused_from_pass=origin.name, original_marker_sha256=sha(marker)))
            from independent_mempool_resume import cached_prefix
            cached_prefix(record, work, [r for r in reuse if r['source_id'] == sid])
    write(out / 'offline_reuse_manifest.json', dict(schema_version=1, responses=reuse, native_cached_bodies_reused=len(reuse), previous_blockstream_prefix_not_spliced=True))
    inputs = {}
    for key, pin in read(parent / 'protocol.json')['inputs'].items():
        p = (parent / pin['file']).resolve(); assert sha(p) == pin['sha256']; inputs['ancestor_'+key] = p
    for name in ['protocol.json', 'precutoff_feature_view.json.gz', 'checkpoint.json.gz', 'request_manifest.json.gz',
                 'resume_checkpoint.json', 'coverage_audit.json', 'independent_verification.json',
                 'private_cache_backup.json', 'run_receipt.json', 'retained_deep_queue.json']:
        inputs['baseline_view' if name == 'precutoff_feature_view.json.gz' else 'parent_'+name.replace('.', '_')] = parent / name
    inputs.update(campaign_selection=CAMPAIGN / 'selection.json', campaign_recovery_plan=CAMPAIGN / 'recovery_plan_20261113.json', preparer=Path(__file__).resolve(),
                  offline_reuse_manifest=out / 'offline_reuse_manifest.json')
    for sid, origin in origins.items():
        for name in ['protocol.json','checkpoint.json.gz','request_manifest.json.gz','independent_verification.json','private_cache_backup.json']:
            inputs['seed_' + sid + '_' + name.replace('.','_')] = origin / name
    origin = BASE / 'independent_provider_bridge_20261112'
    source = BASE / ('source_cohort_work_' + origin.name)
    raw_file = source / 'raw/comparison_0351.json.gz'
    old = read(origin / 'checkpoint.json.gz')['entries']['comparison_0351']
    assert old['raw_sha256'] == sha(raw_file) == rows['comparison_0351']['precutoff_history_provenance']['raw_sha256']
    cursor = read(source / 'native_cursors.json')['comparison_0351']['last_native_cursor']
    proof = BASE / 'independent_provider_native_20261112_03/resume_checkpoint.json'
    retained = next(r for r in read(proof)['retained_native_partial_queue'] if r['source_id'] == 'comparison_0351')
    assert hashlib.sha256(cursor.encode()).hexdigest() == retained['last_native_cursor_sha256']
    (work / 'bridge-seed-raw.json.gz').write_bytes(raw_file.read_bytes())
    write(work / 'bridge_seed.json', dict(raw_file='bridge-seed-raw.json.gz', raw_sha256=sha(raw_file), native_cursor=cursor))
    for name in ['protocol.json','checkpoint.json.gz','independent_verification.json','private_cache_backup.json']:
        inputs['bridge_origin_' + name.replace('.','_')] = origin / name
    inputs['bridge_cursor_proof'] = proof
    for name in ['resume_fifty_bridge.py','audit_fifty_bridge.py','test_fifty_bridge.py']:
        inputs['bridge_' + name.replace('.','_')] = BASE / name
    budget = dict(before_statuses_at_most=1, fresh_native_pages_at_most=16, after_statuses_at_most=1,
                  funding_statuses_at_most=sum(r['registry_input_slots'] for r in records))
    maximum = sum(budget.values()); budget['total_new_requests_at_most'] = maximum
    q = dict(schema_version=4, pass_name=out.name, created_on='2026-11-13',
        authorization=selection['authorization'], campaign=CAMPAIGN.name, campaign_segment=unit,
        provider='https://mempool.space/api', source_ids=ids,
        baseline_vectors=sum(r['features'] is not None for r in baseline['rows']),
        unit=selection['unit'], target=selection['target'], predictors=selection['predictors'],
        max_pages_per_address=maximum_pages, maximum_requests=maximum, request_budget=budget,
        requests_per_second=.2, minimum_dispatch_interval_seconds=5, workers=1, timeout_seconds=45,
        offline_successful_responses_reused=len(reuse), offline_native_pages_reused=(32*len(ids) if reuse else 0),
        stop_policy='First failure/refusal/inconsistency; no in-scope retry, consumed-scope restart or provider/account/IP/proxy/TLS change. Audit/save before expansion.',
        transport='Same Mempool provider, inherited proxy, verified TLS, no redirects; declared 45-second timeout',
        blockstream_cooldown_preserved_until=policy['provider_access_policies']['https://blockstream.info/api']['next_network_attempt_not_before'],
        live_policy_file='../comparison_access_retries_20261030/retry_policy.json',
        private_plan_sha256=sha(work / 'plan.json'), private_lock_manifest_sha256=sha(work / 'historical_locks.json'),
        private_identity_registry_sha256=sha(work / 'remaining_source_registry.json'),
        private_retained_bridge_native_cursors_sha256=sha(work / 'retained_bridge_native_cursors.json'),
        private_parent_native_cursors_sha256=sha(work / 'parent_native_cursors.json'),
        full_current_history_status_promotion=False, model_fits=0, new_scores=0,
        inputs={k: dict(file=os.path.relpath(p, out), sha256=sha(p)) for k, p in sorted(inputs.items())})
    q.update(private_bridge_seed_sha256=sha(work / 'bridge_seed.json'), native_start_cursor_sha256=hashlib.sha256(cursor.encode()).hexdigest(), maximum_new_native_pages=16, focused_tests_previously_passed=33)
    write(out / 'protocol.json', q)
    (out / 'retained_deep_queue.json').write_bytes((parent / 'retained_deep_queue.json').read_bytes())
    write(out / 'preparation_verification.json', dict(status='passed', selected=len(ids),
        frozen_identities_verified=len(ids), input_pins_verified=len(inputs), baseline_vectors=q['baseline_vectors'],
        campaign_requested_sources=50, provider_requests=0, tests_previously_passed=29))
    (out / 'README.md').write_text(f'''# Fifty-source campaign: unit {unit}

This bounded final-frontier native-Mempool unit is part of the explicitly requested
[fifty-source campaign](../{CAMPAIGN.name}/README.md). The source/reference pairs
and cohort are frozen. Fresh sources use thirty-two pages; pure saved native histories reuse all thirty-two old pages and add at most sixteen more. Keep one worker,
five-second spacing and the verified forty-five-second response timeout.

Empty terminal page, fresh reference anchors and original UTXO funding closure
are mandatory for a complete fourteen-variable prefix. Retain null features for
bounded histories. The operational incident-membership target and unknown theft/
hardware-wallet labels stay unchanged. No fit, score, split or threshold change.

Require fresh historical/local locks, the live provider gate and an exact published
lease/readback. Stop at first failure/refusal/inconsistency; never revive consumed
operational flags or automatically rotate provider/account/IP/proxy/TLS. The closed
Blockstream gate is unchanged. Audit, save and publish before the next unit.
''')
    (out / 'README.md').write_text('''# Actual native frontier extension of the retained bridge

Select only comparison_0351 from the frozen fifty-source campaign. Reuse the
verified 844-transaction mixed-provider raw seed and its actual saved Mempool
cursor. Never use the sorted union as a cursor. The legacy boundary must stay
strictly above the native frontier. Add at most sixteen new native pages, with
fresh before/after reference anchors and funding closure before completeness.

Keep one worker, five-second spacing, a forty-five-second response timeout,
fresh locks and exact published lease/readback. Stop at first failure/refusal
or inconsistency. Saved legacy and native evidence page counts stay distinct.
Preserve all old vectors, labels, cutoffs and queues. No fit, score, paid service,
provider/account/IP/proxy/TLS rotation, in-scope retry or automatic schedule.
Audit and save this bounded scope before any successor.
''')
    return dict(scope=out.name, source_ids=ids, maximum_requests=maximum, input_pins=len(inputs))


if __name__ == '__main__':
    import json
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('unit', choices=['bridge']); p.add_argument('parent', type=Path)
    a = p.parse_args(); print(json.dumps(prepare(a.unit, a.parent), sort_keys=True))
