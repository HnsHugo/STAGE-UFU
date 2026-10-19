"""Descriptive movements only: never propagate address labels to transactions."""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def summarize(folder):
    manifest = json.loads((folder / 'manifest.json').read_text())
    if manifest['status'] != 'complete':
        raise ValueError('Incomplete collection')
    addresses, movements, txids = [], [], set()
    for entry in manifest['results']:
        raw = (folder / entry['file']).read_bytes()
        if hashlib.sha256(raw).hexdigest() != entry['sha256']:
            raise ValueError('History file hash mismatch')
        data = json.loads(raw)
        address = data['address']
        addresses.append(dict(address=address, **data['audit']['observed'],
                              first_confirmed_at=data['first_confirmed_at'],
                              last_confirmed_at=data['last_confirmed_at']))
        for tx in sorted(data['transactions'], key=lambda t: t['status']['block_time']):
            txids.add(tx['txid'])
            received = sum(o['value'] for o in tx['vout'] if o.get('scriptpubkey_address') == address)
            spent = sum(i['prevout']['value'] for i in tx['vin'] if i.get('prevout') and i['prevout'].get('scriptpubkey_address') == address)
            movements.append(dict(address=address, txid=tx['txid'],
                                  block_height=tx['status']['block_height'],
                                  block_hash=tx['status']['block_hash'],
                                  confirmed_at=datetime.fromtimestamp(tx['status']['block_time'], timezone.utc).isoformat(),
                                  received_sat=received, spent_sat=spent,
                                  theft_status='unknown_at_transaction_level'))
    return dict(status='descriptive_only', address_count=len(addresses),
                transaction_address_observations=len(movements),
                unique_transaction_count=len(txids), addresses=addresses, movements=movements,
                warning='Cumulative received values are not stolen-fund totals; all addresses share one source group.')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('folder', type=Path)
    p.add_argument('output', type=Path)
    a = p.parse_args()
    report = summarize(a.folder)
    with a.output.open('x') as f:
        json.dump(report, f, indent=2)
        f.write('\n')
    print(json.dumps({k: report[k] for k in ('address_count', 'transaction_address_observations', 'unique_transaction_count')}))


if __name__ == '__main__':
    main()
