# Task 2 — Coldcard case study and first ML experiment

This directory contains a reproducible pipeline for analysing the blocks provided by the professor. The initial objective is an interpretable decision-tree experiment; general theft detection and hardware identification have not yet been demonstrated.


## Additions verified on October 15, 2026

- [Course exercise: 100 payments + 100 comparisons](COURSE_EXERCISE.md), with ten features, a readable tree and a search for destinations to examine.
- [Analysis of flows and the five consolidations](case_flows_20261015/CASE_FLOWS.md), with amounts, observed addresses, time spans and dated output status.
- [Offline demonstration](../../REPRODUCIBILITY.md) and [requirements audit](../../REQUIREMENTS.md).

The grouped metrics below were reproduced exactly from the verified CSV. The new teaching exercise is separate: its perfect score on a small test linked to the same address does not replace grouped validation.

## Current status

- 98 selected JSON blocks, 493571 unique transactions; 98 coinbase transactions.
- 5 transactions present in the data are attributed to the case by an external investigation.
- 1070 direct parents found out of 2349 searched for; the others remain outside coverage.
- 4 observed parent groups: 491, 341, 204 and 34.
- Features extracted and checked; random, chronological and grouped experiments completed.
- Automated tests cover splits, metrics, group merging, flow handling and provenance; see the repository-wide verification guide for the current run.

The terms “candidate” and “source-attributed” describe provenance. They do not replace independent verification of theft or hardware-wallet control. Unattributed transactions remain unknown.

## Reading the results

- PARENT_AUDIT.md: coverage of funding relationships.
- FEATURE_ANALYSIS.md: integrity checks and descriptive differences.
- EXPERIMENT.md: the high random-split score and failure on later candidates.
- GROUPED_EXPERIMENT.md: evaluation with each candidate group held out of training.
- TRANSITION.md: closure of the previous pilot and the new priority.
- LABEL_PROTOCOL.md: rules for constructing labels for the next dataset.

## Installation

Use Python 3.12 and install the dependencies from this directory:

```bash
python -m pip install -r requirements.txt
```

Keep raw blocks outside Git, in blocks/; retain a copy of the original archive. The extractor accepts the 98 extensionless files named by their hashes. The audit also accepts the original archive.

## Complete pipeline

Run the following commands from Task 2/research/coldcard. Choose new output names if an extraction or experiment has already been run: the scripts reject existing output directories.

```bash
python audit_coldcard_parents.py blocks > parents.json
python extract_features.py blocks parents.json features_output
python extract_candidate_groups.py blocks parents.json candidate_groups.json
python audit_dataset.py features_output/transactions.csv.gz features_output/manifest.json candidate_groups.json
python train_exploratory.py features_output/transactions.csv.gz experiment_output
python train_grouped.py features_output/transactions.csv.gz candidate_groups.json features_output/manifest.json grouped_output
python -m unittest discover -p 'test_*.py' -v
```

Check for status complete in features_output/manifest.json before training. The training scripts reproduce this exact pilot version and verify the compressed CSV's SHA256; a new dataset requires a new documented version of the protocol and its checksum.

Trees are exported as text for inspection, and metrics as JSON. No production model or calibrated theft probability is published.

## Main finding

The full tree recovers 874/1070 candidates across grouped validation and produces 1072 background alerts. It fails completely on one group and recovers only 43/204 in another. Its mean recall across groups is 55.20%. This supports improving case diversity and labels before introducing a more complex model.

## Exported research model

A final tree, fitted to all eligible observations after the experiments, is available in grouped_results_20261008/research_proxy_model.json. This JSON file contains no executable code or pickle. Its scores are weighted leaf proportions, not calibrated theft probabilities. It has no separate validation score: the fold-specific tree metrics do not evaluate this final artifact.

To apply it to another CSV with the same features and TXIDs:

```bash
python proxy_model.py score grouped_results_20261008/research_proxy_model.json other_features.csv.gz research_scores.csv.gz
```

The output uses research_candidate_score and research_candidate_like, with the interpretation similar_to_training_candidates_not_confirmed_theft. Do not use this output as a list of criminals or as evidence of hardware control. Out-of-distribution data require external validation.

## ML comparison on October 16, 2026

The [univariate grouped baselines](GROUPED_BASELINES_20261016.md) quantify the recall/alert trade-off against the historical tree, without retraining it. The three new baselines and their rules for each fold are saved separately.
