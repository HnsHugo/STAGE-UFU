"""Seal already-written evidence after process termination; never issues HTTP."""
import argparse
from contextlib import ExitStack
from datetime import datetime, timezone
import fcntl
import hashlib
from pathlib import Path

import collect_reference_tail as tail
from prepare_frontier_checkpoint import read, sha, write


def seal(out):
    out = out.resolve()
    work = out.parent / ('source_cohort_work_' + out.name)
    q = read(out / 'protocol.json')
    assert not (out / 'run_receipt.json').exists()
    for pin in q['inputs'].values():
        assert sha((out / pin['file']).resolve()) == pin['sha256']
    locks = sorted(set(read(work / 'historical_locks.json')) | {str(work / 'collector.lock')})
    with ExitStack() as stack:
        for name in locks:
            lock = stack.enter_context(Path(name).open('a+'))
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        markers = [(p, read(p)) for p in sorted((work / 'requests').glob('*/*.json'))]
        fresh = [(p, m) for p, m in markers if not m.get('offline_reused')]
        unknown = []
        for p, m in fresh:
            if 'error_type' not in m and m.get('http_status') != 200:
                assert not p.with_suffix('.json.gz').exists() and 'sha256' not in m
                unknown.append(dict(source_id=m['source_id'], key=m['key'],
                                    original_marker_sha256=sha(p),
                                    outcome='unknown_after_process_termination'))
        # Preserve original request markers, including unacknowledged intents.
        tail.export(out / 'protocol.json', out, work)
        entries = read(out / 'checkpoint.json.gz')['entries']
        receipt = dict(schema_version=1, status='stopped',
                       error=dict(error_type='ProcessTermination', reason='Execution was interrupted; offline sealing only, no restart or new request.'),
                       provider=q['provider'], provider_requests=len(fresh),
                       http200=sum(m.get('http_status') == 200 for p, m in fresh),
                       failures=sum('error_type' in m for p, m in fresh),
                       unknown_response_outcomes=len(unknown),
                       reused_successful_responses=len(markers)-len(fresh),
                       finalized_sources=len(entries), operational_locks_released=True,
                       blockstream_provider_requests=0, automatic_retry_performed=False,
                       proxy_account_ip_or_tls_changed=False, model_fits=0, new_scores=0,
                       receipt_reconstructed_offline=True)
        write(out / 'interruption_receipt.json', dict(schema_version=1,
              observed_at=datetime.now(timezone.utc).isoformat(), scope=out.name,
              original_response_markers_unchanged=True, unacknowledged_requests=unknown,
              original_request_records=len(markers), saved_http200=receipt['http200'],
              already_finalized_sources=list(entries), restart_same_scope_allowed=False,
              offline_sealing_provider_requests=0, historical_and_local_locks_free=len(locks),
              limitation='An unacknowledged request has unknown server outcome. No response, HTTP failure, or provider ban is inferred. Pending pages are saved without promoting a vector.'))
        write(out / 'run_receipt.json', receipt)
    return receipt


def retain_pending(out):
    out = out.resolve()
    work = out.parent / ('source_cohort_work_' + out.name)
    audit = read(out / 'coverage_audit.json')
    receipt = read(out / 'run_receipt.json')
    assert audit['status'] == 'passed' and receipt['status'] == 'stopped'
    assert receipt['operational_locks_released'] and receipt['receipt_reconstructed_offline']
    resume = read(out / 'resume_checkpoint.json')
    cursors = read(work / 'native_cursors.json')
    pending = []
    for item in audit['pending_source_page_checkpoints']:
        sid = item['source_id']
        cur = cursors[sid]
        assert not cur['finalized']
        if not item['saved_tail_pages']:
            continue
        assert item['last_cursor_sha256'] == hashlib.sha256(cur['cursor'].encode()).hexdigest()
        pending.append(dict(source_id=sid, provider='https://mempool.space/api',
            native_pages=item['saved_tail_pages'], saved_evidence_pages=item['saved_tail_pages'],
            seed_kind='native_pending_unfinalized', finalized=False,
            last_native_cursor_sha256=item['last_cursor_sha256'],
            evidence_scope=out.name, no_vector_promoted=True,
            requires_distinct_pinned_successor=True,
            requires_fresh_before_after_anchor_and_funding_closure=True))
    queue = {r['source_id']: r for r in resume['retained_native_partial_queue']}
    for item in pending:
        assert item['source_id'] not in queue
        queue[item['source_id']] = item
    resume.update(retained_native_partial_queue=list(queue.values()),
                  interrupted_pending_native_evidence=pending,
                  unknown_response_outcomes=receipt['unknown_response_outcomes'],
                  restart_same_scope_allowed=False, collection_can_resume=False,
                  next_action='Execution is interrupted and safely closed; do not automatically restart. Preserve the unfinished native pages and actual cursor in a distinct successor, with fresh anchors and exact published lease/readback. ' + resume['next_action'])
    write(out / 'resume_checkpoint.json', resume)
    interrupted = read(out / 'interruption_receipt.json')
    interrupted.update(independently_audited=True, pending_native_evidence=pending,
                       unknown_outcomes_not_classified_as_http_failures=True)
    write(out / 'interruption_receipt.json', interrupted)
    verified = read(out / 'execution_verification.json')
    verified.update(interrupted_pending_native_histories_preserved=len(pending),
                    unknown_response_outcomes=receipt['unknown_response_outcomes'],
                    unacknowledged_original_markers_unchanged=True,
                    pending_vectors_not_promoted=True, offline_sealer_sha256=sha(Path(__file__)))
    write(out / 'execution_verification.json', verified)
    pp = out.parent / 'comparison_access_retries_20261030/retry_policy.json'
    policy = read(pp)
    assert policy['collector_lease']['state'] == 'idle'
    policy.update(latest_status='fifty_checkpoint_interrupted_verified',
                  coverage_pause_reason='Execution interrupted; all observed evidence audited and preserved. No active collector or automatic restart.',
                  next_coverage_action=resume['next_action'])
    write(pp, policy)
    return dict(pending_native_histories_preserved=len(pending),
                unknown_response_outcomes=receipt['unknown_response_outcomes'])


if __name__ == '__main__':
    import json
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('scope', type=Path)
    p.add_argument('--retain-pending', action='store_true')
    args = p.parse_args()
    print(json.dumps(retain_pending(args.scope) if args.retain_pending else seal(args.scope), sort_keys=True))
