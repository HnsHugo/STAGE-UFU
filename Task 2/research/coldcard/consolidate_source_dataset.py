"""Join pinned source features and evidence; describe, without fitting a model."""
import argparse
from collections import Counter, defaultdict
from copy import deepcopy
import gzip
import json
import math
from pathlib import Path

from build_source_registry import digest, json_bytes
from prepayment_pilot import FEATURE_NAMES
import source_cohort as cohort


def index_rows(rows, key='source_id'):
    result = {}
    for row in rows:
        if row[key] in result:
            raise ValueError('Duplicate evidence key: ' + str(row[key]))
        result[row[key]] = row
    return result


def match_identity(row, record):
    expected = (record['address_sha256'], digest(record['payment_txid'].encode()),
                record['cutoff_height'])
    actual = tuple(row[k] for k in ('address_sha256', 'payment_txid_sha256', 'cutoff_height'))
    if actual != expected:
        raise ValueError('Evidence source/payment/cutoff mismatch')


def event_observation(record, entry, payment, comparison):
    if (payment['txid'] != record['payment_txid']
            or not payment['status']['confirmed']
            or (payment['status']['block_height'], payment['status']['block_hash'])
            != (record['cutoff_height'], record['cutoff_block_hash'])):
        raise ValueError('Reference payment anchor mismatch')
    received = {o['outpoint_id']: o['value_sat'] for t in entry['prefix'] for o in t['received']}
    spent = {o['outpoint_id'] for t in entry['prefix'] for o in t['spent']}
    unspent = {k: v for k, v in received.items() if k not in spent}
    inputs = [i for i in payment['vin']
              if (i.get('prevout') or {}).get('scriptpubkey_address') == record['address']]
    observed = {digest(f"{i['txid']}:{i['vout']}".encode()): i['prevout']['value'] for i in inputs}
    if (not inputs or len(observed) != len(inputs)
            or len(inputs) != comparison['observed_input_count']
            or sum(observed.values()) != comparison['observed_input_value_sat']):
        raise ValueError('Reference input count/value mismatch')
    if any(k in received and (k in spent or received[k] != value) for k, value in observed.items()):
        raise ValueError('Reference input conflicts with prior-block evidence')
    return dict(observed_input_count=len(inputs), observed_input_value_sat=sum(observed.values()),
                known_prior_block_utxo_count=len(unspent),
                known_prior_block_utxos_consumed=len(unspent.keys() & observed.keys()),
                known_prior_block_value_consumed_sat=sum(v for k, v in unspent.items() if k in observed),
                known_prior_block_utxos_not_consumed=len(unspent.keys() - observed.keys()),
                known_prior_block_value_not_consumed_sat=sum(v for k, v in unspent.items() if k not in observed),
                reference_inputs_outside_known_prior_block_utxos=len(observed.keys() - unspent.keys()),
                consumes_all_known_prior_block_utxos=bool(unspent) and unspent.keys() <= observed.keys())


