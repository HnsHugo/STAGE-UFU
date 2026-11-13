"""Prepare smaller durable checkpoints of the same frozen fifty-source campaign."""
import argparse
from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path

from prepare_frontier_checkpoint import read, sha, write

BASE = Path(__file__).resolve().parent
CAMPAIGN = BASE / 'mempool_fifty_20261112'


def prepare(unit, parent):
    selection = read(CAMPAIGN / 'recovery_plan_20261113.json')
    assert 1 <= unit <= 8, 'Saved-frontier segments use their separate seed preparer'
    chosen = selection['segments'][unit-1]; ids = chosen['source_ids']
    assert len(ids) == 5 and chosen['kind'] == 'fresh_native'
    parent = parent.resolve(); oldwork = BASE / ('source_cohort_work_' + parent.name)
    assert read(parent / 'independent_verification.json')['status'] == 'passed'
    assert read(parent / 'private_cache_backup.json')['saved_privately']
    progress = read(CAMPAIGN / 'progress.json')
    assert set(ids) <= set(progress['pending_source_ids']) and not set(ids) & set(progress['finalized_source_ids'])
    policy = read(BASE / 'comparison_access_retries_20261030/retry_policy.json')
    assert policy['collector_lease']['state'] == 'idle' and policy['active_collection_scope'] == 'none'
    gate = policy['provider_access_policies']['https://mempool.space/api'].get('next_network_attempt_not_before')
    assert gate is None or datetime.now(timezone.utc) >= datetime.fromisoformat(gate)
    out = BASE / (CAMPAIGN.name + f'_segment_20261113_{unit:02d}'); work = BASE / ('source_cohort_work_' + out.name)
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
    write(out / 'offline_reuse_manifest.json', dict(schema_version=1, responses=[], native_cached_bodies_reused=0,
        previous_blockstream_prefix_not_spliced=True))
    inputs = {}
    for key, pin in read(parent / 'protocol.json')['inputs'].items():
        p = (parent / pin['file']).resolve(); assert sha(p) == pin['sha256']; inputs['ancestor_'+key] = p
    for name in ['protocol.json', 'precutoff_feature_view.json.gz', 'checkpoint.json.gz', 'request_manifest.json.gz',
                 'resume_checkpoint.json', 'coverage_audit.json', 'independent_verification.json',
                 'private_cache_backup.json', 'run_receipt.json', 'retained_deep_queue.json']:
        inputs['baseline_view' if name == 'precutoff_feature_view.json.gz' else 'parent_'+name.replace('.', '_')] = parent / name
    inputs.update(campaign_selection=CAMPAIGN / 'selection.json', campaign_recovery_plan=CAMPAIGN / 'recovery_plan_20261113.json', preparer=Path(__file__).resolve(),
                  offline_reuse_manifest=out / 'offline_reuse_manifest.json')
    budget = dict(full_references_at_most=5, tail_pages_at_most=5*32, after_anchor_statuses_at_most=5,
                  funding_statuses_at_most=sum(r['registry_input_slots'] for r in records))
    maximum = sum(budget.values()); budget['total_new_requests_at_most'] = maximum
    q = dict(schema_version=4, pass_name=out.name, created_on='2026-11-13',
        authorization=selection['authorization'], campaign=CAMPAIGN.name, campaign_segment=unit,
        provider='https://mempool.space/api', source_ids=ids,
        baseline_vectors=sum(r['features'] is not None for r in baseline['rows']),
        unit=selection['unit'], target=selection['target'], predictors=selection['predictors'],
        max_pages_per_address=32, maximum_requests=maximum, request_budget=budget,
        requests_per_second=.2, minimum_dispatch_interval_seconds=5, workers=1, timeout_seconds=45,
        offline_successful_responses_reused=0, offline_native_pages_reused=0,
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
    write(out / 'protocol.json', q)
    (out / 'retained_deep_queue.json').write_bytes((parent / 'retained_deep_queue.json').read_bytes())
    write(out / 'preparation_verification.json', dict(status='passed', selected=5,
        frozen_identities_verified=5, input_pins_verified=len(inputs), baseline_vectors=q['baseline_vectors'],
        campaign_requested_sources=50, provider_requests=0, tests_previously_passed=29))
    (out / 'README.md').write_text(f'''# Fifty-source campaign: unit {unit}

This bounded five-source native-Mempool unit is part of the explicitly requested
[fifty-source campaign](../{CAMPAIGN.name}/README.md). The source/reference pairs
and cohort are frozen. Use at most thirty-two native pages per source, one worker,
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
    return dict(scope=out.name, source_ids=ids, maximum_requests=maximum, input_pins=len(inputs))


if __name__ == '__main__':
    import json
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('unit', type=int); p.add_argument('parent', type=Path)
    a = p.parse_args(); print(json.dumps(prepare(a.unit, a.parent), sort_keys=True))
