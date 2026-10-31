"""Pilot and bounded collection of confirmed history before a frozen payment.

This is a different coverage scope from a full-current-history counter audit.
Only an exhausted, anchored cursor tail may yield pre-cutoff predictors. The
full-history status of the baseline is never promoted by this collector.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import fcntl
import gzip
import json
from pathlib import Path
from threading import Event
import time

from build_source_registry import digest, json_bytes
from collect_comparison_coverage import Pages
from comparison_http import PersistentHTTP
import prepayment_pilot as fixed
from source_cohort import atomic_write


def now():
    return datetime.now(timezone.utc).isoformat()


def anchor_check(record, anchor):
    if anchor['txid'] != record['payment_txid']:
        raise ValueError('Reference transaction identity mismatch')
    status = anchor['status']
    if (status.get('confirmed') is not True or
            status['block_height'] != record['cutoff_height'] or
            status['block_hash'] != record['cutoff_block_hash']):
        raise ValueError('Reference confirmation anchor mismatch')
    own = [v for v in anchor['vin']
           if (v.get('prevout') or {}).get('scriptpubkey_address') == record['address']]
    if (len(own) != record['registry_input_slots'] or
            sum(v['prevout']['value'] for v in own) != record['reference_input_value_sat']):
        raise ValueError('Frozen reference input count/value mismatch')
    return own


def tail_check(record, anchor, transactions, exhausted, anchor_after, parent_statuses):
    own = anchor_check(record, anchor)
    if any(anchor_after.get(k) != anchor['status'].get(k)
           for k in ('confirmed', 'block_height', 'block_hash')):
        raise ValueError('Reference anchor changed during collection')
    ids, previous_height = set(), record['cutoff_height']
    by_id = {}
    for tx in transactions:
        status = tx['status']
        if status.get('confirmed') is not True or not status.get('block_hash'):
            raise ValueError('Unconfirmed or unanchored transaction in confirmed tail')
        if tx['txid'] in ids or tx['txid'] == record['payment_txid']:
            raise ValueError('Repeated cursor transaction')
        if status['block_height'] > previous_height:
            raise ValueError('Tail is not reverse-height ordered')
        previous_height = status['block_height']
        ids.add(tx['txid'])
        by_id[tx['txid']] = tx
    if not exhausted:
        return dict(status='bounded_incomplete', features=None, prefix=None,
                    reason='No empty terminal page within the recorded bound')
    # Every reference input funding transaction must be in the exhausted tail,
    # or explicitly confirmed in the excluded reference block. An empty result
    # from a missing cursor cannot silently manufacture an empty prior history.
    for vin in own:
        parent = by_id.get(vin['txid'])
        if parent is not None:
            output = parent['vout'][vin['vout']]
            if (output.get('scriptpubkey_address') != record['address'] or
                    output['value'] != vin['prevout']['value']):
                raise ValueError('Reference funding output mismatch')
        else:
            status = parent_statuses.get(vin['txid'], {})
            if (status.get('confirmed') is not True or
                    status.get('block_height') != record['cutoff_height'] or
                    status.get('block_hash') != record['cutoff_block_hash']):
                raise ValueError('Prior reference funding transaction absent from tail')
    prefix = fixed.normalize_prefix(record['address'], transactions, record['cutoff_height'])
    features = fixed.features(prefix, record['cutoff_height'])
    return dict(status='complete_prior_prefix', features=features, prefix=prefix,
                audit=dict(scope='confirmed heights strictly below the frozen payment block',
                    reference_anchor_verified=True, reference_funding_closure_verified=True,
                    reverse_height_order_verified=True, pagination_exhausted=True,
                    completeness_basis='Original-provider indexed cursor contract; exhausted anchored tail',
                    full_history_counter_coverage_verified=False,
                    cryptographic_inclusion_verified=False))


def collect_one(record, pages, work, max_pages):
    key = record['pilot_id']
    result = work/'results'/(key+'.json.gz')
    if result.exists():
        return json.loads(gzip.decompress(result.read_bytes()))
    anchor = pages.get(record, 'reference', '/tx/'+record['payment_txid'])
    own = anchor_check(record, anchor)
    cursor, transactions, exhausted = record['payment_txid'], [], False
    for index in range(max_pages):
        page = pages.get(record, 'tail_%04d' % index,
            '/address/'+record['address']+'/txs/chain/'+cursor)
        if not isinstance(page, list) or len(page) > 25:
            raise ValueError('Invalid cursor page')
        if not page:
            exhausted = True
            break
        transactions.extend(page)
        cursor = page[-1]['txid']
    after = pages.get(record, 'reference_after', '/tx/'+record['payment_txid']+'/status')
    parents = {}
    if exhausted:
        seen = {t['txid'] for t in transactions}
        for vin in own:
            if vin['txid'] not in seen and vin['txid'] not in parents:
                parents[vin['txid']] = pages.get(record, 'parent_'+digest(vin['txid'].encode()),
                                                '/tx/'+vin['txid']+'/status')
    normalized = tail_check(record, anchor, transactions, exhausted, after, parents)
    raw = gzip.compress(json_bytes(dict(address=record['address'], anchor=anchor,
        transactions=transactions, anchor_after=after, parent_statuses=parents,
        pagination_exhausted=exhausted, pages_fetched=index+1,
        collected_at=now())), mtime=0)
    atomic_write(work/'raw'/(key+'.json.gz'), raw)
    entry = dict(source_id=key, address_sha256=record['address_sha256'],
        payment_txid_sha256=record['payment_txid_sha256'], cutoff_height=record['cutoff_height'],
        cutoff_block_hash=record['cutoff_block_hash'], raw_file='raw/'+key+'.json.gz',
        raw_sha256=digest(raw), pages_fetched=index+1, **normalized)
    atomic_write(result, gzip.compress(json_bytes(entry), mtime=0))
    return entry


def guarded(record, pages, work, max_pages):
    try:
        return collect_one(record, pages, work, max_pages)
    except Exception:
        pages.stop.set()
        raise


def export(protocol_path, output, work):
    proto = json.loads(protocol_path.read_bytes())
    entries = {}
    for key in proto['source_ids']:
        file = work/'results'/(key+'.json.gz')
        if file.exists():
            entries[key] = json.loads(gzip.decompress(file.read_bytes()))
    output.mkdir(parents=True, exist_ok=True)
    requests = [json.loads(f.read_bytes()) for f in sorted((work/'requests').glob('*/*.json'))]
    atomic_write(output/'checkpoint.json.gz', gzip.compress(json_bytes(dict(
        protocol_sha256=digest(protocol_path.read_bytes()), entries=entries)), mtime=0))
    atomic_write(output/'request_manifest.json.gz', gzip.compress(json_bytes(requests), mtime=0))
    summary = dict(selected=len(proto['source_ids']), attempted=len(entries),
        complete_prior_prefix=sum(e['status']=='complete_prior_prefix' for e in entries.values()),
        bounded_incomplete=sum(e['status']=='bounded_incomplete' for e in entries.values()),
        pending=len(proto['source_ids'])-len(entries), requests_started=len(requests),
        failed_requests=[r for r in requests if 'error_type' in r],
        full_history_status_not_promoted=True, training_performed=False)
    atomic_write(output/'progress.json', json_bytes(summary))
    return summary


def run(q, output, work):
    proto = json.loads(q.read_bytes())
    for pin in proto['inputs'].values():
        if digest((q.parent/pin['file']).read_bytes()) != pin['sha256']:
            raise ValueError('Pinned input changed')
    records = json.loads((work/'plan.json').read_bytes())
    if digest(json_bytes(records)) != proto['private_plan_sha256']:
        raise ValueError('Private plan fingerprint mismatch')
    if [r['pilot_id'] for r in records] != proto['source_ids']:
        raise ValueError('Frozen source order changed')
    stop = Event()
    with (work/'collector.lock').open('a+') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        print('LOCK_HELD_READY', flush=True)
        deadline = time.monotonic()+300
        while not (work/'lease_published').exists():
            if time.monotonic() > deadline:
                raise RuntimeError('Lease publication not confirmed; no HTTP')
            time.sleep(.25)
        with PersistentHTTP(1) as http:
            pages = Pages(work, http, stop)
            try:
                if proto.get('preflight_source'):
                    check = json.loads((work/'preflight.json').read_bytes())
                    data = pages.get(check, 'availability_counter', '/address/'+check['address'])
                    if data.get('address') != check['address']:
                        raise ValueError('Access-check address mismatch')
                    print('NORMAL_COUNTER_HTTP_200', flush=True)
                for offset in range(0, len(records), 20):
                    with ThreadPoolExecutor(max_workers=2) as pool:
                        futures = [pool.submit(guarded, r, pages, work, proto['max_pages_per_address'])
                                   for r in records[offset:offset+20]]
                        for future in as_completed(futures):
                            e = future.result()
                            print(e['source_id']+': '+e['status'], flush=True)
                    print('BATCH '+json.dumps(export(q, output, work)), flush=True)
            except Exception as error:
                stop.set()
                print('STOPPED '+type(error).__name__+': '+str(error), flush=True)
            finally:
                print('FINAL '+json.dumps(export(q, output, work)), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('protocol', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('work', type=Path)
    args = parser.parse_args()
    run(args.protocol, args.output, args.work)