def join(records, state, comparisons, reports, payments, case_id):
    evidence = index_rows(comparisons)
    ids = {r['pilot_id'] for r in records}
    if set(evidence) != ids or set(state['entries']) != ids:
        raise ValueError('Feature/evidence cohort coverage mismatch')
    report_ids = set()
    report_keys = set()
    grouped = defaultdict(list)
    targets = {r['pilot_id']: r for r in records}
    for report in reports:
        if report['status'] != 'mapped_first_person_report':
            continue
        if report['source_id'] not in targets:
            raise ValueError('Owner report outside cohort')
        match_identity(report, targets[report['source_id']])
        key = (report['reporter_id_sha256'], report['source_id'])
        if report['report_id'] in report_ids or key in report_keys:
            raise ValueError('Duplicate owner report/account-source evidence')
        if report['incident_group'] != case_id:
            raise ValueError('Owner report incident mismatch')
        if (report['reported_loss_label'] != 1
                or report['reported_hardware_association_label'] not in (None, 'Coldcard')
                or report['verified_target_training_eligible']
                or any(report[k] is not None for k in (
                    'independently_verified_compromise_label',
                    'independently_verified_seed_origin_label', 'hardware_signing_at_event_label'))):
            raise ValueError('Owner evidence tier changed; review required')
        report_ids.add(report['report_id'])
        report_keys.add(key)
        grouped[report['source_id']].append(deepcopy(report))
    rows = []
    for record in records:
        source_id = record['pilot_id']
        entry, comparison = state['entries'][source_id], evidence[source_id]
        match_identity(comparison, record)
        if (entry['status'] != 'complete' or set(entry['features']) != set(FEATURE_NAMES)
                or entry['compromise_label'] is not None or entry['hardware_label'] is not None):
            raise ValueError('Unexpected feature status/schema/label')
        if (comparison['case_relation'] != 'source_attributed'
                or not comparison['both_external_reconstructions_agree']
                or comparison['supervised_training_eligible']
                or any(comparison[k] is not None for k in (
                    'independently_verified_compromise_label', 'hardware_seed_origin_label',
                    'hardware_signing_at_event_label'))):
            raise ValueError('Case evidence tier changed; review required')
        owner = grouped[source_id]
        rows.append(dict(source_id=source_id, address_sha256=record['address_sha256'],
                         payment_txid_sha256=digest(record['payment_txid'].encode()),
                         incident_group=case_id, verified_entity_group=None,
                         cutoff_height=record['cutoff_height'], cutoff_block_hash=record['cutoff_block_hash'],
                         features=deepcopy(entry['features']),
                         history_evidence=dict(collected_at=entry['collected_at'],
                             raw_sha256=entry['raw_sha256'], prefix_sha256=digest(json_bytes(entry['prefix'])),
                             coverage_complete_by_provider_counters=True,
                             cryptographic_inclusion_verified=False),
                         case_evidence=dict(case_relation=comparison['case_relation'],
                             both_external_reconstructions_agree=True, label_available_at=None,
                             comparison_row_source_id=source_id),
                         event_evidence=event_observation(record, entry, payments[record['payment_txid']], comparison),
                         owner_reports=owner,
                         labels=dict(reported_loss=1 if owner else None,
                             reported_hardware_association='Coldcard' if any(
                                 r['reported_hardware_association_label'] == 'Coldcard' for r in owner) else None,
                             independently_verified_compromise=None, independently_verified_seed_origin=None,
                             hardware_signing_at_event=None),
                         verified_target_training_eligible=False))
    return rows


def distribution(values):
    present = sorted(v for v in values if v is not None)
    if any(type(v) not in (int, float) or not math.isfinite(v) for v in present):
        raise ValueError('Nonfinite/non-numeric feature')
    result = dict(nonmissing=len(present), missing=len(values)-len(present),
                  zeros=present.count(0), distinct_nonmissing=len(set(present)))
    for key, p in [('min', 0), ('p25', .25), ('p50', .5), ('p75', .75), ('p95', .95), ('max', 1)]:
        result[key] = present[max(0, math.ceil(p*len(present))-1)] if present else None
    return result


def summarize(rows, state):
    columns = {k: [r['features'][k] for r in rows] for k in FEATURE_NAMES}
    vectors = Counter(tuple(r['features'][k] for k in FEATURE_NAMES) for r in rows)
    prefixes = [state['entries'][r['source_id']]['prefix'] for r in rows]
    small = [o for prefix in prefixes for tx in prefix for o in tx['received'] if o['value_sat'] <= 1000]
    return dict(source_count=len(rows), feature_count=len(FEATURE_NAMES),
                incident_group_count=len({r['incident_group'] for r in rows}),
                verified_entity_group_count=0, documented_control_count=0,
                case_attributed_sources=sum(r['case_evidence']['case_relation']=='source_attributed' for r in rows),
                owner_reported_loss_sources=sum(r['labels']['reported_loss']==1 for r in rows),
                owner_reported_coldcard_sources=sum(r['labels']['reported_hardware_association']=='Coldcard' for r in rows),
                distinct_reporting_accounts=len({p['reporter_id_sha256'] for r in rows for p in r['owner_reports']}),
                verified_compromise_labels=0, verified_device_labels=0,
                sources_with_prior_spending=sum(r['features']['spending_tx_count']>0 for r in rows),
                sources_without_prior_spending=sum(r['features']['spending_tx_count']==0 for r in rows),
                sources_with_one_prior_transaction=sum(r['features']['confirmed_tx_count']==1 for r in rows),
                prior_address_transaction_observations=sum(r['features']['confirmed_tx_count'] for r in rows),
                distinct_prior_transaction_references=len({t['transaction_id'] for p in prefixes for t in p}),
                reference_input_observations=sum(r['event_evidence']['observed_input_count'] for r in rows),
                observed_source_input_value_sat=sum(r['event_evidence']['observed_input_value_sat'] for r in rows),
                sources_consuming_all_known_prior_utxos=sum(r['event_evidence']['consumes_all_known_prior_block_utxos'] for r in rows),
                partial_reference_spends=[dict(source_id=r['source_id'], **r['event_evidence']) for r in rows
                    if not r['event_evidence']['consumes_all_known_prior_block_utxos']],
                reference_inputs_outside_known_prior_utxos=sum(r['event_evidence']['reference_inputs_outside_known_prior_block_utxos'] for r in rows),
                prior_received_outputs_at_most_1000_sat=len(small),
                prior_received_value_at_most_1000_sat=sum(o['value_sat'] for o in small),
                duplicate_full_feature_vector_groups=sum(n>1 for n in vectors.values()),
                rows_in_duplicate_full_feature_vector_groups=sum(n for n in vectors.values() if n>1),
                constant_nonmissing_features=[k for k, v in columns.items() if None not in v and len(set(v))==1],
                identical_feature_column_pairs=[[a,b] for i,a in enumerate(FEATURE_NAMES)
                    for b in FEATURE_NAMES[i+1:] if columns[a]==columns[b]],
                feature_profiles={k:distribution(v) for k,v in columns.items()},
                quantile_method='Empirical inverse CDF: sorted observed value at rank max(1, ceil(p*n)); p50 is a lower median for even n. Missing values excluded.',
                collection_performed=False, training_performed=False)


