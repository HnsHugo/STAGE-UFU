"""Build/check the source-address write-up from frozen saved results; no fitting or HTTP."""
import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess


TASK = Path(__file__).resolve().parents[1]
DATA = TASK / 'research/coldcard'
OUTPUT = TASK / 'source_address_study'
BASELINE = 'source_membership_baseline_20261102_162335'
FEASIBILITY = 'source_comparison_feasibility_20261102_1603'
MODEL_COMMIT = '00659df35d3140143fa12b37ba35ea56722a4854'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def json_bytes(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False)+'\n').encode()


def read(relative):
    path = DATA / relative
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == '.gz' else data)


def require(condition, text):
    if not condition:
        raise ValueError(text)


def table(header, rows):
    return '\n'.join(['| '+' | '.join(header)+' |', '| '+' | '.join(['---']*len(header))+' |'] +
                     ['| '+' | '.join(map(str, row))+' |' for row in rows])


FEATURES = [
    ('confirmed_tx_count', 'Distinct confirmed prior transactions affecting the address; count.'),
    ('receipt_tx_count', 'Prior transactions creating an output to the address; count.'),
    ('spending_tx_count', 'Prior transactions consuming an address output; count.'),
    ('received_output_count', 'Prior outputs received by the address; count.'),
    ('spent_output_count', 'Address outputs consumed before cutoff; count.'),
    ('received_sat', 'Sum of received prior-output values; integer satoshis.'),
    ('spent_sat', 'Sum of consumed prior-output values; integer satoshis.'),
    ('balance_sat', 'Received minus spent values before cutoff; integer satoshis.'),
    ('unspent_output_count', 'Received outputs not yet consumed before cutoff; count.'),
    ('active_block_count', 'Distinct prior heights containing address activity; count.'),
    ('activity_span_blocks', 'Last minus first prior activity height; blocks; undefined for an empty prefix.'),
    ('blocks_since_first_activity', 'Reference minus first prior activity height; blocks; undefined for an empty prefix.'),
    ('blocks_since_last_activity', 'Reference minus last prior activity height; blocks; undefined for an empty prefix.'),
    ('median_spending_tx_fee_rate_sat_vb', 'Median whole-transaction fee / virtual size for prior spending; sat/vB; undefined without spending.'),
]


