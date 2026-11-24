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

[Experiment history](../README.md) · [Current candidate](../CURRENT.md)
