# Fourteen methods across the 49-cell matrix

Compare the same 49 training and test combinations across Coldcard, CryptoBilis and BTCPay. All methods use the original source-cohort target, the same observations and the same reserved components. The predictors use confirmed histories strictly before the reference block.

[Complete 49-cell benchmark CSV](2026-11-24-method-benchmark.csv)

## External transfer results

Each row averages the nine external comparisons with a single target incident, assigning the same weight to each comparison. These comparisons reuse incident populations.

| Method | Mean average precision | Mean recall | Mean false-alert rate | Transfers at or below 5% |
| --- | ---: | ---: | ---: | ---: |
| Inactivity alone | 0.792 | 53.8% | 11.3% | 4/9 |
| Histogram gradient boosting | 0.682 | 36.7% | 7.6% | 5/9 |
| Random forest | 0.681 | 36.8% | 7.1% | 5/9 |
| Logistic, all 14 predictors | 0.671 | 44.7% | 8.7% | 3/9 |
| Logistic, without time since last activity | 0.665 | 43.1% | 8.8% | 3/9 |
| Logistic, inactivity + balance | 0.664 | 42.8% | 8.5% | 3/9 |
| Gaussian naive Bayes | 0.657 | 31.3% | 5.1% | 6/9 |
| Balance alone | 0.642 | 28.5% | 5.2% | 3/9 |
| RBF support vector machine | 0.637 | 41.9% | 7.1% | 4/9 |
| Main decision tree | 0.602 | 33.8% | 10.6% | 4/9 |
| Logistic, without activity timing | 0.587 | 31.6% | 6.4% | 3/9 |
| Logistic, without timing and counts | 0.585 | 33.0% | 6.6% | 3/9 |
| Smaller decision tree | 0.568 | 28.0% | 6.9% | 4/9 |
| Logistic, balance alone | 0.528 | 17.3% | 6.0% | 3/9 |

## Selected matched comparisons

| Training → test | Method | Sources retrieved | False alerts | AP |
| --- | --- | ---: | ---: | ---: |
| Coldcard → CryptoBilis | Inactivity alone | 60/122 | 7/145 | 0.854 |
| Coldcard → CryptoBilis | Logistic, inactivity + balance | 100/122 | 6/145 | 0.961 |
| Coldcard → CryptoBilis | Gaussian naive Bayes | 109/122 | 4/145 | 0.973 |
| Coldcard → CryptoBilis | Random forest | 63/122 | 9/145 | 0.900 |
| Coldcard → CryptoBilis | Histogram gradient boosting | 64/122 | 7/145 | 0.903 |
| Coldcard + CryptoBilis → BTCPay | Inactivity alone | 4/16 | 5/22 | 0.571 |
| Coldcard + CryptoBilis → BTCPay | Logistic, inactivity + balance | 1/16 | 2/22 | 0.487 |
| Coldcard + CryptoBilis → BTCPay | Gaussian naive Bayes | 2/16 | 4/22 | 0.464 |
| Coldcard + CryptoBilis → BTCPay | Random forest | 0/16 | 1/22 | 0.422 |
| Coldcard + CryptoBilis → BTCPay | Histogram gradient boosting | 2/16 | 5/22 | 0.445 |

Gaussian naive Bayes is a challenger on the already inspected Coldcard → CryptoBilis transfer. Inactivity has the highest mean external AP. On pooled transfer to BTCPay, every method with a realized false-alert rate at or below 5% retrieves zero sources. The registry candidate stays provisional pending a previously untouched incident.

## Calibration and reproduction

- External cutoffs use five grouped out-of-fold training scores and target a maximum 5% witness false-alert rate. Internal predictions and cutoffs use nested grouped folds, preserving each scored fold outside fitting and calibration. Mixed cells combine the reserved predictions for each incident. The external rates report the realized proportion on eligible witnesses.
- The two trees use the original specifications. The six logistic regressions use fixed L2 and the prior activity-feature ablations. New comparators have fixed settings: random forest with 96 trees, maximum depth 6 and minimum leaf size 8; histogram gradient boosting with 75 iterations, maximum 7 leaves and minimum leaf size 12; Gaussian naive Bayes with equal priors and variance smoothing 1e-8; RBF SVM with C = 1 and scale gamma. Medians and scales use only each fit partition. The new classifiers use the logged and scaled predictors and their missingness indicators.
- The CSV includes incident-level metrics, pooled observations and equal-incident averages. Pooled ranking scores can depend on cross-incident score scales. The overlap audit has eight unavailable Coldcard histories. The BTCPay pilot has sixteen sources. The target is source-cohort membership.
- The original tree scores were replayed exactly. The earlier nine-transfer budget results were reproduced for all previously evaluated methods. A separate metric calculation verified all 2,548 aggregate rows.

[Current candidate](../CURRENT.md) · [Experiment history](../README.md)
