# Univariate baselines on the Coldcard groups — October 16, 2026

## Hypothesis and protocol

The historical tree relies heavily on fees. This experiment measures what three interpretable baselines with a single split contribute: fee rate, output count and total output amount. The three variables and hyperparameters were fixed before this run. All baselines are published; none is selected based on the results.

The 493,468 eligible transactions and four candidate groups are identical to the historical experiment: 1,070 candidates and 492,398 unattributed transactions. Each candidate group is entirely excluded from training in its fold; the background is partitioned using the same TXID hash. Each row is predicted exactly once outside training. The report retains hashes of the corpus, group file, historical metrics and fold assignments.

Each model is a depth-1 tree with a minimum of 20 observations per leaf, balanced class weights learned from training, and seed 42. The split is fitted only on the other three groups and their training background. The predicted class is sklearn's, with no threshold adjustment after inspection. No validation set is used to select parameters: this fully predefined comparison makes no selection. Because the groups had already been inspected, this is a development diagnostic, not a new held-out test.

## Results actually executed

| Method | Candidates recovered | Alerts on unknown background | Proxy precision | Proxy recall | Proxy F1 | Mean recall across groups |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Fee rate only | 1036/1070 | 7878 | 11.62% | 96.82% | 20.75% | 75.00% |
| Output count only | 1070/1070 | 54510 | 1.93% | 100.00% | 3.78% | 100.00% |
| Output amount only | 892/1070 | 64571 | 1.36% | 83.36% | 2.68% | 67.77% |
| Full historical tree, without retraining | 874/1070 | 1072 | 44.91% | 81.68% | 57.96% | 55.20% |

## Breakdown by held-out group

| Group prefix | Candidates | Fees only: recovered / alerts | Outputs only: recovered / alerts | Amounts only: recovered / alerts |
| --- | ---: | ---: | ---: | ---: |
| 0c6bf853a645 | 341 | 341 / 410 | 341 / 13677 | 341 / 19928 |
| 14edd9ee8445 | 491 | 491 / 6539 | 491 / 13604 | 491 / 20171 |
| 38b6dc366fca | 34 | 0 / 425 | 34 / 13531 | 17 / 16044 |
| 4b50d61a3d6e | 204 | 204 / 504 | 204 / 13698 | 43 / 8428 |

## Interpretation and limitations

The historical model reduces alerts compared with each baseline, but its overall recall and mean recall across groups are lower than those of fees alone. The output-count baseline recovers every candidate at the cost of 54,510 alerts: recall alone is therefore insufficient to judge quality. An improvement in F1 can conceal groups with poorer coverage.

Fee rate alone misses the group of 34 candidates. The exact rules for each fold are saved in the JSON. This documents a dependence on fee regimes; it identifies neither a device, an owner nor a theft. Alerts on the unknown background are not confirmed false positives. The metrics still describe a candidate relationship to a single case.

The candidate groups are not independent external incidents. Relationships between background entities and missing transactions remain unknown. No chronological split is imposed: these retrospective data do not establish real-time detection. No confidence interval treating each transaction as independent is added. The historical models and results, and the frozen external forest, are preserved.

## Reproduce and test

From the repository root, with the Coldcard dependencies and a new output file:

```bash
python "Task 2/research/coldcard/compare_grouped_baselines.py" \
  /path/to/transactions.csv.gz /path/to/candidate_groups.json /path/to/manifest.json \
  "Task 2/research/coldcard/grouped_results_20261008/metrics.json" \
  /path/to/new_results.json
python -m unittest discover -s "Task 2/research/coldcard" -p 'test*.py'
```

The result of this run is `grouped_baselines_20261016.json`. All 45 Coldcard tests pass, including four new tests covering thresholds learned outside the test set, constant variables, non-finite values and metrics under severe class imbalance.

## Next ML work unit

Analyze Real-CATS validation errors by category and missing-value pattern, without modifying the external model or tuning parameters on the already inspected held-out test set. If a model must be refitted to obtain validation predictions, reproduce only the frozen parameters and split; retain this diagnostic as a new experiment.
