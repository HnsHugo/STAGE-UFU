"""Generate an article supplement from published frozen results, without inference.

No model library, fitting, provider HTTP or new score is used. Existing study,
model, data, predictions, quarantine and incomplete outcomes stay immutable.
"""
import argparse
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess

import build_source_address_study as prior

TASK = Path(__file__).resolve().parents[1]
DATA = TASK / 'research'
OUTPUT = TASK / 'source_transfer_study_20261104'
FROZEN = DATA/'external_cases/cryptobilis_frozen_transfer_20261104_215520'
OVERLAP = DATA/'external_cases/cryptobilis_overlap_20261104_205032'
BASELINE = DATA/'coldcard/source_membership_baseline_20261102_162335'
RESULT_COMMIT = '8d0b0e345cbcb29d2e435cb9a9906a873721b825'
PROTOCOL_COMMIT = '719067dd4467bd59d7da6004cacad022fb5aaf68'
MODEL_SHA = '87101573c2de885adfdb9cfb194cf12366b4dc94b4bb9e51e0435bf5e570f537'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value):
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False)+'\n').encode()


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == '.gz' else data)


def validated():
    sources = dict(protocol=FROZEN/'protocol.json', results=FROZEN/'summary.json',
        predictions=FROZEN/'predictions.json.gz', errors=FROZEN/'errors.json.gz',
        scoring_manifest=FROZEN/'scoring_manifest.json.gz', verification=FROZEN/'verification.json',
        independent=FROZEN/'independent_verification.json', execution=FROZEN/'execution_validation.json',
        overlap=OVERLAP/'summary.json', eligibility=OVERLAP/'eligibility_manifest.json.gz',
        overlap_verification=OVERLAP/'independent_verification.json',
        acquisition=DATA/'external_cases/cryptobilis_reference_prefix_20261104_201345/final_acquisition_audit.json',
        source_selection=DATA/'external_cases/cryptobilis_source_selection_20261103_002428/selection_audit.json',
        source_evidence=DATA/'external_cases/cryptobilis_source_readiness_20261102/scope_audit.json',
        transfer_contract=DATA/'external_cases/cryptobilis_source_readiness_20261102/transfer_protocol.json',
        model=BASELINE/'model.json', baseline=BASELINE/'summary.json', split=BASELINE/'split_manifest.json.gz',
        external_view=DATA/'external_cases/cryptobilis_reference_prefix_20261104_201345/precutoff_feature_view.json.gz',
        previous_study_provenance=TASK/'source_address_study/provenance.json',
        existing_table_adapter=Path(prior.__file__),
        existing_article_preamble=TASK/'source_address_study/article_preamble.tex',
        previous_study_pdf=TASK/'source_address_study/source_address_study.pdf')
    data = {name: read(path) for name, path in sources.items() if path.suffix in ('.json','.gz')}
    protocol, result, verify = data['protocol'], data['results'], data['verification']
    require(verify['protocol_sha256'] == sha(sources['protocol'].read_bytes()), 'Frozen protocol changed')
    for name, expected in verify['outputs'].items():
        require(sha((FROZEN/name).read_bytes()) == expected, 'Frozen output changed: '+name)
    for pin in protocol['inputs'].values():
        path = (DATA/pin['file']).resolve()
        require(path.is_relative_to(DATA) and sha(path.read_bytes()) == pin['sha256'], 'Frozen input changed: '+pin['file'])
    require(sha(sources['model'].read_bytes()) == MODEL_SHA, 'Fitted model changed')
    require(sha(sources['existing_table_adapter'].read_bytes()) == data['previous_study_provenance']['builder_sha256'] and
            prior.PREAMBLE.encode() == sources['existing_article_preamble'].read_bytes(), 'Previous article adapter/preamble changed')
    predictions = data['predictions'];ids = {p['source_id'] for p in predictions}
    eligible = {p['source_id'] for p in data['eligibility']['rows'] if p['status'] == 'eligible_for_frozen_proxy_evaluation'}
    require(len(predictions) == len(ids) == 275 and ids == eligible, 'Scoring population changed')
    confusion = Counter((p['cryptobilis_reference_source_membership'], p['predicted_cryptobilis_reference_source_membership']) for p in predictions)
    actual = [confusion[k] for k in [(1,1),(0,1),(1,0),(0,0)]]
    require(actual == [57,2,65,151], 'Published external confusion changed')
    metric = result['primary_metrics']['frozen_tree']
    require(abs(2*actual[0]/(2*actual[0]+actual[1]+actual[2])-metric['f1_membership']) < 1e-12, 'Saved F1/counts disagree')
    require(len(data['errors']) == 67 and {e['source_id'] for e in data['errors']} ==
            {p['source_id'] for p in predictions if p['cryptobilis_reference_source_membership'] != p['predicted_cryptobilis_reference_source_membership']},
            'Error evidence changed')
    manifest = data['scoring_manifest']['rows']
    require(len(manifest) == 366 and sum(p['score_available'] for p in manifest) == 275 and
            all(p['frozen_coldcard_membership_score'] is None for p in manifest if not p['score_available']), 'Excluded-source scores changed')
    require(data['independent']['exact_numpy_float32_scores_and_paths'] == 275 and
            data['independent']['prediction_export_sha256'] == sha(sources['predictions'].read_bytes()), 'Independent score verification changed')
    require(data['overlap']['counts']['comparison']['quarantined_complete'] == 54 and
            data['acquisition']['bounded_incomplete'] == 37, 'Coverage/quarantine changed')
    require(result['fixed_node_support']['1']['false_negative_membership'] == 63 and
            result['fixed_node_support']['5']['false_negative_membership'] == 2 and
            data['baseline']['node_support']['1']['train']['case'] == 0, 'Fixed-branch error explanation changed')
    require(data['source_selection']['cases'] == 122 and data['source_selection']['comparisons'] == 244 and
            data['source_selection']['block_transactions'] == 7944 and
            data['source_selection']['unique_decoded_positive_input_sources'] == 9356, 'Frozen census changed')
    require(all(all(v is None for v in row['labels'].values()) and row['full_history_status'] == 'not_collected_for_this_source'
                for row in data['external_view']['rows']), 'External labels/full-history statuses changed')
    require(result['new_model_fits'] == result['preprocessing_fits'] == result['provider_requests'] == 0, 'Unexpected execution scope')
    pins = {name: dict(file=str(path.relative_to(TASK)), sha256=sha(path.read_bytes())) for name,path in sources.items()}
    return data, pins


