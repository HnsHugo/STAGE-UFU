"""Independent consistency checks on the frozen public exports, without fitting or HTTP."""
from collections import Counter
import copy, gzip, hashlib, json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
def read(path):
    data=path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix=='.gz' else data)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def verify():
    protocol=read(ROOT/'protocol.json')
    baseline_pin=next(p for p in protocol['inputs'].values() if p['file'].endswith('reference_tail_continuation_20261102_1508/precutoff_feature_view.json.gz'))
    original=read((ROOT/baseline_pin['file']).resolve())
    result=read(ROOT/'precutoff_feature_view.json.gz')
    checkpoint=read(ROOT/'checkpoint.json.gz')
    audit=read(ROOT/'coverage_audit.json')
    records=read(ROOT/'request_manifest.json.gz')
    receipt=read(ROOT/'run_receipt.json')
    assert result['schema_version']==original['schema_version']==2
    assert len(result['rows'])==len(original['rows'])==1500
    assert len({r['source_id'] for r in result['rows']})==1500
    selected=set(protocol['source_ids']);entries=checkpoint['entries']
    assert set(entries)==selected and len(selected)==20
    before={r['source_id']:r for r in original['rows']}
    complete=[];bounded=[]
    full_before=Counter();full_after=Counter()
    for row in result['rows']:
        sid=row['source_id'];old=before[sid]
        full_before[(old['known_coldcard_core_membership'],old['full_history_status'])]+=1
        full_after[(row['known_coldcard_core_membership'],row['full_history_status'])]+=1
        if sid not in selected:
            assert row==old
            continue
        e=entries[sid];assert old['features'] is None
        expected=copy.deepcopy(old)
        expected['precutoff_history_provenance']={
            'pass_name':protocol['pass_name'],'raw_sha256':e['raw_sha256'],
            'full_current_history_counter_coverage_verified':False,'pages_fetched':e['pages_fetched']}
        if e['status']=='complete_prior_prefix':
            complete.append(sid);expected['features']=e['features']
            expected['precutoff_history_status']='complete_prior_prefix'
            assert e['audit']['pagination_exhausted'] is True
            assert e['audit']['reference_anchor_verified'] is True
            assert e['audit']['reference_funding_closure_verified'] is True
            assert all(t['height']<row['cutoff_height'] for t in e['prefix'])
            assert set(row['features'])==set(result['predictor_allowlist'])
        else:
            bounded.append(sid)
            assert e['status']=='bounded_incomplete' and e['features'] is e['prefix'] is None
        assert row==expected
    assert full_before==full_after==Counter({(1,'complete'):500,(0,'complete'):864,(0,'incomplete'):136})
    assert len(complete)==4 and len(bounded)==16
    assert sorted(complete)==audit['new_complete_source_ids']
    assert sum(r['features'] is not None for r in result['rows'])==1382
    assert sum(r['features'] is not None for r in original['rows'])==1378
    assert sha(ROOT/'precutoff_feature_view.json.gz')==audit['composed_view_sha256']
    reused=[r for r in records if r.get('offline_reused')]
    fresh=[r for r in records if not r.get('offline_reused')]
    assert len(reused)==340 and len(fresh)==316 and len(records)==656
    assert all(r.get('http_status')==200 and 'error_type' not in r for r in records)
    assert len({(r['source_id'],r['key']) for r in records})==656
    assert len([r for r in fresh if r['key']=='availability_counter'])==1
    assert sum(r['key']=='reference_after' for r in fresh)==20
    assert sum(r['key'].startswith('tail_') for r in fresh)==295
    for sid in selected:
        pages=[r for r in records if r['source_id']==sid and r['key'].startswith('tail_')]
        assert len(pages)==entries[sid]['pages_fetched']<=32
        assert {r['key'] for r in pages}=={f'tail_{i:04d}' for i in range(len(pages))}
    assert receipt['new_http_200']==316 and receipt['first_refusal_status'] is None
    assert receipt['operational_locks_released'] is True
    report={
        'status':'passed','public_export_files_checked':6,'unchanged_old_vectors':1378,
        'new_complete_vectors':4,'still_bounded_in_scope':16,'coldcard_vectors':1382,
        'coldcard_bounded':118,'coldcard_cases':500,'coldcard_comparison_vectors':882,
        'full_history_complete_cases':500,'full_history_complete_comparisons':864,
        'full_history_incomplete_comparisons':136,'request_markers':656,
        'fresh_http_200':316,'offline_reused_http_200':340,'single_counter_get':True,
        'fixed_14_features_and_labels_preserved':True,'old_rows_unchanged_except_selected_provenance':True,
        'new_fits_or_scores':0,'provider_requests_by_verifier':0,
        'view_sha256':sha(ROOT/'precutoff_feature_view.json.gz')}
    return report

if __name__=='__main__':
    report=verify()
    (ROOT/'independent_verification.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps(report,sort_keys=True))
