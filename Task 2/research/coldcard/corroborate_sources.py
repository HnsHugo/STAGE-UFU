"""Compare case-source evidence with pinned external chain reconstructions."""
import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime
from decimal import Decimal
import gzip
import hashlib
import io
import json
from pathlib import Path

from build_source_registry import artifacts, digest, json_bytes
import source_cohort as cohort


def btc_sat(text):
    value = Decimal(text) * 100_000_000
    if not value.is_finite() or value < 0 or value != value.to_integral_value():
        raise ValueError('Invalid integer-satoshi BTC amount')
    return int(value)


def compare(record, payment, observations, addresses, inputs, transactions, collector):
    gross = sum(row['spent_input_value_sat'] for row in observations)
    values = Counter(row['spent_input_value_sat'] for row in observations)
    listed = [r for r in addresses if r['address'] == record['address']]
    observed = [r for r in inputs if r['address'] == record['address']
                and r['sweep_txid'] == record['payment_txid']]
    reconstructed = [r for r in transactions if r['txid'] == record['payment_txid']]
    input_exact = (bool(observed)
                   and Counter(btc_sat(r['btc_lost']) for r in observed) == values
                   and all(int(r['block']) == record['cutoff_height']
                           and r['collector'] == collector for r in observed))
    fields = {}
    external_classification = None
    if len(reconstructed) == 1:
        other = reconstructed[0]
        actual = dict(block_height=payment['status']['block_height'],
                      block_hash=payment['status']['block_hash'],
                      input_count=len(payment['vin']),
                      input_value_sats=sum(i['prevout']['value'] for i in payment['vin']),
                      output_count=len(payment['vout']),
                      cluster_output_value_sats=sum(o['value'] for o in payment['vout']
                          if o.get('scriptpubkey_address') == collector),
                      fee_sats=payment['fee'],destination_or_intermediate_address=collector)
        for name,value in actual.items():
            fields[name] = (int(other[name]) == value if type(value) is int else other[name] == value)
        fields['block_time_utc'] = (int(datetime.fromisoformat(other['block_time_utc'].replace('Z','+00:00')).timestamp())
                                    == payment['status']['block_time'])
        external_classification = other['classification']
    address_metadata = any(btc_sat(r['btc_lost']) == gross and int(r['utxos']) == len(observations)
                           for r in listed)
    corroborated = bool(listed) and address_metadata and input_exact and bool(fields) and all(fields.values())
    return dict(source_id=record['pilot_id'],address_sha256=record['address_sha256'],
                payment_txid_sha256=digest(record['payment_txid'].encode()),
                cutoff_height=record['cutoff_height'],original_case_relation='graph_candidate',
                case_relation='source_attributed' if corroborated else 'graph_candidate',
                observed_input_count=len(observations),observed_input_value_sat=gross,
                somax_address_membership=bool(listed),somax_address_rows=len(listed),
                somax_gross_value_and_utxo_count_agree=address_metadata,
                somax_payment_input_rows=len(observed),somax_payment_input_value_multiset_agrees=input_exact,
                external_previous_outpoint_ids_available=False,
                alva_payment_rows=len(reconstructed),alva_integer_and_anchor_fields_agree=fields,
                external_transaction_classification=external_classification,
                both_external_reconstructions_agree=corroborated,
                independently_verified_compromise_label=None,hardware_seed_origin_label=None,
                hardware_signing_at_event_label=None,supervised_training_eligible=False)