def validated_inputs():
    sources = {
        'model': BASELINE+'/model.json', 'metrics': BASELINE+'/summary.json',
        'protocol': BASELINE+'/protocol.json', 'verification': BASELINE+'/verification.json',
        'predictions': BASELINE+'/predictions.json.gz', 'split': BASELINE+'/split_manifest.json.gz',
        'rules': BASELINE+'/rules.json', 'errors': BASELINE+'/errors.json.gz',
        'feasibility': FEASIBILITY+'/summary.json',
        'selection': 'source_comparison_selection_20261030/selection.json',
        'block_retrieval': 'source_comparison_selection_20261030/block_collection.json',
        'case_view': 'source_dataset_20261030/view.json.gz',
        'feature_view': 'reference_tail_continuation_20261102_1508/precutoff_feature_view.json.gz',
        'case_report': 'source_dataset_20261030/README.md',
        'corroboration_protocol': 'source_corroboration_protocol_20261030.json',
    }
    parsed = {key: read(path) for key, path in sources.items() if not path.endswith('.md')}
    model, summary, protocol, verification = [parsed[k] for k in ('model', 'metrics', 'protocol', 'verification')]
    require(sha((DATA/sources['protocol']).read_bytes()) == verification['protocol_sha256'], 'Model protocol hash changed')
    for name, expected in verification['outputs'].items():
        require(sha((DATA/BASELINE/name).read_bytes()) == expected, 'Fitted artifact changed: '+name)
    for pin in protocol['inputs'].values():
        require(sha((DATA/pin['file']).read_bytes()) == pin['sha256'], 'Fitted input changed: '+pin['file'])
    require(protocol['target'] == 'known_coldcard_core_membership' and model['fit_partition'] == 'train', 'Wrong target/fit scope')
    require([name for name, _ in FEATURES] == protocol['predictor_allowlist'], 'Feature definitions/order changed')
    require(summary['training_fit_calls'] == 1 and not summary['test_used_for_selection'] and
            not summary['hyperparameter_search_performed'], 'Unexpected experiment scope')
    predictions, split = parsed['predictions'], parsed['split']
    require(len(predictions) == len({r['source_id'] for r in predictions}) == 1378, 'Prediction coverage changed')
    require(len(split['rows']) == 1500 and split['excluded_sources'] == 122, 'Selected population changed')
    require(sum(r['partition'] == 'excluded_unavailable_prefix' for r in split['rows']) == 122, 'Exclusions changed')
    require({r['source_id'] for r in predictions} ==
            {r['source_id'] for r in split['rows'] if r['partition'] != 'excluded_unavailable_prefix'}, 'Unscored population changed')
    components = defaultdict(set)
    for row in split['rows']:
        if row['component_id']:
            components[row['component_id']].add(row['partition'])
    require(len(components) == 918 and all(len(v) == 1 for v in components.values()), 'Component split changed')
    for part, values in summary['partition_metrics'].items():
        m = values['tree']
        confusion = Counter((r['known_coldcard_core_membership'], r['predicted_known_coldcard_core_membership'])
                            for r in predictions if r['partition'] == part)
        actual = [confusion[k] for k in [(1, 1), (0, 1), (1, 0), (0, 0)]]
        expected = [m[k] for k in ['true_positive_membership', 'false_positive_membership', 'false_negative_membership', 'true_negative_membership']]
        require(actual == expected, 'Confusion counts disagree with saved scores')
        tp, fp, fn, tn = actual
        require(abs(2*tp/(2*tp+fp+fn)-m['f1_membership']) < 1e-12, 'F1 disagrees with counts')
    case_rows = parsed['case_view']['rows']
    require(sum(r['labels']['reported_loss'] == 1 for r in case_rows) == 1 and
            all(r['labels']['independently_verified_compromise'] is None and
                r['labels']['hardware_signing_at_event'] is None for r in parsed['feature_view']['rows']), 'Evidence tier changed')
    pins = {key: dict(file=path, sha256=sha((DATA/path).read_bytes())) for key, path in sources.items()}
    return parsed, pins


