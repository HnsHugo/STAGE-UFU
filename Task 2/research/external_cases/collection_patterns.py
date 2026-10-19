"""Collect public address histories and describe cutoff-safe collection patterns.

No hardware, ownership, victim or theft labels are inferred. Transaction input
co-occurrence is not an allocation of input value to a particular output.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import statistics
import sys
import urllib.request

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'coldcard'))
from collect_theft_seeds import check_history


def get(url):
    with urllib.request.urlopen(url, timeout=20) as response:
        return json.load(response)


def collect(address, output, base, max_pages=20):
    """Persist a new compact snapshot; counter consistency is not inclusion proof."""
    if output.exists():
        raise ValueError('Output already exists')
    if max_pages < 1:
        raise ValueError('Positive page limit required')
    before = get(f'{base}/address/{address}')
    transactions, seen, cursor, exhausted = [], set(), '', False
    for _ in range(max_pages):
        page = get(f'{base}/address/{address}/txs/chain' + (f'/{cursor}' if cursor else ''))
        if not page:
            exhausted = True
            break
        for tx in page:
            if tx['txid'] in seen:
                raise ValueError('Repeated transaction during pagination')
            seen.add(tx['txid'])
            transactions.append(tx)
        cursor = page[-1]['txid']
    after = get(f'{base}/address/{address}')
    if before['address'] != address or after['address'] != address:
        raise ValueError('Provider address mismatch')
    audit = check_history(address, transactions, before, after, exhausted)
    if not audit['coverage_complete_by_provider_counters']:
        raise ValueError('History incomplete or provider counters changed')
    observation = dict(address=address, provider=base, before=before, after=after,
                       collected_at=datetime.now(timezone.utc).isoformat(),
                       transactions=transactions, audit=audit,
                       interpretation='Public provider observations; address roles require separate evidence')
    raw = gzip.compress((json.dumps(observation, sort_keys=True, separators=(',', ':')) + '\n').encode(), mtime=0)
    with output.open('xb') as stream:
        stream.write(raw)
    return {'file': output.name, 'sha256': hashlib.sha256(raw).hexdigest(),
            'bytes': len(raw), 'audit': audit}


def describe(address, transactions, cutoff, start=None):
    """Use confirmed block timestamps strictly before cutoff, not current UTXOs.

    With start, activity uses [start, cutoff), while balance includes earlier
    transactions. A single-output receipt does not prove full source depletion.
    """
    if start is not None and start >= cutoff:
        raise ValueError('Window start must precede cutoff')
    seen, consumed = set(), set()
    inputs_seen, destinations = set(), set()
    receipts, spends, rates = [], [], []
    blocks = Counter()
    received = spent = single_output = missing_addresses = balance = 0
    for tx in transactions:
        tid = tx['txid']
        if tid in seen:
            raise ValueError('Duplicate transaction')
        seen.add(tid)
        if not tx['status']['confirmed']:
            raise ValueError('Confirmed history required')
        when = tx['status']['block_time']
        if when >= cutoff:
            continue
        prevouts = [item.get('prevout') or {} for item in tx['vin']]
        for value in [o['value'] for o in tx['vout']] + [o['value'] for o in prevouts if o]:
            if type(value) is not int or value < 0:
                raise ValueError('Nonnegative integer satoshis required')
        incoming = sum(o['value'] for o in tx['vout'] if o.get('scriptpubkey_address') == address)
        outgoing = sum(o.get('value', 0) for o in prevouts if o.get('scriptpubkey_address') == address)
        if not any(o.get('scriptpubkey_address') == address for o in tx['vout'] + prevouts):
            raise ValueError('Unrelated transaction')
        for item in tx['vin']:
            if not item.get('prevout'):
                continue
            outpoint = (item['txid'], item['vout'])
            if outpoint in consumed:
                raise ValueError('Repeated consumed outpoint')
            consumed.add(outpoint)
        balance += incoming - outgoing
        if start is not None and when < start:
            continue
        received += incoming
        spent += outgoing
        if incoming:
            receipts.append(when)
            blocks[tx['status']['block_height']] += 1
            inputs_seen.update(o['scriptpubkey_address'] for o in prevouts if o.get('scriptpubkey_address'))
            missing_addresses += sum(not o.get('scriptpubkey_address') for o in prevouts)
            if len(tx['vout']) == 1 and prevouts and all(o.get('scriptpubkey_address') not in (None, address) for o in prevouts):
                single_output += 1
            if all(prevouts):
                if type(tx['weight']) is not int or tx['weight'] <= 0 or type(tx['fee']) is not int or tx['fee'] < 0:
                    raise ValueError('Positive integer weight and nonnegative integer fee required')
                rates.append(tx['fee'] / ((tx['weight'] + 3) // 4))
        if outgoing:
            spends.append(when)
            destinations.update(o['scriptpubkey_address'] for o in tx['vout']
                                if o.get('scriptpubkey_address') and o['scriptpubkey_address'] != address)
    if balance < 0:
        raise ValueError('Negative observed balance; incomplete or inconsistent prefix')
    return dict(receipt_transaction_count=len(receipts), spending_transaction_count=len(spends),
                received_sat=received, spent_input_sat=spent, observed_balance_sat=balance,
                funding_transaction_distinct_input_addresses=len(inputs_seen),
                funding_transaction_missing_input_address_slots=missing_addresses,
                single_output_external_funding_transaction_count=single_output,
                receipt_confirmation_span_seconds=max(receipts)-min(receipts) if receipts else None,
                receipt_top_block_transaction_share=max(blocks.values())/len(receipts) if receipts else None,
                incoming_transaction_median_fee_rate_sat_vbyte=statistics.median(rates) if rates else None,
                spending_transaction_distinct_other_output_addresses=len(destinations))


def analyze(registry_path, history_dir, cutoff_text, output):
    parsed = datetime.fromisoformat(cutoff_text.replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        raise ValueError('Timezone-aware cutoff required')
    cutoff = int(parsed.timestamp())
    registry = json.loads(registry_path.read_text())
    rows = []
    for record in registry['records']:
        if not record['include_in_pilot']:
            continue
        path = history_dir / (record['address'] + '.json.gz')
        raw = path.read_bytes()
        observation = json.loads(gzip.decompress(raw))
        address = record['address']
        if observation['address'] != address:
            raise ValueError('History address mismatch')
        audit = check_history(address, observation['transactions'], observation['before'], observation['after'],
                              observation['audit']['pagination_exhausted'])
        if not audit['coverage_complete_by_provider_counters']:
            raise ValueError('History counter audit failed')
        rows.append(dict(address=address, case_group=record['case_group'], role=record['role'],
                         evidence_level=record['evidence_level'], hardware_control=record['hardware_control'],
                         file=path.name, history_sha256=hashlib.sha256(raw).hexdigest(),
                         provider=observation['provider'], collected_at=observation['collected_at'], audit=audit,
                         features=describe(address, observation['transactions'], cutoff)))
    report = dict(schema_version=1, registry_sha256=hashlib.sha256(registry_path.read_bytes()).hexdigest(),
                  cutoff_exclusive_utc=cutoff_text, rows=rows,
                  scope='Retrospective descriptive pilot; no trained model or independent accuracy estimate',
                  limits=['Case attribution is a source assertion, not independently confirmed by this analysis',
                          'No source-address hardware, ownership, victim or illicit labels are propagated',
                          'Block timestamps are not transaction arrival times',
                          'All pilot addresses share one incident group',
                          'Co-occurring transaction inputs do not allocate value to individual outputs',
                          'Single-output transactions do not prove complete source-address balance depletion',
                          'Incoming transaction fee rates do not measure receiver fee policy',
                          'Historical prefix lacks verified label availability at the cutoff'])
    with output.open('x') as stream:
        json.dump(report, stream, indent=2)
        stream.write('\n')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    collection = commands.add_parser('collect')
    collection.add_argument('address')
    collection.add_argument('output', type=Path)
    collection.add_argument('--base', default='https://blockstream.info/api')
    collection.add_argument('--max-pages', type=int, default=20)
    analysis = commands.add_parser('analyze')
    analysis.add_argument('registry', type=Path)
    analysis.add_argument('histories', type=Path)
    analysis.add_argument('cutoff')
    analysis.add_argument('output', type=Path)
    args = parser.parse_args()
    if args.command == 'collect':
        result = collect(args.address, args.output, args.base.rstrip('/'), args.max_pages)
    else:
        result = analyze(args.registry, args.histories, args.cutoff, args.output)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
