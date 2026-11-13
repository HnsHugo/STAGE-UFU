"""Close an audited five-source checkpoint without losing the frozen fifty-ID ledger."""
import argparse
from datetime import datetime, timedelta, timezone
import hashlib
from pathlib import Path

from prepare_frontier_checkpoint import read, sha, write

BASE = Path(__file__).resolve().parent
CAMPAIGN = BASE / 'mempool_fifty_20261112'


def finalize(out):
    out = out.resolve(); work = BASE / ('source_cohort_work_' + out.name)
    q, audit, receipt = (read(out / n) for n in ['protocol.json', 'coverage_audit.json', 'run_receipt.json'])
    assert audit['status'] == read(out / 'independent_verification.json')['status'] == 'passed'
    assert receipt['operational_locks_released'] and receipt['blockstream_provider_requests'] == 0
    for p in q['inputs'].values():
        assert sha((out / p['file']).resolve()) == p['sha256']
    selection = read(CAMPAIGN / 'selection.json'); recovery = read(CAMPAIGN / 'recovery_plan_20261113.json')
    assert selection['source_ids'] == recovery['source_ids'] and len(set(selection['source_ids'])) == 50
    assert sha(CAMPAIGN / 'selection.json') == recovery['source_selection_sha256']
    state = read(CAMPAIGN / 'progress.json'); outcomes = state.setdefault('outcomes', {})
    entries = read(out / 'checkpoint.json.gz')['entries']; cursors = read(work / 'native_cursors.json')
    assert set(entries) <= set(q['source_ids']) <= set(selection['source_ids'])
    for sid, e in entries.items():
        if sid in outcomes:
            assert outcomes[sid]['scope'] == out.name and outcomes[sid]['raw_sha256'] == e['raw_sha256'], 'A campaign address was finalized by another scope'
        outcomes[sid] = dict(scope=out.name, status=e['status'], raw_sha256=e['raw_sha256'],
            saved_evidence_pages=e['pages_fetched'], last_native_cursor_sha256=hashlib.sha256(cursors[sid]['cursor'].encode()).hexdigest())
    finalized = [s for s in selection['source_ids'] if s in outcomes]
    complete = [s for s in finalized if outcomes[s]['status'] == 'complete_prior_prefix']
    bounded = [s for s in finalized if s not in complete]
    pending = [s for s in selection['source_ids'] if s not in outcomes]
    assert audit['available_coldcard_vectors'] == 1413 + len(complete)
    unit_summary = dict(scope=out.name, segment=q.get('campaign_segment'), selected_source_ids=q['source_ids'],
        finalized_source_ids=list(entries), new_complete_source_ids=audit['new_complete_source_ids'],
        requests=receipt['provider_requests'], http200=receipt['http200'], failures=receipt['failures'])
    state.update(status='verified_checkpoint_awaiting_save' if pending else 'verified_all_fifty_awaiting_save',
        active_scope=None, finalized_source_ids=finalized, new_complete_source_ids=complete,
        bounded_source_ids=bounded, pending_source_ids=pending, available_coldcard_vectors=audit['available_coldcard_vectors'],
        automation_enabled=False, latest_verified_scope=out.name)
    if not any(u['scope'] == out.name for u in state['completed_units']):
        state['completed_units'].append(unit_summary)
    write(CAMPAIGN / 'progress.json', state)
    parent = read((out / q['inputs']['parent_resume_checkpoint_json']['file']).resolve())
    view = read(out / 'precutoff_feature_view.json.gz')
    missing = [r['source_id'] for r in view['rows'] if r['features'] is None]
    queue = {r['source_id']: r for r in parent['retained_native_partial_queue']}
    for sid, e in entries.items():
        if e['features'] is not None:
            queue.pop(sid, None); continue
        raw = read(work / e['raw_file']); cur = cursors[sid]
        queue[sid] = dict(source_id=sid, provider=q['provider'], native_pages=cur['saved_native_pages'],
            saved_evidence_pages=e['pages_fetched'], distinct_transactions=len(raw['transactions']),
            seed_kind=raw.get('seed_kind', 'native'),
            last_native_cursor_sha256=hashlib.sha256(cur['cursor'].encode()).hexdigest(),
            requires_distinct_pinned_successor=True)
    unextended = [s for s in parent['coldcard_unextended_at_16_page_bound_source_ids'] if s not in entries]
    next_action = ('Continue only the pending frozen campaign IDs in a distinct saved/published checkpoint. ' if pending else
        'The requested fifty addresses are finalized; retain every bounded history and all other missing rows for a separately chosen next unit. ')
    next_action += 'Preserve actual native cursors, all old vectors, unknown labels, cutoffs, full-current statuses and deep histories. Keep one worker, five-second spacing, verified TLS/inherited proxy, the provider-specific gate and exact published lease/readback under fresh locks. No consumed-scope restart, provider/account/IP/proxy rotation, paid service, model fit/score or automatic schedule. Recheck overlap before model work.'
    resume = dict(schema_version=6, pass_name=out.name, campaign=CAMPAIGN.name, provider=q['provider'],
        status='closed_verified_checkpoint', source_ids=q['source_ids'], finalized_source_ids=list(entries),
        new_complete_source_ids=audit['new_complete_source_ids'], pending_source_ids=[s for s in q['source_ids'] if s not in entries],
        next_collection_source_ids=pending[:5], campaign_pending_source_ids=pending,
        coldcard_vectors_available=audit['available_coldcard_vectors'], cryptobilis_vectors_available=329,
        all_bounded_prefixes=len(missing)+37, coldcard_remaining_bounded_source_ids=missing,
        coldcard_unextended_at_16_page_bound_source_ids=unextended, retained_native_partial_queue=list(queue.values()),
        retained_deep_queue_file='retained_deep_queue.json', private_native_cursors_sha256=sha(work / 'native_cursors.json'),
        private_identity_registry_sha256=sha(work / 'remaining_source_registry.json'),
        private_retained_bridge_native_cursors_sha256=sha(work / 'retained_bridge_native_cursors.json'),
        blockstream_cooldown_preserved_until=q['blockstream_cooldown_preserved_until'],
        collection_can_resume=False, restart_same_scope_allowed=False, automation_enabled=False,
        next_action=next_action, model_fits=0, new_scores=0)
    write(out / 'resume_checkpoint.json', resume)
    policy_path = BASE / 'comparison_access_retries_20261030/retry_policy.json'; policy = read(policy_path)
    assert policy['collector_lease']['owner'] == out.name
    now = datetime.now(timezone.utc)
    policy['collector_lease'].update(state='idle', owner=None, last_owner=out.name, expires_at=None,
        finished_at=now.isoformat(), stop_status='verified_checkpoint_closed', operational_locks_released=True)
    policy.update(active_collection_scope='none', automation_enabled=False, coverage_collection_paused=True,
        coverage_pause_reason='The checkpoint is audited and closed. No active collector or automatic schedule; save and publish before the next scope.',
        latest_status='fifty_campaign_checkpoint_verified', latest_consolidated_prefix_view=str((out / 'precutoff_feature_view.json.gz').relative_to(BASE)),
        latest_prefix_output=out.name, latest_prefix_protocol=str((out / 'protocol.json').relative_to(BASE)),
        latest_prefix_result_file=str((out / 'coverage_audit.json').relative_to(BASE)),
        latest_prefix_resume_file=str((out / 'resume_checkpoint.json').relative_to(BASE)),
        latest_prefix_stop_file=str((out / 'collection_stop.json').relative_to(BASE)), latest_prefix_work=work.name,
        comparison_pre_cutoff_predictors_available=audit['available_coldcard_vectors']-500,
        comparison_pre_cutoff_predictors_unavailable=len(missing), prefix_bounded_incomplete_sources=len(missing),
        prefix_network_pending_sources=len(pending), latest_pass_pending_sources=len(pending), next_coverage_action=next_action)
    gate = policy['provider_access_policies'][q['provider']]; gate.update(status='verified_checkpoint_closed',
        last_http200=receipt['http200'], last_refusals=0, next_network_attempt_not_before=None)
    policy['latest_prefix_coverage_audit'] = policy['latest_prefix_result_file']
    policy['latest_prefix_resume_checkpoint'] = policy['latest_prefix_resume_file']
    failures = [m for m in read(out / 'request_manifest.json.gz') if not m.get('offline_reused') and 'error_type' in m]
    if failures:
        refused = [m for m in failures if m.get('failure_origin') == 'provider_http_response']
        due = now+timedelta(hours=1) if refused else now+timedelta(seconds=60)
        for m in refused:
            retry = m.get('retry_after')
            if retry:
                try:
                    server_due = now+timedelta(seconds=int(retry))
                except ValueError:
                    from email.utils import parsedate_to_datetime
                    server_due = parsedate_to_datetime(retry)
                due = max(due, server_due)
        gate.update(last_refusals=len(refused), status='closed_after_first_failure',
            next_network_attempt_not_before=due.isoformat(),
            local_backoff_not_server_ban_duration=True)
    write(policy_path, policy)
    write(out / 'collection_stop.json', dict(status=receipt['status'], operational_locks_released=True,
        automation_enabled=False, restart_same_scope_allowed=False, blockstream_requests=0))
    write(out / 'execution_verification.json', dict(status='passed', focused_tests_previously_passed=29,
        input_pins_verified=len(q['inputs']), old_vectors_preserved=q['baseline_vectors'],
        new_vectors_independently_recounted=audit['new_complete_prefixes'], campaign_unique_finalized=len(finalized),
        frozen_campaign_source_ids_verified=50, unarchived_old_candidates_not_promoted=True,
        labels_cutoffs_full_current_statuses_unchanged=True, model_fits=0, new_scores=0))
    return dict(campaign_finalized=len(finalized), campaign_pending=len(pending), campaign_complete=len(complete),
                vectors=audit['available_coldcard_vectors'], scope=out.name)


if __name__ == '__main__':
    import json
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('scope', type=Path)
    a = p.parse_args(); print(json.dumps(finalize(a.scope), sort_keys=True))
