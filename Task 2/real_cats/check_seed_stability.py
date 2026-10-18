"""Three predeclared forest seeds on fixed development validation, no selection."""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import numpy as np
import pandas as pd
import sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from train_source_categories import HASHES, prepare, split, metrics
from analyze_validation_errors import SETTINGS
from ablate_monetary_features import retained_features, summarize_categories, THRESHOLD

SEEDS = (42, 43, 44)


def descriptive(values):
    values = np.asarray(values, dtype=float)
    if len(values) != len(SEEDS) or not np.isfinite(values).all():
        raise ValueError('Exactly three finite seed results required')
    return {'mean': float(values.mean()), 'std_ddof0': float(values.std()),
            'min': float(values.min()), 'max': float(values.max())}


def verify_cache(reference, ablation, versions, digest):
    normalized = json.loads(json.dumps(SETTINGS))
    if (reference['settings'] != normalized or ablation['model_settings'] != normalized
            or reference['versions'] != versions or ablation['versions'] != versions
            or ablation['reference_sha256'] != digest
            or reference['membership_sha256'] != ablation['membership_sha256']
            or reference['source_sha256'] != HASHES or ablation['source_sha256'] != HASHES
            or reference['threshold_strictly_greater_than'] != THRESHOLD
            or ablation['threshold_strictly_greater_than'] != THRESHOLD
            or ablation['retained_features'] != retained_features(reference['features'])):
        raise ValueError('Seed-42 cached provenance/configuration/runtime mismatch')


def summarize_pairs(rows):
    if tuple(row['seed'] for row in rows) != SEEDS:
        raise ValueError('Unexpected or missing seed')
    keys = ['average_precision','precision','recall','f1','true_positive','false_positive']
    return {key: {'full': descriptive([r['models']['full']['metrics'][key] for r in rows]),
                  'without_monetary': descriptive([r['models']['without_monetary']['metrics'][key] for r in rows]),
                  'paired_delta_without_minus_full': descriptive([
                      r['models']['without_monetary']['metrics'][key]-r['models']['full']['metrics'][key] for r in rows])}
            for key in keys}


def run(source, diagnostic_path, ablation_path, output):
    if output.exists(): raise FileExistsError(output)
    for name, expected in HASHES.items():
        with (source/name).open('rb') as handle:
            if hashlib.file_digest(handle,'sha256').hexdigest()!=expected:
                raise ValueError('Source checksum mismatch')
    reference_raw, ablation_raw = diagnostic_path.read_bytes(), ablation_path.read_bytes()
    reference, ablation = json.loads(reference_raw), json.loads(ablation_raw)
    versions = {'python':platform.python_version(),'sklearn':sklearn.__version__,
                'numpy':np.__version__,'pandas':pd.__version__}
    verify_cache(reference, ablation, versions, hashlib.sha256(reference_raw).hexdigest())
    data = prepare(pd.read_csv(source/'BB.tsv',sep='\t'),pd.read_csv(source/'CB.tsv',sep='\t'))
    train,val,test = split(data)
    if set(train)&set(val) or set(train)&set(test) or set(val)&set(test):
        raise ValueError('Split overlap')
    memberships = {name:hashlib.sha256('\n'.join(sorted(data.iloc[idx].address)).encode()).hexdigest()
                   for name,idx in [('train',train),('validation',val)]}
    if memberships != reference['membership_sha256']:raise ValueError('Split mismatch')
    variants = {'full':reference['features'],'without_monetary':retained_features(reference['features'])}
    yt = data.iloc[train].label.ne('benign').astype(int).to_numpy()
    labels = data.iloc[val].label.to_numpy(); yv = (labels!='benign').astype(int)
    prepared = {}
    for name,columns in variants.items():
        def numeric(indices):
            return data.iloc[indices][columns].apply(pd.to_numeric,errors='coerce').replace([np.inf,-np.inf],np.nan)
        xt,xv=numeric(train),numeric(val)
        if xt.isna().all().any():raise ValueError('Entirely missing training column')
        imputer=SimpleImputer(strategy='median')
        prepared[name]=(imputer.fit_transform(xt),imputer.transform(xv))
    rows=[{'seed':42,'origin':'reused_verified_cached_metrics','models':{
        'full':{'metrics':reference['validation_metrics'],'per_source_category':{
            r['source_category']:{'count':r['count'],'alerts':r['alerts']}
            for r in reference['diagnostic']['strata'] if r['missingness']=='all'}},
        'without_monetary':{'metrics':ablation['validation_metrics'],
                            'per_source_category':ablation['per_source_category']}}}]
    for seed in SEEDS[1:]:
        row={'seed':seed,'origin':'new_fit_training_only','models':{}}
        for name,(xt,xv) in prepared.items():
            forest=RandomForestClassifier(**{**SETTINGS,'random_state':seed})
            forest.fit(xt,yt)
            scores=forest.predict_proba(xv)[:,1];pred=(scores>THRESHOLD).astype(int)
            row['models'][name]={'metrics':metrics(yv,pred,scores),
                                 'per_source_category':summarize_categories(labels,pred)}
            print(seed,name,json.dumps(row['models'][name]['metrics']),flush=True)
        rows.append(row)
    report={'schema_version':1,'experiment':'fixed_split_seed_stability_20261018',
        'seeds':list(SEEDS),'settings_except_seed':{k:v for k,v in SETTINGS.items() if k!='random_state'},
        'threshold_strictly_greater_than':THRESHOLD,'features':variants,'versions':versions,
        'source_sha256':HASHES,'membership_sha256':memberships,
        'cache_sha256':{str(diagnostic_path):hashlib.sha256(reference_raw).hexdigest(),
                        str(ablation_path):hashlib.sha256(ablation_raw).hexdigest()},
        'train_rows':len(train),'validation_rows':len(val),'reserved_test_scored':False,
        'rows':rows,'summary':summarize_pairs(rows),
        'limitations':['Three predeclared seeds vary forest randomness only; the data split stays fixed.',
            'No winning seed or model is selected; this is a development diagnostic on inspected validation.',
            'Standard deviations/ranges are descriptive algorithmic variability, not confidence intervals or significance tests.',
            'max_features=sqrt changes effective candidate count with feature count; ablation is not causal attribution.',
            'Source role labels, unknown entity/incident groups and retrospective profiles retain their limitations.',
            'No reserved-test scoring or modification of the frozen external 19-feature model.']}
    with output.open('x') as handle:
        json.dump(report,handle,indent=2,allow_nan=False);handle.write('\n')
    print('SUMMARY',json.dumps(report['summary'],indent=2),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for key in ['source','diagnostic','ablation','output']:parser.add_argument(key,type=Path)
    args=parser.parse_args();run(args.source,args.diagnostic,args.ablation,args.output)
