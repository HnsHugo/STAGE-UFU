"""Bounded, explicitly authorized acquisition from the independent Mempool API."""
import argparse
from contextlib import ExitStack
from datetime import datetime, timezone
import fcntl
import gzip
import hashlib
import json
from pathlib import Path
import time
import urllib.error

import collect_reference_tail as tail
from comparison_http import PersistentHTTP
from build_source_registry import json_bytes
from prepare_frontier_checkpoint import read, sha, write

BASE = Path(__file__).resolve().parent
PROVIDER = 'https://mempool.space/api'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def status_check(record, status):
    require(status.get('confirmed') is True and
        status.get('block_height') == record['cutoff_height'] and
        status.get('block_hash') == record['cutoff_block_hash'], 'Independent reference anchor differs')


def core(tx):
    """Compare immutable data, including every field used by the fourteen predictors."""
    def output(o):
        return {k: o.get(k) for k in ['scriptpubkey', 'scriptpubkey_address', 'value']}
    return dict(**{k: tx[k] for k in ['txid', 'version', 'locktime', 'size', 'weight', 'fee']},
        status={k: tx['status'].get(k) for k in ['confirmed', 'block_height', 'block_hash', 'block_time']},
        vin=[dict(**{k: i.get(k) for k in ['txid', 'vout', 'is_coinbase', 'scriptsig', 'sequence']},
                  witness=i.get('witness', []), prevout=output(i['prevout']) if i.get('prevout') else None)
             for i in tx['vin']], vout=[output(o) for o in tx['vout']])


def legacy_source(record, work, pins):
    folder = work / 'legacy' / record['pilot_id']
    for key, pin in pins.items():
        marker, body = folder / (key + '.json'), folder / (key + '.json.gz')
        meta = read(marker)
        require(meta.get('http_status') == 200 and 'error_type' not in meta, 'Failed legacy response')
        require(sha(body) == pin['sha256'] == meta['sha256'], 'Legacy body fingerprint differs')
        require(meta['endpoint_sha256'] == pin['endpoint_sha256'], 'Legacy endpoint differs')
    anchor = read(folder / 'reference.json.gz')
    tail.anchor_check(record, anchor)
    pages, transactions, cursor, previous, seen = [], [], record['payment_txid'], record['cutoff_height'], set()
    require(pins['reference']['endpoint_sha256'] == hashlib.sha256(('/tx/' + cursor).encode()).hexdigest(), 'Legacy reference cursor differs')
    for i in range(len(pins) - 1):
        key = f'tail_{i:04d}'
        require(key in pins, 'Legacy page gap')
        endpoint = '/address/' + record['address'] + '/txs/chain/' + cursor
        require(pins[key]['endpoint_sha256'] == hashlib.sha256(endpoint.encode()).hexdigest(), 'Legacy cursor differs')
        page = read(folder / (key + '.json.gz'))
        require(isinstance(page, list) and len(page) <= 25, 'Invalid legacy page')
        require(bool(page) or i == len(pins) - 2, 'Legacy empty page is not terminal')
        for tx in page:
            require(tx['txid'] not in seen and tx['txid'] != record['payment_txid'], 'Repeated legacy transaction')
            require(tx['status'].get('confirmed') is True and tx['status'].get('block_hash') and
                    tx['status']['block_height'] <= previous, 'Unanchored legacy order')
            previous = tx['status']['block_height']; seen.add(tx['txid'])
        pages.append(page); transactions.extend(page)
        if page:
            cursor = page[-1]['txid']
    require(bool(transactions), 'No boundary transaction to compare')
    own = tail.anchor_check(record, anchor)
    require(all(v['txid'] in seen for v in own), 'Pilot needs an unplanned funding-status query')
    return anchor, pages, transactions, cursor


class MempoolHTTP(PersistentHTTP):
    async def request(self, url, timeout):
        require(url.startswith(PROVIDER + '/'), 'Unapproved provider URL')
        async with self.lock:
            delay = max(0, self.next_start - self.loop.time())
            if delay:
                import asyncio
                await asyncio.sleep(delay)
            self.next_start = self.loop.time() + self.interval
            self.last_dispatch_at = datetime.now(timezone.utc).isoformat()
        bound = self.aiohttp.ClientTimeout(total=timeout, connect=timeout, sock_read=timeout)
        async with self.client.get(url, timeout=bound, allow_redirects=False) as response:
            if response.status != 200:
                raise urllib.error.HTTPError(url, response.status, response.reason, response.headers, None)
            return json.loads(await response.read())


