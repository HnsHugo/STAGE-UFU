"""Prespecified reverse source-membership transfer; all provider access is absent."""
import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import gzip
import hashlib
import importlib.metadata
import json
from pathlib import Path
import statistics


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == '.gz' else data)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    require(not path.exists(), 'Refusing to overwrite ' + path.name)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n')


def recount_features(prefix, height):
    require(len({t['transaction_id'] for t in prefix}) == len(prefix), 'Repeated prior transaction')
    require(all(t['height'] < height for t in prefix), 'Reference/future transaction in predictors')
    received = [v for t in prefix for v in t['received']]
    spent = [v for t in prefix for v in t['spent']]
    heights = [t['height'] for t in prefix]
    rates = [t['spending_tx_fee_sat'] / t['spending_tx_vsize_vb'] for t in prefix
             if t['spent'] and t['spending_tx_fee_sat'] is not None and t['spending_tx_vsize_vb']]
    return dict(confirmed_tx_count=len(prefix), receipt_tx_count=sum(bool(t['received']) for t in prefix),
        spending_tx_count=sum(bool(t['spent']) for t in prefix), received_output_count=len(received),
        spent_output_count=len(spent), received_sat=sum(v['value_sat'] for v in received),
        spent_sat=sum(v['value_sat'] for v in spent),
        balance_sat=sum(v['value_sat'] for v in received)-sum(v['value_sat'] for v in spent),
        unspent_output_count=len(received)-len(spent), active_block_count=len(set(heights)),
        activity_span_blocks=max(heights)-min(heights) if heights else None,
        blocks_since_first_activity=height-min(heights) if heights else None,
        blocks_since_last_activity=height-max(heights) if heights else None,
        median_spending_tx_fee_rate_sat_vb=statistics.median(rates) if rates else None)


def partition(tokens):
    parents = {key:key for key in tokens}
    def find(key):
        while parents[key] != key:
            parents[key] = parents[parents[key]];key = parents[key]
        return key
    owners = {}
    for key in sorted(tokens):
        for token in tokens[key]:
            other = owners.setdefault(token, key)
            a, b = find(key), find(other)
            if a != b:
                parents[max(a,b)] = min(a,b)
    groups = defaultdict(list)
    for key in sorted(tokens):
        groups[find(key)].append(key)
    return sorted(groups.values())


def load_evidence(settings, root):
    paths = {}
    for name, pin in settings['inputs'].items():
        path = (root/pin['file']).resolve()
        require(path.is_relative_to(root.resolve()) and sha(path) == pin['sha256'], 'Input fingerprint mismatch: '+name)
        paths[name] = path
    views = {n:read(paths[k]) for n,k in [('coldcard','coldcard_view'),('cryptobilis','external_view')]}
    names = views['coldcard']['predictor_allowlist']
    require(len(names) == 14 and names == views['cryptobilis']['predictor_allowlist'], 'Feature allowlist mismatch')
    checkpoints = {
        'coldcard': {n:read(paths[k])['entries'] for n,k in settings['development_checkpoints'].items()},
        'cryptobilis': {n:read(paths[x['checkpoint']])['entries'] for n,x in settings['external_checkpoints'].items()},
    }
    rows, tokens, observation_counts = {}, {}, Counter()
    for dataset, view in views.items():
        require(view['schema_version'] == 2, 'Unexpected view schema')
        for row in view['rows']:
            key = dataset+':'+row['source_id'];require(key not in rows, 'Repeated source ID')
            target = settings['target_fields'][dataset]
            require(row[target] in (0,1), 'Unexpected operational label')
            require(all(row['labels'][k] is None for k in settings['unknown_label_fields']), 'Verified label changed')
            reference = row['payment_txid_sha256'] if dataset == 'coldcard' else row['reference_txid_sha256']
            tt = [('address',row['address_sha256']),('reference',reference),('any_tx',reference)]
            if row['features'] is not None:
                require(set(row['features']) == set(names), 'Partial vector')
                provenance = row.get('precutoff_history_provenance') or row['full_history_provenance']
                pass_name = provenance.get('pass_name',provenance.get('chosen_pass'))
                entry = checkpoints[dataset][pass_name][row['source_id']]
                prefix = entry['prefix']
                require(entry['features'] == row['features'], 'Checkpoint/view feature mismatch')
                require(recount_features(prefix,row['cutoff_height']) == row['features'], 'Independent feature recount failed: '+key)
                tt.append(('vector',tuple(None if row['features'][n] is None else Fraction(row['features'][n]) for n in names)))
                for tx in prefix:
                    tt.extend([('prior',tx['transaction_id']),('any_tx',tx['transaction_id'])])
                    observation_counts[dataset] += 1
            else:
                require(row['precutoff_history_status'] == 'bounded_incomplete', 'Unexpected missing-vector status')
            rows[key] = row;tokens[key] = tt
    groups = partition(tokens)
    old = read(paths['overlap_evidence'])
    require(groups == sorted(g['source_keys'] for g in old['components']), 'Rebuilt components differ from published audit')
    old_by_group = {tuple(g['source_keys']):g for g in old['components']}
    manifest = [];counts = Counter()
    for group in groups:
        c = old_by_group[tuple(group)]
        cross = len({k.split(':',1)[0] for k in group}) > 1
        require(cross == c['cross_development'], 'Cross-component flag mismatch')
        for key in group:
            dataset = key.split(':',1)[0];row = rows[key]
            status = ('excluded_bounded_incomplete' if row['features'] is None else
                      'training' if dataset == 'cryptobilis' else
                      'quarantined_training_link' if cross else 'evaluation')
            label = row[settings['target_fields'][dataset]]
            manifest.append(dict(key=key, dataset=dataset, source_id=row['source_id'],
                component_id=c['component_id'], cross_incident_component=cross,
                membership=label, status=status, features_available=row['features'] is not None))
            counts[(status,label)] += 1
    manifest.sort(key=lambda r:r['key'])
    for status in ['training','evaluation']:
        require(all(counts[(status,label)] >= 20 for label in (0,1)), 'Minimum class support failed')
    require(len(rows) == 1866 and len(groups) == 1281, 'Input population/component count changed')
    summary = dict(selected=len(rows), available_vectors=sum(r['features'] is not None for r in rows.values()),
        components=len(groups), cross_incident_components=sum(g['cross_development'] for g in old['components']),
        prior_transaction_observations=dict(observation_counts), all_available_vectors_recounted=True,
        component_partition_matches_published_audit=True,
        status_counts={s:{'case':counts[(s,1)],'comparison':counts[(s,0)]} for s in sorted({x[0] for x in counts})})
    return rows, names, manifest, summary


