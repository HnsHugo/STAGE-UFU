"""Fixed family permutation diagnostic on previously inspected validation only."""
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
from sklearn.metrics import average_precision_score
from train_source_categories import HASHES, prepare, split
from analyze_validation_errors import SETTINGS

FAMILIES = {
    'monetary': ['balance','total_received_BTC','total_sent_BTC','max_sent_amount',
        'min_sent_amount','max_received_amount','min_received_amount','received_Variance_BTC','sent_Variance_BTC'],
    'activity_counts': ['transaction_number','payment_transactions','receipt_transactions',
        'total_output_slots','total_input_slots','sent_counters','received_counters'],
    'time_activity': ['lifetime','activity_w','activity_d','activity_time'],
    'fees': ['transaction_fee','transaction_fee_Variance']}
REPEATS, SEED = 5, 42


def validate_families(columns):
    flat = [c for family in FAMILIES.values() for c in family]
    if len(flat) != len(set(flat)) or set(flat) != set(columns):
        raise ValueError('Families must partition every feature exactly once')


def permute_family(matrix, columns, permutation):
    permutation = np.asarray(permutation)
    if permutation.shape != (len(matrix),) or not np.array_equal(np.sort(permutation), np.arange(len(matrix))):
        raise ValueError('A full row permutation is required')
    result = matrix.copy()
    result[:, columns] = matrix[permutation][:, columns]
    return result


def run(source, diagnostic, output):
    if output.exists(): raise FileExistsError(output)
    for name, expected in HASHES.items():
        with (source/name).open('rb') as handle:
            if hashlib.file_digest(handle, 'sha256').hexdigest() != expected:
                raise ValueError('Source checksum mismatch')
    raw = diagnostic.read_bytes(); reference = json.loads(raw)
    columns = reference['features']; validate_families(columns)
    data = prepare(pd.read_csv(source/'BB.tsv', sep='\t'), pd.read_csv(source/'CB.tsv', sep='\t'))
    train, val, test = split(data)
    if set(train) & set(val) or set(train) & set(test) or set(val) & set(test):
        raise ValueError('Split overlap')
    memberships = {name: hashlib.sha256('\n'.join(sorted(data.iloc[idx].address)).encode()).hexdigest()
                   for name,idx in [('train',train),('validation',val)]}
    if memberships != reference['membership_sha256']: raise ValueError('Split mismatch')
    def numeric(indices):
        return data.iloc[indices][columns].apply(pd.to_numeric, errors='coerce').replace([np.inf,-np.inf],np.nan)
    xt, xv = numeric(train), numeric(val)
    if xt.isna().all().any(): raise ValueError('Empty training feature')
    imputer = SimpleImputer(strategy='median')
    model = RandomForestClassifier(**SETTINGS)
    model.fit(imputer.fit_transform(xt), data.iloc[train].label.ne('benign').astype(int))
    xv = imputer.transform(xv)
    yv = data.iloc[val].label.ne('benign').astype(int).to_numpy()
    baseline = float(average_precision_score(yv, model.predict_proba(xv)[:,1]))
    if not np.isclose(baseline, reference['validation_metrics']['average_precision'], rtol=0, atol=1e-12):
        raise ValueError('Historical validation AP not reproduced')
    rng = np.random.default_rng(SEED)
    permutations = [rng.permutation(len(val)) for _ in range(REPEATS)]
    result = {}
    for name, family in {**FAMILIES, 'all_features_control': columns}.items():
        selected = [columns.index(c) for c in family]
        aps = [float(average_precision_score(yv, model.predict_proba(permute_family(xv,selected,p))[:,1]))
               for p in permutations]
        drops = [baseline-score for score in aps]
        result[name] = {'features':family,'permuted_ap':aps,'ap_drop':drops,
            'mean_ap_drop':float(np.mean(drops)),'std_ap_drop_ddof0':float(np.std(drops)),
            'mean_permuted_ap':float(np.mean(aps))}
        print(name,json.dumps(result[name]),flush=True)
    report = {'schema_version':1,'experiment':'grouped_validation_permutation_20261018',
        'reference_sha256':hashlib.sha256(raw).hexdigest(),'source_sha256':HASHES,
        'membership_sha256':memberships,'model_settings':SETTINGS,'features':columns,
        'versions':{'python':platform.python_version(),'numpy':np.__version__,
                    'pandas':pd.__version__,'sklearn':sklearn.__version__},
        'baseline_validation_ap':baseline,'validation_positive_prevalence':float(yv.mean()),
        'repeats':REPEATS,'seed':SEED,'train_rows':len(train),'validation_rows':len(val),
        'permutation_membership_sha256':[hashlib.sha256(p.astype('<i8').tobytes()).hexdigest() for p in permutations],
        'permutation_protocol':'Same 5 row permutations for all families; columns within each family move jointly after train-fitted imputation.',
        'reserved_test_scored':False,'families':result,
        'limitations':['Previously inspected model-selection validation; development diagnostic, not independent evaluation.',
            'Standard deviation describes permutation randomness, not a confidence interval for population performance.',
            'Within-family dependencies are preserved; cross-family algebraic and behavioral dependencies may be broken.',
            'Importance reflects model reliance under this perturbation, not causal relevance or a unique contribution.',
            'Row permutations do not account for unknown entity/incident clusters.',
            'Full-history profiles are retrospective; source labels are not independently verified theft roles.',
            'No threshold, model or hyperparameter selection; external 19-feature model remains unchanged.']}
    with output.open('x') as handle:
        json.dump(report,handle,indent=2,allow_nan=False);handle.write('\n')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for key in ['source','diagnostic','output']:parser.add_argument(key,type=Path)
    args=parser.parse_args();run(args.source,args.diagnostic,args.output)
