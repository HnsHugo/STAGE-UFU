"""Native-Mempool acquisition of frozen prior-prefix sources; no provider fallback."""
import argparse
from contextlib import ExitStack
from datetime import datetime, timezone
import fcntl
import gzip
import time
from pathlib import Path

from build_source_registry import json_bytes
from prepare_frontier_checkpoint import read, sha, write
import collect_reference_tail as tail
from independent_mempool_pilot import MempoolHTTP, Requests, PROVIDER, require, status_check


def validate_page(record, page, seen, previous):
    """Reject malformed, unrelated, repeated or forward-height data before continuation."""
    require(isinstance(page, list) and len(page) <= 25, 'Invalid native cursor page')
    for tx in page:
        require(tx['txid'] not in seen, 'Repeated native transaction')
        require(tx['status'].get('confirmed') is True and tx['status'].get('block_hash') and
                tx['status']['block_height'] <= previous, 'Unanchored native ordering')
        require(any(o.get('scriptpubkey_address') == record['address'] for o in tx['vout']) or
                any((v.get('prevout') or {}).get('scriptpubkey_address') == record['address'] for v in tx['vin']),
                'Native page contains an unrelated transaction')
        previous = tx['status']['block_height']; seen.add(tx['txid'])
    return previous


class NativeRequests(Requests):
    def __init__(self, work, http, maximum, guard):
        super().__init__(work, http, maximum)
        self.guard, self.states = guard, {}

    def get(self, record, key, endpoint):
        self.guard()
        data = super().get(record, key, endpoint)
        sid = record['pilot_id']
        if key == 'reference':
            require(sid not in self.states, 'Native source already started')
            tail.anchor_check(record, data)
            self.states[sid] = dict(seen={record['payment_txid']}, height=record['cutoff_height'],
                                    cursor=record['payment_txid'], next_page=0, terminal=False)
        elif key.startswith('tail_'):
            state = self.states[sid]
            require(not state['terminal'] and key == f"tail_{state['next_page']:04d}", 'Native page sequence differs')
            require(endpoint == '/address/' + record['address'] + '/txs/chain/' + state['cursor'], 'Native cursor differs')
            state['height'] = validate_page(record, data, state['seen'], state['height'])
            state['next_page'] += 1; state['terminal'] = not data
            if data:
                state['cursor'] = data[-1]['txid']
        elif key == 'reference_after':
            status_check(record, data)
        elif key.startswith('parent_'):
            require(data.get('confirmed') is True and data.get('block_height') == record['cutoff_height'] and
                    data.get('block_hash') == record['cutoff_block_hash'], 'Missing funding is not in excluded reference block')
        else:
            raise ValueError('Unplanned native request key')
        return data


def check_lease(q, protocol_path, permit, policy_path):
    lease = permit['collector_lease']
    require(lease['state'] == 'running' and lease['owner'] == q['pass_name'] and lease['provider'] == PROVIDER,
            'Wrong native provider lease')
    require(lease['protocol_sha256'] == sha(protocol_path) and len(permit['published_commit']) == 40 and
            datetime.fromisoformat(lease['expires_at']) > datetime.now(timezone.utc), 'Unverified or expired native lease')
    policy = read(policy_path)
    require(policy['collector_lease'] == lease and policy['active_collection_scope'] == q['pass_name'], 'Live native lease changed')
    gate = policy['provider_access_policies'][PROVIDER].get('next_network_attempt_not_before')
    require(gate is None or datetime.now(timezone.utc) >= datetime.fromisoformat(gate), 'Native provider cooldown not due')
    require(policy['provider_access_policies']['https://blockstream.info/api']['next_network_attempt_not_before'] ==
            q['blockstream_cooldown_preserved_until'], 'Closed Blockstream gate changed')


def run(protocol_path, work):
    out = protocol_path.parent; q = read(protocol_path)
    require(q['provider'] == PROVIDER and not (out / 'run_receipt.json').exists(), 'Wrong or closed native scope')
    for pin in q['inputs'].values():
        require(sha((out / pin['file']).resolve()) == pin['sha256'], 'Native input pin changed')
    require(sha(work / 'plan.json') == q['private_plan_sha256'], 'Native private plan differs')
    require(sha(work / 'historical_locks.json') == q['private_lock_manifest_sha256'], 'Native locks differ')
    records = read(work / 'plan.json')
    require([r['pilot_id'] for r in records] == q['source_ids'], 'Native source order differs')
    require(not list((work / 'requests').glob('*/*.json')) and not list((work / 'results').glob('*.json.gz')),
            'Native scope already consumed')
    policy_path = (out / q['live_policy_file']).resolve(); entries, error = {}, None
    with ExitStack() as stack:
        for name in sorted(set(read(work / 'historical_locks.json')) | {str(work / 'collector.lock')}):
            lock = stack.enter_context(Path(name).open('a+')); fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        print('LOCK_HELD_READY', flush=True)
        deadline = time.monotonic() + 300
        while not (work / 'lease_published').exists():
            require(time.monotonic() < deadline, 'No published native lease; no HTTP')
            time.sleep(.25)
        permit = read(work / 'lease_published')
        check_lease(q, protocol_path, permit, policy_path)
        try:
            with MempoolHTTP(q['requests_per_second']) as http:
                requests = NativeRequests(work, http, q['maximum_requests'],
                    lambda: check_lease(q, protocol_path, permit, policy_path))
                for record in records:
                    entry = tail.collect_one(record, requests, work, q['max_pages_per_address'])
                    if entry['status'] == 'complete_prior_prefix':
                        entry['audit'].update(provider=PROVIDER,
                            completeness_basis='Mempool indexed native cursor contract; exhausted anchored tail')
                        (work / 'results' / (record['pilot_id'] + '.json.gz')).write_bytes(gzip.compress(json_bytes(entry), mtime=0))
                    entries[record['pilot_id']] = entry
                    print(record['pilot_id'] + ': ' + entry['status'], flush=True)
                    tail.export(protocol_path, out, work)
        except Exception as caught:
            error = dict(error_type=type(caught).__name__,
                reason=str(caught) if isinstance(caught, ValueError) else 'Acquisition stopped; see hashed request metadata')
            print('STOPPED ' + type(caught).__name__, flush=True)
    tail.export(protocol_path, out, work)
    metadata = [read(p) for p in sorted((work / 'requests').glob('*/*.json'))]
    write(out / 'run_receipt.json', dict(schema_version=1, status='stopped' if error else 'completed', error=error,
        provider=PROVIDER, provider_requests=len(metadata), http200=sum(m.get('http_status') == 200 for m in metadata),
        failures=sum('error_type' in m for m in metadata), finalized_sources=len(entries),
        operational_locks_released=True, blockstream_provider_requests=0, automatic_retry_performed=False,
        proxy_account_ip_or_tls_changed=False, model_fits=0, new_scores=0))
    print('NATIVE_SCOPE_FINISHED', flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('protocol', type=Path); p.add_argument('work', type=Path)
    a = p.parse_args(); run(a.protocol.resolve(), a.work.resolve())