def narrative(d):
    s = d['results'];tree = s['primary_metrics']['frozen_tree']
    cohort = prior.table(['Stage', 'Case sources', 'Comparisons', 'Total'],
        [['Fixed selection',122,244,366],['Complete prior-prefix vectors',122,207,329],
         ['Complete vectors quarantined',0,54,54],['Bounded prefixes, no vector',0,37,37],['Scored cohort',122,153,275]])
    methods = f'''# External source dataset and fixed protocol

## Question, observation unit and evidence

We asked whether a frozen model of Coldcard source membership transports to an explicitly defined source-linkage proxy in a second historical incident. One observation is one decoded Bitcoin input source address with a fixed reference payment. Membership identifies a relation to the selected case corpus; it does not verify a victim, signing device or seed origin. The original target, `known_coldcard_core_membership`, and external target, `cryptobilis_reference_source_membership`, remain separate operational definitions.

The Coldcard development study retains 500 core sources and 1,000 fixed same-block comparisons. It provides 1,378 complete prior-prefix vectors (500 cases, 878 comparisons); 122 incomplete comparisons remain unscored. Its 918 measured-link components yielded fixed training/validation/test supports of 1,033/111/234 addresses. The original one-incident fitted result is preserved, rather than retrained with external examples.

For the historically attributed CryptoBilis collectors, the pinned snapshots identify 122 source candidates in 122 reference payments, with 140 input-outpoint observations. Their reference blocks are 970590 and 970591, in the fixed UTC day of 9 October 2026. All source-level independently verified compromise, signing-device and seed-origin labels remain unknown. The historical attribution could not be refreshed in the earlier source review; it is not upgraded here. Both collectors belong to the same external incident.

## Acquisition, deterministic comparisons and attrition

The two height/hash-anchored complete blocks contain 7,944 transactions and 9,356 distinct decoded positive input sources. A frozen salted hash ranking selects 244 comparisons, with block quotas 222 and 22. Exclusions include all 1,500 development addresses and the prespecified case/source/collector exclusions. Reference assignment uses the first occurrence by block height and lexical TXID. No collection failure, vector, fee or score changes the sample or triggers replacement.

The anchored prior-prefix collector reuses the recorded Blockstream Esplora route, checks reference block/hash and input value/count, funding closure, reverse-height order and an empty terminal page. Its original pilot matched prefixes and all fourteen variables for eight complete-history controls. Four bounded passes finalized all 366 external selections: 329 complete vectors and 37 retained bounded-incomplete comparisons. Across the passes, 2,262 saved/reused response fingerprints and 19 batch snapshots were verified. Provider-indexed prefix reconciliation does not establish cryptographic inclusion or a complete current address history. This supplement requests no provider data.

{cohort}

Case prevalence rises from 122/366 (33.33%) in the original selection, to 122/329 (37.08%) among complete vectors and 122/275 (44.36%) in the scored cohort. The 54 quarantined complete vectors and 37 incomplete prefixes stay in the saved selection with null scores. These are conditional complete-case/quarantine results, not unbiased estimates for all selected sources.

## Cutoff, overlap and unchanged model

Every predictor uses only confirmed transaction heights strictly below its own frozen reference height. The entire reference block and future are excluded. The unchanged fourteen variables measure receipt/spending transaction and output counts, received/spent/balance values in satoshis, unspent outputs, active blocks, activity span, age/inactivity and median prior-spending fee rate. Reference-payment outcomes, identifiers, labels, provider counters and evidence metadata are excluded from model inputs.

All 1,866 development/external identities and all available normalized prefixes enter the overlap audit. Links comprise repeated address hashes, common prior transactions, common reference payments and exact complete-vector equality including missingness. A conservative transaction-role guard also checks a prior reference in one dataset against an event reference in the other. Forty-five shared prior-transaction groups and one identical-vector group generate four components spanning both datasets. All their external members are quarantined: 67 comparisons, of which 54 have vectors and 13 are already incomplete. Transitive closure matters; quarantine is not restricted to directly matching addresses. Independent graph reconstructions agree, and the original development groups and partitions are unchanged.

Exactly 122 cases and 153 comparisons remain eligible. This passes the frozen overall minimum of 20 per class, without asserting that each block meets that support. All external observations remain outside fitting. Missing links of 122 incomplete Coldcard prefixes and 37 incomplete external prefixes are unknown; measured-link quarantine is not proof of entity independence.

The existing Gini decision tree retains maximum depth 3, minimum 20 samples per leaf, balanced training class weights and seed 42. Fourteen numeric values use only the original training medians, with fourteen fixed missing indicators. The exported JSON tree receives float32 inputs and keeps its original score decision of at least 0.5. Its class-balanced training leaf proportions are not calibrated theft/device probabilities. No model/preprocessing fit, feature search, new split, calibration or threshold change is performed.

## Prespecified comparisons and reproducibility

The comparators are constant Coldcard-training membership prevalence (346/1,033), descending prior inactivity and descending prior balance. The latter use the same training-only median fills, in float64; they have ranking metrics only. We report AP and ROC-AUC for all methods and precision, recall, F1 and confusion counts for the tree at its unchanged threshold. Block results are descriptive strata of one incident.

The protocol and both implementations were published before the first external scores. A standard-library tree traversal and the preserved NumPy implementation agree exactly on all 275 float32 scores, paths and missingness patterns. Scikit-learn independently agrees with all twelve overall/block/method metric sets. All 67 errors, node supports and 91 exclusions are verified; fitting paths are blocked during verification. Twenty failure-oriented tests pass. This write-up reads those saved results without inference, fitting or collection.
'''
    metric_rows = []
    for name, title in [('frozen_tree','Frozen tree'),('inactivity_rank','Prior inactivity'),('balance_rank','Prior balance'),('constant_train_prevalence','Training-prevalence constant')]:
        value=s['primary_metrics'][name]
        metric_rows.append([title, f"{value['average_precision_membership']:.6f}",f"{value['roc_auc_membership']:.6f}",
                            f"{value['f1_membership']:.6f}" if name=='frozen_tree' else 'Ranking only'])
    metrics = prior.table(['Method','AP','ROC-AUC','F1'], metric_rows)
    confusion = prior.table(['External proxy class','Predicted positive','Predicted negative'],
                            [['Case source',57,65],['Comparison',2,151]])
    blocks = prior.table(['Reference block','Cases / comparisons','Tree F1','Tree AP','Inactivity AP'],
        [[height,f"{values['frozen_tree']['case']} / {values['frozen_tree']['comparison']}",
          f"{values['frozen_tree']['f1_membership']:.6f}",f"{values['frozen_tree']['average_precision_membership']:.6f}",
          f"{values['inactivity_rank']['average_precision_membership']:.6f}"] for height,values in s['descriptive_metrics_by_block'].items()])
    leaves = prior.table(['Leaf','Frozen score','Cases','Comparisons','FN','FP'],
        [[node,f"{d['model']['tree']['case_membership_score'][int(node)]:.6f}",v['case'],v['comparison'],v['false_negative_membership'],v['false_positive_membership']]
         for node,v in s['fixed_node_support'].items() if d['model']['tree']['children_left'][int(node)]==-1])
    results = f'''# External results and interpretation

## Frozen transfer performance

On the 275 eligible external addresses, the frozen tree attains membership precision {tree['precision_membership']:.6f}, recall {tree['recall_membership']:.6f} and F1 {tree['f1_membership']:.6f}. It recovers 57 of 122 case sources, misses 65 and assigns two of 153 comparisons to the case class. AP is {tree['average_precision_membership']:.6f} and ROC-AUC is {tree['roc_auc_membership']:.6f}.

{metrics}

{confusion}

The fixed inactivity ranking has higher AP and ROC-AUC than the tree, as does the balance ranking. No classification threshold was fitted for either comparator, so their AP values are not comparator F1 scores. The constant's score remains the training prevalence 0.334947; its external AP equals the scored prevalence 0.443636, with ROC-AUC 0.5. This is a ranking property of a constant, not external recalibration.

The preserved Coldcard internal test F1 is 0.989796 (97 TP, 135 TN, one FP and one FN). The external experiment uses a different source-membership target and a selected population in another incident. It therefore does not measure the same estimand, but demonstrates that the strong internal separation does not ensure reliable transport under the specified external proxy. No threshold was changed to improve this observed result.

{blocks}

The second block has only eleven case sources and eighteen comparisons. These stratum summaries are not independent replications, significance tests or separate minimum-20 claims. The incident, entity dependence and selection limits remain present even where a univariate ranking is high.

## Fixed-rule error diagnosis

The root tests float32-converted prior balance against 14,820,511.5 satoshis (about 0.148205 BTC). Its lower-balance branch contained zero case sources and 642 comparisons in the Coldcard training export. In CryptoBilis, 63 case sources and 137 comparisons enter this branch. All 63 case sources become false negatives under the unchanged rule. The two remaining false negatives have higher balances but enter the fixed inactivity-at-most-1,006.5-block branch. This is an exact replay explanation, not a newly selected threshold or a causal account of incident differences.

{leaves}

Both numeric split variables are observed for every scored address. Prior-spending fee rate is undefined for 121 cases and 101 comparisons; its saved median/indicator is preserved, but neither appears in a tree split. The observed errors reproduce through the fixed balance/inactivity conditions rather than a preparation mismatch. All 67 errors retain their source ID, original fourteen values, label tier, reference hash, component, score and path in the machine-readable export.

## Limits and supported conclusion

The operational positive label is linkage to a selected historical collector payment, not independently verified loss or hardware use. Comparisons are unattributed outside-reference sources, not certified legitimate or non-hardware examples. Both collector snapshots belong to one already inspected incident. Neither the address count nor measured-link grouping establishes independent victims, devices or entities; no untouched or prospective test is claimed.

Coverage and quarantine change the evaluation population and class prevalence. Incomplete prefixes have no vector, while an exhausted prior prefix does not certify an entire current history. Individual CryptoBilis full-current-history status remains not collected for this source. The separate Coldcard comparison full-history counts (864 complete, 136 incomplete) are unchanged. Provider reconciliation, cryptographic inclusion, source attribution and owner/device evidence are distinct claims.

The results support a reproducible, limited comparison of source-linkage profiles. They expose a failure of reliable frozen-tree transport and show that a prespecified inactivity ranking can outperform that model in this selected sample. They do not validate theft probabilities, hardware-wallet identification or population-wide generalization. The high inactivity AP also does not turn inactivity into a validated theft detector. Preserving the negative transfer result is scientifically necessary; adapting the tree or its threshold to these inspected answers would require a separately specified design and independent evaluation evidence.
'''
    return methods, results


