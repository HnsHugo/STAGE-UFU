"""Create a provenance-preserving address view from the two comparison passes."""
import argparse
from collections import Counter
from copy import deepcopy
import gzip
import json
from pathlib import Path

from build_source_registry import digest,json_bytes
from prepayment_pilot import FEATURE_NAMES
import collect_comparison_histories as collect


def merge(selection,original,recovered,allowed):
    ids=[r['source_id'] for r in selection]
    if len(ids)!=len(set(ids)) or not set(recovered)<=set(allowed) or not set(allowed)<=set(ids):
        raise ValueError('Unexpected duplicate or recovery source')
    rows=[]
    for selected in selection:
        key=selected['source_id'];old=original.get(key);new=recovered.get(key)
        if new is not None and old is not None and old['status']!='error':
            raise ValueError('Recovery attempted an original complete/incomplete result')
        chosen=new if new is not None else old
        if chosen is not None:
            if any(chosen[k]!=selected[k] for k in ('address_sha256','payment_txid_sha256','cutoff_height')):
                raise ValueError('Joined history/reference identity mismatch')
            if chosen['compromise_label'] is not None or chosen['hardware_label'] is not None:
                raise ValueError('Recovery promoted an unsupported label')
            if chosen['status']=='complete':
                if set(chosen['features'])!=set(FEATURE_NAMES):raise ValueError('Feature schema changed')
            elif chosen['features'] is not None:raise ValueError('Unavailable history has features')
        row={k:selected[k] for k in ('source_id','address_sha256','payment_txid_sha256','cutoff_height','cutoff_block_hash')}
        row.update(history_status=chosen['status'] if chosen else 'pending',
                   features=deepcopy(chosen['features']) if chosen else None,
                   known_coldcard_core_membership=0,
                   labels=dict(reported_loss=None,reported_hardware_association=None,
                               independently_verified_compromise=None,independently_verified_seed_origin=None,
                               hardware_signing_at_event=None),
                   history_provenance=dict(chosen_pass='network_recovery' if new is not None else 'initial' if old is not None else None,
                       initial_status=old['status'] if old else 'pending',
                       recovery_status=new['status'] if new is not None else 'pending' if key in allowed else 'excluded_original_result_retained',
                       initial_raw_sha256=old.get('raw_sha256') if old else None,
                       recovery_raw_sha256=new.get('raw_sha256') if new else None))
        rows.append(row)
    return rows


def build(protocol_path,output):
    protocol,public=collect.load(protocol_path);root=protocol_path.parent
    if 'network_recovery' not in protocol:raise ValueError('A distinct recovery protocol is required')
    collect.verify(protocol_path,output)
    state=json.loads(gzip.decompress((output/'checkpoint.json.gz').read_bytes()))
    initial_path=root/protocol['inputs']['baseline_checkpoint']['file']
    original=json.loads(gzip.decompress(initial_path.read_bytes()))
    initial_protocol=root/protocol['inputs']['baseline_protocol']['file']
    collect.verify(initial_protocol,initial_path.parent)
    selection=json.loads((root/protocol['inputs']['selection']['file']).read_bytes())['rows']
    allowed=set(protocol['network_recovery']['source_ids'])
    comparisons=merge(selection,original['entries'],state['entries'],allowed)
    design=json.loads((root/protocol['inputs']['design']['file']).read_bytes())
    case_pin=design['inputs']['source_view'];case_raw=(root/case_pin['file']).read_bytes()
    if digest(case_raw)!=case_pin['sha256']:raise ValueError('Original case view changed')
    cases=json.loads(gzip.decompress(case_raw))['rows']
    rows=[]
    for r in cases:
        row={k:r[k] for k in ('source_id','address_sha256','payment_txid_sha256','cutoff_height','cutoff_block_hash')}
        row.update(history_status='complete',features=deepcopy(r['features']),known_coldcard_core_membership=1,
                   labels=deepcopy(r['labels']),history_provenance=dict(chosen_pass='case_recovery',source_id=r['source_id']))
        rows.append(row)
    rows.extend(comparisons)
    if len(rows)!=1500 or len({r['address_sha256'] for r in rows})!=1500:
        raise ValueError('Combined address cohort coverage/overlap mismatch')
    inputs=dict(case_view_sha256=digest(case_raw),initial_checkpoint_sha256=digest(initial_path.read_bytes()),
                recovery_checkpoint_sha256=digest((output/'checkpoint.json.gz').read_bytes()),
                recovery_protocol_sha256=digest(protocol_path.read_bytes()))
    view=dict(schema_version=1,created_on='2026-10-30',inputs=inputs,
              target='known_coldcard_core_membership; retrospective exploratory membership, not independently verified theft or device identity',
              predictor_allowlist=list(FEATURE_NAMES),
              predictor_policy='Only features are predictors; all identities, cutoffs, labels and provenance remain outside predictors.',rows=rows)
    summary=dict(schema_version=1,inputs=inputs,selected_case_sources=len(cases),complete_case_sources=len(cases),
                 selected_comparison_sources=len(comparisons),comparison_statuses=dict(Counter(r['history_status'] for r in comparisons)),
                 combined_selected_sources=len(rows),combined_complete_sources=sum(r['history_status']=='complete' for r in rows),
                 recovery_pending_sources=len(public)-len(state['entries']),
                 original_complete_comparisons_preserved=sum(e['status']=='complete' for e in original['entries'].values()),
                 original_incomplete_comparisons_preserved=sum(e['status']=='incomplete' for e in original['entries'].values()),
                 source_reported_loss_labels=sum(r['labels']['reported_loss']==1 for r in rows),
                 independently_verified_compromise_labels=0,independently_verified_device_labels=0,
                 by_reference_block=[dict(height=h,case_selected=sum(r['cutoff_height']==h for r in rows if r['known_coldcard_core_membership']==1),
                     comparison_statuses=dict(Counter(r['history_status'] for r in comparisons if r['cutoff_height']==h)))
                     for h in sorted({r['cutoff_height'] for r in rows})],
                 original_files_overwritten=False,model_fitted=False,split_created=False,
                 limitations=['Only complete rows have fourteen predictors; unavailable features stay null',
                              'History completeness depends on full-history bounds; inspect completion by class/block before an exploratory fit',
                              'Comparison membership zero is not legitimate/theft-negative/hardware-negative ground truth',
                              'One previously inspected incident does not provide independent-incident or prospective validation'])
    raw=gzip.compress(json_bytes(view),mtime=0);summary['address_dataset_sha256']=digest(raw)
    return {'address_dataset.json.gz':raw,'combined_summary.json':json_bytes(summary)}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=('build','verify'))
    parser.add_argument('protocol',type=Path);parser.add_argument('output',type=Path)
    args=parser.parse_args();outputs=build(args.protocol,args.output)
    if args.command=='build' and any((args.output/name).exists() for name in outputs):
        raise FileExistsError('Combined view exists; use verify or a new output')
    for name,raw in outputs.items():
        path=args.output/name
        if args.command=='build':path.write_bytes(raw)
        elif path.read_bytes()!=raw:raise ValueError('Combined address view reproduction mismatch')
    print(outputs['combined_summary.json'].decode())


if __name__=='__main__':main()
