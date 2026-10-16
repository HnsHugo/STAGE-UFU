"""Retrospective provider-based address profiles at a fixed label snapshot."""
import argparse
from datetime import date, datetime, timezone
import hashlib
import json
from pathlib import Path


def instant(value):
    date = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if date.utcoffset() is None:
        raise ValueError('Timezone required')
    return date.astimezone(timezone.utc)


def features_at(document, snapshot):
    history = document['history']
    transactions = history['transactions']
    before = history['address_stats_before']['chain_stats']
    after = history['address_stats_after']['chain_stats']
    if (before != after or len(transactions) != before['tx_count']
            or history['summary']['coverage'] != 'count_matches_stable_stats'):
        raise ValueError('Full count-consistent saved history required')
    if len({tx['txid'] for tx in transactions}) != len(transactions):
        raise ValueError('Duplicate transaction')
    included = []
    for tx in transactions:
        if tx['address'] != document['seed']['address']:
            raise ValueError('Address mismatch')
        for field in ['address_received_sat', 'address_spent_sat']:
            if type(tx[field]) is not int or tx[field] < 0:
                raise ValueError('Nonnegative integer satoshis required')
        if instant(tx['block_time_utc']) <= snapshot:
            included.append(tx)
    received = sum(t['address_received_sat'] for t in included)
    spent = sum(t['address_spent_sat'] for t in included)
    if spent > received:
        raise ValueError('Negative reconstructed balance')
    last = max((instant(t['block_time_utc']) for t in included), default=None)
    return {'transaction_count': len(included), 'received_sat': received,
            'spent_sat': spent, 'balance_sat': received - spent,
            'days_since_last_observed_transaction': ((snapshot-last).total_seconds()/86400
                                                       if last else None)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('histories', type=Path, nargs='+')
    parser.add_argument('--snapshot', required=True)
    parser.add_argument('--label-publication-date', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    snapshot = instant(args.snapshot)
    publication = date.fromisoformat(args.label_publication_date)
    rows = []
    for path in args.histories:
        data = path.read_bytes(); doc = json.loads(data)
        rows.append({'address': doc['seed']['address'], 'entity': doc['seed']['entity_name'],
            'published_storage': doc['seed']['storage_type'], 'source_url': doc['seed']['storage_source_url'],
            'input_path': str(path), 'input_sha256': hashlib.sha256(data).hexdigest(),
            'features': features_at(doc, snapshot)})
    report = {'schema_version': 1, 'mode': 'retrospective_snapshot_not_training',
        'snapshot_utc': snapshot.isoformat(), 'label_publication_date': publication.isoformat(),
        'label_publication_time_utc': None,
        'label_available_by_snapshot': (publication < snapshot.date()
                                        if publication != snapshot.date() else None), 'addresses': rows,
        'limitations': ['Snapshot and publication are supplied from reviewed source claims, not authenticated by this script.',
            'History completeness uses later provider counts; this is retrospective reconstruction, not an as-observed deployment replay.',
            'No later transaction contributes to the returned features; current provider balance is never used.',
            'Block timestamps are confirmation metadata, not precise receipt or key-use times.',
            'Elapsed time since a transaction is not UTXO holding time or proof of cold storage.',
            'Three addresses from one source entity are not independent entities. No model is fitted.']}
    with args.output.open('x') as handle:
        json.dump(report, handle, indent=2); handle.write('\n')
    print(json.dumps(report, indent=2))
