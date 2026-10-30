"""Audit coverage and unchanged source evidence after comparison collection."""
import argparse
from collections import Counter,defaultdict
import gzip
import json
from pathlib import Path

from build_source_registry import digest,json_bytes
import collect_comparison_histories as collect


def audit(protocol_path,output,work=None):
    protocol,public=collect.load(protocol_path)
    coverage=collect.verify(protocol_path,output,work)
    state=json.loads(gzip.decompress((output/'checkpoint.json.gz').read_bytes()))
    by_id={r['pilot_id']:r for r in public}
    raw_checked=0;raw_status=Counter();modes=Counter();missing_raw=0
    observed_full_counts=[]
    for key,entry in state['entries'].items():
        modes[entry.get('collection_mode','original_bounded_pagination')]+=1
        if not entry.get('raw_file'):continue
        path=work/entry['raw_file'] if work else None
        if path is None or not path.exists():missing_raw+=1;continue
        raw=path.read_bytes()
        if digest(raw)!=entry['raw_sha256']:raise ValueError('Raw audit fingerprint mismatch')
        data=json.loads(gzip.decompress(raw))
        r=by_id[key]
        # Reconstruct the private source only for the local re-extraction check.
        record=dict(r,address=data['address'])
        reference=[t for t in data['transactions'] if digest(t['txid'].encode())==r['payment_txid_sha256']]
        if entry['status']=='complete' and len(reference)!=1:raise ValueError('Complete history lacks the frozen reference')
        if reference:record['payment_txid']=reference[0]['txid']
        else:record['payment_txid']='unknown_reference_not_reached'
        marker=dict(started_at=entry['request_started_at'],finished_at=entry['request_finished_at'])
        regenerated=collect.from_raw(record,raw,marker)
        for field in ('status','features','prefix'):
            if regenerated[field]!=entry[field]:raise ValueError('Raw re-extraction differs: '+key+' '+field)
        raw_checked+=1;raw_status[entry['status']]+=1
        observed_full_counts.append(data['before']['chain_stats']['tx_count'])
    design_pin=json.loads((protocol_path.parent/protocol['inputs']['design']['file']).read_bytes())
    case_pin=design_pin['inputs']['source_view'];case_raw=(protocol_path.parent/case_pin['file']).read_bytes()
    if digest(case_raw)!=case_pin['sha256']:raise ValueError('Original case view changed')
    case=json.loads(gzip.decompress(case_raw))['rows']
    checkpoint_pin=design_pin['inputs']['checkpoint']
    case_checkpoint_raw=(protocol_path.parent/checkpoint_pin['file']).read_bytes()
    if digest(case_checkpoint_raw)!=checkpoint_pin['sha256']:raise ValueError('Original case checkpoint changed')
    case_entries=json.loads(case_checkpoint_raw)['entries']
    complete=[e for e in state['entries'].values() if e['status']=='complete']
    case_refs={t['transaction_id'] for e in case_entries.values() for t in e['prefix']}
    comparison_refs={t['transaction_id'] for e in complete for t in e['prefix']}
    shared_refs=case_refs & comparison_refs
    case_vectors={tuple(row['features'][k] for k in collect.fixed.FEATURE_NAMES) for row in case}
    cross_vector_rows=sum(tuple(e['features'][k] for k in collect.fixed.FEATURE_NAMES) in case_vectors for e in complete)
    strata=[]
    for block in coverage['by_reference_block']:
        case_n=sum(r['cutoff_height']==block['height'] for r in case)
        strata.append(dict(height=block['height'],case_selected=case_n,case_complete=case_n,
                           comparison=block,comparison_completion_fraction=block['complete']/block['selected']))
    return dict(schema_version=1,audited_on='2026-10-30',
        protocol_sha256=digest(protocol_path.read_bytes()),checkpoint_sha256=digest((output/'checkpoint.json.gz').read_bytes()),
        coverage=coverage,case_selected=500,case_complete=500,
        comparison_completion_fraction=coverage['complete_sources']/len(public),by_reference_block=strata,
        error_types=coverage['error_types'],collection_modes=dict(sorted(modes.items())),
        local_raw_histories_reextracted=raw_checked,raw_statuses=dict(sorted(raw_status.items())),
        published_raw_fingerprints_without_local_bytes=missing_raw,
        observed_full_history_tx_count_min=min(observed_full_counts) if observed_full_counts else None,
        observed_full_history_tx_count_max=max(observed_full_counts) if observed_full_counts else None,
        distinct_comparison_prior_transaction_references=len(comparison_refs),
        shared_prior_transaction_references_between_case_and_comparisons=len(shared_refs),
        comparison_sources_sharing_prior_transaction_with_case=sum(any(t['transaction_id'] in shared_refs for t in e['prefix']) for e in complete),
        comparison_rows_with_full_feature_vector_identical_to_a_case_row=cross_vector_rows,
        missing_historical_spending_fee_rates=sum(e['features']['median_spending_tx_fee_rate_sat_vb'] is None for e in complete),
        original_case_checkpoint_and_features_preserved=True,
        replacement_or_retry_performed=False,training_performed=False,split_created=False,
        limitations=['Fixed sample selected before history collection; complete-case population is censored by current full-history coverage bounds',
                    'Case coverage used the original collection plus supplemental recovery; comparison collection is a single bounded pass with a capacity precheck from batch 2',
                    'Unknown comparison compromise/device status is not a verified negative class',
                    'Shared transactions and identical features are overlap diagnostics, not ownership proof; preserve connected components before any exploratory split',
                    'One previously inspected incident does not supply independent-incident or prospective detection validation'])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('protocol',type=Path);parser.add_argument('output',type=Path)
    parser.add_argument('--work',type=Path);parser.add_argument('--verify',action='store_true')
    args=parser.parse_args();result=audit(args.protocol,args.output,args.work)
    path=args.output/'collection_audit.json';raw=json_bytes(result)
    if args.verify:
        if path.read_bytes()!=raw:raise ValueError('Collection audit reproduction mismatch')
    else:
        with path.open('xb') as stream:stream.write(raw)
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
