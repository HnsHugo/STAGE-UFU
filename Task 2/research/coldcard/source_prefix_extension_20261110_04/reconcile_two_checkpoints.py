"""Count the fifteen original sources once across the 64- and 96-page layers."""
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path

OUT=Path(__file__).resolve().parent
BASE=OUT.parent
FIRST=BASE/'source_prefix_extension_20261110_03'
BEFORE=BASE/'source_prefix_extension_20261110_02'


def read(p):
    b=p.read_bytes()
    return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)


def main():
    assert not (OUT/'two_checkpoint_reconciliation.json').exists()
    assert read(OUT/'independent_verification.json')['status']=='passed'
    first=read(FIRST/'checkpoint.json.gz')['entries'];second=read(OUT/'checkpoint.json.gz')['entries']
    first_complete={sid for sid,e in first.items() if e['status']=='complete_prior_prefix'}
    first_bounded=set(first)-first_complete
    assert set(read(OUT/'protocol.json')['source_ids'])==first_bounded
    assert set(second)<=first_bounded and set(second).isdisjoint(first_complete)
    latest=dict(first,**second)
    assert len(latest)==15
    complete=sorted(sid for sid,e in latest.items() if e['status']=='complete_prior_prefix')
    incomplete=sorted(set(latest)-set(complete))
    before=read(BEFORE/'precutoff_feature_view.json.gz');after=read(OUT/'precutoff_feature_view.json.gz')
    old={r['source_id']:r for r in before['rows']}
    for r in after['rows']:
        sid=r['source_id']
        if old[sid]['features'] is not None or sid not in latest:assert r==old[sid]
        elif sid in complete:assert r['features']==latest[sid]['features']
        else:assert r['features'] is None
    available=sum(r['features'] is not None for r in after['rows'])
    assert available==1387+len(complete)
    fresh=[]
    for scope in [FIRST,OUT]:fresh.extend(m for m in read(scope/'request_manifest.json.gz') if not m.get('offline_reused'))
    one=read(FIRST/'continuation_reconciliation.json');two=read(OUT/'continuation_reconciliation.json')
    report=dict(schema_version=1,status='both_checkpoints_verified',original_sources=15,
        completed_source_ids=complete,new_complete_prefixes=len(complete),
        first_checkpoint_new_complete=len(first_complete),second_checkpoint_new_complete=len(complete)-len(first_complete),
        retained_incomplete_source_ids=incomplete,current_checkpoint_pages=96,
        current_work_outcomes=len(second),pending_current_work_ids=sorted(first_bounded-set(second)),
        coldcard_vectors=available,coldcard_unavailable=1500-available,cryptobilis_vectors_unchanged=329,
        total_vectors=available+329,total_remaining_information_gaps=1500-available+37,
        fresh_request_intents=len(fresh),fresh_successful_bodies=sum(m.get('http_status')==200 for m in fresh),
        additional_source_transaction_observations=one['additional_source_transaction_observations']+two['additional_source_transaction_observations'],
        observation_count_is_not_global_unique_transactions=True,original_1387_vectors_preserved=True,
        full_current_histories_unchanged=True,verified_compromise_device_labels_remain_unknown=True,
        model_fits=0,new_scores=0,old_tail_pages_requested_again=False,
        final_view_sha256=hashlib.sha256((OUT/'precutoff_feature_view.json.gz').read_bytes()).hexdigest())
    (OUT/'two_checkpoint_reconciliation.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps(report,sort_keys=True))


if __name__=='__main__':main()