WRAPPER = r'''\documentclass[11pt,a4paper]{article}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage[margin=23mm]{geometry}
\usepackage[hidelinks]{hyperref}
\input{transfer_preamble}
\setlength{\emergencystretch}{2em}
\hypersetup{pdftitle={Coldcard to CryptoBilis: Frozen Source-Membership Transfer},pdfauthor={Research supplement}}
\title{Coldcard to CryptoBilis\\Frozen Source-Membership Transfer}
\author{Research supplement}
\date{4 November 2026}
\begin{document}
\maketitle
\begin{abstract}
An existing source-membership tree is transported without refitting from the Coldcard cohort to an explicitly defined CryptoBilis source-linkage proxy. After fixed acquisition and measured-component quarantine, 275 addresses remain eligible. The tree reaches membership F1 0.629834, with high precision and limited recall; a fixed inactivity ranking has higher AP. This supplement reports methods, attrition, exact errors and evidence limits. It does not establish verified theft/device detection or untouched independent-incident validation.
\end{abstract}
\section{Our Work: external source study}
\input{transfer_methods}
\section{Results: frozen transfer}
\input{transfer_results}
\section{Reproducibility record}
The accompanying provenance record and README contain input hashes, exact tables and a source-to-claim map. The supplied article, authors, bibliography and earlier study remain unchanged.

Saved records: \href{https://github.com/HnsHugo/STAGE-UFU/commit/719067dd4467bd59d7da6004cacad022fb5aaf68}{preregistered protocol (719067d)};
\href{https://github.com/HnsHugo/STAGE-UFU/commit/8d0b0e345cbcb29d2e435cb9a9906a873721b825}{frozen results and all errors (8d0b0e3)};
\href{https://github.com/HnsHugo/STAGE-UFU/commit/9cd2408880a354c86513c73f7112f45578615594}{overlap and eligibility (9cd2408)}.
\end{document}
'''


