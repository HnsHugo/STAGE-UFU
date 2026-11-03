"""Re-extract bounded source prefixes and append an immutable external view.

This is acquisition verification, not an external scoring or training command.
"""
import argparse
from collections import Counter
from copy import deepcopy
import gzip
import json
from pathlib import Path

import collect_cryptobilis_sources as collect
from collect_cryptobilis_sources import ROOT, ready, tail, atomic_write
import audit_reference_tail as independent
import prepayment_pilot as fixed


def compose(baseline, entries, pass_name):
    ready.require(baseline['schema_version'] == 2, 'Expected schema-v2 external view')
    by_id={r['source_id']:r for r in baseline['rows']}
    ready.require(len(by_id)==len(baseline['rows']), 'Repeated baseline source')
    ready.require(set(entries)<=set(by_id), 'Unselected source in checkpoint')
    view=deepcopy(baseline)
    for row in view['rows']:
        key=row['source_id'];old=by_id[key];entry=entries.get(key)
        if entry is None:
            continue
        ready.require(old['features'] is None and old['precutoff_history_status']=='not_completed',
                      'Finished source selected again')
        for field in ('address_sha256','cutoff_height','cutoff_block_hash'):
            ready.require(entry[field]==old[field], 'Frozen source identity/cutoff changed')
        ready.require(entry['payment_txid_sha256']==old['reference_txid_sha256'],'Reference changed')
        if entry['status']=='complete_prior_prefix':
            ready.require(set(entry['features'])==set(fixed.FEATURE_NAMES),'Fourteen-feature definition changed')
            ready.require(fixed.features(entry['prefix'],entry['cutoff_height'])==entry['features'],
                          'Prefix feature recount differs')
            row['features']=deepcopy(entry['features'])
        else:
            ready.require(entry['status']=='bounded_incomplete' and entry['features'] is None
                          and entry['prefix'] is None,'Incomplete prefix supplies a vector')
        row['precutoff_history_status']=entry['status']
        row['prior_prefix_status']=entry['status']
        row['precutoff_history_provenance']=dict(pass_name=pass_name,raw_sha256=entry['raw_sha256'],
            full_current_history_counter_coverage_verified=False)
        ready.require(row['labels']==old['labels'] and row['full_history_status']==old['full_history_status']
                      and row['cryptobilis_reference_source_membership']==old['cryptobilis_reference_source_membership'],
                      'Labels, target or full-history status changed')
    view['latest_pass_name']=pass_name
    return view


def check_requests(work, records, manifest):
    responses=offline=0
    for meta in manifest:
        folder=work/'requests'/meta['source_id'];key=meta['key']
        if 'sha256' not in meta:
            continue
        body=folder/(key+'.json.gz')
        ready.require(ready.sha(body.read_bytes())==meta['sha256'],'Saved response fingerprint mismatch')
        ready.require(meta.get('http_status')==200,'Refused response reused as successful')
        responses+=1;offline+=bool(meta.get('offline_reuse'))
    for record in records:
        cursor=record['payment_txid'];folder=work/'requests'/record['pilot_id']
        endpoints={'reference':'/tx/'+record['payment_txid'],
                   'reference_after':'/tx/'+record['payment_txid']+'/status',
                   'availability_counter':'/address/'+record['address']}
        for index in range(16):
            key='tail_%04d'%index;marker=folder/(key+'.json')
            if not marker.exists():
                break
            endpoints[key]='/address/'+record['address']+'/txs/chain/'+cursor
            meta=ready.read(marker)
            if 'sha256' not in meta:
                break
            page=ready.read(folder/(key+'.json.gz'))
            if not page:
                break
            cursor=page[-1]['txid']
        anchor=folder/'reference.json.gz'
        if anchor.exists():
            for vin in tail.anchor_check(record,ready.read(anchor)):
                endpoints['parent_'+ready.hashed(vin['txid'])]='/tx/'+vin['txid']+'/status'
        for key,endpoint in endpoints.items():
            marker=folder/(key+'.json')
            if marker.exists():
                ready.require(ready.read(marker)['endpoint_sha256']==ready.hashed(endpoint),
                              'Cached response cursor/endpoint mismatch')
    return responses,offline


