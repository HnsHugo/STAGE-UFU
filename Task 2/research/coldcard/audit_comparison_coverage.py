"""Audit and consolidate the separate supplemental full-history coverage pass."""
from pathlib import Path
import json,gzip,statistics,copy,argparse
from collections import Counter
from datetime import datetime,timezone
import collect_comparison_coverage as x,collect_comparison_histories as c
from build_source_registry import digest,json_bytes


def audit(q,o,w):
    p=q.parent
    proto=json.loads(q.read_bytes())
    for key,pin in proto['inputs'].items():assert digest((p/pin['file']).read_bytes())==pin['sha256'],key
    summary=x.export(q,o,w);baseline_raw=(p/proto['inputs']['baseline_view']['file']).read_bytes();baseline=json.loads(gzip.decompress(baseline_raw));view=copy.deepcopy(baseline)
    records=json.loads((w/'plan.json').read_bytes());byid={r['pilot_id']:r for r in records};checkpoint=json.loads(gzip.decompress((o/'checkpoint.json.gz').read_bytes()));entries=checkpoint['entries'];independent=0;raw_checked=0
    for key,e in entries.items():
     r=byid[key];raw=(w/e['raw_file']).read_bytes();assert digest(raw)==e['raw_sha256'];h=json.loads(gzip.decompress(raw));marker=dict(started_at=e['request_started_at'],finished_at=e['request_finished_at']);regen=c.from_raw(r,raw,marker);assert regen==e;raw_checked+=1
     if e['status']!='complete':continue
     txs=[t for t in h['transactions'] if t['status']['confirmed'] and t['status']['block_height']<r['cutoff_height']];a=r['address'];recv={};spent={};receipt=0;spending=0;rates=[];heights=set()
     for t in txs:
      outputs=[(i,v) for i,v in enumerate(t['vout']) if v.get('scriptpubkey_address')==a];inputs=[v for v in t['vin'] if v.get('prevout',{}).get('scriptpubkey_address')==a];receipt+=bool(outputs);spending+=bool(inputs);heights.add(t['status']['block_height'])
      for i,v in outputs:
       k=(t['txid'],i);assert k not in recv;recv[k]=v['value']
      for v in inputs:
       k=(v['txid'],v['vout']);assert k not in spent;spent[k]=v['prevout']['value']
      if inputs:rates.append(t['fee']/((t['weight']+3)//4))
     assert set(spent)<=set(recv) and all(recv[k]==v for k,v in spent.items())
     cut=r['cutoff_height'];features=dict(confirmed_tx_count=len(txs),receipt_tx_count=receipt,spending_tx_count=spending,received_output_count=len(recv),spent_output_count=len(spent),received_sat=sum(recv.values()),spent_sat=sum(spent.values()),balance_sat=sum(recv.values())-sum(spent.values()),unspent_output_count=len(set(recv)-set(spent)),active_block_count=len(heights),activity_span_blocks=max(heights)-min(heights) if heights else None,blocks_since_first_activity=cut-min(heights) if heights else None,blocks_since_last_activity=cut-max(heights) if heights else None,median_spending_tx_fee_rate_sat_vb=statistics.median(rates) if rates else None);assert features==e['features'];independent+=1
    for row in view['rows']:
     e=entries.get(row['source_id'])
     if e and e['status']=='complete':
      assert row['history_status']=='incomplete';row.update(history_status='complete',features=e['features']);row['history_provenance']['prior_chosen_pass']=row['history_provenance']['chosen_pass'];row['history_provenance']['chosen_pass']=proto['pass_name'];row['history_provenance']['supplemental_full_history_coverage']=dict(status=e['status'],raw_sha256=e['raw_sha256'],pass_name=proto['pass_name'])
    for before,after in zip(baseline['rows'],view['rows']):
     if before['history_status']=='complete':assert before==after
     assert before['labels']==after['labels'] and before['cutoff_height']==after['cutoff_height']
    assert len(view['rows'])==1500 and len({r['address_sha256'] for r in view['rows']})==1500
    view['inputs'].update(coverage_protocol_sha256=digest(q.read_bytes()),coverage_checkpoint_sha256=digest((o/'checkpoint.json.gz').read_bytes()),coverage_baseline_view_sha256=digest(baseline_raw));out_raw=gzip.compress(json_bytes(view),mtime=0);(o/'address_dataset.json.gz').write_bytes(out_raw)
    comparisons=[r for r in view['rows'] if r['known_coldcard_core_membership']==0];status=dict(Counter(r['history_status'] for r in comparisons));counters=summary['current_full_transaction_counts'];estimated_pages=sum((n+24)//25+1 for n in counters.values());saved_pages=len(list((w/'requests').glob('*/page_*.json.gz')))
    result=dict(schema_version=1,verified_at=datetime.now(timezone.utc).isoformat(),protocol_sha256=digest(q.read_bytes()),address_dataset_sha256=digest(out_raw),selected=1500,complete_cases=500,comparison_statuses=status,combined_complete=500+status['complete'],new_complete=independent,raw_histories_reextracted=raw_checked,independent_new_vectors_checked=independent,previous_complete_rows_byte_preserved=True,previous_incomplete_results_preserved=True,labels_and_cutoff_unchanged=True,feature_count=14,full_counter_completeness_requirement_unchanged=True,full_transaction_count_min=min(counters.values()) if counters else None,full_transaction_count_max=max(counters.values()) if counters else None,minimum_total_page_requests=estimated_pages,minimum_total_network_seconds_at_one_request_per_second=estimated_pages,saved_pages=saved_pages,failed_requests=summary['failed_requests'],training_performed=False,split_created=False)
    verified_responses=0
    interrupted=[]
    recovered=0
    for file in sorted((w/'requests').glob('*/*.json')):
        meta=json.loads(file.read_bytes())
        body=file.with_suffix('.json.gz')
        if 'sha256' in meta:
            assert body.exists() and digest(body.read_bytes())==meta['sha256']
            json.loads(gzip.decompress(body.read_bytes()))
            verified_responses+=1
            recovered+=bool(meta.get('offline_orphan_recovered_at'))
        elif 'error_type' not in meta:
            interrupted.append(meta)
    result.update(saved_response_fingerprints_verified=verified_responses,
                  orphan_responses_recovered_without_http=recovered,
                  interrupted_consumed_requests=interrupted,
                  automatic_retry_performed=False)
    (o/'coverage_audit.json').write_bytes(json_bytes(result));(o/'combined_summary.json').write_bytes(json_bytes(result))
    return result


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('protocol',type=Path)
    parser.add_argument('output',type=Path)
    parser.add_argument('work',type=Path)
    args=parser.parse_args()
    print(json.dumps(audit(args.protocol,args.output,args.work)))
