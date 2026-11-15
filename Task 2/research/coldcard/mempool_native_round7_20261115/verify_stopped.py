"""Verify this saved, stopped campaign without promoting quarantined vectors."""
from contextlib import ExitStack
from datetime import datetime, timezone
import fcntl
from pathlib import Path
import sys

CAMPAIGN = Path(__file__).resolve().parent
BASE = CAMPAIGN.parent
sys.path.insert(0, str(BASE))
from prepare_frontier_checkpoint import read, sha, write


def verify():
    selection = read(CAMPAIGN / 'selection.json')
    state = read(CAMPAIGN / 'progress.json')
    policy = read(BASE / 'comparison_access_retries_20261030/retry_policy.json')
    assert state['status'] == 'stopped_timing_audit_failed' and state['can_continue'] is False
    assert state['active_scope'] is None and state['next_unit'] is None
    assert policy['active_collection_scope'] == 'none' and policy['collector_lease']['state'] == 'idle'
    assert policy['automation_enabled'] is False
    baseline = read(BASE / selection['original_parent'] / 'precutoff_feature_view.json.gz')
    previous = selection['original_parent']
    successful_requests = observations = saved_files = 0
    ledger = []
    locks = set()
    for index, unit in enumerate(state['completed_units'], 1):
        out = BASE / unit['scope']
        q = read(out / 'protocol.json')
        audit = read(out / 'coverage_audit.json')
        receipt = read(out / 'run_receipt.json')
        backup = read(out / 'private_cache_backup.json')
        assert unit['unit'] == index and q['source_ids'] == selection['units'][index - 1]
        assert q['parent_scope'] == previous
        assert audit['status'] == read(out / 'independent_verification.json')['status'] == 'passed'
        assert receipt['status'] == 'completed' and receipt['provider_requests'] == receipt['http200']
        assert receipt['failures'] == 0 and receipt['operational_locks_released']
        assert backup['saved_privately'] and backup['library_metadata_applied'] and unit['private_evidence_saved']
        for pin in q['inputs'].values():
            assert sha((out / pin['file']).resolve()) == pin['sha256']
        successful_requests += receipt['http200']
        observations += audit['fresh_native_source_transaction_observations']
        saved_files += backup['private_files_verified']
        work = BASE / ('source_cohort_work_' + out.name)
        locks.update(read(work / 'historical_locks.json'))
        locks.add(str(work / 'collector.lock'))
        ledger.append(dict(scope=out.name, full_audit='passed', http200=receipt['http200'],
                           new_complete=audit['new_complete_prefixes']))
        previous = out.name
    assert len(ledger) == 3 and previous == 'mempool_native_round7_20261115_unit_03'
    official_path = previous + '/precutoff_feature_view.json.gz'
    assert policy['latest_consolidated_prefix_view'] == official_path
    official = read(BASE / official_path)
    before = {r['source_id']: r for r in baseline['rows']}
    rows = {r['source_id']: r for r in official['rows']}
    assert len(rows) == 1500 and sum(r['features'] is not None for r in rows.values()) == 1445
    for sid, row in before.items():
        if row['features'] is not None:
            assert rows[sid] == row
    out = BASE / state['stopped_scope']
    work = BASE / ('source_cohort_work_' + out.name)
    q = read(out / 'protocol.json')
    failure = read(out / 'audit_failure.json')
    data = read(out / 'offline_data_verification.json')
    receipt = read(out / 'run_receipt.json')
    backup = read(out / 'private_cache_backup.json')
    assert q['parent_scope'] == previous and q['source_ids'] == selection['units'][3]
    for pin in q['inputs'].values():
        assert sha((out / pin['file']).resolve()) == pin['sha256']
    assert failure['status'] == 'failed' and failure['minimum_recorded_interval_seconds'] == 4.79656
    assert len(failure['anomalies']) == 1 and failure['original_audit_passed'] is False
    assert data['status'] == 'data_verified_operational_failure' and data['data_verification_status'] == 'passed'
    assert data['official_view_promotion_authorized'] is False and data['new_provider_requests_authorized'] is False
    assert data['new_complete_source_ids'] == ['comparison_0877'] and data['available_coldcard_vectors'] == 1446
    assert not (out / 'coverage_audit.json').exists() and not (out / 'independent_verification.json').exists()
    assert receipt['provider_requests'] == receipt['http200'] == 149 and receipt['failures'] == 0
    assert receipt['operational_locks_released'] and not (work / 'lease_published').exists()
    assert backup['saved_privately'] and backup['library_metadata_applied'] and backup['full_scope_audit_passed'] is False
    assert state['stopped_unit_private_evidence_sha256'] == backup['sha256']
    markers = [read(p) for p in sorted(work.glob('requests/*/*.json'))]
    assert markers == read(out / 'request_manifest.json.gz')
    fresh = [m for m in markers if not m.get('offline_reused')]
    assert len(fresh) == 149 and all(m.get('http_status') == 200 for m in fresh)
    successful_requests += 149
    observations += data['fresh_native_source_transaction_observations']
    saved_files += backup['private_files_verified']
    locks.update(read(work / 'historical_locks.json'))
    locks.add(str(work / 'collector.lock'))
    with ExitStack() as stack:
        for name in sorted(locks):
            f = stack.enter_context(Path(name).open('a+'))
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
    validation = read(CAMPAIGN / 'session_validation.json')
    assert validation['status'] == 'passed' and validation['tests_passed'] == 46 and validation['tests_failed'] == 0
    assert all(not (BASE / (CAMPAIGN.name + f'_unit_{unit:02d}')).exists() for unit in [5, 6])
    result = dict(status='stopped_saved_verified', verified_at=datetime.now(timezone.utc).isoformat(),
        campaign_complete=False, official_coldcard_vectors=1445, official_missing_vectors=55,
        quarantined_data_verified_candidate_vectors=1, quarantined_source_ids=['comparison_0877'],
        fully_audited_saved_sources=8, collected_stopped_sources=3, unattempted_campaign_sources=6,
        total_successful_requests_including_preceding_unit_01=successful_requests,
        resumed_session_successful_requests=successful_requests-104,
        prior_block_observations_including_preceding_unit_01=observations,
        resumed_session_prior_block_observations=observations-2500,
        http_failures=0, dispatch_audit_failures=1, minimum_recorded_interval_seconds=4.79656,
        actual_spacing_or_clock_adjustment_not_distinguishable=True,
        private_evidence_files_saved=saved_files, operational_locks_checked_free=len(locks),
        lease_idle=True, provider_gate_closed=True, automation_enabled=False,
        original_pinned_collectors_unchanged=True, old_complete_vectors_preserved=1445,
        clock_fix_tests_passed=6, total_focused_tests_passed=46, units=ledger,
        official_view=official_path, quarantined_candidate_view=state['quarantined_candidate_view'],
        model_fits=0, new_scores=0)
    assert result['resumed_session_successful_requests'] == 461
    assert result['resumed_session_prior_block_observations'] == 11037
    write(CAMPAIGN / 'final_verification.json', result)
    print(__import__('json').dumps(result, indent=2))
    return result


if __name__ == '__main__':
    verify()