def audit(protocol_path, output, work):
    proto=ready.read(protocol_path);collect.validate_inputs(proto)
    records=ready.read(work/'plan.json')
    ready.require(ready.sha(ready.encoded(records))==proto['private_plan_sha256'],'Private plan fingerprint changed')
    ready.require([r['pilot_id'] for r in records]==proto['source_ids'],'Source order changed')
    baseline=ready.read(ROOT/proto['inputs']['baseline_view']['file'])
    cp=ready.read(output/'checkpoint.json.gz')
    ready.require(cp['protocol_sha256']==ready.sha(protocol_path.read_bytes()),'Checkpoint protocol mismatch')
    by_id={r['pilot_id']:r for r in records};entries=cp['entries'];checks=[]
    ready.require(set(entries)<=set(by_id),'Checkpoint includes unselected source')
    complete=0
    for key,entry in entries.items():
        record=by_id[key];raw=work/entry['raw_file']
        ready.require(ready.sha(raw.read_bytes())==entry['raw_sha256'],'Raw tail fingerprint mismatch')
        data=ready.read(raw)
        ready.require(data['address']==record['address'],'Raw source mismatch')
        regen=tail.tail_check(record,data['anchor'],data['transactions'],data['pagination_exhausted'],
                              data['anchor_after'],data['parent_statuses'])
        ready.require(all(regen[f]==entry[f] for f in ('status','features','prefix')),'Raw re-extraction differs')
        ready.require(data['pages_fetched']==entry['pages_fetched']<=16,'Page bound changed')
        if entry['status']=='complete_prior_prefix':
            ready.require(independent.independent_features(record,data)==entry['features'],'Independent fourteen-feature recount differs')
            complete+=1
        checks.append(dict(source_id=key,status=entry['status'],pages=entry['pages_fetched'],
                           pagination_exhausted=data['pagination_exhausted']))
    requests=ready.read(output/'request_manifest.json.gz')
    responses,offline=check_requests(work,records,requests)
    view=compose(baseline,entries,proto['pass_name'])
    view_raw=gzip.compress(ready.encoded(view),mtime=0)
    atomic_write(output/'precutoff_feature_view.json.gz',view_raw)
    rows=view['rows'];final={r['source_id'] for r in rows if r['precutoff_history_status']!='not_completed'}
    classes={}
    for value,name in [(1,'case'),(0,'comparison')]:
        chosen=[r for r in rows if r['cryptobilis_reference_source_membership']==value]
        classes[name]=dict(selected=len(chosen),complete_prefix=sum(r['features'] is not None for r in chosen),
                           statuses=dict(Counter(r['precutoff_history_status'] for r in chosen)))
    summary=dict(schema_version=1,pass_name=proto['pass_name'],targeted_sources=len(records),
        finalized_sources=len(entries),new_complete_vectors=complete,
        new_bounded_incomplete=len(entries)-complete,raw_tails_reextracted=len(checks),
        independent_new_vectors_recounted=complete,saved_response_fingerprints_verified=responses,
        offline_reused_reference_responses=offline,request_markers=len(requests),
        successful_network_responses=responses-offline,failed_requests=[m for m in requests if 'error_type' in m],
        total_selected=len(rows),total_complete_vectors=sum(r['features'] is not None for r in rows),
        total_bounded_incomplete=sum(r['precutoff_history_status']=='bounded_incomplete' for r in rows),
        network_or_unattempted_sources=len(rows)-len(final),classes=classes,
        prior_vectors_preserved=sum(r['features'] is not None for r in baseline['rows']),
        labels_cutoffs_and_frozen_model_unchanged=True,full_history_status_not_promoted=True,
        coldcard_vectors_preserved=1378,model_fits=0,scores_computed=0,feature_count=14,
        complete_cross_development_overlap_audit='pending acquisition completion',can_score_primary_transfer=False,
        feature_view_sha256=ready.sha(view_raw),per_source=checks)
    atomic_write(output/'coverage_audit.json',ready.encoded(summary))
    def pin(path):return dict(file=str(path.relative_to(ROOT)),sha256=ready.sha(path.read_bytes()))
    pins={k:pin(output/name) for k,name in [('checkpoint','checkpoint.json.gz'),('request_manifest','request_manifest.json.gz'),
          ('feature_view','precutoff_feature_view.json.gz'),('audit','coverage_audit.json'),('stop','run_stop.json')]}
    pins['protocol']=pin(protocol_path)
    pins.update({'protocol_input_'+key:deepcopy(value) for key,value in proto['inputs'].items()})
    order=ready.read(ROOT/proto['inputs']['selection_plan_manifest']['file'])['execution_source_ids']
    network=[key for key in order if key not in final]
    resume=dict(schema_version=2,scope='cryptobilis_reference_source_membership_prior_prefixes',
        latest_pass_name=proto['pass_name'],updated_at=collect.now().isoformat(),inputs=pins,
        selected_sources=len(rows),complete_prefix_source_ids=sorted(r['source_id'] for r in rows if r['features'] is not None),
        bounded_incomplete_source_ids=sorted(r['source_id'] for r in rows if r['precutoff_history_status']=='bounded_incomplete'),
        network_source_ids=network,network_sources=len(network),failed_consumed_requests=summary['failed_requests'],
        next_network_attempt_not_before=ready.read(collect.POLICY)['next_network_attempt_not_before'],
        next_action='After global guards, prepare a distinct pinned successor over at most the first 100 network_source_ids. Never repeat complete/bounded-incomplete results or consumed failed markers within their pass.',
        bounds=dict(batch_size=20,max_batches=5,workers=2,global_requests_per_second=1,max_pages=16,timeout_seconds=15),
        full_history_scope='Individual current full histories were not collected/reconciled; exhausted prior prefixes do not promote this status.',
        labels_unchanged=True,model_fits=0,scores_computed=0)
    atomic_write(output/'resume_checkpoint.json',ready.encoded(resume))
    return summary


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('protocol',type=Path);p.add_argument('output',type=Path);p.add_argument('work',type=Path)
    a=p.parse_args();print(json.dumps(audit(a.protocol.resolve(),a.output,a.work)))