class Requests:
    def __init__(self, work, http, maximum):
        self.work, self.http, self.maximum, self.count = work, http, maximum, 0

    def get(self, record, key, endpoint):
        require(self.count < self.maximum, 'Pilot request budget exhausted')
        folder = self.work / 'requests' / record['pilot_id']; folder.mkdir(parents=True, exist_ok=True)
        marker, body = folder / (key + '.json'), folder / (key + '.json.gz')
        require(not marker.exists() and not body.exists(), 'Consumed request cannot be repeated')
        meta = dict(source_id=record['pilot_id'], key=key, provider=PROVIDER,
            endpoint_sha256=hashlib.sha256(endpoint.encode()).hexdigest(),
            started_at=datetime.now(timezone.utc).isoformat())
        write(marker, meta); self.count += 1
        try:
            data = self.http.get_json(PROVIDER + endpoint, 15)
            body.write_bytes(gzip.compress(json_bytes(data), mtime=0))
            meta.update(http_status=200, sha256=sha(body))
            return data
        except Exception as error:
            meta.update(error_type=type(error).__name__)
            if isinstance(error, urllib.error.HTTPError):
                meta['http_status'] = error.code
                meta['failure_origin'] = 'provider_http_response'
                if error.headers and error.headers.get('Retry-After'):
                    meta['retry_after'] = error.headers['Retry-After']
            elif isinstance(error, getattr(self.http.aiohttp, 'ClientHttpProxyError', ())):
                meta.update(proxy_connect_status=error.status, failure_origin='proxy_connect')
            raise
        finally:
            meta.update(finished_at=datetime.now(timezone.utc).isoformat(),
                dispatch_at=getattr(self.http, 'last_dispatch_at', None))
            write(marker, meta)


def collect(record, requests, work, q, legacy_pins):
    anchor, pages, transactions, cursor = legacy_source(record, work, legacy_pins)
    status_check(record, requests.get(record, 'reference_before', '/tx/' + record['payment_txid'] + '/status'))
    boundary = requests.get(record, 'boundary', '/tx/' + cursor)
    require(core(boundary) == core(transactions[-1]), 'Cross-provider boundary transaction differs')
    terminal = not pages[-1]
    effective_pages = len(pages) - int(terminal)
    seen = {t['txid'] for t in transactions}
    previous = transactions[-1]['status']['block_height']
    added, exhausted = [], False
    for i in range(effective_pages, q['max_pages_per_address']):
        page = requests.get(record, f'tail_{i:04d}', '/address/' + record['address'] + '/txs/chain/' + cursor)
        require(isinstance(page, list) and len(page) <= 25, 'Invalid independent cursor page')
        if terminal:
            require(not page, 'Independent provider disagrees with saved terminal page')
        for tx in page:
            require(tx['txid'] not in seen and tx['txid'] != record['payment_txid'], 'Repeated independent cursor transaction')
            require(tx['status'].get('confirmed') is True and tx['status'].get('block_hash') and
                    tx['status']['block_height'] <= previous, 'Unanchored independent ordering')
            require(any(o.get('scriptpubkey_address') == record['address'] for o in tx['vout']) or
                    any((v.get('prevout') or {}).get('scriptpubkey_address') == record['address'] for v in tx['vin']),
                    'Independent page contains an unrelated transaction')
            previous = tx['status']['block_height']; seen.add(tx['txid'])
        if not page:
            exhausted = True
            break
        transactions.extend(page); added.extend(page); cursor = page[-1]['txid']
    after = requests.get(record, 'reference_after', '/tx/' + record['payment_txid'] + '/status')
    status_check(record, after)
    result = tail.tail_check(record, anchor, transactions, exhausted, after, {})
    raw = dict(address=record['address'], anchor=anchor, transactions=transactions, anchor_after=after,
        parent_statuses={}, pagination_exhausted=exhausted, pages_fetched=i + 1,
        mixed_provider_provenance=dict(saved_prefix_provider='https://blockstream.info/api',
            fresh_boundary_continuation_and_status_provider=PROVIDER, boundary_core_equal=True),
        additional_source_transaction_observations=sum(t['status']['block_height'] < record['cutoff_height'] for t in added))
    raw_path = work / 'raw' / (record['pilot_id'] + '.json.gz')
    raw_path.write_bytes(gzip.compress(json_bytes(raw), mtime=0))
    entry = dict(source_id=record['pilot_id'], cutoff_height=record['cutoff_height'],
        raw_file='raw/' + raw_path.name, raw_sha256=sha(raw_path), **result)
    (work / 'results' / (record['pilot_id'] + '.json.gz')).write_bytes(gzip.compress(json_bytes(entry), mtime=0))
    return entry


