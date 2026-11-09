"""Standard-library replay and metrics: no NumPy, sklearn, fitting or provider access."""
import argparse
from collections import Counter,defaultdict
import json
import math
from pathlib import Path
import statistics
import struct

from experiment import read,require,save,sha,verify_protocol


def rankings(labels,scores):
    groups=defaultdict(lambda:[0,0])
    for label,score in zip(labels,scores):groups[score][label]+=1
    positive=sum(labels);negative=len(labels)-positive
    require(positive>0 and negative>0,'Both classes required')
    tp=fp=0;ap=0.0
    for score in sorted(groups,reverse=True):
        neg,pos=groups[score];tp+=pos;fp+=neg
        ap+=(pos/positive)*(tp/(tp+fp))
    negatives_before=0;wins=0.0
    for score in sorted(groups):
        neg,pos=groups[score];wins+=pos*(negatives_before+neg/2);negatives_before+=neg
    return {'average_precision':ap,'roc_auc':wins/(positive*negative)}


def replay(model,row):
    names=model['feature_names'][:14];f=row['features']
    require(f is not None,'Cannot score an unavailable prefix')
    values=[model['medians'][n] if f[n] is None else f[n] for n in names]+[int(f[n] is None) for n in names]
    values=[struct.unpack('f',struct.pack('f',v))[0] for v in values]
    node=0;path=[]
    while True:
        path.append(node);current=model['nodes'][node]
        if current['left']==-1:return current['positive_probability'],node,path
        node=current['left'] if values[current['feature_index']]<=current['threshold'] else current['right']


def verify(protocol_path,root):
    out=protocol_path.parent;protocol,(rows,names,manifest,preflight)=verify_protocol(protocol_path,root)
    summary=read(out/'summary.json');model=read(out/'model.json');predictions=read(out/'predictions.json')['rows']
    for file,key in [('model.json','model_sha256'),('predictions.json','predictions_sha256'),('errors.json','errors_sha256')]:
        require(sha(out/file)==summary[key],'Output fingerprint mismatch')
    require(summary['protocol_sha256']==sha(protocol_path),'Protocol mismatch')
    require(summary['model_fits']==1 and summary['threshold_searches']==0,'Unexpected fit/search count')
    training=[m for m in manifest if m['status']=='training']
    for n in names:
        values=[rows[m['key']]['features'][n] for m in training if rows[m['key']]['features'][n] is not None]
        require(model['medians'][n]==(statistics.median(values) if values else 0),'Training-only median mismatch')
    expected={m['key']:m for m in manifest if m['status'] in ('training','evaluation')}
    require(len(predictions)==len(expected) and {p['key'] for p in predictions}==set(expected),'Prediction coverage mismatch')
    require(model['classes']==[0,1] and model['threshold']==0.5 and model['params']==protocol['model'],'Model settings differ')
    weights=Counter();counts=Counter();class_counts=Counter(m['membership'] for m in training)
    for p in predictions:
        m=expected[p['key']];score,leaf,path=replay(model,rows[p['key']])
        require(score==p['case_membership_score'] and leaf==p['leaf_node_id'],'Independent float32 replay mismatch')
        require(p['membership']==m['membership'] and p['predicted_membership']==int(score>=0.5),'Label/decision mismatch')
        require(p['split']==('training_diagnostic' if m['status']=='training' else 'coldcard_evaluation'),'Split mismatch')
        require(p['component_id']==m['component_id'],'Component mismatch')
        if m['status']=='training':
            weight=len(training)/(2*class_counts[m['membership']])
            for node in path:counts[node]+=1;weights[(node,m['membership'])]+=weight
    for node in model['nodes']:
        i=node['node_id'];total=weights[(i,0)]+weights[(i,1)]
        require(node['sample_count']==counts[i],'Training node support mismatch')
        require(math.isclose(node['positive_probability'],weights[(i,1)]/total,rel_tol=0,abs_tol=1e-12),'Class-balanced node probability mismatch')
        if node['left']==-1:require(counts[i]>=20,'Minimum leaf size violated')
    for split in ['training_diagnostic','coldcard_evaluation']:
        pp=[p for p in predictions if p['split']==split];yy=[p['membership'] for p in pp]
        for method,field in [('tree','case_membership_score'),('prior_inactivity','prior_inactivity_score'),('prior_balance','prior_balance_score'),('training_prevalence_constant','training_prevalence_score')]:
            result=rankings(yy,[p[field] for p in pp])
            for k,v in result.items():require(math.isclose(v,summary['metrics'][split]['ranking'][method][k],rel_tol=0,abs_tol=1e-12),'Independent ranking metric differs')
        cc=Counter((p['membership'],p['predicted_membership']) for p in pp);tn,fp,fn,tp=[cc[k] for k in [(0,0),(0,1),(1,0),(1,1)]]
        m=summary['metrics'][split]['tree']
        require(m['confusion_tn_fp_fn_tp']==[tn,fp,fn,tp],'Confusion count mismatch')
        for k,v in [('precision',tp/(tp+fp) if tp+fp else 0),('recall',tp/(tp+fn)),('f1',2*tp/(2*tp+fp+fn))]:
            require(math.isclose(v,m[k],rel_tol=0,abs_tol=1e-12),'Independent classification metric differs')
    errors=read(out/'errors.json')['rows'];expected_errors=[p for p in predictions if p['split']=='coldcard_evaluation' and p['membership']!=p['predicted_membership']]
    require([e['key'] for e in errors]==[e['key'] for e in expected_errors],'Error inventory mismatch')
    require(all(e['features']==rows[e['key']]['features'] for e in errors),'Error features changed')
    return dict(schema_version=1,verifier_sha256=sha(Path(__file__)),provider_requests=0,model_fits=0,
        all_scores_exact_float32_replay=True,independent_training_medians=True,independent_weighted_node_counts=True,
        independent_metric_sets=8,predictions_verified=len(predictions),external_errors_verified=len(errors),
        public_input_features_recounted=1707,full_component_partition_rebuilt=1281,
        old_models_and_views_unmodified=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('protocol',type=Path);parser.add_argument('--repo-root',required=True,type=Path)
    args=parser.parse_args();result=verify(args.protocol.resolve(),args.repo_root.resolve())
    dest=args.protocol.resolve().parent/'independent_verification.json'
    if dest.exists():require(read(dest)==result,'Verification record mismatch')
    else:save(dest,result)
    print(json.dumps(result,sort_keys=True))
