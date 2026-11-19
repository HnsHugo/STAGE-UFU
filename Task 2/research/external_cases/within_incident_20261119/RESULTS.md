# Coldcard and CryptoBilis within-incident evaluation

The pre-fit [protocol](protocol.json) uses the same frozen fourteen pre-reference variables, decision-tree parameters and 0.5 threshold as the [cross-incident experiments](../bidirectional_transfer_20261119/RESULTS.md). The unit is a source address with a fixed reference payment. The target is documented source-cohort membership for the incident being tested.

## Pooled out-of-fold scores

| Train → test | Tested | Precision | Recall | F1 | Average precision | ROC AUC | TP | FP | FN | TN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Coldcard → Coldcard | 1,471 | 0.9726 | 0.9940 | 0.9832 | 0.9833 | 0.9946 | 497 | 14 | 3 | 957 |
| CryptoBilis → CryptoBilis | 329 | 0.8633 | 0.9836 | 0.9195 | 0.9295 | 0.9734 | 120 | 19 | 2 | 188 |

Prior-inactivity average precision on the same predictions is 0.9553 for Coldcard and 0.8540 for CryptoBilis. Prior-balance average precision is 0.7919 and 0.7485. Tree F1 across individual folds ranges from 0.9709 to 1.0000 for Coldcard and from 0.8727 to 0.9796 for CryptoBilis.

Each address with a complete pre-cutoff vector is evaluated exactly once. Each of the five fits per incident sees only the other four groups of folds from that incident. Imputation is fitted on those training rows. Previously audited connected components stay intact, including those with indirect cross-incident links. Coldcard has 913 components among complete rows and one component of 365 rows. This leaves 251–465 evaluation rows per fold and 1,006–1,220 training rows. CryptoBilis has 261 components, 65–66 evaluation rows and 263–264 training rows per fold. The 29 incomplete Coldcard prefixes and 37 incomplete CryptoBilis prefixes are outside fitting and evaluation.

## Comparison on the same test addresses

This descriptive comparison restricts the saved internal predictions to the exact evaluation addresses of each cross-incident test, joined by incident and source ID with matching labels. Training populations still differ across setups.

| Test incident | Matched test n | Internal F1 | Cross-incident F1 | Internal FP / FN | Cross-incident FP / FN |
| --- | ---: | ---: | ---: | ---: | ---: |
| Coldcard | 1,081 | 0.9851 | 0.9198 | 13 / 2 | 87 / 0 |
| CryptoBilis | 271 | 0.9195 | 0.5665 | 19 / 2 | 2 / 73 |

The largest gap is on CryptoBilis. Its own training folds recover 120 of 122 known sources on the matched rows, while the Coldcard-trained tree recovers 49. Both sets of experiments are retrospective cohort evaluations. Compromise and signing-device labels remain unverified.

## Reproduction

The [fold manifest](folds.json.gz) and [pre-fit audit](preflight.json) were pinned before fitting. The verifier replays the saved trees and training-only medians and independently recomputes the metrics. It checked 1,800 held-out predictions and 10 training partitions with zero connected-component overlap between training and evaluation. Existing inputs and cross-incident results are preserved. This unit uses no blockchain API requests.

- [Pooled and fold metrics CSV](metrics.csv) · [Full metrics JSON](summary.json)
- [Saved models](models.json.gz) · [Per-address predictions](predictions.json.gz)

```sh
python3 "Task 2/research/external_cases/within_incident_20261119/evaluate_within.py" verify
```
