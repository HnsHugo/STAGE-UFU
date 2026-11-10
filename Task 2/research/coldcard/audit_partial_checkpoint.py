"""Audit saved partial pages after a stopped checkpoint, without provider HTTP."""
import argparse
from datetime import datetime
import gzip
import hashlib
import json
import os
from pathlib import Path
import sys

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE / 'source_prefix_extension_20261110_01'))
from prepare_scope import validate_cached


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit(scope):
    scope = scope.resolve(); target = scope / 'partial_page_reconciliation.json'
    assert not target.exists(), 'Never replace a closed partial audit'
    q = read(scope / 'protocol.json'); parent = scope.parent / q['parent_scope']
    work = scope.parent / ('source_cohort_work_' + scope.name)
    old_work = parent.parent / ('source_cohort_work_' + parent.name)
    assert sha(work / 'plan.json') == q['private_plan_sha256']
    assert read(scope / 'independent_verification.json')['status'] == 'passed'
    assert not read(scope / 'checkpoint.json.gz')['entries']
    receipt = read(scope / 'run_receipt.json')
    assert receipt['first_refusal_status'] == 429 and receipt['operational_locks_released']
    before = read(parent / 'precutoff_feature_view.json.gz')
    after = read(scope / 'precutoff_feature_view.json.gz')
    assert before['rows'] == after['rows'] and before['predictor_allowlist'] == after['predictor_allowlist']
    pages = {r['source_id']: r['saved_tail_pages'] for r in read(scope / 'coverage_audit.json')['pending_source_page_checkpoints']}
    details, reusable = [], 0
    for record in read(work / 'plan.json'):
        sid = record['pilot_id']
        old = validate_cached(record, old_work, max_pages=q['previous_bound'])
        new = validate_cached(record, work, max_pages=q['max_pages_per_address'])
        assert len(old) == q['previous_bound'] + 1
        assert len(new) == pages[sid] + 1 and len(new) >= len(old)
        for a, b in zip(old, new):
            assert a[0] == b[0]
            assert all(a[3][k] == b[3][k] for k in ['source_id','key','sha256','endpoint_sha256'])
        old_tx = [tx for key, _, body, _ in old if key.startswith('tail_') for tx in read(body)]
        new_tx = [tx for key, _, body, _ in new if key.startswith('tail_') for tx in read(body)]
        assert new_tx[:len(old_tx)] == old_tx
        added = sum(t['status']['block_height'] < record['cutoff_height'] for t in new_tx) - sum(t['status']['block_height'] < record['cutoff_height'] for t in old_tx)
        sequence = [(key, meta['sha256'], meta['endpoint_sha256']) for key, _, _, meta in new]
        details.append(dict(source_id=sid, previous_pages=len(old)-1,
            saved_pages=len(new)-1, reusable_responses=len(new),
            new_saved_tail_pages=len(new)-len(old),
            additional_source_transaction_observations=added,
            current_feature_vector=None,
            remaining_pages_to_same_target=q['max_pages_per_address']-(len(new)-1),
            cached_sequence_sha256=hashlib.sha256(json.dumps(sequence,separators=(',',':')).encode()).hexdigest()))
        reusable += len(new)
    metadata = read(scope / 'request_manifest.json.gz')
    fresh = [m for m in metadata if not m.get('offline_reused')]
    failures = [m for m in fresh if m.get('http_status') != 200]
    assert len(failures) == 2 and all(m['http_status'] == 429 for m in failures)
    first_stop = min(datetime.fromisoformat(m['finished_at']) for m in failures)
    assert all(datetime.fromisoformat(m['started_at']) <= first_stop for m in fresh)
    first = min(fresh, key=lambda m: datetime.fromisoformat(m['started_at']))
    assert first['key'] == 'availability_counter' and first['http_status'] == 200
    added_pages = sum(r['new_saved_tail_pages'] for r in details)
    assert added_pages + 1 == receipt['new_http_200']
    assert len(fresh) == receipt['new_request_records'] == receipt['new_http_200'] + len(failures)
    old_unit = read(parent / 'continuation_reconciliation.json')
    observations = sum(r['additional_source_transaction_observations'] for r in details)
    stop = read(scope / 'collection_stop.json')
    paths = [Path(__file__), scope / 'protocol.json', parent / 'protocol.json',
        parent / 'precutoff_feature_view.json.gz', parent / 'continuation_reconciliation.json',
        scope / 'precutoff_feature_view.json.gz', scope / 'request_manifest.json.gz',
        scope / 'coverage_audit.json', scope / 'independent_verification.json',
        scope / 'run_receipt.json', scope / 'collection_stop.json', scope / 'resume_checkpoint.json']
    report = dict(schema_version=1, status='passed', scope=scope.name,
        current_scope_additional_observations=observations,
        current_scope_new_successful_tail_pages=added_pages,
        current_scope_fresh_http_200=receipt['new_http_200'], current_scope_http_429=len(failures),
        reusable_successful_reference_tail_responses=reusable,
        original_rows_and_vectors_unchanged=True, old_pages_not_repeated=True,
        no_request_start_after_first_refusal=True,
        consecutive_scope_http_200=old_unit['new_successful_bodies']+receipt['new_http_200'],
        consecutive_scope_additional_source_observations=old_unit['additional_source_transaction_observations']+observations,
        observation_count_is_not_globally_unique_transactions=True,
        coldcard_vectors=q['baseline_vectors'], cryptobilis_vectors_unchanged=329,
        remaining_information_gaps=1500-q['baseline_vectors']+37,
        partial_checkpoints=details, same_target_successor_page_target=q['max_pages_per_address'],
        same_target_successor_tail_request_bound=sum(r['remaining_pages_to_same_target'] for r in details),
        next_network_attempt_not_before=stop['next_network_attempt_not_before'],
        model_fits=0, new_scores=0, provider_requests_by_auditor=0,
        input_sha256={os.path.relpath(p.resolve(),scope):sha(p) for p in paths})
    target.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    return {k:v for k,v in report.items() if k not in ['input_sha256','partial_checkpoints']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('scope', type=Path)
    args = parser.parse_args()
    print(json.dumps(audit(args.scope),sort_keys=True))
