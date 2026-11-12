"""Resume a verified native-Mempool prefix in a distinct finite acquisition scope."""
import argparse
from contextlib import ExitStack
from datetime import datetime, timezone
import fcntl
import gzip
import hashlib
from pathlib import Path
import signal
import time

from build_source_registry import json_bytes
from prepare_frontier_checkpoint import read, sha, write
from source_cohort import atomic_write
import collect_reference_tail as tail
from independent_mempool_pilot import MempoolHTTP, Requests, PROVIDER, require, status_check
from independent_mempool_native import validate_page, check_lease


def cached_prefix(record, work, pins):
    """Use only verified successful reference/tail responses, never failure/intent flags."""
    if not pins:
        return None, [], record['payment_txid'], {record['payment_txid']}, record['cutoff_height'], False
    folder = work / 'requests' / record['pilot_id']
    by_key = {p['key']: p for p in pins}
    require(len(by_key) == len(pins) and 'reference' in by_key, 'Invalid reuse manifest')
    require(set(by_key) == {'reference'} | {f'tail_{i:04d}' for i in range(len(pins) - 1)}, 'Cached page gap')
    def response(key, endpoint):
        pin = by_key[key]; marker = read(folder / (key + '.json')); body = folder / (key + '.json.gz')
        require(marker.get('http_status') == 200 and 'error_type' not in marker and marker.get('offline_reused') is True,
                'Unsuccessful or consumed original intent cannot be reused')
        require(marker.get('provider') == PROVIDER and marker['endpoint_sha256'] == pin['endpoint_sha256'] ==
                hashlib.sha256(endpoint.encode()).hexdigest(), 'Cached native endpoint differs')
        require(sha(body) == pin['sha256'] == marker['sha256'], 'Cached native body differs')
        return read(body)
    anchor = response('reference', '/tx/' + record['payment_txid']); tail.anchor_check(record, anchor)
    pages, cursor, seen, previous, terminal = [], record['payment_txid'], {record['payment_txid']}, record['cutoff_height'], False
    for i in range(len(pins) - 1):
        require(not terminal, 'Cached page follows terminal page')
        page = response(f'tail_{i:04d}', '/address/' + record['address'] + '/txs/chain/' + cursor)
        previous = validate_page(record, page, seen, previous)
        pages.append(page); terminal = not page
        if page:
            cursor = page[-1]['txid']
    return anchor, pages, cursor, seen, previous, terminal


class GuardedRequests(Requests):
    def __init__(self, work, http, maximum, guard):
        super().__init__(work, http, maximum); self.guard = guard

    def get(self, record, key, endpoint):
        self.guard()
        return super().get(record, key, endpoint)


def collect(record, requests, work, q, pins):
    anchor, saved, cursor, seen, previous, exhausted = cached_prefix(record, work, pins)
    old_pages = len(saved); transactions = [tx for page in saved for tx in page]
    if anchor is None:
        anchor = requests.get(record, 'reference', '/tx/' + record['payment_txid'])
        tail.anchor_check(record, anchor)
    else:
        status_check(record, requests.get(record, 'reference_before', '/tx/' + record['payment_txid'] + '/status'))
    own = tail.anchor_check(record, anchor); total_pages = old_pages
    if not exhausted:
        for i in range(old_pages, q['max_pages_per_address']):
            page = requests.get(record, f'tail_{i:04d}', '/address/' + record['address'] + '/txs/chain/' + cursor)
            previous = validate_page(record, page, seen, previous)
            total_pages += 1
            if not page:
                exhausted = True; break
            transactions.extend(page); cursor = page[-1]['txid']
    after = requests.get(record, 'reference_after', '/tx/' + record['payment_txid'] + '/status')
    status_check(record, after); parents = {}
    if exhausted:
        ids = {tx['txid'] for tx in transactions}
        for vin in own:
            if vin['txid'] not in ids and vin['txid'] not in parents:
                status = requests.get(record, 'parent_' + hashlib.sha256(vin['txid'].encode()).hexdigest(),
                                      '/tx/' + vin['txid'] + '/status')
                status_check(record, status); parents[vin['txid']] = status
    result = tail.tail_check(record, anchor, transactions, exhausted, after, parents)
    if result['status'] == 'complete_prior_prefix':
        result['audit'].update(provider=PROVIDER,
            completeness_basis='Mempool native indexed cursor contract; verified cached prefix and exhausted anchored tail')
    raw = dict(address=record['address'], anchor=anchor, transactions=transactions, anchor_after=after,
        parent_statuses=parents, pagination_exhausted=exhausted, pages_fetched=total_pages,
        provider=PROVIDER, offline_native_pages_reused=old_pages, fresh_native_pages=total_pages-old_pages,
        collected_at=datetime.now(timezone.utc).isoformat())
    raw_path = work / 'raw' / (record['pilot_id'] + '.json.gz')
    atomic_write(raw_path, gzip.compress(json_bytes(raw), mtime=0))
    entry = dict(source_id=record['pilot_id'], address_sha256=record['address_sha256'],
        payment_txid_sha256=record['payment_txid_sha256'], cutoff_height=record['cutoff_height'],
        cutoff_block_hash=record['cutoff_block_hash'], raw_file='raw/' + raw_path.name,
        raw_sha256=sha(raw_path), pages_fetched=total_pages, **result)
    atomic_write(work / 'results' / (record['pilot_id'] + '.json.gz'), gzip.compress(json_bytes(entry), mtime=0))
    return entry


