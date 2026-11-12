"""Join independent address indexes by a complete-block overlap, not a partial block cursor."""
import argparse
import gzip
from pathlib import Path

import independent_mempool_pilot as original
from independent_mempool_pilot import core, legacy_source, require, status_check
from build_source_registry import json_bytes


def choose_bridge(record, anchor, transactions):
    boundary_height = min(t['status']['block_height'] for t in transactions)
    require(boundary_height < record['cutoff_height'], 'Pilot requires a prior-block boundary')
    newer = [t for t in transactions if t['status']['block_height'] > boundary_height]
    bridge = newer[-1] if newer else anchor
    require(bridge['status']['block_height'] > boundary_height, 'Bridge does not precede the partial boundary block')
    return bridge, boundary_height


def merge_transaction(record, tx, existing, fresh_seen, boundary_height):
    require(tx['txid'] not in fresh_seen and tx['txid'] != record['payment_txid'], 'Repeated provider-native cursor transaction')
    fresh_seen.add(tx['txid'])
    require(any(o.get('scriptpubkey_address') == record['address'] for o in tx['vout']) or
        any((v.get('prevout') or {}).get('scriptpubkey_address') == record['address'] for v in tx['vin']),
        'Unrelated independent history transaction')
    if tx['txid'] in existing:
        require(core(existing[tx['txid']]) == core(tx), 'Conflicting cross-provider overlap')
        return False
    require(tx['status']['block_height'] <= boundary_height, 'Unknown transaction in a previously complete newer block')
    existing[tx['txid']] = tx
    return True


def collect(record, requests, work, q, legacy_pins):
    anchor, legacy_pages, old, _ = legacy_source(record, work, legacy_pins)
    bridge, boundary_height = choose_bridge(record, anchor, old)
    status_check(record, requests.get(record, 'reference_before', '/tx/' + record['payment_txid'] + '/status'))
    boundary = requests.get(record, 'boundary', '/tx/' + bridge['txid'])
    require(core(boundary) == core(bridge), 'Independent bridge transaction differs')
    existing = {t['txid']: t for t in old}
    fresh_seen = {bridge['txid']}; cursor = bridge['txid']; previous = bridge['status']['block_height']
    added, overlap, exhausted, pages = [], 0, False, 0
    for i in range(q['new_provider_page_limit']):
        page = requests.get(record, f'native_tail_{i:04d}', '/address/' + record['address'] + '/txs/chain/' + cursor)
        require(isinstance(page, list) and len(page) <= 25, 'Invalid independent page')
        pages += 1
        if not page:
            exhausted = True
            break
        for tx in page:
            require(tx['status'].get('confirmed') is True and tx['status'].get('block_hash') and
                tx['status']['block_height'] <= previous, 'Unanchored independent page order')
            previous = tx['status']['block_height']
            if merge_transaction(record, tx, existing, fresh_seen, boundary_height):
                added.append(tx)
            else:
                overlap += 1
        cursor = page[-1]['txid']
    after = requests.get(record, 'reference_after', '/tx/' + record['payment_txid'] + '/status')
    status_check(record, after)
    transactions = sorted(existing.values(), key=lambda t: (-t['status']['block_height'], t['txid']))
    result = original.tail.tail_check(record, anchor, transactions, exhausted, after, {})
    raw = dict(address=record['address'], anchor=anchor, transactions=transactions, anchor_after=after,
        parent_statuses={}, pagination_exhausted=exhausted, pages_fetched=len(legacy_pages) + pages,
        legacy_provider_pages=len(legacy_pages), independent_provider_pages=pages,
        bridge_txid=bridge['txid'], bridge_height=bridge['status']['block_height'],
        partial_boundary_height=boundary_height, cross_provider_overlap_verified=overlap,
        distinct_transactions=len(transactions),
        mixed_provider_provenance=dict(saved_prefix_provider='https://blockstream.info/api',
            fresh_provider=original.PROVIDER, method='rewind above partial block; native cursor walk; immutable overlap equality; TXID union'),
        additional_source_transaction_observations=sum(t['status']['block_height'] < record['cutoff_height'] for t in added))
    raw_path = work / 'raw' / (record['pilot_id'] + '.json.gz')
    raw_path.write_bytes(gzip.compress(json_bytes(raw), mtime=0))
    entry = dict(source_id=record['pilot_id'], cutoff_height=record['cutoff_height'],
        raw_file='raw/' + raw_path.name, raw_sha256=original.sha(raw_path), **result)
    (work / 'results' / (record['pilot_id'] + '.json.gz')).write_bytes(gzip.compress(json_bytes(entry), mtime=0))
    return entry


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('protocol', type=Path); parser.add_argument('work', type=Path)
    args = parser.parse_args()
    original.collect = collect
    original.run(args.protocol.resolve(), args.work.resolve())
