# Pooled Coldcard and CryptoBilis evaluation

Each of five shallow trees trains on both incidents and predicts one held-out
fold. Every complete address vector receives one out-of-fold prediction. The
Coldcard and CryptoBilis rows below summarize subsets of those same predictions.
The target is documented source-cohort membership for the reference incident.

## Out-of-fold results

| Test cohort | Vectors | Precision | Recall | F1 | Average precision | ROC AUC | TP | FP | FN | TN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Pooled | 1,800 | 0.9106 | 0.9662 | 0.9376 | 0.9544 | 0.9859 | 601 | 59 | 21 | 1,119 |
| Coldcard | 1,471 | 0.9036 | 0.9940 | 0.9467 | 0.9594 | 0.9896 | 497 | 53 | 3 | 918 |
| CryptoBilis | 329 | 0.9455 | 0.8525 | 0.8966 | 0.9401 | 0.9738 | 104 | 6 | 18 | 201 |

Global F1 ranges from 0.8971 to 0.9762 across folds. The pooled average precision
of prior inactivity alone is 0.9284. The pooled average precision of prior
balance alone is 0.7821.

The [separate within-incident evaluation](../within_incident_20261119/RESULTS.md)
had F1 of 0.9832 on Coldcard and 0.9195 on CryptoBilis. On the same 1,800 vectors,
the pooled evaluation flags 39 more Coldcard comparisons and misses 16 more
CryptoBilis source-cohort members. The training populations and fold
assignments differ, so these changes are descriptive. This retrospective
evaluation measures cohort membership on held-out groups from the two known
incidents. Evidence of compromise and signing device remains unverified.

## Protocol and verification

The 1,800 vectors comprise 622 source-cohort members and 1,178 comparisons.
The 29 incomplete Coldcard prefixes and 37 incomplete CryptoBilis prefixes are
outside the experiment. The [pre-fit protocol](protocol.json) pins the fourteen
predictors built from confirmed transactions strictly before each reference
block. The balanced decision tree uses depth at most three, at least 20 training
vectors per leaf and a decision threshold of 0.50. Each fit uses training-fold
medians and missing-value indicators. Incident and component identifiers guide
the fold assignment and are excluded from the predictors.

The [fold manifest](folds.json.gz) and [pre-fit audit](preflight.json) keep all
1,170 linked components intact, including components that span both incidents.
The largest contains 394 vectors. Four folds hold out 317 vectors each. The
remaining fold holds out 532. Every training and test partition contains both
classes from both incidents.

The verifier checked all five fitted trees against training-fold support and
weights, replayed 1,800 predictions and independently recomputed the metrics.
It found zero component overlap between training and evaluation.

- [Global and per-fold metrics CSV](metrics.csv) · [Full metrics JSON](summary.json)
- [Fitted trees](models.json.gz) · [Held-out predictions](predictions.json.gz)

```sh
python3 "Task 2/research/external_cases/pooled_incidents_20261119/evaluate_pool.py" verify
```