def narrative(d):
    s, f = d['metrics'], d['feasibility']
    coverage = table(['Reference block', 'Case available / selected', 'Comparison available / selected', 'Comparison unavailable'],
                     [[height, f"{next(c for c in f['coverage'] if c['cutoff_height']==height and c['membership']=='case')['available']} / {next(c for c in f['coverage'] if c['cutoff_height']==height and c['membership']=='case')['selected']}",
                       f"{next(c for c in f['coverage'] if c['cutoff_height']==height and c['membership']=='comparison')['available']} / {next(c for c in f['coverage'] if c['cutoff_height']==height and c['membership']=='comparison')['selected']}",
                       next(c for c in f['coverage'] if c['cutoff_height']==height and c['membership']=='comparison')['unavailable']]
                      for height in [960188, 960189, 960190, 960191]])
    feature_table = table(['Predictor', 'Definition and unit'], [[f'`{name}`', meaning] for name, meaning in FEATURES])
    partitions = table(['Partition', 'Cases', 'Comparisons', 'Components'],
                       [[part.title(), s['partition_counts'][part]['case'], s['partition_counts'][part]['comparison'],
                         s['partition_counts'][part]['components']] for part in ('train', 'validation', 'test')])
    methods = f'''# Source-address dataset and evaluation

## Observation unit and evidence

The observation unit is one unique decoded Bitcoin input source address with one fixed reference payment. The case cohort comprises 500 addresses whose payments entered the reported Coldcard collector in blocks 960188-960191 on 30 July 2026 UTC. Five later registry sources are kept outside this study. An address is neither a verified individual, a device nor an independent incident.

The target is `known_coldcard_core_membership`: 1 for these 500 fixed core sources and 0 for the selected sources outside the core and other case exclusions. The latter are operational comparisons, not certified legitimate or non-hardware addresses. All independently verified compromise and signing-device labels remain unknown. One exactly mapped owner report is retained as reported evidence, separate from verified labels. [SomaxBT's reconstruction](https://github.com/somaxbt/coldcard-drain-addresses/tree/1e7fef87060808c29beaf9d137eb5ff9e37f8811) and [Alvaro P.'s reconstruction](https://github.com/alva-p/coldcard-weak-rng-research/tree/f93cfed16302bb91c8409fdee9ce5576a34b7e52) corroborate all 500 source/payment relations. They observe the same chain and do not provide 500 independent owner confirmations. Their exact pinned files and attribution caveats remain in the repository's corroboration record.

## Acquisition, sampling and coverage

The source registry reuses the supplied transaction corpus. The same-block comparison census uses four complete, height/hash-anchored Blockchain.info block responses collected on 30 October. The census contains 5,526 distinct source addresses before exclusions and 5,025 eligible comparisons. A deterministic salted hash ranking selects 1,000 sources, with a two-comparisons-per-case quota in each reference-block stratum. No source is replaced after a collection failure or incomplete history. The census, selection and normalized evidence are public; private raw caches are not redistributed.

Address histories use the recorded Blockstream Esplora API route. Full-history pagination/counter audits and, where necessary, the separately validated anchored pre-cutoff collector support the published prefixes. That anchored method matched both prefixes and all fourteen variables for eight complete-history pilot controls across the four blocks. Successful saved pages were reused only after fingerprint and cursor-sequence checks. Provider reconciliation is not cryptographic inclusion verification. This report performs no new provider requests.

Exactly 1,378 vectors are available: 500 cases and 878 comparisons. The 122 remaining comparison prefixes are bounded-incomplete, with null vectors and no model score. They are retained in the selected population but excluded from fitting and scoring. Full-current-history coverage is a different measure: 864 comparison histories are complete and 136 incomplete. Fourteen of those incomplete current histories nevertheless have an exhausted, validated prior prefix.

{coverage}

## Predictor boundary and definitions

For a reference at height h, only confirmed transactions with height strictly less than h enter a feature. The whole reference block and all future data are excluded. This uses block heights, not timestamps or within-block transaction order. Reference-payment inputs, values, fees, recipients and UTXO-depletion outcomes remain outside the predictors, as do raw/hash identifiers, labels, collection counters and evidence metadata.

{feature_table}

One transaction can be both a receipt and a spend. Undefined historical fee rates stay missing; they are not zero, the reference-payment fee, or an allocated fee for one address. Amounts are address-associated output values, not a certified stolen total. The saved audit reproduced every available vector from 35,323 normalized address/transaction observations.

## Frozen grouping and model

Connected components combine repeated source-address hashes, shared prior-transaction references, common reference TXIDs and identical fourteen-variable vectors including missingness. These 918 observed-link components are overlap safeguards, not proven ownership groups. Unknown prior links through the 122 excluded histories are not claimed absent.

Each component uses the lexical minimum address SHA256. SHA256 of the fixed prefix `coldcard-source-split-v1:42:` followed by that minimum hash determines a residue modulo ten: 0-6 for training, 7 for validation and 8-9 for test. Every partition has at least 20 rows of each membership class, with no measured component/shared-link group crossing partitions. No seed reroll or component splitting is used.

{partitions}

One prespecified `DecisionTreeClassifier` is fitted on 1,033 training rows: Gini criterion, maximum depth 3, minimum 20 rows per leaf, balanced training class weights and random seed 42. Each of the fourteen original variables uses its observed training median; zero is a fallback only for an entirely missing training column. Fourteen fixed missingness indicators accompany the variables. Validation/test rows do not fit this preparation, select features/parameters/thresholds or enter a final all-row refit.

The exported score is a class-balanced training leaf proportion. Its field is `case_membership_score`. The membership decision includes every score >= 0.5. The three prespecified comparators are constant training membership prevalence, descending prior inactivity and descending prior balance. Undefined comparator values use the same training-only median fill. Comparators have ranking metrics only.
'''
    metric_rows = []
    for part in ('validation', 'test'):
        m = s['partition_metrics'][part]['tree']
        metric_rows.append([part.title()] + [f"{m[k]:.6f}" for k in ['average_precision_membership', 'roc_auc_membership', 'precision_membership', 'recall_membership', 'f1_membership']])
    metrics_table = table(['Partition', 'AP', 'ROC-AUC', 'Precision', 'Recall', 'F1'], metric_rows)
    confusion_table = table(['Partition', 'TP', 'FP', 'FN', 'TN'],
                            [[part.title()]+[s['partition_metrics'][part]['tree'][k] for k in ['true_positive_membership','false_positive_membership','false_negative_membership','true_negative_membership']] for part in ('train','validation','test')])
    ranking_table = table(['Fixed test method', 'Membership AP', 'Membership ROC-AUC'],
                          [[name]+[f"{s['partition_metrics']['test'][key][k]:.6f}" for k in ['average_precision_membership','roc_auc_membership']]
                           for key,name in [('constant_train_prevalence','Training-prevalence constant'),('inactivity_rank','Longer inactivity'),('balance_rank','Larger balance'),('tree','Prespecified tree')]])
    test = s['partition_metrics']['test']['tree']
    inactivity = s['partition_metrics']['test']['inactivity_rank']
    errors = [e for e in d['errors'] if e['partition'] != 'train']
    errors_table = table(['Partition / membership error', 'Source ID', 'Prior balance (sat)', 'Inactivity (blocks)'],
                         [[e['partition']+' / '+('FN' if e['known_coldcard_core_membership'] else 'FP'), f"`{e['source_id']}`",e['features']['balance_sat'],e['features']['blocks_since_last_activity']] for e in errors])
    results = f'''# Source-membership results and limitations

## Fixed development performance

In the frozen 234-address test partition, the tree recovers 97 of 98 core memberships and assigns one of 136 outside-core comparisons to the core class. Membership precision, recall and F1 are each {test['f1_membership']:.6f}. These metrics evaluate the operational membership labels, not independently verified theft or hardware identity.

{metrics_table}

{confusion_table}

Train counts are resubstitution diagnostics. Validation and test are held out from fitting, but belong to the same previously inspected incident/window; they are not an untouched or independent-incident evaluation. All AP and ROC-AUC values were independently checked from tied score groups and pairwise ranking counts. Confusion counts and F1 also reproduce directly from the saved predictions.

{ranking_table}

Inactivity alone already achieves test AP {inactivity['average_precision_membership']:.6f}. The tree's descriptive gain is {100*(test['average_precision_membership']-inactivity['average_precision_membership']):.2f} percentage points on this fixed partition. No independent significance or causal claim follows, and no additional parameter search or model was fitted after inspecting these results.

## Rules and errors

The fitted tree has five leaves and uses only prior balance and inactivity. At the fixed decision threshold, the positive-membership region requires float32-converted balance greater than 14,820,511.5 satoshis and inactivity greater than 1,006.5 blocks. A further split at 8,750 blocks distinguishes two positive leaf scores. This is the fitted cohort rule, not a proposed operational theft/device threshold. A redundant split between two zero-score comparison leaves is retained without post-hoc pruning. Exact replay conditions and per-partition node/leaf supports remain in the saved model and rules.

No explicit missingness indicator was selected, and no observed source reached a numeric split using an imputed value for that split variable. The full training-only preparation remains exported. This observation does not characterize the unknown vectors of excluded histories.

{errors_table}

The missed case source `cohort_0191` has 105 earlier receipt transactions and last activity only 409 blocks before reference. It falls outside the learned inactivity region despite its case membership. The test comparison `comparison_0401` has one earlier receipt, a balance of 40,096,077 satoshis and 7,000 blocks of inactivity, resembling the covered case profile. The validation error is also an old-funded comparison. These are membership errors; neither predictions nor corrections settle compromise or device status.

## Coverage and inference limits

Coverage is 100% for cases and 87.8% for selected comparisons, ranging from 81.36% to 91.51% across comparison strata. The sampled core prevalence increases from 33.33% of selections to 36.28% of available vectors. The 122 unavailable comparisons have median saved full-current-history transaction count 3,347, versus 3 for available comparisons. These counts were observed at different collection snapshots and are diagnostic metadata, never prior-block predictors or estimates of missing features. Missingness cannot be assumed random.

All 500 positives come from one retrospectively reconstructed incident. Core membership and case evidence were learned after the event; their publication/availability dates are not established for prospective use. Addresses are not independent victims or devices. Same-chain reconstruction agreement, an owner report, provider coverage and genuine device/compromise verification are distinct evidence tiers. Independently verified compromise/device labels remain unknown for every selection, and comparisons are not verified benign examples.

The result supports a reproducible, interpretable description of covered source profiles and a narrow within-window membership baseline. It does not establish a cause of loss, a signing-device fingerprint, calibrated theft probabilities, independent-incident transfer or general blockchain detection performance. The selection prevalence is study-defined. The 122 bounded-incomplete prefixes remain unresolved; a validated prefix also does not certify a complete current history. The frozen external nineteen-feature forest and all earlier experiment artifacts remain unchanged.

## Reproducibility and supported conclusion

The fitted experiment is pinned to [commit {MODEL_COMMIT[:7]}](https://github.com/HnsHugo/STAGE-UFU/commit/{MODEL_COMMIT}) on branch `task-2-wallet-analysis`. Its protocol freezes the data, component assignments, preparation, tree parameters, threshold and software versions. All 1,378 JSON-exported scores exactly match the fitted estimator. Thirty focused tests and verification without a model refit passed in the saved execution. The report builder checks the saved predictions, confusion counts, F1, fingerprints, exclusions and component partitioning; it performs no new training or collection.

A separate independent evaluation would require a justified additional incident/source universe, evidence-backed label definitions and a new prespecified protocol. The current validation/test outcomes must not be reused for tuning or described as newly independent evidence.
'''
    return methods, results


