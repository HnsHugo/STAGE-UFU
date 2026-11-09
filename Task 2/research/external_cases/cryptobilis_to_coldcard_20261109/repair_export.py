"""Remove a redundant probability normalization without refitting or rescoring."""
import argparse
import copy
import json
from pathlib import Path

from experiment import read,require,save,sha,verify_protocol
from verify_results import replay


def repair(protocol_path,root):
    out=protocol_path.parent
    require(not (out/'export_correction.json').exists(),'Correction already exists; do not repeat')
    _,(rows,_,_,_)=verify_protocol(protocol_path,root)
    original=read(out/'model.json');model=copy.deepcopy(original);summary=read(out/'summary.json')
    require(sha(out/'model.json')==summary['model_sha256'],'Initial model fingerprint differs')
    require(sha(out/'predictions.json')==summary['predictions_sha256'],'Predictions fingerprint differs')
    require(sha(out/'errors.json')==summary['errors_sha256'],'Errors fingerprint differs')
    predictions=read(out/'predictions.json')['rows'];observed={};deltas=[]
    for p in predictions:
        score,leaf,_=replay(original,rows[p['key']])
        require(leaf==p['leaf_node_id'],'Path differs; this correction cannot repair paths')
        require(abs(score-p['case_membership_score'])<=1e-12,'Difference exceeds rounding-only scope')
        require(int(score>=.5)==p['predicted_membership'],'Decision differs; cannot repair')
        if leaf in observed:require(observed[leaf]==p['case_membership_score'],'Estimator leaf scores differ')
        observed[leaf]=p['case_membership_score'];deltas.append(abs(score-p['case_membership_score']))
    require(set(observed)=={n['node_id'] for n in model['nodes'] if n['left']==-1},'Not every fitted leaf is observed')
    for leaf,score in observed.items():model['nodes'][leaf]['positive_probability']=score
    for p in predictions:
        score,leaf,_=replay(model,rows[p['key']])
        require(score==p['case_membership_score'] and leaf==p['leaf_node_id'],'Corrected replay is not exact')
    initial_model_sha=sha(out/'model.json');initial_summary_sha=sha(out/'summary.json')
    (out/'model_export_initial.json').write_bytes((out/'model.json').read_bytes())
    (out/'summary_initial.json').write_bytes((out/'summary.json').read_bytes())
    (out/'model.json').write_text(json.dumps(model,indent=2,sort_keys=True,allow_nan=False)+'\n')
    correction=dict(schema_version=1,reason='sklearn 1.8 predict_proba returns stored tree values directly; the initial exporter redundantly divided by their floating-point sum',
        scope='Only exact saved estimator leaf probabilities replace renormalized exported leaf probabilities',
        initial_model_sha256=initial_model_sha,initial_summary_sha256=initial_summary_sha,
        corrected_model_sha256=sha(out/'model.json'),predictions_sha256=summary['predictions_sha256'],
        errors_sha256=summary['errors_sha256'],correction_code_sha256=sha(Path(__file__)),
        changed_leaf_probabilities=sum(original['nodes'][leaf]['positive_probability']!=score for leaf,score in observed.items()),
        original_probability_mismatches=sum(d>0 for d in deltas),maximum_absolute_probability_delta=max(deltas),
        paths_changed=0,decisions_changed=0,metrics_changed=False,model_fits=0,provider_requests=0,
        all_scores_exact_after_correction=True,training_and_test_predictions_preserved=True)
    save(out/'export_correction.json',correction)
    summary.update(model_sha256=sha(out/'model.json'),initial_model_sha256=initial_model_sha,
        initial_summary_sha256=initial_summary_sha,export_correction_sha256=sha(out/'export_correction.json'))
    (out/'summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True,allow_nan=False)+'\n')
    print(json.dumps(correction,sort_keys=True))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('protocol',type=Path);parser.add_argument('--repo-root',required=True,type=Path)
    a=parser.parse_args();repair(a.protocol.resolve(),a.repo_root.resolve())
