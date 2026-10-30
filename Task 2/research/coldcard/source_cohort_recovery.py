"""Explicit one-pass recovery of a pinned cohort's unavailable histories."""
import argparse
import copy
import json
from pathlib import Path

import source_cohort as cohort


def load(protocol_path):
    protocol = json.loads(protocol_path.read_bytes())
    recovery = protocol['recovery']
    original_path = protocol_path.parent / recovery['original_protocol_file']
    checkpoint_path = protocol_path.parent / recovery['original_checkpoint_file']
    for path, expected in ((original_path, recovery['original_protocol_sha256']),
                           (checkpoint_path, recovery['original_checkpoint_sha256'])):
        if cohort.digest(path.read_bytes()) != expected:
            raise ValueError('Pinned recovery input checksum mismatch')
    original = json.loads(original_path.read_bytes())
    allowed = {'max_pages_per_address', 'timeout_seconds', 'recovery'}
    if ({k: v for k, v in protocol.items() if k not in allowed}
            != {k: v for k, v in original.items() if k not in allowed}):
        raise ValueError('Recovery changed a frozen protocol field')
    if protocol['max_pages_per_address'] != 16 or protocol['timeout_seconds'] != 15:
        raise ValueError('Recovery requires the prespecified 16-page / 15-second bounds')
    _, records = cohort.plan(original_path)
    _, new_records = cohort.plan(protocol_path)
    if records != new_records:
        raise ValueError('Recovery changed the source plan')
    base = json.loads(checkpoint_path.read_bytes())
    cohort.validate(base, original_path, records)
    if len(base['entries']) != len(records):
        raise ValueError('Recovery requires an exhausted original population')
    selected = [r['pilot_id'] for r in records
                if base['entries'][r['pilot_id']]['status'] != 'complete']
    if selected != recovery['source_ids']:
        raise ValueError('Recovery source selection mismatch')
    return protocol, records, base, selected


def validate_preservation(state, base, selected):
    ordered = list(selected)
    selected = set(selected)
    for key, entry in base['entries'].items():
        if key not in selected and state['entries'].get(key) != entry:
            raise ValueError('An original complete history was changed or removed')
    assigned = [key for batch in state['batches'] for key in batch['source_ids']]
    if (len(assigned) != len(set(assigned)) or not set(assigned) <= selected
            or assigned != ordered[:len(assigned)]):
        raise ValueError('Recovery attempted a complete or duplicate source')


def prepare(protocol_path, work):
    _, records, base, selected = load(protocol_path)
    path = work / 'state.json'
    if path.exists():
        state = json.loads(path.read_bytes())
    else:
        state = cohort.empty_state(protocol_path, records)
        state['entries'] = {key: copy.deepcopy(entry) for key, entry in base['entries'].items()
                            if entry['status'] == 'complete'}
    cohort.validate(state, protocol_path, records, work)
    validate_preservation(state, base, selected)
    cohort.atomic_write(path, cohort.json_bytes(state))
    return state


def audit(protocol_path, output):
    protocol, records, base, selected = load(protocol_path)
    folders = sorted(output.glob('batch_[0-9][0-9][0-9][0-9]'))
    if not folders:
        raise ValueError('No recovery snapshots')
    prior = {key: entry for key, entry in base['entries'].items() if entry['status'] == 'complete'}
    for folder in folders:
        cohort.verify(protocol_path, folder)
        state = json.loads((folder / 'checkpoint.json').read_bytes())
        validate_preservation(state, base, selected)
        if any(state['entries'].get(key) != entry for key, entry in prior.items()):
            raise ValueError('Recovery changed a preceding result')
        prior = state['entries']
    transitions = []
    for key in selected:
        before, after = base['entries'][key], state['entries'].get(key)
        transitions.append(dict(source_id=key,original_status=before['status'],
                                original_reason=before.get('reason'),
                                recovery_status=after['status'] if after else 'pending',
                                recovery_reason=after.get('reason') if after else None))
    return dict(schema_version=1,original_checkpoint_sha256=protocol['recovery']['original_checkpoint_sha256'],
                recovery_protocol_sha256=cohort.digest(protocol_path.read_bytes()),
                original_coverage=cohort.counts(base,len(records)),
                coverage=cohort.counts(state,len(records)),
                preserved_complete_entries=sum(e['status']=='complete' for e in base['entries'].values()),
                fixed_recovery_sources=selected,transitions=transitions,
                completed_batch_ids=[b['batch_id'] for b in state['batches'] if b['status']=='completed'],
                original_results_overwritten=False,training_performed=False,
                verified_compromise_labels=0,verified_hardware_labels=0,
                limitations=['Separate supplemental collection with larger pagination/time bounds; not comparable missingness under the original four-page protocol',
                             'One incident, unknown address-specific compromise/device labels and no documented negative controls',
                             'Unchanged prior-block features; provider-counter reconciliation is not cryptographic inclusion verification'])


