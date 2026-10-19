"""Collect bounded confirmed address history and auditable descriptive features."""
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from collect_addresses import FIELDS, load_seeds, write_json

BASE = 'https://blockstream.info/api'
TX_FIELDS = 'address txid block_height block_time_utc address_received_sat address_spent_sat address_net_sat transaction_fee_sat vsize_vb fee_rate_sat_vb input_count output_count'.split()
SUMMARY_FIELDS = FIELDS + 'collection_status chain_tx_count_before chain_tx_count_after confirmed_balance_sat_before observed_tx_count coverage stop_reason oldest_observed_utc newest_observed_utc observed_received_sat observed_spent_sat error'.split()


def utc(timestamp=None):
    return datetime.fromtimestamp(timestamp, timezone.utc).isoformat() if timestamp is not None else datetime.now(timezone.utc).isoformat()


def get_json(path):
    url = BASE + path
    for attempt in range(3):
        try:
            with urlopen(Request(url, headers={'User-Agent': 'UFU-address-research/0.1'}), timeout=30) as response:
                data = response.read()
            return json.loads(data), {'url': url, 'retrieved_at_utc': utc(), 'response_sha256': hashlib.sha256(data).hexdigest()}
        except HTTPError as exc:
            if exc.code not in (429, 500, 502, 503, 504) or attempt == 2:
                raise
        except (URLError, TimeoutError):
            if attempt == 2:
                raise
        time.sleep(2 ** (attempt + 1))
    raise RuntimeError('Request failed')


def transaction_row(address, tx):
    if tx['status'].get('confirmed') is not True:
        raise ValueError('Unconfirmed transaction on chain endpoint')
    received = sum(v['value'] for v in tx['vout'] if v.get('scriptpubkey_address') == address)
    spent = sum(v['prevout']['value'] for v in tx['vin'] if v.get('prevout') and v['prevout'].get('scriptpubkey_address') == address)
    if not received and not spent:
        raise ValueError('Transaction does not involve queried address')
    vsize = (tx['weight'] + 3) // 4
    if vsize <= 0 or tx['fee'] < 0:
        raise ValueError('Invalid transaction size/fee')
    return dict(zip(TX_FIELDS, [address, tx['txid'], tx['status']['block_height'],
        utc(tx['status']['block_time']), received, spent, received - spent,
        tx['fee'], vsize, tx['fee'] / vsize, len(tx['vin']), len(tx['vout'])]))


def sample(address, max_pages=1, getter=get_json, sleeper=time.sleep):
    prefix = '/address/' + address
    before, evidence = getter(prefix)
    if before.get('address') != address:
        raise ValueError('Address stats response mismatch')
    requests = [evidence]
    transactions = []
    seen = set()
    cursor = ''
    reason = 'page_limit'
    for _ in range(max_pages):
        sleeper(1)
        page, evidence = getter(prefix + '/txs/chain' + cursor)
        requests.append(evidence)
        if not isinstance(page, list) or len(page) > 25:
            raise ValueError('Invalid history page')
        for tx in page:
            if tx['txid'] in seen:
                raise ValueError('Repeated txid across history pages')
            seen.add(tx['txid'])
            transactions.append(transaction_row(address, tx))
        if len(page) < 25:
            reason = 'endpoint_exhausted'
            break
        cursor = '/' + page[-1]['txid']
    sleeper(1)
    after, evidence = getter(prefix)
    requests.append(evidence)
    if after.get('address') != address:
        raise ValueError('Address stats response mismatch')
    first = before['chain_stats']
    last = after['chain_stats']
    count = len(transactions)
    if first != last:
        coverage = 'stats_changed'
    elif count > last['tx_count']:
        coverage = 'inconsistent_count'
    elif count == last['tx_count']:
        coverage = 'count_matches_stable_stats'
    else:
        coverage = 'partial'
    dates = sorted(t['block_time_utc'] for t in transactions)
    summary = {'collection_status': 'ok', 'chain_tx_count_before': first['tx_count'],
        'chain_tx_count_after': last['tx_count'],
        'confirmed_balance_sat_before': first['funded_txo_sum'] - first['spent_txo_sum'],
        'observed_tx_count': count, 'coverage': coverage, 'stop_reason': reason,
        'oldest_observed_utc': dates[0] if dates else '', 'newest_observed_utc': dates[-1] if dates else '',
        'observed_received_sat': sum(t['address_received_sat'] for t in transactions),
        'observed_spent_sat': sum(t['address_spent_sat'] for t in transactions), 'error': ''}
    return {'schema_version': 1, 'source': 'Blockstream Esplora', 'address': address,
        'max_pages': max_pages, 'requests': requests, 'address_stats_before': before,
        'address_stats_after': after, 'transactions': transactions, 'summary': summary}


def write_csv(path, fields, rows):
    temp = path.with_suffix('.tmp')
    with temp.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    temp.replace(path)


def run(input_path, output, max_pages=1, getter=get_json, sleeper=time.sleep):
    seeds = load_seeds(input_path)
    digest = hashlib.sha256(input_path.read_bytes()).hexdigest()
    output.mkdir(parents=True, exist_ok=True)
    manifest_path = output / 'manifest.json'
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
        if manifest['input_sha256'] != digest or manifest['max_pages'] != max_pages:
            raise ValueError('Input or max-pages changed; use a new output directory')
    else:
        if any(output.iterdir()):
            raise ValueError('Output directory is nonempty without a manifest')
        manifest = {'schema_version': 1, 'input_sha256': digest, 'max_pages': max_pages,
                    'started_at_utc': utc(), 'records': []}
        write_json(manifest_path, manifest)
    (output / 'input.csv').write_bytes(input_path.read_bytes())
    summaries, tx_rows, records = [], [], []
    for seed in seeds:
        address = seed['address']
        path = output / (address + '.json')
        if path.exists():
            observation = json.loads(path.read_text())
            if observation.get('address') != address or observation.get('max_pages') != max_pages or observation.get('source') != 'Blockstream Esplora':
                raise ValueError('Cached observation mismatch')
            cached = True
        else:
            try:
                observation = sample(address, max_pages, getter, sleeper)
            except (URLError, TimeoutError, ValueError, KeyError, TypeError) as exc:
                summaries.append({**seed, 'collection_status': 'error', 'error': str(exc)})
                records.append({'address': address, 'status': 'error', 'error': str(exc)})
                observation = None
            else:
                write_json(path, observation)
                cached = False
        if observation is not None:
            summaries.append({**seed, **observation['summary']})
            tx_rows.extend(observation['transactions'])
            records.append({'address': address, 'status': 'ok', 'cached': cached, 'snapshot': path.name})
        write_csv(output / 'address_summary.csv', SUMMARY_FIELDS, summaries)
        write_csv(output / 'transactions.csv', TX_FIELDS, tx_rows)
        manifest['records'] = records
        manifest['updated_at_utc'] = utc()
        write_json(manifest_path, manifest)
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--max-pages', type=int, default=1, help='25 confirmed transactions/page; default 1')
    args = parser.parse_args()
    if not 1 <= args.max_pages <= 100:
        parser.error('--max-pages must be in 1..100')
    try:
        records = run(args.input, args.output_dir, args.max_pages)
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(1, f'Collection failed: {exc}\n')
    errors = sum(r['status'] == 'error' for r in records)
    print(json.dumps({'addresses': len(records), 'ok': len(records)-errors, 'errors': errors}))
    if errors:
        parser.exit(1, 'Some addresses failed; rerun the same input/output to retry.\n')


if __name__ == '__main__':
    main()
