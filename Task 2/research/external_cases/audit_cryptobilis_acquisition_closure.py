"""Read-only whole-cohort closure audit from pinned public and private evidence.

No provider HTTP, fitting, scoring, overwrite of historical exports, or promotion
of prefix coverage to full-current-history coverage is performed.
"""
import argparse
from collections import Counter
import json
from pathlib import Path

import audit_cryptobilis_sources as prior
from audit_cryptobilis_sources import ROOT, ready, fixed, tail, independent
from select_cryptobilis_sources import replay


def validate_view(view, selected):
    rows=view['rows'];original=selected['rows']
    ready.require(view['schema_version']==2, 'Not a schema-v2 prefix view')
    by_id={row['source_id']:row for row in rows}
    originals={row['source_id']:row for row in original}
    ready.require(len(by_id)==len(rows) and len(originals)==len(original)
                  and set(by_id)==set(originals), 'Cohort source IDs changed or repeated')
    ready.require(len({r['address_sha256'] for r in rows})==len(rows), 'Repeated source address')
    for key,row in by_id.items():
        for field,value in originals[key].items():
            if field not in {'features','prior_prefix_status'}:
                ready.require(row[field]==value, 'Frozen selection field changed: '+field)
        ready.require(all(v is None for v in row['labels'].values()), 'Unknown source labels changed')
        ready.require(row['full_history_status']=='not_collected_for_this_source', 'Full-history status promoted')
        status=row['precutoff_history_status']
        ready.require(status in {'complete_prior_prefix','bounded_incomplete'}, 'Network or unattempted source remains')
        ready.require(row['prior_prefix_status']==status, 'Prefix status fields disagree')
        if status=='complete_prior_prefix':
            ready.require(isinstance(row['features'],dict) and set(row['features'])==set(fixed.FEATURE_NAMES),
                          'Complete prefix lacks the fourteen-variable vector')
        else:
            ready.require(row['features'] is None, 'Bounded-incomplete prefix supplies a vector')
    return by_id


def pinned_inputs(config):
    paths={}
    for name,pin in config['inputs'].items():
        path=(ROOT/pin['file']).resolve()
        ready.require(path.is_relative_to(ROOT), 'Input outside research root')
        ready.require(ready.sha(path.read_bytes())==pin['sha256'], 'Input fingerprint mismatch: '+name)
        paths[name]=path
    return paths


def check_cached_assembly(record, data, work):
    folder=work/'requests'/record['pilot_id']
    ready.require(ready.read(folder/'reference.json.gz')==data['anchor'], 'Raw reference differs from saved response')
    ready.require(ready.read(folder/'reference_after.json.gz')==data['anchor_after'], 'Raw after-status differs from response')
    offset=0;last_empty=False
    for index in range(data['pages_fetched']):
        page=ready.read(folder/('tail_%04d.json.gz'%index))
        ready.require(isinstance(page,list) and len(page)<=25, 'Invalid saved cursor page')
        ready.require(page==data['transactions'][offset:offset+len(page)], 'Raw tail differs from saved cursor pages')
        offset+=len(page);last_empty=not page
        ready.require(not last_empty or index==data['pages_fetched']-1, 'Page fetched after empty terminal page')
        del page
    ready.require(offset==len(data['transactions']) and last_empty==data['pagination_exhausted'],
                  'Raw tail exhaustion/length differs from saved pages')
    for txid,status in data['parent_statuses'].items():
        ready.require(ready.read(folder/('parent_'+ready.hashed(txid)+'.json.gz'))==status,
                      'Raw parent status differs from saved response')


