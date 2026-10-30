"""Map curated first-person assertions without promoting forensic ground truth."""
import argparse
from datetime import datetime, timezone
import gzip
import json
from pathlib import Path

from build_source_registry import digest, json_bytes
import source_cohort as cohort


def map_report(report, records, payments, entries):
    if (report.get('declared_role') != 'owner_source'
            or not report.get('first_person_wallet_address')
            or not report.get('first_person_loss_report')):
        return dict(report_id=report['report_id'],status='insufficient_first_person_source_assertion')
    matches = [r for r in records if r['address'] == report.get('address')
               and r['payment_txid'] == report.get('payment_txid')]
    if len(matches) != 1:
        return dict(report_id=report['report_id'],status='no_unique_exact_source_payment_match')
    record = matches[0]
    payment = payments[record['payment_txid']]
    if ((payment['status']['block_height'],payment['status']['block_hash'])
            != (record['cutoff_height'],record['cutoff_block_hash'])):
        raise ValueError('Reference payment anchor mismatch')
    inputs = [i for i in payment['vin'] if (i.get('prevout') or {}).get('scriptpubkey_address') == report['address']]
    if not inputs:
        return dict(report_id=report['report_id'],status='claimed_address_is_not_a_payment_source')
    if sum(i['prevout']['value'] for i in payment['vin']) - sum(o['value'] for o in payment['vout']) != payment['fee']:
        raise ValueError('Reference payment value/fee mismatch')
    entry = entries[record['pilot_id']]
    received = {o['outpoint_id'] for tx in entry['prefix'] for o in tx['received']}
    spent = {o['outpoint_id'] for tx in entry['prefix'] for o in tx['spent']}
    prior_unspent = received - spent
    payment_outpoints = {digest(f"{i['txid']}:{i['vout']}".encode()) for i in inputs}
    if len(payment_outpoints) != len(inputs):
        raise ValueError('Repeated payment input')
    return dict(report_id=report['report_id'],status='mapped_first_person_report',
                source_id=record['pilot_id'],address_sha256=record['address_sha256'],
                payment_txid_sha256=digest(record['payment_txid'].encode()),
                reporter_id_sha256=report['reporter_id_sha256'],incident_group='coldcard_2026',
                event_confirmed_utc=datetime.fromtimestamp(payment['status']['block_time'],timezone.utc).isoformat(),
                cutoff_height=record['cutoff_height'],matched_input_count=len(inputs),
                observed_spent_input_sat=sum(i['prevout']['value'] for i in inputs),
                reference_payment_fee_sat=payment['fee'],
                known_prior_block_utxo_count=len(prior_unspent),
                known_prior_block_utxos_consumed=len(prior_unspent & payment_outpoints),
                consumes_all_known_prior_block_utxos=bool(prior_unspent) and prior_unspent <= payment_outpoints,
                reported_loss_label=1,
                reported_hardware_association_label='Coldcard' if any(
                    str(model).lower()=='coldcard' or str(model).lower().startswith('coldcard ')
                    for model in report.get('reported_hardware',[])) else None,
                declared_hardware_models=report.get('reported_hardware',[]),
                declared_setup_period=report.get('reported_setup_period'),
                declared_restore_period=report.get('reported_restore_period'),
                declared_firmware_version=report.get('firmware_version'),
                source_published_at=report.get('public_source_published_at'),
                label_available_at=report.get('label_available_at'),
                observed_by_project_on=report['observed_by_project_on'],
                evidence_grade='first_person_report_with_exact_chain_match',
                owner_identity_independently_verified=False,proof_of_control_verified=False,
                independently_verified_compromise_label=None,
                independently_verified_seed_origin_label=None,
                hardware_signing_at_event_label=None,
                verified_target_training_eligible=False,
                sources=report['sources'],caveats=report['caveats'])


