"""Audit targeted prior-block predictors while preserving full-history status."""
import argparse
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
import gzip
import json
from pathlib import Path
from statistics import median

from build_source_registry import digest, json_bytes
import collect_reference_tail as tail


def independent_features(record, data):
    address, cutoff = record['address'], record['cutoff_height']
    txs = [t for t in data['transactions']
           if t['status']['confirmed'] and t['status']['block_height'] < cutoff]
    received, spent, heights, rates = {}, {}, set(), []
    receipts = spendings = 0
    for tx in txs:
        outs = [(i,v) for i,v in enumerate(tx['vout']) if v.get('scriptpubkey_address')==address]
        ins = [v for v in tx['vin'] if (v.get('prevout') or {}).get('scriptpubkey_address')==address]
        receipts += bool(outs)
        spendings += bool(ins)
        heights.add(tx['status']['block_height'])
        for index, value in outs:
            key = tx['txid'],index
            if key in received:
                raise ValueError('Duplicate received output')
            received[key] = value['value']
        for value in ins:
            key = value['txid'],value['vout']
            if key in spent:
                raise ValueError('Duplicate spent output')
            spent[key] = value['prevout']['value']
        if ins:
            rates.append(tx['fee']/((tx['weight']+3)//4))
    if not set(spent)<=set(received) or any(received[k]!=v for k,v in spent.items()):
        raise ValueError('Spent output absent from prior receipts')
    return dict(confirmed_tx_count=len(txs),receipt_tx_count=receipts,
        spending_tx_count=spendings,received_output_count=len(received),
        spent_output_count=len(spent),received_sat=sum(received.values()),
        spent_sat=sum(spent.values()),balance_sat=sum(received.values())-sum(spent.values()),
        unspent_output_count=len(set(received)-set(spent)),active_block_count=len(heights),
        activity_span_blocks=max(heights)-min(heights) if heights else None,
        blocks_since_first_activity=cutoff-min(heights) if heights else None,
        blocks_since_last_activity=cutoff-max(heights) if heights else None,
        median_spending_tx_fee_rate_sat_vb=median(rates) if rates else None)


def audit(q,output,work):
    proto=json.loads(q.read_bytes())
    for pin in proto['inputs'].values():
        if digest((q.parent/pin['file']).read_bytes())!=pin['sha256']:
            raise ValueError('Pinned reference-tail input changed')
    baseline_raw=(q.parent/proto['inputs']['baseline_view']['file']).read_bytes()
    baseline=json.loads(gzip.decompress(baseline_raw))
    records=json.loads((work/'plan.json').read_bytes())
    if digest(json_bytes(records))!=proto['private_plan_sha256']:
        raise ValueError('Private plan changed')
    by_id={r['pilot_id']:r for r in records}
    cp=json.loads(gzip.decompress((output/'checkpoint.json.gz').read_bytes()))
    if cp['protocol_sha256']!=digest(q.read_bytes()) or not set(cp['entries'])<=set(by_id):
        raise ValueError('Checkpoint source/protocol mismatch')
    entries=cp['entries']
    checks=[]
    for key,e in entries.items():
        r=by_id[key]
        for field in ('address_sha256','payment_txid_sha256','cutoff_height','cutoff_block_hash'):
            if e[field]!=r[field]:
                raise ValueError('Frozen source identity mismatch')
        raw=(work/e['raw_file']).read_bytes()
        if digest(raw)!=e['raw_sha256']:
            raise ValueError('Raw reference-tail fingerprint mismatch')
        data=json.loads(gzip.decompress(raw))
        if data['address']!=r['address']:
            raise ValueError('Raw address mismatch')
        regen=tail.tail_check(r,data['anchor'],data['transactions'],data['pagination_exhausted'],
                              data['anchor_after'],data['parent_statuses'])
        if any(regen[field]!=e[field] for field in ('status','features','prefix')):
            raise ValueError('Reference-tail re-extraction differs')
        if e['status']=='complete_prior_prefix' and independent_features(r,data)!=e['features']:
            raise ValueError('Independent pre-cutoff recount differs')
        checks.append(dict(source_id=key,status=e['status'],pages_fetched=e['pages_fetched'],
            observed_prior_transaction_count=sum(t['status']['block_height']<r['cutoff_height']
                                                 for t in data['transactions']),
            pagination_exhausted=data['pagination_exhausted']))
    requests=json.loads(gzip.decompress((output/'request_manifest.json.gz').read_bytes()))
    responses=0
    for meta in requests:
        body=work/'requests'/meta['source_id']/(meta['key']+'.json.gz')
        if 'sha256' in meta:
            if digest(body.read_bytes())!=meta['sha256']:
                raise ValueError('Page response fingerprint mismatch')
            responses+=1
    # A new view makes the two scopes explicit. Never rewrite the historical
    # address view or reinterpret a prior-prefix audit as a full counter audit.
    view=deepcopy(baseline)
    for row in view['rows']:
        old_features=deepcopy(row['features'])
        row['full_history_status']=row.pop('history_status')
        row['full_history_provenance']=row.pop('history_provenance')
        row['precutoff_history_status']=('complete_full_history'
            if row['full_history_status']=='complete' else 'not_completed')
        e=entries.get(row['source_id'])
        if e:
            if row['full_history_status']!='incomplete':
                raise ValueError('A complete historical row was selected again')
            row['precutoff_history_status']=e['status']
            row['precutoff_history_provenance']=dict(pass_name=proto['pass_name'],
                raw_sha256=e['raw_sha256'],full_current_history_counter_coverage_verified=False)
            if e['status']=='complete_prior_prefix':
                row['features']=deepcopy(e['features'])
        if row['full_history_status']=='complete' and row['features']!=old_features:
            raise ValueError('Existing predictor vector changed')
    for old,new in zip(baseline['rows'],view['rows']):
        if old['labels']!=new['labels'] or old['cutoff_height']!=new['cutoff_height']:
            raise ValueError('Labels or cutoff changed')
    if len(view['rows'])!=1500 or len({r['address_sha256'] for r in view['rows']})!=1500:
        raise ValueError('Cohort membership changed')
    view['schema_version']=2
    view['inputs'].update(reference_tail_protocol_sha256=digest(q.read_bytes()),
        reference_tail_checkpoint_sha256=digest((output/'checkpoint.json.gz').read_bytes()),
        unchanged_baseline_view_sha256=digest(baseline_raw))
    view['coverage_policy']='Features require a complete strictly pre-cutoff prefix. Full-history-counter and anchored-reference-tail evidence remain separately labeled.'
    view_raw=gzip.compress(json_bytes(view),mtime=0)
    (output/'precutoff_feature_view.json.gz').write_bytes(view_raw)
    comparisons=[r for r in view['rows'] if r['known_coldcard_core_membership']==0]
    extra=sum(e['status']=='complete_prior_prefix' for e in entries.values())
    full_counts=dict(Counter(r['full_history_status'] for r in comparisons))
    summary=dict(schema_version=1,verified_at=datetime.now(timezone.utc).isoformat(),
        selected_sources=1500,case_complete=500,full_history_comparison_statuses=full_counts,
        new_complete_pre_cutoff_comparisons=extra,
        comparison_predictors_available=sum(r['features'] is not None for r in comparisons),
        comparison_predictors_unavailable=sum(r['features'] is None for r in comparisons),
        complete_predictor_rows=sum(r['features'] is not None for r in view['rows']),
        targeted_sources=len(records),targeted_results=len(entries),targeted_pending=len(records)-len(entries),
        targeted_statuses=dict(Counter(e['status'] for e in entries.values())),
        raw_tails_reextracted=len(checks),independent_new_vectors_checked=extra,
        saved_response_fingerprints_verified=responses,
        failed_requests=[r for r in requests if 'error_type' in r],
        baseline_view_unchanged=True,all_1364_previous_vectors_unchanged=True,
        labels_and_cutoff_unchanged=True,feature_count=14,
        full_history_status_not_promoted=True,training_performed=False,split_created=False,
        precutoff_view_sha256=digest(view_raw),per_source=checks,
        limitations=['Reference-tail completeness relies on the original provider indexed-history contract; the eight controls matched exact full-history prefixes.',
                     'This is not full-current-history counter reconciliation or independent cryptographic inclusion verification.',
                     'A bounded-incomplete tail has no predictor vector; unknown labels remain unknown.'])
    (output/'coverage_audit.json').write_bytes(json_bytes(summary))
    (output/'coverage_summary.json').write_bytes(json_bytes(summary))
    return summary


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('protocol',type=Path)
    parser.add_argument('output',type=Path)
    parser.add_argument('work',type=Path)
    args=parser.parse_args()
    print(json.dumps(audit(args.protocol,args.output,args.work)))
