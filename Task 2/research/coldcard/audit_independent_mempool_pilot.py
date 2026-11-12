"""Verify independent-provider responses, cached evidence, and unchanged predictors."""
import argparse
import copy
import gzip
import hashlib
from pathlib import Path
import sys

from build_source_registry import json_bytes
from prepare_frontier_checkpoint import read, sha, write
import independent_mempool_pilot as pilot


def audit(out, work):
    out, work = out.resolve(), work.resolve()
    assert not (out / 'coverage_audit.json').exists()
    q = read(out / 'protocol.json')
    for pin in q['inputs'].values():
        assert sha((out / pin['file']).resolve()) == pin['sha256']
    baseline = read((out / q['inputs']['baseline_view']['file']).resolve())
    before = {r['source_id']: r for r in baseline['rows']}
    assert sum(r['features'] is not None for r in baseline['rows']) == q['baseline_vectors']
    records = {r['pilot_id']: r for r in read(work / 'plan.json')}
    assert list(records) == q['source_ids'] and sha(work / 'plan.json') == q['private_plan_sha256']
    pins = read(out / 'legacy_reuse_manifest.json')['responses']
    cached = {sid: pilot.legacy_source(r, work,
        {m['key']: m for m in pins if m['source_id'] == sid}) for sid, r in records.items()}
    checkpoint = read(out / 'checkpoint.json.gz')
    assert checkpoint['protocol_sha256'] == sha(out / 'protocol.json')
    metadata = read(out / 'request_manifest.json.gz')
    assert len(metadata) <= q['maximum_requests']
    assert len({(m['source_id'], m['key']) for m in metadata}) == len(metadata)
    dispatched = sorted(m['dispatch_at'] for m in metadata if m.get('dispatch_at'))
    from datetime import datetime
    assert all((datetime.fromisoformat(b) - datetime.fromisoformat(a)).total_seconds() >= 4.9
        for a, b in zip(dispatched, dispatched[1:]))
    for m in metadata:
        assert m['provider'] == pilot.PROVIDER and m['source_id'] in records
        r = records[m['source_id']]
        key = m['key']
        by_key = {p['key']: p for p in pins if p['source_id'] == m['source_id']}
        _, old_pages, old_txs, cursor = cached[r['pilot_id']]
        if key.startswith('reference_'):
            endpoint = '/tx/' + r['payment_txid'] + '/status'
        elif key == 'boundary':
            endpoint = '/tx/' + cursor
        else:
            assert key.startswith('tail_')
            index = int(key[5:]); start = len(old_pages) - int(not old_pages[-1])
            for i in range(start, index):
                page = read(work / 'requests' / r['pilot_id'] / (f'tail_{i:04d}.json.gz'))
                assert page
                cursor = page[-1]['txid']
            endpoint = '/address/' + r['address'] + '/txs/chain/' + cursor
        assert hashlib.sha256(endpoint.encode()).hexdigest() == m['endpoint_sha256']
        if m.get('http_status') == 200:
            assert sha(work / 'requests' / r['pilot_id'] / (key + '.json.gz')) == m['sha256']
    sys.path.insert(0, str(out.parents[1] / 'external_cases/cryptobilis_to_coldcard_20261109'))
    from experiment import recount_features
    composed = copy.deepcopy(baseline); rows = {r['source_id']: r for r in composed['rows']}
    complete, bounded, observations = [], [], 0
    for sid, e in checkpoint['entries'].items():
        r = records[sid]; assert before[sid]['features'] is None
        by_key = {p['key']: p for p in pins if p['source_id'] == sid}
        anchor, pages, old_txs, cursor = cached[sid]
        raw_path = work / e['raw_file']; assert sha(raw_path) == e['raw_sha256']
        raw = read(raw_path)
        assert raw['anchor'] == anchor and raw['transactions'][:len(old_txs)] == old_txs
        assembled = list(old_txs); exhausted = False
        start = len(pages) - int(not pages[-1])
        for i in range(start, raw['pages_fetched']):
            page = read(work / 'requests' / sid / (f'tail_{i:04d}.json.gz'))
            assert isinstance(page, list) and len(page) <= 25
            if not page:
                assert i == raw['pages_fetched'] - 1
                exhausted = True
            assembled.extend(page)
        assert raw['transactions'] == assembled and raw['pagination_exhausted'] == exhausted
        assert raw['anchor_after'] == read(work / 'requests' / sid / 'reference_after.json.gz')
        boundary = read(work / 'requests' / sid / 'boundary.json.gz')
        assert pilot.core(boundary) == pilot.core(old_txs[-1])
        pilot.status_check(r, read(work / 'requests' / sid / 'reference_before.json.gz'))
        pilot.status_check(r, raw['anchor_after'])
        expected = pilot.tail.tail_check(r, anchor, raw['transactions'], raw['pagination_exhausted'], raw['anchor_after'], {})
        assert all(e[k] == expected[k] for k in ['status', 'features', 'prefix'])
        fresh_txs = raw['transactions'][len(old_txs):]
        added = sum(t['status']['block_height'] < r['cutoff_height'] for t in fresh_txs)
        assert added == raw['additional_source_transaction_observations']; observations += added
        if e['status'] == 'complete_prior_prefix':
            assert recount_features(e['prefix'], r['cutoff_height']) == e['features']
            rows[sid]['features'] = e['features']; rows[sid]['precutoff_history_status'] = 'complete_prior_prefix'; complete.append(sid)
        else:
            assert e['features'] is None and e['prefix'] is None; bounded.append(sid)
        rows[sid]['precutoff_history_provenance'] = dict(pass_name=out.name, raw_sha256=e['raw_sha256'],
            pages_fetched=raw['pages_fetched'], full_current_history_counter_coverage_verified=False,
            provider_comparison='saved Blockstream prefix plus independently checked Mempool boundary, continuation and fresh statuses')
    for sid, row in rows.items():
        old = before[sid]
        for key in ['source_id', 'address_sha256', 'payment_txid_sha256', 'cutoff_height', 'cutoff_block_hash',
                    'known_coldcard_core_membership', 'labels', 'full_history_status']:
            assert row.get(key) == old.get(key)
        if sid not in checkpoint['entries'] or old['features'] is not None:
            assert row == old
    composed['inputs']['independent_mempool_protocol_sha256'] = sha(out / 'protocol.json')
    (out / 'precutoff_feature_view.json.gz').write_bytes(gzip.compress(json_bytes(composed), mtime=0))
    available = sum(r['features'] is not None for r in composed['rows'])
    receipt = read(out / 'run_receipt.json')
    assert receipt['operational_locks_released'] and receipt['blockstream_provider_requests'] == 0
    report = dict(schema_version=1, status='passed', provider=pilot.PROVIDER, selected=len(records),
        finalized=len(checkpoint['entries']), pending=len(records) - len(checkpoint['entries']),
        new_complete_prefixes=len(complete), new_complete_source_ids=complete, bounded_source_ids=bounded,
        preserved_old_vectors=q['baseline_vectors'], coldcard_vectors=available, coldcard_unavailable_prefixes=1500 - available,
        cryptobilis_vectors_unchanged=329, total_remaining_information_gaps=1500 - available + 37,
        successful_response_fingerprints_verified=sum(m.get('http_status') == 200 for m in metadata),
        saved_blockstream_response_fingerprints_verified=len(pins), provider_requests=len(metadata),
        new_vectors_independently_recounted=len(complete), additional_source_transaction_observations=observations,
        observation_count_is_not_globally_unique_transactions=True, blockstream_provider_requests=0,
        labels_cutoffs_fourteen_predictors_and_full_current_statuses_unchanged=True,
        raw_tails_reextracted=len(checkpoint['entries']), final_view_sha256=sha(out / 'precutoff_feature_view.json.gz'),
        model_fits=0, new_scores=0)
    write(out / 'coverage_audit.json', report)
    write(out / 'independent_verification.json', dict(report,
        verification_basis='Response fingerprints/cursors, independent boundary comparison, original raw re-extraction, separate feature recount, complete old-row preservation'))
    return report


if __name__ == '__main__':
    import json
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('scope', type=Path); p.add_argument('work', type=Path)
    args = p.parse_args(); print(json.dumps(audit(args.scope, args.work), sort_keys=True))
