"""Explicit supplemental full-history coverage, with immutable page checkpoints.

The former 16-page pass stays immutable. This pass exhausts the original
provider's confirmed-history cursor and keeps the existing counter audit and
feature extractor. A failed or interrupted request is never silently retried.
"""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import fcntl
import gzip
import json
from pathlib import Path
from threading import Event
import urllib.error

from build_source_registry import digest, json_bytes
import collect_comparison_histories as prior
from comparison_http import PersistentHTTP
from source_cohort import atomic_write


def now():
    return datetime.now(timezone.utc).isoformat()


class Pages:
    def __init__(self, work, http, stop):
        self.work, self.http, self.stop = work, http, stop

    def get(self, record, key, endpoint):
        folder = self.work / 'requests' / record['pilot_id']
        marker, body = folder / (key + '.json'), folder / (key + '.json.gz')
        if body.exists():
            meta = json.loads(marker.read_bytes())
            raw = body.read_bytes()
            if digest(raw) != meta['sha256']:
                raise ValueError('Saved response fingerprint changed')
            return json.loads(gzip.decompress(raw))
        # Marker precedes HTTP. A marker without bytes consumes the request.
        if marker.exists():
            raise RuntimeError('Consumed request has no saved response: ' + key)
        if self.stop.is_set():
            raise InterruptedError('Collector stopped before this request')
        folder.mkdir(parents=True, exist_ok=True)
        meta = dict(source_id=record['pilot_id'], key=key, started_at=now(),
                    endpoint_sha256=digest(endpoint.encode()))
        with marker.open('xb') as stream:
            stream.write(json_bytes(meta))
        try:
            data = self.http.get_json('https://blockstream.info/api' + endpoint, 15)
            raw = gzip.compress(json_bytes(data), mtime=0)
            atomic_write(body, raw)
            meta.update(finished_at=now(), sha256=digest(raw), http_status=200)
        except Exception as error:
            meta.update(finished_at=now(), error_type=type(error).__name__, reason=str(error))
            if isinstance(error, urllib.error.HTTPError):
                meta['http_status'] = error.code
                if error.headers and error.headers.get('Retry-After'):
                    meta['retry_after'] = error.headers['Retry-After']
            # A failure stops scheduling. There is no internal retry.
            self.stop.set()
            raise
        finally:
            atomic_write(marker, json_bytes(meta))
        return data


def finish_source(record, pages, work):
    key = record['pilot_id']
    result_path = work / 'results' / (key + '.json.gz')
    if result_path.exists():
        return json.loads(gzip.decompress(result_path.read_bytes()))
    folder = work / 'requests' / key
    marker = json.loads((folder / 'before.json').read_bytes())
    transactions, cursor, seen, exhausted, count = [], '', set(), False, 0
    before = pages.get(record, 'before', '/address/' + record['address'])
    while not exhausted:
        endpoint = '/address/' + record['address'] + '/txs/chain' + ('/' + cursor if cursor else '')
        batch = pages.get(record, 'page_%06d' % count, endpoint)
        if not isinstance(batch, list) or len(batch) > 25:
            raise ValueError('Invalid confirmed-history page')
        count += 1
        for tx in batch:
            if tx['txid'] in seen:
                raise ValueError('Repeated transaction in cursor history')
            if transactions and tx['status']['block_height'] > transactions[-1]['status']['block_height']:
                raise ValueError('Provider history is not newest first')
            seen.add(tx['txid'])
            transactions.append(tx)
        if not batch:
            exhausted = True
        else:
            cursor = batch[-1]['txid']
        if count % 16 == 0:
            atomic_write(work / 'cursors' / (key + '.json'), json_bytes(dict(
                source_id=key, pages_saved=count, transactions_saved=len(transactions),
                last_txid_sha256=digest(cursor.encode()), updated_at=now())))
            print(key + ': saved %d pages / %d transactions' % (count, len(transactions)), flush=True)
    after = pages.get(record, 'after', '/address/' + record['address'])
    history = dict(address=record['address'], provider='https://blockstream.info/api',
                   before=before, after=after, transactions=transactions,
                   audit=prior.fixed.check_history(record['address'], transactions, before, after, exhausted),
                   pages_fetched=count, collected_at=now(), collection_mode='extended_full_history_pagination')
    raw = gzip.compress(json_bytes(history), mtime=0)
    atomic_write(work / 'raw' / (key + '.json.gz'), raw)
    entry = prior.from_raw(record, raw, dict(started_at=marker['started_at'], finished_at=now()))
    atomic_write(result_path, gzip.compress(json_bytes(entry), mtime=0))
    return entry


