"""Validate extracted features against manifest and candidate provenance.
Usage: python audit_dataset.py transactions.csv.gz manifest.json candidate_groups.json
Prints a JSON report; exits nonzero for inconsistent data.
"""
import hashlib,json,sys
import numpy as np
import pandas as pd
from train_grouped import validate_groups
from train_exploratory import FEATURES


def audit(df,manifest,groups):
    if manifest['status']!='complete':raise ValueError('Extraction is incomplete.')
    if len(df)!=manifest['transaction_count'] or df.txid.duplicated().any():raise ValueError('Row count or TXID uniqueness mismatch.')
    actual={str(k):int(v) for k,v in df.relation.value_counts().items()}
    if actual!=manifest['relation_counts']:raise ValueError('Relation counts mismatch.')
    validate_groups(df,groups,manifest)
    ordinary=df[df.is_coinbase==0]
    if not np.isfinite(ordinary[FEATURES].to_numpy(float)).all():raise ValueError('Missing/nonfinite ordinary transaction features.')
    if not ((ordinary.input_total_sat-ordinary.output_total_sat)==ordinary.fee_sat).all():raise ValueError('Input/output/fee inconsistency.')
    if not (ordinary.vsize_vb>0).all():raise ValueError('Invalid vsize.')
    if not np.allclose(ordinary.fee_rate_sat_vb,ordinary.fee_sat/ordinary.vsize_vb,rtol=1e-10,atol=1e-10):raise ValueError('Fee rate inconsistency.')
    if (ordinary[['fee_sat','input_total_sat','output_total_sat']]<0).any().any():raise ValueError('Negative fee or amount.')
    return {'status':'consistent','rows':len(df),'unique_txids':int(df.txid.nunique()),
            'coinbase_rows':int((df.is_coinbase==1).sum()),'block_heights':int(df.block_height.nunique()),
            'relation_counts':actual,'group_counts':groups['group_counts'],
            'warning':'Internal feature consistency does not independently authenticate chain data or source labels.'}

if __name__=='__main__':
    if len(sys.argv)!=4:sys.exit('Usage: python audit_dataset.py transactions.csv.gz manifest.json candidate_groups.json')
    report=audit(pd.read_csv(sys.argv[1]),json.load(open(sys.argv[2])),json.load(open(sys.argv[3])))
    with open(sys.argv[1],'rb') as f:report['features_sha256']=hashlib.file_digest(f,'sha256').hexdigest()
    print(json.dumps(report,indent=2))
