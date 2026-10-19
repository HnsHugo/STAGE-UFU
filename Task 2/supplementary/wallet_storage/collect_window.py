"""Collect bounded history and measure activity in a fixed UTC window."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from statistics import median
from collect_addresses import load_seeds, write_json
from collect_history import sample, get_json


def checkpoint_getter(address, path, getter=get_json):
    """Reuse history pages only while live chain statistics match the anchor."""
    cache = json.loads(path.read_text()) if path.exists() else {
        'schema_version': 1, 'address': address, 'chain_stats': None, 'pages': {}}
    if cache.get('schema_version') != 1 or cache.get('address') != address:
        raise ValueError('Checkpoint mismatch')
    prefix = '/address/' + address

    def get(url):
        if url == prefix:
            data, evidence = getter(url)
            if data.get('address') != address:
                raise ValueError('Address stats response mismatch')
            if cache['chain_stats'] is None:
                cache['chain_stats'] = data['chain_stats']
                write_json(path, cache)
            elif cache['chain_stats'] != data['chain_stats']:
                raise ValueError('Chain stats changed since checkpoint; use a new output directory')
            return data, evidence
        if not url.startswith(prefix + '/txs/chain'):
            raise ValueError('Unexpected checkpoint request')
        if url in cache['pages']:
            page = cache['pages'][url]
            return page['data'], page['evidence']
        data, evidence = getter(url)
        cache['pages'][url] = {'data': data, 'evidence': evidence}
        write_json(path, cache)
        return data, evidence
    return get


def prepare_output(input_path, output, start, end):
    expected = {'schema_version': 2,
                'input_sha256': hashlib.sha256(input_path.read_bytes()).hexdigest(),
                'start_utc_inclusive': start.isoformat(), 'end_utc_exclusive': end.isoformat()}
    output.mkdir(parents=True, exist_ok=True)
    path = output / 'manifest.json'
    if path.exists():
        if json.loads(path.read_text()) != expected:
            raise ValueError('Input, dates or collector version changed; use a new output directory')
    else:
        if any(output.iterdir()):
            raise ValueError('Nonempty output without manifest')
        write_json(path, expected)
        (output / 'input.csv').write_bytes(input_path.read_bytes())


def parse_utc(value):
    date = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if date.utcoffset() is None or date.utcoffset().total_seconds() != 0:
        raise ValueError('Window boundaries must explicitly use UTC')
    return date


def measure(observation, start, end):
    if start >= end:
        raise ValueError('Start must precede end')
    rows = observation['transactions']
    if len({r['txid'] for r in rows}) != len(rows):
        raise ValueError('Duplicate transaction ID')
    selected = [r for r in rows if start <= parse_utc(r['block_time_utc']) < end]
    # Do not infer coverage from one old timestamp: block times can be nonmonotone.
    covered = observation['summary']['coverage'] == 'count_matches_stable_stats'
    metrics = None
    if covered:
        outgoing = [r for r in selected if r['address_spent_sat'] > 0]
        metrics = {
            'transaction_count': len(selected),
            'transactions_per_day': len(selected) / ((end-start).total_seconds()/86400),
            'active_utc_days': len({parse_utc(r['block_time_utc']).date() for r in selected}),
            'received_sat': sum(r['address_received_sat'] for r in selected),
            'spent_sat': sum(r['address_spent_sat'] for r in selected),
            'spending_transaction_count': len(outgoing),
            'receive_only_transaction_count': sum(r['address_spent_sat'] == 0 for r in selected),
            'median_spending_fee_rate_sat_vb': median(r['fee_rate_sat_vb'] for r in outgoing) if outgoing else None,
        }
    return {'start_utc_inclusive': start.isoformat(), 'end_utc_exclusive': end.isoformat(),
            'window_coverage': 'count_consistent_full_history' if covered else 'unverified',
            'observed_window_transaction_count': len(selected), 'metrics': metrics,
            'transactions': selected}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--start', required=True)
    parser.add_argument('--end', required=True)
    parser.add_argument('--max-pages', type=int, default=1)
    args = parser.parse_args()
    try:
        start, end = parse_utc(args.start), parse_utc(args.end)
        if start >= end or end > datetime.now(timezone.utc):
            raise ValueError('Require start < end <= current time')
        if not 1 <= args.max_pages <= 100:
            raise ValueError('max-pages must be in 1..100')
        seeds = load_seeds(args.input)
        prepare_output(args.input, args.output_dir, start, end)
        errors = 0
        for seed in seeds:
            try:
                getter = checkpoint_getter(seed['address'],
                    args.output_dir / (seed['address'] + '.pages.json'))
                observation = sample(seed['address'], args.max_pages, getter=getter)
                result = {'seed': seed, 'storage_prediction': 'unknown',
                          'storage_label_window_validity': 'unverified',
                          'history': observation, 'window': measure(observation, start, end)}
            except Exception as exc:
                errors += 1
                result = {'seed': seed, 'collection_status': 'error', 'error': str(exc), 'metrics': None}
            write_json(args.output_dir / (seed['address'] + '.json'), result)
        print(json.dumps({'addresses': len(seeds), 'errors': errors}))
        if errors:
            parser.exit(1, 'Some addresses failed; results retain errors.\n')
    except (OSError, ValueError) as exc:
        parser.exit(1, str(exc) + '\n')


if __name__ == '__main__':
    main()
