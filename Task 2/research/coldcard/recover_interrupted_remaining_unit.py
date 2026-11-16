"""Close unit 12 from saved bytes, preserving its single unknown request intent.

No collector is restarted. The original request marker and protocol stay intact.
Only the 120 completed responses have a verifiable dispatch clock; the last
intent has neither a response nor dispatch evidence and is never called a failure.
"""
import argparse
from contextlib import ExitStack
from datetime import datetime, timezone
import fcntl
import importlib.util
from pathlib import Path

from prepare_frontier_checkpoint import read, sha, write
import recorded_remaining_campaign as campaign
import recorded_mempool_resume as recorded

BASE = campaign.BASE
SCOPE = 'mempool_remaining_fifty_20261116_unit_12'
OUT = BASE / SCOPE
WORK = BASE / ('source_cohort_work_' + SCOPE)
UNKNOWN = ('comparison_0157', 'native_tail_0012')
ORIGINAL_VERIFY = recorded.verify_dispatch_evidence


def classify(markers):
    """Require one final unresolved intent and an intact, fully recorded prefix."""
    known, unknown = [], []
    for marker in markers:
        if marker.get('http_status') == 200:
            assert 'error_type' not in marker and marker.get('finished_at')
            assert marker.get('sha256') and marker.get('dispatch_clock_evidence')
            known.append(marker)
        else:
            assert (marker['source_id'], marker['key']) == UNKNOWN
            assert not any(k in marker for k in (
                'http_status', 'sha256', 'error_type', 'finished_at',
                'dispatch_at', 'dispatch_clock_evidence', 'dispatch_not_attempted'))
            unknown.append(marker)
    assert len(unknown) == 1 and known
    assert all(m['finished_at'] <= unknown[0]['started_at'] for m in known)
    clock = ORIGINAL_VERIFY(known)
    return known, unknown, clock


def verify_interrupted_clock(markers):
    proof = read(OUT / 'interruption_recovery.json')
    assert markers == [read(p) for p in sorted(WORK.glob('requests/*/*.json'))]
    for item in proof['original_request_markers']:
        assert sha(WORK / item['file']) == item['sha256']
    known, unknown, clock = classify(markers)
    assert len(known) == proof['http200'] == 120
    return dict(status='incomplete_unknown_intent',
        known_successful_dispatches=clock, unresolved_intents=len(unknown),
        original_marker_unchanged=True, unknown_outcome_not_imputed=True)


