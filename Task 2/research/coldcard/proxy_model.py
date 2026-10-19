"""Export/apply a research candidate-relation tree as plain JSON, no pickle.
fit: python proxy_model.py fit transactions.csv.gz model.json
score: python proxy_model.py score model.json other_features.csv.gz scores.csv.gz
Scores are weighted leaf proportions, not calibrated probabilities of theft.
"""
import csv,gzip,hashlib,json,sys
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from train_exploratory import FEATURES,EXPECTED_SHA


def export(model):
    t=model.tree_
    values=t.value[:,0,:]
    scores=(values[:,1]/values.sum(axis=1)).tolist()
    return {'features':FEATURES,'children_left':t.children_left.tolist(),
            'children_right':t.children_right.tolist(),'feature':t.feature.tolist(),
            'threshold':t.threshold.tolist(),'candidate_score':scores}


def score_rows(frame,model):
    if model['features']!=FEATURES:raise ValueError('Unsupported feature schema.')
    x=frame[FEATURES].to_numpy(np.float32)  # Match sklearn tree input conversion.
    if not np.isfinite(x).all():raise ValueError('Missing/nonfinite features.')
    scores=[]
    for row in x:
        node=0;visits=0
        while model['children_left'][node]!=-1:
            visits+=1
            if visits>len(model['feature']):raise ValueError('Cyclic model tree.')
            col=model['feature'][node]
            if col<0 or col>=len(FEATURES):raise ValueError('Invalid feature index.')
            node=(model['children_left'][node] if float(row[col])<=model['threshold'][node] else model['children_right'][node])
            if node<0 or node>=len(model['feature']):raise ValueError('Invalid child index.')
        scores.append(model['candidate_score'][node])
    return np.array(scores)


def fit(source,destination):
    if Path(destination).exists():raise ValueError('Output already exists.')
    with open(source,'rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
    if digest!=EXPECTED_SHA:raise ValueError('Dataset differs from inspected features.')
    df=pd.read_csv(source);df=df[(df.is_coinbase==0)&(df.relation!='source_attributed')]
    if not np.isfinite(df[FEATURES].to_numpy(float)).all():raise ValueError('Missing/nonfinite features.')
    model=DecisionTreeClassifier(max_depth=4,min_samples_leaf=20,class_weight='balanced',random_state=42)
    model.fit(df[FEATURES],df.relation.eq('direct_parent_candidate').astype(int))
    result=export(model)
    result.update(target='direct_parent_candidate relation',warning='Research-only proxy labels. Weighted score is not a calibrated theft or hardware probability.',
                  training_sha256=digest,training_rows=len(df),candidate_rows=int(df.relation.eq('direct_parent_candidate').sum()),
                  evaluation='See GROUPED_EXPERIMENT.md. This final tree uses all eligible data; no held-out performance is claimed for this fitted artifact.')
    with open(destination,'x') as f:json.dump(result,f,indent=2)


def apply(model_path,source,destination):
    if Path(destination).exists():raise ValueError('Output already exists.')
    model=json.load(open(model_path))
    with gzip.open(destination,'xt',newline='') as stream:
        w=csv.writer(stream);w.writerow(['txid','research_candidate_score','research_candidate_like','interpretation'])
        for df in pd.read_csv(source,chunksize=20000):
            ordinary=df[df.is_coinbase==0].copy() if 'is_coinbase' in df else df
            scores=score_rows(ordinary,model)
            for txid,s in zip(ordinary.txid,scores):
                w.writerow([txid,float(s),int(s>=.5),'similar_to_training_candidates_not_confirmed_theft'])

if __name__=='__main__':
    if len(sys.argv)==5 and sys.argv[1]=='score':apply(*sys.argv[2:])
    elif len(sys.argv)==4 and sys.argv[1]=='fit':fit(*sys.argv[2:])
    else:sys.exit('fit: proxy_model.py fit features.csv.gz model.json | score: proxy_model.py score model.json features.csv.gz output.csv.gz')
