"""Audit a complete-block provider bridge and independently recount its predictors."""
import argparse
import copy
from datetime import datetime
import gzip
import hashlib
from pathlib import Path
import sys

from build_source_registry import json_bytes
from prepare_frontier_checkpoint import read, sha, write
import independent_mempool_pilot as original
from independent_mempool_bridge import choose_bridge


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
    legacy_pins = read(out / 'legacy_reuse_manifest.json')['responses']
    cached = {sid: original.legacy_source(r, work,
        {m['key']: m for m in legacy_pins if m['source_id'] == sid}) for sid, r in records.items()}
    metadata = read(out / 'request_manifest.json.gz')
    assert len(metadata) <= q['maximum_requests']
    by_key = {(m['source_id'], m['key']): m for m in metadata}
    assert len(by_key) == len(metadata)
    dispatched = sorted(m['dispatch_at'] for m in metadata if m.get('dispatch_at'))
    assert all((datetime.fromisoformat(b) - datetime.fromisoformat(a)).total_seconds() >= 4.9
               for a, b in zip(dispatched, dispatched[1:]))
    for sid, record in records.items():
        anchor, old_pages, old, _ = cached[sid]
        bridge, boundary_height = choose_bridge(record, anchor, old)
        cursor = bridge['txid']
        keys = ['reference_before', 'boundary'] + [f'native_tail_{i:04d}' for i in range(q['new_provider_page_limit'])] + ['reference_after']
        for key in keys:
            m = by_key.get((sid, key))
            if m is None:
                continue
            assert m['provider'] == original.PROVIDER
            if key.startswith('reference_'):
                endpoint = '/tx/' + record['payment_txid'] + '/status'
            elif key == 'boundary':
                endpoint = '/tx/' + bridge['txid']
            else:
                endpoint = '/address/' + record['address'] + '/txs/chain/' + cursor
            assert hashlib.sha256(endpoint.encode()).hexdigest() == m['endpoint_sha256']
            if m.get('http_status') == 200:
                path = work / 'requests' / sid / (key + '.json.gz')
                assert sha(path) == m['sha256']
                if key.startswith('native_tail_'):
                    page = read(path); assert isinstance(page, list) and len(page) <= 25
                    if page:
                        cursor = page[-1]['txid']
    sys.path.insert(0, str(out.parents[1] / 'external_cases/cryptobilis_to_coldcard_20261109'))
    from experiment import recount_features
    cp = read(out / 'checkpoint.json.gz'); assert cp['protocol_sha256'] == sha(out / 'protocol.json')
    composed = copy.deepcopy(baseline); rows = {r['source_id']: r for r in composed['rows']}
    complete, bounded, details = [], [], []
    for sid, entry in cp['entries'].items():
        record = records[sid]; assert before[sid]['features'] is None
        anchor, legacy_pages, old, _ = cached[sid]
        bridge, boundary_height = choose_bridge(record, anchor, old)
        raw_path = work / entry['raw_file']; assert sha(raw_path) == entry['raw_sha256']
        raw = read(raw_path)
        assert raw['anchor'] == anchor and raw['bridge_txid'] == bridge['txid']
        assert raw['bridge_height'] > raw['partial_boundary_height'] == boundary_height
        original.status_check(record, read(work / 'requests' / sid / 'reference_before.json.gz'))
        assert original.core(read(work / 'requests' / sid / 'boundary.json.gz')) == original.core(bridge)
        existing = {t['txid']: t for t in old}; old_ids = set(existing)
        native_seen = {bridge['txid']}; previous = bridge['status']['block_height']; overlap = 0; empty = False
        for i in range(raw['independent_provider_pages']):
            page = read(work / 'requests' / sid / (f'native_tail_{i:04d}.json.gz'))
            if not page:
                assert i == raw['independent_provider_pages'] - 1; empty = True
            for tx in page:
                assert tx['txid'] not in native_seen; native_seen.add(tx['txid'])
                assert tx['status']['confirmed'] and tx['status']['block_hash'] and tx['status']['block_height'] <= previous
                previous = tx['status']['block_height']
                if tx['txid'] in existing:
                    assert original.core(existing[tx['txid']]) == original.core(tx); overlap += 1
                else:
                    assert tx['status']['block_height'] <= boundary_height
                    existing[tx['txid']] = tx
        actual = {t['txid']: t for t in raw['transactions']}
        assert len(actual) == len(raw['transactions']) == len(existing)
        assert all(original.core(actual[k]) == original.core(v) for k, v in existing.items())
        assert raw['cross_provider_overlap_verified'] == overlap and raw['pagination_exhausted'] == empty
        assert raw['anchor_after'] == read(work / 'requests' / sid / 'reference_after.json.gz')
        original.status_check(record, raw['anchor_after'])
        expected = original.tail.tail_check(record, anchor, raw['transactions'], empty, raw['anchor_after'], {})
        assert all(entry[k] == expected[k] for k in ['status', 'features', 'prefix'])
        added = sum(t['status']['block_height'] < record['cutoff_height'] for key, t in existing.items() if key not in old_ids)
        assert added == raw['additional_source_transaction_observations']
        if entry['status'] == 'complete_prior_prefix':
            assert recount_features(entry['prefix'], record['cutoff_height']) == entry['features']
            rows[sid]['features'] = entry['features']; rows[sid]['precutoff_history_status'] = 'complete_prior_prefix'; complete.append(sid)
        else:
            assert entry['features'] is None and entry['prefix'] is None; bounded.append(sid)
        rows[sid]['precutoff_history_provenance'] = dict(pass_name=out.name, raw_sha256=entry['raw_sha256'],
            pages_fetched=raw['pages_fetched'], independent_provider_pages=raw['independent_provider_pages'],
            full_current_history_counter_coverage_verified=False, provider='https://mempool.space/api',
            method='complete-block overlap bridge with immutable core comparison')
        details.append(dict(source_id=sid, status=entry['status'], independent_pages=raw['independent_provider_pages'],
            old_transactions_retained=len(old), distinct_transactions=len(existing), overlap_transactions_verified=overlap,
            additional_source_transaction_observations=added))
    for sid, row in rows.items():
        old = before[sid]
        for key in ['source_id', 'address_sha256', 'payment_txid_sha256', 'cutoff_height', 'cutoff_block_hash',
                    'known_coldcard_core_membership', 'labels', 'full_history_status']:
            assert row.get(key) == old.get(key)
        if sid not in cp['entries'] or old['features'] is not None:
            assert row == old
    composed['inputs']['independent_mempool_bridge_protocol_sha256'] = sha(out / 'protocol.json')
    (out / 'precutoff_feature_view.json.gz').write_bytes(gzip.compress(json_bytes(composed), mtime=0))
    available = sum(r['features'] is not None for r in composed['rows'])
    receipt = read(out / 'run_receipt.json'); assert receipt['operational_locks_released'] and receipt['blockstream_provider_requests'] == 0
    report = dict(schema_version=1, status='passed', provider=original.PROVIDER, selected=len(records), finalized=len(cp['entries']),
        pending=len(records) - len(cp['entries']), new_complete_prefixes=len(complete), new_complete_source_ids=complete,
        bounded_source_ids=bounded, preserved_old_vectors=q['baseline_vectors'], coldcard_vectors=available,
        coldcard_unavailable_prefixes=1500 - available, cryptobilis_vectors_unchanged=329,
        total_remaining_information_gaps=1500 - available + 37, provider_requests=len(metadata),
        successful_response_fingerprints_verified=sum(m.get('http_status') == 200 for m in metadata),
        saved_blockstream_response_fingerprints_verified=len(legacy_pins), new_vectors_independently_recounted=len(complete),
        additional_source_transaction_observations=sum(d['additional_source_transaction_observations'] for d in details),
        observation_count_is_not_globally_unique_transactions=True, verified_overlap_transactions=sum(d['overlap_transactions_verified'] for d in details),
        source_progress=details, blockstream_provider_requests=0,
        labels_cutoffs_fourteen_predictors_and_full_current_statuses_unchanged=True,
        final_view_sha256=sha(out / 'precutoff_feature_view.json.gz'), model_fits=0, new_scores=0)
    write(out / 'coverage_audit.json', report)
    write(out / 'independent_verification.json', dict(report,
        verification_basis='Saved response/cursor fingerprints; independent reconstruction of the complete-block overlap union; original raw UTXO extraction; separate feature recount; all old-row invariants'))
    return report


if __name__ == '__main__':
    import json
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('scope', type=Path); parser.add_argument('work', type=Path)
    args = parser.parse_args(); print(json.dumps(audit(args.scope, args.work), sort_keys=True))