def run(protocol_path, work):
    out = protocol_path.parent; q = read(protocol_path)
    require(q['provider'] == PROVIDER and not (out / 'run_receipt.json').exists(), 'Wrong or closed pilot')
    for pin in q['inputs'].values():
        require(sha((out / pin['file']).resolve()) == pin['sha256'], 'Pinned input changed')
    require(sha(work / 'plan.json') == q['private_plan_sha256'], 'Pilot plan differs')
    require(sha(work / 'historical_locks.json') == q['private_lock_manifest_sha256'], 'Pilot locks differ')
    pins = read(out / 'legacy_reuse_manifest.json')['responses']
    by_source = {sid: {m['key']: m for m in pins if m['source_id'] == sid} for sid in q['source_ids']}
    records = read(work / 'plan.json')
    require([r['pilot_id'] for r in records] == q['source_ids'], 'Pilot source order differs')
    for r in records:
        legacy_source(r, work, by_source[r['pilot_id']])
    entries, error = {}, None
    with ExitStack() as stack:
        for name in sorted(set(read(work / 'historical_locks.json')) | {str(work / 'collector.lock')}):
            lock = stack.enter_context(Path(name).open('a+')); fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        print('LOCK_HELD_READY', flush=True)
        deadline = time.monotonic() + 300
        while not (work / 'lease_published').exists():
            require(time.monotonic() < deadline, 'No published pilot lease; no HTTP')
            time.sleep(.25)
        permit = read(work / 'lease_published'); lease = permit['collector_lease']
        require(lease['state'] == 'running' and lease['owner'] == q['pass_name'] and lease['provider'] == PROVIDER,
            'Wrong provider lease')
        require(lease['protocol_sha256'] == sha(protocol_path) and len(permit['published_commit']) == 40 and
            datetime.fromisoformat(lease['expires_at']) > datetime.now(timezone.utc), 'Unverified or expired pilot lease')
        try:
            with MempoolHTTP(q['requests_per_second']) as http:
                requests = Requests(work, http, q['maximum_requests'])
                for record in records:
                    entry = collect(record, requests, work, q, by_source[record['pilot_id']])
                    entries[record['pilot_id']] = entry
                    print(record['pilot_id'] + ': ' + entry['status'], flush=True)
        except Exception as caught:
            error = dict(error_type=type(caught).__name__,
                reason=str(caught) if isinstance(caught, ValueError) else 'Acquisition stopped; see hashed request metadata')
            print('STOPPED ' + type(caught).__name__, flush=True)
    metadata = [read(p) for p in sorted((work / 'requests').glob('*/*.json'))]
    write(out / 'run_receipt.json', dict(schema_version=1, status='stopped' if error else 'completed', error=error,
        provider=PROVIDER, provider_requests=len(metadata), http200=sum(m.get('http_status') == 200 for m in metadata),
        failures=sum('error_type' in m for m in metadata), finalized_sources=len(entries),
        operational_locks_released=True, blockstream_provider_requests=0, automatic_retry_performed=False,
        proxy_account_ip_or_tls_changed=False, model_fits=0))
    (out / 'checkpoint.json.gz').write_bytes(gzip.compress(json_bytes(dict(protocol_sha256=sha(protocol_path), entries=entries)), mtime=0))
    (out / 'request_manifest.json.gz').write_bytes(gzip.compress(json_bytes(metadata), mtime=0))
    print('PILOT_FINISHED', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('protocol', type=Path); parser.add_argument('work', type=Path)
    args = parser.parse_args()
    run(args.protocol.resolve(), args.work.resolve())
