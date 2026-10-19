# Validation-only weighting and threshold experiment

## Objective and protocol

Reduce additional alerts while measuring the loss in recall. This development experiment uses the same original training and validation address splits as train_benchmark.py. Test addresses are reserved and never used for fitting, threshold selection or evaluation in this script. No new test score is reported.

All trees retain depth 8, min_samples_leaf=20, random_state=42 and the 51 full-profile features. Three weighting options are predefined: no weighting, illicit weight 3 versus licit weight 1, and balanced weights. Each tree is fitted only to training addresses. Nineteen predefined thresholds from 0.05 to 0.95 are evaluated on validation. A positive prediction requires score strictly greater than the threshold, matching scikit-learn's class-0 tie-break at exactly 0.5.

The criterion is maximum validation F1 across weight/threshold configurations. This is an exploratory choice, not a user-specified operational cost function. We retain the full grid to make precision/recall tradeoffs reviewable. Scores are not calibrated probabilities.

## Results on the same validation set

Validation: 53,071 addresses, including 2,853 illicit and 50,218 licit labels.

| Weighting | Threshold | Precision | Recall | F1 | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Balanced, original reference | 0.50 | 30.28% | 88.22% | 45.09% | 2517 | 5795 | 336 |
| Unweighted, best grid F1 | 0.35 | 83.45% | 56.36% | 67.28% | 1608 | 319 | 1245 |
| Illicit weight 3, best grid F1 | 0.75 | 80.88% | 59.62% | 68.64% | 1701 | 402 | 1152 |
| Balanced, best grid F1 | 0.90 | 67.92% | 57.73% | 62.41% | 1647 | 778 | 1206 |

The selected development configuration is illicit weight 3 and threshold 0.75.
Relative to the original model on validation, false alerts decrease from 5795 to 402, while recovered illicit examples decrease from 2517 to 1701. This is a precision/recall tradeoff, not a universal improvement on every criterion. A more conservative configuration may be useful when review capacity is limited; the original higher-recall configuration may be preferable when missed positives are especially costly.

At threshold 0.50, the balanced tree exactly reproduces the original validation metrics. Raising a threshold does not change the fitted tree or its ranking/average precision; changing weights trains a different tree and can alter its ranking.

## Reproduction and artifacts

From this directory, after downloading the pinned original inputs:

```bash
python tune_validation.py /path/to/ellipticplusplus /path/to/new_validation_output
python -m unittest discover -p 'test_*.py' -v
```

The output directory must be new. Inputs are verified using their original SHA-256 hashes. Results are in validation_tuning_20261013/validation_metrics.json, with the full threshold grid and three readable trees. Seven benchmark tests now pass, including tie behaviour and the non-increasing alert count when a fixed model's threshold increases.

## Interpretation limits and next step

Validation was reused to select the model and threshold: the winning validation score is optimistically selected and is not independent confirmation. The original test was previously inspected and remains a historical reference; it is not evaluated again here or used to choose thresholds. Further confirmation requires an independent evaluation dataset/protocol.

The offline-profile and related-address limitations of the original benchmark remain. These results do not validate real-time detection, stolen-fund attribution or hardware-wallet identification. A threshold of 0.75 is a rule over this model's scores, not a 75% probability of criminality.

Methodological reference: https://scikit-learn.org/stable/modules/classification_threshold.html
