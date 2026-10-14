"""Deterministic training-only references for extraction edge-case checks."""
import argparse
import hashlib
import json
from pathlib import Path
import pandas as pd
from train_source_categories import HASHES, prepare, split


def select(source):
    for name, expected in HASHES.items():
        with (source/name).open('rb') as f:
            if hashlib.file_digest(f,'sha256').hexdigest()!=expected:raise ValueError('Source checksum mismatch')
    data=prepare(pd.read_csv(source/'BB.tsv',sep='\t'),pd.read_csv(source/'CB.tsv',sep='\t'))
    train,_,_=split(data);pool=data.iloc[train].copy()
    pool=pool[(pool.transaction_number>=2)&(pool.transaction_number<=10)]
    pool['selection_order']=pool.address.map(lambda a:hashlib.sha256(a.encode()).hexdigest())
    pool=pool.sort_values('selection_order')
    conditions={
        'nonconstant_allocated_fees':(pool.payment_transactions>=2)&(pool.transaction_fee_Variance>0),
        'no_spending_direction':pool.payment_transactions==0,
        'multiple_own_inputs':pool.total_input_slots>pool.payment_transactions,
        'same_transaction_receipt_and_spend':pool.payment_transactions+pool.receipt_transactions>pool.transaction_number,
    }
    records=[];unavailable=[];used=set()
    for case,mask in conditions.items():
        candidates=pool[mask & ~pool.address.isin(used)]
        if candidates.empty:unavailable.append(case);continue
        row=candidates.iloc[0];used.add(row.address)
        records.append(dict(address=row.address,source_id='real_cats_training_edge_reference',source_label=row.label,
                            case_group=None,label_available_at=None,training_label='source_category_only',
                            selection_case=case,source_transaction_count=int(row.transaction_number)))
    return dict(status='Training-only schema development references',source_sha256=HASHES,
                selection='SHA256(address) ascending within four predefined source-feature strata; not performance sampling',
                records=records,unavailable_strata=unavailable)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    if a.output.exists():raise ValueError('Output must be new')
    report=select(a.source);a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
