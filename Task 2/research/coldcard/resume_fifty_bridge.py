"""Extend the verified mixed-provider seed using its actual saved native cursor."""
import argparse
import gzip
import hashlib
from pathlib import Path

from build_source_registry import json_bytes
from prepare_frontier_checkpoint import read, sha
from source_cohort import atomic_write
import independent_mempool_resume as native
from independent_mempool_native import validate_page
from independent_mempool_pilot import require, status_check, PROVIDER
from resume_mempool_slow_response import SlowResponseHTTP


def seed(record, work, q):
    spec = read(work / 'bridge_seed.json')
    require(sha(work / 'bridge_seed.json') == q['private_bridge_seed_sha256'], 'Bridge seed specification changed')
    require(sha(work / spec['raw_file']) == spec['raw_sha256'], 'Saved bridge raw fingerprint differs')
    raw = read(work / spec['raw_file'])
    require(hashlib.sha256(spec['native_cursor'].encode()).hexdigest() == q['native_start_cursor_sha256'], 'Actual native cursor differs')
    native.tail.anchor_check(record, raw['anchor'])
    values = raw['transactions']; seen = {record['payment_txid']}; height = record['cutoff_height']
    for offset in range(0, len(values), 25):
        height = validate_page(record, values[offset:offset+25], seen, height)
    point = next(t for t in values if t['txid'] == spec['native_cursor'])
    require(raw['pagination_exhausted'] is False and point['status']['block_height'] == height and
            raw['partial_boundary_height'] > height, 'Saved native frontier does not separate the legacy boundary')
    return spec, raw, list(values), seen, height


def collect(record, requests, work, q, unused_pins):
    spec, old, values, seen, height = seed(record, work, q); cursor = spec['native_cursor']; old_count = len(values)
    status_check(record, requests.get(record, 'reference_before', '/tx/' + record['payment_txid'] + '/status'))
    exhausted = False; pages = 0
    for i in range(q['maximum_new_native_pages']):
        page = requests.get(record, f'extension_{i:04d}', '/address/' + record['address'] + '/txs/chain/' + cursor)
        height = validate_page(record, page, seen, height); pages += 1
        if not page:
            exhausted = True; break
        values.extend(page); cursor = page[-1]['txid']
    after = requests.get(record, 'reference_after', '/tx/' + record['payment_txid'] + '/status')
    status_check(record, after); own = native.tail.anchor_check(record, old['anchor']); parents = {}
    if exhausted:
        ids = {t['txid'] for t in values}
        for vin in own:
            if vin['txid'] not in ids and vin['txid'] not in parents:
                status = requests.get(record, 'parent_' + hashlib.sha256(vin['txid'].encode()).hexdigest(), '/tx/' + vin['txid'] + '/status')
                status_check(record, status); parents[vin['txid']] = status
    result = native.tail.tail_check(record, old['anchor'], values, exhausted, after, parents)
    if result['features'] is not None:
        result['audit'].update(provider=PROVIDER, completeness_basis='Verified mixed seed plus exhausted actual native-cursor continuation')
    raw = dict(address=record['address'], anchor=old['anchor'], transactions=values, anchor_after=after,
        parent_statuses=parents, pagination_exhausted=exhausted, pages_fetched=old['pages_fetched']+pages,
        seed_kind='bridge_union', seed_raw_sha256=spec['raw_sha256'], seed_transactions=old_count,
        partial_boundary_height=old['partial_boundary_height'], legacy_provider_pages=old['legacy_provider_pages'],
        independent_provider_pages=old['independent_provider_pages']+pages, new_native_pages=pages,
        actual_native_last_cursor=cursor, native_continuation_start_cursor=spec['native_cursor'],
        page_count_semantics='Mixed saved evidence plus fresh native pages; not one provider serial-pagination count')
    path = work / 'raw' / (record['pilot_id'] + '.json.gz'); atomic_write(path, gzip.compress(json_bytes(raw), mtime=0))
    entry = dict(source_id=record['pilot_id'], address_sha256=record['address_sha256'], payment_txid_sha256=record['payment_txid_sha256'],
        cutoff_height=record['cutoff_height'], cutoff_block_hash=record['cutoff_block_hash'],
        raw_file='raw/' + path.name, raw_sha256=sha(path), pages_fetched=raw['pages_fetched'], **result)
    atomic_write(work / 'results' / (record['pilot_id'] + '.json.gz'), gzip.compress(json_bytes(entry), mtime=0))
    return entry


def run(protocol, work):
    q = read(protocol); records = read(work / 'plan.json')
    require(len(records) == 1 and records[0]['pilot_id'] == 'comparison_0351' and q['maximum_new_native_pages'] == 16,
            'Unexpected bridge scope')
    seed(records[0], work, q)
    native.collect = collect; SlowResponseHTTP.response_timeout_seconds = q['timeout_seconds']; native.MempoolHTTP = SlowResponseHTTP
    native.run(protocol, work)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('protocol', type=Path); p.add_argument('work', type=Path)
    a = p.parse_args(); run(a.protocol.resolve(), a.work.resolve())