def assertion_bytes(protocol, output, inputs, records):
    path = inputs/protocol['input_snapshot_file']
    if path.exists():
        raw = path.read_bytes()
    else:
        public = json.loads((output/'redacted_assertions.json').read_bytes())
        if public['original_input_sha256'] != protocol['input_snapshot_sha256']:
            raise ValueError('Redacted assertion snapshot fingerprint mismatch')
        assertions = public['assertions']
        for report in assertions['reports']:
            address_hash = report.pop('address_sha256')
            payment_hash = report.pop('payment_txid_sha256')
            matches = [r for r in records if r['address_sha256']==address_hash
                       and digest(r['payment_txid'].encode())==payment_hash]
            if len(matches)!=1:
                raise ValueError('Redacted identifiers cannot be reconstructed uniquely')
            report['address'] = matches[0]['address']
            report['payment_txid'] = matches[0]['payment_txid']
        raw = json_bytes(assertions)
    if digest(raw) != protocol['input_snapshot_sha256']:
        raise ValueError('Curated assertion snapshot checksum mismatch')
    return raw


def build(protocol_path, inputs):
    protocol = json.loads(protocol_path.read_bytes())
    root = protocol_path.parent.parent
    for name in ('cohort_protocol','checkpoint','source_registry_protocol'):
        path = root/protocol[name+'_file']
        if digest(path.read_bytes()) != protocol[name+'_sha256']:
            raise ValueError('Pinned input checksum mismatch: '+name)
    _,records = cohort.plan(root/protocol['cohort_protocol_file'])
    assertions = json.loads(assertion_bytes(protocol,protocol_path.parent,inputs,records))
    state = json.loads((root/protocol['checkpoint_file']).read_bytes())
    cohort.validate(state,root/protocol['cohort_protocol_file'],records)
    registry = json.loads((root/protocol['source_registry_protocol_file']).read_bytes())
    history = json.loads(gzip.decompress((root/registry['history_file']).read_bytes()))
    payments = {t['txid']:t for t in history['transactions']}
    rows, seen, duplicates = [],set(),0
    for report in assertions['reports']:
        key = (report['reporter_id_sha256'],report.get('address'),report.get('payment_txid'))
        if key in seen:
            duplicates += 1
            continue
        seen.add(key)
        rows.append(map_report(report,records,payments,state['entries']))
    accepted = [r for r in rows if r['status']=='mapped_first_person_report']
    return dict(schema_version=1,reviewed_on=protocol['reviewed_on'],
                protocol_sha256=digest(protocol_path.read_bytes()),
                assertion_snapshot_sha256=protocol['input_snapshot_sha256'],
                checkpoint_sha256=protocol['checkpoint_sha256'],rows=rows,
                summary=dict(distinct_reports_reviewed=len(rows),duplicate_reports_collapsed=duplicates,
                             exact_cohort_source_matches=len(accepted),
                             owner_reported_loss_sources=len({r['source_id'] for r in accepted}),
                             owner_reported_coldcard_sources=len({r['source_id'] for r in accepted if r['reported_hardware_association_label']}),
                             independently_verified_compromise_sources=0,independently_verified_device_sources=0,
                             unchanged_other_cohort_sources=len(records)-len({r['source_id'] for r in accepted}),
                             original_features_or_labels_changed=False,training_performed=False),
                lead_outcomes=assertions['lead_outcomes'],
                limitations=['First-person reports are sourced assertions; account identity/control and device origin are not independently verified',
                             'Duplicate posts by the same account are not independent confirmations',
                             'Publication and original label-availability timestamps remain unknown; do not backdate labels from transaction time',
                             'Spending known prior-block UTXOs does not establish depletion of an entire multi-address wallet or unauthorized intent',
                             'A matched report does not transfer its hardware/loss assertion to the other 499 sources'])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=('build','verify'))
    parser.add_argument('protocol',type=Path)
    parser.add_argument('inputs',type=Path)
    args=parser.parse_args()
    result=build(args.protocol,args.inputs)
    path=args.protocol.parent/'adjudication.json'
    raw=json_bytes(result)
    if args.command=='build':
        if path.exists():raise FileExistsError(path)
        path.write_bytes(raw)
    elif path.read_bytes()!=raw:
        raise ValueError('Owner-report reproduction mismatch')
    print(json.dumps(result['summary'],indent=2))


if __name__=='__main__':main()
