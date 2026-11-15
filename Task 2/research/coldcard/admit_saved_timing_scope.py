"""Offline admission of scientific data, retaining a failed collection timing audit."""
from contextlib import ExitStack
from copy import deepcopy
from datetime import datetime, timezone
import fcntl
import gzip
import hashlib
import os
from pathlib import Path
import sys

from prepare_frontier_checkpoint import read, sha, write
from build_source_registry import json_bytes
import collect_reference_tail as tail
from independent_mempool_resume import cached_prefix

BASE = Path(__file__).resolve().parent
SCOPE = 'mempool_data_admission_20261115'


def admit():
    out = BASE / SCOPE
    work = BASE / ('source_cohort_work_' + SCOPE)
    assert not out.exists() and not work.exists()
    src = BASE / 'mempool_native_round7_20261115_unit_04'
    rawwork = BASE / ('source_cohort_work_' + src.name)
    policy_path = BASE / 'comparison_access_retries_20261030/retry_policy.json'
    policy = read(policy_path)
    assert policy['collector_lease']['state'] == 'idle' and policy['active_collection_scope'] == 'none'
    parent = (BASE / policy['latest_consolidated_prefix_view']).parent
    baseline = read(parent / 'precutoff_feature_view.json.gz')
    before = {r['source_id']: r for r in baseline['rows']}
    assert sum(r['features'] is not None for r in before.values()) == 1445
    failure = read(src / 'audit_failure.json')
    data = read(src / 'offline_data_verification.json')
    assert failure['status'] == 'failed' and failure['minimum_recorded_interval_seconds'] == 4.79656
    assert data['data_verification_status'] == 'passed' and data['operational_audit_status'] == 'failed'
    assert read(src / 'private_cache_backup.json')['saved_privately']
    locks = sorted(set(read(rawwork / 'historical_locks.json')) | {str(rawwork / 'collector.lock')})
    records = {r['pilot_id']: r for r in read(rawwork / 'plan.json')}
    entries = read(src / 'checkpoint.json.gz')['entries']
    assert set(entries) == set(records) == {'comparison_0853', 'comparison_0877', 'comparison_0892'}
    sys.path.insert(0, str(BASE.parent / 'external_cases/cryptobilis_to_coldcard_20261109'))
    from experiment import recount_features
    with ExitStack() as stack:
        for name in locks:
            f = stack.enter_context(Path(name).open('a+'))
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        markers = [read(p) for p in sorted(rawwork.glob('requests/*/*.json'))]
        assert markers == read(src / 'request_manifest.json.gz')
        for p in rawwork.glob('requests/*/*.json'):
            meta = read(p)
            assert meta.get('http_status') == 200 and sha(p.with_suffix('.json.gz')) == meta['sha256']
        for sid, entry in entries.items():
            record = records[sid]
            for k in ['address_sha256', 'payment_txid_sha256', 'cutoff_height', 'cutoff_block_hash']:
                assert record[k] == before[sid][k]
            raw_path = rawwork / entry['raw_file']
            assert sha(raw_path) == entry['raw_sha256']
            raw = read(raw_path)
            expected = tail.tail_check(record, raw['anchor'], raw['transactions'], raw['pagination_exhausted'],
                                       raw['anchor_after'], raw['parent_statuses'])
            assert all(entry[k] == expected[k] for k in ['status', 'features', 'prefix'])
            if entry['features'] is not None:
                assert sid == 'comparison_0877' and raw['pagination_exhausted']
                assert recount_features(entry['prefix'], record['cutoff_height']) == entry['features']
        view = read(src / 'offline_candidate_feature_view.json.gz')
        rows = {r['source_id']: r for r in view['rows']}
        assert set(rows) == set(before)
        for sid, old in before.items():
            if old['features'] is not None or sid not in entries:
                assert rows[sid] == old
            for k in ['source_id', 'address_sha256', 'payment_txid_sha256', 'cutoff_height', 'cutoff_block_hash',
                      'labels', 'known_coldcard_core_membership', 'full_history_status']:
                assert rows[sid].get(k) == old.get(k)
        assert sum(r['features'] is not None for r in rows.values()) == 1446
        out.mkdir()
        work.mkdir(mode=0o700)
        for name in ['remaining_source_registry.json', 'retained_bridge_native_cursors.json']:
            (work / name).write_bytes((rawwork / name).read_bytes())
        write(work / 'plan.json', list(records.values()))
        write(work / 'native_cursors.json', read(rawwork / 'offline_native_cursors.json'))
        write(work / 'historical_locks.json', locks)
        write(work / 'admitted_evidence.json', dict(source_scope=src.name, source_work=rawwork.name,
            entries={sid: dict(raw_file=e['raw_file'], raw_sha256=e['raw_sha256']) for sid, e in entries.items()},
            required_saved_archive=read(src / 'private_cache_backup.json'), operational_failure_preserved=True))
        pins = dict(predecessor_view=parent / 'precutoff_feature_view.json.gz', predecessor_resume=parent / 'resume_checkpoint.json',
            source_protocol=src / 'protocol.json', source_checkpoint=src / 'checkpoint.json.gz',
            source_data_audit=src / 'offline_data_verification.json', source_timing_failure=src / 'audit_failure.json',
            source_private_backup=src / 'private_cache_backup.json', admission_code=Path(__file__).resolve())
        q = dict(pass_name=SCOPE, purpose='Explicitly authorized offline scientific-data admission, not collection-audit clearance',
            user_request='Aller go fais en 20 en plus de save; approve the proposed offline admission and twenty saved histories.',
            source_ids=list(records), provider_requests=0, original_operational_failure_preserved=True,
            inputs={k: dict(file=os.path.relpath(p, out), sha256=sha(p)) for k,p in pins.items()})
        write(out / 'protocol.json', q)
        for sid in entries:
            rows[sid]['precutoff_history_provenance']['offline_data_admission_scope'] = SCOPE
        view['inputs']['offline_data_admission_protocol_sha256'] = sha(out / 'protocol.json')
        view['collection_operational_warnings'] = [dict(source_scope=src.name, audit='failed_UTC_spacing',
            data_admitted_by=SCOPE, original_failure_sha256=sha(src / 'audit_failure.json'))]
        (out / 'precutoff_feature_view.json.gz').write_bytes(gzip.compress(json_bytes(view), mtime=0))
        resume = deepcopy(read(parent / 'resume_checkpoint.json'))
        queue = {r['source_id']: r for r in resume['retained_native_partial_queue']}
        cursors = read(work / 'native_cursors.json')
        queue.pop('comparison_0877')
        for sid in ['comparison_0853', 'comparison_0892']:
            cur = cursors[sid]
            queue[sid] = dict(source_id=sid, provider='https://mempool.space/api', seed_kind='native',
                native_pages=cur['saved_native_pages'], saved_evidence_pages=cur['saved_native_pages'],
                last_native_cursor_sha256=hashlib.sha256(cur['cursor'].encode()).hexdigest(),
                evidence_scope=src.name, offline_data_admission_scope=SCOPE, finalized=True,
                requires_distinct_pinned_successor=True)
        resume.update(pass_name=SCOPE, status='offline_data_admission_complete', coldcard_vectors_available=1446,
            coldcard_remaining_bounded_source_ids=[sid for sid,r in rows.items() if r['features'] is None],
            retained_native_partial_queue=list(queue.values()), collection_can_resume=False,
            original_operational_failure_preserved=True, provider_requests=0)
        write(out / 'resume_checkpoint.json', resume)
        (out / 'retained_deep_queue.json').write_bytes((parent / 'retained_deep_queue.json').read_bytes())
        report = dict(status='passed',scope=SCOPE,verification_scope='offline_scientific_data_admission_only',
            provider_requests=0, old_complete_vectors_preserved=1445, admitted_complete_source_ids=['comparison_0877'],
            available_vectors=1446, missing_vectors=54, admitted_partial_evidence_source_ids=['comparison_0853','comparison_0892'],
            original_operational_audit_status='failed', original_failure_preserved=True,
            source_bodies_verified=len(markers), features_independently_recounted=1,
            model_fits=0,new_scores=0,verified_at=datetime.now(timezone.utc).isoformat())
        write(out / 'independent_verification.json', report)
        write(out / 'run_receipt.json', dict(status='offline_completed',provider_requests=0,http200=0,failures=0,
            operational_locks_released=True,blockstream_provider_requests=0,model_fits=0,new_scores=0))
        policy.update(latest_consolidated_prefix_view=SCOPE+'/precutoff_feature_view.json.gz',
            latest_prefix_resume_file=SCOPE+'/resume_checkpoint.json', latest_prefix_work=work.name,
            comparison_pre_cutoff_predictors_available=946,comparison_pre_cutoff_predictors_unavailable=54,
            latest_status='offline_data_admission_1446_with_original_timing_warning_preserved')
        write(policy_path, policy)
        (out / 'README.md').write_text('# Offline scientific-data admission\n\nOne complete prefix is independently reconstructed and admitted under the current user instruction: 1,446/1,500 vectors, 54 missing. The original collection timing audit remains failed and preserved. No provider request is issued and no old scope is reopened. Two partial histories are also admitted as reusable evidence, without a complete vector. New traffic needs the recorded timing runner, a distinct pinned protocol, fresh locks and published lease/readback. The private delta references the already-saved full source evidence layer.\n')
    return report


if __name__ == '__main__':
    print(__import__('json').dumps(admit(), sort_keys=True))
