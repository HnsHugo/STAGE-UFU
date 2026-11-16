"""Reconstruct mixed continuations from pinned seeds and fresh response evidence."""
from copy import deepcopy
import gzip
import hashlib
from pathlib import Path
import sys

from build_source_registry import json_bytes
from prepare_frontier_checkpoint import read, sha, write
from independent_mempool_native import validate_page
from independent_mempool_pilot import PROVIDER, status_check
from recorded_mixed_resume import seed
from recorded_mempool_resume import verify_dispatch_evidence
import collect_reference_tail as tail


def audit(out, work):
    q = read(out / 'protocol.json')
    assert not (out / 'coverage_audit.json').exists()
    for pin in q['inputs'].values():
        assert sha((out / pin['file']).resolve()) == pin['sha256']
    assert sha(work / 'plan.json') == q['private_plan_sha256']
    records = read(work / 'plan.json')
    assert [r['pilot_id'] for r in records] == q['source_ids']
    baseline = read((out / q['inputs']['baseline_view']['file']).resolve())
    before = {r['source_id']: r for r in baseline['rows']}
    parent_resume = read((out / q['inputs']['parent_resume']['file']).resolve())
    queue = {r['source_id']: r for r in parent_resume['retained_native_partial_queue']}
    manifest = read(out / 'request_manifest.json.gz')
    assert manifest == [read(p) for p in sorted((work / 'requests').glob('*/*.json'))]
    verify_dispatch_evidence(manifest)
    assert len(manifest) <= q['maximum_requests']
    checkpoint = read(out / 'checkpoint.json.gz')
    assert checkpoint['protocol_sha256'] == sha(out / 'protocol.json')
    entries = checkpoint['entries']
    assert set(entries) <= set(q['source_ids'])
    composed = deepcopy(baseline)
    rows = {r['source_id']: r for r in composed['rows']}
    complete, details, cursors, consumed = [], [], {}, set()
    sys.path.insert(0, str(out.parents[1] / 'external_cases/cryptobilis_to_coldcard_20261109'))
    from experiment import recount_features

    for record in records:
        sid = record['pilot_id']
        spec, old, values, seen, height = seed(record, work, q)
        assert before[sid]['features'] is None
        assert before[sid]['precutoff_history_provenance']['raw_sha256'] == spec['raw_sha256']
        assert queue[sid]['last_native_cursor_sha256'] == hashlib.sha256(spec['native_cursor'].encode()).hexdigest()
        assert queue[sid]['native_pages'] == old['independent_provider_pages']
        old_values = list(values)
        cursor = spec['native_cursor']
        folder = work / 'requests' / sid

        def response(key, endpoint):
            marker, body = folder / (key + '.json'), folder / (key + '.json.gz')
            if not marker.exists():
                return None
            m = read(marker)
            assert m['source_id'] == sid and m['key'] == key and m['provider'] == PROVIDER
            assert (sid, key) not in consumed
            consumed.add((sid, key))
            assert m['endpoint_sha256'] == hashlib.sha256(endpoint.encode()).hexdigest()
            if not body.exists():
                assert 'sha256' not in m
                return None
            assert m.get('http_status') == 200 and sha(body) == m['sha256']
            return read(body)

        first = response('reference_before', '/tx/' + record['payment_txid'] + '/status')
        if first is not None:
            status_check(record, first)
        pages, exhausted = 0, False
        for i in range(q['maximum_new_native_pages']):
            page = response(f'extension_{i:04d}', '/address/' + record['address'] + '/txs/chain/' + cursor)
            if page is None:
                break
            height = validate_page(record, page, seen, height)
            pages += 1
            if not page:
                exhausted = True
                break
            values.extend(page)
            cursor = page[-1]['txid']
        after = response('reference_after', '/tx/' + record['payment_txid'] + '/status')
        parents = {}
        for txid in sorted({v['txid'] for v in tail.anchor_check(record, old['anchor'])}):
            key = 'parent_' + hashlib.sha256(txid.encode()).hexdigest()
            if (folder / (key + '.json')).exists():
                value = response(key, '/tx/' + txid + '/status')
                if value is not None:
                    status_check(record, value)
                    parents[txid] = value
        if sid in entries:
            e = entries[sid]
            assert sha(work / e['raw_file']) == e['raw_sha256'] and first is not None
            raw = read(work / e['raw_file'])
            assert raw['anchor'] == old['anchor'] and raw['transactions'] == values
            assert raw['transactions'][:len(old_values)] == old_values
            assert raw['anchor_after'] == after and raw['parent_statuses'] == parents
            assert raw['pagination_exhausted'] == exhausted
            assert raw['native_continuation_start_cursor'] == spec['native_cursor']
            assert raw['actual_native_last_cursor'] == cursor
            assert raw['pages_fetched'] == old['pages_fetched'] + pages
            assert raw['independent_provider_pages'] == old['independent_provider_pages'] + pages
            assert raw['legacy_provider_pages'] == old['legacy_provider_pages']
            assert raw['partial_boundary_height'] == old['partial_boundary_height']
            expected = tail.tail_check(record, old['anchor'], values, exhausted, after, parents)
            assert all(e[k] == expected[k] for k in ['status', 'features', 'prefix'])
            if e['features'] is not None:
                assert recount_features(e['prefix'], record['cutoff_height']) == e['features']
                rows[sid]['features'] = e['features']
                rows[sid]['precutoff_history_status'] = 'complete_prior_prefix'
                complete.append(sid)
            rows[sid]['precutoff_history_provenance'] = dict(pass_name=out.name,
                raw_sha256=e['raw_sha256'], pages_fetched=raw['pages_fetched'],
                independent_provider_pages=raw['independent_provider_pages'], provider=PROVIDER,
                method='Verified mixed union plus actual native cursor continuation beyond the legacy boundary',
                full_current_history_counter_coverage_verified=False)
        cursors[sid] = dict(provider=PROVIDER, cursor=cursor,
            saved_native_pages=old['independent_provider_pages'] + pages,
            saved_evidence_pages=old['pages_fetched'] + pages,
            pagination_exhausted=exhausted, finalized=sid in entries)
        details.append(dict(source_id=sid, new_native_pages=pages,
            saved_native_pages=cursors[sid]['saved_native_pages'],
            saved_evidence_pages=cursors[sid]['saved_evidence_pages'],
            old_transactions_retained=len(old_values),
            retained_prior_block_observations=sum(t['status']['block_height'] < record['cutoff_height'] for t in old_values),
            fresh_native_source_transaction_observations=sum(t['status']['block_height'] < record['cutoff_height'] for t in values[len(old_values):]),
            last_native_cursor_sha256=hashlib.sha256(cursor.encode()).hexdigest()))

    assert len(consumed) == len(manifest)
    failures = [m for m in manifest if 'error_type' in m]
    if failures:
        stop = min(m['finished_at'] for m in failures)
        assert all(m['started_at'] <= stop for m in manifest)
    receipt = read(out / 'run_receipt.json')
    assert receipt['provider_requests'] == len(manifest) and receipt['failures'] == len(failures)
    assert receipt['operational_locks_released'] and receipt['blockstream_provider_requests'] == 0
    assert receipt['model_fits'] == receipt['new_scores'] == 0
    for row in composed['rows']:
        previous = before[row['source_id']]
        for key in ['source_id', 'address_sha256', 'payment_txid_sha256', 'cutoff_height',
                    'cutoff_block_hash', 'known_coldcard_core_membership', 'labels', 'full_history_status']:
            assert row.get(key) == previous.get(key)
        if previous['features'] is not None or row['source_id'] not in entries:
            assert row == previous
    assert len(rows) == 1500 and sum(r['features'] is not None for r in before.values()) == q['baseline_vectors']
    composed['inputs']['recorded_mixed_resume_protocol_sha256'] = sha(out / 'protocol.json')
    (out / 'precutoff_feature_view.json.gz').write_bytes(gzip.compress(json_bytes(composed), mtime=0))
    write(work / 'native_cursors.json', cursors)
    available = sum(r['features'] is not None for r in composed['rows'])
    result = dict(status='passed', selected=len(records), finalized=len(entries),
        new_complete_source_ids=complete, new_complete_prefixes=len(complete),
        bounded_in_scope=len(entries)-len(complete), pending_in_scope=len(records)-len(entries),
        available_coldcard_vectors=available, preserved_old_vectors=q['baseline_vectors'],
        fresh_native_source_transaction_observations=sum(d['fresh_native_source_transaction_observations'] for d in details),
        source_progress=details, private_native_cursors_sha256=sha(work / 'native_cursors.json'),
        composed_view_sha256=sha(out / 'precutoff_feature_view.json.gz'),
        unknown_labels_cutoffs_and_current_statuses_unchanged=True,
        successful_fresh_requests=sum(m.get('http_status') == 200 for m in manifest),
        failed_request_records=len(failures), model_fits=0, new_scores=0)
    write(out / 'coverage_audit.json', result)
    write(out / 'independent_verification.json', dict(result,
        verification_basis='Pinned mixed seeds; actual-native endpoint replay; unchanged saved union; exhausted funding closure; separate feature recount; old-row and recorded-clock invariants'))
    return result