def run(protocol_path, work, output):
    prepare(protocol_path, work)
    summary = cohort.run_many(protocol_path,work,output,max_batches=2,max_seconds=2400)
    if summary['new_source_attempts'] or not (work/'run_summary.json').exists():
        cohort.atomic_write(work/'run_summary.json',cohort.json_bytes(summary))
    result = audit(protocol_path,output)
    if result['coverage']['pending_sources']:
        return result
    path = output/'recovery_audit.json'
    raw = cohort.json_bytes(result)
    if path.exists() and path.read_bytes() != raw:
        raise ValueError('Existing recovery audit differs')
    cohort.atomic_write(path,raw)
    return result


def label_eligibility(protocol_path, output):
    """Describe eligibility from the saved evidence, without creating labels."""
    result = audit(protocol_path, output)
    review_path = protocol_path.parent/'source_label_review_20261029.json'
    review = json.loads(review_path.read_bytes())
    if review['address_specific_assertions']:
        raise ValueError('New address-specific assertions require a separate adjudication protocol')
    latest = sorted(output.glob('batch_[0-9][0-9][0-9][0-9]'))[-1]
    state = json.loads((latest/'checkpoint.json').read_bytes())
    rows = [dict(source_id=key,split_group='coldcard_2026',cutoff_height=entry['cutoff_height'],
                 history_status=entry['status'],features_available=entry['status']=='complete',
                 observed_relation='source_input_to_case_collector',
                 case_relation='graph_candidate',compromise_label=None,
                 hardware_seed_origin_label=None,hardware_signing_at_event_label=None,
                 supervised_training_eligible=False)
            for key,entry in sorted(state['entries'].items())]
    return dict(schema_version=1,reviewed_on=review['reviewed_on'],
                checkpoint_sha256=cohort.digest((latest/'checkpoint.json').read_bytes()),
                evidence_review_file=review_path.name,evidence_review_sha256=cohort.digest(review_path.read_bytes()),
                rows=rows,feature_complete_sources=result['coverage']['complete_sources'],
                verified_compromise_labels=0,verified_hardware_seed_origin_labels=0,
                verified_hardware_signing_labels=0,documented_negative_controls=0,
                independently_evaluable_incident_groups=1,supervised_eligible_sources=0,
                training_ready=False,training_performed=False,
                blockers=['No independent address-specific compromise labels in the reviewed evidence',
                          'No individual seed-origin or event-signing device evidence',
                          'No documented target-matched negative-control cohort',
                          'One incident group cannot provide independent incident-level evaluation'],
                required_evidence_fields=review['minimum_evidence_record'],
                review_scope=review['scope'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=('run','verify','eligibility'))
    parser.add_argument('protocol',type=Path)
    parser.add_argument('output',type=Path)
    parser.add_argument('--work',type=Path)
    args = parser.parse_args()
    if args.command == 'run':
        if args.work is None:
            parser.error('run requires --work')
        result = run(args.protocol,args.work,args.output)
    elif args.command == 'verify':
        result = audit(args.protocol,args.output)
        if (args.output/'recovery_audit.json').read_bytes() != cohort.json_bytes(result):
            raise ValueError('Recovery audit reproduction mismatch')
    else:
        result = label_eligibility(args.protocol,args.output)
        path = args.output/'label_eligibility.json'
        raw = cohort.json_bytes(result)
        if path.exists() and path.read_bytes()!=raw:
            raise ValueError('Existing label-eligibility artifact differs')
        cohort.atomic_write(path,raw)
        print(json.dumps({k:v for k,v in result.items() if k!='rows'},indent=2))
        return
    print(json.dumps(result['coverage'],indent=2))


if __name__ == '__main__':
    main()