def prepare(settings_path, root):
    settings = read(settings_path);out = settings_path.parent
    rows,names,manifest,summary = load_evidence(settings,root)
    save(out/'eligibility_manifest.json',dict(schema_version=1,rows=manifest))
    save(out/'preflight.json',dict(schema_version=1,provider_requests=0,model_fits=0,scores_computed=0,**summary))
    protocol = dict(settings=settings_path.name,settings_sha256=sha(settings_path),
        experiment_code='experiment.py',experiment_code_sha256=sha(out/'experiment.py'),
        fit_code='fit_model.py',fit_code_sha256=sha(out/'fit_model.py'),
        independent_verifier='verify_results.py',independent_verifier_sha256=sha(out/'verify_results.py'),
        eligibility_manifest='eligibility_manifest.json',eligibility_manifest_sha256=sha(out/'eligibility_manifest.json'),
        preflight='preflight.json',preflight_sha256=sha(out/'preflight.json'),
        software={n:importlib.metadata.version(n) for n in ['numpy','scikit-learn','scipy']},
        model_fits_before_publication=0,scores_computed_before_publication=0,
        minimum_class_support=20,model=settings['model'],classification_threshold=0.5,
        training_incident='cryptobilis',evaluation_incident='coldcard',
        validation='No internal split or model selection; parameters and threshold fixed before fit; all 329 available CryptoBilis vectors fit once',
        target='Retrospective incident-source membership with incident-specific operational labels',
        time_direction='October-to-July reverse-time exploratory transfer; no prospective/untouched claim',
        cutoff='Every transaction height strictly below each frozen reference block',
        unavailable_policy='Retain null prefixes without replacement or fabricated vectors',
        overlap_policy='All selected CryptoBilis sources contribute known links; quarantine entire cross-incident components on the Coldcard evaluation side',
        preprocessing='14 numeric fields, train-only medians and 14 fixed missing indicators; zero only for an entirely missing training column',
        comparators=['training_prevalence_constant','descending_prior_inactivity','descending_prior_balance'],
        metrics=['precision','recall','f1','average_precision','roc_auc','confusion_counts'],
        provider_requests=0,unknown_verified_labels_preserved=True)
    save(out/'protocol.json',protocol)
    print(json.dumps(summary,sort_keys=True))


def verify_protocol(protocol_path,root):
    p = read(protocol_path);out = protocol_path.parent
    for name,key in [('settings','settings_sha256'),('experiment_code','experiment_code_sha256'),
        ('fit_code','fit_code_sha256'),('independent_verifier','independent_verifier_sha256'),
        ('eligibility_manifest','eligibility_manifest_sha256'),('preflight','preflight_sha256')]:
        require(sha(out/p[name]) == p[key], 'Frozen protocol file changed: '+name)
    data = load_evidence(read(out/p['settings']),root)
    require(data[2] == read(out/p['eligibility_manifest'])['rows'], 'Frozen eligibility changed')
    return p,data


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode',choices=['prepare','verify-inputs'])
    parser.add_argument('configuration',type=Path)
    parser.add_argument('--repo-root',required=True,type=Path)
    args=parser.parse_args()
    if args.mode=='prepare':prepare(args.configuration.resolve(),args.repo_root.resolve())
    else:
        _,data=verify_protocol(args.configuration.resolve(),args.repo_root.resolve())
        print(json.dumps(data[3],sort_keys=True))
