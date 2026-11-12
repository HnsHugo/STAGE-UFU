"""Separate fingerprinted old-page recovery from genuinely additional coverage."""
import argparse
from pathlib import Path

from prepare_frontier_checkpoint import read, sha, write
from run_frontier_checkpoint import verify_recovered_response


def finalize(out):
    out = out.resolve()
    assert not (out / 'continuation_reconciliation.json').exists()
    q = read(out / 'protocol.json')
    base = out.parent
    parent = base / q['parent_scope']
    work = base / ('source_cohort_work_' + out.name)
    assert read(out / 'independent_verification.json')['status'] == 'passed'
    assert sha(work / 'remaining_source_registry.json') == q['private_remaining_registry_sha256']
    cp = read(out / 'checkpoint.json.gz')
    assert cp['protocol_sha256'] == sha(out / 'protocol.json')
    entries = cp['entries']
    selected = q['source_ids']
    assert set(entries) <= set(selected)
    original = read(parent / 'precutoff_feature_view.json.gz')
    result = read(out / 'precutoff_feature_view.json.gz')
    before = {r['source_id']: r for r in original['rows']}
    rows = {r['source_id']: r for r in result['rows']}
    assert len(rows) == len(before) == 1500
    for sid, row in rows.items():
        if before[sid]['features'] is not None or sid not in entries:
            assert row == before[sid]
    expected = {(m['source_id'], m['key']): m for m in read(out / 'expected_recovery_manifest.json')['responses']}
    requests = read(out / 'request_manifest.json.gz')
    assert all(not m.get('offline_reused') for m in requests)
    verified = []
    recovered_pages = []
    extra_pages = []
    per_source = []
    for sid in selected:
        markers = [m for m in requests if m['source_id'] == sid]
        saved = [m for m in markers if m.get('http_status') == 200 and 'sha256' in m]
        old = []
        extra = []
        for marker in saved:
            key = marker['key']
            body = work / 'requests' / sid / (key + '.json.gz')
            assert sha(body) == marker['sha256']
            if (sid, key) in expected:
                verify_recovered_response(expected[sid, key], marker)
                verified.append(marker)
            if key.startswith('tail_'):
                index = int(key[5:])
                page = read(body)
                assert isinstance(page, list) and len(page) <= 25
                observations = sum(t['status']['block_height'] < before[sid]['cutoff_height'] for t in page)
                item = dict(source_id=sid, key=key, prior_block_observations=observations)
                if index < q['recovery_old_page_bound']:
                    old.append(item)
                    recovered_pages.append(item)
                else:
                    extra.append(item)
                    extra_pages.append(item)
        if extra:
            assert len(old) == q['recovery_old_page_bound']
            assert sum(m['source_id'] == sid and m['key'] == 'reference' for m in verified) == 1
        status = entries[sid]['status'] if sid in entries else 'pending'
        if sid in entries:
            assert entries[sid]['pages_fetched'] == len(old) + len(extra)
        per_source.append(dict(source_id=sid, status=status, previous_known_page_bound=16,
            old_pages_recovered=len(old), pages_saved=len(old) + len(extra),
            recovered_old_prior_block_observations=sum(x['prior_block_observations'] for x in old),
            additional_source_transaction_observations=sum(x['prior_block_observations'] for x in extra)))
    complete = sorted(sid for sid, e in entries.items() if e['status'] == 'complete_prior_prefix')
    bounded = sorted(sid for sid, e in entries.items() if e['status'] == 'bounded_incomplete')
    pending = [sid for sid in selected if sid not in entries]
    missing = sorted(sid for sid, row in rows.items() if row['features'] is None)
    available = 1500 - len(missing)
    assert available == q['baseline_vectors'] + len(complete)
    old_resume = read(parent / 'resume_checkpoint.json')
    unextended = [sid for sid in old_resume['coldcard_unextended_at_16_page_bound_source_ids'] if sid not in selected]
    assert set(unextended) <= set(missing)
    # Preserve the long-source queue byte for byte, without rerunning it.
    deep = parent / 'retained_deep_queue.json'
    (out / deep.name).write_bytes(deep.read_bytes())
    details = {p['source_id']: p for p in per_source}
    queue = [dict(source_id=sid, saved_pages=details[sid]['pages_saved'],
        previous_known_page_bound=16, requires_distinct_pinned_successor=True,
        next_checkpoint_pages=64 if sid in bounded else 32) for sid in bounded + pending]
    report = dict(schema_version=1, status='all_selected_finalized' if not pending else 'partial_checkpoint',
        selected=len(selected), finalized=len(entries), new_complete_prefixes=len(complete),
        new_complete_source_ids=complete, bounded_incomplete_source_ids=bounded, pending_source_ids=pending,
        preceding_vectors_preserved=q['baseline_vectors'], coldcard_vectors=available,
        coldcard_unavailable_prefixes=len(missing), cryptobilis_vectors_unchanged=329,
        cryptobilis_unavailable_unchanged=37, total_remaining_information_gaps=len(missing) + 37,
        fresh_request_intents=len(requests), fresh_http_200=sum(m.get('http_status') == 200 for m in requests),
        offline_responses_reused=0, recovered_old_responses_fingerprint_verified=len(verified),
        recovered_old_tail_pages=len(recovered_pages), fresh_tail_pages_beyond_old_bound=len(extra_pages),
        recovered_old_prior_block_observations=sum(x['prior_block_observations'] for x in recovered_pages),
        additional_source_transaction_observations=sum(x['prior_block_observations'] for x in extra_pages),
        recovered_pages_excluded_from_added_coverage=True,
        observation_count_is_not_a_global_unique_transaction_count=True,
        source_progress=per_source, continuation_queue=queue,
        remaining_previously_unselected_16_page_sources=len(unextended),
        retained_deep_queue_sha256=sha(out / deep.name), retained_deep_queue_unchanged=True,
        old_scopes_restarted=False, explicit_old_body_reacquisition=True,
        full_current_history_statuses_unchanged=True, verified_device_compromise_labels_remain_unknown=True,
        model_fits=0, new_scores=0, provider_requests_by_reconciler=0,
        final_view_sha256=sha(out / 'precutoff_feature_view.json.gz'))
    write(out / 'continuation_reconciliation.json', report)
    prepared = out / 'resume_checkpoint.json'
    (out / 'prepared_resume_checkpoint.json').write_bytes(prepared.read_bytes())
    write(prepared, dict(schema_version=2, pass_name=out.name, status='closed_checkpoint_audit_passed',
        source_ids=selected, finalized_source_ids=sorted(entries), network_source_ids=pending,
        bounded_incomplete_source_ids=bounded, continuation_required_source_ids=bounded + pending,
        continuation_queue=queue, retained_deep_queue_file=deep.name, collection_can_resume=False,
        restart_same_scope_allowed=False, automation_enabled=False, is_enabled=False, checkpoint_pages=32,
        coldcard_vectors_available=available, coldcard_remaining_bounded_source_ids=missing,
        coldcard_unextended_at_16_page_bound_source_ids=unextended, next_extension_source_ids=unextended[:20],
        cryptobilis_vectors_available=329, cryptobilis_bounded_incomplete=37,
        all_vectors_available=available + 329, all_bounded_prefixes=len(missing) + 37,
        protocol_sha256=sha(out / 'protocol.json'), model_fits=0, new_scores=0,
        next_action='Preserve all finalized and partial pages. If selected sources are pending, finish only those in a distinct bounded successor after live access/cooldown checks. Otherwise select the next at-most-twenty untouched IDs in registry order. Retain every deeper queue and other incomplete row; use fresh locks/lease and the original route. Recheck overlap before updated-snapshot models.',
        overlap_recheck_required_before_updated_snapshot_model_work=True))
    return {k: v for k, v in report.items() if k not in ['source_progress', 'continuation_queue']}


if __name__ == '__main__':
    import json
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('scope', type=Path)
    print(json.dumps(finalize(parser.parse_args().scope), sort_keys=True))
