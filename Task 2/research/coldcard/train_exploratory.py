"""Exploratory candidate-relation classification, NOT confirmed theft detection.
Usage: python train_exploratory.py transactions.csv.gz output_directory
Fixed settings; no test-set tuning. Outputs aggregate metrics and readable trees.
"""
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
import pandas as pd
import sklearn
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support, average_precision_score
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, export_text

FEATURES = ['input_count','output_count','distinct_input_addresses','distinct_output_addresses',
            'input_address_missing_count','output_address_missing_count','input_total_sat',
            'output_total_sat','fee_sat','vsize_vb','fee_rate_sat_vb','version','lock_time',
            'min_output_sat','max_output_sat','zero_value_outputs']
EXPECTED_SHA = '158788226288dce22bfd5ea20deab1b72551c5d0c32bdb547e113c83273841b4'


def metrics(y, pred, score=None):
    p,r,f,_=precision_recall_fscore_support(y,pred,average='binary',zero_division=0)
    tn,fp,fn,tp=confusion_matrix(y,pred,labels=[0,1]).ravel()
    return {'precision_proxy':float(p),'recall_proxy':float(r),'f1_proxy':float(f),
            'true_negative_proxy':int(tn),'false_positive_proxy':int(fp),
            'false_negative_proxy':int(fn),'true_positive_proxy':int(tp),
            'average_precision_proxy':None if score is None else float(average_precision_score(y,score)),
            'background_alert_rate':float(fp/(tn+fp)) if tn+fp else None}


def partitions(df):
    y=df.relation.eq('direct_parent_candidate').astype(int).to_numpy()
    idx=np.arange(len(df))
    train,test=train_test_split(idx,test_size=.25,stratify=y,random_state=42)
    # A diagnostic reference only: related candidate transactions may leak across this split.
    yield 'random_reference_related_leakage_possible',train,test
    # Chronological split fixed before fitting. Block is metadata only, not a feature.
    train=idx[df.block_height.to_numpy()<960377]
    test=idx[df.block_height.to_numpy()>=960377]
    yield 'chronological_block_960377',train,test


def run(source,destination):
    with open(source,'rb') as f: digest=hashlib.file_digest(f,'sha256').hexdigest()
    if digest != EXPECTED_SHA: raise ValueError('Input differs from inspected feature dataset.')
    df=pd.read_csv(source)
    if df.txid.duplicated().any() or len(df)!=493571: raise ValueError('Coverage/uniqueness mismatch.')
    df=df[(df.is_coinbase==0)&(df.relation!='source_attributed')].reset_index(drop=True)
    if not np.isfinite(df[FEATURES].to_numpy(dtype=float)).all(): raise ValueError('Missing/nonfinite feature values.')
    out=Path(destination);out.mkdir(exist_ok=False)
    y=df.relation.eq('direct_parent_candidate').astype(int).to_numpy()
    report={'target':'direct parent relation versus unattributed background',
            'warning':'Proxy labels; not theft/hardware ground truth. No collector independence is established.',
            'dataset_sha256':digest,'versions':{'python':sys.version.split()[0],'sklearn':sklearn.__version__,'pandas':pd.__version__,'numpy':np.__version__},
            'settings':{'max_depth':4,'min_samples_leaf':20,'class_weight':'balanced','random_state':42},
            'excluded':['txid','block_height','relation','is_coinbase'],
            'eligible_rows':len(df),'candidate_rows':int(y.sum()),'splits':{}}
    for name,train,test in partitions(df):
        assert not set(train).intersection(test)
        split={'train_count':len(train),'test_count':len(test),'train_candidates':int(y[train].sum()),'test_candidates':int(y[test].sum()),
               'train_height_min':int(df.iloc[train].block_height.min()),'train_height_max':int(df.iloc[train].block_height.max()),
               'test_height_min':int(df.iloc[test].block_height.min()),'test_height_max':int(df.iloc[test].block_height.max()),'models':{}}
        yt=y[test]
        split['models']['always_background']=metrics(yt,np.zeros(len(test),dtype=int))
        rule=((df.iloc[test].output_count==1)&(df.iloc[test].fee_rate_sat_vb>=4.95)).astype(int).to_numpy()
        split['models']['previously_observed_rule']=metrics(yt,rule)
        for variant,columns in [('tree_all',FEATURES),('tree_without_fees',[f for f in FEATURES if f not in ['fee_sat','fee_rate_sat_vb']])]:
            model=DecisionTreeClassifier(max_depth=4,min_samples_leaf=20,class_weight='balanced',random_state=42)
            model.fit(df.iloc[train][columns],y[train])
            pred=model.predict(df.iloc[test][columns]);score=model.predict_proba(df.iloc[test][columns])[:,1]
            split['models'][variant]=metrics(yt,pred,score)
            split['models'][variant]['feature_importances']={c:float(v) for c,v in zip(columns,model.feature_importances_) if v}
            (out/(name+'_'+variant+'.txt')).write_text(export_text(model,feature_names=columns,max_depth=4,decimals=5))
        report['splits'][name]=split
    (out/'metrics.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))

if __name__=='__main__':
    if len(sys.argv)!=3: sys.exit('Usage: python train_exploratory.py transactions.csv.gz output_directory')
    run(*sys.argv[1:])