def build(protocol_path):
    protocol = json.loads(protocol_path.read_bytes())
    root = protocol_path.parent.parent
    loaded = {}
    for name, pin in protocol['inputs'].items():
        raw = (root/pin['file']).read_bytes()
        if digest(raw) != pin['sha256']:
            raise ValueError('Pinned input changed: '+name)
        if name != 'feature_extractor':
            loaded[name] = json.loads(raw)
    cp = loaded['checkpoint']
    _, records = cohort.plan(root/protocol['inputs']['cohort_protocol']['file'])
    cohort.validate(cp, root/protocol['inputs']['cohort_protocol']['file'], records)
    if len(records) != protocol['expected_source_count']:
        raise ValueError('Unexpected source count')
    for name in ('corroboration', 'owner_reports'):
        if loaded[name]['checkpoint_sha256'] != protocol['inputs']['checkpoint']['sha256']:
            raise ValueError('Evidence uses a different checkpoint: '+name)
    registry = loaded['registry_protocol']
    raw = (root/registry['history_file']).read_bytes()
    if digest(raw) != registry['history_sha256']:
        raise ValueError('Pinned reference history changed')
    payments = index_rows(json.loads(gzip.decompress(raw))['transactions'], 'txid')
    rows = join(records, cp, loaded['corroboration']['rows'], loaded['owner_reports']['rows'], payments,
                protocol['incident_group'])
    view = dict(schema_version=1, protocol_sha256=digest(protocol_path.read_bytes()),
                built_on=protocol['built_on'], inputs=protocol['inputs'],
                reference_history_sha256=registry['history_sha256'],
                predictor_allowlist=list(FEATURE_NAMES),
                non_predictor_fields='All fields outside features, including identifiers, cutoff metadata, outcome/event evidence, labels, reports and provenance.',
                rows=rows)
    summary = summarize(rows, cp)
    summary['protocol_sha256'] = view['protocol_sha256']
    raw = json_bytes(view)
    compressed = gzip.compress(raw, mtime=0)
    summary['view_uncompressed_sha256'] = digest(raw)
    summary['view_gzip_sha256'] = digest(compressed)
    return {'view.json.gz':compressed, 'summary.json':json_bytes(summary)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('build','verify'))
    parser.add_argument('protocol', type=Path)
    args = parser.parse_args()
    outputs = build(args.protocol)
    if args.command == 'build' and any((args.protocol.parent/name).exists() for name in outputs):
        raise FileExistsError('Output already exists; use verify or a new dated output')
    for filename, raw in outputs.items():
        path = args.protocol.parent/filename
        if args.command == 'build':
            with path.open('xb') as handle:
                handle.write(raw)
        elif path.read_bytes() != raw:
            raise ValueError('Consolidated output mismatch: '+filename)
    summary = json.loads(outputs['summary.json'])
    print(json.dumps({k:v for k,v in summary.items() if k!='feature_profiles'}, indent=2))


if __name__ == '__main__':
    main()