def guarded_source(record, pages, work):
    try:
        return finish_source(record, pages, work)
    except Exception:
        pages.stop.set()
        raise


def export(protocol_path, output, work):
    protocol = json.loads(protocol_path.read_bytes())
    entries = {}
    for key in protocol['source_ids']:
        file = work / 'results' / (key + '.json.gz')
        if file.exists():
            entries[key] = json.loads(gzip.decompress(file.read_bytes()))
    # Redact address endpoints and cursor TXIDs; publish only fingerprints/counts.
    requests = []
    for file in sorted((work / 'requests').glob('*/*.json')):
        requests.append(json.loads(file.read_bytes()))
    output.mkdir(parents=True, exist_ok=True)
    atomic_write(output / 'checkpoint.json.gz', gzip.compress(json_bytes(dict(
        protocol_sha256=digest(protocol_path.read_bytes()), entries=entries)), mtime=0))
    atomic_write(output / 'request_manifest.json.gz', gzip.compress(json_bytes(requests), mtime=0))
    counters = {}
    for key in protocol['source_ids']:
        body = work / 'requests' / key / 'before.json.gz'
        if body.exists():
            counters[key] = json.loads(gzip.decompress(body.read_bytes()))['chain_stats']['tx_count']
    status = Counter(e['status'] for e in entries.values())
    summary = dict(selected=160, completed_results=len(entries), statuses=dict(status),
        pending=160-len(entries), counters_observed=len(counters),
        current_full_transaction_counts=counters, requests_started=len(requests),
        saved_responses=sum('sha256' in r for r in requests),
        failed_requests=[r for r in requests if r.get('http_status', 200) != 200 or 'error_type' in r],
        training_performed=False, labels_changed=False, previous_results_preserved=True)
    atomic_write(output / 'progress.json', json_bytes(summary))
    return summary


def run(protocol_path, output, work, batch_limit):
    proto = json.loads(protocol_path.read_bytes())
    records = json.loads((work / 'plan.json').read_bytes())
    if digest(json_bytes(records)) != proto['private_plan_sha256']:
        raise ValueError('Private plan changed')
    by_id = {r['pilot_id']:r for r in records}
    stop = Event()
    with (work / 'collector.lock').open('a+') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        print('LOCK_HELD_READY', flush=True)
        import time
        deadline = time.monotonic() + 300
        while not (work / 'lease_published').exists():
            if time.monotonic() > deadline:
                raise RuntimeError('Published lease not confirmed; no HTTP')
            time.sleep(.25)
        with PersistentHTTP(1) as http:
            pages = Pages(work, http, stop)
            try:
                # First address is also the unique ordinary due access check.
                first = records[0]
                pages.get(first, 'before', '/address/' + first['address'])
                print('FIRST_COUNTER_HTTP_200', flush=True)
                # Record all counters once; shortest histories first is a frozen
                # workload policy, never sample replacement or outcome selection.
                with ThreadPoolExecutor(max_workers=2) as pool:
                    fs = [pool.submit(pages.get, r, 'before', '/address/' + r['address']) for r in records]
                    for future in as_completed(fs):
                        future.result()
                summary = export(protocol_path, output, work)
                order = sorted(records, key=lambda r:(summary['current_full_transaction_counts'][r['pilot_id']], r['pilot_id']))
                print('COUNTERS_SAVED ' + json.dumps(summary['current_full_transaction_counts']), flush=True)
                for offset in range(0, len(order), 20):
                    if offset // 20 >= batch_limit or stop.is_set():
                        break
                    with ThreadPoolExecutor(max_workers=2) as pool:
                        futures = [pool.submit(guarded_source, r, pages, work) for r in order[offset:offset+20]]
                        for f in as_completed(futures):
                            e = f.result()
                            print(e['source_id'] + ': ' + e['status'], flush=True)
                    print('BATCH_VERIFIED ' + json.dumps(export(protocol_path, output, work)), flush=True)
            except Exception as error:
                stop.set()
                print('STOPPED ' + type(error).__name__ + ': ' + str(error), flush=True)
            finally:
                print('FINAL ' + json.dumps(export(protocol_path, output, work)), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('protocol', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('work', type=Path)
    parser.add_argument('--max-batches', type=int, default=8)
    args = parser.parse_args()
    run(args.protocol, args.output, args.work, args.max_batches)