def build(configuration):
    config=ready.read(configuration);paths=pinned_inputs(config)
    ready.require(paths['auditor']==Path(__file__).resolve(), 'Wrong closure auditor')
    view=ready.read(paths['view']);selected=ready.read(paths['source_selection'])
    by_id=validate_view(view,selected)
    ready.require(len(by_id)==366, 'Frozen CryptoBilis sample size changed')
    transfer=ready.read(paths['transfer_protocol'])
    ready.require(view['predictor_allowlist']==transfer['predictor_allowlist']==list(fixed.FEATURE_NAMES),
                  'Fourteen definitions changed')
    chosen=replay(ready.read(paths['input_census']),transfer['comparison_selection'])
    comparisons=[r for r in selected['rows'] if r['cryptobilis_reference_source_membership']==0]
    ready.require(chosen==[r['address_sha256'] for r in comparisons], 'Fixed comparison replay differs')
    coldcard=ready.read(paths['coldcard_view'])
    ready.require(len(coldcard['rows'])==1500 and sum(r['features'] is not None for r in coldcard['rows'])==1378,
                  'Frozen Coldcard coverage changed')
    checked=set();checks=[];passes=[];responses=offline=complete=snapshots=0
    for specification in config['passes']:
        proto=ready.read(paths[specification['protocol']])
        cp=ready.read(paths[specification['checkpoint']])
        work=(ROOT/specification['work_directory']).resolve()
        ready.require(work.is_relative_to(ROOT), 'Private work directory outside research root')
        records=ready.read(work/'plan.json');records_by_id={r['pilot_id']:r for r in records}
        ready.require(ready.sha(ready.encoded(records))==proto['private_plan_sha256'], 'Private plan fingerprint differs')
        ready.require([r['pilot_id'] for r in records]==proto['source_ids'], 'Execution order changed')
        ready.require(cp['protocol_sha256']==ready.sha(paths[specification['protocol']].read_bytes()), 'Checkpoint protocol differs')
        entries=cp['entries'];ready.require(set(entries)==set(proto['source_ids']), 'Pass has unfinished source results')
        ready.require(not checked.intersection(entries), 'A finished source was collected in two passes')
        for key,entry in entries.items():
            ready.require(key in by_id and entry['source_id']==key, 'Unselected or mislabeled source')
            row=by_id[key];record=records_by_id[key]
            ready.require(ready.hashed(record['address'])==row['address_sha256'], 'Decoded address differs')
            ready.require(ready.hashed(record['payment_txid'])==row['reference_txid_sha256'], 'Reference differs')
            for field in ('address_sha256','cutoff_height','cutoff_block_hash'):
                ready.require(entry[field]==record[field]==row[field], 'Source/cutoff join differs')
            ready.require(entry['payment_txid_sha256']==row['reference_txid_sha256'], 'Reference hash differs')
            ready.require(row['precutoff_history_provenance']['pass_name']==proto['pass_name'], 'Provenance pass differs')
            ready.require(entry['status']==row['precutoff_history_status'] and entry['features']==row['features'],
                          'Latest vector/status differs from chosen checkpoint')
            raw=(work/entry['raw_file']).resolve();ready.require(raw.is_relative_to(work), 'Raw path outside pass')
            ready.require(ready.sha(raw.read_bytes())==entry['raw_sha256'], 'Raw response fingerprint differs')
            data=ready.read(raw);ready.require(data['address']==record['address'], 'Raw address differs')
            regenerated=tail.tail_check(record,data['anchor'],data['transactions'],data['pagination_exhausted'],
                                        data['anchor_after'],data['parent_statuses'])
            ready.require(all(regenerated[k]==entry[k] for k in ('status','features','prefix')), 'Raw re-extraction differs')
            ready.require(data['pages_fetched']==entry['pages_fetched']<=16, 'Page limit differs')
            check_cached_assembly(record,data,work)
            if entry['status']=='complete_prior_prefix':
                ready.require(independent.independent_features(record,data)==entry['features'], 'Independent vector recount differs')
                complete+=1
            checks.append(dict(source_id=key,pass_name=proto['pass_name'],status=entry['status'],pages=entry['pages_fetched']))
            del data,regenerated
        requests=ready.read(paths[specification['requests']])
        ready.require(not any('error_type' in m or m.get('http_status')!=200 for m in requests), 'Consumed failed request remains in chosen pass')
        n,reused=prior.check_requests(work,records,requests);responses+=n;offline+=reused
        for snapshot_key in specification['milestones']:
            snap=ready.read(paths[snapshot_key])['entries'];count=len(snap)
            ready.require(set(snap)==set(proto['source_ids'][:count]) and all(v==entries[k] for k,v in snap.items()),
                          'Immutable batch snapshot differs from final pass')
            snapshots+=1
        checked.update(entries);passes.append(dict(pass_name=proto['pass_name'],sources=len(entries),
            complete_vectors=sum(e['features'] is not None for e in entries.values()),
            bounded_incomplete=sum(e['features'] is None for e in entries.values()),
            response_fingerprints_verified=n,offline_reference_responses=reused))
    ready.require(checked==set(by_id), 'Whole-cohort raw evidence is incomplete')
    classes={}
    for target,name in [(1,'case'),(0,'comparison')]:
        rows=[r for r in by_id.values() if r['cryptobilis_reference_source_membership']==target]
        classes[name]=dict(selected=len(rows),complete_vectors=sum(r['features'] is not None for r in rows),
                          bounded_incomplete=sum(r['features'] is None for r in rows))
    ready.require(classes['case']['selected']==122 and classes['comparison']['selected']==244, 'Class sample sizes changed')
    return dict(schema_version=1,configuration_sha256=ready.sha(configuration.read_bytes()),
        scope='Closed fixed CryptoBilis prior-prefix acquisition; no full-history, victim/device or model evaluation claim.',
        selected_sources=len(by_id),raw_tails_reextracted=len(checked),independent_vectors_recounted=complete,
        complete_vectors=complete,bounded_incomplete=len(by_id)-complete,network_sources_remaining=0,
        response_fingerprints_verified=responses,offline_reference_responses=offline,
        successful_prefix_network_responses=responses-offline,immutable_batch_snapshots_verified=snapshots,
        fixed_comparison_replay_exact=True,full_current_source_histories_reconciled=0,
        all_raw_cached_page_assemblies_exact=True,
        full_history_status_not_promoted=True,unknown_labels_unchanged=True,feature_count=14,
        coldcard_selected_rows_preserved=1500,coldcard_vectors_preserved=1378,
        frozen_model_sha256=ready.sha(paths['frozen_model'].read_bytes()),
        model_fits=0,scores_computed=0,external_overlap_and_scoring_gate='Pending a separate unit',
        classes=classes,passes=passes,per_source=checks)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['build','verify'])
    p.add_argument('configuration',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    result=ready.encoded(build(a.configuration.resolve()))
    if a.mode=='build':
        ready.require(not a.output.exists(), 'Refusing to overwrite an audit output');a.output.write_bytes(result)
    else:
        ready.require(a.output.read_bytes()==result, 'Saved whole-cohort audit differs')
    d=json.loads(result);print(json.dumps({k:v for k,v in d.items() if k not in {'per_source','passes'}}))
