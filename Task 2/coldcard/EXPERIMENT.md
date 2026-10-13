# First decision-tree experiment

## What is actually being tested

The target is “direct parent candidate of a consolidation attributed to the case” versus “unattributed transaction.” This is not ground truth for theft or hardware-wallet control. The five consolidations and 98 coinbase transactions are excluded: 493,468 transactions, including 1,070 candidates.

The tree uses 16 numerical transaction properties. TXID, height, provenance and the coinbase indicator are excluded. Settings are fixed before training: depth 4, at least 20 observations per leaf, balanced class weights, random_state 42. No setting was selected from test results. The comparison rule, however, had already been observed on the full dataset; it remains a descriptive reference.

## Results computed on 8 October 2026

| Split | Model | Candidates recovered | Alerts in unattributed background | Proxy precision | Proxy recall |
|---|---|---:|---:|---:|---:|
| Random, reference with leakage risk | Full tree | 266 / 267 | 53 | 83.39% | 99.63% |
| Random, reference with leakage risk | Tree without fees | 267 / 267 | 6048 | 4.23% | 100% |
| Chronological | Full tree | 0 / 34 | 139 | 0% | 0% |
| Chronological | Tree without fees | 34 / 34 | 15820 | 0.21% | 100% |
| Chronological | One output and fee rate >=4.95 sat/vB | 34 / 34 | 5953 | 0.57% | 100% |

These background alerts are neither newly detected thefts nor legally established false positives. Metrics refer only to the proxy target.

Stratified random split: 370101 training observations (803 candidates), 123367 test observations (267 candidates). This split may place members of the same collector in both sets; its result must not be presented as independent validation.

Chronological split: training at heights <960377 (163328 observations, 1036 candidates), test at heights >=960377 (330140 observations, 34 candidates). Blocks do not overlap between sets. Entity or collector independence is not established; this test covers only a small late candidate group and a single incident.

## Why the random-split score is misleading

The 1036 earlier candidates, across five blocks, have a median fee rate of 30 sat/vB. The 34 candidates in block 960733 have a median of 4.9590 sat/vB. The full chronological tree mainly splits on fees around 30, so it misses all later candidates. This shows dependence on a fee signature specific to the earlier group, without demonstrating a general theft rule.

Without fees, transaction shape and amounts recover the small late group, but alerts rise to 15820 out of 330106 background observations (4.79%). Generalization is not established.

## Reproduction

From Task 2/coldcard, with features already extracted:

```bash
python -m pip install -r requirements.txt
python train_exploratory.py features_output/transactions.csv.gz experiment_output
python -m unittest discover -p test_experiment.py -v
```

Versions are recorded in metrics.json. The script verifies the received file's exact SHA256. The output directory must be new. Text exports describe the models for each split; their weights are not calibrated theft probabilities. No production model is supplied.

## Next step

```bash
python extract_candidate_groups.py blocks parents.json candidate_groups.json
```

This script groups candidates by descendant consolidation, merges groups sharing collection addresses and groups sharing a parent, and checks coverage against parents.json. Addresses are used only for grouping and are not published in the output. Extraction must run in Codespaces, where the complete blocks are available.

Groups remain incomplete with respect to missing blocks and background relationships. Grouped validation, followed by documented external cases and sourced controls, is necessary before claiming theft detection.

## Methodological sources

- https://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeClassifier.html
- https://scikit-learn.org/stable/modules/cross_validation.html
- https://scikit-learn.org/stable/common_pitfalls.html
- Initial attribution: https://bitquery.io/investigations/coldcard-wallet-hack
