# Random-forest comparison on validation

## Protocol

This experiment compares three predefined random forests on the exact original training/validation address split. It does not evaluate or tune on test addresses. Input SHA-256 checksums and repeated-profile checks are reused from the benchmark.

Each forest uses 100 trees, bootstrap samples, max_features=sqrt, min_samples_leaf=20 and random_state=42. The predefined configurations are depth 12 without class weights, depth 12 with illicit weight 3, and depth 20 with illicit weight 3. Two CPU jobs are used. Each configuration is compared over the same 19 predefined thresholds as the previous tree experiment; prediction requires score strictly above the threshold.

The selection criterion is maximum validation F1 across the predefined models and thresholds. The winning validation score is a development result, not independent confirmation.

## Results on the same validation addresses

| Model | Threshold | Precision | Recall | F1 | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Adjusted single tree, previous reference | 0.75 | 80.88% | 59.62% | 68.64% | 1701 | 402 | 1152 |
| depth12_unweighted | 0.30 | 82.20% | 69.93% | 75.57% | 1995 | 432 | 858 |
| depth12_illicit_weight3 | 0.55 | 87.26% | 66.53% | 75.50% | 1898 | 277 | 955 |
| depth20_illicit_weight3 | 0.55 | 86.69% | 69.86% | 77.37% | 1993 | 306 | 860 |

Selected development configuration: depth 20, illicit class weight 3, threshold 0.55. Its validation precision is 86.69%, recall 69.86% and F1 77.37%. Compared with the adjusted tree on the same validation set, it recovers 292 additional illicit-labeled addresses and raises 96 fewer false alerts. This supports an ensemble as a promising development direction; it does not prove improved performance on independent cases.

Average precision for the selected forest is 85.82% on validation. It describes score ranking over the precision-recall curve and is not the precision at threshold 0.55. Forest scores are not calibrated probabilities.

## How the forest differs from one tree

Trees are fitted on different bootstrap samples and examine random subsets of features at splits. RandomForestClassifier averages their class probability estimates; a threshold then turns that average score into a label. It does not simply require a majority of hard binary votes. Individual trees may partition mixed profiles differently, but this experiment does not establish a causal explanation of any specific error correction.

## Reproduction and artifacts

```bash
python train_forest_validation.py /path/to/ellipticplusplus /path/to/new_forest_output
python -m unittest discover -p 'test_*.py' -v
```

The output directory must be new. status.json records incomplete until all configurations finish, then complete with the metrics file's checksum. forest_validation_20261013/forest_validation_metrics.json retains all thresholds, confusion counts, feature importances, settings, runtimes and the selected configuration. Seven existing benchmark tests pass; the actual experiment's confusion counts, derived precision/recall and output checksum were independently checked.

No serialized fitted forest or deployed model is exported. Re-running the pinned script reproduces fitting and the validation comparison. Feature importances are impurity-based, not SHAP or causal evidence.

## Limits and next step

The same validation set has now supported several development decisions, so the winning score can overestimate independent performance. The original test remains a historical reference and was not evaluated again here. Further confirmation requires an independent evaluation protocol/dataset.

Original labels concern offline illicit/licit historical address profiles. Full-history aggregate features and address-level separation do not establish real-time, entity-independent or case-independent detection. This forest is not validated on stolen-fund cases or hardware-wallet labels.

Next work: retain this configuration as a development candidate, analyse its remaining errors, and prioritize decision-time features and independent sourced cases before claiming a validated detector.

Reference: https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html