def render(markdown):
    data = subprocess.run(['pandoc','--from=markdown','--to=latex','--shift-heading-level-by=1','--wrap=auto'],
                          input=markdown.encode(),capture_output=True,check=True).stdout
    def break_identifier(match):
        return b'\\texttt{'+match[1].replace(b'\\_',b'\\_\\allowbreak{}')+b'}'
    return b'\\begingroup\n\\setlength{\\emergencystretch}{2em}\n'+re.sub(rb'\\texttt\{([^{}]*)\}',break_identifier,data)+b'\n\\endgroup\n'


def build():
    data,pins = validated();methods,results = narrative(data)
    intro = '''# Frozen source-membership transfer supplement

English article-ready supplement to the preserved [Coldcard source-address study](../source_address_study/README.md). It reports the completed CryptoBilis transfer and its negative transport result, without fitting or recomputing model scores.

[PDF review copy](source_transfer_study.pdf) · [Our Work fragment](transfer_methods.tex) · [Results fragment](transfer_results.tex) · [Saved experiment](../research/external_cases/cryptobilis_frozen_transfer_20261104_215520/README.md)

## Article integration

Retain the original article and the two earlier Coldcard fragments. Add `transfer_methods.tex` under `Our Work`, after the source dataset/baseline description, and `transfer_results.tex` under `Results`, after the fixed Coldcard results. The `transfer_preamble.tex` packages match the earlier supplement: use those packages only once, with the article's existing `hyperref`. The wrapper `report.tex` is a standalone review copy and does not replace the main article, author list or bibliography. No live Overleaf document or originally supplied article file was edited.

For an uploaded folder named `source_transfer_study_20261104`, the additions are:

```tex
% Preamble: skip this input if these packages were already added for the Coldcard supplement.
\\input{source_transfer_study_20261104/transfer_preamble}
% Inside Our Work, after the earlier source_methods:
\\input{source_transfer_study_20261104/transfer_methods}
% Inside Results, after the earlier source_results:
\\input{source_transfer_study_20261104/transfer_results}
```

The existing introduction should distinguish the completed tabular baseline and proxy transfer from proposed GNN work. The conclusion should report the limited transport and stronger inactivity ranking, without claiming verified theft/device identification. [ARTICLE_MAP](../docs/ARTICLE_MAP.md) tracks the supplied outline. [Provenance](provenance.json) records saved sources and generated-text hashes; [facts](tables.json) retain exact values.

'''
    def subordinate(text):
        return '\n'.join('#'+line if line.startswith('#') else line for line in text.splitlines())+'\n'
    check = '''
## Saved sources and reproduction

- [Historical source evidence and attribution limits](../research/external_cases/cryptobilis_source_readiness_20261102/README.md).
- [Deterministic complete-block census and selection](../research/external_cases/cryptobilis_source_selection_20261103_002428/README.md).
- [Final bounded acquisition audit](../research/external_cases/cryptobilis_reference_prefix_20261104_201345/README.md).
- [Overlap, quarantine and eligibility](../research/external_cases/cryptobilis_overlap_20261104_205032/README.md).
- [Fixed model, all scores/errors and independent verification](../research/external_cases/cryptobilis_frozen_transfer_20261104_215520/README.md).
- [Original Coldcard fitted study](../research/coldcard/source_membership_baseline_20261102_162335/README.md).

The supplement's builder checks saved hashes, source selection, confusion/F1, errors, exclusions and branch counts. It imports no model library, evaluates no model and queries no provider. Render/compile records are in `validation.json`; the previous five-page Coldcard report is preserved separately.

```sh
python "Task 2/docs/build_source_transfer_study.py" check
```
'''
    files={'README.md':(intro+subordinate(methods)+'\n'+subordinate(results)+check).encode(),
           'transfer_methods.tex':render(methods),'transfer_results.tex':render(results),
           'transfer_preamble.tex':prior.PREAMBLE.encode(),'report.tex':WRAPPER.encode()}
    facts=dict(schema_version=1, result_commit=RESULT_COMMIT, preregistered_commit=PROTOCOL_COMMIT,
        external_results=data['results'], overlap_counts=data['overlap']['counts'],
        acquisition_classes=data['acquisition']['classes'],
        coldcard_internal_test=data['baseline']['partition_metrics']['test']['tree'],
        low_balance_branch_training=data['baseline']['node_support']['1']['train'],
        unknown_labels_unchanged=True, model_fits=0, new_scores=0, provider_requests=0)
    files['tables.json']=encoded(facts)
    files['provenance.json']=encoded(dict(schema_version=1, date='2026-11-04',input_commit=RESULT_COMMIT,
        preregistered_commit=PROTOCOL_COMMIT, inputs=pins, builder_sha256=sha(Path(__file__).read_bytes()),
        inherited_frozen_input_pins_verified=len(data['protocol']['inputs']),
        generated_text_sha256={name:sha(value) for name,value in files.items()},
        claim_map=dict(sampling='source_selection',coverage='acquisition',quarantine='overlap',
            exact_metrics='results',error_counts='predictions/errors',fixed_rule_explanation='model/baseline/results',
            independent_verification='independent'),
        original_article_layout='Existing source_address_study integration contract; originals and live Overleaf unchanged',
        model_fits=0,new_scores=0,provider_requests=0))
    return files


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('mode',choices=['build','check'])
    args=parser.parse_args();files=build()
    if args.mode=='build':
        OUTPUT.mkdir(exist_ok=True)
        for name,data in files.items():
            (OUTPUT/name).write_bytes(data)
    else:
        for name,data in files.items():
            require((OUTPUT/name).read_bytes()==data,'Write-up differs from saved inputs: '+name)
    print(json.dumps(dict(mode=args.mode,generated_files=len(files),saved_external_predictions_checked=275,
        saved_errors_checked=67,model_fits=0,new_scores=0,provider_requests=0)))
