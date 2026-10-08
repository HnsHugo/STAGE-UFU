"""Group direct-parent candidates by shared collectors/descendant consolidations.
Usage: python extract_candidate_groups.py blocks parents.json candidate_groups.json
Groups describe only observed links; background independence remains unverified.
"""
import hashlib
import json
from pathlib import Path
import sys
from audit_coldcard_parents import transactions, SEEDS


def grouping(path,parents):
    wanted={}
    collectors={}
    found=set()
    for height,tx in transactions(path):
        seed=tx['hash']
        if seed not in SEEDS:continue
        found.add(seed)
        collectors[seed]={i['prev_out']['addr'] for i in tx['inputs'] if i['prev_out'].get('addr')}
        for i in tx['inputs']:
            o=i['prev_out'];wanted.setdefault(o['tx_index'],set()).add(seed)
    root={s:s for s in found}
    def find(s):
        while root[s]!=s:
            root[s]=root[root[s]];s=root[s]
        return s
    def union(a,b):
        a,b=find(a),find(b)
        if a!=b:root[max(a,b)]=min(a,b)
    seeds=sorted(found)
    for i,a in enumerate(seeds):
        for b in seeds[i+1:]:
            if collectors[a]&collectors[b]:union(a,b)
    for children in wanted.values():
        children=sorted(children)
        for c in children[1:]:union(children[0],c)
    rows=[]
    for height,tx in transactions(path):
        if tx['tx_index'] in wanted:
            children=sorted(wanted[tx['tx_index']])
            rows.append({'txid':tx['hash'],'group_id':find(children[0]),'descendant_seed_txids':children})
    expected={r['txid'] for r in parents['parents']}
    if {r['txid'] for r in rows}!=expected:raise ValueError('Candidate coverage differs from parents report.')
    counts={}
    for r in rows:counts[r['group_id']]=counts.get(r['group_id'],0)+1
    return {'warning':'Observed candidate-only groups. Missing blocks and background relationships may still cause leakage.',
            'group_counts':counts,'seeds_found':sorted(found),'seeds_missing':sorted(SEEDS-found),
            'candidates':sorted(rows,key=lambda r:r['txid'])}

if __name__=='__main__':
    if len(sys.argv)!=4:sys.exit('Usage: python extract_candidate_groups.py blocks parents.json candidate_groups.json')
    output=Path(sys.argv[3])
    if output.exists():sys.exit('Output already exists; choose a new path.')
    raw=Path(sys.argv[2]).read_bytes();p=json.loads(raw)
    r=grouping(sys.argv[1],p);r['parent_report_sha256']=hashlib.sha256(raw).hexdigest()
    with output.open('x') as f:json.dump(r,f,indent=2)
    print(json.dumps({'group_counts':r['group_counts'],'candidate_count':len(r['candidates'])}))
