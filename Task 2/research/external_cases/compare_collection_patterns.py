"""Compare pinned histories in equal UTC-day windows, without fitting a model."""
from collections import Counter
from datetime import datetime, timezone
import argparse
import gzip
import hashlib
import json
from pathlib import Path

from collection_patterns import check_history, describe


def day_start(day):
    return int(datetime.strptime(day, '%Y-%m-%d').replace(tzinfo=timezone.utc).timestamp())


def busiest_day(address, transactions, cutoff):
    """Retrospective stress window; maximize receipts, breaking ties by earliest day."""
    counts = Counter(datetime.fromtimestamp(tx['status']['block_time'], timezone.utc).date().isoformat()
                     for tx in transactions if tx['status']['block_time'] < cutoff
                     and any(o.get('scriptpubkey_address') == address and o['value'] > 0 for o in tx['vout']))
    if not counts:
        raise ValueError('No receipt before stress-window selection cutoff')
    return min(counts, key=lambda day: (-counts[day], day))


def compare(registry_path):
    registry = json.loads(registry_path.read_text())
    rows, tx_sets, input_sets = [], [], []
    for record in registry['records']:
        path = registry_path.parent / record['history_file']
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != record['history_sha256']:
            raise ValueError('History checksum mismatch')
        observation = json.loads(gzip.decompress(raw))
        address = record['address']
        if observation['address'] != address:
            raise ValueError('Address mismatch')
        audit = check_history(address, observation['transactions'], observation['before'], observation['after'],
                              observation['audit']['pagination_exhausted'])
        if not audit['coverage_complete_by_provider_counters']:
            raise ValueError('Incomplete provider history')
        # Validate the full confirmed history before selecting a window.
        describe(address, observation['transactions'], float('inf'))
        windows = [(day, 'incident_calendar_day') for day in record['calendar_days']]
        if record.get('stress_selection_before'):
            windows.append((busiest_day(address, observation['transactions'],
                                        day_start(record['stress_selection_before'])),
                            'retrospective_busiest_receipt_day'))
        for day, policy in windows:
            start = day_start(day)
            end = start + 86400
            features = describe(address, observation['transactions'], end, start=start)
            count = features['receipt_transaction_count']
            features['single_output_external_funding_share'] = (
                features['single_output_external_funding_transaction_count']/count if count else None)
            rows.append(dict(name=record['name'], address=address, group=record['group'],
                             context=record['context'], source_url=record['source_url'],
                             label_available_at=None, hardware_control='unknown',
                             history_sha256=record['history_sha256'], provider_audit=audit,
                             day_utc=day, selection_policy=policy, window_seconds=86400,
                             features=features))
            selected = [t for t in observation['transactions'] if start <= t['status']['block_time'] < end]
            tx_sets.append({t['txid'] for t in selected})
            input_sets.append({i['prevout']['scriptpubkey_address'] for t in selected for i in t['vin']
                               if i.get('prevout') and i['prevout'].get('scriptpubkey_address')})
    overlaps = [dict(row_a=i, row_b=j, same_group=rows[i]['group'] == rows[j]['group'],
                     same_address=rows[i]['address'] == rows[j]['address'],
                     shared_transactions=len(tx_sets[i] & tx_sets[j]),
                     shared_input_addresses=len(input_sets[i] & input_sets[j]))
                for i in range(len(rows)) for j in range(i+1, len(rows))]
    report = dict(schema_version=1, registry_sha256=hashlib.sha256(registry_path.read_bytes()).hexdigest(),
                scope='Retrospective descriptive comparison; no classifier or independent accuracy estimate',
                independent_sample_policy='Two source-attributed incident groups and one comparison entity; windows are not independent cases',
                rows=rows, overlap_checks=overlaps,
                limits=['Matched duration does not match address age, fee market, volume or observation date',
                        'EFF is a documented donation recipient, not certified legitimate funds',
                        'One convenience comparison entity cannot establish specificity or precision',
                        'Source-to-hardware mapping and historical label availability remain unverified',
                        'Busiest-day selection is retrospective and cannot support prospective detection claims',
                        'Same-block confirmation timestamps do not establish simultaneous broadcast',
                        'Single-output funding does not establish complete source-address depletion',
                        'Exact non-overlap does not establish independence of entities or incidents'])
    if registry.get('schema_version', 1) >= 2:
        # New cohorts have explicit counts; schema-1 reports stay reproducible.
        incidents = {r['group'] for r in rows if r['context'] == 'incident'}
        comparisons = {r['group'] for r in rows if r['context'] == 'documented_donation_comparison'}
        if incidents & comparisons:
            raise ValueError('A split group cannot be both an incident and comparison entity')
        report['schema_version'] = 2
        report['group_summary'] = dict(incident_groups=len(incidents), comparison_entities=len(comparisons),
                                     address_count=len({r['address'] for r in rows}), observation_windows=len(rows))
        report['independent_sample_policy'] = (
            f'{len(incidents)} source-attributed incident groups and {len(comparisons)} '
            'documented comparison entities; windows are repeated observations, not independent cases')
        report['limits'][1:3] = [
            'Donation-purpose evidence does not certify every received fund as legitimate',
            'A small convenience comparison cohort cannot establish specificity or precision']
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('registry', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    result = compare(args.registry)
    with args.output.open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    for row in result['rows']:
        print(row['name'], row['day_utc'], json.dumps(row['features']))


if __name__ == '__main__':
    main()