PREAMBLE = r'''% Add once in the original article preamble, before \begin{document}.
\usepackage{booktabs,longtable,array,calc}
\usepackage{amsmath}
\providecommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}
'''

WRAPPER = r'''\documentclass[11pt,a4paper]{article}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage[margin=24mm]{geometry}
\usepackage{graphicx}
\usepackage[hidelinks]{hyperref}
\input{article_preamble}
\setlength{\emergencystretch}{2em}
\title{Coldcard Source Addresses\\Dataset, Frozen Membership Baseline and Limits}
\author{Research working report}
\date{2 November 2026}
\begin{document}
\maketitle
\begin{abstract}
This report documents a retrospective source-address study of one Coldcard-related incident. It distinguishes membership in a reconstructed case from verified compromise or hardware identity, retains incomplete coverage explicitly, and presents one prespecified shallow tree with unchanged grouped development partitions. The result is reproducible cohort separation, not independent-incident validation.
\end{abstract}
\section{Our Work}
\input{source_methods}
\section{Results}
\input{source_results}
\end{document}
'''


def build():
    data, pins = validated_inputs()
    methods, results = narrative(data)
    intro = '''# Coldcard source-address study

English research write-up of the fixed dataset and membership baseline. The two LaTeX fragments follow the supplied article's `Our Work` and `Results` sections. This is new text for integration; the live Overleaf project and the originally supplied files were not modified.

[PDF review copy](source_address_study.pdf) · [Method fragment](source_methods.tex) · [Result fragment](source_results.tex) · [Saved experiment](../research/coldcard/source_membership_baseline_20261102_162335/README.md) · [Evidence alignment](../ALIGNMENT.md)

## Article integration

Add `article_preamble.tex` once before `\\begin{document}`. Place `\\input{source_methods}` in `Our Work`, alongside the initial dataset description, and `\\input{source_results}` in `Results`. The source-address sections supplement the financial/transaction work; their membership scores must not replace or be combined with transaction-target metrics. Reconcile the existing introduction's proposed GNN with this completed tabular baseline rather than asserting that GNN training occurred. The standalone `report.tex` is a review wrapper, not a replacement for the article or its author list/bibliography.

The fragments require only the listed standard LaTeX packages in addition to the original `graphicx` and `hyperref`. Exact observations are generated from the pinned saved JSON. Public reconstruction attribution and artifact links follow the text; no private raw cache or imported bulk address list is published.

'''
    links = '''
## Sources and saved evidence

- [Case-source consolidation and evidence tiers](../research/coldcard/source_dataset_20261030/README.md).
- [Two published reconstruction comparisons and pinned sources](../research/coldcard/source_corroboration_20261030/README.md).
- [One owner-report adjudication](../research/coldcard/owner_report_adjudication_20261030/README.md).
- [Fixed same-block comparison selection](../research/coldcard/source_comparison_selection_20261030/README.md).
- [Coverage/grouping audit](../research/coldcard/source_comparison_feasibility_20261102_1603/README.md).
- [Frozen fitted experiment and scores](../research/coldcard/source_membership_baseline_20261102_162335/README.md).
- [Public normalized predictor view](../research/coldcard/reference_tail_continuation_20261102_1508/precutoff_feature_view.json.gz).
- [Report input/output provenance](provenance.json).

SomaxBT's pinned `coldcard-drain-addresses` reconstruction and Alvaro P.'s pinned `coldcard-weak-rng-research` reconstruction corroborate chain observations, not independent owner/device ground truth. Exact URLs, versions, licensing caveats and the limited input-value comparison are retained in the linked corroboration review. No external CSV is copied into this report.

## Check and compile

From the repository root:

```sh
python "Task 2/docs/build_source_address_study.py" check
cd "Task 2/source_address_study"
mkdir -p /tmp/ufu-report-build
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=/tmp/ufu-report-build report.tex
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=/tmp/ufu-report-build report.tex
```

Relative fragment inputs resolve from this working directory. The two passes settle long-table widths and references. The checked PDF is already included. Report checks read frozen results and never fit a model or query a provider.
'''
    def subordinate(text):
        return '\n'.join('#'+line if line.startswith('#') else line for line in text.splitlines())+'\n'
    files = {'README.md': (intro+subordinate(methods)+'\n'+subordinate(results)+links).encode(),
             'article_preamble.tex': PREAMBLE.encode(), 'report.tex': WRAPPER.encode()}
    for name, markdown in [('source_methods.tex', methods), ('source_results.tex', results)]:
        rendered = subprocess.run(['pandoc','--from=markdown','--to=latex','--shift-heading-level-by=1','--wrap=auto'],
                                  input=markdown.encode(), capture_output=True, check=True).stdout
        # Keep unchanged identifiers readable inside the original narrow article
        # layout: permit line breaks after underscores without adding characters.
        def break_identifier(match):
            value = match[1]
            if re.fullmatch(rb'[0-9a-f]{40,64}', value):
                value = b'\\allowbreak{}'.join(value[i:i+8] for i in range(0,len(value),8))
            else:
                value = value.replace(b'\\_', b'\\_\\allowbreak{}').replace(b'-', b'-\\allowbreak{}')
            return b'\\texttt{'+value+b'}'
        rendered = re.sub(rb'\\texttt\{([^{}]*)\}', break_identifier, rendered)
        rendered = b'\\begingroup\n\\setlength{\\emergencystretch}{2em}\n'+rendered+b'\n\\endgroup\n'
        files[name] = rendered
    facts = dict(model_commit=MODEL_COMMIT, selected_sources=1500, available_vectors=1378,
                 excluded_comparisons=122, components=918, features=[name for name,_ in FEATURES],
                 partition_counts=data['metrics']['partition_counts'],
                 partition_metrics=data['metrics']['partition_metrics'],
                 independently_verified_compromise_labels=0, independently_verified_device_labels=0,
                 owner_reports=1, full_history_comparison_statuses=data['metrics']['full_history_comparison_statuses'])
    files['tables.json'] = json_bytes(facts)
    provenance = dict(schema_version=1, report_date='2026-11-02', frozen_model_commit=MODEL_COMMIT,
                      inputs=pins, builder_sha256=sha(Path(__file__).read_bytes()),
                      generated_text_sha256={name:sha(value) for name,value in files.items()},
                      generated_by='Saved-result report builder; no model imports, fit or provider HTTP.',
                      training_performed=False, collection_performed=False, unknown_labels_promoted=False,
                      article_layout_review='Supplied main (1).tex and annotation.tex read on 2026-11-02; inputs placed under Our Work / Results; originals not republished or edited.')
    files['provenance.json'] = json_bytes(provenance)
    return files


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['build', 'check'])
    args = parser.parse_args()
    files = build()
    if args.mode == 'build':
        OUTPUT.mkdir(exist_ok=True)
        for name,data in files.items():
            (OUTPUT/name).write_bytes(data)
    else:
        for name,data in files.items():
            require((OUTPUT/name).read_bytes() == data, 'Report differs from frozen inputs: '+name)
    print(json.dumps(dict(mode=args.mode, generated_text_files=len(files), verified_eligible_sources=1378,
                          frozen_model_commit=MODEL_COMMIT, model_fits=0, provider_requests=0)))


if __name__ == '__main__':
    main()