def close():
    assert not (OUT / 'run_receipt.json').exists()
    assert not (OUT / 'coverage_audit.json').exists()
    q = read(OUT / 'protocol.json')
    policy = read(campaign.POLICY)
    assert policy['collector_lease']['owner'] == policy['active_collection_scope'] == SCOPE
    assert policy['collector_lease']['protocol_sha256'] == sha(OUT / 'protocol.json')
    for pin in q['inputs'].values():
        assert sha((OUT / pin['file']).resolve()) == pin['sha256']
    locks = set(read(WORK / 'historical_locks.json')) | {str(WORK / 'collector.lock')}
    with ExitStack() as stack:
        for name in sorted(locks):
            handle = stack.enter_context(Path(name).open('a+'))
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        paths = sorted(WORK.glob('requests/*/*.json'))
        markers = [read(p) for p in paths]
        known, unknown, clock = classify(markers)
        assert len(markers) == 121 and len(known) == 120
        for marker in known:
            body = WORK / 'requests' / marker['source_id'] / (marker['key'] + '.json.gz')
            assert sha(body) == marker['sha256']
        unresolved = WORK / 'requests' / UNKNOWN[0] / (UNKNOWN[1] + '.json.gz')
        assert not unresolved.exists()
        results = sorted(p.name for p in (WORK / 'results').glob('*.json.gz'))
        assert results == ['comparison_0176.json.gz', 'comparison_0230.json.gz']
        proof = dict(status='passed', scope=SCOPE, recovery_kind='offline_data_recovery',
            recovered_at=datetime.now(timezone.utc).isoformat(),
            recovery_code_sha256=sha(Path(__file__)), original_protocol_sha256=sha(OUT / 'protocol.json'),
            original_request_markers=[dict(file=str(p.relative_to(WORK)), sha256=sha(p)) for p in paths],
            http200=120, failed_provider_responses=0, unresolved_request_intents=1,
            unresolved_source_id=UNKNOWN[0], unresolved_key=UNKNOWN[1],
            unresolved_marker_sha256=sha(unresolved.with_suffix('')),
            unresolved_dispatch_and_provider_outcome='unknown',
            known_successful_dispatch_verification=clock, original_full_clock_audit='incomplete',
            operational_locks_checked_free=len(locks), restart_same_scope_allowed=False,
            new_provider_requests_during_recovery=0, model_fits=0, new_scores=0)
        write(OUT / 'interruption_recovery.json', proof)
        write(WORK / 'interruption_recovery.json', proof)
        from collect_reference_tail import export
        export(OUT / 'protocol.json', OUT, WORK)
        write(OUT / 'run_receipt.json', dict(status='interrupted_unknown_outcome',
            receipt_origin='Offline administrative recovery; original runner did not finish',
            provider_requests=121, http200=120, failures=0, unresolved_intents=1,
            finalized_sources=2, operational_locks_released=True,
            blockstream_provider_requests=0, automatic_retry_performed=False,
            original_full_clock_audit='incomplete', model_fits=0, new_scores=0))
        import audit_planned_funding_bridge as audit
        recorded.verify_dispatch_evidence = verify_interrupted_clock
        audit.verify_dispatch_evidence = verify_interrupted_clock
        result = campaign.finish(SCOPE)
        for name in ['coverage_audit.json', 'independent_verification.json']:
            report = read(OUT / name)
            report.update(data_reconstruction_status='passed',
                original_full_clock_audit='incomplete_unknown_intent',
                known_successful_dispatches=clock, unresolved_request_intents=1,
                original_request_marker_preserved=True,
                recovery_proof_sha256=sha(OUT / 'interruption_recovery.json'),
                verification_basis='Immutable response/body/endpoint replay and feature checks; clock verified only for 120 completed responses. One final request has unknown dispatch and provider outcome.')
            write(OUT / name, report)
        # No provider refusal is recorded. The current user has explicitly
        # requested continuation. The consumed scope and unknown intent stay
        # closed; a distinct future scope still needs fresh locks/readback.
        policy = read(campaign.POLICY)
        gate = policy['provider_access_policies'][campaign.PROVIDER]
        gate.update(status='interruption_closed_unknown_outcome', no_new_probe_authorized=False,
            operational_validation_required=False,
            next_network_attempt_not_before=policy['collector_lease']['finished_at'],
            unknown_request_outcomes_preserved=1,
            operational_resolution='Saved successful evidence recovered offline under the current explicit Continue authorization; no actual refusal is known. Never restart unit 12.')
        policy['latest_status'] = 'interrupted_unit_data_recovered_clock_incomplete'
        write(campaign.POLICY, policy)
        state = read(campaign.CAMPAIGN / 'progress.json')
        state.update(can_continue=True, next_unit=13,
            continuation_authorization='User: continue je te donne toute les autorisation github',
            deferred_interrupted_source_ids=[UNKNOWN[0]])
        state['completed_units'][-1].update(unresolved_intents=1,
            original_full_clock_audit='incomplete_unknown_intent')
        write(campaign.CAMPAIGN / 'progress.json', state)
        proof = read(OUT / 'interruption_recovery.json')
        proof.update(finalized_sources=2,
            saved_unfinished_native_pages=read(OUT / 'coverage_audit.json')['unfinalized_evidence'][0]['saved_native_pages'],
            original_protocol_preserved=sha(OUT / 'protocol.json') == proof['original_protocol_sha256'])
        # Keep the proof already pinned by the data audit immutable.
        write(OUT / 'recovery_summary.json', proof)
    return result


def saved():
    result = campaign.saved(SCOPE)
    (OUT / 'RESULTS.md').write_text(
        '# Interrupted unit recovered from saved evidence\n\n'
        'Two bounded histories finalized; twelve native pages of the third are retained only as an unfinished continuation seed. '
        '120 responses are saved and independently replayed. One final request intent has unknown dispatch and provider outcome; its original bytes are unchanged. '
        'Data reconstruction passes. Dispatch timing passes for the 120 completed responses only; the original full-scope clock audit is incomplete. '
        'No request was issued during recovery. Coverage remains 1,457/1,500; all previous vectors, unknown labels and cutoffs are unchanged. '
        'The scope is closed. Continue untouched units in distinct scopes; retain comparison_0157 for a distinct successor from its actual saved cursor.\n')
    report = campaign.CAMPAIGN / 'RESULTS.md'
    report.write_text(report.read_text().replace(
        'All completed checkpoints pass data/clock audits and are privately saved.',
        'All saved data checkpoints pass reconstruction checks. Unit 12 has one unresolved request intent: only its 120 completed dispatches have verified timing; its full-scope clock audit remains incomplete.'))
    return result


def verify():
    spec = importlib.util.spec_from_file_location('remaining_progress', campaign.CAMPAIGN / 'verify_progress.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    def dispatch(markers):
        if any((m['source_id'], m['key']) == UNKNOWN and 'finished_at' not in m for m in markers):
            return verify_interrupted_clock(markers)
        return ORIGINAL_VERIFY(markers)
    module.verify_dispatch_evidence = dispatch
    report = module.verify()
    report.update(original_full_clock_audits_complete=False, unresolved_request_intents=1,
        incomplete_clock_scope=SCOPE, known_successful_dispatches_verified=True)
    write(campaign.CAMPAIGN / 'progress_verification.json', report)
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['close', 'saved', 'verify'])
    print(__import__('json').dumps(globals()[parser.parse_args().command](), indent=2))
