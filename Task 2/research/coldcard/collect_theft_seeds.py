"""Collect confirmed Esplora histories; public source labels remain address-level."""
import argparse
import hashlib
import json
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'


def validate_address(address):
    n = 0
    for char in address:
        n = n * 58 + ALPHABET.index(char)
    raw = n.to_bytes((n.bit_length() + 7) // 8, 'big')
    raw = b'\0' * (len(address) - len(address.lstrip('1'))) + raw
    if len(raw) != 25 or raw[0] not in (0, 5):
        raise ValueError('Expected mainnet Base58Check address')
    if hashlib.sha256(hashlib.sha256(raw[:-4]).digest()).digest()[:4] != raw[-4:]:
        raise ValueError('Invalid address checksum')


def get(url):
    for attempt in range(3):
        try:
            with urllib.request.urlopen(url, timeout=25) as response:
                return json.loads(response.read())
        except Exception:
            if attempt == 2:
                raise
            time.sleep(attempt + 1)


def check_history(address, transactions, before, after, exhausted):
    ids = [tx['txid'] for tx in transactions]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate transactions')
    funded = spent = funded_count = spent_count = 0
    for tx in transactions:
        if not tx['status']['confirmed']:
            raise ValueError('Unconfirmed transaction in chain history')
        if not tx['status'].get('block_hash'):
            raise ValueError('Missing block anchor')
        outputs = [o for o in tx['vout'] if o.get('scriptpubkey_address') == address]
        inputs = [i['prevout'] for i in tx['vin'] if i.get('prevout') and i['prevout'].get('scriptpubkey_address') == address]
        if not outputs and not inputs:
            raise ValueError('Transaction unrelated to address')
        funded_count += len(outputs)
        spent_count += len(inputs)
        funded += sum(o['value'] for o in outputs)
        spent += sum(i['value'] for i in inputs)
    observed = dict(tx_count=len(ids), funded_txo_count=funded_count,
                    spent_txo_count=spent_count, funded_txo_sum=funded, spent_txo_sum=spent)
    complete = exhausted and before['chain_stats'] == after['chain_stats'] == observed
    return dict(coverage_complete_by_provider_counters=complete, observed=observed,
                counters_stable=before['chain_stats'] == after['chain_stats'],
                pagination_exhausted=exhausted,
                cryptographic_inclusion_verified=False)


def collect(record, base):
    address = record['address']
    validate_address(address)
    before = get(f'{base}/address/{address}')
    txs, seen, cursor = [], set(), ''
    exhausted = False
    for _ in range(100):
        endpoint = f'{base}/address/{address}/txs/chain' + (f'/{cursor}' if cursor else '')
        page = get(endpoint)
        if not page:
            exhausted = True
            break
        for tx in page:
            if tx['txid'] in seen:
                raise ValueError('Repeated transaction during pagination')
            seen.add(tx['txid'])
            txs.append(tx)
        cursor = page[-1]['txid']
    after = get(f'{base}/address/{address}')
    audit = check_history(address, txs, before, after, exhausted)
    times = [tx['status']['block_time'] for tx in txs]
    return dict(address=address, source_record=record, provider=base,
                collected_at=datetime.now(timezone.utc).isoformat(),
                before=before, after=after, audit=audit,
                first_confirmed_at=datetime.fromtimestamp(min(times), timezone.utc).isoformat() if times else None,
                last_confirmed_at=datetime.fromtimestamp(max(times), timezone.utc).isoformat() if times else None,
                transactions=txs,
                transaction_theft_labels='unknown; address attribution does not label every transaction')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('registry', type=Path)
    p.add_argument('output', type=Path)
    p.add_argument('--base', default='https://blockstream.info/api')
    args = p.parse_args()
    registry = json.loads(args.registry.read_text())
    args.output.mkdir(parents=True, exist_ok=False)
    results = []
    for record in registry['records']:
        address = record['address']
        try:
            result = collect(record, args.base.rstrip('/'))
            filename = address + '.json'
            raw = (json.dumps(result, indent=2) + '\n').encode()
            (args.output / filename).write_bytes(raw)
            summary = {k: result[k] for k in ('address', 'audit', 'first_confirmed_at', 'last_confirmed_at')}
            summary.update(file=filename, sha256=hashlib.sha256(raw).hexdigest())
        except Exception as error:
            summary = dict(address=address, error=str(error))
        results.append(summary)
        (args.output / 'manifest.json').write_text(json.dumps(dict(
            status='complete' if len(results) == len(registry['records']) and all(r.get('audit', {}).get('coverage_complete_by_provider_counters') for r in results) else 'incomplete',
            registry_sha256=hashlib.sha256(args.registry.read_bytes()).hexdigest(),
            provider=args.base, results=results), indent=2) + '\n')
        print(json.dumps(summary), flush=True)


if __name__ == '__main__':
    main()