def build(protocol_path, inputs):
    protocol = json.loads(protocol_path.read_bytes())
    root = protocol_path.parent
    for name in ('cohort_protocol','checkpoint','registry_protocol'):
        path = root / protocol[name+'_file']
        if digest(path.read_bytes()) != protocol[name+'_sha256']:
            raise ValueError('Pinned local input changed: '+name)
    _, records = cohort.plan(root/protocol['cohort_protocol_file'])
    state = json.loads((root/protocol['checkpoint_file']).read_bytes())
    cohort.validate(state,root/protocol['cohort_protocol_file'],records)
    external = {}
    for source in protocol['sources']:
        raw = (inputs/source['local_file']).read_bytes()
        blob = hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        if digest(raw) != source['sha256'] or blob != source['git_blob_sha']:
            raise ValueError('Pinned external snapshot changed: '+source['id'])
        if source['local_file'].endswith('.csv'):
            external[source['id']] = list(csv.DictReader(io.StringIO(raw.decode(),newline='')))
    registry = root/protocol['registry_protocol_file']
    registry_protocol = json.loads(registry.read_bytes())
    files,_ = artifacts(registry)
    grouped = defaultdict(list)
    for line in files['input_evidence.jsonl'].decode().splitlines():
        row = json.loads(line)
        if row['scope'] == 'candidate_window':
            grouped[row['source_address'],row['payment_txid']].append(row)
    history = json.loads(gzip.decompress((root/registry_protocol['history_file']).read_bytes()))
    payments = {tx['txid']:tx for tx in history['transactions']}
    rows = [compare(record,payments[record['payment_txid']],
                    grouped[record['address'],record['payment_txid']],
                    external['somax_address'],external['somax_utxo'],external['alva_tx'],
                    registry_protocol['collector_address']) for record in records]
    summary = dict(source_count=len(rows),
                   somax_address_matches=sum(r['somax_address_membership'] for r in rows),
                   somax_value_count_agreement=sum(r['somax_gross_value_and_utxo_count_agree'] for r in rows),
                   somax_input_multiset_agreement=sum(r['somax_payment_input_value_multiset_agrees'] for r in rows),
                   alva_exact_payment_agreement=sum(bool(r['alva_integer_and_anchor_fields_agree']) and
                       all(r['alva_integer_and_anchor_fields_agree'].values()) for r in rows),
                   corroborated_case_sources=sum(r['both_external_reconstructions_agree'] for r in rows),
                   compared_input_observations=sum(r['observed_input_count'] for r in rows),
                   local_input_value_sat=sum(r['observed_input_value_sat'] for r in rows),
                   verified_compromise_labels=0,verified_hardware_labels=0,
                   original_predictors_or_labels_changed=False,training_performed=False)
    result = dict(schema_version=1,reviewed_on=protocol['reviewed_on'],
                  protocol_sha256=digest(protocol_path.read_bytes()),
                  checkpoint_sha256=protocol['checkpoint_sha256'],summary=summary,rows=rows,
                  source_snapshots=protocol['sources'],
                  attribution='SomaxBT, coldcard-drain-addresses; Alvaro P., coldcard-weak-rng-research. See pinned URLs and methods in the protocol.',
                  independence=protocol['independence'],
                  limitations=['Published chain reconstruction corroborates case relation, not authorization or the device behind an address',
                               'The external per-UTXO CSV lacks prevout transaction IDs/indexes: value multiset agreement is not exact external outpoint verification',
                               'External classification/confidence strings are author assertions, not calibrated theft probabilities',
                               'Commit timestamps pin versions; public label availability at those timestamps is not established',
                               'All sources belong to one incident group; no independently verified controls or supervised model'])
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=('build','verify'))
    parser.add_argument('protocol',type=Path)
    parser.add_argument('inputs',type=Path)
    parser.add_argument('output',type=Path)
    args = parser.parse_args()
    result = build(args.protocol,args.inputs)
    raw = json_bytes(result)
    if args.command == 'build':
        args.output.mkdir(parents=True,exist_ok=False)
        (args.output/'comparison.json').write_bytes(raw)
    elif (args.output/'comparison.json').read_bytes() != raw:
        raise ValueError('External corroboration reproduction mismatch')
    print(json.dumps(result['summary'],indent=2))


if __name__ == '__main__':
    main()
