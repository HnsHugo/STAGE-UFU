"""Provider-audited descriptive quantities, not an asserted Real-CATS adapter."""
import argparse
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
from collect_binance_research_seed import helper


def describe(history):
    address = history['address']
    txs = history['transactions']
    audit = helper().check_history(address, txs, history['before'], history['after'], True)
    if not history['audit']['pagination_exhausted'] or not audit['coverage_complete_by_provider_counters']:
        raise ValueError('Complete stable provider history required')
    receipts = [t for t in txs if any(v.get('scriptpubkey_address') == address for v in t['vout'])]
    spends = [t for t in txs if any(v.get('prevout', {}).get('scriptpubkey_address') == address for v in t['vin'])]
    times = [t['status']['block_time'] for t in txs]
    day = lambda t: datetime.fromtimestamp(t['status']['block_time'], timezone.utc).date().isoformat()
    observed = audit['observed']
    return dict(address=address, observation_policy='All confirmed provider transactions at collection time',
                complete_by_provider_counters=True, cryptographic_inclusion_verified=False,
                transaction_number=len(txs), receipt_transactions=len(receipts), payment_transactions=len(spends),
                received_sat=observed['funded_txo_sum'], spent_input_sat=observed['spent_txo_sum'],
                balance_sat=observed['funded_txo_sum']-observed['spent_txo_sum'],
                lifetime_seconds=max(times)-min(times) if times else 0,
                first_confirmed_utc=datetime.fromtimestamp(min(times),timezone.utc).isoformat() if times else None,
                last_confirmed_utc=datetime.fromtimestamp(max(times),timezone.utc).isoformat() if times else None,
                active_utc_days=len({day(t) for t in txs}), receipt_utc_days=len({day(t) for t in receipts}),
                spending_utc_days=len({day(t) for t in spends}),
                input_slots=observed['spent_txo_count'], output_slots=observed['funded_txo_count'],
                model_compatible=False, training_label=history['source_record'].get('training_label','pending_evidence_review'))


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('history',type=Path)
    parser.add_argument('output',type=Path)
    args=parser.parse_args()
    if args.output.exists(): raise ValueError('Output must be new')
    raw=gzip.decompress(args.history.read_bytes()) if args.history.suffix == '.gz' else args.history.read_bytes()
    report=describe(json.loads(raw))
    report['history_sha256']=hashlib.sha256(args.history.read_bytes()).hexdigest()
    args.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