class ExecutionStopped(Exception):
    pass


def run(protocol_path, work):
    out = protocol_path.parent; q = read(protocol_path)
    require(q['provider'] == PROVIDER and not (out / 'run_receipt.json').exists(), 'Wrong or closed resume scope')
    for pin in q['inputs'].values():
        require(sha((out / pin['file']).resolve()) == pin['sha256'], 'Resume input pin changed')
    for name, key in [('plan.json', 'private_plan_sha256'), ('historical_locks.json', 'private_lock_manifest_sha256'),
                      ('remaining_source_registry.json', 'private_identity_registry_sha256'),
                      ('retained_bridge_native_cursors.json', 'private_retained_bridge_native_cursors_sha256'),
                      ('parent_native_cursors.json', 'private_parent_native_cursors_sha256')]:
        require(sha(work / name) == q[key], 'Resume private input differs: ' + name)
    records = read(work / 'plan.json'); require([r['pilot_id'] for r in records] == q['source_ids'], 'Resume source order differs')
    all_pins = read(out / 'offline_reuse_manifest.json')['responses']
    pins = {sid: [m for m in all_pins if m['source_id'] == sid] for sid in q['source_ids']}
    markers = [read(p) for p in (work / 'requests').glob('*/*.json')]
    require(len(markers) == len(all_pins) and all(m.get('offline_reused') for m in markers) and
            not list((work / 'results').glob('*.json.gz')), 'Resume scope already consumed')
    for record in records:
        cached_prefix(record, work, pins[record['pilot_id']])
    policy_path = (out / q['live_policy_file']).resolve(); error, entries = None, {}
    def stop(signum, frame):
        raise ExecutionStopped('Execution signal received; no automatic restart')
    signal.signal(signal.SIGTERM, stop); signal.signal(signal.SIGINT, stop)
    with ExitStack() as stack:
        for name in sorted(set(read(work / 'historical_locks.json')) | {str(work / 'collector.lock')}):
            lock = stack.enter_context(Path(name).open('a+')); fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        print('LOCK_HELD_READY', flush=True); deadline = time.monotonic() + 300
        while not (work / 'lease_published').exists():
            require(time.monotonic() < deadline, 'No published resume lease; no HTTP'); time.sleep(.25)
        permit = read(work / 'lease_published'); check_lease(q, protocol_path, permit, policy_path)
        try:
            with MempoolHTTP(q['requests_per_second']) as http:
                requests = GuardedRequests(work, http, q['maximum_requests'],
                    lambda: check_lease(q, protocol_path, permit, policy_path))
                for record in records:
                    entry = collect(record, requests, work, q, pins[record['pilot_id']]); entries[record['pilot_id']] = entry
                    print(record['pilot_id'] + ': ' + entry['status'], flush=True); tail.export(protocol_path, out, work)
        except Exception as caught:
            error = dict(error_type=type(caught).__name__, reason=str(caught) if isinstance(caught, (ValueError, ExecutionStopped))
                         else 'Acquisition stopped; see hashed request metadata')
            print('STOPPED ' + type(caught).__name__, flush=True)
    tail.export(protocol_path, out, work)
    metadata = [read(p) for p in sorted((work / 'requests').glob('*/*.json'))]
    fresh = [m for m in metadata if not m.get('offline_reused')]
    write(out / 'run_receipt.json', dict(schema_version=1, status='stopped' if error else 'completed', error=error,
        provider=PROVIDER, provider_requests=len(fresh), http200=sum(m.get('http_status') == 200 for m in fresh),
        reused_successful_responses=len(metadata)-len(fresh), failures=sum('error_type' in m for m in fresh),
        finalized_sources=len(entries), operational_locks_released=True, blockstream_provider_requests=0,
        automatic_retry_performed=False, proxy_account_ip_or_tls_changed=False, model_fits=0, new_scores=0))
    print('RESUME_SCOPE_FINISHED', flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('protocol', type=Path); p.add_argument('work', type=Path)
    a = p.parse_args(); run(a.protocol.resolve(), a.work.resolve())
