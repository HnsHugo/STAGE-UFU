"""Prepare the fresh-history units of the explicitly requested fifty-source campaign."""
import argparse
from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path

from prepare_frontier_checkpoint import read, sha, write

BASE = Path(__file__).resolve().parent
CAMPAIGN = BASE / 'mempool_fifty_20261112'


def initialize():
    if CAMPAIGN.exists():
        return read(CAMPAIGN / 'selection.json')
    parent = BASE / 'independent_provider_native_20261112_03'
    resume = read(parent / 'resume_checkpoint.json')
    rows = {r['source_id']: r for r in read(parent / 'precutoff_feature_view.json.gz')['rows']}
    fresh = resume['coldcard_unextended_at_16_page_bound_source_ids']
    retained = [r['source_id'] for r in resume['retained_native_partial_queue']]
    ids = fresh + retained
    assert len(fresh) == 42 and len(retained) == 8 and len(ids) == len(set(ids)) == 50
    assert all(rows[s]['features'] is None for s in ids)
    CAMPAIGN.mkdir()
    selection = dict(schema_version=1, campaign=CAMPAIGN.name, requested_sources=50,
        authorization='Current explicit user instruction: Go la suite fait 50. This supersedes the older at-most-twenty scheduling suggestion; acquisition remains divided into bounded audited/saved units.',
        baseline_view_sha256=sha(parent / 'precutoff_feature_view.json.gz'), baseline_vectors=1413,
        source_ids=ids, fresh_native_source_ids=fresh, retained_native_source_ids=retained,
        units=[dict(unit=1, source_ids=fresh[:20], kind='fresh_native', max_pages_per_source=32),
               dict(unit=2, source_ids=fresh[20:40], kind='fresh_native', max_pages_per_source=32),
               dict(unit=3, source_ids=fresh[40:]+retained, kind='two_fresh_and_eight_saved_native_extensions',
                    fresh_page_bound=32, maximum_additional_native_pages_per_retained_source=16)],
        other_coldcard_missing_sources_retained=37, cryptobilis_vectors_unchanged=329,
        unit='Frozen source/reference pair', target='Operational incident membership, not proven theft/device use',
        predictors='Original fourteen predictors strictly before the reference block',
        model_fits=0, new_scores=0, preserve_unknown_labels=True,
        automatic_provider_rotation=False, automatic_schedule=False)
    write(CAMPAIGN / 'selection.json', selection)
    write(CAMPAIGN / 'progress.json', dict(status='prepared', requested_sources=50,
        finalized_source_ids=[], pending_source_ids=ids, completed_units=[], active_scope=None,
        available_coldcard_vectors=1413, automation_enabled=False))
    (CAMPAIGN / 'README.md').write_text('''# Fifty-source native-Mempool coverage campaign

The user explicitly requests fifty addresses. The frozen selection comprises
forty-two previously unextended 16-page-bound identities and eight retained
native partial histories. This changes scheduling size, not the scientific
cohort, labels, fourteen variables or frozen reference cutoff. Thirty-seven
other missing Coldcard histories and all CryptoBilis rows stay retained.

Work is divided into twenty, twenty and ten sources. Audit, save private evidence
and publish each bounded unit before another acquisition unit. Fresh histories
use native Mempool pagination through at most thirty-two pages. The final unit
also extends eight existing native cursors by at most sixteen new pages each;
the original mixed-provider bridge must retain its actual native cursor and
verified raw union, never the sorted union's last transaction as an API cursor.

Keep one worker, five-second spacing, the verified forty-five-second response
timeout, provider-specific live gate, historical/local locks and exact published
lease/readback. Stop on first failure/refusal/inconsistency. Never restart a
consumed scope or revive operational flags. No account/IP/proxy/provider rotation,
TLS change, paid service, model fitting/scoring or automatic schedule. Preserve
all old vectors, missing rows, unknown theft/device labels and full-current
statuses. Recheck overlap before future updated-snapshot model work.

Fifty processed sources does not imply fifty complete histories. Bounded results
retain null features, their observations and actual private continuation cursor.
''')
    return selection


def prepare(unit, parent):
    selection = initialize()
    assert unit in (1, 2), 'Mixed saved-history unit requires its separately verified seed preparer'
    chosen = selection['units'][unit-1]; ids = chosen['source_ids']
    assert len(ids) == 20 and chosen['kind'] == 'fresh_native'
    parent = parent.resolve(); oldwork = BASE / ('source_cohort_work_' + parent.name)
    assert read(parent / 'independent_verification.json')['status'] == 'passed'
    assert read(parent / 'private_cache_backup.json')['saved_privately']
    progress = read(CAMPAIGN / 'progress.json')
    assert set(ids) <= set(progress['pending_source_ids']) and not set(ids) & set(progress['finalized_source_ids'])
    policy = read(BASE / 'comparison_access_retries_20261030/retry_policy.json')
    assert policy['collector_lease']['state'] == 'idle' and policy['active_collection_scope'] == 'none'
    gate = policy['provider_access_policies']['https://mempool.space/api'].get('next_network_attempt_not_before')
    assert gate is None or datetime.now(timezone.utc) >= datetime.fromisoformat(gate)
    out = BASE / (CAMPAIGN.name + f'_{unit:02d}'); work = BASE / ('source_cohort_work_' + out.name)
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
    inputs.update(campaign_selection=CAMPAIGN / 'selection.json', preparer=Path(__file__).resolve(),
                  offline_reuse_manifest=out / 'offline_reuse_manifest.json')
    budget = dict(full_references_at_most=20, tail_pages_at_most=20*32, after_anchor_statuses_at_most=20,
                  funding_statuses_at_most=sum(r['registry_input_slots'] for r in records))
    maximum = sum(budget.values()); budget['total_new_requests_at_most'] = maximum
    q = dict(schema_version=4, pass_name=out.name, created_on='2026-11-12',
        authorization=selection['authorization'], campaign=CAMPAIGN.name, campaign_unit=unit,
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
    write(out / 'preparation_verification.json', dict(status='passed', selected=20,
        frozen_identities_verified=20, input_pins_verified=len(inputs), baseline_vectors=q['baseline_vectors'],
        campaign_requested_sources=50, provider_requests=0, tests_previously_passed=29))
    (out / 'README.md').write_text(f'''# Fifty-source campaign: unit {unit}

This bounded twenty-source native-Mempool unit is part of the explicitly requested
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
