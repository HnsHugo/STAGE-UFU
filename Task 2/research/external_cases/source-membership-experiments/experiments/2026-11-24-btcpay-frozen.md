# BTCPay pilot and frozen-tree transfer

The pilot contained 16 reference blocks and 48 complete histories, with one source and two same-block witnesses per block. All 14 predictors were reconstructed from confirmed transactions strictly before the reference block. The overlap audit removed 10 witnesses and retained 16 sources and 22 witnesses. Detailed histories were available for 1,792 of the 1,800 complete Coldcard and CryptoBilis development observations. Eight Coldcard histories were unavailable.

The five frozen trees trained on Coldcard and CryptoBilis were replayed at a decision threshold of 0.50. Each row summarizes the same 38 BTCPay observations.

| Frozen tree | Sources retrieved | False alerts | ROC AUC |
| --- | ---: | ---: | ---: |
| 1 | 0 of 16 | 1 | 0.5540 |
| 2 | 0 of 16 | 1 | 0.4460 |
| 3 | 2 of 16 | 5 | 0.5270 |
| 4 | 0 of 16 | 1 | 0.5270 |
| 5 | 0 of 16 | 1 | 0.5028 |

Prior inactivity obtained ROC AUC 0.6278. The evidence supports an exploratory source-cohort test on this pilot. Each tree has gaps in detailed training-history coverage.

[BTCPay preparation protocol](../../btcpay_test_preparation_20261120/README.md) · [Experiment history](../README.md)
