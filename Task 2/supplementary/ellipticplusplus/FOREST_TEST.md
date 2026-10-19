# Locked random-forest evaluation on held-out addresses

## Configuration locked before evaluation

The selected development forest is evaluated without changing its configuration: 100 trees, max_depth=20, min_samples_leaf=20, max_features=sqrt, bootstrap=True, illicit class weight 3 versus licit weight 1, random_state=42. Prediction requires score strictly greater than 0.55.

Inputs and profiles use the original checksum-verified benchmark. Only the original 159,212 training addresses are used to fit the forest; validation is not added to fitting. Evaluation uses the original 53,071 test addresses (2,853 illicit, 50,218 licit), disjoint from training and validation. No threshold sweep or model selection is performed on test.

## Results

| Measure | Development validation | Held-out test |
| --- | ---: | ---: |
| Precision | 86.69% | 88.77% |
| Recall | 69.86% | 70.63% |
| F1 | 77.37% | 78.66% |
| Average precision | 85.82% | 86.90% |
| True positives | 1993 | 2015 |
| False positives | 306 | 255 |
| False negatives | 860 | 838 |
| True negatives | 49912 | 49963 |

Test confusion matrix (positive = original illicit label):

| Dataset label | Predicted licit | Predicted illicit |
| --- | ---: | ---: |
| Licit | 49963 | 255 |
| Illicit | 838 | 2015 |

The comparable validation and test scores support performance on held-out address profiles from this dataset. They do not establish performance on independent cases, new periods or another data source. The original full-profile baseline tree had test precision 30.74%, recall 88.50% and F1 45.63%; the selected forest produces more reliable alerts but has lower recall. The adjusted single tree was evaluated on validation only, so its 80.88%/59.62% scores must not be presented as a same-test comparison.

## Important evaluation-history limitation

The original test had already been inspected for the baseline tree before later validation-only development. The forest was not tuned on test scores, but this is not a pristine final test following an entirely blind research process. It is a useful held-out control within Elliptic++, not the independent external validation previously identified as necessary.

Address-disjoint splits do not prove entity/case independence. Full-history aggregate features do not support a causal real-time interpretation. Original illicit labels do not specifically identify stolen bitcoin. Scores are not calibrated criminality probabilities.

## Reproduction

```bash
python evaluate_frozen_forest.py /path/to/ellipticplusplus /path/to/new_test_output
```

The script checks original file hashes, fits exactly one locked configuration, and writes forest_test_metrics.json and status.json. The output directory must be new. The experiment has completed, and confusion totals, precision and the metrics checksum were independently checked. Seven benchmark tests pass. No serialized fitted forest is exported.

## Next priority

Freeze this result as a documented benchmark. Further tuning must not chase these test results. To validate the internship's stolen-funds objective, acquire independent sourced cases and controls, define address roles and decision dates, reconstruct compatible decision-time features, and establish a new evaluation protocol before fitting. The existing FBI/Binance references alone do not supply a complete independent binary benchmark.
