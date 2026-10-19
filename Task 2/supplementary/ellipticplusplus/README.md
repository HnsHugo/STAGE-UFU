# Elliptic++ offline address-classification benchmark

## Purpose

This experiment predicts the original Elliptic++ illicit/licit label from an address's historical profile. It is an educational baseline for the internship's address-analysis pipeline. It does not identify stolen funds, hardware wallets, victims, or the cause of an individual transaction.

Sources: https://github.com/git-disl/EllipticPlusPlus and https://arxiv.org/abs/2306.06108
Pinned source revision: `08fe6aded83afb97bf5a79a71130f542ca783c2e`.
The input SHA-256 checksums are recorded in the script and audit. Both full CSV files were downloaded and verified on 13 October 2026.

## Data audit and unit of observation

The feature file contains 1,268,260 rows and 57 columns, including address and Time step. It covers 822,942 unique addresses and time steps 1–49. There are 347,569 exact duplicate rows, also counted as duplicate address/time-step rows. No cells are missing, and numeric features are finite.

For each address, all 55 non-temporal numeric features are identical across its observations. The script verifies this before collapsing repeated observations to a single address profile. It rejects conflicting profiles rather than silently choosing or averaging them. Feature and label address sets agree exactly; labels have no duplicate address.

Original class 1 becomes target 1 (illicit), and original class 2 becomes target 0 (licit). The 557,588 unknown-class addresses are excluded rather than treated as licit. The supervised dataset contains 265,354 address profiles: 14,266 illicit and 251,088 licit.

Address, Time step and four absolute block fields (first/last appearance and first sent/received block) are excluded from predictors. The full variant has 51 features; the fee-free variant has 41. Lifetime and other aggregate features are retained only under the explicit offline-profile interpretation.

## Training, validation and test

Unique addresses are sorted before two deterministic class-stratified splits, using random states 42 and 43. No address appears in more than one set.

| Set | Addresses | Illicit | Licit |
| --- | ---: | ---: | ---: |
| Training | 159,212 | 8,560 | 150,652 |
| Validation | 53,071 | 2,853 | 50,218 |
| Test | 53,071 | 2,853 | 50,218 |

Four candidate trees are specified before training: depth 4/8, each with all profile features or without fee features. All use min_samples_leaf=20, balanced class weights and random_state=42. The winning configuration is selected by validation F1, with candidate order breaking ties. The selected tree remains fitted to training only; validation is not added back before the test. No threshold is tuned and no configuration is selected using test results.

## Validation results

| Candidate | Precision | Recall | F1 | Average precision |
| --- | ---: | ---: | ---: | ---: |
| Full profile, depth 4 | 22.89% | 80.13% | 35.61% | 26.63% |
| Full profile, depth 8 | 30.28% | 88.22% | 45.09% | 59.21% |
| Without fees, depth 4 | 23.60% | 74.69% | 35.87% | 26.32% |
| Without fees, depth 8 | 25.51% | 79.04% | 38.58% | 50.23% |

## Final held-out test

Selected model: full profile, depth 8.

| Measure | Value |
| --- | ---: |
| Precision | 30.74% |
| Recall | 88.50% |
| F1 | 45.63% |
| Average precision | 62.02% |
| Illicit addresses recovered (TP) | 2,525 |
| Illicit addresses missed (FN) | 328 |
| Licit addresses alerted (FP) | 5,690 |
| Licit addresses not alerted (TN) | 44,528 |

An always-licit baseline has zero precision/recall/F1 and average precision equal to the test's illicit prevalence (about 5.38%). Overall accuracy is deliberately not the headline metric because labels are highly imbalanced.

The model recovers many illicit-labeled examples but raises many additional alerts. These labels describe the benchmark, not a legal determination. Weighted scores are not calibrated probabilities. Feature importance is dominated by total_txs (about 35.74%), followed by transacted_w_address_total (10.73%), fees_max (8.97%), btc_sent_mean (8.10%) and blocks_btwn_txs_mean (7.26%). These are impurity-based model importances, not causal explanations or SHAP values.

## Artifacts and reproduction

Use Python 3.12. From this directory:

```bash
python -m pip install -r requirements.txt
python ../../research/coldcard/download_ellipticplusplus.py /tmp/ellipticplusplus
python train_benchmark.py /tmp/ellipticplusplus /tmp/ellipticplusplus_new_run
python -m unittest discover -p test_benchmark.py -v
```

The output directory must be new. status.json starts incomplete and becomes complete only after all experiment artifacts have been written. Five tests cover profile collapse, conflicting profiles, coverage/label rejection, split separation/reproducibility and metric errors.

The committed results_20261013 directory contains audit.json, metrics.json, four readable trees, a non-executable selected_tree.json and the original run's artifact manifest status.json. The JSON tree records features, split thresholds, child indices and weighted class proportions; scikit-learn converts inputs to float32. It is the evaluated training-only tree, not a separately refitted production model.

Large raw inputs, split_assignments.csv.gz and test_predictions.csv.gz are not committed. The run generates the latter two files locally for inspection. status.json lists their hashes even though they are omitted from Git; it describes the original complete run, not a self-contained downloadable dataset. Logical splits are reproducible with the pinned inputs and dependency versions; gzip byte hashes may differ across reruns because compression timestamps are not fixed.

## Limits and next work

Address separation does not prove entity or case independence. Related addresses may occur across sets. Aggregates span complete address histories and may include events after the Time step value: this experiment is not a causal temporal test or real-time detection system. A chronological split over these unmodified aggregates would not resolve that issue.

The FBI/Binance theft references use different roles and feature definitions. No external theft score is reported, and this tree must not be applied directly to the existing transaction proxy CSV. Next work is to reconstruct features available at a specified decision date, expand sourced theft cases and controls, and test case-level generalization. Further parameter or threshold development must use training/validation; this test has now been inspected and must not be repeatedly used for tuning.

## Validation-only development follow-up

See [VALIDATION_TUNING.md](VALIDATION_TUNING.md) for weight/threshold comparisons on validation. No new held-out test score is reported; the original test results above remain unchanged.
