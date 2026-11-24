# Bitfinex 2016 retrospective pilot

Twelve reference transactions across seven Bitcoin blocks yielded five selected source groups and ten same-block witnesses. The fifteen complete address histories cover four reference blocks. Predictors use confirmed transactions strictly before each observation’s reference block. The target is membership in the documented Bitfinex source cohort.

The observed overlap audit compared addresses, references, historic transactions, outpoints, funding and co-input links with Coldcard. All fifteen observations were retained. The audit included 1,500 Coldcard identity records and recounted 1,463 of the 1,471 complete training histories. Detailed evidence for eight training histories remains unavailable.

The three methods and their thresholds were frozen on Coldcard before scoring Bitfinex. Each threshold flagged 48 of 971 witnesses in the original grouped out-of-fold calibration.

| Method | Sources retrieved | False alerts on witnesses | Observed false-alert rate | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: |
| Inactivity alone | 3/5 | 0/10 | 0% | 1.000 | 1.000 |
| Logistic, inactivity + balance | 4/5 | 2/10 | 20% | 0.883 | 0.860 |
| Gaussian naive Bayes | 3/5 | 1/10 | 10% | 0.650 | 0.680 |

Inactivity alone is the only method at or below the 5% false-alert target on this pilot. It ranks all five sources above the ten witnesses. With ten witnesses, a single false alert is 10 percentage points. The small sample and incomplete detailed overlap audit limit the result. The Bitfinex reference blocks predate Coldcard training references, so this is a retrospective stress test. The current candidate still requires a chronologically later independent incident.

## All 14 previously benchmarked methods

This extension uses the same five sources and ten witnesses. Each procedure was reproduced from the frozen Coldcard training data and original benchmark configuration. The grouped calibration cutoffs were replayed exactly, as were all original scores on the 305 earlier external observations. Bitfinex provides the retrospective test population.

| Method | Sources retrieved | False alerts | False-alert rate | F1 | AP | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Main decision tree | 4/5 | 1/10 | 10% | 0.800 | 0.747 | 0.860 |
| Smaller decision tree | 4/5 | 1/10 | 10% | 0.800 | 0.707 | 0.760 |
| Inactivity alone | 3/5 | 0/10 | 0% | 0.750 | 1.000 | 1.000 |
| Balance alone | 4/5 | 1/10 | 10% | 0.800 | 0.867 | 0.800 |
| Logistic, balance alone | 4/5 | 1/10 | 10% | 0.800 | 0.867 | 0.800 |
| Logistic, inactivity + balance | 4/5 | 2/10 | 20% | 0.727 | 0.883 | 0.860 |
| Logistic, all 14 predictors | 4/5 | 2/10 | 20% | 0.727 | 0.877 | 0.840 |
| Logistic, without time since last activity | 4/5 | 2/10 | 20% | 0.727 | 0.877 | 0.840 |
| Logistic, without activity timing | 4/5 | 4/10 | 40% | 0.615 | 0.827 | 0.780 |
| Logistic, without timing and counts | 4/5 | 4/10 | 40% | 0.615 | 0.827 | 0.780 |
| Random forest | 4/5 | 1/10 | 10% | 0.800 | 0.871 | 0.900 |
| Histogram gradient boosting | 4/5 | 2/10 | 20% | 0.727 | 0.900 | 0.900 |
| Gaussian naive Bayes | 3/5 | 1/10 | 10% | 0.667 | 0.650 | 0.680 |
| RBF support vector machine | 4/5 | 4/10 | 40% | 0.615 | 0.800 | 0.760 |

Inactivity alone reaches the 5% false-alert target with three of five sources detected. The balance rule, balance-only regression, both trees and random forest each detect four sources with one false alert. These five methods have the highest F1 (0.800) at the unchanged cutoffs. No method retrieves all five sources. The test contains only ten witnesses, so each alert shifts the measured rate by ten percentage points.

[Full 14-method benchmark across Coldcard, CryptoBilis and BTCPay](2026-11-24-method-benchmark.md)

[Experiment history](../README.md) · [Current candidate](../CURRENT.md)
